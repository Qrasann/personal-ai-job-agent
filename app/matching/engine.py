from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.agents.job_signals import analyze_job_signals
from app.database.models import CandidateFact, Job, ResumeProfile, SearchProfile
from app.domain.employer_policy import LEGACY_INDUSTRY_EXCLUSIONS
from app.domain.employer_policy import decision as employer_decision
from app.domain.role_text import role_tokens
from app.geo.countries import normalize_country
from app.matching.recommendation import build_recommendation_breakdown
from app.matching.technical_score import score_technical_v2
from app.search.preferences import discovery_queries, search_strategy

# Bump whenever score, fit-lane, cap, or exclusion semantics change.
MATCH_ASSESSMENT_VERSION = 4


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
    recommendation_scores: dict = field(default_factory=dict)


def _terms(settings: dict, key: str) -> list[str]:
    return [str(x).casefold() for x in (settings.get(key) or [])]


_RESUME_GENERIC_TOKENS = {
    "engineer", "administrator", "specialist", "developer",
    "инженер", "администратор", "специалист", "разработчик",
    "experience", "work", "with", "from", "years",
    "опыт", "работа", "года", "лет",
}

# Other short fragments retain the previous minimum-length policy.
_SHORT_ROLE_TERMS = frozenset({"qa", "hr", "go", "c", "c#", "it", "ui", "ux"})


def _matching_role_tokens(text: str) -> set[str]:
    return {token for token in role_tokens(text) if len(token) >= 3 or token in _SHORT_ROLE_TERMS}


def _resume_content_overlap(job: Job, resume: ResumeProfile) -> int:
    job_tokens = _matching_role_tokens(f"{job.title} {job.description}") - _RESUME_GENERIC_TOKENS
    resume_tokens = _matching_role_tokens(str(resume.content or "")) - _RESUME_GENERIC_TOKENS
    return len(job_tokens & resume_tokens)

def choose_resume(job: Job, resumes: list[ResumeProfile]) -> int | None:
    available = [
        resume
        for resume in resumes
        if resume.active is not False and getattr(resume, "deleted_at", None) is None
    ]
    if not available:
        return None

    job_tokens = _matching_role_tokens(f"{job.title} {job.description}")
    ranked: list[tuple[int, int]] = []
    for resume in available:
        score = 0
        for token in _matching_role_tokens(resume.role) - _RESUME_GENERIC_TOKENS:
            if token in job_tokens:
                score += 5

        score += min(10, _resume_content_overlap(job, resume))

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


def _relocation_country_match(job: Job, settings: dict) -> bool:
    """Treat a configured destination as a relocation lane, not as support proof.

    Relocation-first searches must still score ordinary destination-country
    postings when the employer says nothing about visa or moving assistance.
    The evidence remains unknown and keeps its existing conservative score; this
    helper only prevents those postings from falling into the unscoped lane.
    """
    if search_strategy(settings) != "relocation_first":
        return False
    country = normalize_country(str(job.country or ""))
    if not country:
        return False
    configured = {
        normalized
        for value in (settings.get("target_countries") or [])
        if (normalized := normalize_country(str(value)))
    }
    return country in configured


_YEAR_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


def _candidate_commercial_years(facts: list[CandidateFact]) -> int | None:
    best = None
    word_pattern = "|".join(_YEAR_WORDS)
    for fact in facts:
        if fact.active is False or getattr(fact, "deleted_at", None) is not None:
            continue
        if (fact.experience_type or "unknown").casefold() != "commercial":
            continue
        text = (fact.value or "").casefold()
        values = [
            int(value)
            for value in re.findall(r"\b(\d{1,2})\+?\s*(?:years?|yrs?|лет|года|год)\b", text)
        ]
        for word in re.findall(rf"\b(?:more than|over|at least)\s+({word_pattern})\s+years?\b", text):
            values.append(_YEAR_WORDS[word])
        if values:
            current = max(values)
            best = current if best is None else max(best, current)
    return best

def _required_experience_years(job: Job) -> int | None:
    text = f"{job.title} {job.description}".casefold()
    patterns = (
        r"(?:опыт|стаж)[^0-9\n]{0,30}(\d+)\s*[–—-]\s*\d+\s*(?:лет|года|год)",
        r"\b(\d+)\s*[–—-]\s*\d+\s*years?\b",
        r"(?:опыт|стаж)[^0-9\n]{0,30}(?:от\s*)?(\d+)\+?\s*(?:лет|года|год)",
        r"(?:at least|minimum(?:\s+of)?)\s+(\d+)\s+years?",
        r"(?:more than|over)\s+(\d+)\s+years?",
        r"(?:более|свыше)\s+(\d+)\s*(?:лет|года|год)",
        r"\b(\d+)\+?\s+years?(?:\s+of)?\s+experience\b",
        r"\b(\d+)\+\s+years?\b",
        r"\b(\d+)[–—-]\d+\s*(?:лет|года|год)\b",
    )
    preferred_markers = re.compile(
        r"\b(?:preferred|desirable|desired|nice[- ]to[- ]have|bonus|plus)\b|"
        r"\b(?:желательно|приветствуется|будет плюсом|будет преимуществом)\b"
    )
    required_markers = re.compile(
        r"\b(?:required|must have|minimum(?: of)?|at least)\b|"
        r"\b(?:обязател\w*|не менее|от)\b"
    )
    required_values: list[int] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            start, end = match.span(1)
            previous_boundary = max(
                (text.rfind(boundary, 0, start) for boundary in ".;!?\n"),
                default=-1,
            )
            next_boundaries = [
                position for boundary in ".;!?\n"
                if (position := text.find(boundary, end)) >= 0
            ]
            context_start = max(previous_boundary + 1, start - 60)
            context_end = min(min(next_boundaries, default=len(text)), end + 60)
            nearby = text[context_start:context_end]

            def marker_distance(marker: re.Match[str]) -> int:
                marker_start = context_start + marker.start()
                marker_end = context_start + marker.end()
                return start - marker_end if marker_end <= start else marker_start - end if marker_start >= end else 0

            preferred = [marker_distance(item) for item in preferred_markers.finditer(nearby)]
            required = [marker_distance(item) for item in required_markers.finditer(nearby)]
            # An explicitly preferred experience band must not become the
            # minimum used for candidate fit. Unlabelled years retain the
            # established conservative behavior.
            if preferred and (not required or min(preferred) < min(required)):
                continue
            required_values.append(int(match.group(1)))

    return max(required_values) if required_values else None

def _experience_fit(job: Job, facts: list[CandidateFact]) -> tuple[str | None, str | None]:
    candidate = _candidate_commercial_years(facts)
    required = _required_experience_years(job)
    if candidate is None or required is None:
        return None, None
    gap = required - candidate
    if gap <= 0:
        fit = "good"
    elif gap <= 2:
        fit = "stretch"
    else:
        fit = "skip"
    reason = f"опыт: commercial {candidate}+; требуется {required}+"
    return fit, reason

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
        # Staff is an engineering level only when it qualifies a technical
        # role. Lower-barrier titles such as "hotel staff" mean employees,
        # not senior engineers, and must retain their normal fit evaluation.
        r"\bstaff(?:[\s-]+level)?[\s:/-]+(?:[\w+#./-]+\s+){0,4}(?:engineer|developer|scientist|researcher|programmer|devops|sre)\b",
        r"\b(?:engineer|developer|scientist|researcher|programmer|devops|sre)[\s,(/:\-–—]+staff\b",
        r"\bhead\b",
        r"\barchitect\b",
        r"\bстарш(?:ий|ая|ее)\b",
        r"\bведущ(?:ий|ая|ее)\b",
        r"\bруководител[ья]\b",
    )
    if any(re.search(pattern, title) for pattern in hard_patterns):
        return "senior", "senior/lead уровень в названии"

    # Use the same required-year extraction as candidate experience fit. A
    # preferred 5+ year band must not override an actual three-year minimum.
    required_years = _required_experience_years(job)
    if required_years is not None and required_years >= 5:
        return "high_experience", "требование 5+ лет/высокого опыта"

    stretch_experience = (
        r"(?:опыт|стаж)[^0-9\n]{0,30}(?:от\s*)?(?:3|4)\+?\s*(?:лет|года)",
        r"(?:3|4)\+\s*years?",
        r"(?:at least)\s+(?:3|4)\s+years?",
        # HH commonly exposes the broad platform band "3–6 лет" on cards.
        r"(?:опыт[^\n]{0,30})?3[–—-]6\s*лет",
        r"3[–—-]6\s*years?",
    )
    if required_years is not None and required_years >= 3 and any(
        re.search(pattern, text) for pattern in stretch_experience
    ):
        return "stretch", "требуется около 3–4 лет опыта"

    return None, None


def non_actionable_role_reason(job: Job) -> str | None:
    """Keep explicit non-openings and unpaid roles out of automatic Good results."""
    title = (job.title or "").casefold()
    unpaid_patterns = (
        r"\bvolunteer\b",
        r"\bvoluntary\b",
        r"\bunpaid\b",
        r"\bволонт[её]р",
        r"\bнеоплачиваем",
    )
    if any(re.search(pattern, title) for pattern in unpaid_patterns):
        return "волонтёрская/неоплачиваемая роль"
    if re.search(r"\bexpression of interest(?: form)?\b", title):
        return "форма предварительного интереса, не подтверждённая открытая вакансия"
    return None


def _career_role_scope_reason(job: Job, settings: dict) -> str | None:
    """Exclude measured end-user support/management false Goods on Career-first."""
    if search_strategy(settings) != "career_first":
        return None
    title = (job.title or "").casefold()
    target_engineering = re.search(
        r"\b(?:devops|sre|site reliability|infrastructure|platform engineer)\b", title
    )
    outside_roles = (
        (r"\b(?:desktop|workstation)\b.*\bsupport\b|\b(?:help|service)\s*desk\b",
         "роль пользовательской поддержки вне Career-first"),
        (r"\bengineering manager\b", "управленческая инженерная роль вне Career-first"),
    )
    if target_engineering:
        return None
    for pattern, reason in outside_roles:
        if re.search(pattern, title):
            return reason
    return None


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

def _normalize_salary_currency(value: str | None) -> str:
    currency = (value or "").upper().strip()
    return {"RUR": "RUB"}.get(currency, currency)


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
    industry_tags = getattr(job, "industry_tags", None)
    if not isinstance(industry_tags, (list, tuple)):
        industry_tags = []
    industry_hay = " ".join(
        str(value).casefold() for value in industry_tags if isinstance(value, str)
    )
    chosen_resume = choose_resume(job, resumes)

    employer_action, employer_reason = employer_decision(job.company, industry_tags, settings)
    if employer_action == "block":
        return MatchResult(0, 0, 0, 0, 0, "Исключено по политике работодателя: " + str(employer_reason), chosen_resume, "unknown", "skip")

    # Existing saved profiles may still carry the old sector terms. Sector
    # preferences now belong to the explicit ALLOW/WARN/BLOCK policy.
    exclude = [term for term in _terms(settings, "exclude_terms") if term not in LEGACY_INDUSTRY_EXCLUSIONS]
    exclusion_hay = f"{hay} {industry_hay}"
    hit_exclude = [x for x in exclude if x and x in exclusion_hay]
    if hit_exclude:
        return MatchResult(0, 0, 0, 0, 0, "Исключено по фильтру: " + ", ".join(hit_exclude), chosen_resume, "excluded", "skip")

    signals = analyze_job_signals(job)
    enabled = _enabled_tracks(settings)
    viable = signals.tracks & enabled
    if "relocation" in enabled and _relocation_country_match(job, settings):
        viable.add("relocation")
    if signals.tracks and not viable:
        return MatchResult(0, 0, 0, 0, 0, "Режим этой вакансии выключен", chosen_resume, "disabled", "skip")

    preferred = _terms(settings, "preferred_terms")
    strong = _terms(settings, "strong_terms")
    fact_text = " ".join(x.value for x in facts if x.active is not False).casefold()
    preferred_hits = [x for x in preferred if x in hay and x in fact_text]
    strong_hits = [x for x in strong if x in hay and x in fact_text]

    title_tokens = role_tokens(job.title)
    query_hits: list[str] = []
    generic_role_tokens = {
        "engineer", "administrator", "admin", "specialist", "developer",
        "инженер", "администратор", "специалист", "разработчик",
    }
    role_queries = [query.casefold() for query in discovery_queries(settings)]
    for query in role_queries:
        all_tokens = _matching_role_tokens(query)
        meaningful = all_tokens - generic_role_tokens
        tokens = meaningful or all_tokens
        if tokens and tokens <= title_tokens:
            query_hits.append(query)

    technical = min(100, 40 + min(25, len(query_hits) * 20) + len(preferred_hits) * 6 + len(strong_hits) * 7)
    if role_queries and not query_hits:
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
    non_actionable_reason = non_actionable_role_reason(job)
    if non_actionable_reason:
        fit = "skip"
    career_scope_reason = _career_role_scope_reason(job, settings)
    if career_scope_reason:
        fit = "skip"
    experience_fit, experience_reason = _experience_fit(job, facts)
    if experience_fit == "stretch" and fit == "good":
        fit = "stretch"
    elif experience_fit == "skip":
        fit = "skip"
        technical = min(technical, 52)

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

    minimums = {
        _normalize_salary_currency(currency): value
        for currency, value in (settings.get("minimum_salary") or {}).items()
    }
    minimum = minimums.get(_normalize_salary_currency(job.salary_currency))
    if minimum is None:
        salary = 58 if not (job.salary_from or job.salary_to) else 72
    else:
        observed = job.salary_to or job.salary_from or 0
        period = str(getattr(job, "salary_period", None) or "").strip().casefold()
        if period in {"annual", "yearly", "per-year"}:
            # Profile minimums are monthly. Preserve the source's annual
            # amount in storage/display and compare its monthly equivalent.
            observed /= 12
        if period not in {"monthly", "per-month", "annual", "yearly", "per-year"}:
            # Hourly/weekly pay needs contracted hours or weeks; do not
            # invent those to claim that a monthly minimum has been met.
            salary = 58
        else:
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
    user_allow = employer_action == "allow" and bool(employer_reason and employer_reason.startswith("решение пользователя"))
    if user_allow:
        risk_penalty, risk_reason = 0, None
    if employer_action == "warn":
        risk_penalty = max(risk_penalty, 14)
        risk_reason = employer_reason or risk_reason
    if risk_reason and fit == "good":
        fit = "stretch"
    total -= risk_penalty

    if signals.remote_eligibility == "no" and track == "remote":
        total = min(total, 45)
    if signals.relocation_blocked and country not in {"", "RU"} and track == "relocation":
        total = min(total, 40)

    if experience_fit == "skip":
        total = min(total, 58)
    elif experience_fit == "stretch" and seniority is None:
        total = min(total, 72)

    if non_actionable_reason:
        total = min(total, 58)
    if career_scope_reason:
        total = min(total, 58)


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
    if non_actionable_reason:
        bits.append(non_actionable_reason)
    if career_scope_reason:
        bits.append(career_scope_reason)
    if experience_reason:
        bits.append(experience_reason)
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
    if employer_reason and employer_action == "warn" and risk_reason != employer_reason:
        bits.append(employer_reason)
    if signals.remote_reason:
        bits.append(signals.remote_reason)
    if signals.relocation_reason:
        bits.append(signals.relocation_reason)
    recommendation_scores = build_recommendation_breakdown(
        job, facts, signals, technical_score=technical, salary_score=salary,
        relocation_score=relocation, fit=fit, technical_text=technical_text,
    )
    return MatchResult(technical, geography, salary, relocation, max(0, min(100, total)), "; ".join(bits), chosen_resume, track, fit, recommendation_scores)
