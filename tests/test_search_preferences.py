from dataclasses import replace

from app.domain.jobs import NormalizedJob
from app.search.preferences import job_priority, source_enabled, vacancy_allowed


def make_job(**kwargs):
    base = NormalizedJob(source="hh", source_job_id="1", title="DevOps Engineer", company="Example", country="RU", city="Tver")
    return replace(base, **kwargs)


def test_source_filter_is_backward_compatible():
    assert source_enabled({}, "hh")
    assert not source_enabled({"disabled_sources": ["hh"]}, "hh")


def test_current_and_selected_city_scope():
    cfg = {"local_city": "Tver", "selected_cities": ["Moscow"], "geography": {"configured": True, "include_current_city": True, "include_other_cities": False, "include_other_countries": False, "worldwide": False}}
    assert vacancy_allowed(make_job(city="Tver"), cfg, current_country="RU")
    assert vacancy_allowed(make_job(city="Moscow"), cfg, current_country="RU")
    assert not vacancy_allowed(make_job(city="Kazan"), cfg, current_country="RU")


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
