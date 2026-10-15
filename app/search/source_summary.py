from __future__ import annotations

from app.sources.diagnostics import SourceSummaryError, legacy_diagnostic


COUNTERS = ("found", "discovered", "preference_filtered", "processed", "qualified", "stretch", "notified", "filtered", "duplicate", "retry", "fallback", "processing_errors", "publication_date_provided", "publication_date_missing")


def normalize_attempt(info: dict) -> dict:
    status = info.get("status")
    if status is None:
        status = "failed" if info.get("error") else "skipped" if info.get("skipped") else "partial" if info.get("partial") else "success"
    if status not in {"success", "partial", "failed", "skipped"}:
        raise SourceSummaryError("status")
    if status in {"success", "partial"} and "found" not in info:
        raise SourceSummaryError("found")
    result = dict(info)
    result.update({key: int(info.get(key, 0)) for key in COUNTERS})
    result.update(status=status, partial=status == "partial", failed=int(status == "failed"),
                  skipped=int(status == "skipped"), attempts=1,
                  successful_attempts=int(status in {"success", "partial"}),
                  partial_attempts=int(status == "partial"), duration_ms=int(info.get("duration_ms", 0)))
    result["diagnostics"] = [dict(item) for item in info.get("diagnostics", [])]
    if info.get("error") and not result["diagnostics"]:
        result["diagnostics"] = [legacy_diagnostic(info["error"])]
    # Never retain an arbitrary legacy exception message.
    if status == "failed":
        result["error"] = next((item["code"] for item in reversed(result["diagnostics"]) if item.get("action") != "fallback"), "SOURCE_PROCESSING_FAILED")
    else:
        result.pop("error", None)
    return result


def merge_diagnostics(items: list[dict]) -> list[dict]:
    events = {}
    for item in items:
        key = (item.get("observation_id", ""), item.get("code"), item.get("stage"), item.get("action"), item.get("operation"))
        if key not in events:
            events[key] = {**item, "profiles": list(item.get("profiles", []))}
        else:
            previous = events[key]
            previous["count"] = max(previous.get("count", 1), item.get("count", 1))
            previous["profiles"] = list(dict.fromkeys(previous["profiles"] + item.get("profiles", [])))
    return list(events.values())


def aggregate_source(sources: dict, source_id: str, info: dict) -> None:
    attempt = normalize_attempt(info)
    previous = sources.get(source_id)
    history = list(previous.get("history", [])) if previous else []
    # Accept old in-memory summaries as well as the new attempt ledger.
    if previous and not history:
        history.append(normalize_attempt(previous))
    history.append(attempt)
    for index, entry in enumerate(history):
        for item in entry["diagnostics"]:
            item.setdefault("observation_id", f"attempt:{index}")
    observations = {}
    for entry in history:
        observations.update(entry.get("partial_failure_observations", {}))
    result = {key: sum(entry[key] for entry in history) for key in COUNTERS}
    result.update({key: sum(entry[key] for entry in history) for key in
                   ("attempts", "failed", "skipped", "successful_attempts", "partial_attempts")})
    result["partial_failures"] = (sum(observations.values()) if observations else
                                  sum(entry.get("partial_failures", 0) for entry in history))
    result["partial_failure_observations"] = observations
    incomplete = bool(result["failed"] or result["skipped"] or result["partial_attempts"] or result["partial_failures"] or result["processing_errors"])
    result["status"] = ("partial" if incomplete else "success") if result["successful_attempts"] else "failed" if result["failed"] else "skipped"
    result["partial"] = result["status"] == "partial"
    result["duration_ms"] = max(entry["duration_ms"] for entry in history)
    result["cache"] = all(entry.get("cache", False) for entry in history if entry["successful_attempts"]) if result["successful_attempts"] else False
    result["name"] = info.get("name", previous.get("name", source_id) if previous else source_id)
    result["history"] = history
    result["diagnostics"] = merge_diagnostics([item for entry in history for item in entry["diagnostics"]])
    if result["status"] == "failed":
        result["error"] = next((item["code"] for item in reversed(result["diagnostics"]) if item.get("action") != "fallback"), "SOURCE_PROCESSING_FAILED")
    sources[source_id] = result


def scan_outcome(summary: dict) -> str:
    statuses = [info.get("status") or normalize_attempt(info)["status"] for info in summary.get("sources", {}).values()]
    if not statuses or all(status == "success" for status in statuses):
        return "completed"
    return "partial" if any(status in {"success", "partial"} for status in statuses) else "failed" if "failed" in statuses else "partial"


def render_source_summary(source_id: str, info: dict) -> str:
    """Plain dashboard text; callers escape once for Telegram HTML."""
    from app.sources.diagnostics import MESSAGES, legacy_diagnostic
    status = info.get("status") or normalize_attempt(info)["status"]
    label = {"success": "готово", "partial": "частично", "failed": "ошибка", "skipped": "пропущен"}[status]
    name = str(info.get("name") or source_id)
    line = f"• {name}: {label} · {int(info.get('found', 0))} вакансий ({int(info.get('duration_ms', 0)) / 1000:.1f} с)"
    if info.get("cache"):
        line += " · кэш"
    if info.get("partial_failures"):
        line += f" · сбои: {int(info['partial_failures'])}"
    if info.get("discovered"):
        line += f" · получено до настроек: {int(info['discovered'])}"
        line += f" · исключено настройками: {int(info.get('preference_filtered', 0))}"
    date_total = int(info.get("publication_date_provided", 0)) + int(info.get("publication_date_missing", 0))
    if date_total:
        line += f" · поле даты публикации заполнено: {int(info.get('publication_date_provided', 0))}/{date_total}"
    for key, title in (("processed", "обработано"), ("qualified", "Good"), ("stretch", "Stretch"), ("filtered", "отфильтровано"), ("duplicate", "дубликатов"), ("failed", "ошибок попыток"), ("skipped", "пропусков"), ("processing_errors", "ошибок обработки"), ("partial_attempts", "частичных попыток"), ("retry", "повторов"), ("fallback", "fallback")):
        if isinstance(info.get(key), int) and info[key]:
            line += f" · {title}: {info[key]}"
    items = info.get("diagnostics", []) or ([legacy_diagnostic(info["error"])] if info.get("error") else [])
    issues = {}
    for item in items:
        code = item.get("code") if item.get("code") in MESSAGES else "SOURCE_PROCESSING_FAILED"
        profiles = issues.setdefault(code, [])
        profiles.extend(item.get("profiles", []))
    for code, profiles in issues.items():
        scope = " / ".join(dict.fromkeys(profiles))
        line += f"\n  {MESSAGES[code]} [{code}]" + (f" · {scope}" if scope else "")
    return line


def select_scan_dashboard(manual: dict, scheduled: dict) -> dict:
    """Prefer active manual work; otherwise display the most recent scan."""
    manual = manual if isinstance(manual, dict) else {}
    scheduled = scheduled if isinstance(scheduled, dict) else {}
    if manual.get("status") == "running":
        return manual
    if scheduled and str(scheduled.get("started_at", "")) > str(manual.get("started_at", "")):
        return scheduled
    return manual or scheduled


def render_source_dashboard(sources: dict, *, limit: int = 2600) -> str:
    """Bound the HTML source section before Telegram's 4096-character limit."""
    import html
    text = "\n".join(render_source_summary(name, info) for name, info in sources.items())
    encoded = html.escape(text)
    if len(encoded) <= limit:
        return encoded
    suffix = "\n… Остальные сведения сохранены в диагностике; новые ошибки сообщаются отдельно."
    # Cut plain text before escaping; splitting an encoded entity is invalid.
    budget = limit - len(html.escape(suffix))
    low, high = 0, len(text)
    while low < high:
        middle = (low + high + 1) // 2
        if len(html.escape(text[:middle])) <= budget:
            low = middle
        else:
            high = middle - 1
    return html.escape(text[:low] + suffix)
