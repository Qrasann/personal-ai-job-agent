from __future__ import annotations

import httpx

from app.domain.jobs import NormalizedJob, SourceCapabilities
from app.sources.base import JobSource, SourceContext


class RemoteOKSource(JobSource):
    source_id = "remoteok"
    name = "Remote OK"
    capabilities = SourceCapabilities(discovery=True, details=True, apply=False, messages=False)
    endpoint = "https://remoteok.com/api"

    async def discover(self, context: SourceContext) -> list[NormalizedJob]:
        headers = {"User-Agent": "JobAgentV3/0.1 (job discovery client)"}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(self.endpoint, headers=headers)
            response.raise_for_status()
            payload = response.json()

        queries = [q.casefold() for q in (context.queries or [])]
        out: list[NormalizedJob] = []
        for row in payload:
            if not isinstance(row, dict) or not row.get("id"):
                continue
            title = str(row.get("position") or "")
            tags = [str(x) for x in (row.get("tags") or [])]
            hay = " ".join([title, " ".join(tags), str(row.get("description") or "")]).casefold()
            if queries and not any(q in hay or any(token in hay for token in q.split()) for q in queries):
                continue
            out.append(
                NormalizedJob(
                    source=self.source_id,
                    source_job_id=str(row["id"]),
                    title=title,
                    company=str(row.get("company") or ""),
                    description=str(row.get("description") or ""),
                    url=str(row.get("url") or row.get("apply_url") or ""),
                    country=str(row.get("location") or "") or None,
                    work_mode="remote",
                    remote_scope="worldwide/unspecified",
                    salary_from=row.get("salary_min"),
                    salary_to=row.get("salary_max"),
                    salary_currency="USD" if row.get("salary_min") or row.get("salary_max") else None,
                    skills=tags,
                    published_at=str(row.get("date") or "") or None,
                    raw=row,
                )
            )
        return out
