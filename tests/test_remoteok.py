import asyncio

import httpx

from app.agents.job_signals import analyze_job_signals
from app.database.models import Job
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
    assert jobs[0].remote_scope == "unspecified"
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
