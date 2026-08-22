from __future__ import annotations

import re
from hashlib import sha256

from app.domain.jobs import NormalizedJob


SALARY_RE = re.compile(r"(?P<currency>[$€£])\s?(?P<low>\d[\d\s,.]*)(?:\s*[-–—]\s*(?P<high>\d[\d\s,.]*))?", re.I)


def _number(value: str | None) -> int | None:
    if not value:
        return None
    cleaned = re.sub(r"[^0-9]", "", value)
    return int(cleaned) if cleaned else None


def parse_telegram_job(text: str, *, source_ref: str, source_url: str = "") -> NormalizedJob:
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    title = lines[0][:240] if lines else "Telegram vacancy"
    lowered = text.casefold()
    salary = SALARY_RE.search(text)
    symbols = {"$": "USD", "€": "EUR", "£": "GBP"}
    remote = "remote" in lowered or "удален" in lowered or "удалён" in lowered
    relocation = any(x in lowered for x in ("relocation", "релокац", "visa sponsorship", "виза"))
    source_job_id = sha256(f"{source_ref}|{text}".encode()).hexdigest()[:24]
    return NormalizedJob(
        source="telegram",
        source_job_id=source_job_id,
        title=title,
        description=text,
        url=source_url,
        work_mode="remote" if remote else None,
        remote_scope="unspecified" if remote else None,
        relocation=relocation,
        visa_sponsorship=True if "visa sponsorship" in lowered else None,
        salary_from=_number(salary.group("low")) if salary else None,
        salary_to=_number(salary.group("high")) if salary else None,
        salary_currency=symbols.get(salary.group("currency")) if salary else None,
        raw={"source_ref": source_ref, "text": text},
    )
