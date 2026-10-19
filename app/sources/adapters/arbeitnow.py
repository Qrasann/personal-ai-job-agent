from __future__ import annotations

import asyncio
import logging

import httpx

from app.domain.job_text import clean_html_text
from app.domain.jobs import NormalizedJob, SourceCapabilities
from app.geo.locations import parse_city_country
from app.domain.remote_evidence import remote_location_restriction
from app.domain.support_evidence import support_evidence
from app.domain.vacancy_availability import source_datetime
from app.sources.diagnostics import SourceInvalidResponse
from app.sources.base import JobSource, SourceContext


log = logging.getLogger(__name__)


_ROLE_ALIASES = {
    "warehouse worker": ("lagerhelfer", "lagermitarbeiter", "kommissionierer"),
    "production worker": ("produktionsmitarbeiter", "produktionshelfer"),
    "hotel staff": ("hotelmitarbeiter", "hotel staff"),
    "kitchen assistant": ("küchenhilfe", "kitchen assistant"),
    "cleaner": ("reinigungskraft", "cleaner"),
    "construction worker": ("bauhelfer", "construction worker"),
}


def _query_phrases(query: str) -> tuple[str, ...]:
    normalized = " ".join(query.casefold().split())
    return (normalized, *_ROLE_ALIASES.get(normalized, ()))


def _tags(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


class ArbeitnowSource(JobSource):
    source_id = "arbeitnow"
    name = "Arbeitnow"
    capabilities = SourceCapabilities(discovery=True, details=True, apply=False, messages=False)
    endpoint = "https://www.arbeitnow.com/api/job-board-api"
    request_retries = 1
    request_timeout_seconds = 15.0

    @staticmethod
    def parse_payload(payload: dict, context: SourceContext) -> list[NormalizedJob]:
        if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
            raise SourceInvalidResponse("Arbeitnow API contract unavailable")
        query_groups = [
            _query_phrases(str(query))
            for query in (context.queries or [])
            if str(query).strip()
        ]
        jobs: list[NormalizedJob] = []
        for row in payload.get("data") or []:
            if not isinstance(row, dict) or not row.get("slug") or not row.get("title"):
                continue
            title = str(row["title"])
            tags = _tags(row.get("tags"))
            role_hay = " ".join([title, *tags]).casefold()
            if query_groups and not any(
                any(phrase and phrase in role_hay for phrase in phrases)
                for phrases in query_groups
            ):
                continue

            description = clean_html_text(str(row.get("description") or ""))
            support = support_evidence(f"{title}\n{description}")
            published = source_datetime(row.get("created_at"))
            remote = row.get("remote") is True
            location = str(row.get("location") or "").strip()
            parsed_city, parsed_country = parse_city_country(location) if not remote else (None, None)
            physical_country = None if remote else parsed_country or "DE"
            city = None if remote else parsed_city or location or None
            jobs.append(
                NormalizedJob(
                    source=ArbeitnowSource.source_id,
                    source_job_id=str(row["slug"]),
                    title=title,
                    company=str(row.get("company_name") or ""),
                    description=description,
                    url=str(row.get("url") or ""),
                    # A remote posting's free-form location may be an office
                    # or scope label, not the employee's work country.
                    country=physical_country,
                    city=city,
                    work_mode="remote" if remote else "onsite",
                    remote_scope=remote_location_restriction(row.get("location")) if remote else None,
                    relocation=support["relocation"],
                    visa_sponsorship=support["visa_sponsorship"],
                    skills=tags,
                    published_at=published.isoformat() if published else None,
                    raw={**row, "source_location": location or None,
                         "location_resolution": "provider_location_city_country" if parsed_country else None},
                )
            )
        return jobs

    async def discover(self, context: SourceContext) -> list[NormalizedJob]:
        self.retry_count = 0
        headers = {"User-Agent": "JobAgentV3/0.1 (job discovery client)"}
        async with httpx.AsyncClient(timeout=self.request_timeout_seconds) as client:
            for attempt in range(self.request_retries + 1):
                try:
                    response = await client.get(self.endpoint, headers=headers)
                    response.raise_for_status()
                    payload = response.json()
                    break
                except httpx.TransportError as exc:
                    if attempt >= self.request_retries:
                        raise
                    log.warning(
                        "Arbeitnow transport failure (%s); retry %s/%s",
                        type(exc).__name__, attempt + 1, self.request_retries,
                    )
                    self.retry_count += 1
                    await asyncio.sleep(0.5 * (2 ** attempt))
        return self.parse_payload(payload, context)
