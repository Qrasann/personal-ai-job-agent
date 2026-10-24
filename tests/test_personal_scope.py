from app.database.models import CandidateFact, Job, SearchProfile
from app.matching.engine import score_job
from app.agents.job_signals import analyze_job_signals
import pytest


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


@pytest.mark.parametrize("description", [
    "On site. Work must be completed at the physical location. There is no option to work remotely.",
    "Work setting: Remote location. Willing to relocate.",
])
def test_onsite_job_bank_language_is_not_remote_work(description):
    job = Job(
        fingerprint="jobbank-onsite",
        title="light duty cleaner",
        company="ACME",
        description=description,
        country="CA",
    )

    signals = analyze_job_signals(job)

    assert "remote_international" not in signals.tracks
    assert signals.remote_eligibility == "unknown"


def test_job_bank_onsite_destination_stays_in_relocation_lane():
    search = SearchProfile(id=2, profile_id=1, settings={
        "search_strategy": "relocation_first",
        "queries": ["DevOps Engineer"],
        "relocation_queries": ["cleaner"],
        "target_countries": ["CA"],
        "modes": {"local_ru": False, "remote_international": True, "relocation": True},
    })
    job = Job(
        fingerprint="jobbank-onsite-relocation",
        title="light duty cleaner",
        company="ACME",
        description=(
            "On site. Work must be completed at the physical location. "
            "There is no option to work remotely."
        ),
        country="CA",
    )

    result = score_job(job, search, [], [])

    assert result.track == "relocation"
    assert result.geography_score == 85
    assert "remote" not in result.reason


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


@pytest.mark.parametrize("description, blocked", [
    ("We do not provide visa sponsorship or relocation assistance.", True),
    ("Visa sponsorship is not available. No relocation assistance.", True),
    ("Must already have the right to work in Germany.", True),
    ("Visa sponsorship may be available.", False),
    ("We provide visa sponsorship guidance.", False),
])
def test_matching_signal_does_not_promote_negated_or_unknown_support(description, blocked):
    job = Job(fingerprint="support-conservative", title="DevOps Engineer", description=description, country="DE")
    signals = analyze_job_signals(job)
    assert signals.relocation_positive is False
    assert "relocation" not in signals.tracks
    assert signals.relocation_blocked is blocked


def test_matching_signal_keeps_explicit_denial_over_stale_positive_flags():
    job = Job(
        fingerprint="support-stale", title="DevOps Engineer", country="DE",
        description="No visa sponsorship. Relocation assistance is not available.",
        visa_sponsorship=True, relocation=True,
    )
    signals = analyze_job_signals(job)
    assert signals.relocation_positive is False
    assert signals.relocation_blocked is True


@pytest.mark.parametrize("description, offered, denied", [
    (
        "We do not provide relocation assistance, but we offer visa sponsorship.",
        "visa_sponsorship", "relocation",
    ),
    (
        "We do not provide visa sponsorship, but we offer relocation assistance.",
        "relocation", "visa_sponsorship",
    ),
])
def test_separate_support_offer_survives_another_component_refusal(description, offered, denied):
    job = Job(
        fingerprint="support-mixed", title="DevOps Engineer", company="ACME", country="DE",
        description=f"Linux Docker. {description}",
    )
    signals = analyze_job_signals(job)
    assert signals.support_components[offered] is True
    assert signals.support_components[denied] is False
    assert signals.support_components["work_permit"] is None
    assert signals.relocation_positive is True
    assert signals.relocation_blocked is False
    assert "relocation" in signals.tracks
    assert "часть помощи явно не предоставляется" in signals.relocation_reason
    result = score_job(job, _search(), _facts(), [])
    assert result.track == "relocation"
    assert result.relocation_score >= 90
    assert result.total_score > 40


def test_authorization_prerequisite_still_blocks_a_separate_support_offer():
    job = Job(
        fingerprint="support-prerequisite", title="DevOps Engineer", company="ACME", country="DE",
        description="Linux Docker. We offer relocation assistance. Must already have the right to work in Germany.",
    )
    signals = analyze_job_signals(job)
    assert signals.support_components["relocation"] is True
    assert signals.support_components["visa_sponsorship"] is None
    assert signals.relocation_blocked is True
    result = score_job(job, _search(), _facts(), [])
    assert result.relocation_score == 5
    assert result.total_score <= 40


def test_same_component_refusal_still_wins_over_offer():
    job = Job(
        fingerprint="support-conflict", title="DevOps Engineer", company="ACME", country="DE",
        description="Linux Docker. We offer visa sponsorship. Visa sponsorship is not available.",
    )
    signals = analyze_job_signals(job)
    assert signals.support_components["visa_sponsorship"] is False
    assert signals.relocation_positive is False
    assert signals.relocation_blocked is True
    result = score_job(job, _search(), _facts(), [])
    assert result.relocation_score == 5


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

def test_rub_and_rur_share_salary_minimum():
    search = _search()
    search.settings["minimum_salary"] = {"RUB": 100000}

    below = Job(
        fingerprint="salary-rur-below",
        title="DevOps Engineer",
        company="ACME",
        description="Linux Docker",
        country="RU",
        salary_to=80000,
        salary_currency="RUR",
        salary_period="monthly",
    )
    above = Job(
        fingerprint="salary-rur-above",
        title="DevOps Engineer",
        company="ACME",
        description="Linux Docker",
        country="RU",
        salary_to=150000,
        salary_currency="RUR",
        salary_period="monthly",
    )

    below_result = score_job(below, search, _facts(), [])
    above_result = score_job(above, search, _facts(), [])

    assert below_result.salary_score == 80
    assert above_result.salary_score == 100
