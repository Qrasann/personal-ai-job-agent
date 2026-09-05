from __future__ import annotations

from typing import Iterable

from app.database.models import CandidateFact
from app.matching.fact_comparison import compare_facts


_EXPERIENCE_WEIGHTS: dict[str, float] = {
    "commercial": 1.00,
    "lab": 0.75,
    "unknown": 0.60,
    "learning": 0.40,
    "missing": 0.00,
}


def _coverage(items) -> float:
    if not items:
        return 0.0
    return sum(_EXPERIENCE_WEIGHTS[item.status] for item in items) / len(items)


def score_technical_v2(
    vacancy_text: str,
    facts: Iterable[CandidateFact],
) -> int | None:
    """Score structured technical requirements against Candidate Facts.

    Returns None when no explicit required technical requirements were found.
    The caller can then fall back to the legacy rule-based technical score.

    Required requirements dominate the score. When preferred requirements are
    also present, required requirements contribute 85% and preferred
    requirements contribute 15%. Other/unknown technical mentions do not
    increase the structured score.
    """
    comparison = compare_facts(vacancy_text, facts)

    required = comparison.items_for_importance("required")
    if not required:
        return None

    preferred = comparison.items_for_importance("preferred")

    required_score = _coverage(required)

    if not preferred:
        return max(0, min(100, round(required_score * 100)))

    preferred_score = _coverage(preferred)
    score = required_score * 85 + preferred_score * 15

    return max(0, min(100, round(score)))
