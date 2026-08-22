from __future__ import annotations

import re
from dataclasses import dataclass

from app.agents.job_signals import analyze_job_signals
from app.database.models import CandidateFact, Job, ResumeProfile, SearchProfile


@dataclass(slots=True)
class MatchResult:
    technical_score: int
    geography_score: int
    salary_score: int
    relocation_score: int
    total_score: int
    reason: str
    resume_id: int | None = None
    track: str = "unknown"


def _terms(settings: dict, key: str) -> list[str]:
    return [str(x).casefold() for x in (settings.get(key) or [])]


def choose_resume(job: Job, resumes: list[ResumeProfile]) -> int | None:
    if not resumes:
        return None
    hay = f"{job.title} {job.description}".casefold()
    ranked: list[tuple[int, int]] = []
    for resume in resumes:
        score = 0
        for token in re.findall(r"[a-zа-я0-9+#.-]+", resume.role.casefold()):
            if len(token) >= 3 and token in hay:
                score += 5
        if (job.country or "").upper() not in {"", "RU"} and resume.language == "en":
            score += 5
        if (job.country or "").upper() == "RU" and resume.language == "ru":
            score += 3
        ranked.append((score, resume.id))
    ranked.sort(reverse=True)
    return ranked[0][1]


def _enabled_tracks(settings: dict) -> set[str]:
    modes = settings.get("modes") or {}
    enabled = set()
    if modes.get("local_ru", True):
        enabled.add("local_ru")
    if modes.get("remote_international", True):
        enabled.add("remote_international")
    if modes.get("relocation", True):
        enabled.add("relocation")
    return enabled


def score_job(job: Job, search: SearchProfile, facts: list[CandidateFact], resumes: list[ResumeProfile]) -> MatchResult:
    settings = search.settings or {}
    hay = " ".join([job.title, job.company, job.description]).casefold()
    chosen_resume = choose_resume(job, resumes)

    exclude = _terms(settings, "exclude_terms")
    hit_exclude = [x for x in exclude if x and x in hay]
    if hit_exclude:
        return MatchResult(0, 0, 0, 0, 0, "Исключено по фильтру: " + ", ".join(hit_exclude), chosen_resume, "excluded")

    signals = analyze_job_signals(job)
    enabled = _enabled_tracks(settings)
    viable = signals.tracks & enabled
    if signals.tracks and not viable:
        return MatchResult(0, 0, 0, 0, 0, "Режим этой вакансии выключен", chosen_resume, "disabled")

    preferred = _terms(settings, "preferred_terms")
    strong = _terms(settings, "strong_terms")
    fact_text = " ".join(x.value for x in facts if x.active is not False).casefold()
    preferred_hits = [x for x in preferred if x in hay and x in fact_text]
    strong_hits = [x for x in strong if x in hay and x in fact_text]

    title_hay = job.title.casefold()
    query_hits: list[str] = []
    for query in _terms(settings, "queries"):
        tokens = [x for x in re.findall(r"[a-zа-я0-9+#.-]+", query) if len(x) >= 3]
        matched = sum(token in title_hay for token in tokens)
        if tokens and matched >= max(1, len(tokens) - 1):
            query_hits.append(query)

    technical = min(100, 40 + min(25, len(query_hits) * 20) + len(preferred_hits) * 6 + len(strong_hits) * 7)
    if settings.get("queries") and not query_hits:
        technical = max(20, technical - 18)

    country = (job.country or "").upper()
    geography = 45
    track = "unknown"
    if "relocation" in viable:
        track = "relocation"
        geography = 85
    if "remote_international" in viable:
        track = "remote"
        geography = {"yes": 100, "uncertain": 68, "unknown": 60, "no": 10}.get(signals.remote_eligibility, 55)
    if "local_ru" in viable:
        track = "russia_remote" if "remote" in (job.work_mode or "").casefold() or "удален" in (job.work_mode or "").casefold() else "russia"
        geography = max(geography, 95)
    if country not in {"", "RU"} and not viable:
        geography = 25

    minimums = settings.get("minimum_salary") or {}
    minimum = minimums.get(job.salary_currency or "")
    if minimum is None:
        salary = 58 if not (job.salary_from or job.salary_to) else 72
    else:
        observed = job.salary_to or job.salary_from or 0
        salary = 100 if observed >= int(minimum) else max(0, int(observed / int(minimum) * 100)) if minimum else 60

    relocation_enabled = "relocation" in enabled
    if signals.relocation_blocked:
        relocation = 5
    elif job.visa_sponsorship is True:
        relocation = 100
    elif signals.relocation_positive:
        relocation = 92
    elif relocation_enabled and country not in {"", "RU"}:
        relocation = 42
    else:
        relocation = 50

    total = round(technical * 0.48 + geography * 0.27 + salary * 0.12 + relocation * 0.13)
    if signals.remote_eligibility == "no" and track == "remote":
        total = min(total, 45)
    if signals.relocation_blocked and country not in {"", "RU"} and track == "relocation":
        total = min(total, 40)

    bits = [f"режим {track}", f"техника {technical}", f"география {geography}", f"зарплата {salary}", f"релокация {relocation}"]
    if query_hits:
        bits.append("роль: " + ", ".join(query_hits[:3]))
    if preferred_hits:
        bits.append("совпадения: " + ", ".join(preferred_hits[:8]))
    if signals.remote_reason:
        bits.append(signals.remote_reason)
    if signals.relocation_reason:
        bits.append(signals.relocation_reason)
    return MatchResult(technical, geography, salary, relocation, max(0, min(100, total)), "; ".join(bits), chosen_resume, track)
