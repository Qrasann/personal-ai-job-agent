import asyncio

import httpx
import pytest

from app.domain.job_text import format_salary
from app.domain.vacancy_availability import vacancy_availability
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


@pytest.mark.parametrize("application_link", [
    "https://user:secret@himalayas.app/companies/example/jobs/1",
    "https://himalayas.app:8443/companies/example/jobs/1",
    "https://himalayas.app:bad/companies/example/jobs/1",
    "https://evil.example/companies/example/jobs/1",
    "http://himalayas.app/companies/example/jobs/1",
])
def test_himalayas_rejects_unsafe_application_links(application_link):
    context = SourceContext(user_id=1, target_countries=["GE"], queries=["DevOps Engineer"])
    job = listing("unsafe", "DevOps Engineer", [], applicationLink=application_link)

    assert HimalayasSource.parse_payload({"jobs": [job]}, context) == []


def test_himalayas_accepts_https_application_link_without_credentials_or_nonstandard_port():
    context = SourceContext(user_id=1, target_countries=["GE"], queries=["DevOps Engineer"])
    job = listing("safe", "DevOps Engineer", [])

    parsed = HimalayasSource.parse_payload({"jobs": [job]}, context)

    assert len(parsed) == 1
    assert parsed[0].url == job["applicationLink"]


def test_himalayas_rejects_oversized_application_link():
    context = SourceContext(user_id=1, target_countries=["GE"], queries=["DevOps Engineer"])
    job = listing("oversized", "DevOps Engineer", [], applicationLink="https://himalayas.app/" + "x" * 2050)

    assert HimalayasSource.parse_payload({"jobs": [job]}, context) == []


def test_himalayas_bounds_long_provider_ids_with_stable_distinct_hashes():
    context = SourceContext(user_id=1, target_countries=["GE"], queries=["DevOps Engineer"])
    first = listing("a" * 300, "DevOps Engineer", [])
    second = listing("b" * 300, "DevOps Engineer", [])

    parsed = HimalayasSource.parse_payload({"jobs": [first, second, first]}, context)

    assert len(parsed) == 3
    assert len(parsed[0].source_job_id) <= 256
    assert parsed[0].source_job_id == parsed[2].source_job_id
    assert parsed[0].source_job_id != parsed[1].source_job_id


def test_himalayas_bounds_long_url_fallback_provider_id():
    context = SourceContext(user_id=1, target_countries=["GE"], queries=["DevOps Engineer"])
    long_url = "https://himalayas.app/" + "x" * 280
    job = listing(None, "DevOps Engineer", [], applicationLink=long_url)

    parsed = HimalayasSource.parse_payload({"jobs": [job]}, context)

    assert len(parsed) == 1
    assert len(parsed[0].source_job_id) <= 256
    assert parsed[0].url == long_url


def test_himalayas_accepts_documented_country_object_shape():
    jobs = HimalayasSource.parse_payload(
        {"jobs": [listing("am", "DevOps Engineer", [{"alpha2": "AM", "name": "Armenia", "slug": "armenia"}])]},
        SourceContext(user_id=1, target_countries=["AM"], queries=["DevOps Engineer"]),
    )

    assert len(jobs) == 1
    assert jobs[0].country == "AM"


@pytest.mark.parametrize("amount", [float("nan"), float("inf"), -float("inf"), 2**31, 10**400, True, -1, 0, 20.5])
def test_invalid_optional_salary_does_not_lose_valid_neighboring_jobs(amount):
    jobs = HimalayasSource.parse_payload({"jobs": [
        listing("invalid-salary", "DevOps Engineer", [], minSalary=amount, maxSalary=None),
        listing("valid", "DevOps Engineer", [], minSalary=72000),
    ]}, SourceContext(user_id=1, queries=["DevOps Engineer"]))
    assert [job.source_job_id for job in jobs] == ["invalid-salary", "valid"]
    assert jobs[0].salary_from is None
    assert jobs[1].salary_from == 72000


def test_storage_representable_salary_boundary_is_preserved():
    assert HimalayasSource._amount(2**31 - 1) == 2**31 - 1
    assert HimalayasSource._amount(72000.0) == 72000


@pytest.mark.parametrize("expiry", [1893456000, 1893456000000, "2030-01-01T00:00:00Z"])
def test_himalayas_preserves_listing_expiry_without_changing_publication_or_match_signals(expiry):
    context = SourceContext(user_id=1, target_countries=["GE"], queries=["DevOps Engineer"])
    row = listing("dated", "DevOps Engineer", [], expiryDate=expiry)
    with_expiry = HimalayasSource.parse_payload({"jobs": [row]}, context)[0]
    row.pop("expiryDate")
    without_expiry = HimalayasSource.parse_payload({"jobs": [row]}, context)[0]

    assert with_expiry.raw["availability"] == {
        "source_field": "expiryDate", "source_value": expiry,
        "expires_at": "2030-01-01T00:00:00+00:00",
    }
    assert with_expiry.published_at == without_expiry.published_at
    # Expiry is evidence for review; it neither promotes nor filters a match.
    dated_signals = analyze_job_signals(Job(**{
        key: getattr(with_expiry, key)
        for key in ("title", "description", "country", "work_mode", "remote_scope")
    }))
    undated_signals = analyze_job_signals(Job(**{
        key: getattr(without_expiry, key)
        for key in ("title", "description", "country", "work_mode", "remote_scope")
    }))
    assert dated_signals == undated_signals
    assert vacancy_availability(without_expiry.raw).status == "unknown"


@pytest.mark.parametrize("published", [True, "no date", "2026-10-11T14:49:28", []])
def test_himalayas_ambiguous_or_malformed_publication_dates_remain_unknown(published):
    context = SourceContext(user_id=1, queries=["DevOps Engineer"])
    jobs = HimalayasSource.parse_payload(
        {"jobs": [listing("bad-date", "DevOps Engineer", [], pubDate=published)]}, context,
    )
    assert jobs[0].published_at is None


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


def test_himalayas_remote_plan_searches_selected_support_for_both_markets(monkeypatch):
    calls = []

    async def get(self, url, **kwargs):
        params = kwargs["params"]
        calls.append(params)
        rows = []
        if params["q"] == "customer support":
            market = params["country"]
            rows = [listing(f"support-{market}", "Customer Support Representative", [market])]
        return httpx.Response(200, json={"jobs": rows}, request=httpx.Request("GET", url))

    async def no_wait(_delay):
        return None

    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    monkeypatch.setattr(asyncio, "sleep", no_wait)
    selected = ["warehouse worker", "production worker", "hotel staff", "kitchen assistant",
                "cleaner", "construction worker", "customer support"]
    context = SourceContext(user_id=1, current_country="RU", target_countries=["GE", "AM"], queries=selected.copy())
    jobs = asyncio.run(HimalayasSource().discover(context))

    assert len(calls) == 8
    assert calls[:2] == [
        {"sort": "recent", "page": 1, "q": "customer support", "country": "GE"},
        {"sort": "recent", "page": 1, "q": "customer support", "country": "AM"},
    ]
    assert {job.country for job in jobs} == {"GE", "AM"}
    assert all(job.visa_sponsorship is None and job.relocation is None for job in jobs)
    assert context.queries == selected


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
    source = HimalayasSource()
    jobs = asyncio.run(
        source.discover(
            SourceContext(user_id=1, target_countries=["GE", "AM"], queries=["DevOps Engineer"])
        )
    )

    assert source.partial_failures == 1
    assert source.discovery_diagnostics[0]["code"] == "NETWORK_CONNECT_TIMEOUT"
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
