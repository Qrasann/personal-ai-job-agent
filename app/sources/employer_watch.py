from __future__ import annotations

import asyncio
from dataclasses import dataclass

import httpx

from app.sources.employer_watchlist import WatchedEmployer


@dataclass(frozen=True)
class EmployerProbe:
    employer_id: str
    ats: str
    status: str
    advertised_count: int | None
    watched_openings: int
    current_openings: int
    missing_provider_ids: tuple[str, ...]
    error_code: str | None = None


def _provider_ids(employer: WatchedEmployer, payload: object) -> tuple[set[str], int]:
    if employer.ats == "greenhouse":
        rows = payload.get("jobs") if isinstance(payload, dict) else None
    elif employer.ats == "smartrecruiters":
        rows = payload.get("content") if isinstance(payload, dict) else None
    elif employer.ats == "lever":
        rows = payload
    else:
        raise ValueError("custom career pages do not have a JSON contract")
    if not isinstance(rows, list):
        raise ValueError("public ATS response contract changed")
    identifiers = {
        str(row["id"])
        for row in rows
        if isinstance(row, dict) and row.get("id") is not None
    }
    return identifiers, len(rows)


async def probe_employer(
    employer: WatchedEmployer,
    *,
    client: httpx.AsyncClient,
) -> EmployerProbe:
    expected = {opening.provider_id for opening in employer.openings}
    try:
        if employer.api_url:
            params = {"mode": "json", "limit": 100} if employer.ats == "lever" else {"limit": 100}
            response = await client.get(employer.api_url, params=params)
            response.raise_for_status()
            current, advertised_count = _provider_ids(employer, response.json())
        else:
            # Custom pages have no stable public JSON contract. Verify every
            # reviewed official opening URL without following cross-host redirects.
            results = await asyncio.gather(*(client.get(item.url) for item in employer.openings))
            current = {
                opening.provider_id
                for opening, response in zip(employer.openings, results, strict=True)
                if response.status_code == 200
            }
            advertised_count = None
        missing = tuple(sorted(expected - current))
        return EmployerProbe(
            employer_id=employer.id,
            ats=employer.ats,
            status="current" if not missing else "changed",
            advertised_count=advertised_count,
            watched_openings=len(expected),
            current_openings=len(expected - set(missing)),
            missing_provider_ids=missing,
        )
    except (httpx.HTTPError, ValueError) as exc:
        return EmployerProbe(
            employer_id=employer.id,
            ats=employer.ats,
            status="unavailable",
            advertised_count=None,
            watched_openings=len(expected),
            current_openings=0,
            missing_provider_ids=tuple(sorted(expected)),
            error_code=type(exc).__name__,
        )


async def probe_watchlist(employers: tuple[WatchedEmployer, ...]) -> tuple[EmployerProbe, ...]:
    timeout = httpx.Timeout(15.0, connect=10.0)
    headers = {"Accept": "application/json, text/html", "User-Agent": "PersonalAIJobAgent/3.5.7 (read-only employer watch)"}
    async with httpx.AsyncClient(timeout=timeout, headers=headers, follow_redirects=False) as client:
        results: list[EmployerProbe] = []
        # Sequential probing is deliberate: the curated pilot is small and
        # should not create a burst against unrelated employer systems.
        for employer in employers:
            try:
                async with asyncio.timeout(20.0):
                    result = await probe_employer(employer, client=client)
            except TimeoutError:
                result = EmployerProbe(
                    employer_id=employer.id,
                    ats=employer.ats,
                    status="unavailable",
                    advertised_count=None,
                    watched_openings=len(employer.openings),
                    current_openings=0,
                    missing_provider_ids=tuple(sorted(item.provider_id for item in employer.openings)),
                    error_code="PROBE_TIMEOUT",
                )
            results.append(result)
            await asyncio.sleep(0.2)
        return tuple(results)
