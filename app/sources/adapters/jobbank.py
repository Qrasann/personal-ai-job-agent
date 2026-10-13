from __future__ import annotations

import asyncio
import logging
import re
import time

import httpx
from bs4 import BeautifulSoup

from app.domain.jobs import NormalizedJob, SourceCapabilities
from app.sources.base import JobSource, SourceContext


_REQUEST_LOCK = asyncio.Lock()
_LAST_REQUEST_STARTED: float | None = None
_DETAIL_CACHE: dict[str, tuple[float, str]] = {}
logger = logging.getLogger(__name__)


def _monotonic() -> float:
    return time.monotonic()


async def _wait_for_request_slot(delay: float) -> None:
    """Enforce a minimum interval between serialized request starts."""
    global _LAST_REQUEST_STARTED
    if _LAST_REQUEST_STARTED is not None:
        remaining = delay - (_monotonic() - _LAST_REQUEST_STARTED)
        if remaining > 0:
            await asyncio.sleep(remaining)
    _LAST_REQUEST_STARTED = _monotonic()


class JobBankSource(JobSource):
    """Bounded public international TFW discovery; LMIA is not visa approval."""

    source_id = "jobbank"
    name = "Job Bank Canada"
    capabilities = SourceCapabilities(True, True, False, False)
    origin = "https://www.jobbank.gc.ca"
    max_details = 12
    request_delay = 5  # Public robots.txt Crawl-delay.
    detail_cache_ttl = 60 * 60
    max_cached_details = 256

    async def _fetch(self, client: httpx.AsyncClient, url: str, **kwargs) -> str:
        """Fetch one page, retrying a single transport failure within the crawl lock."""
        async with _REQUEST_LOCK:
            for attempt in range(2):
                # Keep starts at least five seconds apart across retries and
                # scan profiles. A slow response already consumes the interval.
                await _wait_for_request_slot(self.request_delay)
                try:
                    response = await client.get(url, **kwargs)
                    response.raise_for_status()
                    return response.text
                except httpx.TransportError as exc:
                    if attempt == 1:
                        raise
                    logger.warning(
                        "Job Bank transport failure (%s); retry 1/1",
                        type(exc).__name__,
                    )
        raise RuntimeError("Job Bank request exhausted without a response")

    @classmethod
    def parse_search(cls, html: str) -> list[NormalizedJob]:
        soup = BeautifulSoup(html, "html.parser")
        if soup.select_one("#results-list-content") is None:
            raise ValueError("Job Bank search contract unavailable")
        jobs = []
        for card in soup.select("a.resultJobItem"):
            match = re.match(r"/jobsearch/jobposting(?:tfw)?/(\d+)", str(card.get("href", "")))
            title = card.select_one(".noctitle")
            if not match or not title:
                continue
            def value(selector):
                node = card.select_one(selector)
                return node.get_text(" ", strip=True) if node else ""
            jobs.append(NormalizedJob(
                source=cls.source_id, source_job_id=match[1],
                title=title.get_text(" ", strip=True), company=value(".business"),
                country="CA", city=value(".location").removeprefix("Location ") or None,
                url=f"{cls.origin}/jobsearch/jobpostingtfw/{match[1]}",
                published_at=value(".date") or None,
                # Preserve decimal CAD/hour rates without feeding the legacy
                # integer/USD salary fallback or inventing monthly amounts.
                raw={"lmia_status": value(".jobLMIAflag"), "source_salary_text": value(".salary")},
            ))
        return jobs

    @staticmethod
    def enrich(job: NormalizedJob, html: str) -> NormalizedJob:
        soup = BeautifulSoup(html, "html.parser")
        body = soup.select_one(".job-posting-details-body")
        if body is None:
            raise ValueError("Job Bank detail contract unavailable")
        # Avoid navigation/footer text and source-wide immigration guidance.
        job.description = body.get_text(" ", strip=True)
        eligibility = body.select_one(".job-posting-detail-apply")
        eligibility_text = eligibility.get_text(" ", strip=True) if eligibility else ""
        restricted = "do not apply if you are not authorized to work in canada" in eligibility_text.casefold()
        job.raw["international_candidates"] = False if restricted else (
            True if "with or without a valid canadian work permit" in eligibility_text.casefold() else None
        )
        job.raw["eligibility_evidence"] = eligibility_text
        job.raw["evidence_url"] = job.url
        # Only explicit employer offers count; LMIA and eligibility stay separate.
        signals = {}
        evidence = {}
        refusals = {}
        for key, pattern in {
            "visa_sponsorship": r"\b(?:we (?:offer|provide)|employer (?:offers|provides)) visa sponsorship(?=[.!;,]|$| (?:for|to|and)\b)",
            "relocation": r"\b(?:we (?:offer|provide)|employer (?:offers|provides)) relocation (?:assistance|support|package)(?=[.!;,]|$| (?:for|to|and)\b)",
        }.items():
            found = re.search(pattern, job.description, re.I)
            negative = {
                "visa_sponsorship": r"no visa sponsorship|visa sponsorship (?:is )?not (?:available|provided|offered)",
                "relocation": r"no relocation|relocation (?:assistance|support|package) (?:is )?not (?:available|provided|offered)",
            }[key]
            refusal = re.search(negative, job.description, re.I)
            refusals[key] = bool(refusal)
            signals[key] = bool(found) and not restricted and not refusal
            if signals[key]:
                evidence[key] = found[0]
        signals["relocation_package"] = signals["relocation"]
        signals["immigration_support"] = signals["visa_sponsorship"]
        job.visa_sponsorship = True if signals["visa_sponsorship"] else (False if restricted or refusals["visa_sponsorship"] else None)
        job.relocation = True if signals["relocation"] else (False if refusals["relocation"] else None)
        job.raw["support_signals"] = signals
        job.raw["support_evidence"] = evidence
        return job

    async def discover(self, context: SourceContext) -> list[NormalizedJob]:
        jobs = {}
        search_transport_errors: list[httpx.TransportError] = []
        successful_searches = 0
        async with httpx.AsyncClient(timeout=30, follow_redirects=True,
                                     headers={"User-Agent": "JobAgentV3/0.1 (public job discovery)"}) as client:
            for query in (context.queries or [])[:6]:
                try:
                    page = await self._fetch(
                        client,
                        f"{self.origin}/jobsearch/jobsearch",
                        params={"fsrc": "32", "fglo": "1", "searchstring": query, "sort": "M"},
                    )
                except httpx.TransportError as exc:
                    search_transport_errors.append(exc)
                    logger.warning(
                        "Job Bank search failed after retries (%s); continuing",
                        type(exc).__name__,
                    )
                    continue
                successful_searches += 1
                for job in self.parse_search(page):
                    jobs.setdefault(job.source_job_id, job)
                if len(jobs) >= self.max_details:
                    break
            if not jobs:
                if search_transport_errors and successful_searches == 0:
                    raise search_transport_errors[-1]
                return []

            result = []
            detail_transport_errors: list[httpx.TransportError] = []
            successful_details = 0
            for job in list(jobs.values())[:self.max_details]:
                cached = _DETAIL_CACHE.get(job.url)
                use_cache = (not context.force_refresh and cached is not None
                             and time.monotonic() - cached[0] < self.detail_cache_ttl)
                if use_cache:
                    detail = cached[1]
                else:
                    try:
                        detail = await self._fetch(client, job.url)
                    except httpx.TransportError as exc:
                        detail_transport_errors.append(exc)
                        logger.warning(
                            "Job Bank detail request failed after retries (%s); skipping vacancy",
                            type(exc).__name__,
                        )
                        continue
                successful_details += 1
                job = self.enrich(job, detail)
                if not use_cache:
                    _DETAIL_CACHE.pop(job.url, None)
                    _DETAIL_CACHE[job.url] = (time.monotonic(), detail)
                    while len(_DETAIL_CACHE) > self.max_cached_details:
                        _DETAIL_CACHE.pop(next(iter(_DETAIL_CACHE)))
                if job.raw["international_candidates"] is not False:
                    result.append(job)
            if successful_details == 0 and detail_transport_errors:
                raise detail_transport_errors[-1]
            return result
