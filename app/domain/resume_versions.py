from __future__ import annotations

from datetime import UTC, datetime


VERSION_KEY = "cv_version_v1"


def version_metadata(rules: dict | None) -> dict:
    """Return compatible CV version metadata; pre-versioning CVs stay approved."""
    raw = (rules or {}).get(VERSION_KEY)
    if not isinstance(raw, dict):
        return {"status": "approved", "legacy": True}
    status = raw.get("status")
    return {**raw, "status": status if status in {"draft", "approved"} else "draft"}


def draft_version_rules(rules: dict | None, *, parent_id: int) -> dict:
    result = dict(rules or {})
    result[VERSION_KEY] = {"status": "draft", "parent_id": int(parent_id)}
    return result


def approved_version_rules(rules: dict | None, *, now: datetime | None = None) -> dict:
    result = dict(rules or {})
    current = version_metadata(result)
    result[VERSION_KEY] = {
        key: value for key, value in current.items()
        if key in {"parent_id"}
    } | {
        "status": "approved",
        "approved_at": (now or datetime.now(UTC)).astimezone(UTC).isoformat().replace("+00:00", "Z"),
    }
    return result
