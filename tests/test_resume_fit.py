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
