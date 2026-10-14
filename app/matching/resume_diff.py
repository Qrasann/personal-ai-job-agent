from __future__ import annotations

from app.matching.fact_comparison import FactComparison, extract_technical_requirements


def compare_resume_coverage(comparison: FactComparison, resume_text: str) -> dict[str, tuple[str, ...]]:
    """Compare detected vacancy skills with the chosen CV and active facts.

    This is a review aid only: it never edits or generates resume content.
    """
    resume_skills = set(extract_technical_requirements(resume_text or ""))
    result: dict[str, list[str]] = {
        "supported_in_resume": [],
        "supported_missing_from_resume": [],
        "resume_only_unconfirmed": [],
        "missing_from_both": [],
    }

    for requirement in comparison.requirements:
        fact_supported = requirement.status != "missing"
        in_resume = requirement.skill in resume_skills
        if fact_supported and in_resume:
            bucket = "supported_in_resume"
        elif fact_supported:
            bucket = "supported_missing_from_resume"
        elif in_resume:
            bucket = "resume_only_unconfirmed"
        else:
            bucket = "missing_from_both"
        result[bucket].append(requirement.skill)

    return {key: tuple(values) for key, values in result.items()}
