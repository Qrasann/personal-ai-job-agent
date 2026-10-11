from __future__ import annotations

import re

import httpx

from app.domain.job_text import clean_html_text
from app.domain.jobs import NormalizedJob, SourceCapabilities
from app.sources.base import JobSource, SourceContext
from app.geo.countries import normalize_country


class GreenhouseSource(JobSource):
    """Public Greenhouse discovery for a deliberately curated company board."""

    source_id = "greenhouse"
    name = "Greenhouse · Lineate"
    capabilities = SourceCapabilities(discovery=True, details=True, apply=False, messages=False)
    board_token = "lineate"
    company = "Lineate"
    endpoint = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
    supported_countries = frozenset({"AM", "GE"})
    request_timeout_seconds = 15.0
    user_agent = "PersonalAIJobAgent/3.5.7 (public job discovery)"

    @staticmethod
    def _role_tokens(text: str) -> set[str]:
        return set(re.findall(r"[\w+#.-]+", (text or "").casefold()))

    @classmethod
    def _matches_role(cls, title: str, queries: list[str] | None) -> bool:
        if not queries:
            return True
        generic = {
            "admin", "administrator", "engineer", "инженер", "lead", "manager",
            "менеджер", "senior", "specialist", "специалист", "staff", "разработчик",
        }
        title_tokens = cls._role_tokens(title)
        for query in queries:
            tokens = cls._role_tokens(query)
            meaningful = tokens - generic or tokens
            if meaningful and title_tokens & meaningful:
                return True
        return False

    @staticmethod
    def _country_and_city(location: str) -> tuple[str | None, str | None]:
        normalized = " ".join(location.casefold().split())
        if re.search(r"\b(?:armenia|yerevan)\b", normalized):
            country = "AM"
        elif re.search(r"\b(?:georgia|georgian office|tbilisi|batumi|kutaisi)\b", normalized):
            country = "GE"
        else:
            return None, None

        city = next(
            (
                name
                for name in ("Yerevan", "Tbilisi", "Batumi", "Kutaisi")
                if re.search(rf"\b{re.escape(name.casefold())}\b", normalized)
            ),
            None,
        )
        return country, city

    @staticmethod
    def _support_signals(description: str) -> tuple[bool | None, bool | None, dict[str, str]]:
        patterns = {
            "visa_sponsorship": (
                r"\b(?:we|the company|employer) (?:offer|provide|sponsor(?:s)?)[^.!;]{0,80}\bvisa sponsorship\b",
                r"\b(?:no visa sponsorship|visa sponsorship (?:is )?not (?:available|provided|offered))\b",
            ),
            "relocation": (
                r"\b(?:we|the company|employer) (?:offer|provide)[^.!;]{0,80}\brelocation (?:assistance|support|package)\b",
                r"\b(?:no relocation (?:assistance|support|package)|relocation (?:assistance|support|package) (?:is )?not (?:available|provided|offered))\b",
            ),
        }
        values: dict[str, bool | None] = {}
        evidence: dict[str, str] = {}
        for key, (positive_pattern, negative_pattern) in patterns.items():
            refusal = re.search(negative_pattern, description, re.I)
            offer = re.search(positive_pattern, description, re.I)
            if refusal:
                values[key] = False
                evidence[key] = refusal.group(0)
            elif offer:
                values[key] = True
                evidence[key] = offer.group(0)
            else:
                values[key] = None
        return values["visa_sponsorship"], values["relocation"], evidence

    @classmethod
    def parse_payload(cls, payload: dict, context: SourceContext) -> list[NormalizedJob]:
        rows = payload.get("jobs") if isinstance(payload, dict) else None
        if not isinstance(rows, list):
            raise ValueError("Greenhouse Job Board API contract unavailable")

        selected_countries = {
            normalized
            for code in [context.current_country, *(context.target_countries or [])]
            if (normalized := normalize_country(str(code or "")))
        }
        selected_countries &= cls.supported_countries
        if not selected_countries:
            return []

        jobs: list[NormalizedJob] = []
        for row in rows:
            if not isinstance(row, dict) or not row.get("id") or not row.get("title"):
                continue
            title = str(row["title"]).strip()
            if not title or not cls._matches_role(title, context.queries):
                continue

            location_data = row.get("location")
            location = (
                str(location_data.get("name") or "")
                if isinstance(location_data, dict)
                else str(location_data or "")
            )
            country, city = cls._country_and_city(location)
            if country not in selected_countries:
                continue

            url = str(row.get("absolute_url") or "").strip()
            if not url.startswith("https://"):
                continue
            description = clean_html_text(str(row.get("content") or ""))
            visa_sponsorship, relocation, support_evidence = cls._support_signals(description)
            work_mode = None
            if re.search(r"\bremote\b", location, re.I):
                work_mode = "remote"
            elif re.search(r"\bhybrid\b", location, re.I):
                work_mode = "hybrid"

            jobs.append(
                NormalizedJob(
                    source=cls.source_id,
                    source_job_id=f"{cls.board_token}:{row['id']}",
                    title=title,
                    company=cls.company,
                    description=description,
                    url=url,
                    country=country,
                    city=city,
                    work_mode=work_mode,
                    visa_sponsorship=visa_sponsorship,
                    relocation=relocation,
                    raw={
                        "board_token": cls.board_token,
                        "source_location": location,
                        "updated_at": row.get("updated_at"),
                        "support_evidence": support_evidence,
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
        if not (selected & self.supported_countries):
            return []

        async with httpx.AsyncClient(
            timeout=self.request_timeout_seconds,
            headers={"User-Agent": self.user_agent, "Accept": "application/json"},
        ) as client:
            response = await client.get(self.endpoint, params={"content": "true"})
            response.raise_for_status()
            payload = response.json()
        return self.parse_payload(payload, context)
