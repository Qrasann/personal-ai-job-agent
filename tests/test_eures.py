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
    assert result[0].raw["location_resolution"] == "eures_location_map_country"
    assert result[0].visa_sponsorship is None
    assert result[0].relocation is None


def test_search_query_token_does_not_match_a_longer_unrelated_title_word():
    rows = [
        search_row(id="javascript", title="JavaScript Developer"),
        search_row(id="java", title="Java DevOps Engineer"),
    ]

    result = EuresSource.parse_search({"jvs": rows}, "Java")

    assert [job.source_job_id for job in result] == ["java"]


def test_generic_engineer_token_does_not_admit_unrelated_eures_roles():
    rows = [
        search_row(id="devops", title="DevOps Specialist"),
        search_row(id="data", title="Data Engineer"),
        search_row(id="manufacturing", title="Manufacturing Quality Engineer"),
    ]

    result = EuresSource.parse_search({"jvs": rows}, "DevOps Engineer")

    assert [job.source_job_id for job in result] == ["devops"]


@pytest.mark.parametrize("value", [True, False])
def test_boolean_creation_date_remains_unknown(value):
    assert EuresSource._timestamp(value) is None


def test_malformed_optional_search_metadata_does_not_drop_other_eures_results():
    malformed_optional = search_row(
        id="optional-metadata", locationMap=7, employer=["invalid shape"],
    )

    result = EuresSource.parse_search(
        {"jvs": [search_row(id="valid"), malformed_optional]}, "DevOps"
    )

    assert [job.source_job_id for job in result] == ["valid", "optional-metadata"]
    assert result[1].country is None
    assert result[1].company == ""


def test_eures_flag_is_not_visa_or_relocation_support():
    job = EuresSource.parse_search({"jvs": [search_row()]}, "DevOps")[0]
    job = EuresSource.enrich(job, details())
    assert job.country == "DE"
    assert normalize_country(job.country) == "DE"
    assert job.city == "Berlin"
    assert job.raw["location_resolution"] == "eures_structured_city_country"
    assert job.company == "Example GmbH"
    assert job.url == "https://careers.example.org/123"
    assert job.visa_sponsorship is None
    assert job.relocation is None
    assert job.raw["international_candidates"] is True
    assert job.raw["evidence_url"].endswith(job.source_job_id + "?requestLang=en")


@pytest.mark.parametrize("target", [
    "https://user:password@careers.example.org/123",
    "javascript:alert(1)",
    "https://[invalid/123",
])
def test_eures_ignores_unsafe_application_instruction_links(target):
    job = EuresSource.parse_search({"jvs": [search_row()]}, "DevOps")[0]

    enriched = EuresSource.enrich(job, details(
        applicationInstructions=[f'<a href="{target}">Apply</a>']
    ))

    assert enriched.url == EuresSource.portal_url


def test_eures_long_application_url_uses_portal_fallback_to_preserve_clickability():
    target = "https://careers.example.org/" + "x" * 600
    job = EuresSource.parse_search({"jvs": [search_row()]}, "DevOps")[0]

    enriched = EuresSource.enrich(job, details(
        applicationInstructions=[f'<a href="{target}">Apply</a>']
    ))

    assert enriched.url == EuresSource.portal_url


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
    assert job.raw["location_resolution"] == "eures_structured_country"


def test_eures_detail_with_country_only_records_structured_country_provenance():
    job = EuresSource.parse_search({"jvs": [search_row()]}, "DevOps")[0]
    job = EuresSource.enrich(job, details(locations=[{"countryCode": "ie"}]))

    assert job.country == "IE"
    assert job.city is None
    assert job.raw["location_resolution"] == "eures_structured_country"


def test_eures_multiple_locations_do_not_arbitrarily_select_first_country_or_city():
    job = EuresSource.parse_search({"jvs": [search_row()]}, "DevOps")[0]
    job = EuresSource.enrich(job, details(locations=[
        {"countryCode": "de", "cityName": "Berlin"},
        {"countryCode": "fr", "cityName": "Paris"},
    ]))

    assert job.country is None
    assert job.city is None
    assert job.raw["location_resolution"] == "eures_multiple_locations_ambiguous"


def test_eures_multiple_cities_keep_only_the_common_verified_country():
    job = EuresSource.parse_search({"jvs": [search_row()]}, "DevOps")[0]
    job = EuresSource.enrich(job, details(locations=[
        {"countryCode": "de", "cityName": "Berlin"},
        {"countryCode": "de", "cityName": "Hamburg"},
    ]))

    assert job.country == "DE"
    assert job.city is None
    assert job.raw["location_resolution"] == "eures_multiple_locations_same_country"


def test_eures_repeated_same_city_locations_resolve_city_and_country():
    job = EuresSource.parse_search({"jvs": [search_row()]}, "DevOps")[0]
    job = EuresSource.enrich(job, details(locations=[
        {"countryCode": "de", "cityName": "Berlin"},
        {"countryCode": "DE", "cityName": " Berlin "},
    ]))

    assert job.country == "DE"
    assert job.city == "Berlin"
    assert job.raw["location_resolution"] == "eures_multiple_locations_same_city_country"


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
    assert [job.source_job_id for job in result] == ["first", "second"]
    assert result[0].description == "Operate cloud infrastructure."
    assert result[0].url == EuresSource.portal_url
    assert source.partial_failures == 1


def test_discover_returns_search_cards_when_every_detail_request_fails(monkeypatch):
    async def post(self, url, json=None, **kwargs):
        return httpx.Response(200, json={"jvs": [
            search_row(id="first"), search_row(id="second", title="Cloud Engineer"),
        ]}, request=httpx.Request("POST", url))

    async def get(self, url, **kwargs):
        return httpx.Response(503, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    source = EuresSource()

    result = asyncio.run(source.discover(SourceContext(1, queries=["Engineer"])))

    assert [job.source_job_id for job in result] == ["first", "second"]
    assert all(job.description == "Operate cloud infrastructure." for job in result)
    assert all(job.url == EuresSource.portal_url for job in result)
    assert source.partial_failures == 2
    assert [item["operation"] for item in source.discovery_diagnostics] == ["detail_request"] * 2


def test_detail_request_bound_does_not_truncate_valid_search_card_results(monkeypatch):
    detail_ids = []

    async def post(self, url, json=None, **kwargs):
        return httpx.Response(200, json={"jvs": [
            search_row(id=f"posting-{index}", title=f"DevOps Engineer {index}")
            for index in range(5)
        ]}, request=httpx.Request("POST", url))

    async def get(self, url, **kwargs):
        detail_ids.append(url)
        return httpx.Response(200, json=details(), request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    source = EuresSource()
    source.max_details = 2

    result = asyncio.run(source.discover(SourceContext(1, queries=["DevOps"])))

    assert len(result) == 5
    assert len(detail_ids) == 2
    assert [job.url == EuresSource.portal_url for job in result] == [False, False, True, True, True]


def test_discover_reports_all_search_http_failures(monkeypatch):
    async def post(self, url, json=None, **kwargs):
        return httpx.Response(503, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(EuresSource().discover(SourceContext(1, queries=["DevOps", "Cloud"])))
