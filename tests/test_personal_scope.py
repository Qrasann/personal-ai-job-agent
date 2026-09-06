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


def test_senior_devops_is_below_notification_lane():
    job = Job(
        fingerprint="senior",
        title="Senior DevOps Engineer",
        company="ACME",
        description="Linux Docker Kubernetes. Remote.",
        country="RU",
        work_mode="remote",
    )
    result = score_job(job, _search(), _facts(), [])
    assert result.total_score <= 54
    assert "senior/lead" in result.reason


def test_russian_senior_title_is_below_notification_lane():
    job = Job(
        fingerprint="senior-ru",
        title="Старший DevOps-инженер",
        company="ACME",
        description="Linux Docker Kubernetes",
        country="RU",
    )
    result = score_job(job, _search(), _facts(), [])
    assert result.total_score <= 54


def test_three_plus_years_is_stretch_but_can_be_notified():
    job = Job(
        fingerprint="stretch",
        title="DevOps Engineer",
        company="ACME",
        description="Linux Docker. Опыт от 3 лет.",
        country="RU",
    )
    result = score_job(job, _search(), _facts(), [])
    assert 65 <= result.total_score <= 72
    assert "3–4" in result.reason


def test_hh_three_to_six_band_is_stretch_not_five_plus():
    job = Job(
        fingerprint="hh-3-6",
        title="DevOps Engineer",
        company="ACME",
        description="Linux Docker. Опыт работы 3–6 лет.",
        country="RU",
    )
    result = score_job(job, _search(), _facts(), [])
    assert 65 <= result.total_score <= 72
    assert "3–4" in result.reason
    assert "5+" not in result.reason


def test_explicit_five_plus_stays_below_notification_lane():
    job = Job(
        fingerprint="five-plus",
        title="DevOps Engineer",
        company="ACME",
        description="Linux Docker. Опыт от 5 лет.",
        country="RU",
    )
    result = score_job(job, _search(), _facts(), [])
    assert result.total_score <= 58
    assert "5+" in result.reason

def test_russia_city_and_work_mode_policy():
    search = _search()
    search.settings["local_city"] = "Тверь"
    search.settings["domestic_relocation"] = False

    local = Job(
        fingerprint="city-local",
        title="DevOps Engineer",
        company="ACME",
        description="Linux Docker",
        country="RU",
        city="Тверь",
        work_mode="Офис",
    )
    remote_other = Job(
        fingerprint="city-remote-other",
        title="DevOps Engineer",
        company="ACME",
        description="Linux Docker",
        country="RU",
        city="Москва",
        work_mode="Удалённо",
    )
    onsite_other = Job(
        fingerprint="city-onsite-other",
        title="DevOps Engineer",
        company="ACME",
        description="Linux Docker",
        country="RU",
        city="Москва",
        work_mode="Гибрид",
    )
    unknown = Job(
        fingerprint="city-unknown",
        title="DevOps Engineer",
        company="ACME",
        description="Linux Docker",
        country="RU",
    )

    local_result = score_job(local, search, _facts(), [])
    remote_result = score_job(remote_other, search, _facts(), [])
    onsite_result = score_job(onsite_other, search, _facts(), [])
    unknown_result = score_job(unknown, search, _facts(), [])

    assert local_result.geography_score == 95
    assert local_result.fit != "skip"
    assert remote_result.geography_score == 95
    assert remote_result.fit != "skip"
    assert onsite_result.geography_score <= 30
    assert onsite_result.fit == "skip"
    assert 60 <= unknown_result.geography_score < 95
    assert unknown_result.fit != "skip"

    search.settings["domestic_relocation"] = True
    relocation_result = score_job(onsite_other, search, _facts(), [])
    assert 60 <= relocation_result.geography_score < 95
    assert relocation_result.fit != "skip"
