from __future__ import annotations

import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from app.config import settings
from app.domain.jobs import NormalizedJob, SourceCapabilities
from app.providers.hh import HHAPIForbidden, HHCaptchaRequired, HHClient
from app.sources.base import JobSource, SourceContext


log = logging.getLogger(__name__)


class HHSource(JobSource):
    source_id = "hh"
    name = "HeadHunter"
    capabilities = SourceCapabilities(discovery=True, details=False, apply=False, messages=False)

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
        if not text:
            return None, None, None
        compact = text.replace("\u202f", " ").replace("\xa0", " ")
        nums = [int(x.replace(" ", "")) for x in re.findall(r"\d[\d ]{2,}", compact)]
        currency = None
        if "₽" in compact or "руб" in compact.casefold():
            currency = "RUR"
        elif "$" in compact or "USD" in compact.upper():
            currency = "USD"
        elif "€" in compact or "EUR" in compact.upper():
            currency = "EUR"
        elif "₾" in compact or "GEL" in compact.upper():
            currency = "GEL"
        if not nums:
            return None, None, currency
        folded = compact.casefold().strip()
        if len(nums) >= 2:
            return nums[0], nums[1], currency
        if folded.startswith("до "):
            return None, nums[0], currency
        return nums[0], None, currency

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
            description = " ".join(description_parts) or card_text[:2500]
            salary_text = salary_node.get_text(" ", strip=True) if salary_node else ""
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
                raw={"transport": "web", "salary_text": salary_text},
            ))
        return out

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
