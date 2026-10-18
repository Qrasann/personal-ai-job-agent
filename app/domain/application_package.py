from __future__ import annotations

from copy import deepcopy
from typing import Any

def snapshot_vacancy(
    job,
    *,
    source_id: str | None = None,
    source_job_id: str | None = None,
    source_url: str | None = None,
    relocation_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Copy posting and explicitly selected evidence used for this package."""
    snapshot: dict[str, Any] = {
        "title": job.title or "",
        "company": job.company or "",
        "description": job.description or "",
        "source_url": source_url or "",
    }
    if source_id:
        snapshot["source_id"] = " ".join(str(source_id).split())[:64]
    if source_job_id:
        snapshot["source_job_id"] = " ".join(str(source_job_id).split())[:256]
    if isinstance(relocation_evidence, dict):
        snapshot["relocation_evidence"] = deepcopy(relocation_evidence)
    return snapshot
