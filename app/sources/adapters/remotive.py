from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import UTC
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse

import httpx

from app.domain.job_text import clean_html_text
from app.domain.jobs import NormalizedJob, SourceCapabilities
from app.geo.countries import load_country_catalog, normalize_country
from app.domain.vacancy_availability import source_datetime
from app.sources.diagnostics import SourceInvalidResponse
from app.sources.base import JobSource, SourceContext


class RemotiveSource(JobSource):
    """Daily, bounded discovery from Remotive's public DevOps/Sysadmin feed."""

    source_id = "remotive"
    name = "Remotive Remote Jobs"
    capabilities = SourceCapabilities(discovery=True, details=True, apply=False, messages=False)
    # The API currently ignores category query parameters and returns a broad
    # feed. Remotive's official RSS feed is scoped to this category.
    endpoint = "https://remotive.com/remote-jobs/devops/feed"
    category = "Devops"
    result_limit = 250
    request_timeout_seconds = 20.0
    max_remote_scope_length = 160
    user_agent = "PersonalAIJobAgent/3.5.7 (public job discovery; https://github.com/Qrasann/personal-ai-job-agent)"
    # Common location labels not present in this app's selectable-country catalog.
    _external_country_aliases = {
        "US": ("United States", "United States of America", "USA", "U.S.A.", "U.S.", "US"),
        "GB": ("United Kingdom", "UK", "Great Britain", "Britain"),
        "CA": ("Canada",),
        "AU": ("Australia",),
        "IN": ("India",),
        "IL": ("Israel",),
        "BR": ("Brazil",),
        "MX": ("Mexico",),
        "PH": ("Philippines",),
        "SG": ("Singapore",),
        "CH": ("Switzerland",),
        "NZ": ("New Zealand",),
    }

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
            if meaningful and title_tokens & meaningful:
                return True
        return False

    @staticmethod
    def _worldwide(location: str) -> bool:
        return bool(re.search(
            r"\b(?:worldwide|global|anywhere(?:\s+in\s+the\s+world)?|work\s+from\s+anywhere|all\s+countries)\b",
            location,
            re.I,
        ))

    @staticmethod
    def _published_at(value: object) -> str | None:
        """Normalize Remotive ISO/API and RFC 2822/RSS dates to UTC."""
        if not isinstance(value, str) or not value.strip() or len(value) > 128:
            return None
        parsed = source_datetime(value)
        if parsed is None:
            try:
                parsed = parsedate_to_datetime(value.strip())
                if parsed.tzinfo is None or parsed.utcoffset() is None:
                    return None
                parsed = parsed.astimezone(UTC)
            except (TypeError, ValueError, OverflowError):
                return None
        return parsed.astimezone(UTC).isoformat()

    @classmethod
    def _country_codes_in_location(cls, location: str) -> set[str]:
        text = location.casefold()
        codes: set[str] = set()
        catalog = load_country_catalog().get("countries", {})
        for code, cfg in catalog.items():
            names = [cfg.get("name", ""), *(cfg.get("aliases") or [])]
            for name in names:
                name = str(name).strip()
                if name and re.search(rf"(?<!\w){re.escape(name.casefold())}(?!\w)", text):
                    codes.add(str(code).upper())
                    break
        for code, names in cls._external_country_aliases.items():
            for name in names:
                if re.search(rf"(?<!\w){re.escape(name.casefold())}(?!\w)", text):
                    codes.add(code)
                    break
        # Accept uppercase ISO alpha-2 codes only when they are clearly used
        # as a location token. Lowercase matching would misread ordinary words
        # such as "in" and "am" as country codes.
        known_codes = {str(code).upper() for code in catalog} | set(cls._external_country_aliases)
        for match in re.finditer(r"(?<![A-Za-z])([A-Z]{2})(?![A-Za-z])", location):
            code = match.group(1)
            if code not in known_codes:
                continue
            prefix = location[:match.start()].rstrip()
            suffix = location[match.end():].lstrip()
            clearly_scoped = (
                not prefix and not suffix
                or prefix.endswith((",", "(", "[", "/", "|", "-"))
                or suffix.startswith((",", ")", "]", "/", "|", "-"))
                or re.search(r"\b(?:only|remote|country|based|residents?)\s*$", prefix, re.I)
                or re.match(r"(?:only|remote|country|based|residents?)\b", suffix, re.I)
            )
            if clearly_scoped:
                codes.add(code)
        # "Georgia, USA" refers to the US state, while unqualified "Georgia"
        # remains the country. Do not let the country catalog alias override
        # an explicit country qualifier in the source's hiring-location text.
        if "US" in codes and "GE" in codes and re.search(
            r"\b(?:u\.?s\.?a?\.?|united states(?: of america)?)\b", text, re.I
        ):
            codes.discard("GE")
        return codes

    @classmethod
    def parse_payload(cls, payload: object, context: SourceContext) -> list[NormalizedJob]:
        rows = payload.get("jobs") if isinstance(payload, dict) else None
        if not isinstance(rows, list):
            raise SourceInvalidResponse("Remotive public API contract unavailable")

        market_values = context.target_countries or [context.current_country]
        selected = list(dict.fromkeys(
            code
            for value in market_values
            if (code := normalize_country(str(value or "")))
        ))
        jobs: list[NormalizedJob] = []
        seen: set[str] = set()
        for row in rows:
            if not isinstance(row, dict) or not row.get("id") or not row.get("title"):
                continue
            category = str(row.get("category") or "").strip()
            if "devops" not in category.casefold() and "sysadmin" not in category.casefold():
                continue

            title = str(row["title"]).strip()
            if not cls._matches_role(title, context.queries):
                continue

            url = str(row.get("url") or "").strip()
            parsed_url = urlparse(url)
            if parsed_url.scheme != "https" or parsed_url.hostname not in {"remotive.com", "www.remotive.com"}:
                continue

            location = str(row.get("candidate_required_location") or "").strip()
            worldwide = cls._worldwide(location)
            location_countries = cls._country_codes_in_location(location)
            matched_selected = [code for code in selected if code in location_countries]
            if location_countries and not matched_selected and not worldwide:
                # An explicit country list that excludes the selected market
                # is not treated as a generally available remote opportunity.
                continue
            if re.search(r"\bonly\b", location, re.I) and not matched_selected and not worldwide:
                # Conservative for country/region-specific labels such as
                # "USA Only" or "Europe Only"; region membership is not inferred.
                continue

            row_id = str(row["id"])
            if row_id in seen:
                continue
            seen.add(row_id)
            scope = "worldwide" if worldwide else location or "unknown"
            if len(scope) > cls.max_remote_scope_length:
                scope = scope[: cls.max_remote_scope_length - 1] + "…"
            description = clean_html_text(str(row.get("description") or ""))
            raw = {
                "source_url": url,
                "candidate_required_location": location or None,
                "category": category,
                "job_type": row.get("job_type"),
                "salary_text": row.get("salary"),
                "publication_date": row.get("publication_date"),
            }
            jobs.append(
                NormalizedJob(
                    source=cls.source_id,
                    source_job_id=row_id,
                    title=title,
                    company=str(row.get("company_name") or "").strip(),
                    description=description,
                    url=url,
                    country=matched_selected[0] if matched_selected else None,
                    work_mode="remote",
                    remote_scope=scope,
                    # Remotive's salary field is free text; leave numeric salary
                    # unknown until the source supplies a structured amount.
                    published_at=cls._published_at(row.get("publication_date")),
                    skills=[category] if category else [],
                    raw=raw,
                )
            )
        return jobs

    @staticmethod
    def _local_name(tag: str) -> str:
        return tag.rsplit("}", 1)[-1].casefold()

    @classmethod
    def _xml_text(cls, item: ET.Element, *names: str) -> str:
        wanted = {name.casefold() for name in names}
        for child in item.iter():
            if cls._local_name(child.tag) in wanted:
                value = "".join(child.itertext()).strip()
                if value:
                    return value
        return ""

    @classmethod
    def parse_feed(cls, content: bytes | str) -> dict:
        try:
            root = ET.fromstring(content)
        except ET.ParseError as exc:
            raise SourceInvalidResponse("Remotive RSS feed is malformed") from exc
        if cls._local_name(root.tag) != "rss":
            raise SourceInvalidResponse("Remotive RSS feed contract unavailable")

        rows: list[dict] = []
        for item in root.iter():
            if cls._local_name(item.tag) != "item":
                continue
            title = cls._xml_text(item, "title")
            url = cls._xml_text(item, "link", "url")
            description = cls._xml_text(item, "description", "encoded")
            identifier = cls._xml_text(item, "guid", "id") or url
            if not title or not url or not identifier:
                continue
            rows.append(
                {
                    "id": identifier,
                    "title": title,
                    "company_name": cls._xml_text(item, "company-name", "company_name"),
                    "category": cls._xml_text(item, "category") or cls.category,
                    "job_type": cls._xml_text(item, "job-type", "job_type"),
                    "publication_date": cls._xml_text(item, "pubdate", "publication-date", "published"),
                    "candidate_required_location": cls._xml_text(
                        item, "candidate-location-restriction", "candidate_required_location"
                    ),
                    "salary": cls._xml_text(item, "salary"),
                    "description": description,
                    "url": url,
                }
            )
            if len(rows) >= cls.result_limit:
                break
        return {"jobs": rows, "job-count": len(rows)}

    async def fetch_payload(self) -> dict:
        async with httpx.AsyncClient(
            timeout=self.request_timeout_seconds,
            headers={"User-Agent": self.user_agent, "Accept": "application/rss+xml, application/xml;q=0.9"},
        ) as client:
            response = await client.get(self.endpoint)
            response.raise_for_status()
            content = response.content
        return self.parse_feed(content)

    async def discover(self, context: SourceContext) -> list[NormalizedJob]:
        return self.parse_payload(await self.fetch_payload(), context)
