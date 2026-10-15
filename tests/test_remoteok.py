import asyncio

import httpx

from app.agents.job_signals import analyze_job_signals
from app.database.models import Job
from app.domain.relocation_evidence import build_relocation_evidence
from app.sources.adapters.remoteok import RemoteOKSource
from app.sources.base import SourceContext


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
