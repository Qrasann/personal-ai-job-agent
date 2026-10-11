from __future__ import annotations

from app.database.models import CandidateFact, Job
from app.matching.engine import score_job
from app.database.models import SearchProfile


def _search():
    return SearchProfile(id=1, profile_id=1, settings={"queries": ["DevOps Engineer"]})


def test_recommendation_dimensions_use_evidence_and_keep_missing_data_unknown():
    job = Job(
        fingerprint="rec-1", title="DevOps Engineer", company="Example",
        description=("Required: Linux, Kubernetes. Mentorship and professional development. "
                     "Start immediately. Remote worldwide with relocation assistance."),
        country="DE", work_mode="remote", salary_from=None, salary_to=None,
    )
    facts = [CandidateFact(profile_id=1, value="Commercial Linux administration")]

    result = score_job(job, _search(), facts, [])

    scores = result.recommendation_scores
    assert scores["technical"]["score"] == result.technical_score
    assert scores["growth"]["score"] == 100
    assert scores["fast_exit"]["score"] == 100
    assert scores["interview_risk"]["score"] == 70
    assert scores["salary"]["score"] is None
    assert scores["remote"]["score"] == 100
    assert scores["relocation"]["score"] == result.relocation_score
    assert scores["infrastructure"]["score"] == 50
    assert scores["security"]["score"] is None
    assert scores["competition"]["score"] is None


def test_recommendation_breakdown_does_not_change_legacy_total_score():
    job = Job(
        fingerprint="rec-2", title="DevOps Engineer", company="Example",
        description="Linux Docker", country="RU", salary_from=120_000,
        salary_to=150_000, salary_currency="RUB", work_mode="office",
    )
    result = score_job(job, _search(), [], [])

    assert result.total_score == 70
    assert result.recommendation_scores["competition"]["score"] is None
    assert result.recommendation_scores["salary"]["score"] == result.salary_score


def test_negated_growth_and_fast_start_phrases_are_not_positive_evidence():
    job = Job(
        fingerprint="rec-3", title="DevOps Engineer", company="Example",
        description="No mentorship and no immediate start available.", country="RU",
    )
    result = score_job(job, _search(), [], [])

    assert result.recommendation_scores["growth"]["score"] is None
    assert result.recommendation_scores["fast_exit"]["score"] is None


def test_interview_risk_uses_necessary_qualifications_section():
    job = Job(
        fingerprint="rec-necessary-qualifications",
        title="Infrastructure Engineer",
        company="Example",
        description=(
            "Necessary Qualifications:\n"
            "Minimum 3 years of Linux system administration experience.\n"
            "Minimum 2 years of AWS production experience.\n"
            "Preferred:\nTerraform."
        ),
        country="GE",
    )
    facts = [CandidateFact(profile_id=1, value="Linux", experience_type="commercial")]

    result = score_job(job, _search(), facts, [])

    assert result.recommendation_scores["interview_risk"]["score"] is not None
    assert result.recommendation_scores["interview_risk"]["score"] > 0
    assert "явное покрытие обязательных требований" in result.recommendation_scores["interview_risk"]["evidence"]
