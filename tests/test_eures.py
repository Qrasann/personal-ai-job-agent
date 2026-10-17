from __future__ import annotations

import asyncio
import ssl

import httpx
import pytest

from app.geo.countries import normalize_country
from app.sources.adapters.eures import EuresSource
from app.sources.base import SourceContext
from app.sources.registry import build_source_plan, source_capabilities


def search_row(**overrides):
    row = {
        "id": "MTAwMDEtMTAwMTEzOTMxMS1TIDE",
        "title": "Senior DevOps Engineer",
        "description": "Operate cloud infrastructure.",
        "creationDate": 1789814100284,
        "locationMap": {"DE": ["DE12B"]},
        "euresFlag": True,
        "employer": {"name": "Example GmbH"},
    }
    return {**row, **overrides}


def details(**overrides):
    profile = {
        "title": "Senior DevOps Engineer",
        "description": "<p>Operate cloud infrastructure.</p>",
        "euresFlag": True,
        "locations": [{"countryCode": "de", "cityName": "Berlin"}],
        "employer": {"name": "Example GmbH"},
        "applicationInstructions": [
            'Apply at <a href="https://careers.example.org/123">the employer</a>'
        ],
    }
    return {"jvProfiles": {"en": {**profile, **overrides}}}


def test_search_only_returns_employer_flagged_role_relevant_vacancies():
    payload = {"jvs": [search_row(), search_row(id="2", euresFlag=False),
                       search_row(id="3", title="Marketing assistant") ]}
    result = EuresSource.parse_search(payload, "DevOps Engineer")
    assert len(result) == 1
    assert result[0].source == "eures"
    assert result[0].raw["international_candidates"] is True
    assert result[0].country == "DE"
    assert result[0].visa_sponsorship is None
    assert result[0].relocation is None


def test_search_query_token_does_not_match_a_longer_unrelated_title_word():
    rows = [
        search_row(id="javascript", title="JavaScript Developer"),
        search_row(id="java", title="Java DevOps Engineer"),
    ]

    result = EuresSource.parse_search({"jvs": rows}, "Java")

    assert [job.source_job_id for job in result] == ["java"]


def test_eures_flag_is_not_visa_or_relocation_support():
    job = EuresSource.parse_search({"jvs": [search_row()]}, "DevOps")[0]
    job = EuresSource.enrich(job, details())
    assert job.country == "DE"
    assert normalize_country(job.country) == "DE"
    assert job.city == "Berlin"
    assert job.company == "Example GmbH"
    assert job.url == "https://careers.example.org/123"
    assert job.visa_sponsorship is None
    assert job.relocation is None
    assert job.raw["international_candidates"] is True
    assert job.raw["evidence_url"].endswith(job.source_job_id + "?requestLang=en")


def test_eures_city_collapses_source_padding_before_storage():
    padded = "CAHERCALLA COMMUNITY HOSPITAL" + (" " * 300) + "Cahercalla Comm Hosp, Co. Clare V95 NR59"
    job = EuresSource.parse_search({"jvs": [search_row()]}, "DevOps")[0]
    job = EuresSource.enrich(job, details(locations=[{"countryCode": "ie", "cityName": padded}]))
    assert job.country == "IE"
    assert job.city == "CAHERCALLA COMMUNITY HOSPITAL Cahercalla Comm Hosp, Co. Clare V95 NR59"
    assert len(job.city) <= 256


def test_eures_unusable_long_city_remains_unknown_with_source_value_preserved():
    source_city = "Subregion " * 40
    job = EuresSource.parse_search({"jvs": [search_row()]}, "DevOps")[0]
    job = EuresSource.enrich(job, details(locations=[{"countryCode": "ie", "cityName": source_city}]))
    assert job.country == "IE"
    assert job.city is None
    assert job.raw["location_text"] == source_city


def test_search_request_filters_for_cross_border_vacancies():
    request = EuresSource.request_payload("DevOps")
    assert request["keywords"] == [{"keyword": "DevOps", "specificSearchCode": "EVERYWHERE"}]
    assert request["euresFlagCodes"] == ["WITH"]
    assert request["resultsPerPage"] <= 50


def test_bad_search_contract_is_not_silently_empty():
    try:
        EuresSource.parse_search({"error": "unavailable"}, "DevOps")
    except ValueError as exc:
        assert "contract unavailable" in str(exc)
    else:
        raise AssertionError("invalid EURES response should fail")


def test_source_is_registered_as_public_discovery_only():
    plan = build_source_plan("RU", [])
    assert next(item for item in plan if item.source_id == "eures").implemented
    assert not source_capabilities("eures").apply


def test_discover_uses_active_queries_and_enriches_bounded_results(monkeypatch):
    calls = []

    async def post(self, url, json=None, **kwargs):
        calls.append(("post", url, json))
        payload = {"jvs": [search_row()]}
        return httpx.Response(200, json=payload, request=httpx.Request("POST", url))

    async def get(self, url, **kwargs):
        calls.append(("get", url, None))
        return httpx.Response(200, json=details(), request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    result = asyncio.run(EuresSource().discover(SourceContext(1, queries=["DevOps", "Cloud"])))
    assert len(result) == 1
    assert [call[0] for call in calls].count("post") == 2
    assert [call[0] for call in calls].count("get") == 1
    assert calls[0][2]["keywords"][0]["keyword"] == "DevOps"


def test_discover_requests_uncompressed_response_body(monkeypatch):
    client_headers = {}
    original_init = httpx.AsyncClient.__init__

    def capture_init(self, *args, **kwargs):
        client_headers.update(kwargs.get("headers") or {})
        original_init(self, *args, **kwargs)

    async def post(self, url, json=None, **kwargs):
        return httpx.Response(200, json={"jvs": []}, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx.AsyncClient, "__init__", capture_init)
    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    asyncio.run(EuresSource().discover(SourceContext(1, queries=["DevOps"])))

    assert client_headers["Accept-Encoding"] == "identity"


def test_discover_retries_transient_transport_failure(monkeypatch):
    calls = []

    async def post(self, url, json=None, **kwargs):
        calls.append(url)
        if len(calls) == 1:
            raise httpx.ReadError("TLS record layer failure", request=httpx.Request("POST", url))
        return httpx.Response(200, json={"jvs": []}, request=httpx.Request("POST", url))

    async def no_wait(_):
        return None

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    monkeypatch.setattr("app.sources.adapters.eures.asyncio.sleep", no_wait)
    source = EuresSource()
    result = asyncio.run(source.discover(SourceContext(1, queries=["DevOps"])))
    assert result == []
    assert len(calls) == 2
    assert source.retry_count == 1


def test_request_does_not_retry_http_status_errors():
    calls = []

    async def request(url):
        calls.append(url)
        return httpx.Response(503, request=httpx.Request("GET", url))

    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(EuresSource()._request_with_retry(request, "https://example.org"))
    assert len(calls) == 1


def test_request_retries_raw_ssl_error(monkeypatch):
    calls = []

    async def request(url):
        calls.append(url)
        if len(calls) == 1:
            raise ssl.SSLError("record layer failure")
        return httpx.Response(200, json={"ok": True}, request=httpx.Request("GET", url))

    async def no_wait(_):
        return None

    monkeypatch.setattr("app.sources.adapters.eures.asyncio.sleep", no_wait)
    response = asyncio.run(EuresSource()._request_with_retry(request, "https://example.org"))
    assert response.status_code == 200
    assert len(calls) == 2


def test_discover_keeps_successful_queries_when_another_exhausts_retries(monkeypatch):
    posts = []
    gets = []

    async def post(self, url, json=None, **kwargs):
        query = json["keywords"][0]["keyword"]
        posts.append(query)
        if query == "DevOps":
            raise ssl.SSLError("record layer failure")
        return httpx.Response(
            200, json={"jvs": [search_row(id="cloud", title="Cloud Engineer")]},
            request=httpx.Request("POST", url),
        )

    async def get(self, url, **kwargs):
        gets.append(url)
        return httpx.Response(200, json=details(title="Cloud Engineer"), request=httpx.Request("GET", url))

    async def no_wait(_):
        return None

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    monkeypatch.setattr("app.sources.adapters.eures.asyncio.sleep", no_wait)
    source = EuresSource()
    result = asyncio.run(source.discover(SourceContext(1, queries=["DevOps", "Cloud"])))
    assert [job.title for job in result] == ["Cloud Engineer"]
    assert posts == ["DevOps"] * 3 + ["Cloud"]
    assert len(gets) == 1
    assert source.partial_failures == 1


@pytest.mark.parametrize("bad_kind", ["http", "contract"])
def test_discover_keeps_second_query_after_first_bad_response(monkeypatch, bad_kind):
    async def post(self, url, json=None, **kwargs):
        query = json["keywords"][0]["keyword"]
        status = 503 if query == "DevOps" and bad_kind == "http" else 200
        payload = ({"error": "bad contract"} if query == "DevOps" and bad_kind == "contract"
                   else {"jvs": [search_row(id="cloud", title="Cloud Engineer")]})
        return httpx.Response(status, json=payload, request=httpx.Request("POST", url))

    async def get(self, url, **kwargs):
        return httpx.Response(200, json=details(title="Cloud Engineer"), request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    result = asyncio.run(EuresSource().discover(SourceContext(1, queries=["DevOps", "Cloud"])))
    assert [job.title for job in result] == ["Cloud Engineer"]


def test_discover_keeps_other_details_after_one_http_error(monkeypatch):
    async def post(self, url, json=None, **kwargs):
        rows = [search_row(id="first"), search_row(id="second")]
        return httpx.Response(200, json={"jvs": rows}, request=httpx.Request("POST", url))

    async def get(self, url, **kwargs):
        status = 404 if "first" in url else 200
        return httpx.Response(status, json=details(), request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    source = EuresSource()
    result = asyncio.run(source.discover(SourceContext(1, queries=["DevOps"])))
    assert [job.source_job_id for job in result] == ["second"]
    assert source.partial_failures == 1


def test_discover_reports_all_search_http_failures(monkeypatch):
    async def post(self, url, json=None, **kwargs):
        return httpx.Response(503, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(EuresSource().discover(SourceContext(1, queries=["DevOps", "Cloud"])))
