from __future__ import annotations

import asyncio
import logging
import re
import ssl
import uuid
from datetime import datetime, timezone
from urllib.parse import quote, urlparse

import httpx
from bs4 import BeautifulSoup

from app.domain.jobs import NormalizedJob, SourceCapabilities
from app.domain.job_text import clean_html_text
from app.sources.base import JobSource, SourceContext

log = logging.getLogger(__name__)


class EuresSource(JobSource):
    """Public EURES vacancies explicitly flagged for cross-border recruitment."""

    source_id = "eures"
    name = "EURES"
    capabilities = SourceCapabilities(True, True, False, False)
    search_endpoint = "https://europa.eu/eures/api/jv-searchengine/public/jv-search/search"
    detail_endpoint = "https://europa.eu/eures/api/jv-searchengine/public/jv/id/{}"
    portal_url = "https://eures.europa.eu/portal/jv-se/home?lang=en&pageCode=find_a_job"
    max_queries = 6
    max_details = 8
    request_retries = 2

    async def _request_with_retry(self, request, *args, **kwargs):
        """Retry transient transport failures without masking HTTP responses."""
        for attempt in range(self.request_retries + 1):
            try:
                response = await request(*args, **kwargs)
                response.raise_for_status()
                return response
            except (httpx.TransportError, ssl.SSLError) as exc:
                if attempt >= self.request_retries:
                    raise
                log.warning(
                    "EURES transport failure (%s); retry %s/%s",
                    type(exc).__name__, attempt + 1, self.request_retries,
                )
                await asyncio.sleep(0.5 * (2 ** attempt))

    @staticmethod
    def request_payload(query: str, page: int = 1) -> dict:
        return {
            "resultsPerPage": 50,
            "page": page,
            "sortSearch": "MOST_RECENT",
            "keywords": [{"keyword": query, "specificSearchCode": "EVERYWHERE"}],
            "publicationPeriod": None,
            "occupationUris": [],
            "skillUris": [],
            "requiredExperienceCodes": [],
            "positionScheduleCodes": [],
            "sectorCodes": [],
            "educationAndQualificationLevelCodes": [],
            "positionOfferingCodes": [],
            "locationCodes": [],
            "euresFlagCodes": ["WITH"],
            "otherBenefitsCodes": [],
            "requiredLanguages": [],
            "minNumberPost": None,
            "sessionId": str(uuid.uuid4()),
            "userPreferredLanguage": None,
            "requestLanguage": "en",
        }

    @staticmethod
    def _query_tokens(query: str) -> list[str]:
        return [token for token in re.findall(r"[\w+#.-]+", query.casefold()) if len(token) > 2]

    @classmethod
    def parse_search(cls, payload: dict, query: str) -> list[NormalizedJob]:
        if not isinstance(payload.get("jvs"), list):
            raise ValueError("EURES search contract unavailable")
        tokens = cls._query_tokens(query)
        jobs = []
        for row in payload["jvs"]:
            if not isinstance(row, dict) or not row.get("id") or not row.get("title"):
                continue
            # The endpoint can return broad/fuzzy matches. Require a meaningful
            # query token in the title so unrelated vacancies do not leak in.
            title = str(row["title"])
            if tokens and not any(token in title.casefold() for token in tokens):
                continue
            if row.get("euresFlag") is not True:
                continue
            location_map = row.get("locationMap") or {}
            country = next(iter(location_map), None)
            jobs.append(NormalizedJob(
                source=cls.source_id,
                source_job_id=str(row["id"]),
                title=title,
                company=str((row.get("employer") or {}).get("name") or ""),
                description=clean_html_text(str(row.get("description") or "")),
                url=cls.portal_url,
                country=str(country).upper() if country else None,
                published_at=cls._timestamp(row.get("creationDate")),
                raw={
                    "eures_flag": True,
                    "international_candidates": True,
                    "international_candidates_evidence": "Employer-marked EURES vacancy for cross-border recruitment",
                    "evidence_url": f"https://europa.eu/eures/api/jv-searchengine/public/jv/id/{quote(str(row['id']), safe='')}?requestLang=en",
                    "location_map": location_map,
                    "source_summary": row,
                },
            ))
        return jobs

    @staticmethod
    def _timestamp(value) -> str | None:
        if not isinstance(value, (int, float)):
            return None
        try:
            return datetime.fromtimestamp(value / 1000, tz=timezone.utc).isoformat()
        except (OverflowError, OSError, ValueError):
            return None

    @classmethod
    def enrich(cls, job: NormalizedJob, payload: dict) -> NormalizedJob:
        profiles = payload.get("jvProfiles") or {}
        profile = profiles.get("en") or next(iter(profiles.values()), {})
        if not isinstance(profile, dict) or not profile:
            raise ValueError("EURES detail contract unavailable")
        job.title = str(profile.get("title") or job.title)
        job.description = clean_html_text(str(profile.get("description") or job.description))
        locations = profile.get("locations") or []
        if locations and isinstance(locations[0], dict):
            location = locations[0]
            job.country = str(location.get("countryCode") or job.country or "").upper() or None
            job.city = str(location.get("cityName") or "").strip() or None
        job.company = str((profile.get("employer") or {}).get("name") or job.company)

        # Preserve a verified, source-provided application destination when one
        # exists. EURES flags are about cross-border recruitment; they do not
        # imply visa sponsorship or relocation benefits.
        instructions = profile.get("applicationInstructions") or []
        for instruction in instructions:
            soup = BeautifulSoup(str(instruction), "html.parser")
            for anchor in soup.select("a[href]"):
                target = str(anchor.get("href") or "")
                if urlparse(target).scheme == "https" and urlparse(target).netloc:
                    job.url = target
                    break
            if job.url != cls.portal_url:
                break
        job.raw["eures_flag"] = profile.get("euresFlag") is True
        job.raw["international_candidates"] = True if profile.get("euresFlag") is True else None
        job.raw["international_candidates_evidence"] = (
            "Employer-marked EURES vacancy for cross-border recruitment"
            if profile.get("euresFlag") is True else None
        )
        job.raw["evidence_url"] = (
            f"https://europa.eu/eures/api/jv-searchengine/public/jv/id/{quote(job.source_job_id, safe='')}?requestLang=en"
        )
        # EURES does not turn this flag into visa/relocation support claims.
        job.visa_sponsorship = None
        job.relocation = None
        return job

    async def discover(self, context: SourceContext) -> list[NormalizedJob]:
        queries = list(dict.fromkeys(str(q).strip() for q in (context.queries or []) if str(q).strip()))
        if not queries:
            return []
        headers = {"User-Agent": "JobAgentV3/3.5 (public job discovery)", "Accept": "application/json"}
        found: dict[str, NormalizedJob] = {}
        transport_errors: list[Exception] = []
        async with httpx.AsyncClient(timeout=25, follow_redirects=True, headers=headers) as client:
            successful_searches = 0
            for index, query in enumerate(queries[: self.max_queries], start=1):
                try:
                    response = await self._request_with_retry(
                        client.post, self.search_endpoint, json=self.request_payload(query)
                    )
                except (httpx.TransportError, ssl.SSLError) as exc:
                    transport_errors.append(exc)
                    log.warning(
                        "EURES search %s failed after retries (%s); continuing",
                        index, type(exc).__name__,
                    )
                    continue
                successful_searches += 1
                for job in self.parse_search(response.json(), query):
                    found.setdefault(job.source_job_id, job)
            if successful_searches == 0 and transport_errors:
                raise transport_errors[-1]
            enriched = []
            for job in list(found.values())[: self.max_details]:
                try:
                    response = await self._request_with_retry(client.get, job.raw["evidence_url"])
                except (httpx.TransportError, ssl.SSLError) as exc:
                    transport_errors.append(exc)
                    log.warning(
                        "EURES detail request failed after retries (%s); skipping vacancy",
                        type(exc).__name__,
                    )
                    continue
                enriched.append(self.enrich(job, response.json()))
            if not enriched and transport_errors:
                raise transport_errors[-1]
            return enriched
