from __future__ import annotations

import asyncio
from dataclasses import replace
from pathlib import Path

import httpx
import pytest
import yaml

from app.sources.employer_watch import probe_employer, probe_watchlist
from app.sources.employer_watchlist import load_employer_watchlist
from app.sources.adapters.employer_career_watch import EmployerCareerWatchSource
from app.sources.base import SourceContext
from app.sources.registry import build_source_plan, source_capabilities


def test_curated_watchlist_has_realistic_bounded_pilot() -> None:
    watchlist = load_employer_watchlist()

    assert 10 <= len(watchlist.employers) <= 20
    assert len({item.id for item in watchlist.employers}) == len(watchlist.employers)
    assert all(item.enabled and item.openings for item in watchlist.employers)
    assert sum(len(item.openings) for item in watchlist.employers) == 14
    assert {item.ats for item in watchlist.employers} == {
        "custom", "greenhouse", "lever", "smartrecruiters"
    }


def test_priority_openings_and_unknown_eligibility_are_explicit() -> None:
    watchlist = load_employer_watchlist()
    rows = {
        (employer.id, opening.provider_id): opening
        for employer in watchlist.employers
        for opening in employer.openings
    }

    assert rows[("emerging-travel-group", "167")].title == "Technical Support Specialist"
    assert rows[("canonical", "6448444")].title == "Associate Linux Support Engineer"
    assert rows[("nebius", "4967085101")].title == "Site Reliability Engineer - Early Talent"
    assert rows[("xsolla", "fe6a2e57-3aa8-4226-93f0-1264e815507e")].title == "Operations Engineer"
    assert all(
        evidence == "unknown"
        for opening in rows.values()
        for evidence in (opening.work_authorization, opening.visa_sponsorship, opening.relocation)
    )


def test_employer_watch_is_a_global_common_search_source_with_provenance() -> None:
    plan = next(item for item in build_source_plan("RU", ["GE"]) if item.source_id == "employer_career_watch")
    assert plan.implemented and plan.scope == "global"
    assert source_capabilities("employer_career_watch").discovery
    assert not source_capabilities("employer_career_watch").apply

    context = SourceContext(user_id=1, current_country="RU", target_countries=["GE"], queries=["SRE"])
    jobs = asyncio.run(EmployerCareerWatchSource().discover(context))
    watchlist = load_employer_watchlist()
    expected = sum(len(item.openings) for item in watchlist.employers if item.enabled)
    assert len(jobs) == expected == 14
    for job in jobs:
        employer_id, provider_id = job.source_job_id.split(":", 1)
        employer = next(item for item in watchlist.employers if item.id == employer_id)
        opening = next(item for item in employer.openings if item.provider_id == provider_id)
        assert job.url == opening.url
        assert job.raw["provider_id"] == provider_id
        assert job.raw["catalog_verified_at"] == watchlist.verified_at.isoformat()
        assert job.country is None and job.city is None
        assert job.raw["visa_sponsorship_evidence"] == "unknown"
        assert job.raw["work_authorization_evidence"] == "unknown"
        assert job.raw["relocation_evidence"] == "unknown"


def test_watchlist_rejects_unreviewed_api_endpoint(tmp_path: Path) -> None:
    original = yaml.safe_load(Path("data/employer_watchlist.yaml").read_text(encoding="utf-8"))
    original["employers"][1]["api_url"] = "https://example.test/jobs"
    target = tmp_path / "watchlist.yaml"
    target.write_text(yaml.safe_dump(original), encoding="utf-8")

    with pytest.raises(ValueError, match="endpoint"):
        load_employer_watchlist(target)


def test_watchlist_rejects_posting_outside_employer_hosts(tmp_path: Path) -> None:
    original = yaml.safe_load(Path("data/employer_watchlist.yaml").read_text(encoding="utf-8"))
    original["employers"][0]["openings"][0]["url"] = "https://example.test/job/166"
    target = tmp_path / "watchlist.yaml"
    target.write_text(yaml.safe_dump(original), encoding="utf-8")

    with pytest.raises(ValueError, match="host contract"):
        load_employer_watchlist(target)


def test_probe_compares_provider_ids_without_treating_count_as_fit() -> None:
    employer = next(item for item in load_employer_watchlist().employers if item.id == "canonical")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.host == "boards-api.greenhouse.io"
        return httpx.Response(200, json={"jobs": [{"id": 6448444}, {"id": 999}]})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await probe_employer(employer, client=client)

    result = asyncio.run(run())
    assert result.status == "changed"
    assert result.advertised_count == 2
    assert result.current_openings == 1
    assert result.missing_provider_ids == ("5370815",)


def test_probe_rejects_changed_response_contract() -> None:
    employer = next(item for item in load_employer_watchlist().employers if item.id == "xsolla")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"unexpected": []})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await probe_employer(employer, client=client)

    result = asyncio.run(run())
    assert result.status == "unavailable"
    assert result.error_code == "ValueError"
    assert result.current_openings == 0


def test_watchlist_probe_has_overall_bound_per_employer(monkeypatch) -> None:
    employer = next(item for item in load_employer_watchlist().employers if item.id == "canonical")

    async def stuck(*args, **kwargs):
        await asyncio.sleep(1)

    class ImmediateTimeout:
        async def __aenter__(self):
            raise TimeoutError

        async def __aexit__(self, *args):
            return False

    monkeypatch.setattr("app.sources.employer_watch.probe_employer", stuck)
    monkeypatch.setattr("app.sources.employer_watch.asyncio.timeout", lambda _seconds: ImmediateTimeout())

    result = asyncio.run(probe_watchlist((employer,)))
    assert result[0].status == "unavailable"
    assert result[0].error_code == "PROBE_TIMEOUT"
