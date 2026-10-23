from __future__ import annotations

import asyncio
from pathlib import Path

import httpx
import pytest
import yaml
from urllib.parse import urlparse

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
    assert sum(len(item.openings) for item in watchlist.employers) == 15
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
    assert rows[("betsson-group", "8200701")].location == "Malta"
    assert rows[("betsson-group", "8200701")].suitability == "medium"
    assert next(item for item in watchlist.employers if item.id == "betsson-group").industry_tags == (
        "betting", "gambling"
    )
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

    context = SourceContext(user_id=1, current_country="RU", target_countries=["GE"], queries=["Reliability"])
    watchlist = load_employer_watchlist()
    greenhouse = next(item for item in watchlist.employers if item.ats == "greenhouse")
    jobs = EmployerCareerWatchSource.parse_board_payload(greenhouse, {
        "jobs": [{"id": 123, "title": "Site Reliability Engineer", "absolute_url": f"https://{next(iter(greenhouse.allowed_hosts))}/jobs/123", "location": {"name": "Amsterdam, Netherlands"}, "content": "<p>Kubernetes</p>"}]
    }, context)
    assert len(jobs) == 1
    job = jobs[0]
    assert job.source_job_id == f"{greenhouse.id}:123"
    assert job.url.endswith("/jobs/123")
    assert job.raw["provider_id"] == "123"
    assert job.raw["watchlist_verified_at"] == watchlist.verified_at.isoformat()
    assert job.raw["provider_feed_observed_at"]
    assert job.description == "Kubernetes"
    assert job.country == "NL" and job.city == "Amsterdam"
    assert job.raw["location_resolution"] == "provider_location_city_country"
    assert job.raw["visa_sponsorship_evidence"] == "unknown"
    assert job.raw["work_authorization_evidence"] == "unknown"
    assert job.raw["relocation_evidence"] == "unknown"


def test_employer_watch_matches_sre_alias_without_related_reliability_role():
    context = SourceContext(user_id=1, current_country="RU", target_countries=["GE"], queries=["Site Reliability Engineer"])
    employer = next(item for item in load_employer_watchlist().employers if item.ats == "greenhouse")
    host = next(iter(employer.allowed_hosts))
    jobs = EmployerCareerWatchSource.parse_board_payload(employer, {
        "jobs": [
            {"id": 123, "title": "SRE", "absolute_url": f"https://{host}/jobs/123", "location": {"name": "Amsterdam, Netherlands"}},
            {"id": 124, "title": "Software Engineer", "absolute_url": f"https://{host}/jobs/124", "location": {"name": "Amsterdam, Netherlands"}},
        ]
    }, context)
    assert [job.raw["provider_id"] for job in jobs] == ["123"]


def test_employer_watch_resolves_exact_country_only_office_without_city_guess():
    employer = next(
        item for item in load_employer_watchlist().employers
        if item.id == "betsson-group"
    )
    context = SourceContext(user_id=1, current_country="RU", target_countries=["MT"], queries=["DevOps"])
    jobs = EmployerCareerWatchSource.parse_board_payload(employer, {
        "jobs": [{
            "id": 8200701,
            "title": "Platform Core DevOps Engineer - Infra",
            "absolute_url": "https://job-boards.greenhouse.io/betsson/jobs/8200701",
            "location": {"name": "Malta"},
            "content": "Kubernetes and platform infrastructure",
        }]
    }, context)
    assert len(jobs) == 1
    assert jobs[0].city is None and jobs[0].country == "MT"
    assert jobs[0].raw["source_location"] == "Malta"
    assert jobs[0].raw["location_resolution"] == "provider_location_country"
    assert jobs[0].raw["industry_tags"] == ["betting", "gambling"]


def test_employer_watch_resolves_office_based_provider_wrapper_only():
    employer = next(item for item in load_employer_watchlist().employers if item.id == "canonical")
    context = SourceContext(user_id=1, queries=["Linux"])
    host = next(iter(employer.allowed_hosts))
    payload = {"jobs": [
        {
            "id": "office-london", "title": "Linux Support Engineer",
            "absolute_url": f"https://{host}/jobs/office-london",
            "location": {"name": "Office Based - London, UK"},
        },
        {
            "id": "home-apac", "title": "Linux Support Engineer",
            "absolute_url": f"https://{host}/jobs/home-apac",
            "location": {"name": "Home Based - APAC"},
        },
    ]}

    jobs = EmployerCareerWatchSource.parse_board_payload(employer, payload, context)

    assert (jobs[0].city, jobs[0].country) == ("London", "GB")
    assert jobs[0].raw["source_location"] == "Office Based - London, UK"
    assert jobs[0].raw["location_resolution"] == "provider_location_city_country"
    assert jobs[1].city is None and jobs[1].country is None
    assert jobs[1].raw["location_resolution"] is None


def test_employer_watch_fetches_bounded_public_ats_boards(monkeypatch) -> None:
    employers = [item for item in load_employer_watchlist().employers if item.api_url]
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        employer = next(item for item in employers if request.url.path == urlparse(item.api_url).path)
        calls.append(employer.id)
        host = next(iter(employer.allowed_hosts))
        if employer.ats == "greenhouse":
            payload = {"jobs": [{"id": "new-1", "title": "DevOps Engineer", "absolute_url": f"https://{host}/jobs/new-1", "location": {"name": "Remote"}}]}
        elif employer.ats == "lever":
            payload = [{"id": "new-1", "text": "DevOps Engineer", "hostedUrl": f"https://{host}/new-1", "categories": {"location": "Remote"}}]
        else:
            payload = {"content": [{"id": "new-1", "name": "DevOps Engineer", "postingUrl": f"https://{host}/new-1", "location": {"city": "Remote"}}]}
        return httpx.Response(200, json=payload)

    class MockClient(httpx.AsyncClient):
        def __init__(self, *args, **kwargs):
            kwargs["transport"] = httpx.MockTransport(handler)
            super().__init__(*args, **kwargs)

    monkeypatch.setattr("app.sources.adapters.employer_career_watch.httpx.AsyncClient", MockClient)
    context = SourceContext(user_id=1, queries=["DevOps"])
    jobs = asyncio.run(EmployerCareerWatchSource().discover(context))
    expected = {item.id for item in employers} - {"collectly", "devexperts"}
    assert len(jobs) == len(expected) == 10
    assert set(calls) == expected
    assert all(job.title == "DevOps Engineer" and job.country is None for job in jobs)


def test_employer_watch_rejects_unapproved_url_and_nonmatching_titles() -> None:
    employer = next(item for item in load_employer_watchlist().employers if item.ats == "lever")
    context = SourceContext(user_id=1, queries=["DevOps"])
    payload = [
        {"id": "unsafe", "text": "DevOps Engineer", "hostedUrl": "https://evil.example/jobs/unsafe"},
        {"id": "irrelevant", "text": "Sales Manager", "hostedUrl": f"https://jobs.lever.co/{employer.identifier}/irrelevant"},
    ]
    assert EmployerCareerWatchSource.parse_board_payload(employer, payload, context) == []


def test_employer_watch_keeps_exact_reviewed_opening_without_query_token_overlap() -> None:
    employer = next(
        item for item in load_employer_watchlist().employers
        if item.id == "xsolla"
    )
    reviewed = next(
        item for item in employer.openings
        if item.title == "Operations Engineer"
    )
    context = SourceContext(user_id=1, queries=["DevOps Engineer"])
    payload = [
        {
            "id": reviewed.provider_id,
            "text": reviewed.title,
            "hostedUrl": reviewed.url,
            "categories": {"location": reviewed.location},
            "descriptionPlain": "Infrastructure operations and production systems",
        },
        {
            "id": "unreviewed-operations",
            "text": "Business Operations Manager",
            "hostedUrl": "https://jobs.lever.co/xsolla/unreviewed-operations",
        },
    ]

    jobs = EmployerCareerWatchSource.parse_board_payload(employer, payload, context)

    assert len(jobs) == 1
    assert jobs[0].source_job_id == f"xsolla:{reviewed.provider_id}"
    assert jobs[0].title == "Operations Engineer"
    assert jobs[0].raw["reviewed_inventory_match"] is True
    assert jobs[0].raw["curated_suitability"] == "high"
    assert jobs[0].raw["work_authorization_evidence"] == "unknown"
    assert jobs[0].raw["visa_sponsorship_evidence"] == "unknown"
    assert jobs[0].raw["relocation_evidence"] == "unknown"


def test_smartrecruiters_structured_city_country_is_normalized():
    employer = next(item for item in load_employer_watchlist().employers if item.ats == "smartrecruiters")
    context = SourceContext(user_id=1, queries=["Reliability"])
    payload = {"content": [{
        "id": "reliable-id", "name": "Site Reliability Engineer",
        "postingUrl": "https://jobs.smartrecruiters.com/Devexperts/reliable-id-sre",
        "location": {"city": "Sofia", "region": "Sofia City Province", "country": "Bulgaria"},
    }]}
    jobs = EmployerCareerWatchSource.parse_board_payload(employer, payload, context)
    assert len(jobs) == 1
    assert (jobs[0].city, jobs[0].country) == ("Sofia", "BG")
    assert jobs[0].raw["location_resolution"] == "provider_structured_country_city"

    payload["content"][0]["location"]["remote"] = True
    remote = EmployerCareerWatchSource.parse_board_payload(employer, payload, context)[0]
    assert remote.city is None and remote.country is None
    assert remote.raw["source_location"] == "Sofia, Sofia City Province, Bulgaria"


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
