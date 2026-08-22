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
        generic_role_tokens = {
            "engineer", "administrator", "admin", "specialist", "developer",
            "инженер", "администратор", "специалист", "разработчик",
        }
        meaningful_queries: list[list[str]] = []
        for query in queries:
            tokens = [t for t in query.replace("/", " ").split() if len(t) >= 3]
            meaningful = [t for t in tokens if t not in generic_role_tokens]
            meaningful_queries.append(meaningful or tokens)
        out: list[NormalizedJob] = []
        for row in payload:
            if not isinstance(row, dict) or not row.get("id"):
                continue
            title = str(row.get("position") or "")
            tags = [str(x) for x in (row.get("tags") or [])]
            # Discovery should match the role, not a generic word such as
            # "engineer" buried somewhere in a long description. This avoids
            # unrelated RemoteOK rows such as housekeeping/data/software roles
            # entering the DevOps feed.
            role_hay = " ".join([title, " ".join(tags)]).casefold()
            if meaningful_queries and not any(
                tokens and all(token in role_hay for token in tokens)
                for tokens in meaningful_queries
            ):
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
