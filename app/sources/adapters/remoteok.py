from __future__ import annotations

import asyncio
import logging
import math

import httpx

from app.domain.jobs import NormalizedJob, SourceCapabilities
from app.domain.remote_evidence import remote_location_restriction
from app.domain.role_text import role_tokens
from app.domain.vacancy_availability import source_datetime
from app.sources.base import JobSource, SourceContext
from app.sources.diagnostics import SourceInvalidResponse


log = logging.getLogger(__name__)

_ROLE_QUERY_ALIASES = {
    frozenset({"site", "reliability", "engineer"}): frozenset({"sre"}),
}


class RemoteOKSource(JobSource):
    source_id = "remoteok"
    name = "Remote OK"
    capabilities = SourceCapabilities(discovery=True, details=True, apply=False, messages=False)
    endpoint = "https://remoteok.com/api"
    request_retries = 1

    @staticmethod
    def _amount(value: object) -> int | None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        if isinstance(value, float) and not math.isfinite(value):
            return None
        if not 0 < value <= 2**31 - 1:
            return None
        amount = int(value)
        return amount if amount == value else None

    @staticmethod
    def _tags(value: object) -> list[str]:
        if not isinstance(value, list):
            return []
        return [item.strip() for item in value if isinstance(item, str) and item.strip()]

    async def discover(self, context: SourceContext) -> list[NormalizedJob]:
        self.retry_count = 0
        headers = {"User-Agent": "JobAgentV3/0.1 (job discovery client)"}
        async with httpx.AsyncClient(timeout=httpx.Timeout(connect=30, read=30, write=30, pool=30)) as client:
            for attempt in range(self.request_retries + 1):
                try:
                    response = await client.get(self.endpoint, headers=headers)
                    response.raise_for_status()
                    payload = response.json()
                    break
                except httpx.TransportError as exc:
                    if attempt >= self.request_retries:
                        raise
                    self.retry_count += 1
                    log.warning(
                        "RemoteOK transport failure (%s); retry %s/%s",
                        type(exc).__name__, attempt + 1, self.request_retries,
                    )
                    await asyncio.sleep(0.5 * (2 ** attempt))

        if not isinstance(payload, list):
            raise SourceInvalidResponse("RemoteOK expected a list")

        queries = [q.casefold() for q in (context.queries or [])]
        generic_role_tokens = {
            "engineer", "administrator", "admin", "specialist", "developer",
            "инженер", "администратор", "специалист", "разработчик",
        }
        meaningful_queries: list[set[str]] = []
        for query in queries:
            tokens = role_tokens(query)
            meaningful = tokens - generic_role_tokens
            required = meaningful or tokens
            meaningful_queries.append(required)
            alias = _ROLE_QUERY_ALIASES.get(frozenset(tokens))
            if alias:
                meaningful_queries.append(set(alias))
        out: list[NormalizedJob] = []
        for row in payload:
            if not isinstance(row, dict) or not row.get("id"):
                continue
            title = str(row.get("position") or "")
            tags = self._tags(row.get("tags"))
            published = source_datetime(row.get("date"))
            # Discovery should match the role, not a generic word such as
            # "engineer" buried somewhere in a long description. This avoids
            # unrelated RemoteOK rows such as housekeeping/data/software roles
            # entering the DevOps feed.
            title_tokens = role_tokens(" ".join([title, *tags]))
            if meaningful_queries and not any(
                tokens and tokens <= title_tokens
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
                    # RemoteOK's location is free-form and may be an office,
                    # region or "Worldwide" label. Preserve it as source text,
                    # not as a normalized work-country claim.
                    country=None,
                    work_mode="remote",
                    # Retain an explicit limit; bare office/global labels do
                    # not establish which countries the employer can hire from.
                    remote_scope=remote_location_restriction(row.get("location")) or "unspecified",
                    salary_from=self._amount(row.get("salary_min")),
                    salary_to=self._amount(row.get("salary_max")),
                    salary_currency="USD" if self._amount(row.get("salary_min")) or self._amount(row.get("salary_max")) else None,
                    skills=tags,
                    published_at=published.isoformat() if published else None,
                    raw={**row, "source_location": row.get("location")},
                )
            )
        return out
