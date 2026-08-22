from __future__ import annotations

from dataclasses import asdict, dataclass, field
from hashlib import sha256
from typing import Any


@dataclass(slots=True)
class SourceCapabilities:
    discovery: bool = True
    details: bool = True
    apply: bool = False
    messages: bool = False
    history: bool = False


@dataclass(slots=True)
class NormalizedJob:
    source: str
    source_job_id: str
    title: str
    company: str = ""
    description: str = ""
    url: str = ""
    country: str | None = None
    city: str | None = None
    work_mode: str | None = None
    remote_scope: str | None = None
    relocation: bool | None = None
    visa_sponsorship: bool | None = None
    salary_from: int | None = None
    salary_to: int | None = None
    salary_currency: str | None = None
    salary_period: str | None = None
    published_at: str | None = None
    skills: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    def canonical_fingerprint(self) -> str:
        # Deliberately excludes URL/source so reposts from another board can collapse.
        company_or_body = self.company.strip().casefold()
        if not company_or_body:
            company_or_body = " ".join(self.description.split())[:500].casefold()
        key = "|".join(
            [
                company_or_body,
                self.title.strip().casefold(),
                (self.country or "").strip().casefold(),
                (self.city or "").strip().casefold(),
            ]
        )
        return sha256(key.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
