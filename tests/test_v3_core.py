from app.domain.jobs import NormalizedJob
from app.database.models import CandidateFact, Job, ResumeProfile, SearchProfile
from app.matching.engine import score_job, choose_resume
from app.sources.adapters.telegram_ingest import parse_telegram_job
from app.sources.registry import build_source_plan


def test_cross_source_fingerprint_is_source_independent():
    a = NormalizedJob(source="hh", source_job_id="1", title="DevOps Engineer", company="ACME", country="GE")
    b = NormalizedJob(source="telegram", source_job_id="x", title="DevOps Engineer", company="ACME", country="GE")
    assert a.canonical_fingerprint() == b.canonical_fingerprint()


def test_resume_selector_prefers_linux_resume_for_linux_job():
    job = Job(fingerprint="x", title="Linux Administrator", company="ACME", description="linux nginx systemd")
    resumes = [
        ResumeProfile(id=1, profile_id=1, name="DevOps", language="en", role="DevOps Engineer"),
        ResumeProfile(id=2, profile_id=1, name="Linux", language="en", role="Linux Administrator"),
    ]
    assert choose_resume(job, resumes) == 2


def test_matching_uses_candidate_facts_and_excludes_gambling():
    search = SearchProfile(id=1, profile_id=1, settings={
        "preferred_terms": ["linux", "docker", "nginx"],
        "strong_terms": ["linux", "docker"],
        "exclude_terms": ["gambling"],
        "remote_worldwide": True,
        "relocation_enabled": True,
        "minimum_salary": {"USD": 1500},
    })
    facts = [
        CandidateFact(profile_id=1, value="Practical Linux and Docker experience"),
        CandidateFact(profile_id=1, value="Configured Nginx reverse proxy"),
    ]
    good = Job(fingerprint="g", title="DevOps Engineer", company="ACME", description="Linux Docker Nginx", work_mode="remote", salary_from=2000, salary_currency="USD")
    bad = Job(fingerprint="b", title="DevOps Engineer", company="Casino", description="gambling platform Linux Docker")
    assert score_job(good, search, facts, []).total_score >= 70
    assert score_job(bad, search, facts, []).total_score == 0


def test_telegram_parser_extracts_remote_and_salary():
    job = parse_telegram_job("DevOps Engineer\nRemote worldwide\n$3000-4500\nDocker Kubernetes", source_ref="test")
    assert job.work_mode == "remote"
    assert job.salary_from == 3000
    assert job.salary_to == 4500
    assert job.salary_currency == "USD"


def test_georgia_plan_has_real_collectors_and_moldova_is_registered():
    ge = {x.source_id: x for x in build_source_plan("GE", [], include_international=False)}
    md = {x.source_id: x for x in build_source_plan("MD", [], include_international=False)}
    assert ge["jobs_ge"].implemented is True
    assert ge["hr_ge"].implemented is True
    assert "rabota_md" in md
