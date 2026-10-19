from __future__ import annotations

import asyncio
import re
from datetime import UTC, datetime
from urllib.parse import urlparse

import httpx

from app.domain.job_text import clean_html_text
from app.domain.jobs import NormalizedJob, SourceCapabilities
from app.geo.countries import normalize_country
from app.geo.locations import parse_city_country
from app.sources.diagnostics import classify_source_error, diagnostic
from app.sources.base import JobSource, SourceContext
from app.sources.employer_watchlist import enabled_employers, load_employer_watchlist


class EmployerCareerWatchSource(JobSource):
    """Discover real jobs from owner-reviewed employer career sources.

    ATS feeds are queried live; custom pages use the checked-in validated
    opening. Provider IDs and official links are retained. Country/city and
    hiring evidence remain unknown instead of being inferred from market tags.
    """

    source_id = "employer_career_watch"
    name = "Employer Career Watch"
    capabilities = SourceCapabilities(discovery=True, details=False, apply=False, messages=False)
    timeout_seconds = 8.0
    max_rows_per_board = 500
    already_covered_employers = {"collectly", "devexperts"}

    @staticmethod
    def _safe_url(value: object, employer) -> str | None:
        if not isinstance(value, str):
            return None
        try:
            parsed = urlparse(value.strip())
            port = parsed.port
        except ValueError:
            return None
        if (
            parsed.scheme != "https" or not parsed.hostname
            or parsed.hostname.casefold() not in employer.allowed_hosts
            or parsed.username is not None or parsed.password is not None
            or port not in {None, 443} or parsed.fragment
        ):
            return None
        return value.strip()

    @staticmethod
    def _matches_query(title: str, queries: list[str] | None) -> bool:
        if not queries:
            return True
        title_tokens = set(re.findall(r"[\w+#.-]+", title.casefold()))
        generic = {"admin", "administrator", "engineer", "инженер", "lead", "manager", "менеджер", "senior", "specialist", "специалист", "staff"}
        for query in queries:
            tokens = set(re.findall(r"[\w+#.-]+", query.casefold()))
            meaningful = tokens - generic or tokens
            if meaningful and title_tokens.intersection(meaningful):
                return True
        return False

    @staticmethod
    def _reviewed_opening(employer, provider_id: str, title: str):
        """Return the exact reviewed inventory row, without broad title inference."""
        normalized_title = " ".join(title.casefold().split())
        return next(
            (
                opening
                for opening in employer.openings
                if opening.provider_id == provider_id
                and " ".join(opening.title.casefold().split()) == normalized_title
            ),
            None,
        )

    @classmethod
    def parse_board_payload(cls, employer, payload: object, context: SourceContext) -> list[NormalizedJob]:
        if employer.ats == "greenhouse":
            rows = payload.get("jobs") if isinstance(payload, dict) else None
        elif employer.ats == "smartrecruiters":
            rows = payload.get("content") if isinstance(payload, dict) else None
        elif employer.ats == "lever":
            rows = payload
        else:
            raise ValueError("employer has no supported public ATS feed")
        if not isinstance(rows, list):
            raise ValueError("public ATS response contract changed")

        jobs: list[NormalizedJob] = []
        for row in rows[:cls.max_rows_per_board]:
            if not isinstance(row, dict) or isinstance(row.get("id"), bool) or not isinstance(row.get("id"), (str, int)):
                continue
            provider_id = str(row["id"]).strip()
            if not provider_id or len(provider_id) > 128:
                continue
            title_value = row.get("title") if employer.ats == "greenhouse" else (
                row.get("text") if employer.ats == "lever" else row.get("name")
            )
            title = title_value.strip() if isinstance(title_value, str) else ""
            reviewed_opening = cls._reviewed_opening(employer, provider_id, title) if title else None
            if not title or (not reviewed_opening and not cls._matches_query(title, context.queries)):
                continue
            url_value = row.get("absolute_url") if employer.ats == "greenhouse" else (
                row.get("hostedUrl") if employer.ats == "lever" else row.get("postingUrl")
            )
            url = cls._safe_url(url_value, employer)
            if not url:
                continue

            location_value = row.get("location")
            if isinstance(location_value, dict):
                location = location_value.get("name")
                if not location and employer.ats == "smartrecruiters":
                    location = ", ".join(
                        str(location_value.get(key) or "").strip()
                        for key in ("city", "region", "country")
                        if str(location_value.get(key) or "").strip()
                    )
            elif employer.ats == "lever":
                categories = row.get("categories")
                location = categories.get("location") if isinstance(categories, dict) else None
            else:
                location = location_value
            source_location = str(location or "").strip()
            workplace_type = str(row.get("workplaceType") or "").strip().casefold()
            is_remote = (
                workplace_type == "remote"
                or row.get("remote") is True
                or (isinstance(location_value, dict) and location_value.get("remote") is True)
                or bool(re.search(r"\bremote\b", source_location, re.I))
            )
            city, country = parse_city_country(source_location) if not is_remote else (None, None)
            location_resolution = None
            if employer.ats == "smartrecruiters" and isinstance(location_value, dict) and not is_remote:
                structured_country = normalize_country(str(location_value.get("country") or ""))
                structured_city = str(location_value.get("city") or "").strip()
                if structured_country and structured_city and len(structured_city) <= 96:
                    city, country = structured_city, structured_country
                    location_resolution = "provider_structured_country_city"
            elif country:
                location_resolution = (
                    "provider_location_city_country" if city else "provider_location_country"
                )
            description = ""
            if employer.ats == "greenhouse":
                description = clean_html_text(str(row.get("content") or ""))
            elif employer.ats == "lever":
                description = clean_html_text(str(row.get("descriptionPlain") or row.get("descriptionBodyPlain") or ""))
            jobs.append(NormalizedJob(
                source=cls.source_id,
                source_job_id=f"{employer.id}:{provider_id}",
                title=title,
                company=employer.name,
                description=description,
                url=url,
                country=country,
                city=city,
                raw={
                    "provider": employer.ats,
                    "provider_id": provider_id,
                    "employer_id": employer.id,
                    "industry_tags": list(employer.industry_tags),
                    "employer_careers_url": employer.careers_url,
                    "source_location": source_location or None,
                    "location_resolution": location_resolution,
                    "watchlist_verified_at": load_employer_watchlist().verified_at.isoformat(),
                    "provider_feed_observed_at": datetime.now(UTC).isoformat(),
                    "curated_suitability": reviewed_opening.suitability if reviewed_opening else None,
                    "reviewed_inventory_match": bool(reviewed_opening),
                    "work_authorization_evidence": "unknown",
                    "visa_sponsorship_evidence": "unknown",
                    "relocation_evidence": "unknown",
                },
            ))
        return jobs

    async def discover(self, context: SourceContext) -> list[NormalizedJob]:
        catalog = load_employer_watchlist()
        employers = enabled_employers()
        self.partial_failures = 0
        self.discovery_diagnostics = []
        jobs: list[NormalizedJob] = []

        # Custom pages have no reviewed JSON contract; retain only their verified
        # catalog entries. Public ATS boards are queried live with bounded fanout.
        for employer in employers:
            if employer.api_url:
                continue
            for opening in employer.openings:
                if self._matches_query(opening.title, context.queries):
                    jobs.append(NormalizedJob(
                        source=self.source_id,
                        source_job_id=f"{employer.id}:{opening.provider_id}",
                        title=opening.title,
                        company=employer.name,
                        url=opening.url,
                        raw={
                            "provider": employer.ats,
                            "provider_id": opening.provider_id,
                            "employer_id": employer.id,
                            "employer_careers_url": employer.careers_url,
                            "source_location": opening.location,
                            "catalog_verified_at": catalog.verified_at.isoformat(),
                            "curated_suitability": opening.suitability,
                            "work_authorization_evidence": opening.work_authorization,
                            "visa_sponsorship_evidence": opening.visa_sponsorship,
                            "relocation_evidence": opening.relocation,
                        },
                    ))

        # Avoid re-fetching boards already served by dedicated maintained
        # adapters; canonical dedupe remains a second line of defense.
        api_employers = [item for item in employers if item.api_url and item.id not in self.already_covered_employers]
        semaphore = asyncio.Semaphore(4)
        headers = {"Accept": "application/json", "User-Agent": "PersonalAIJobAgent/3.5.7 (read-only employer watch)"}
        async with httpx.AsyncClient(timeout=self.timeout_seconds, headers=headers, follow_redirects=False) as client:
            async def fetch(employer):
                params = {"content": "true"} if employer.ats == "greenhouse" else (
                    {"mode": "json", "limit": 100} if employer.ats == "lever" else {"limit": 100, "offset": 0}
                )
                try:
                    async with semaphore:
                        async with asyncio.timeout(self.timeout_seconds + 2):
                            response = await client.get(employer.api_url, params=params)
                            response.raise_for_status()
                            return self.parse_board_payload(employer, response.json(), context)
                except Exception as exc:
                    self.partial_failures += 1
                    self.discovery_diagnostics.append(classify_source_error(exc))
                    return []

            results = await asyncio.gather(*(fetch(employer) for employer in api_employers))
        jobs.extend(job for group in results for job in group)
        if self.partial_failures:
            self.discovery_diagnostics.append(diagnostic("SOURCE_PARTIAL_RESULTS", action="continue_partial", count=self.partial_failures))
        return jobs
