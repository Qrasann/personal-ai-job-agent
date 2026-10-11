from __future__ import annotations

import re

from app.agents.job_signals import JobSignals
from app.database.models import CandidateFact, Job
from app.domain.job_text import clean_html_text
from app.matching.technical_score import score_technical_v2


_INFRASTRUCTURE = {
    "linux": ("linux",),
    "containers": ("docker", "containerd", "podman"),
    "kubernetes": ("kubernetes", "k8s"),
    "infrastructure as code": ("terraform", "opentofu", "ansible"),
    "cloud": ("aws", "azure", "gcp", "cloud platform"),
    "observability": ("prometheus", "grafana", "opentelemetry", "datadog"),
    "ci/cd": ("ci/cd", "jenkins", "gitlab ci", "github actions"),
}
_GROWTH = (
    "professional development", "learning budget", "training budget", "mentorship",
    "career development", "обучение за счет компании", "обучение за счёт компании",
    "наставничество", "профессиональное развитие",
)
_FAST = (
    "immediate start", "start immediately", "urgent hiring", "start asap",
    "срочный выход", "выходить сразу", "приступить немедленно",
)
_FAST_BLOCK = ("start date next year", "hiring freeze", "начало работы в следующем году")


def _score(value: int | None, evidence: str = "") -> dict[str, int | str | None]:
    return {"score": value, "evidence": evidence}


def _explicit_term(text: str, terms: tuple[str, ...]) -> str | None:
    for sentence in re.split(r"[\n.;!?]+", text):
        for term in terms:
            if term not in sentence:
                continue
            before = sentence.split(term, 1)[0]
            if re.search(r"\b(?:no|not|without|не|нет|без)\b", before):
                continue
            return term
    return None


def build_recommendation_breakdown(
    job: Job,
    facts: list[CandidateFact],
    signals: JobSignals,
    *,
    technical_score: int,
    salary_score: int,
    relocation_score: int,
    fit: str,
) -> dict[str, dict[str, int | str | None]]:
    """Expose evidence-backed dimensions without inventing missing signals.

    This is an explainability breakdown, not a reweighting of the established
    notification score. Dimensions without source evidence stay null.
    """
    text = clean_html_text(" ".join((job.title or "", job.description or ""))).casefold()
    text = re.sub(r"\s+", " ", text)
    fact_text = " ".join(
        fact.value.casefold()
        for fact in facts
        if fact.active is not False and getattr(fact, "deleted_at", None) is None
    )

    growth_hit = _explicit_term(text, _GROWTH)
    fast_hit = _explicit_term(text, _FAST)
    fast_block = _explicit_term(text, _FAST_BLOCK)
    required_technical = score_technical_v2(job.description or "", facts)

    infrastructure_terms = {
        label: aliases
        for label, aliases in _INFRASTRUCTURE.items()
        if any(alias in text for alias in aliases)
    }
    infrastructure_score = None
    infrastructure_evidence = ""
    if infrastructure_terms:
        covered = [
            label for label, aliases in infrastructure_terms.items()
            if any(alias in fact_text for alias in aliases)
        ]
        infrastructure_score = round(100 * len(covered) / len(infrastructure_terms))
        infrastructure_evidence = f"{len(covered)}/{len(infrastructure_terms)} явно упомянутых групп подтверждены Candidate Facts"

    if signals.remote_eligibility == "yes":
        remote_score = 100
    elif signals.remote_eligibility == "uncertain":
        remote_score = 50
    elif signals.remote_eligibility == "no":
        remote_score = 0
    else:
        remote_score = None

    if signals.relocation_positive:
        relocation_evidence = signals.relocation_reason or "есть явный сигнал поддержки"
        relocation_value = relocation_score
    elif signals.relocation_blocked:
        relocation_evidence = signals.relocation_reason or "есть явное ограничение"
        relocation_value = relocation_score
    else:
        relocation_evidence = "поддержка и ограничения не подтверждены"
        relocation_value = None

    return {
        "technical": _score(technical_score, "текущая оценка технического соответствия"),
        "growth": _score(100 if growth_hit else None, growth_hit or "в описании нет явных условий развития"),
        "fast_exit": _score(100 if fast_hit else 0 if fast_block else None, fast_hit or fast_block or "срок выхода не указан"),
        "interview_risk": _score(100 - required_technical if required_technical is not None else None,
                                  f"явное покрытие обязательных требований; fit={fit}" if required_technical is not None else "нет извлечённых обязательных требований"),
        "salary": _score(salary_score if job.salary_from is not None or job.salary_to is not None else None,
                         "зарплата указана структурированными полями" if job.salary_from is not None or job.salary_to is not None else "зарплата не указана"),
        "remote": _score(remote_score, signals.remote_reason or "remote-сигнал не указан"),
        "relocation": _score(relocation_value, relocation_evidence),
        "security": _score(None, "нет сопоставимого публичного сигнала безопасности работодателя"),
        "infrastructure": _score(infrastructure_score, infrastructure_evidence or "инфраструктурные требования не найдены"),
        "competition": _score(None, "открытые источники не предоставляют число конкурирующих кандидатов"),
    }
