from __future__ import annotations

import re
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from app.domain.jobs import NormalizedJob, SourceCapabilities
from app.sources.base import JobSource, SourceContext


UA = "JobAgentV3/0.1 (low-rate public job discovery)"


def _matches(title: str, queries: list[str] | None) -> bool:
    if not queries:
        return True
    hay = title.casefold()
    for query in queries:
        tokens = [x for x in re.findall(r"[a-zа-я0-9+#.-]+", query.casefold()) if len(x) >= 3]
        if any(token in hay for token in tokens):
            return True
    return False


class JobsGESource(JobSource):
    source_id = "jobs_ge"
    name = "JOBS.GE"
    capabilities = SourceCapabilities(discovery=True, details=True)
    base = "https://jobs.ge/en/"

    async def discover(self, context: SourceContext) -> list[NormalizedJob]:
        async with httpx.AsyncClient(timeout=30, headers={"User-Agent": UA}) as client:
            page = await client.get(self.base)
            page.raise_for_status()
            soup = BeautifulSoup(page.text, "html.parser")
            links: list[tuple[str, str]] = []
            for a in soup.find_all("a", href=True):
                href = str(a.get("href") or "")
                title = a.get_text(" ", strip=True)
                if "view=jobs" not in href or "id=" not in href or not title or not _matches(title, context.queries):
                    continue
                url = urljoin(self.base, href)
                if (title, url) not in links:
                    links.append((title, url))
                if len(links) >= 20:
                    break

            jobs: list[NormalizedJob] = []
            for title, url in links:
                detail = await client.get(url)
                detail.raise_for_status()
                detail_soup = BeautifulSoup(detail.text, "html.parser")
                text = detail_soup.get_text("\n", strip=True)
                job_id = re.search(r"[?&]id=(\d+)", url)
                company_match = re.search(r"Provided By:\s*([^\n]+)", text, re.I)
                company = company_match.group(1).strip() if company_match else ""
                jobs.append(NormalizedJob(
                    source=self.source_id,
                    source_job_id=job_id.group(1) if job_id else url,
                    title=title,
                    company=company,
                    description=text[:50000],
                    url=url,
                    country="GE",
                    city="Tbilisi" if "Tbilisi" in text else None,
                    work_mode="remote" if "remote" in text.casefold() else None,
                    relocation=True if "relocation" in text.casefold() else None,
                    raw={"url": url},
                ))
            return jobs


class HRGESource(JobSource):
    source_id = "hr_ge"
    name = "HR.ge"
    capabilities = SourceCapabilities(discovery=True, details=True)
    base = "https://www.hr.ge/en/"

    async def discover(self, context: SourceContext) -> list[NormalizedJob]:
        async with httpx.AsyncClient(timeout=30, headers={"User-Agent": UA}) as client:
            page = await client.get(self.base)
            page.raise_for_status()
            soup = BeautifulSoup(page.text, "html.parser")
            links: list[tuple[str, str]] = []
            for a in soup.find_all("a", href=True):
                href = str(a.get("href") or "")
                title = a.get_text(" ", strip=True)
                if "/announcement/" not in href or not title or not _matches(title, context.queries):
                    continue
                url = urljoin(self.base, href)
                if (title, url) not in links:
                    links.append((title, url))
                if len(links) >= 20:
                    break

            jobs: list[NormalizedJob] = []
            for title, url in links:
                detail = await client.get(url)
                detail.raise_for_status()
                detail_soup = BeautifulSoup(detail.text, "html.parser")
                text = detail_soup.get_text("\n", strip=True)
                job_id_match = re.search(r"/announcement/(\d+)/", url)
                salary_match = re.search(r"Salary:\s*(?:Fixed\s*)?(\d+)\s*[-–]\s*(\d+)", text, re.I)
                work_match = re.search(r"Work Location:\s*([^\n]+)", text, re.I)
                company = ""
                # The first company-like anchor after the title is difficult to identify reliably;
                # keep it blank rather than hallucinating. Detail text stays available to the matcher.
                jobs.append(NormalizedJob(
                    source=self.source_id,
                    source_job_id=job_id_match.group(1) if job_id_match else url,
                    title=title,
                    company=company,
                    description=text[:50000],
                    url=url,
                    country="GE",
                    city="Tbilisi" if "Tbilisi" in text else None,
                    work_mode=(work_match.group(1).strip().casefold() if work_match else None),
                    salary_from=int(salary_match.group(1)) if salary_match else None,
                    salary_to=int(salary_match.group(2)) if salary_match else None,
                    salary_currency="GEL" if salary_match else None,
                    raw={"url": url},
                ))
            return jobs
