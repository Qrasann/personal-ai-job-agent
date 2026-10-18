from __future__ import annotations

from app.matching.fact_comparison import FactComparison, extract_technical_requirements


def compare_resume_coverage(comparison: FactComparison, resume_text: str) -> dict[str, object]:
    """Compare detected vacancy skills with the chosen CV and active facts.

    This is a review aid only: it never edits or generates resume content.
    """
    resume_skills = set(extract_technical_requirements(resume_text or ""))
    groups = comparison.alternative_groups + comparison.preferred_alternative_groups
    grouped_skills = {skill for group in groups for skill in group}
    result: dict[str, list[str]] = {
        "supported_in_resume": [],
        "supported_missing_from_resume": [],
        "resume_only_unconfirmed": [],
        "missing_from_both": [],
    }

    for requirement in comparison.requirements:
        if requirement.skill in grouped_skills:
            continue
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

    requirements = {item.skill: item for item in comparison.requirements}
    alternatives = []
    for group in groups:
        fact_options = tuple(
            skill for skill in group
            if skill in requirements and requirements[skill].status != "missing"
        )
        resume_options = tuple(skill for skill in group if skill in resume_skills)
        confirmed_options = tuple(skill for skill in group if skill in fact_options and skill in resume_options)
        unconfirmed_resume_options = tuple(skill for skill in resume_options if skill not in fact_options)
        if confirmed_options:
            status = "confirmed"
        elif resume_options:
            status = "resume_unconfirmed"
        elif fact_options:
            status = "facts_not_in_resume"
        else:
            status = "missing"
        alternatives.append({
            "options": tuple(group),
            "status": status,
            "candidate_fact_options": fact_options,
            "resume_options": resume_options,
            "confirmed_options": confirmed_options,
            "unconfirmed_resume_options": unconfirmed_resume_options,
        })
    return {
        **{key: tuple(values) for key, values in result.items()},
        "alternative_groups": tuple(alternatives),
    }
