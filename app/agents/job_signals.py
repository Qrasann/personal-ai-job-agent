from __future__ import annotations

import re
from dataclasses import dataclass

from app.database.models import Job


@dataclass(slots=True)
class JobSignals:
    tracks: set[str]
    remote_eligibility: str = "unknown"
    remote_reason: str = ""
    relocation_positive: bool = False
    relocation_blocked: bool = False
    relocation_reason: str = ""


def analyze_job_signals(job: Job) -> JobSignals:
    text = " ".join([job.title or "", job.description or "", job.remote_scope or "", job.work_mode or ""]).casefold()
    country = (job.country or "").upper()
    tracks: set[str] = set()

    remote = "remote" in text or "удален" in text or "удалён" in text
    if country in {"RU", "RUSSIA", "РОССИЯ"}:
        tracks.add("local_ru")
    if remote and country not in {"RU", "RUSSIA", "РОССИЯ"}:
        tracks.add("remote_international")

    relocation_positive_terms = (
        "visa sponsorship", "visa sponsor", "sponsorship available", "relocation assistance",
        "relocation package", "relocation support", "work permit sponsorship",
        "релокац", "помощь с переезд", "визовая поддержка", "рабочую визу",
    )
    relocation_block_terms = (
        "no visa sponsorship", "without visa sponsorship", "sponsorship is not available",
        "must already have the right to work", "must have the right to work",
        "eu work permit required", "must be authorized to work", "no relocation",
        "без релокации", "визу не спонсируем",
    )
    relocation_positive = job.visa_sponsorship is True or job.relocation is True or any(x in text for x in relocation_positive_terms)
    relocation_blocked = any(x in text for x in relocation_block_terms)
    if relocation_positive:
        tracks.add("relocation")

    no_remote_patterns = (
        r"\bus[- ]only\b", r"united states only", r"must (?:live|reside|be based) in (?:the )?u\.?s\.?",
        r"authorized to work in (?:the )?u\.?s\.?", r"\beu[- ]only\b", r"european union only",
        r"must (?:live|reside|be based) in the eu", r"must already have (?:eu|european union) work authorization",
    )
    yes_remote_terms = ("remote worldwide", "worldwide remote", "work from anywhere", "anywhere in the world", "global remote")
    uncertain_remote_terms = ("emea", "europe remote", "remote europe", "european time zones")

    remote_eligibility = "unknown"
    remote_reason = ""
    if remote:
        if any(re.search(pattern, text) for pattern in no_remote_patterns):
            remote_eligibility = "no"
            remote_reason = "remote ограничен страной/правом на работу"
        elif any(x in text for x in yes_remote_terms):
            remote_eligibility = "yes"
            remote_reason = "remote worldwide"
        elif any(x in text for x in uncertain_remote_terms):
            remote_eligibility = "uncertain"
            remote_reason = "региональный remote — нужно проверить доступность из РФ"
        else:
            remote_eligibility = "uncertain"
            remote_reason = "remote указан, но допустимые страны неясны"

    relocation_reason = ""
    if relocation_blocked:
        relocation_reason = "есть ограничение sponsorship/work authorization"
    elif relocation_positive:
        relocation_reason = "есть признаки relocation/visa support"

    return JobSignals(
        tracks=tracks,
        remote_eligibility=remote_eligibility,
        remote_reason=remote_reason,
        relocation_positive=relocation_positive,
        relocation_blocked=relocation_blocked,
        relocation_reason=relocation_reason,
    )
