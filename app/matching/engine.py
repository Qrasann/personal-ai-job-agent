from __future__ import annotations

import re
from dataclasses import dataclass

from app.agents.job_signals import analyze_job_signals
from app.database.models import CandidateFact, Job, ResumeProfile, SearchProfile
from app.matching.technical_score import score_technical_v2


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
    fit: str = "good"


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


def _seniority_flags(job: Job) -> tuple[str | None, str | None]:
    """Return (level, reason) for obvious seniority signals.

    This is intentionally conservative. Middle is allowed because the personal
    profile may reasonably stretch to lower-middle roles. Senior/lead+ is not
    auto-notified in fallback mode unless the user later changes the policy.
    """
    title = (job.title or "").casefold()
    text = f"{job.title} {job.description}".casefold()

    hard_patterns = (
        r"\bsenior\b",
        r"\blead\b",
        r"\bprincipal\b",
        r"\bstaff\b",
        r"\bhead\b",
        r"\barchitect\b",
        r"\bстарш(?:ий|ая|ее)\b",
        r"\bведущ(?:ий|ая|ее)\b",
        r"\bруководител[ья]\b",
    )
    if any(re.search(pattern, title) for pattern in hard_patterns):
        return "senior", "senior/lead уровень в названии"

    very_high_experience = (
        r"(?:опыт|стаж)[^0-9\n]{0,30}(?:от\s*)?(?:5|6|7|8|9|10)\+?\s*(?:лет|года)",
        r"(?:5|6|7|8|9|10)\+\s*years?",
        r"(?:more than|at least)\s+(?:5|6|7|8|9|10)\s+years?",
        r"более\s+(?:5|6)\s+лет",
    )
    if any(re.search(pattern, text) for pattern in very_high_experience):
        return "high_experience", "требование 5+ лет/высокого опыта"

    stretch_experience = (
        r"(?:опыт|стаж)[^0-9\n]{0,30}(?:от\s*)?(?:3|4)\+?\s*(?:лет|года)",
        r"(?:3|4)\+\s*years?",
        r"(?:at least)\s+(?:3|4)\s+years?",
        # HH commonly exposes the broad platform band "3–6 лет" on cards.
        # Treat it as a stretch, not as an explicit 5+ requirement.
        r"(?:опыт[^\n]{0,30})?3[–—-]6\s*лет",
        r"3[–—-]6\s*years?",
    )
    if any(re.search(pattern, text) for pattern in stretch_experience):
        return "stretch", "требуется около 3–4 лет опыта"

    return None, None


def _best_skill_experience(facts: list[CandidateFact], aliases: tuple[str, ...]) -> str:
    rank = {"missing": 0, "learning": 1, "unknown": 2, "lab": 3, "commercial": 4}
    best = "missing"
    for fact in facts:
        if fact.active is False or getattr(fact, "deleted_at", None) is not None:
            continue
        value = (fact.value or "").casefold()
        if not any(alias in value for alias in aliases):
            continue
        kind = (fact.experience_type or "unknown").casefold()
        if rank.get(kind, 0) > rank.get(best, 0):
            best = kind
    return best

def _normalize_city(value: str | None) -> str:
    text = (value or "").casefold().replace("ё", "е").strip()
    text = re.sub(r"^г\.?\s*", "", text)
    text = re.split(r"[,;/|]", text, maxsplit=1)[0]
    return re.sub(r"\s+", " ", text).strip()

def _is_remote_job(job: Job) -> bool:
    text = ((job.work_mode or "") + " " + (job.description or "")).casefold().replace("ё", "е")
    return "remote" in text or "удален" in text

def _local_ru_location(job: Job, settings: dict) -> tuple[int, str, str | None, bool]:
    if _is_remote_job(job):
        return 95, "russia_remote", None, False

    local_city = _normalize_city(settings.get("local_city"))
    if not local_city:
        return 95, "russia", None, False

    job_city = _normalize_city(job.city)
    if not job_city:
        return 75, "russia_unknown_city", "город вакансии не определён", False
    if job_city == local_city:
        return 95, "russia_local", None, False
    if settings.get("domestic_relocation", False):
        return 70, "russia_relocation", "другой город РФ; внутренняя релокация разрешена", False
    return 25, "russia_other_city", f"другой город РФ: {job.city}", True

def _management_requirement(job: Job, technical_text: str | None = None) -> str | None:
    text = (technical_text if technical_text is not None else (job.description or "")).casefold()
    preferred_markers = ("приветств", "желательно", "будет плюсом", "preferred", "nice to have")
    hard_markers = (
        "руководство командой",
        "управление командой",
        "управлять командой",
        "управления командой",
        "people management",
        "team management",
        "line management",
        "manage a team",
        "managing a team",
    )
    for chunk in re.split(r"[\n.;]+", text):
        if any(marker in chunk for marker in preferred_markers):
            continue
        if any(marker in chunk for marker in hard_markers):
            return "требуется управление командой"
    return None

def _production_role_experience_gap(job: Job, technical_text: str | None = None) -> str | None:
    text = (technical_text if technical_text is not None else (job.description or "")).casefold()
    production_markers = ("production", "продакш", "боев", "промышленн")
    preferred_markers = ("приветств", "желательно", "будет плюсом", "preferred", "nice to have")
    role_markers = ("devops", "sre", "site reliability", "platform engineer", "platform engineering")
    years_patterns = (
        r"(?:от\s*)?(?:3|4)\+?\s*(?:лет|года)",
        r"(?:3|4)\+\s*years?",
        r"(?:at least|minimum of)\s+(?:3|4)\s+years?",
    )
    for chunk in re.split(r"[\n.;]+", text):
        if any(marker in chunk for marker in preferred_markers):
            continue
        if not any(marker in chunk for marker in production_markers):
            continue
        if not any(marker in chunk for marker in role_markers):
            continue
        if any(re.search(pattern, chunk) for pattern in years_patterns):
            return "3+ года production DevOps/SRE опыта"
    return None

def _production_skill_gap(job: Job, facts: list[CandidateFact], technical_text: str | None = None) -> tuple[str, str] | None:
    text = (technical_text if technical_text is not None else (job.description or "")).casefold()
    skills = {
        "kubernetes": ("kubernetes", "k8s"),
        "terraform": ("terraform",),
        "ansible": ("ansible",),
    }
    production_markers = ("production", "продакш", "боев", "промышленн")
    requirement_markers = ("опыт", "experience", "required", "треб", "обязател")
    preferred_markers = ("приветств", "желательно", "будет плюсом", "preferred", "nice to have")
    for chunk in re.split(r"[\n.;]+", text):
        if any(marker in chunk for marker in preferred_markers):
            continue
        if not any(marker in chunk for marker in production_markers):
            continue
        if not any(marker in chunk for marker in requirement_markers):
            continue
        for skill, aliases in skills.items():
            if any(alias in chunk for alias in aliases):
                experience = _best_skill_experience(facts, aliases)
                if experience != "commercial":
                    return skill, experience
    return None

def _risk_penalty(job: Job, settings: dict) -> tuple[int, str | None]:
    """Soft penalty for domains the owner wants manually reviewed.

    Hard bans remain in exclude_terms. This only keeps questionable crypto/web3
    roles out of the automatic notification lane while still preserving them in
    the DB for manual inspection.
    """
    hay = f"{job.title} {job.company}".casefold()
    review_terms = _terms(settings, "review_terms") or ["blockchain", "crypto", "web3"]
    hits = [term for term in review_terms if term and term in hay]
    if not hits:
        return 0, None
    return 14, "нужна ручная проверка домена: " + ", ".join(sorted(set(hits))[:4])


def score_job(job: Job, search: SearchProfile, facts: list[CandidateFact], resumes: list[ResumeProfile], *, technical_text: str | None = None) -> MatchResult:
    settings = search.settings or {}
    hay = " ".join([job.title, job.company, job.description]).casefold()
    chosen_resume = choose_resume(job, resumes)

    exclude = _terms(settings, "exclude_terms")
    hit_exclude = [x for x in exclude if x and x in hay]
    if hit_exclude:
        return MatchResult(0, 0, 0, 0, 0, "Исключено по фильтру: " + ", ".join(hit_exclude), chosen_resume, "excluded", "skip")

    signals = analyze_job_signals(job)
    enabled = _enabled_tracks(settings)
    viable = signals.tracks & enabled
    if signals.tracks and not viable:
        return MatchResult(0, 0, 0, 0, 0, "Режим этой вакансии выключен", chosen_resume, "disabled", "skip")

    preferred = _terms(settings, "preferred_terms")
    strong = _terms(settings, "strong_terms")
    fact_text = " ".join(x.value for x in facts if x.active is not False).casefold()
    preferred_hits = [x for x in preferred if x in hay and x in fact_text]
    strong_hits = [x for x in strong if x in hay and x in fact_text]

    title_hay = job.title.casefold()
    query_hits: list[str] = []
    generic_role_tokens = {
        "engineer", "administrator", "admin", "specialist", "developer",
        "инженер", "администратор", "специалист", "разработчик",
    }
    for query in _terms(settings, "queries"):
        all_tokens = [x for x in re.findall(r"[a-zа-я0-9+#.-]+", query) if len(x) >= 3]
        meaningful = [x for x in all_tokens if x not in generic_role_tokens]
        tokens = meaningful or all_tokens
        if tokens and all(token in title_hay for token in tokens):
            query_hits.append(query)

    technical = min(100, 40 + min(25, len(query_hits) * 20) + len(preferred_hits) * 6 + len(strong_hits) * 7)
    if settings.get("queries") and not query_hits:
        technical = max(20, technical - 18)

    structured_technical = score_technical_v2(technical_text if technical_text is not None else (job.description or ""), facts)
    if structured_technical is not None:
        technical = structured_technical

    seniority, seniority_reason = _seniority_flags(job)
    fit = "good"
    if seniority == "stretch":
        fit = "stretch"
    elif seniority in {"senior", "high_experience"}:
        fit = "skip"
    management_gap = _management_requirement(job, technical_text)
    if management_gap:
        fit = "skip"
        technical = min(technical, 48)

    production_role_gap = _production_role_experience_gap(job, technical_text)
    if production_role_gap:
        fit = "skip"
        technical = min(technical, 52)

    production_gap = _production_skill_gap(job, facts, technical_text)
    if production_gap:
        gap_skill, gap_experience = production_gap
        fit = "skip"
        technical = min(technical, 52)

    if seniority == "senior":
        technical = min(technical, 48)
    elif seniority == "high_experience":
        technical = min(technical, 52)
    elif seniority == "stretch":
        # Stretch roles should still be visible to a strong Junior+/pre-Middle
        # candidate. A small penalty is enough; the previous -12 together with
        # a 64 cap made every 3–4 year role mathematically unable to cross the
        # default 65 notification threshold.
        technical = max(20, technical - 6)

    country = (job.country or "").upper()
    geography = 45
    track = "unknown"
    geography_reason = None
    if "relocation" in viable:
        track = "relocation"
        geography = 85
    if "remote_international" in viable:
        track = "remote"
        geography = {"yes": 100, "uncertain": 68, "unknown": 60, "no": 10}.get(signals.remote_eligibility, 55)
    if "local_ru" in viable:
        geography, track, geography_reason, domestic_city_blocked = _local_ru_location(job, settings)
        if domestic_city_blocked:
            fit = "skip"
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

    risk_penalty, risk_reason = _risk_penalty(job, settings)
    total -= risk_penalty

    if signals.remote_eligibility == "no" and track == "remote":
        total = min(total, 45)
    if signals.relocation_blocked and country not in {"", "RU"} and track == "relocation":
        total = min(total, 40)

    # In rule-only fallback mode, obvious senior roles must not slip above the
    # normal notification threshold merely because geography/salary look good.

    if seniority == "senior":
        total = min(total, int(settings.get("senior_score_cap", 54)))
    elif seniority == "high_experience":
        total = min(total, int(settings.get("high_experience_score_cap", 58)))
    elif seniority == "stretch":
        stretch_cap = int(settings.get("stretch_score_cap", 72))
        # v3.3.2 persisted 64 in existing profiles. Upgrade that legacy
        # default in-place logically so users do not need to reset their DB.
        if stretch_cap == 64:
            stretch_cap = 72
        total = min(total, stretch_cap)

    bits = [f"режим {track}", f"техника {technical}", f"география {geography}", f"зарплата {salary}", f"релокация {relocation}"]
    if query_hits:
        bits.append("роль: " + ", ".join(query_hits[:3]))
    if preferred_hits:
        bits.append("совпадения: " + ", ".join(preferred_hits[:8]))
    if seniority_reason:
        bits.append(seniority_reason)
    if management_gap:
        bits.append(management_gap)
    if production_role_gap:
        bits.append(production_role_gap)
    if production_gap:
        bits.append(f"production-требование {gap_skill} без commercial опыта ({gap_experience})")

    if geography_reason:
        bits.append(geography_reason)
    if risk_reason:
        bits.append(risk_reason)
    if signals.remote_reason:
        bits.append(signals.remote_reason)
    if signals.relocation_reason:
        bits.append(signals.relocation_reason)
    return MatchResult(technical, geography, salary, relocation, max(0, min(100, total)), "; ".join(bits), chosen_resume, track, fit)
