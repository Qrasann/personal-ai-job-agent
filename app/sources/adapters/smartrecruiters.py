from __future__ import annotations

import asyncio
import logging
import re
from datetime import UTC, datetime
from urllib.parse import urlparse

import httpx

from app.domain.job_text import clean_html_text
from app.domain.jobs import NormalizedJob, SourceCapabilities
from app.domain.support_evidence import support_evidence
from app.geo.countries import normalize_country
from app.sources.diagnostics import SourceInvalidResponse, classify_source_error
from app.sources.base import JobSource, SourceContext


log = logging.getLogger(__name__)


class SmartRecruitersSource(JobSource):
    """Curated public Devexperts postings for the selected Georgian market.

    The documented Posting API exposes public jobs without authentication.
    Internal postings, application endpoints and untrusted detail URLs are
    deliberately outside this adapter's read-only discovery contract.
    """

    source_id = "smartrecruiters"
    name = "SmartRecruiters · Devexperts"
    capabilities = SourceCapabilities(discovery=True, details=True, apply=False, messages=False)
    company_identifier = "Devexperts"
    company = "Devexperts"
    endpoint = f"https://api.smartrecruiters.com/v1/companies/{company_identifier}/postings"
    supported_countries = frozenset({"GE"})
    page_size = 100
    max_details = 10
    request_timeout_seconds = 10.0
    discovery_timeout_seconds = 60.0
    transport_retries = 1
    retry_delay_seconds = 0.25
    user_agent = "PersonalAIJobAgent/3.5.7 (public job discovery)"
    _ROLE_QUERY_ALIASES = {frozenset({"site", "reliability", "engineer"}): {"sre"}}

    @classmethod
    def _selected(cls, context: SourceContext) -> bool:
        return any(
            normalize_country(str(value or "")) in cls.supported_countries
            for value in [context.current_country, *(context.target_countries or [])]
        )

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return set(re.findall(r"[\w+#.-]+", (text or "").casefold()))

    @classmethod
    def _matches_role(cls, title: str, queries: list[str] | None) -> bool:
        if not queries:
            return True
        generic = {
            "admin", "administrator", "engineer", "инженер", "lead", "manager",
            "менеджер", "senior", "specialist", "специалист", "staff", "разработчик",
        }
        title_tokens = cls._tokens(title)
        for query in queries:
            query_tokens = cls._tokens(query)
            meaningful = query_tokens - generic or query_tokens
            aliases = cls._ROLE_QUERY_ALIASES.get(frozenset(query_tokens), set())
            if meaningful and (title_tokens & meaningful or title_tokens & aliases):
                return True
        return False

    @staticmethod
    def _posting_id(row: dict) -> str | None:
        value = row.get("id")
        if isinstance(value, bool) or not isinstance(value, (str, int)):
            return None
        text = str(value)
        return text if re.fullmatch(r"[0-9]{1,24}", text) else None

    @classmethod
    def _eligible(cls, row: object, context: SourceContext) -> bool:
        if not isinstance(row, dict) or not cls._posting_id(row):
            return False
        title = row.get("name")
        if not isinstance(title, str) or not title.strip() or not cls._matches_role(title, context.queries):
            return False
        location = row.get("location")
        if not isinstance(location, dict) or normalize_country(str(location.get("country") or "")) != "GE":
            return False
        if row.get("active") is False:
            return False
        visibility = row.get("visibility")
        return visibility is None or str(visibility).upper() == "PUBLIC"

    @classmethod
    def _posting_url(cls, row: dict) -> str | None:
        url = row.get("postingUrl")
        if not isinstance(url, str):
            return None
        url = url.strip()
        try:
            parsed = urlparse(url)
        except ValueError:
            return None
        parts = parsed.path.strip("/").split("/")
        posting_id = cls._posting_id(row)
        if (
            parsed.scheme != "https"
            or parsed.hostname != "jobs.smartrecruiters.com"
            or parsed.netloc != "jobs.smartrecruiters.com"
            or parsed.username is not None
            or parsed.password is not None
            or len(parts) != 2
            or parts[0].casefold() != cls.company_identifier.casefold()
            or not posting_id
            or not (parts[1] == posting_id or parts[1].startswith(f"{posting_id}-"))
        ):
            return None
        return url

    @staticmethod
    def _description(row: dict) -> str:
        job_ad = row.get("jobAd")
        sections = job_ad.get("sections") if isinstance(job_ad, dict) else None
        if not isinstance(sections, dict):
            raise SourceInvalidResponse("SmartRecruiters posting details contract unavailable")
        parts: list[str] = []
        for key in ("companyDescription", "jobDescription", "qualifications", "additionalInformation"):
            section = sections.get(key)
            if not isinstance(section, dict):
                continue
            title = clean_html_text(str(section.get("title") or ""))
            text = clean_html_text(str(section.get("text") or ""))
            if title or text:
                parts.append("\n".join(value for value in (title, text) if value))
        return "\n\n".join(parts)

    @staticmethod
    def _published_at(value: object) -> str | None:
        if not isinstance(value, str) or len(value) > 64:
            return None
        try:
            parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
            if parsed.tzinfo is None or parsed.utcoffset() is None:
                return None
            return parsed.astimezone(UTC).isoformat()
        except (ValueError, OverflowError):
            return None

    @classmethod
    def parse_payload(cls, payload: object, context: SourceContext) -> list[NormalizedJob]:
        rows = payload.get("content") if isinstance(payload, dict) else None
        if not isinstance(rows, list):
            raise SourceInvalidResponse("SmartRecruiters Posting API contract unavailable")
        if not cls._selected(context):
            return []

        jobs: list[NormalizedJob] = []
        seen: set[str] = set()
        for row in rows:
            if not cls._eligible(row, context):
                continue
            posting_id = cls._posting_id(row)
            url = cls._posting_url(row)
            if posting_id in seen or not url:
                continue
            description = cls._description(row)
            signals = support_evidence(description)
            location = row["location"]
            # Structured hybrid takes precedence over prose suggesting possible
            # remote work. A remote posting remains restricted to Georgia.
            work_mode = (
                "hybrid" if location.get("hybrid") is True
                else "remote" if location.get("remote") is True
                else "onsite" if location.get("remote") is False and location.get("hybrid") is False
                else None
            )
            raw = {
                "source_url": url,
                "company_identifier": cls.company_identifier,
                "source_location": str(location.get("fullLocation") or location.get("city") or ""),
                "source_country": str(location.get("country") or ""),
                "source_active": row.get("active") if isinstance(row.get("active"), bool) else None,
                "source_visibility": row.get("visibility"),
                "released_date": row.get("releasedDate"),
                "posting_language": row.get("language"),
                "support_evidence": signals,
            }
            jobs.append(NormalizedJob(
                source=cls.source_id,
                source_job_id=f"{cls.company_identifier}:{posting_id}",
                title=row["name"].strip(),
                company=cls.company,
                description=description,
                url=url,
                country="GE",
                city=str(location.get("city") or "").strip() or None,
                work_mode=work_mode,
                remote_scope="Georgia" if work_mode == "remote" else None,
                visa_sponsorship=signals["visa_sponsorship"],
                relocation=signals["relocation"],
                published_at=cls._published_at(row.get("releasedDate")),
                raw=raw,
            ))
            seen.add(posting_id)
        return jobs

    async def _get(self, client: httpx.AsyncClient, url: str, **kwargs) -> httpx.Response:
        for attempt in range(self.transport_retries + 1):
            try:
                response = await client.get(url, **kwargs)
                response.raise_for_status()
                return response
            except httpx.TransportError:
                if attempt == self.transport_retries:
                    raise
                self.retry_count = getattr(self, "retry_count", 0) + 1
                await asyncio.sleep(self.retry_delay_seconds)
        raise AssertionError("unreachable request retry state")

    async def _discover(self, context: SourceContext, verified_jobs: list[NormalizedJob]) -> list[NormalizedJob]:
        async with httpx.AsyncClient(
            timeout=self.request_timeout_seconds,
            headers={"User-Agent": self.user_agent, "Accept": "application/json"},
        ) as client:
            response = await self._get(client, self.endpoint, params={
                "country": "ge", "destination": "PUBLIC", "offset": 0, "limit": self.page_size,
            })
            payload = response.json()
            rows = payload.get("content") if isinstance(payload, dict) else None
            if not isinstance(rows, list):
                raise SourceInvalidResponse("SmartRecruiters Posting API contract unavailable")

            errors: list[Exception] = []
            seen: set[str] = set()
            successful_details = 0
            # One country-filtered page only; never follow feed-provided URLs.
            for row in rows[: self.page_size]:
                if not self._eligible(row, context):
                    continue
                posting_id = self._posting_id(row)
                if posting_id in seen:
                    continue
                if len(seen) >= self.max_details:
                    break
                seen.add(posting_id)
                try:
                    detail = await self._get(client, f"{self.endpoint}/{posting_id}")
                    posting = detail.json()
                    if not isinstance(posting, dict) or self._posting_id(posting) != posting_id:
                        raise SourceInvalidResponse("SmartRecruiters posting details contract unavailable")
                    parsed = self.parse_payload({"content": [posting]}, context)
                    successful_details += 1
                    verified_jobs.extend(parsed)
                except (httpx.TransportError, httpx.HTTPStatusError, ValueError) as exc:
                    errors.append(exc)
                    self.partial_failures += 1
                    self.discovery_diagnostics.append({**classify_source_error(exc, action="continue_partial"), "operation": "detail_request"})
                    log.warning("SmartRecruiters posting %s unavailable (%s)", posting_id, type(exc).__name__)
            if errors and not successful_details:
                raise errors[-1]
            return verified_jobs

    async def discover(self, context: SourceContext) -> list[NormalizedJob]:
        self.partial_failures = 0
        self.discovery_diagnostics = []
        self.retry_count = 0
        if not self._selected(context):
            return []
        verified_jobs: list[NormalizedJob] = []
        budget = asyncio.timeout(self.discovery_timeout_seconds)
        try:
            async with budget:
                return await self._discover(context, verified_jobs)
        except TimeoutError as exc:
            # Keep only already validated, usable postings on our own budget
            # expiry. External task cancellation must continue to propagate.
            if not budget.expired() or not verified_jobs:
                raise
            self.partial_failures += 1
            self.discovery_diagnostics.append(classify_source_error(exc, action="continue_partial"))
            log.warning("SmartRecruiters discovery budget expired; keeping %d verified posting(s)", len(verified_jobs))
            return verified_jobs
