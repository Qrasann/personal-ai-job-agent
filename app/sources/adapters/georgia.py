from __future__ import annotations

import asyncio
import logging
import re
from urllib.parse import urljoin, urlsplit

import httpx
from bs4 import BeautifulSoup

from app.domain.jobs import NormalizedJob, SourceCapabilities
from app.sources.base import JobSource, SourceContext


log = logging.getLogger(__name__)
UA = "JobAgentV3/0.1 (low-rate public job discovery)"
MAX_DETAILS_PER_SOURCE = 6
REQUEST_INTERVAL_SECONDS = 2.0
REQUEST_TIMEOUT_SECONDS = 15.0
GENERIC_ROLE_TOKENS = {
    "admin",
    "administrator",
    "assistant",
    "администратор",
    "developer",
    "engineer",
    "инженер",
    "lead",
    "manager",
    "менеджер",
    "operator",
    "оператор",
    "senior",
    "specialist",
    "специалист",
    "staff",
    "worker",
    "рабочий",
}
CITY_NAMES = (
    "Tbilisi",
    "Batumi",
    "Kutaisi",
    "Rustavi",
    "Zugdidi",
    "Gori",
    "Poti",
    "Telavi",
    "Akhaltsikhe",
)


def _tokens(text: str) -> set[str]:
    # Unicode words admit owner-selected Georgian/Armenian role text while
    # preserving the original treatment of technical punctuation/underscores.
    return set(re.findall(r"(?:[^\W_]|[+#.-])+", text.casefold()))


def _matches(title: str, queries: list[str] | None) -> bool:
    if not queries:
        return True
    title_tokens = _tokens(title)
    for query in queries:
        query_tokens = _tokens(query)
        specific_tokens = query_tokens - GENERIC_ROLE_TOKENS
        match_tokens = specific_tokens or query_tokens
        if title_tokens & match_tokens:
            return True
    return False


def _source_detail_url(base: str, href: str) -> str | None:
    """Keep listing-provided detail requests on the source's HTTPS host."""
    url = urljoin(base, href)
    try:
        parsed = urlsplit(url)
        host = urlsplit(base).hostname
        if (parsed.scheme != "https" or parsed.hostname != host
                or parsed.port not in (None, 443)
                or parsed.username is not None or parsed.password is not None):
            return None
    except ValueError:
        return None
    return url


def _salary_from_text(
    text: str,
) -> tuple[int | None, int | None, str | None, str | None, str | None]:
    """Parse only a labeled salary range with explicit currency and period."""
    line = next(
        (line.strip() for line in text.splitlines() if re.search(r"\bSalary\s*:", line, re.I)),
        None,
    )
    if not line:
        return None, None, None, None, None

    range_match = re.search(r"([0-9][0-9 ,]*)\s*[-–—]\s*([0-9][0-9 ,]*)", line)
    currency_codes = {code.upper() for code in re.findall(r"\b(GEL|USD|EUR)\b", line, re.I)}
    currency_symbols = set(re.findall(r"[₾€]", line))
    currency_map = {"₾": "GEL", "€": "EUR"}
    normalized = currency_codes | {currency_map[symbol] for symbol in currency_symbols}
    # A bare dollar sign can represent several currencies; require the USD code.
    if "$" in line and "USD" not in normalized:
        normalized.add("AMBIGUOUS_DOLLAR")
    period_matches = {
        "month": r"\b(?:per\s+month|monthly|month)\b|/\s*month\b",
        "year": r"\b(?:per\s+year|per\s+annum|yearly|annual(?:ly)?|year)\b|/\s*(?:year|yr)\b",
        "week": r"\b(?:per\s+week|weekly|week)\b|/\s*week\b",
        "day": r"\b(?:per\s+day|daily|day)\b|/\s*day\b",
        "hour": r"\b(?:per\s+hour|hourly|hour)\b|/\s*(?:hour|hr)\b",
    }
    periods = {period for period, pattern in period_matches.items() if re.search(pattern, line, re.I)}
    if not range_match or len(normalized) != 1 or periods != {"month"}:
        return None, None, None, None, line

    def amount(value: str) -> int:
        return int(re.sub(r"[ ,]", "", value))

    try:
        return (
            amount(range_match.group(1)),
            amount(range_match.group(2)),
            normalized.pop(),
            periods.pop(),
            line,
        )
    except ValueError:
        return None, None, None, None, line


def _city_from_text(text: str) -> str | None:
    locations = re.findall(
        r"(?:^|\n)\s*(?:Work\s+)?(?:Location|City)\s*:\s*([^\n]+)",
        text,
        re.I,
    )
    for city in CITY_NAMES:
        if any(re.search(rf"(?<!\w){re.escape(city)}(?!\w)", location, re.I) for location in locations):
            return city
    return None


def _company_from_text(text: str) -> str:
    match = re.search(r"(?:Provided By|Company|Employer)\s*:\s*([^\n]+)", text, re.I)
    return match.group(1).strip() if match else ""


async def _fetch_details(
    client: httpx.AsyncClient,
    links: list[tuple[str, str]],
    source_name: str,
    build_job,
) -> list[NormalizedJob]:
    jobs: list[NormalizedJob] = []
    last_error: httpx.HTTPError | None = None
    for title, url in links[:MAX_DETAILS_PER_SOURCE]:
        await asyncio.sleep(REQUEST_INTERVAL_SECONDS)
        try:
            detail = await client.get(url)
            detail.raise_for_status()
        except httpx.HTTPError as exc:
            last_error = exc
            log.warning("%s detail request failed (%s); continuing", source_name, type(exc).__name__)
            continue
        detail_soup = BeautifulSoup(detail.text, "html.parser")
        text = detail_soup.get_text("\n", strip=True)
        jobs.append(build_job(title, url, text, detail_soup))
    if links and not jobs and last_error is not None:
        raise last_error
    return jobs


class JobsGESource(JobSource):
    source_id = "jobs_ge"
    name = "JOBS.GE"
    capabilities = SourceCapabilities(discovery=True, details=True)
    base = "https://jobs.ge/en/"

    async def discover(self, context: SourceContext) -> list[NormalizedJob]:
        timeout = httpx.Timeout(REQUEST_TIMEOUT_SECONDS, connect=5.0)
        async with httpx.AsyncClient(timeout=timeout, headers={"User-Agent": UA}) as client:
            page = await client.get(self.base)
            page.raise_for_status()
            soup = BeautifulSoup(page.text, "html.parser")
            links: list[tuple[str, str]] = []
            for a in soup.find_all("a", href=True):
                href = str(a.get("href") or "")
                title = a.get_text(" ", strip=True)
                if "view=jobs" not in href or "id=" not in href or not title or not _matches(title, context.queries):
                    continue
                url = _source_detail_url(self.base, href)
                if url is None:
                    continue
                if (title, url) not in links:
                    links.append((title, url))
                if len(links) >= MAX_DETAILS_PER_SOURCE:
                    break

            def build_job(title: str, url: str, text: str, _soup: BeautifulSoup) -> NormalizedJob:
                job_id = re.search(r"[?&]id=(\d+)", url)
                return NormalizedJob(
                    source=self.source_id,
                    source_job_id=job_id.group(1) if job_id else url,
                    title=title,
                    company=_company_from_text(text),
                    description=text[:50000],
                    url=url,
                    country="GE",
                    city=_city_from_text(text),
                    # Text mentions alone are not reliable evidence of remote work or relocation.
                    raw={"url": url},
                )

            return await _fetch_details(client, links, self.name, build_job)


class HRGESource(JobSource):
    source_id = "hr_ge"
    name = "HR.ge"
    capabilities = SourceCapabilities(discovery=True, details=True)
    base = "https://www.hr.ge/en/"

    async def discover(self, context: SourceContext) -> list[NormalizedJob]:
        timeout = httpx.Timeout(REQUEST_TIMEOUT_SECONDS, connect=5.0)
        async with httpx.AsyncClient(timeout=timeout, headers={"User-Agent": UA}) as client:
            page = await client.get(self.base)
            page.raise_for_status()
            soup = BeautifulSoup(page.text, "html.parser")
            links: list[tuple[str, str]] = []
            for a in soup.find_all("a", href=True):
                href = str(a.get("href") or "")
                title = a.get_text(" ", strip=True)
                if "/announcement/" not in href or not title or not _matches(title, context.queries):
                    continue
                url = _source_detail_url(self.base, href)
                if url is None:
                    continue
                if (title, url) not in links:
                    links.append((title, url))
                if len(links) >= MAX_DETAILS_PER_SOURCE:
                    break

            def build_job(title: str, url: str, text: str, _soup: BeautifulSoup) -> NormalizedJob:
                job_id_match = re.search(r"/announcement/(\d+)/", url)
                (
                    salary_from,
                    salary_to,
                    salary_currency,
                    salary_period,
                    source_salary_text,
                ) = _salary_from_text(text)
                raw = {"url": url}
                if source_salary_text:
                    raw["source_salary_text"] = source_salary_text
                return NormalizedJob(
                    source=self.source_id,
                    source_job_id=job_id_match.group(1) if job_id_match else url,
                    title=title,
                    company=_company_from_text(text),
                    description=text[:50000],
                    url=url,
                    country="GE",
                    city=_city_from_text(text),
                    salary_from=salary_from,
                    salary_to=salary_to,
                    salary_currency=salary_currency,
                    salary_period=salary_period,
                    # Do not map the site's work-location label to work mode.
                    raw=raw,
                )

            return await _fetch_details(client, links, self.name, build_job)
