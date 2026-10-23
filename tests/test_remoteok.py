import asyncio

import httpx
import pytest

from app.agents.job_signals import analyze_job_signals
from app.database.models import Job
from app.domain.relocation_evidence import build_relocation_evidence
from app.sources.adapters.remoteok import RemoteOKSource
from app.sources.base import SourceContext


@pytest.mark.parametrize("tags", [42, True, "DevOps", {"DevOps": True}, [None, 1, {"name": "DevOps"}]])
def test_remoteok_malformed_optional_tags_do_not_abort_valid_roles(monkeypatch, tags):
    async def get(self, url, **kwargs):
        return httpx.Response(200, json=[
            {"id": 1, "position": "DevOps Engineer", "tags": tags},
            {"id": 2, "position": "DevOps Engineer", "tags": ["Linux", None]},
        ], request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    jobs = asyncio.run(RemoteOKSource().discover(SourceContext(user_id=1, queries=["DevOps"])))
    assert [job.source_job_id for job in jobs] == ["1", "2"]
    assert jobs[0].skills == []
    assert jobs[1].skills == ["Linux"]


@pytest.mark.parametrize("amount", ["not-a-number", {}, True, -1, 0, 2**31, 2000.5])
def test_remoteok_invalid_salary_stays_unknown_without_losing_role(monkeypatch, amount):
    async def get(self, url, **kwargs):
        return httpx.Response(200, json=[
            {"id": 1, "position": "DevOps", "salary_min": amount, "salary_max": amount},
            {"id": 2, "position": "DevOps", "salary_min": 60000, "salary_max": 90000},
        ], request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    jobs = asyncio.run(RemoteOKSource().discover(SourceContext(user_id=1)))
    assert [job.source_job_id for job in jobs] == ["1", "2"]
    assert jobs[0].salary_from is None and jobs[0].salary_to is None
    assert jobs[0].salary_currency is None
    assert (jobs[1].salary_from, jobs[1].salary_to, jobs[1].salary_currency) == (60000, 90000, "USD")
    assert jobs[1].salary_period is None  # The feed has not confirmed a pay period.


@pytest.mark.parametrize("published", [None, True, {}, "no date", "2026-10-17T12:00:00"])
def test_remoteok_unusable_publication_date_is_unknown_and_neighbor_survives(monkeypatch, published):
    async def get(self, url, **kwargs):
        return httpx.Response(200, json=[
            {"id": 1, "position": "DevOps", "date": published},
            {"id": 2, "position": "DevOps", "date": "2026-10-17T12:00:00+00:00"},
        ], request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    jobs = asyncio.run(RemoteOKSource().discover(SourceContext(user_id=1)))
    assert [job.source_job_id for job in jobs] == ["1", "2"]
    assert jobs[0].published_at is None
    assert jobs[1].published_at == "2026-10-17T12:00:00+00:00"


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
        ("System Administrator", "Systems Administrator", "Network Administrator"),
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


def test_remoteok_matches_standard_sre_abbreviation_for_site_reliability_query(monkeypatch):
    async def get(self, url, **kwargs):
        return httpx.Response(200, json=[
            {"id": 1, "position": "SRE", "tags": []},
            {"id": 2, "position": "Site Reliability Engineer", "tags": []},
            {"id": 3, "position": "Software Engineer", "tags": ["reliability"]},
        ], request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    jobs = asyncio.run(RemoteOKSource().discover(SourceContext(
        user_id=1, queries=["Site Reliability Engineer"]
    )))
    assert [job.source_job_id for job in jobs] == ["1", "2"]


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
