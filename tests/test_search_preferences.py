from dataclasses import replace

import pytest

from app.domain.jobs import NormalizedJob
from app.search.preferences import discovery_queries, job_priority, search_strategy, source_enabled, vacancy_allowed


def make_job(**kwargs):
    base = NormalizedJob(source="hh", source_job_id="1", title="DevOps Engineer", company="Example", country="RU", city="Tver")
    return replace(base, **kwargs)


def test_source_filter_is_backward_compatible():
    assert source_enabled({}, "hh")
    assert not source_enabled({"disabled_sources": ["hh"]}, "hh")


def test_strict_salary_floor_only_excludes_proven_comparable_below_minimum():
    settings = {
        "strict_salary_floor": True,
        "minimum_salary": {"USD": 3000},
    }
    assert not vacancy_allowed(make_job(salary_from=2000, salary_to=2500, salary_currency="USD"), settings)
    assert vacancy_allowed(make_job(salary_from=2000, salary_to=3200, salary_currency="USD"), settings)
    assert not vacancy_allowed(make_job(salary_to=2500, salary_currency="USD"), settings)
    assert vacancy_allowed(make_job(salary_from=2000, salary_currency="USD"), settings)
    assert vacancy_allowed(make_job(salary_from=2500, salary_to=29000, salary_currency="EUR"), settings)
    assert vacancy_allowed(make_job(salary_from=2000, salary_to=2500, salary_currency="USD", salary_period="hourly"), settings)
    assert vacancy_allowed(make_job(salary_from=None, salary_to=None, salary_currency=None), settings)


def test_strict_salary_floor_supports_annual_salary_and_rur_alias():
    settings = {"strict_salary_floor": True, "minimum_salary": {"RUB": 100000}}
    assert not vacancy_allowed(
        make_job(salary_from=900000, salary_to=1_100_000, salary_currency="RUR", salary_period="annual"),
        settings,
    )
    assert vacancy_allowed(
        make_job(salary_from=1_200_000, salary_currency="RUB", salary_period="annual"),
        settings,
    )


def test_strict_salary_floor_is_opt_in():
    job = make_job(salary_from=1000, salary_to=2000, salary_currency="USD")
    assert vacancy_allowed(job, {"minimum_salary": {"USD": 3000}})


def test_current_and_selected_city_scope():
    cfg = {"local_city": "Tver", "selected_cities": ["Moscow"], "geography": {"configured": True, "include_current_city": True, "include_other_cities": False, "include_other_countries": False, "worldwide": False}}
    assert vacancy_allowed(make_job(city="Tver"), cfg, current_country="RU")
    assert vacancy_allowed(make_job(city="Moscow"), cfg, current_country="RU")
    assert not vacancy_allowed(make_job(city="Kazan"), cfg, current_country="RU")


def test_relocation_first_excludes_onsite_jobs_in_current_country():
    cfg = {
        "search_strategy": "relocation_first",
        "target_countries": ["GE", "AM"],
    }
    local_onsite = make_job(country="RU", city="Tyumen", work_mode="onsite")

    assert not vacancy_allowed(local_onsite, cfg, current_country="RU")


def test_relocation_first_keeps_remote_and_unknown_country_jobs():
    cfg = {
        "search_strategy": "relocation_first",
        "target_countries": ["GE", "AM"],
    }
    remote_ru = make_job(country="RU", city="Moscow", work_mode="remote")
    unknown_country = make_job(country=None, city="Tbilisi", work_mode="onsite")

    assert vacancy_allowed(remote_ru, cfg, current_country="RU")
    assert vacancy_allowed(unknown_country, cfg, current_country="RU")


def test_relocation_first_allows_domestic_move_only_when_explicit():
    cfg = {
        "search_strategy": "relocation_first",
        "target_countries": ["GE", "AM"],
        "domestic_relocation": True,
    }
    local_onsite = make_job(country="RU", city="Tyumen", work_mode="onsite")

    assert vacancy_allowed(local_onsite, cfg, current_country="RU")
    assert not vacancy_allowed(
        local_onsite,
        {**cfg, "domestic_relocation": "false"},
        current_country="RU",
    )


def test_career_first_keeps_current_country_onsite_jobs():
    cfg = {"search_strategy": "career_first", "target_countries": ["GE", "AM"]}
    local_onsite = make_job(country="RU", city="Tyumen", work_mode="onsite")

    assert vacancy_allowed(local_onsite, cfg, current_country="RU")


def test_selected_country_can_be_the_only_foreign_country():
    cfg = {"target_countries": ["DE"], "geography": {"configured": True, "include_current_city": True, "include_other_cities": False, "include_other_countries": False, "worldwide": False}}
    assert vacancy_allowed(make_job(country="DE", city="Berlin"), cfg, current_country="RU")
    assert not vacancy_allowed(make_job(country="ES", city="Madrid"), cfg, current_country="RU")


def test_required_visa_is_hard_gate():
    cfg = {"relocation_preferences": {"visa_sponsorship": "require"}}
    assert vacancy_allowed(make_job(visa_sponsorship=True), cfg, current_country="RU")
    assert not vacancy_allowed(make_job(visa_sponsorship=False), cfg, current_country="RU")


def test_text_signals_for_relocation_package_and_work_permit():
    cfg = {"relocation_preferences": {"relocation_package": "require", "work_permit": "require"}}
    item = make_job(country="DE", city="Berlin", description="We provide a relocation package and work permit support.")
    assert vacancy_allowed(item, cfg, current_country="RU")


def test_priority_prefers_target_country_and_source():
    cfg = {"source_priorities": {"hh": 25, "remoteok": 100}, "country_priorities": {"ES": 100, "RU": 25}, "target_countries": ["ES"], "relocation_preferences": {"visa_sponsorship": "prefer"}}
    local = make_job(source="hh", country="RU")
    target = make_job(source="remoteok", country="ES", city="Madrid", visa_sponsorship=True)
    assert job_priority(target, cfg, current_country="RU") > job_priority(local, cfg, current_country="RU")


def test_balanced_strategy_combines_career_and_relocation_queries():
    cfg = {
        "search_strategy": "balanced",
        "queries": ["DevOps Engineer", "DevOps Engineer"],
        "relocation_queries": ["warehouse worker", "hotel staff"],
    }
    assert discovery_queries(cfg, "fallback") == [
        "DevOps Engineer",
        "warehouse worker",
        "hotel staff",
    ]


def test_each_strategy_keeps_its_query_track_independent():
    cfg = {"queries": ["SRE"], "relocation_queries": ["factory worker"]}
    assert discovery_queries({**cfg, "search_strategy": "career_first"}) == ["SRE"]
    assert discovery_queries({**cfg, "search_strategy": "relocation_first"}) == ["factory worker"]


def test_relocation_strategy_falls_back_without_disabling_discovery():
    cfg = {"search_strategy": "relocation_first", "relocation_queries": []}
    assert discovery_queries(cfg, "DevOps Engineer") == ["DevOps Engineer"]
    assert search_strategy({"search_strategy": "unexpected"}) == "balanced"


def test_relocation_strategy_prioritizes_evidence_but_not_unknown_as_false():
    cfg = {"search_strategy": "relocation_first"}
    unknown = make_job(country="DE", city="Berlin")
    supported = make_job(
        country="DE",
        city="Berlin",
        description="Relocation package and work permit support are provided.",
    )
    assert vacancy_allowed(unknown, cfg, current_country="RU")
    assert job_priority(supported, cfg, current_country="RU") > job_priority(unknown, cfg, current_country="RU")


def test_relocation_strategy_prioritizes_remote_work_without_claiming_scope():
    cfg = {"search_strategy": "relocation_first", "target_countries": ["GE", "AM"]}
    remote = make_job(country="GE", city="Tbilisi", work_mode="remote", remote_scope="unspecified")
    onsite = make_job(country="GE", city="Tbilisi", work_mode="onsite")

    assert job_priority(remote, cfg, current_country="RU") > job_priority(onsite, cfg, current_country="RU")
    assert vacancy_allowed(remote, cfg, current_country="RU")
    assert remote.remote_scope == "unspecified"


def test_remote_priority_applies_to_both_profiles_and_explicit_remote_modes():
    remote = make_job(work_mode="Удалённо")
    office = make_job(work_mode="Офис")
    relocation = {"search_strategy": "relocation_first"}
    career = {"search_strategy": "career_first"}
    balanced = {"search_strategy": "balanced"}

    assert job_priority(remote, relocation) > job_priority(office, relocation)
    assert job_priority(remote, career) > job_priority(office, career)
    assert job_priority(remote, balanced) > job_priority(office, balanced)
    not_remote = make_job(work_mode="not remote")
    assert job_priority(not_remote, relocation) == job_priority(office, relocation)
    assert job_priority(not_remote, career) == job_priority(office, career)


def test_remote_scope_can_signal_remote_work_but_unknown_scope_cannot():
    relocation = {"search_strategy": "relocation_first"}
    remote_scope = make_job(work_mode=None, remote_scope="unspecified")
    unknown = make_job(work_mode=None, remote_scope="unknown")

    assert job_priority(remote_scope, relocation) > job_priority(unknown, relocation)


@pytest.mark.parametrize("key", ["visa_sponsorship", "relocation", "relocation_package"])
def test_explicit_support_denial_never_satisfies_require_or_prefer(key):
    denied = make_job(description="We do not provide visa sponsorship or relocation assistance.")
    unknown = make_job()
    assert not vacancy_allowed(denied, {"relocation_preferences": {key: "require"}})
    assert vacancy_allowed(denied, {"relocation_preferences": {key: "exclude"}})
    preferred = {"search_strategy": "relocation_first", "relocation_preferences": {key: "prefer"}}
    assert job_priority(denied, preferred) == job_priority(unknown, preferred)


@pytest.mark.parametrize("description", [
    "Must already have the right to work in Germany.",
    "A valid work permit is required.",
    "You must obtain a work permit.",
])
def test_authorization_prerequisite_is_not_employer_permit_assistance(description):
    item = make_job(description=description)
    assert not vacancy_allowed(item, {"relocation_preferences": {"work_permit": "require"}})
    assert vacancy_allowed(item, {})


@pytest.mark.parametrize("raw", [
    {"relocation": None},
    {"visa_sponsorship": False, "work_permit": None},
    {"visa_sponsorship": True, "relocation": "unknown"},
    {"navigation": "Visa sponsorship and relocation assistance are provided."},
])
def test_raw_metadata_is_not_support_prose(raw):
    item = make_job(raw=raw)
    assert not vacancy_allowed(item, {"relocation_preferences": {"relocation": "require"}})
    assert not vacancy_allowed(item, {"relocation_preferences": {"visa_sponsorship": "require"}})


def test_explicit_denial_overrides_a_stale_positive_normalized_flag():
    item = make_job(
        relocation=True, visa_sponsorship=True,
        description="No visa sponsorship. Relocation assistance is not provided.",
    )
    assert not vacancy_allowed(item, {"relocation_preferences": {"visa_sponsorship": "require"}})
    assert not vacancy_allowed(item, {"relocation_preferences": {"relocation": "require"}})


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
def test_mixed_support_policies_remain_independent(description, offered, denied):
    item = make_job(description=description)
    assert vacancy_allowed(item, {"relocation_preferences": {offered: "require", denied: "exclude"}})
    assert not vacancy_allowed(item, {"relocation_preferences": {denied: "require"}})
    assert job_priority(item, {"relocation_preferences": {offered: "prefer"}}) > job_priority(item, {})
    assert job_priority(item, {"relocation_preferences": {denied: "prefer"}}) == job_priority(item, {})
