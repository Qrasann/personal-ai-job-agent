from __future__ import annotations

from bs4 import BeautifulSoup

from app.domain.jobs import NormalizedJob, SourceCapabilities
from app.providers.hh import HHClient
from app.sources.base import JobSource, SourceContext


class HHSource(JobSource):
    source_id = "hh"
    name = "HeadHunter"
    capabilities = SourceCapabilities(discovery=True, details=True, apply=True, messages=True)

    def __init__(self, client: HHClient | None = None) -> None:
        self.client = client or HHClient()

    @staticmethod
    def _clean(value: str) -> str:
        return BeautifulSoup(value or "", "html.parser").get_text(" ", strip=True)

    async def discover(self, context: SourceContext) -> list[NormalizedJob]:
        out: list[NormalizedJob] = []
        for query in context.queries or []:
            payload = await self.client.search(query, per_page=20, area="113" if (context.current_country or "").upper() == "RU" else None)
            for row in payload.get("items", []):
                job_id = str(row.get("id", ""))
                if not job_id:
                    continue
                full = await self.client.vacancy(job_id)
                area = full.get("area") or {}
                address = full.get("address") or {}
                salary = full.get("salary_range") or full.get("salary") or {}
                work_format = full.get("work_format") or []
                work_mode = ", ".join(x.get("name", "") for x in work_format if x.get("name")) or None
                out.append(
                    NormalizedJob(
                        source=self.source_id,
                        source_job_id=job_id,
                        title=full.get("name", ""),
                        company=(full.get("employer") or {}).get("name", ""),
                        description=self._clean(full.get("description", "")),
                        url=full.get("alternate_url", ""),
                        country="RU" if (context.current_country or "").upper() == "RU" else None,
                        city=address.get("city") or area.get("name"),
                        work_mode=work_mode,
                        salary_from=salary.get("from"),
                        salary_to=salary.get("to"),
                        salary_currency=salary.get("currency"),
                        published_at=full.get("published_at"),
                        raw=full,
                    )
                )
        return out
