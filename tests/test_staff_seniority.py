import pytest

from app.database.models import Job, SearchProfile
from app.matching.engine import score_job


def _job(title, description="No previous experience is required.", *, sponsorship=None):
    return Job(
        fingerprint=f"staff-seniority-{title}",
        title=title,
        company="Example",
        description=description,
        country="AM",
        visa_sponsorship=sponsorship,
    )


def _search(*, exclude_terms=None):
    return SearchProfile(
        id=1,
        profile_id=1,
        settings={
            "search_strategy": "relocation_first",
            "relocation_queries": ["hotel staff", "warehouse worker"],
            "notify_min_score": 65,
            "exclude_terms": exclude_terms or [],
        },
    )


@pytest.mark.parametrize("title", ["Hotel Staff", "Kitchen Staff", "Warehouse Staff", "Staff Accountant"])
def test_lower_barrier_staff_titles_are_not_senior(title):
    job = _job(title)

    result = score_job(job, _search(), [], [])

    assert result.fit == "good"
    assert "senior/lead уровень" not in result.reason
    # Correcting a title does not establish sponsorship or guarantee that
    # the independent profile's unchanged threshold has been met.
    assert job.visa_sponsorship is None
    assert job.relocation is None
    assert result.relocation_score == 42
    assert result.total_score < 65


@pytest.mark.parametrize("title", [
    "Staff Engineer", "Staff Software Engineer", "Staff Linux Support Engineer",
    "Staff SRE", "Staff Data Scientist", "Software Engineer (Staff)",
    "Staff-level Infrastructure Engineer", "Staff Level Developer", "SRE — Staff",
])
def test_staff_technical_titles_keep_senior_restriction(title):
    result = score_job(_job(title, sponsorship=True), _search(), [], [])

    assert result.fit == "skip"
    assert result.total_score <= 54
    assert "senior/lead уровень" in result.reason


@pytest.mark.parametrize("level", ["Senior", "Lead", "Principal"])
def test_explicit_senior_titles_still_block_lower_barrier_roles(level):
    result = score_job(_job(f"{level} Hotel Staff", sponsorship=True), _search(), [], [])

    assert result.fit == "skip"
    assert result.total_score <= 54


def test_lower_barrier_staff_role_keeps_high_experience_restriction():
    result = score_job(
        _job("Hotel Staff", "At least 5 years of experience required.", sponsorship=True),
        _search(),
        [],
        [],
    )

    assert result.fit == "skip"
    assert result.total_score <= 58
    assert "высокого опыта" in result.reason


def test_lower_barrier_staff_role_keeps_management_restriction():
    result = score_job(
        _job("Hotel Staff", "Responsibilities: people management for the hotel team.", sponsorship=True),
        _search(),
        [],
        [],
    )

    assert result.fit == "skip"
    assert "требуется управление командой" in result.reason


def test_lower_barrier_staff_role_keeps_explicit_owner_exclusions():
    result = score_job(_job("Hotel Staff", sponsorship=True), _search(exclude_terms=["hotel"]), [], [])

    assert result.fit == "skip"
    assert result.total_score == 0
    assert result.reason == "Исключено по фильтру: hotel"
