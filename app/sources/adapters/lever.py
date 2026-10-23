from __future__ import annotations

import re
from urllib.parse import urlparse

import httpx

from app.domain.job_text import clean_html_text
from app.domain.jobs import NormalizedJob, SourceCapabilities
from app.geo.countries import normalize_country
from app.sources.diagnostics import SourceInvalidResponse
from app.sources.base import JobSource, SourceContext


class LeverSource(JobSource):
    """Bounded discovery from Collectly's public Lever Postings API."""

    source_id = "lever"
    name = "Lever · Collectly"
    capabilities = SourceCapabilities(discovery=True, details=True, apply=False, messages=False)
    board_token = "CollectlyInc"
    company = "Collectly"
    endpoint = f"https://api.lever.co/v0/postings/{board_token}"
    supported_countries = frozenset({"AM", "GE"})
    page_size = 100
    request_timeout_seconds = 15.0
    user_agent = "PersonalAIJobAgent/3.5.7 (public job discovery)"
    _ROLE_QUERY_ALIASES = {frozenset({"site", "reliability", "engineer"}): {"sre"}}

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
    def _timezone_scope(text: str) -> str | None:
        match = re.search(
            r"\b(?:GMT|UTC)\s*([+-]\s*\d{1,2})\s*(?:to|through|–|—)\s*(?:GMT|UTC)\s*([+-]\s*\d{1,2})\b",
            text,
            re.I,
        )
        if not match:
            return None

        def offset(value: str) -> int:
            return int(value.replace(" ", ""))

        start, end = offset(match.group(1)), offset(match.group(2))
        lower, upper = sorted((start, end))
        if not lower <= 4 <= upper:
            return None
        return f"GMT{start:+d} to GMT{end:+d} time zones"

    @staticmethod
    def _amount(value: object) -> int | None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        number = int(value)
        return number if number > 0 and number == value else None

    @staticmethod
    def _description(row: dict) -> str:
        parts = [str(row.get("descriptionPlain") or row.get("descriptionBodyPlain") or "")]
        for section in row.get("lists") or []:
            if not isinstance(section, dict):
                continue
            heading = str(section.get("text") or "").strip()
            content = clean_html_text(str(section.get("content") or ""))
            if heading or content:
                parts.append("\n".join(part for part in (heading, content) if part))
        additional = str(row.get("additionalPlain") or "").strip()
        if additional:
            parts.append(additional)
        return clean_html_text("\n\n".join(part for part in parts if part.strip()))

    @classmethod
    def parse_payload(cls, payload: object, context: SourceContext) -> list[NormalizedJob]:
        if not isinstance(payload, list):
            raise SourceInvalidResponse("Lever Postings API contract unavailable")

        selected = {
            normalized
            for code in [context.current_country, *(context.target_countries or [])]
            if (normalized := normalize_country(str(code or "")))
        }
        if not selected.intersection(cls.supported_countries):
            return []

        jobs: list[NormalizedJob] = []
        for row in payload:
            if not isinstance(row, dict) or not row.get("id") or not row.get("text"):
                continue
            title = str(row["text"]).strip()
            if not cls._matches_role(title, context.queries):
                continue

            workplace_type = str(row.get("workplaceType") or "").strip().casefold()
            if workplace_type != "remote":
                continue

            description = cls._description(row)
            timezone_scope = cls._timezone_scope(f"{title}\n{description}")
            if not timezone_scope:
                # The curated feed is enabled only where the current, explicit
                # timezone range includes the target market's UTC+4 timezone.
                continue

            url = str(row.get("hostedUrl") or "").strip()
            parsed_url = urlparse(url)
            if parsed_url.scheme != "https" or parsed_url.hostname not in {"jobs.lever.co", "jobs.eu.lever.co"}:
                continue
            if not parsed_url.path.lstrip("/").startswith(f"{cls.board_token}/"):
                continue

            categories = row.get("categories") if isinstance(row.get("categories"), dict) else {}
            source_location = str(categories.get("location") or "").strip()
            source_country = str(row.get("country") or "").strip().upper() or None
            salary = row.get("salaryRange") if isinstance(row.get("salaryRange"), dict) else {}
            jobs.append(
                NormalizedJob(
                    source=cls.source_id,
                    source_job_id=f"{cls.board_token}:{row['id']}",
                    title=title,
                    company=cls.company,
                    description=description,
                    url=url,
                    # Lever's API lists Belgrade/RS for this remote role. Do
                    # not turn that office metadata into an employee-country
                    # restriction or imply GE/AM hiring eligibility.
                    country=None,
                    work_mode="remote",
                    remote_scope=timezone_scope,
                    salary_from=cls._amount(salary.get("min")),
                    salary_to=cls._amount(salary.get("max")),
                    salary_currency=str(salary.get("currency") or "").upper() or None,
                    salary_period=str(salary.get("interval") or "").casefold() or None,
                    raw={
                        "board_token": cls.board_token,
                        "source_location": source_location,
                        "source_country": source_country,
                        "created_at": row.get("createdAt"),
                        "timezone_scope": timezone_scope,
                        "team": categories.get("team"),
                        "department": categories.get("department"),
                        "commitment": categories.get("commitment"),
                        "source_workplace_type": workplace_type,
                    },
                )
            )
        return jobs

    async def discover(self, context: SourceContext) -> list[NormalizedJob]:
        selected = {
            normalized
            for code in [context.current_country, *(context.target_countries or [])]
            if (normalized := normalize_country(str(code or "")))
        }
        if not selected.intersection(self.supported_countries):
            return []

        async with httpx.AsyncClient(
            timeout=self.request_timeout_seconds,
            headers={"User-Agent": self.user_agent, "Accept": "application/json"},
        ) as client:
            response = await client.get(
                self.endpoint,
                params={"mode": "json", "skip": 0, "limit": self.page_size},
            )
            response.raise_for_status()
            payload = response.json()
        return self.parse_payload(payload, context)
