from __future__ import annotations

from bs4 import BeautifulSoup

from app.config import settings
from app.domain.jobs import NormalizedJob, SourceCapabilities
from app.providers.hh import HHClient
from app.sources.base import JobSource, SourceContext


class HHSource(JobSource):
    source_id = "hh"
    name = "HeadHunter"
    # New personal builds treat HH as discovery-only. Applicant OAuth is not a
    # prerequisite and private actions are intentionally not exposed in the UI.
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
        # HH supports a search query language. Combining roles keeps anonymous
        # discovery to one request per scan instead of one request per role.
        return " OR ".join(f'"{q}"' for q in cleaned[:8])

    async def discover(self, context: SourceContext) -> list[NormalizedJob]:
        query = self._combined_query(list(context.queries or []))
        if not query:
            return []

        is_ru = (context.current_country or "").upper() == "RU"
        payload = await self.client.search(
            query,
            per_page=max(1, min(100, settings.hh_public_per_page)),
            area="113" if is_ru else None,
        )

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
            out.append(
                NormalizedJob(
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
                )
            )
        return out
