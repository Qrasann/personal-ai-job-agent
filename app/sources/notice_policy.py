from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

from app.sources.diagnostics import STAGES


STATE_KEY = "source_notice_state.v1"
REPEAT_SUMMARY_AFTER = timedelta(hours=6)
_VALID_STATES = {"healthy", "degraded", "partial", "failed"}


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
    if not isinstance(payload, dict) or payload.get("version") != 1:
        return {}
    rows = payload.get("sources")
    return rows if isinstance(rows, dict) else {}


def _current(source_id: str, info: dict) -> dict | None:
    status = str(info.get("status") or "failed")
    diagnostics = info.get("diagnostics") if isinstance(info.get("diagnostics"), list) else []
    codes: set[str] = set()
    saw_cooldown = False
    for item in diagnostics:
        if not isinstance(item, dict):
            continue
        action = item.get("action")
        code = str(item.get("code") or "SOURCE_PROCESSING_FAILED")
        if action == "cooldown" and code != "TLS_VALIDATION_FAILED":
            saw_cooldown = True
            continue
        if source_id == "hh" and code == "HTTP_403_FORBIDDEN" and action == "fallback":
            # Expected anonymous API refusal is retained in Diagnostics. The
            # successful permitted web fallback is operational, not an alert.
            continue
        codes.add(code)

    if not codes and saw_cooldown and status in {"failed", "skipped"}:
        # A cooldown is the continuation of the preceding state, not a fresh
        # source transition every scheduled pass.
        return None
    if status == "failed":
        state = "failed"
    elif status == "partial":
        state = "partial" if codes else "healthy"
    elif codes:
        state = "degraded"
    else:
        state = "healthy"
    return {"state": state, "codes": sorted(codes)}


def plan_source_notices(
    sources: dict,
    raw_state: str,
    *,
    now: datetime | None = None,
) -> tuple[list[dict], str]:
    """Return state-change/repeat notices and the next bounded persisted state."""
    timestamp = _utc(now)
    stamp = timestamp.isoformat(timespec="seconds")
    previous_rows = _load(raw_state)
    next_rows: dict[str, dict] = {}
    notices: list[dict] = []

    for source_id, info in list(sources.items())[:64]:
        if not isinstance(info, dict):
            continue
        current = _current(str(source_id), info)
        previous = previous_rows.get(str(source_id))
        previous = previous if isinstance(previous, dict) else {}
        if current is None:
            if previous:
                next_rows[str(source_id)] = previous
            continue

        signature = current["state"] + "|" + ",".join(current["codes"])
        same = previous.get("signature") == signature
        occurrence = int(previous.get("occurrences") or 0) + 1 if same else 1
        row = {
            "signature": signature,
            "state": current["state"],
            "codes": current["codes"],
            "occurrences": occurrence,
            "first_seen_at": previous.get("first_seen_at") if same else stamp,
            "last_seen_at": stamp,
            "last_notified_at": previous.get("last_notified_at") if same else None,
        }
        event: dict | None = None
        if not same:
            previous_state = previous.get("state")
            if current["state"] == "healthy":
                if previous_state in _VALID_STATES - {"healthy"}:
                    event = {
                        "kind": "recovered",
                        "previous_state": previous_state,
                        "previous_codes": list(previous.get("codes") or []),
                        "previous_occurrences": int(previous.get("occurrences") or 1),
                    }
            else:
                event = {"kind": "issue"}
        elif current["state"] != "healthy":
            last_notified = _parse_time(previous.get("last_notified_at"))
            if last_notified is None or timestamp - last_notified >= REPEAT_SUMMARY_AFTER:
                event = {"kind": "repeat"}

        if event is not None:
            row["last_notified_at"] = stamp
            notices.append({
                "source_id": str(source_id),
                "state": current["state"],
                "codes": current["codes"],
                "occurrences": occurrence,
                **event,
            })
        next_rows[str(source_id)] = row

    encoded = json.dumps(
        {"version": 1, "updated_at": stamp, "sources": next_rows},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return notices, encoded


def render_source_state_notice(event: dict, info: dict) -> str:
    source = str(info.get("name") or event.get("source_id") or "source")[:128]
    found = int(info.get("found") or 0)
    processed = int(info.get("processed") or 0)
    codes = ", ".join(event.get("codes") or event.get("previous_codes") or ["UNKNOWN"])
    relevant_codes = set(event.get("codes") or event.get("previous_codes") or [])
    diagnostics = info.get("diagnostics") if isinstance(info.get("diagnostics"), list) else []
    profiles: list[str] = []
    stages: list[str] = []
    for item in diagnostics:
        if not isinstance(item, dict) or item.get("code") not in relevant_codes:
            continue
        profiles.extend(str(value)[:128] for value in item.get("profiles", []) if str(value).strip())
        stage = STAGES.get(item.get("stage"))
        if stage:
            stages.append(stage)
    context = ""
    if profiles:
        context += "\nПрофили: " + " / ".join(dict.fromkeys(profiles)) + "."
    if stages:
        context += "\nЭтапы: " + " / ".join(dict.fromkeys(stages)) + "."
    cause = " Причина устанавливается." if relevant_codes & {
        "NETWORK_CONNECT_ERROR", "NETWORK_CONNECT_TIMEOUT", "SOURCE_PROCESSING_FAILED"
    } else ""
    kind = event.get("kind")
    if kind == "recovered":
        count = int(event.get("previous_occurrences") or 1)
        return (
            f"✅ Источник {source} восстановлен после {count} наблюдений сбоя.\n"
            f"Предыдущие коды: {codes}.{context} Сейчас найдено: {found}, обработано: {processed}.\n"
            "Подробная история сохранена в /scanstatus и Diagnostics."
        )
    if kind == "repeat":
        return (
            f"⚠️ Источник {source}: проблема сохраняется; одинаковых наблюдений: "
            f"{int(event.get('occurrences') or 1)}.\nКоды: {codes}. "
            f"{cause}{context}\nСохранено результатов: {found}; обработано: {processed}.\n"
            "Повторы сгруппированы; подробности сохранены в /scanstatus и Diagnostics."
        )
    label = {
        "failed": "результаты текущей попытки недоступны",
        "partial": "получены частичные результаты",
        "degraded": "обнаружена техническая деградация",
    }.get(event.get("state"), "изменилось техническое состояние")
    return (
        f"⚠️ Источник {source}: {label}.\nКоды: {codes}.{cause}{context}\n"
        f"Сохранено результатов: {found}; обработано: {processed}.\n"
        "Одинаковые повторы будут сгруппированы; подробности — /scanstatus и Diagnostics."
    )
