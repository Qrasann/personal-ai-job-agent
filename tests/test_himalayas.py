import asyncio

import httpx
import pytest

from app.domain.job_text import format_salary
from app.agents.job_signals import analyze_job_signals
from app.database.models import Job
from app.sources.adapters.himalayas import HimalayasSource
from app.sources.base import SourceContext
from app.sources.registry import build_source_plan, source_capabilities


def listing(guid, title, restrictions, **extra):
    return {
        "guid": guid,
        "title": title,
        "companyName": "Example Corp",
        "locationRestrictions": restrictions,
        "employmentType": "Full Time",
        "minSalary": 72000,
        "maxSalary": 96000,
        "salaryPeriod": "annual",
        "currency": "USD",
        "description": "&lt;p&gt;Linux, Docker and incident response.&lt;/p&gt;",
        "pubDate": 1791730168,
        "applicationLink": f"https://himalayas.app/companies/example/jobs/{guid}",
        **extra,
    }


def test_himalayas_keeps_only_selected_location_restrictions_and_preserves_salary_period():
    context = SourceContext(
        user_id=1,
        current_country="RU",
        target_countries=["GE", "AM"],
        queries=["DevOps Engineer", "Infrastructure Engineer"],
    )
    jobs = HimalayasSource.parse_payload(
        {
            "jobs": [
                listing("world", "DevOps Engineer", []),
                listing("country", "Infrastructure Engineer", ["Armenia", "Georgia"]),
                listing("wrong-country", "DevOps Engineer", ["United States"]),
                listing("unknown-region", "DevOps Engineer", ["EMEA"]),
                listing("wrong-role", "Data Analyst", ["Georgia"]),
            ]
        },
        context,
    )

    assert [job.source_job_id for job in jobs] == ["world", "country"]
    worldwide, country_limited = jobs
    assert worldwide.country is None
    assert worldwide.remote_scope == "worldwide"
    assert worldwide.work_mode == "remote"
    assert country_limited.country == "GE"
    assert country_limited.remote_scope == "Armenia, Georgia"
    assert worldwide.description == "Linux, Docker and incident response."
    assert worldwide.salary_from == 72000
    assert worldwide.salary_to == 96000
    assert worldwide.salary_period == "annual"
    assert worldwide.published_at == "2026-10-11T14:49:28+00:00"
    assert format_salary(
        worldwide.salary_from,
        worldwide.salary_to,
        worldwide.salary_currency,
        period=worldwide.salary_period,
    ) == "72 000–96 000 $ в год"
    assert worldwide.url.startswith("https://himalayas.app/")


def test_himalayas_accepts_documented_country_object_shape():
    jobs = HimalayasSource.parse_payload(
        {"jobs": [listing("am", "DevOps Engineer", [{"alpha2": "AM", "name": "Armenia", "slug": "armenia"}])]},
        SourceContext(user_id=1, target_countries=["AM"], queries=["DevOps Engineer"]),
    )

    assert len(jobs) == 1
    assert jobs[0].country == "AM"


def test_himalayas_missing_location_restrictions_remains_unknown():
    row = listing("missing-location", "DevOps Engineer", [])
    row.pop("locationRestrictions")
    jobs = HimalayasSource.parse_payload(
        {"jobs": [row]},
        SourceContext(user_id=1, target_countries=["GE"], queries=["DevOps Engineer"]),
    )

    assert len(jobs) == 1
    assert jobs[0].remote_scope == "unknown"
    assert jobs[0].country is None
    signals = analyze_job_signals(
        Job(
            fingerprint="missing-location",
            title=jobs[0].title,
            description=jobs[0].description,
            country=jobs[0].country,
            work_mode=jobs[0].work_mode,
            remote_scope=jobs[0].remote_scope,
        )
    )
    assert signals.remote_eligibility == "uncertain"


def test_himalayas_bounds_saved_remote_scope_length():
    restrictions = ["Georgia", "Armenia", *(f"Country {index}" for index in range(40))]
    jobs = HimalayasSource.parse_payload(
        {"jobs": [listing("many-countries", "DevOps Engineer", restrictions)]},
        SourceContext(user_id=1, target_countries=["GE", "AM"], queries=["DevOps Engineer"]),
    )

    assert len(jobs) == 1
    assert len(jobs[0].remote_scope) <= 128


def test_himalayas_discovery_queries_selected_markets_with_a_bounded_request_count(monkeypatch):
    calls = []

    async def get(self, url, **kwargs):
        calls.append((url, kwargs))
        return httpx.Response(200, json={"jobs": []}, request=httpx.Request("GET", url))

    async def no_wait(_delay):
        return None

    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    monkeypatch.setattr(asyncio, "sleep", no_wait)
    context = SourceContext(
        user_id=1,
        current_country="RU",
        target_countries=["GE", "AM", "DE", "FR"],
        queries=["DevOps Engineer", "Infrastructure Engineer", "Linux Administrator", "SRE", "ignored fifth query"],
    )

    result = asyncio.run(HimalayasSource().discover(context))

    assert result == []
    assert len(calls) == HimalayasSource.max_markets * HimalayasSource.max_queries
    assert calls[0][0] == HimalayasSource.endpoint
    assert calls[0][1]["params"] == {"sort": "recent", "page": 1, "q": "DevOps Engineer", "country": "GE"}
    assert calls[1][1]["params"]["country"] == "AM"
    assert all("ignored fifth query" not in str(kwargs) for _, kwargs in calls)


def test_himalayas_keeps_successes_when_one_market_request_fails(monkeypatch):
    async def get(self, url, **kwargs):
        if kwargs["params"].get("country") == "AM":
            request = httpx.Request("GET", url)
            raise httpx.ConnectTimeout("temporary timeout", request=request)
        return httpx.Response(
            200,
            json={"jobs": [listing("ge", "DevOps Engineer", ["Georgia"])]},
            request=httpx.Request("GET", url),
        )

    async def no_wait(_delay):
        return None

    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    monkeypatch.setattr(asyncio, "sleep", no_wait)
    jobs = asyncio.run(
        HimalayasSource().discover(
            SourceContext(user_id=1, target_countries=["GE", "AM"], queries=["DevOps Engineer"])
        )
    )

    assert [job.source_job_id for job in jobs] == ["ge"]


def test_himalayas_rejects_an_unrecognized_api_payload():
    with pytest.raises(ValueError, match="contract unavailable"):
        HimalayasSource.parse_payload({"error": "unavailable"}, SourceContext(user_id=1))


def test_himalayas_is_registered_as_remote_public_discovery_only():
    plan = build_source_plan("RU", ["GE"])
    source = next(item for item in plan if item.source_id == "himalayas")

    assert source.implemented
    assert source.scope == "remote"
    assert not source_capabilities("himalayas").apply
    assert not source_capabilities("himalayas").messages
