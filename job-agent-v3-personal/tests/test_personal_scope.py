from app.database.models import CandidateFact, Job, SearchProfile
from app.matching.engine import score_job
from app.agents.job_signals import analyze_job_signals


def _search(modes=None):
    return SearchProfile(id=1, profile_id=1, settings={
        "queries": ["DevOps Engineer"],
        "preferred_terms": ["linux", "docker", "nginx"],
        "strong_terms": ["linux", "docker"],
        "exclude_terms": ["gambling"],
        "modes": modes or {"local_ru": True, "remote_international": True, "relocation": True},
        "minimum_salary": {"RUB": 100000, "USD": 1500},
    })


def _facts():
    return [CandidateFact(profile_id=1, value="Linux Docker Nginx practical experience")]


def test_russia_local_track_is_high_geography():
    job = Job(fingerprint="ru", title="DevOps Engineer", company="ACME", description="Linux Docker", country="RU")
    result = score_job(job, _search(), _facts(), [])
    assert result.track == "russia"
    assert result.geography_score >= 90


def test_remote_worldwide_is_good_from_russia():
    job = Job(fingerprint="rw", title="DevOps Engineer", company="ACME", description="Linux Docker. Remote worldwide.", country="DE", work_mode="remote")
    signals = analyze_job_signals(job)
    assert signals.remote_eligibility == "yes"
    result = score_job(job, _search(), _facts(), [])
    assert result.track == "remote"
    assert result.geography_score == 100


def test_us_only_remote_is_capped():
    job = Job(fingerprint="us", title="DevOps Engineer", company="ACME", description="Linux Docker. Remote US only. Must be authorized to work in the US.", country="US", work_mode="remote")
    result = score_job(job, _search(), _facts(), [])
    assert result.track == "remote"
    assert result.total_score <= 45


def test_relocation_sponsorship_detected():
    job = Job(fingerprint="rel", title="DevOps Engineer", company="ACME", description="Linux Docker. Visa sponsorship available and relocation assistance.", country="DE")
    signals = analyze_job_signals(job)
    assert signals.relocation_positive is True
    result = score_job(job, _search(), _facts(), [])
    assert result.track == "relocation"
    assert result.relocation_score >= 90


def test_disabled_remote_mode_filters_remote_only_job():
    job = Job(fingerprint="remoteoff", title="DevOps Engineer", company="ACME", description="Linux Docker Remote worldwide", country="DE", work_mode="remote")
    result = score_job(job, _search({"local_ru": True, "remote_international": False, "relocation": False}), _facts(), [])
    assert result.total_score == 0
