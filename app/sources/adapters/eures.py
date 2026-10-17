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
from app.sources.diagnostics import classify_source_error, SourceInvalidResponse
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
                self.retry_count = getattr(self, "retry_count", 0) + 1
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
        if not isinstance(payload, dict) or not isinstance(payload.get("jvs"), list):
            raise SourceInvalidResponse("EURES search contract unavailable")
        tokens = cls._query_tokens(query)
        jobs = []
        for row in payload["jvs"]:
            if not isinstance(row, dict) or not row.get("id") or not row.get("title"):
                continue
            # The endpoint can return broad/fuzzy matches. Require a meaningful
            # whole query token in the title so fuzzy substring matches do
            # not let e.g. Java return JavaScript roles.
            title = str(row["title"])
            title_folded = title.casefold()
            if tokens and not any(
                re.search(rf"(?<!\w){re.escape(token)}(?!\w)", title_folded)
                for token in tokens
            ):
                continue
            if row.get("euresFlag") is not True:
                continue
            location_map = row.get("locationMap")
            if not isinstance(location_map, dict):
                # Location and employer blocks are optional search metadata.
                # A malformed block must not discard valid sibling listings.
                location_map = {}
            country = next(iter(location_map), None)
            employer = row.get("employer")
            if not isinstance(employer, dict):
                employer = {}
            jobs.append(NormalizedJob(
                source=cls.source_id,
                source_job_id=str(row["id"]),
                title=title,
                company=str(employer.get("name") or ""),
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
        if not isinstance(payload, dict) or not isinstance(payload.get("jvProfiles"), dict):
            raise SourceInvalidResponse("EURES detail contract unavailable")
        profiles = payload["jvProfiles"]
        profile = profiles.get("en") or next(iter(profiles.values()), {})
        if not isinstance(profile, dict) or not profile:
            raise SourceInvalidResponse("EURES detail contract unavailable")
        job.title = str(profile.get("title") or job.title)
        job.description = clean_html_text(str(profile.get("description") or job.description))
        locations = profile.get("locations") or []
        if locations and isinstance(locations[0], dict):
            location = locations[0]
            job.country = str(location.get("countryCode") or job.country or "").upper() or None
            raw_city = str(location.get("cityName") or "")
            normalized_city = re.sub(r"\s+", " ", raw_city).strip()
            # EURES sometimes pads the location with long whitespace blocks.
            # Normalize them before saving to the bounded city column. If the
            # remaining value is still too long to be a useful city label, keep
            # it as source evidence and leave city unknown.
            if normalized_city and len(normalized_city) <= 256:
                job.city = normalized_city
            else:
                job.city = None
                if raw_city:
                    job.raw["location_text"] = raw_city
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
        self.partial_failures = 0
        self.retry_count = 0
        self.discovery_diagnostics = []
        queries = list(dict.fromkeys(str(q).strip() for q in (context.queries or []) if str(q).strip()))
        if not queries:
            return []
        # In the deployed container, EURES compressed response bodies failed
        # during TLS reads after returning HTTP 200. Identity encoding returned
        # complete JSON consistently in a live contract check.
        headers = {
            "User-Agent": "JobAgentV3/3.5 (public job discovery)",
            "Accept": "application/json",
            "Accept-Encoding": "identity",
        }
        found: dict[str, NormalizedJob] = {}
        source_errors: list[Exception] = []
        async with httpx.AsyncClient(timeout=25, follow_redirects=True, headers=headers) as client:
            successful_searches = 0
            for index, query in enumerate(queries[: self.max_queries], start=1):
                try:
                    response = await self._request_with_retry(
                        client.post, self.search_endpoint, json=self.request_payload(query)
                    )
                    parsed = self.parse_search(response.json(), query)
                except (httpx.HTTPError, ssl.SSLError, ValueError, TypeError, KeyError, AttributeError) as exc:
                    source_errors.append(exc)
                    self.discovery_diagnostics.append({**classify_source_error(exc, action="continue_partial"), "operation": "search_request"})
                    self.partial_failures += 1
                    log.warning(
                        "EURES search %s failed (%s); continuing",
                        index, f"HTTP {exc.response.status_code}" if isinstance(exc, httpx.HTTPStatusError) else type(exc).__name__,
                    )
                    continue
                successful_searches += 1
                for job in parsed:
                    found.setdefault(job.source_job_id, job)
            if successful_searches == 0 and source_errors:
                raise source_errors[-1]
            enriched = []
            detail_errors: list[Exception] = []
            for job in list(found.values())[: self.max_details]:
                try:
                    response = await self._request_with_retry(client.get, job.raw["evidence_url"])
                    enriched_job = self.enrich(job, response.json())
                except (httpx.HTTPError, ssl.SSLError, ValueError, TypeError, KeyError, AttributeError) as exc:
                    detail_errors.append(exc)
                    self.discovery_diagnostics.append({**classify_source_error(exc, action="continue_partial"), "operation": "detail_request"})
                    self.partial_failures += 1
                    log.warning(
                        "EURES detail request failed (%s); skipping vacancy",
                        f"HTTP {exc.response.status_code}" if isinstance(exc, httpx.HTTPStatusError) else type(exc).__name__,
                    )
                    continue
                enriched.append(enriched_job)
            if not enriched and detail_errors:
                raise detail_errors[-1]
            return enriched
