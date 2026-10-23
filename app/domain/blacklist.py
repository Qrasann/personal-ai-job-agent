from __future__ import annotations

from datetime import UTC, datetime


BLACKLIST_RULE_KINDS = frozenset({"vacancy", "company", "company_role", "role", "phrase"})


def _norm(value: object) -> str:
    return " ".join(str(value or "").casefold().split())


def _active(rule: dict, now: datetime) -> bool:
    if rule.get("enabled") is False:
        return False
    expires_at = rule.get("expires_at")
    if not expires_at:
        return True
    if not isinstance(expires_at, str):
        return False
    try:
        expires = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    return expires.tzinfo is not None and expires.astimezone(UTC) > now


def matching_blacklist_rule(job, settings: dict | None, *, now: datetime | None = None) -> dict | None:
    """Return the first active structured blacklist rule matching a vacancy.

    Exact identity matching is deliberate for vacancy, company and role rules;
    only an explicit phrase rule performs bounded free-text containment.
    """
    observed = now or datetime.now(UTC)
    title = _norm(getattr(job, "title", ""))
    company = _norm(getattr(job, "company", ""))
    fingerprint = _norm(getattr(job, "fingerprint", ""))
    job_id = _norm(getattr(job, "id", ""))
    haystack = _norm(" ".join((
        str(getattr(job, "title", "") or ""),
        str(getattr(job, "company", "") or ""),
        str(getattr(job, "description", "") or ""),
    )))
    for raw in (settings or {}).get("blacklist_rules") or []:
        if not isinstance(raw, dict) or raw.get("kind") not in BLACKLIST_RULE_KINDS:
            continue
        if not _active(raw, observed):
            continue
        value = _norm(raw.get("value"))
        if not value:
            continue
        kind = raw["kind"]
        if kind == "vacancy" and value in {fingerprint, job_id}:
            return raw
        if kind == "company" and value == company:
            return raw
        if kind == "role" and value == title:
            return raw
        if kind == "company_role":
            expected_company, separator, expected_role = value.partition("|")
            if separator and expected_company.strip() == company and expected_role.strip() == title:
                return raw
        if kind == "phrase" and value in haystack:
            return raw
    return None
