from app.geo.countries import normalize_country, local_sources
from app.sources.registry import build_source_plan


def test_country_aliases():
    assert normalize_country("GE") == "GE"
    assert normalize_country("Грузия") == "GE"
    assert normalize_country("Moldova") == "MD"


def test_georgia_local_sources():
    ids = {x["id"] for x in local_sources("GE")}
    assert {"jobs_ge", "hr_ge"}.issubset(ids)


def test_source_plan_keeps_international():
    ids = {x.source_id for x in build_source_plan("MD", ["GE"], include_international=True)}
    assert "rabota_md" in ids
    assert "jobs_ge" in ids
    assert "remoteok" in ids
    assert "telegram" in ids
