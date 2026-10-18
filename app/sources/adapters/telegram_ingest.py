from __future__ import annotations

import re
from hashlib import sha256

from app.domain.jobs import NormalizedJob
from app.domain.support_evidence import support_evidence
from app.sources.telegram_post import post_fields


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
    compact = value.replace(" ", "").replace("\u00a0", "")
    if len(compact) > 10:
        return None
    number = int(compact)
    return number if 0 < number <= 2**31 - 1 else None


def _remote(text: str) -> bool:
    for clause in re.split(r"[\n.!?;]+", text.casefold()):
        if re.search(r"\b(?:no|not|without) (?:\w+ )?remote\b|remote (?:is )?not|не (?:удален|удалён)|удал[её]н\w* (?:не|нет)", clause):
            continue
        if re.search(r"^\s*(?:fully |globally |worldwide )?remote\b|\b(?:work remotely|remote[- ]first|fully remote)\b|\bудал[её]н(?:но|ная работа|ный формат)\b", clause):
            return True
    return False


def parse_telegram_job(text: str, *, source_ref: str, source_url: str = "") -> NormalizedJob:
    fields = post_fields(text)
    title = fields["title"]
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
    mode = fields["work_mode"] or ("remote" if _remote(text) else None)
    support = support_evidence(text)
    raw = {"source_ref": source_ref, "text": text, "support_evidence": support,
           "source_location": fields.get("location")}
    if salary:
        raw["source_salary_text"] = text[salary.start():salary.end() + (period_match.end() if period_match else 0)]
    source_job_id = sha256(f"{source_ref}|{text}".encode()).hexdigest()[:24]
    return NormalizedJob(
        source="telegram",
        source_job_id=source_job_id,
        title=title,
        company=fields.get("company", ""),
        description=text,
        url=source_url,
        country=fields["country"],
        city=fields["city"],
        work_mode=mode,
        remote_scope=(fields.get("location") or "unspecified")[:128] if mode == "remote" else None,
        relocation=support["relocation"],
        visa_sponsorship=support["visa_sponsorship"],
        salary_from=low if structured else None,
        salary_to=high if structured else None,
        salary_currency=currency if structured else None,
        salary_period=period if structured else None,
        raw=raw,
    )


def parse_forwarded_job(text: str, *, chat_id: int, message_id: int, origin) -> NormalizedJob:
    source_ref = f"forward:{chat_id}:{message_id}"
    url = ""
    if getattr(origin, "type", None) == "channel":
        channel = origin.chat
        source_ref = f"channel:{channel.id}:{origin.message_id}"
        username = getattr(channel, "username", None)
        if isinstance(username, str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{4,31}", username):
            url = f"https://t.me/{username}/{origin.message_id}"
    return parse_telegram_job(text, source_ref=source_ref, source_url=url)
