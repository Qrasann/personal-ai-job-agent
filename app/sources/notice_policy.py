from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta


STATE_KEY = "source_notice_state.v1"
DAILY_SUMMARY_AFTER = timedelta(hours=24)
_SEVERITY = {"healthy": 0, "limited": 1, "material_loss": 2, "unavailable": 3}
_NETWORK_CODES = {
    "DNS_RESOLUTION_FAILED", "NETWORK_CONNECT_TIMEOUT", "NETWORK_READ_TIMEOUT",
    "NETWORK_POOL_TIMEOUT", "NETWORK_CONNECT_ERROR", "NETWORK_TRANSPORT_FAILED",
    "NETWORK_PROXY_ERROR", "NETWORK_CONNECTION_RESET", "NETWORK_CONNECTION_REFUSED",
    "NETWORK_UNREACHABLE", "TLS_CONNECTION_FAILED", "TLS_VALIDATION_FAILED",
}


def _utc(now: datetime | None = None) -> datetime:
    value = now or datetime.now(UTC)
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


def _parse_time(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except (ValueError, OverflowError):
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(UTC)


def _load(raw: str) -> dict[str, dict]:
    try:
        payload = json.loads(raw)
    except (TypeError, ValueError):
        return {}
    # Migrate v1 rows in place. The old signature included raw error codes.
    if not isinstance(payload, dict) or payload.get("version") not in {1, 2}:
        return {}
    rows = payload.get("sources")
    return rows if isinstance(rows, dict) else {}


def _current(info: dict) -> dict | None:
    status = str(info.get("status") or "failed")
    diagnostics = info.get("diagnostics") if isinstance(info.get("diagnostics"), list) else []
    codes = sorted({
        str(item.get("code") or "SOURCE_PROCESSING_FAILED")
        for item in diagnostics
        if isinstance(item, dict)
        and item.get("action") != "fallback"
        and not (item.get("action") == "cooldown" and item.get("code") != "TLS_VALIDATION_FAILED")
    })
    saw_cooldown = any(
        isinstance(item, dict) and item.get("action") == "cooldown"
        for item in diagnostics
    )
    if status in {"failed", "skipped"} and saw_cooldown and not codes:
        return None

    if status == "failed":
        state = "unavailable"
        impact = "critical"
    elif status in {"partial", "success"} and codes:
        attempts = max(0, int(info.get("attempts") or 0))
        failed = max(0, int(info.get("failed") or 0))
        found = max(0, int(info.get("found") or 0))
        processed = max(0, int(info.get("processed") or 0))
        successful = max(0, int(info.get("successful_attempts") or 0))
        processing_errors = max(0, int(info.get("processing_errors") or 0))
        material_loss = info.get("material_loss") is True
        majority_failed = attempts > 0 and failed / attempts >= 0.5
        no_results = (found == 0 and (
            failed > 0 or int(info.get("partial_failures") or 0) > 0
        )) or (
            processing_errors > 0 and processed == 0
        )
        state = "material_loss" if material_loss or majority_failed or no_results else "limited"
        impact = "material" if state == "material_loss" else "limited"
        if state == "material_loss" and successful == 0 and failed:
            state = "unavailable"
            impact = "critical"
    else:
        state = "healthy"
        impact = "none"

    # Exact codes stay in Diagnostics/state, but code churn does not change
    # the state/impact signature sent to chat.
    family = "network" if codes and set(codes) <= _NETWORK_CODES else (
        "provider_or_processing" if codes else "none"
    )
    return {"state": state, "impact": impact, "codes": codes, "family": family}


def plan_source_notices(
    sources: dict,
    raw_state: str,
    *,
    now: datetime | None = None,
) -> tuple[list[dict], str]:
    """Plan notices from one already profile-aggregated row per provider."""
    timestamp = _utc(now)
    stamp = timestamp.isoformat(timespec="seconds")
    previous_rows = _load(raw_state)
    next_rows: dict[str, dict] = {}
    notices: list[dict] = []

    for source_id, info in list(sources.items())[:64]:
        if not isinstance(info, dict):
            continue
        current = _current(info)
        previous = previous_rows.get(str(source_id))
        previous = previous if isinstance(previous, dict) else {}
        if current is None:
            if previous:
                next_rows[str(source_id)] = previous
            continue

        signature = f"{current['state']}|{current['impact']}"
        same = previous.get("signature") == signature or (
            previous.get("state") == current["state"]
            and previous.get("impact", current["impact"]) == current["impact"]
        )
        occurrence = int(previous.get("occurrences") or 0) + 1 if same else 1
        row = {
            "signature": signature,
            "state": current["state"],
            "impact": current["impact"],
            "family": current["family"],
            "codes": current["codes"],
            "occurrences": occurrence,
            "first_seen_at": previous.get("first_seen_at") if same else stamp,
            "last_seen_at": stamp,
            "last_notified_at": previous.get("last_notified_at") if same else None,
        }
        previous_state = str(previous.get("state") or "healthy")
        event: dict | None = None
        if current["state"] == "healthy":
            if previous_state in {"material_loss", "unavailable"}:
                event = {
                    "kind": "recovered",
                    "previous_state": previous_state,
                    "previous_codes": list(previous.get("codes") or []),
                    "previous_occurrences": int(previous.get("occurrences") or 1),
                }
        elif _SEVERITY[current["state"]] > _SEVERITY.get(previous_state, 0):
            if current["state"] in {"material_loss", "unavailable"}:
                event = {"kind": "critical" if current["state"] == "unavailable" else "issue"}
        elif same:
            last_notified = _parse_time(previous.get("last_notified_at"))
            reference = last_notified or _parse_time(previous.get("first_seen_at"))
            if reference is not None and timestamp - reference >= DAILY_SUMMARY_AFTER:
                event = {"kind": "daily"}

        if event is not None:
            row["last_notified_at"] = stamp
            notices.append({
                "source_id": str(source_id),
                "state": current["state"],
                "impact": current["impact"],
                "codes": current["codes"],
                "occurrences": occurrence,
                **event,
            })
        next_rows[str(source_id)] = row

    encoded = json.dumps(
        {"version": 2, "updated_at": stamp, "sources": next_rows},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return notices, encoded


def render_source_state_notice(event: dict, info: dict) -> str:
    source = str(info.get("name") or event.get("source_id") or "source")[:128]
    found = max(0, int(info.get("found") or 0))
    kind = event.get("kind")
    if kind == "recovered":
        count = int(event.get("previous_occurrences") or 1)
        return f"✅ Поиск по источнику {source} восстановился после {count} наблюдений."
    if kind == "daily":
        return f"ℹ️ Источник {source} всё ещё работает с ограничениями; подробности — /scanstatus."
    if kind == "critical":
        return f"🔴 Источник {source} недоступен; вакансии этого источника не получены. Проверь /scanstatus."
    return (
        f"⚠️ Источник {source} потерял существенную часть результатов; сохранено вакансий: {found}. "
        "Подробности — /scanstatus."
    )


def render_source_daily_digest(events: list[dict], sources: dict) -> str:
    names = [
        str((sources.get(event.get("source_id")) or {}).get("name") or event.get("source_id") or "источник")[:80]
        for event in events[:12]
    ]
    extra = len(events) - len(names)
    suffix = f" и ещё {extra}" if extra > 0 else ""
    return (
        "ℹ️ Ежедневная сводка: ограничения остаются у "
        + ", ".join(names) + suffix + ". Подробности — /scanstatus."
    )
