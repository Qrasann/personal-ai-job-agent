from __future__ import annotations


def snapshot_vacancy(job, *, source_url: str | None = None) -> dict[str, str]:
    """Copy the posting used for this package, without mutable/raw source data."""
    return {
        "title": job.title or "",
        "company": job.company or "",
        "description": job.description or "",
        "source_url": source_url or "",
    }
