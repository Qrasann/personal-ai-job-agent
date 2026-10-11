from __future__ import annotations

import asyncio
import re

import httpx
from bs4 import BeautifulSoup

from app.domain.jobs import NormalizedJob, SourceCapabilities
from app.sources.base import JobSource, SourceContext


_REQUEST_LOCK = asyncio.Lock()


class JobBankSource(JobSource):
    """Bounded public international TFW discovery; LMIA is not visa approval."""

    source_id = "jobbank"
    name = "Job Bank Canada"
    capabilities = SourceCapabilities(True, True, False, False)
    origin = "https://www.jobbank.gc.ca"
    max_details = 12
    request_delay = 5  # Public robots.txt Crawl-delay.

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
        async with httpx.AsyncClient(timeout=30, follow_redirects=True,
                                     headers={"User-Agent": "JobAgentV3/0.1 (public job discovery)"}) as client:
            async def fetch(url, **kwargs):
                # Scheduled/manual scans share one crawl budget in this process.
                async with _REQUEST_LOCK:
                    await asyncio.sleep(self.request_delay)
                    response = await client.get(url, **kwargs)
                    response.raise_for_status()
                    return response.text

            for query in (context.queries or [])[:6]:
                page = await fetch(f"{self.origin}/jobsearch/jobsearch",
                                   params={"fsrc": "32", "fglo": "1", "searchstring": query, "sort": "M"})
                for job in self.parse_search(page):
                    jobs.setdefault(job.source_job_id, job)
                if len(jobs) >= self.max_details:
                    break
            result = []
            for job in list(jobs.values())[:self.max_details]:
                job = self.enrich(job, await fetch(job.url))
                if job.raw["international_candidates"] is not False:
                    result.append(job)
            return result
