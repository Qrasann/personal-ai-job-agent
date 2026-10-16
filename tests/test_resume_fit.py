import pytest

from app.database.models import CandidateFact, Job, ResumeProfile, SearchProfile
from app.matching.engine import choose_resume, score_job


def _resume(resume_id, content, *, active=True):
    return ResumeProfile(
        id=resume_id,
        profile_id=1,
        name=f"Resume {resume_id}",
        language="en",
        role="Infrastructure Engineer",
        content=content,
        active=active,
    )


def test_resume_selector_uses_resume_content_to_break_role_tie():
    job = Job(
        fingerprint="resume-content-fit",
        title="Infrastructure Engineer",
        company="ACME",
        description="Linux Docker Nginx systemd",
    )
    windows = _resume(2, "Windows Active Directory PowerShell")
    linux = _resume(1, "Linux Docker Nginx systemd")

    assert choose_resume(job, [windows, linux]) == 1

def test_resume_selector_ignores_inactive_resume():
    job = Job(
        fingerprint="resume-active-fit",
        title="Infrastructure Engineer",
        company="ACME",
        description="Linux Docker Nginx",
    )
    inactive = _resume(2, "Linux Docker Nginx", active=False)
    active = _resume(1, "Linux")

    assert choose_resume(job, [inactive, active]) == 1


@pytest.mark.parametrize(("role", "unrelated_role"), [
    ("QA Engineer", "Platform Engineer"),
    ("Go Developer", "Python Developer"),
    ("HR Specialist", "Recruitment Specialist"),
    ("C# Developer", "C++ Developer"),
    ("JavaScript Developer", "Java Developer"),
])
def test_resume_selector_prefers_exact_short_role_over_generic_tie(role, unrelated_role):
    job = Job(title=role, description="", country="AM")
    selected, unrelated = _resume(1, ""), _resume(2, "")
    selected.role, unrelated.role = role, unrelated_role
    assert choose_resume(job, [selected, unrelated]) == 1
    assert choose_resume(job, [unrelated, selected]) == 1


def test_resume_content_overlap_retains_short_technical_names_without_new_claims():
    job = Job(title="Developer", description="C# .NET", country="AM")
    selected, unrelated = _resume(1, "C#"), _resume(2, "Python")
    selected.role = unrelated.role = "Developer"
    assert choose_resume(job, [selected, unrelated]) == 1
    assert selected.content == "C#"


def test_resume_selection_does_not_inflate_match_score():
    search = SearchProfile(
        id=1,
        profile_id=1,
        settings={
            "queries": ["Infrastructure Engineer"],
            "preferred_terms": ["linux", "docker"],
            "strong_terms": ["linux"],
            "modes": {"local_ru": True},
        },
    )
    facts = [
        CandidateFact(
            profile_id=1,
            value="Linux Docker commercial experience",
            experience_type="commercial",
        )
    ]
    job = Job(
        fingerprint="resume-score-neutral",
        title="Infrastructure Engineer",
        company="ACME",
        description="Linux Docker",
        country="RU",
    )
    resume = _resume(7, "Linux Docker")

    without_resume = score_job(job, search, facts, [])
    with_resume = score_job(job, search, facts, [resume])

    assert with_resume.resume_id == 7
    assert with_resume.total_score == without_resume.total_score
    assert with_resume.technical_score == without_resume.technical_score
