import asyncio

import httpx
import pytest

from app.agents.job_signals import analyze_job_signals
from app.database.models import Job
from app.domain.relocation_evidence import build_relocation_evidence
from app.sources.adapters.remoteok import RemoteOKSource
from app.sources.base import SourceContext


def test_remoteok_preserves_explicit_location_limit_over_worldwide_boilerplate(monkeypatch):
    async def get(self, url, **kwargs):
        return httpx.Response(200, json=[{
            "id": 1, "position": "DevOps Engineer", "location": "Germany only",
            "description": "Work from anywhere. Join our remote team.",
        }], request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    item = asyncio.run(RemoteOKSource().discover(SourceContext(user_id=1)))[0]
    assert item.remote_scope == "Germany only"
    assert item.country is None
    signals = analyze_job_signals(Job(
        title=item.title, description=item.description,
        work_mode=item.work_mode, remote_scope=item.remote_scope,
    ))
    assert signals.remote_eligibility == "uncertain"
    evidence = build_relocation_evidence(item)["fields"]
    restriction = evidence["citizenship_or_residence_restriction"]
    assert restriction["excerpt"] == "Germany only"
    assert restriction["interpretation"]["scope"] == "unspecified"
    assert evidence["work_country"]["status"] == "unknown"
    assert evidence["existing_work_authorization_required"]["status"] == "unknown"
    assert evidence["visa_sponsorship"]["status"] == "unknown"


@pytest.mark.parametrize(
    ("query", "matching_title", "unrelated_title"),
    [
        ("QA Engineer", "Senior QA Engineer", "Platform Engineer"),
        ("Go Developer", "Go Developer", "Google Cloud Developer"),
        ("HR", "HR Specialist", "Threat Analyst"),
        ("C# Developer", "C# Developer", "C++ Developer"),
        ("C++ Developer", "C++ Developer", "C# Developer"),
        ("Java Developer", "Java Engineer", "JavaScript Developer"),
        ("DevOps Engineer", "DevOps/SRE Engineer", "Software Engineer"),
        ("Linux Administrator", "Linux-System Administrator", "Windows Administrator"),
    ],
)
def test_remoteok_matches_role_tokens_without_dropping_short_terms(
    monkeypatch, query, matching_title, unrelated_title,
):
    async def get(self, url, **kwargs):
        return httpx.Response(200, json=[
            {"id": 1, "position": matching_title, "tags": []},
            # Description mentions must not turn an unrelated role into a match.
            {"id": 2, "position": unrelated_title, "description": query, "tags": []},
        ], request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    jobs = asyncio.run(RemoteOKSource().discover(SourceContext(user_id=1, queries=[query])))
    assert [job.source_job_id for job in jobs] == ["1"]


def test_remoteok_matches_all_specific_query_tokens_across_title_and_tags(monkeypatch):
    async def get(self, url, **kwargs):
        return httpx.Response(200, json=[
            {"id": 1, "position": "QA Engineer", "tags": ["automation"]},
            {"id": 2, "position": "Automation Engineer", "tags": ["manufacturing"]},
            {"id": 3, "position": "Customer Support", "tags": []},
        ], request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    jobs = asyncio.run(RemoteOKSource().discover(
        SourceContext(user_id=1, queries=["QA Automation Engineer", "Customer Support"])
    ))
    assert [job.source_job_id for job in jobs] == ["1", "3"]


def test_remoteok_does_not_turn_unspecified_country_eligibility_into_worldwide(monkeypatch):
    async def get(self, url, **kwargs):
        return httpx.Response(
            200,
            json=[
                {
                    "id": 1,
                    "position": "DevOps Engineer",
                    "company": "Example Corp",
                    "location": "Worldwide",
                    "tags": ["DevOps"],
                    "description": "Remote DevOps role.",
                    "url": "https://remoteok.com/remote-jobs/1",
                }
            ],
            request=httpx.Request("GET", url),
        )

    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    jobs = asyncio.run(
        RemoteOKSource().discover(
            SourceContext(user_id=1, queries=["DevOps Engineer"])
        )
    )

    assert len(jobs) == 1
    assert jobs[0].work_mode == "remote"
    assert jobs[0].country is None
    assert jobs[0].remote_scope == "unspecified"
    country_evidence = build_relocation_evidence(jobs[0])["fields"]["work_country"]
    assert country_evidence["status"] == "unknown"
    assert country_evidence["value"] is None
    assert country_evidence["excerpt"] == "Worldwide"
    signals = analyze_job_signals(
        Job(
            fingerprint="remoteok-1",
            title=jobs[0].title,
            description=jobs[0].description,
            country=jobs[0].country,
            work_mode=jobs[0].work_mode,
            remote_scope=jobs[0].remote_scope,
        )
    )
    assert signals.remote_eligibility == "uncertain"


def test_remoteok_invalid_schema_is_not_reported_as_zero_results(monkeypatch):
    import pytest
    from app.sources.diagnostics import SourceInvalidResponse
    async def get(self,url,**kwargs):
        return httpx.Response(200,json={'error':'private body'},request=httpx.Request('GET',url))
    monkeypatch.setattr(httpx.AsyncClient,'get',get)
    with pytest.raises(SourceInvalidResponse):
        asyncio.run(RemoteOKSource().discover(SourceContext(user_id=1)))


def test_remoteok_connect_timeout_preserves_type_and_phase_budget(monkeypatch):
    import pytest
    async def get(self,url,**kwargs):
        assert self.timeout.connect==30
        assert self.timeout.read==30
        assert self.timeout.pool==30
        raise httpx.ConnectTimeout('private endpoint')
    monkeypatch.setattr(httpx.AsyncClient,'get',get)
    with pytest.raises(httpx.ConnectTimeout):
        asyncio.run(RemoteOKSource().discover(SourceContext(user_id=1)))
