from __future__ import annotations

import re
from hashlib import sha256

from app.domain.jobs import NormalizedJob
from app.domain.support_evidence import support_evidence


SALARY_RE = re.compile(
    r"(?<!\w)(?P<currency>USD|EUR|GBP|CAD|RUB|RUR|GEL|AMD|[$€£₽₾])\s*"
    r"(?P<low>\d+(?:[ \u00a0]\d{3})*(?:[.,]\d+)?)"
    r"(?:\s*[-–—]\s*(?P<high>\d+(?:[ \u00a0]\d{3})*(?:[.,]\d+)?))?", re.I,
)
_PERIOD = re.compile(r"^\s*(?P<period>per month|monthly|per year|annually|annual|yearly|per hour|hourly|/month|/year|/hour|в месяц|в год|в час)\b", re.I)
_PERIODS = {value: period for period, values in {
    "monthly": ("per month", "monthly", "/month", "в месяц"),
    "annual": ("per year", "annually", "annual", "yearly", "/year", "в год"),
    "hourly": ("per hour", "hourly", "/hour", "в час"),
}.items() for value in values}


def _number(value: str | None) -> int | None:
    # Decimal and comma-separated amounts remain display-only; stripping
    # punctuation would silently change the source value or its units.
    if not value or "." in value or "," in value:
        return None
    return int(value.replace(" ", "").replace("\u00a0", ""))


def _remote(text: str) -> bool:
    for clause in re.split(r"[\n.!?;]+", text.casefold()):
        if re.search(r"\b(?:no|not|without) (?:\w+ )?remote\b|remote (?:is )?not|не (?:удален|удалён)|удал[её]н\w* (?:не|нет)", clause):
            continue
        if re.search(r"^\s*(?:fully |globally |worldwide )?remote\b|\b(?:work remotely|remote[- ]first|fully remote)\b|\bудал[её]н(?:но|ная работа|ный формат)\b", clause):
            return True
    return False


def parse_telegram_job(text: str, *, source_ref: str, source_url: str = "") -> NormalizedJob:
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    title = lines[0][:240] if lines else "Telegram vacancy"
    salary = SALARY_RE.search(text)
    symbols = {"€": "EUR", "₽": "RUB", "₾": "GEL"}
    period_match = _PERIOD.match(text[salary.end():]) if salary else None
    period = _PERIODS[period_match.group("period").casefold()] if period_match else None
    currency = (symbols.get(salary.group("currency"), salary.group("currency").upper())
                if salary else None)
    low = _number(salary.group("low")) if salary else None
    high = _number(salary.group("high")) if salary else None
    structured = bool(salary and period and currency not in {"$", "£"}
                      and low and (not salary.group("high") or high))
    remote = _remote(text)
    support = support_evidence(text)
    raw = {"source_ref": source_ref, "text": text, "support_evidence": support}
    if salary:
        raw["source_salary_text"] = text[salary.start():salary.end() + (period_match.end() if period_match else 0)]
    source_job_id = sha256(f"{source_ref}|{text}".encode()).hexdigest()[:24]
    return NormalizedJob(
        source="telegram",
        source_job_id=source_job_id,
        title=title,
        description=text,
        url=source_url,
        work_mode="remote" if remote else None,
        remote_scope="unspecified" if remote else None,
        relocation=support["relocation"],
        visa_sponsorship=support["visa_sponsorship"],
        salary_from=low if structured else None,
        salary_to=high if structured else None,
        salary_currency=currency if structured else None,
        salary_period=period if structured else None,
        raw=raw,
    )
