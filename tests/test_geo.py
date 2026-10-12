from app.geo.countries import normalize_country, local_sources
from app.sources.registry import build_source_plan
from app.telegram.source_display import manual_source_line


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
    assert "arbeitnow" in ids
    assert "telegram" in ids


def test_selected_market_manual_sources_are_link_only_entries():
    ge_plan = {x.source_id: x for x in build_source_plan("RU", ["GE"])}
    am_plan = {x.source_id: x for x in build_source_plan("RU", ["AM"])}

    findjobs = ge_plan["findjobs_ge_manual"]
    assert findjobs.manual is True
    assert findjobs.url == "https://findjobs.ge/en/"
    assert findjobs.implemented is False
    assert findjobs.transport == "manual"

    ita_jobs = am_plan["ita_jobs_manual"]
    assert ita_jobs.manual is True
    assert ita_jobs.url == "https://jobs.ita.am/"
    assert ita_jobs.implemented is False
    assert "findjobs_ge_manual" not in am_plan

    for plan in (ge_plan, am_plan):
        etg = plan["emerging_travel_manual"]
        assert etg.manual is True
        assert etg.url == "https://www.emergingtravel.com/career/positions/166/"
        assert etg.implemented is False
        assert etg.transport == "manual"
        assert "B1+" in etg.availability_note


def test_manual_source_display_links_the_site_and_marks_manual_use():
    item = next(x for x in build_source_plan("RU", ["GE"]) if x.source_id == "findjobs_ge_manual")

    line = manual_source_line(item)

    assert '<a href="https://findjobs.ge/en/">Findjobs.ge · Georgia</a>' in line
    assert "ручной поиск" in line
    assert "written permission" in line

    etg = next(x for x in build_source_plan("RU", ["AM"]) if x.source_id == "emerging_travel_manual")
    etg_line = manual_source_line(etg)
    assert '<a href="https://www.emergingtravel.com/career/positions/166/">Emerging Travel Group · Junior DevOps</a>' in etg_line
    assert "ручной поиск" in etg_line
    assert "B1+" in etg_line
