import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app import services
from app.domain.jobs import NormalizedJob


def configure_scan(monkeypatch, sources, priorities=None):
    async def context(user_id):
        return (
            SimpleNamespace(id=7, current_country="RU", telegram_chat_id="123"),
            SimpleNamespace(target_role="DevOps"),
            [SimpleNamespace(id=11, name="Career-first", settings={
                "queries": ["DevOps"],
                "source_priorities": priorities or {},
            })],
        )

    monkeypatch.setattr(services, "_user_context", context)
    monkeypatch.setattr(services, "_DISCOVERY_CACHE", {})
    monkeypatch.setattr(services.repo, "get_state", AsyncMock(return_value="false"))
    monkeypatch.setattr(services, "build_source_plan", lambda *a, **k: [
        SimpleNamespace(source_id=name, implemented=True) for name in sources
    ])
    for name, factory in sources.items():
        adapter = {"hh": "HHSource", "remoteok": "RemoteOKSource", "arbeitnow": "ArbeitnowSource"}[name]
        monkeypatch.setattr(services, adapter, factory)


def test_source_timeout_and_error_do_not_discard_successful_discovery(monkeypatch):
    cancelled = []
    matched = []

    class Source:
        def __init__(self, name, *args):
            self.source_id = self.name = name

        async def discover(self, context):
            if self.source_id == "remoteok":
                raise RuntimeError("remote feed unavailable")
            if self.source_id == "arbeitnow":
                try:
                    await asyncio.sleep(1)
                except asyncio.CancelledError:
                    cancelled.append(self.source_id)
                    raise
            return [NormalizedJob(source="hh", source_job_id="1", title="DevOps")]

    async def ingest(bot, job, **kwargs):
        matched.append((job.source, kwargs["only_search_profile_id"]))
        return {"processed": 1}

    configure_scan(monkeypatch, {
        "hh": lambda *a: Source("hh"),
        "remoteok": lambda: Source("remoteok"),
        "arbeitnow": lambda: Source("arbeitnow"),
    })
    monkeypatch.setattr(services, "DISCOVERY_TIMEOUT_SECONDS", 0.02)
    monkeypatch.setattr(services, "ingest_and_match", ingest)
    alerts = AsyncMock()
    monkeypatch.setattr(services, "notify_chat", alerts)

    summary = asyncio.run(services.scan_for_user(object(), 7, force_refresh=True))

    assert matched == [("hh", 11)]
    assert cancelled == ["arbeitnow"]
    assert summary["processed"] == 1
    assert summary["sources"]["hh"]["found"] == 1
    assert summary["sources"]["remoteok"]["error"] == "remote feed unavailable"
    assert summary["sources"]["arbeitnow"]["error"] == "TimeoutError"
    assert all("duration_ms" in info for info in summary["sources"].values())
    assert alerts.await_count == 2
    assert set(summary["searches"]["11"]["sources"]) == {"hh", "remoteok", "arbeitnow"}


def test_ingestion_respects_source_priority_when_discovery_finishes_out_of_order(monkeypatch):
    discovered = []
    matched = []

    class Source:
        def __init__(self, name, delay):
            self.source_id = self.name = name
            self.delay = delay

        async def discover(self, context):
            await asyncio.sleep(self.delay)
            discovered.append(self.source_id)
            return [NormalizedJob(source=self.source_id, source_job_id="1", title="DevOps")]

    async def ingest(bot, job, **kwargs):
        matched.append(job.source)
        return {"processed": 1}

    configure_scan(monkeypatch, {
        "hh": lambda *a: Source("hh", 0),
        "remoteok": lambda: Source("remoteok", 0.02),
        "arbeitnow": lambda: Source("arbeitnow", 0.01),
    }, {"hh": 25, "remoteok": 100, "arbeitnow": 50})
    monkeypatch.setattr(services, "ingest_and_match", ingest)

    summary = asyncio.run(services.scan_for_user(object(), 7, force_refresh=True))

    assert discovered == ["hh", "arbeitnow", "remoteok"]
    assert matched == ["remoteok", "arbeitnow", "hh"]
    assert summary["processed"] == 3
