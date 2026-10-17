from __future__ import annotations

import asyncio
import logging
import math
import re
from urllib.parse import urlparse

import httpx

from app.domain.job_text import clean_html_text
from app.domain.jobs import NormalizedJob, SourceCapabilities
from app.domain.remote_evidence import remote_residence_requirement
from app.domain.vacancy_availability import listing_expiry_metadata, source_datetime
from app.geo.countries import normalize_country
from app.sources.diagnostics import SourceInvalidResponse, classify_source_error
from app.sources.base import JobSource, SourceContext
from app.sources.query_plan import remote_discovery_queries


log = logging.getLogger(__name__)


class HimalayasSource(JobSource):
    """Country-filtered remote job search through Himalayas' public API."""

    source_id = "himalayas"
    name = "Himalayas Remote Jobs"
    capabilities = SourceCapabilities(discovery=True, details=True, apply=False, messages=False)
    endpoint = "https://himalayas.app/jobs/api/search"
    request_timeout_seconds = 20.0
    max_queries = 4
    max_markets = 3
    results_per_request = 20
    max_remote_scope_length = 128
    user_agent = "PersonalAIJobAgent/3.5.7 (public job discovery; https://github.com/Qrasann/personal-ai-job-agent)"

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return set(re.findall(r"[\w+#.-]+", (text or "").casefold()))

    @classmethod
    def _matches_role(cls, row: dict, queries: list[str] | None) -> bool:
        if not queries:
            return True
        generic = {
            "admin", "administrator", "engineer", "инженер", "lead", "manager",
            "менеджер", "senior", "specialist", "специалист", "staff", "разработчик",
        }
        searchable = " ".join(
            [
                str(row.get("title") or ""),
                *(str(value) for value in row.get("categories", []) if value),
                *(str(value) for value in row.get("parentCategories", []) if value),
            ]
        )
        title_tokens = cls._tokens(searchable)
        for query in queries:
            query_tokens = cls._tokens(query)
            meaningful = query_tokens - generic or query_tokens
            if meaningful and title_tokens & meaningful:
                return True
        return False

    @staticmethod
    def _restriction_values(row: dict) -> list[str]:
        values = row.get("locationRestrictions")
        if not isinstance(values, list):
            return []
        result: list[str] = []
        for value in values:
            if isinstance(value, str):
                text = value.strip()
            elif isinstance(value, dict):
                text = str(value.get("name") or value.get("alpha2") or value.get("slug") or "").strip()
            else:
                continue
            if text:
                result.append(text)
        return result

    @staticmethod
    def _amount(value: object) -> int | None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        if isinstance(value, float) and not math.isfinite(value):
            return None
        # Existing PostgreSQL salary columns are signed 32-bit Integer.
        # Invalid optional metadata must not abort discovery or overflow writes.
        if not 0 < value <= 2**31 - 1:
            return None
        number = int(value)
        return number if number == value and number > 0 else None

    @staticmethod
    def _published_at(value: object) -> str | None:
        parsed = source_datetime(value)
        return parsed.isoformat() if parsed else None

    @classmethod
    def parse_payload(cls, payload: dict, context: SourceContext) -> list[NormalizedJob]:
        rows = payload.get("jobs") if isinstance(payload, dict) else None
        if not isinstance(rows, list):
            raise SourceInvalidResponse("Himalayas Jobs API contract unavailable")

        markets = cls._markets(context)
        selected_countries = {country for country in markets if country}
        jobs: list[NormalizedJob] = []
        for row in rows:
            if not isinstance(row, dict) or not row.get("title"):
                continue
            if not cls._matches_role(row, context.queries):
                continue

            restriction_field = row.get("locationRestrictions")
            restrictions = cls._restriction_values(row)
            worldwide = (
                isinstance(restriction_field, list)
                and not restriction_field
            ) or any(
                value.casefold() in {"worldwide", "global", "anywhere"}
                for value in restrictions
            )
            restricted_countries = {
                normalized
                for value in restrictions
                if (normalized := normalize_country(value))
            }
            matched_countries = [country for country in markets if country in restricted_countries]
            if restrictions and not worldwide and not matched_countries:
                # Keep the source's country limits authoritative. An unknown
                # region such as EMEA is not assumed to include the user's
                # selected destination.
                continue

            application_link = str(row.get("applicationLink") or "").strip()
            try:
                parsed_url = urlparse(application_link)
                safe_application_link = (
                    len(application_link) <= 2048
                    and parsed_url.scheme.casefold() == "https"
                    and parsed_url.hostname in {"himalayas.app", "www.himalayas.app"}
                    and parsed_url.username is None
                    and parsed_url.password is None
                    and parsed_url.port in {None, 443}
                )
            except ValueError:
                safe_application_link = False
            if not safe_application_link:
                continue

            description = clean_html_text(str(row.get("description") or row.get("excerpt") or ""))
            residence_requirement = remote_residence_requirement(description)
            location_scope = (
                residence_requirement or "worldwide"
                if worldwide
                else ", ".join(dict.fromkeys(restrictions)) if restrictions else "unknown"
            )
            if len(location_scope) > cls.max_remote_scope_length:
                location_scope = location_scope[: cls.max_remote_scope_length - 1] + "…"
            raw = {
                "source_url": application_link,
                "location_restrictions": restrictions,
                "timezone_restrictions": row.get("timezoneRestrictions") or row.get("timezoneRestriction") or [],
                "employment_type": row.get("employmentType"),
                "seniority": row.get("seniority"),
                "salary_period": row.get("salaryPeriod") or "annual",
                "source_salary_min": row.get("minSalary"),
                "source_salary_max": row.get("maxSalary"),
                "source_currency": row.get("currency"),
                "categories": row.get("categories") or [],
                "availability": listing_expiry_metadata(row.get("expiryDate")),
            }
            jobs.append(
                NormalizedJob(
                    source=cls.source_id,
                    source_job_id=str(row.get("guid") or application_link),
                    title=str(row["title"]).strip(),
                    company=str(row.get("companyName") or "").strip(),
                    description=description,
                    url=application_link,
                    country=None if worldwide or not restrictions else matched_countries[0],
                    work_mode="remote",
                    remote_scope=location_scope,
                    salary_from=cls._amount(row.get("minSalary")),
                    salary_to=cls._amount(row.get("maxSalary")),
                    salary_currency=str(row.get("currency") or "").upper() or None,
                    salary_period=str(row.get("salaryPeriod") or "annual").casefold(),
                    published_at=cls._published_at(row.get("pubDate")),
                    skills=[str(value) for value in (row.get("categories") or []) if value],
                    raw=raw,
                )
            )
        return jobs

    @staticmethod
    def _markets(context: SourceContext) -> list[str | None]:
        target_countries = list(dict.fromkeys(
            country
            for value in (context.target_countries or [])
            if (country := normalize_country(str(value or "")))
        ))
        if target_countries:
            return target_countries[: HimalayasSource.max_markets]
        current = normalize_country(str(context.current_country or ""))
        return [current] if current else [None]

    async def discover(self, context: SourceContext) -> list[NormalizedJob]:
        self.partial_failures = 0
        self.discovery_diagnostics = []
        queries = remote_discovery_queries(context.queries, limit=self.max_queries)
        markets = self._markets(context)
        headers = {"User-Agent": self.user_agent, "Accept": "application/json"}
        unique_rows: dict[str, dict] = {}
        successful_requests = 0
        transport_errors: list[Exception] = []

        async with httpx.AsyncClient(timeout=self.request_timeout_seconds, headers=headers) as client:
            for query in queries or [""]:
                for market in markets:
                    params: dict[str, str | int] = {"sort": "recent", "page": 1}
                    if query:
                        params["q"] = query
                    if market:
                        params["country"] = market
                    else:
                        params["worldwide"] = "true"
                    try:
                        response = await client.get(self.endpoint, params=params)
                        response.raise_for_status()
                        payload = response.json()
                        rows = payload.get("jobs") if isinstance(payload, dict) else None
                        if not isinstance(rows, list):
                            raise SourceInvalidResponse("Himalayas Jobs API contract unavailable")
                        successful_requests += 1
                        for row in rows[: self.results_per_request]:
                            if isinstance(row, dict):
                                key = str(row.get("guid") or row.get("applicationLink") or "")
                                if key:
                                    unique_rows[key] = row
                    except (httpx.TransportError, httpx.HTTPStatusError, SourceInvalidResponse) as exc:
                        transport_errors.append(exc)
                        self.partial_failures += 1
                        self.discovery_diagnostics.append({**classify_source_error(exc, action="continue_partial"), "operation": "search_request"})
                        log.warning(
                            "Himalayas search failed for query=%r country=%s (%s)",
                            query,
                            market or "worldwide",
                            type(exc).__name__,
                        )
                    if len(queries or [""]) * len(markets) > 1:
                        await asyncio.sleep(0.25)

        if successful_requests == 0 and transport_errors:
            raise transport_errors[-1]
        if transport_errors:
            log.warning("Himalayas search completed partially: %s request(s) failed", len(transport_errors))
        return self.parse_payload({"jobs": list(unique_rows.values())}, context)
