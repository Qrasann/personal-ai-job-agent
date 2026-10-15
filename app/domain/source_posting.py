"""Source-specific normalized posting text for deduplicated jobs."""
from __future__ import annotations

import hashlib
import json
from types import SimpleNamespace

from app.domain.jobs import NormalizedJob


_STRING_LIMITS = {
    "title": 512,
    "company": 512,
    "description": 100000,
    "country": 128,
    "city": 256,
    "work_mode": 64,
    "remote_scope": 128,
    "salary_currency": 16,
    "salary_period": 32,
    "published_at": 64,
}
_OPTIONAL_VALUES = ("relocation", "visa_sponsorship", "salary_from", "salary_to")


def snapshot_source_posting(job: NormalizedJob) -> dict:
    """Store only normalized fields from this exact source observation."""
    snapshot = {"schema": "normalized_posting_v1"}
    for field, limit in _STRING_LIMITS.items():
        value = getattr(job, field)
        snapshot[field] = str(value)[:limit] if value is not None else None
    for field in _OPTIONAL_VALUES:
        snapshot[field] = getattr(job, field)
    return snapshot


def posting_snapshot_digest(snapshot) -> str | None:
    """Stable identity for the normalized card version used by a detail cache."""
    if not isinstance(snapshot, dict) or snapshot.get("schema") != "normalized_posting_v1":
        return None
    try:
        payload = json.dumps(snapshot, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    except (TypeError, ValueError):
        return None
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def source_posting_view(job, source_ref):
    """Overlay the selected source's posting without mutating the canonical Job.

    Older refs have no snapshot and retain the established canonical fallback.
    """
    raw = getattr(source_ref, "raw", None) or {}
    snapshot = raw.get("normalized_posting_v1") if isinstance(raw, dict) else None
    valid_snapshot = (
        isinstance(snapshot, dict)
        and snapshot.get("schema") == "normalized_posting_v1"
        and isinstance(snapshot.get("title"), str)
        and bool(snapshot["title"].strip())
    )
    cached = raw.get("details_cache_v1") if isinstance(raw, dict) else None
    cache_digest = raw.get("details_cache_posting_digest_v1") if isinstance(raw, dict) else None
    valid_cache = isinstance(cached, dict) and any(
        isinstance(cached.get(field), str) and cached[field].strip()
        for field in ("title", "company", "description")
    )
    if cache_digest and cache_digest != posting_snapshot_digest(snapshot):
        valid_cache = False
    if not valid_snapshot and not valid_cache:
        return job

    view = SimpleNamespace(**{
        key: value for key, value in vars(job).items() if not key.startswith("_")
    })
    if valid_snapshot:
        for field in _STRING_LIMITS:
            value = snapshot.get(field)
            if value is None or isinstance(value, str):
                setattr(view, field, value)
        for field in ("relocation", "visa_sponsorship"):
            value = snapshot.get(field)
            if value is None or isinstance(value, bool):
                setattr(view, field, value)
        for field in ("salary_from", "salary_to"):
            value = snapshot.get(field)
            if value is None or isinstance(value, int) and not isinstance(value, bool):
                setattr(view, field, value)
    if valid_cache:
        for field in ("title", "company", "description"):
            value = cached.get(field)
            if isinstance(value, str) and value.strip():
                setattr(view, field, value[:_STRING_LIMITS[field]])
    return view
