from __future__ import annotations

import asyncio

import httpx

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
