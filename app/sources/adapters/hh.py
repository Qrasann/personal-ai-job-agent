from __future__ import annotations

import json
import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from app.config import settings
from app.domain.jobs import NormalizedJob, SourceCapabilities
from app.domain.job_text import clean_html_text, parse_salary_text, salary_fragment
from app.providers.hh import HHAPIForbidden, HHCaptchaRequired, HHClient
from app.sources.base import JobSource, SourceContext


log = logging.getLogger(__name__)


class HHSource(JobSource):
    source_id = "hh"
    name = "HeadHunter"
    capabilities = SourceCapabilities(discovery=True, details=True, apply=False, messages=False)

    def __init__(self, client: HHClient | None = None) -> None:
        self.client = client or HHClient()

    @staticmethod
    def _clean(value: str) -> str:
        return BeautifulSoup(value or "", "html.parser").get_text(" ", strip=True)

    @staticmethod
    def _combined_query(queries: list[str]) -> str:
        cleaned = [q.strip() for q in queries if q and q.strip()]
        if not cleaned:
            return ""
        if len(cleaned) == 1:
            return cleaned[0]
        return " OR ".join(f'"{q}"' for q in cleaned[:8])

    @staticmethod
    def _salary(text: str) -> tuple[int | None, int | None, str | None]:
        return parse_salary_text(text)

    @staticmethod
    def _first(card: Tag, selectors: tuple[str, ...]) -> Tag | None:
        for selector in selectors:
            found = card.select_one(selector)
            if found:
                return found
        return None

    @classmethod
    def parse_web_html(cls, html: str, *, is_ru: bool = True) -> list[NormalizedJob]:
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select('[data-qa="vacancy-serp__vacancy"]')

        # Fallback for layout changes: find title links and walk up to a card-like container.
        if not cards:
            candidates = soup.select('a[data-qa="serp-item__title"], a[href*="/vacancy/"]')
            seen_nodes: set[int] = set()
            cards = []
            for anchor in candidates:
                parent = anchor
                for _ in range(8):
                    if not getattr(parent, "parent", None):
                        break
                    parent = parent.parent
                    if not isinstance(parent, Tag):
                        break
                    classes = " ".join(parent.get("class") or [])
                    data_qa = parent.get("data-qa", "")
                    if "vacancy-serp" in classes or data_qa == "vacancy-serp__vacancy":
                        break
                if isinstance(parent, Tag) and id(parent) not in seen_nodes:
                    seen_nodes.add(id(parent))
                    cards.append(parent)

        out: list[NormalizedJob] = []
        seen_ids: set[str] = set()
        for card in cards:
            title_node = cls._first(card, (
                'a[data-qa="serp-item__title"]',
                '[data-qa="serp-item__title-text"]',
                'a[href*="/vacancy/"]',
            ))
            if not title_node:
                continue
            anchor = title_node if title_node.name == "a" else title_node.find_parent("a")
            href = (anchor or title_node).get("href", "")
            match = re.search(r"/vacancy/(\d+)", href)
            if not match:
                continue
            job_id = match.group(1)
            if job_id in seen_ids:
                continue
            seen_ids.add(job_id)

            title = title_node.get_text(" ", strip=True)
            company_node = cls._first(card, (
                '[data-qa="vacancy-serp__vacancy-employer"]',
                'a[href*="/employer/"]',
            ))
            salary_node = cls._first(card, (
                '[data-qa="vacancy-serp__vacancy-compensation"]',
                '[data-qa*="compensation"]',
            ))
            address_node = cls._first(card, (
                '[data-qa="vacancy-serp__vacancy-address"]',
                '[data-qa*="vacancy-address"]',
            ))
            req_node = cls._first(card, (
                '[data-qa="vacancy-serp__vacancy_snippet_requirement"]',
                '[data-qa*="snippet_requirement"]',
            ))
            resp_node = cls._first(card, (
                '[data-qa="vacancy-serp__vacancy_snippet_responsibility"]',
                '[data-qa*="snippet_responsibility"]',
            ))

            card_text = card.get_text(" ", strip=True)
            description_parts = [
                node.get_text(" ", strip=True)
                for node in (req_node, resp_node)
                if node and node.get_text(" ", strip=True)
            ]
            # Keep the visible card text as well as the snippets. HH often places
            # seniority/experience/work-format signals outside the requirement
            # snippet, and the matcher needs those signals in fallback mode.
            description = " ".join(description_parts + [card_text])[:3500]
            salary_text = salary_node.get_text(" ", strip=True) if salary_node else ""
            # Current HH layouts sometimes expose a payment-frequency node under
            # compensation selectors instead of the actual salary. Prefer the
            # amount/currency fragment visible in the full card when present.
            card_salary = salary_fragment(card_text)
            if card_salary:
                salary_text = card_salary
            salary_from, salary_to, salary_currency = cls._salary(salary_text)
            city = address_node.get_text(" ", strip=True) if address_node else None
            work_mode = "Удалённо" if "можно удалённо" in card_text.casefold() or "удаленно" in card_text.casefold() or "удалённо" in card_text.casefold() else None

            out.append(NormalizedJob(
                source="hh",
                source_job_id=job_id,
                title=title,
                company=company_node.get_text(" ", strip=True) if company_node else "",
                description=description,
                url=urljoin("https://hh.ru", href),
                country="RU" if is_ru else None,
                city=city,
                work_mode=work_mode,
                salary_from=salary_from,
                salary_to=salary_to,
                salary_currency=salary_currency,
                raw={"transport": "web", "salary_text": salary_text, "card_text": card_text[:5000]},
            ))
        return out


    @classmethod
    def parse_vacancy_web_html(cls, html: str) -> dict:
        """Parse an ordinary public HH vacancy page into display details."""
        soup = BeautifulSoup(html, "html.parser")

        posting: dict = {}
        for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
            raw = script.string or script.get_text()
            try:
                payload = json.loads(raw)
            except Exception:
                continue
            candidates = payload if isinstance(payload, list) else [payload]
            for candidate in candidates:
                if not isinstance(candidate, dict):
                    continue
                if candidate.get("@type") == "JobPosting":
                    posting = candidate
                    break
                for item in candidate.get("@graph", []) if isinstance(candidate.get("@graph"), list) else []:
                    if isinstance(item, dict) and item.get("@type") == "JobPosting":
                        posting = item
                        break
                if posting:
                    break
            if posting:
                break

        def qa_text(*selectors: str) -> str:
            for selector in selectors:
                node = soup.select_one(selector)
                if node:
                    value = node.get_text(" ", strip=True)
                    if value:
                        return value
            return ""

        description_html = str(posting.get("description") or "")
        if not description_html:
            node = soup.select_one('[data-qa="vacancy-description"]')
            if node:
                description_html = node.decode_contents()
        description = clean_html_text(description_html)

        organization = posting.get("hiringOrganization") or {}
        if not isinstance(organization, dict):
            organization = {}
        job_location = posting.get("jobLocation") or {}
        if not isinstance(job_location, dict):
            job_location = {}
        address = job_location.get("address") or {}
        if not isinstance(address, dict):
            address = {}
        applicant_location = posting.get("applicantLocationRequirements") or {}
        if isinstance(applicant_location, list):
            applicant_location_name = ", ".join(
                str(item.get("name") or "") for item in applicant_location if isinstance(item, dict) and item.get("name")
            )
        elif isinstance(applicant_location, dict):
            applicant_location_name = str(applicant_location.get("name") or "")
        else:
            applicant_location_name = ""

        salary_text = qa_text('[data-qa="vacancy-salary"]')
        salary_from, salary_to, salary_currency = cls._salary(salary_text)

        # HH exposes a schema.org JobPosting. Prefer structured baseSalary when
        # present: the rendered salary node can sometimes show only one bound
        # even though JSON-LD contains the full range.
        base_salary = posting.get("baseSalary") or {}
        if isinstance(base_salary, dict):
            structured_currency = str(base_salary.get("currency") or "") or None
            structured_value = base_salary.get("value")
            structured_from = structured_to = None
            if isinstance(structured_value, dict):
                structured_from = structured_value.get("minValue")
                structured_to = structured_value.get("maxValue")
                if structured_from is None and structured_to is None:
                    exact = structured_value.get("value")
                    structured_from = exact
            elif structured_value is not None:
                structured_from = structured_value

            def as_int(value):
                try:
                    return int(float(value)) if value is not None else None
                except (TypeError, ValueError):
                    return None

            structured_from = as_int(structured_from)
            structured_to = as_int(structured_to)
            if structured_from or structured_to:
                salary_from = structured_from
                salary_to = structured_to
                salary_currency = structured_currency or salary_currency

        experience = qa_text('[data-qa="vacancy-experience"]', '[data-qa="work-experience-text"]')
        work_mode = qa_text('[data-qa="work-formats-text"]', '[data-qa="work-schedule-by-days-text"]')

        return {
            "title": str(posting.get("title") or qa_text('[data-qa="vacancy-title"]')),
            "company": str(organization.get("name") or qa_text('[data-qa="vacancy-company-name"]')),
            "description": description,
            "experience": experience,
            "salary_text": salary_text,
            "salary_from": salary_from,
            "salary_to": salary_to,
            "salary_currency": salary_currency,
            "city": str(address.get("addressLocality") or qa_text('[data-qa="vacancy-view-raw-address"]')),
            "work_mode": work_mode,
            "published_at": str(posting.get("datePosted") or ""),
            "applicant_location": applicant_location_name,
        }

    def _from_api(self, payload: dict, *, is_ru: bool) -> list[NormalizedJob]:
        out: list[NormalizedJob] = []
        for row in payload.get("items", []):
            job_id = str(row.get("id", ""))
            if not job_id:
                continue
            area = row.get("area") or {}
            address = row.get("address") or {}
            salary = row.get("salary") or {}
            snippet = row.get("snippet") or {}
            work_format = row.get("work_format") or []
            work_mode = ", ".join(x.get("name", "") for x in work_format if isinstance(x, dict) and x.get("name")) or None
            description = " ".join(
                x for x in [
                    self._clean(snippet.get("requirement", "")),
                    self._clean(snippet.get("responsibility", "")),
                ] if x
            )
            row = dict(row)
            row["transport"] = "api"
            out.append(NormalizedJob(
                source=self.source_id,
                source_job_id=job_id,
                title=row.get("name", ""),
                company=(row.get("employer") or {}).get("name", ""),
                description=description,
                url=row.get("alternate_url", ""),
                country="RU" if is_ru else None,
                city=address.get("city") or area.get("name"),
                work_mode=work_mode,
                salary_from=salary.get("from"),
                salary_to=salary.get("to"),
                salary_currency=salary.get("currency"),
                published_at=row.get("published_at"),
                raw=row,
            ))
        return out

    async def discover(self, context: SourceContext) -> list[NormalizedJob]:
        query = self._combined_query(list(context.queries or []))
        if not query:
            return []
        is_ru = (context.current_country or "").upper() == "RU"
        area = "113" if is_ru else None

        try:
            payload = await self.client.search(
                query,
                per_page=max(1, min(100, settings.hh_public_per_page)),
                area=area,
            )
            return self._from_api(payload, is_ru=is_ru)
        except HHAPIForbidden:
            if not settings.hh_web_fallback_enabled:
                raise
            log.warning("HH API returned 403; using ordinary public HH web search fallback")

        out: list[NormalizedJob] = []
        seen: set[str] = set()
        pages = max(1, min(3, settings.hh_web_max_pages))
        for page in range(pages):
            html = await self.client.search_web(query, page=page, area=area)
            jobs = self.parse_web_html(html, is_ru=is_ru)
            if not jobs:
                break
            for job in jobs:
                if job.source_job_id in seen:
                    continue
                seen.add(job.source_job_id)
                out.append(job)
        return out
