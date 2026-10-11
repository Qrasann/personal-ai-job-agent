import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app import services


def test_georgia_sources_use_a_long_scheduled_cache():
    assert services._cache_ttl("jobs_ge") == 6 * 60 * 60
    assert services._cache_ttl("hr_ge") == 6 * 60 * 60


def test_force_refresh_bypasses_discovery_cache(monkeypatch):
    calls = []
    class FakeHHSource:
        source_id = "hh"
        name = "HH"
        def __init__(self, *args): pass
        async def discover(self, context):
            calls.append(1)
            return []

    async def fake_context(user_id):
        user = SimpleNamespace(id=7, current_country="RU")
        profile = SimpleNamespace(target_role="DevOps")
        search = SimpleNamespace(id=1, name="Career-first", settings={"queries": ["DevOps"], "modes": {"local_ru": True, "remote_international": False, "relocation": False}})
        return user, profile, [search]
    monkeypatch.setattr(services, "_user_context", fake_context)
    monkeypatch.setattr(services.repo, "get_state", AsyncMock(return_value="false"))
    monkeypatch.setattr(services, "build_source_plan", lambda *a, **k: [SimpleNamespace(source_id="hh", implemented=True)])
    monkeypatch.setattr(services, "HHSource", FakeHHSource)
    services._DISCOVERY_CACHE.clear()

    asyncio.run(services.scan_for_user(object(), 7))
    asyncio.run(services.scan_for_user(object(), 7))
    asyncio.run(services.scan_for_user(object(), 7, force_refresh=True))

    assert len(calls) == 2


def test_scan_uses_each_search_profile_independently(monkeypatch):
    contexts = []
    matched_searches = []

    class FakeHHSource:
        source_id = "hh"
        name = "HH"
        def __init__(self, *args): pass
        async def discover(self, context):
            contexts.append(list(context.queries))
            return [SimpleNamespace(source="hh", source_job_id=str(len(contexts)), country="RU", city="Tver")]

    async def fake_context(user_id):
        user = SimpleNamespace(id=7, current_country="RU", telegram_chat_id="123")
        profile = SimpleNamespace(target_role="DevOps")
        career = SimpleNamespace(id=11, name="Career-first", settings={"search_strategy": "career_first", "queries": ["SRE"], "modes": {"local_ru": True, "remote_international": False}})
        relocation = SimpleNamespace(id=12, name="Relocation-first", settings={"search_strategy": "relocation_first", "queries": ["SRE"], "relocation_queries": ["warehouse"], "modes": {"local_ru": True, "remote_international": False}})
        return user, profile, [career, relocation]

    async def fake_ingest(bot, job, **kwargs):
        matched_searches.append(kwargs["only_search_profile_id"])
        return {key: 0 for key in ("processed", "qualified", "stretch", "notified", "filtered", "duplicate")}

    monkeypatch.setattr(services, "_user_context", fake_context)
    monkeypatch.setattr(services.repo, "get_state", AsyncMock(return_value="false"))
    monkeypatch.setattr(services, "build_source_plan", lambda *a, **k: [SimpleNamespace(source_id="hh", implemented=True)])
    monkeypatch.setattr(services, "HHSource", FakeHHSource)
    monkeypatch.setattr(services, "vacancy_allowed", lambda *a, **k: True)
    monkeypatch.setattr(services, "job_priority", lambda *a, **k: 0)
    monkeypatch.setattr(services, "ingest_and_match", fake_ingest)
    services._DISCOVERY_CACHE.clear()

    summary = asyncio.run(services.scan_for_user(object(), 7, force_refresh=True))

    assert contexts == [["SRE"], ["warehouse"]]
    assert matched_searches == [11, 12]
    assert set(summary["searches"]) == {"11", "12"}


def test_jobbank_respects_disabled_source_and_independent_profiles(monkeypatch):
    contexts = []
    matched = []

    class FakeJobBank:
        source_id = "jobbank"
        name = "Job Bank Canada"

        async def discover(self, context):
            contexts.append(context.queries)
            return [SimpleNamespace(source="jobbank", source_job_id="1", country="CA")]

    async def fake_context(user_id):
        user = SimpleNamespace(id=7, current_country="RU", telegram_chat_id="123")
        profile = SimpleNamespace(target_role="DevOps")
        searches = [
            SimpleNamespace(id=11, name="Career-first", settings={"search_strategy": "career_first", "queries": ["SRE"], "disabled_sources": ["jobbank"]}),
            SimpleNamespace(id=12, name="Relocation-first", settings={"search_strategy": "relocation_first", "queries": ["SRE"], "relocation_queries": ["warehouse worker"]}),
        ]
        return user, profile, searches

    async def ingest(bot, job, **kwargs):
        matched.append(kwargs["only_search_profile_id"])
        return {}

    monkeypatch.setattr(services, "_user_context", fake_context)
    monkeypatch.setattr(services.repo, "get_state", AsyncMock(return_value="false"))
    monkeypatch.setattr(services, "build_source_plan", lambda *a, **k: [SimpleNamespace(source_id="jobbank", implemented=True)])
    monkeypatch.setattr(services, "JobBankSource", FakeJobBank)
    monkeypatch.setattr(services, "vacancy_allowed", lambda *a, **k: True)
    monkeypatch.setattr(services, "job_priority", lambda *a, **k: 0)
    monkeypatch.setattr(services, "ingest_and_match", ingest)
    services._DISCOVERY_CACHE.clear()
    summary = asyncio.run(services.scan_for_user(object(), 7, force_refresh=True))
    assert contexts == [["warehouse worker"]]
    assert matched == [12]
    assert not summary["searches"]["11"]["sources"]
    assert summary["searches"]["12"]["sources"]["jobbank"]["found"] == 1


def test_scan_discovers_sources_concurrently_with_a_bounded_limit(monkeypatch):
    active = 0
    peak = 0

    class FakeSource:
        def __init__(self, source_id):
            self.source_id = source_id
            self.name = source_id

        async def discover(self, context):
            nonlocal active, peak
            active += 1
            peak = max(peak, active)
            await asyncio.sleep(0.02)
            active -= 1
            return []

    async def fake_context(user_id):
        user = SimpleNamespace(id=7, current_country="RU", telegram_chat_id="123")
        profile = SimpleNamespace(target_role="DevOps")
        search = SimpleNamespace(id=1, name="Career", settings={"queries": ["SRE"], "modes": {"local_ru": True, "remote_international": True, "relocation": True}})
        return user, profile, [search]

    monkeypatch.setattr(services, "_user_context", fake_context)
    monkeypatch.setattr(services.repo, "get_state", AsyncMock(return_value="false"))
    monkeypatch.setattr(services, "build_source_plan", lambda *a, **k: [SimpleNamespace(source_id=name, implemented=True) for name in ("hh", "remoteok", "arbeitnow", "jobbank")])
    monkeypatch.setattr(services, "HHSource", lambda *a: FakeSource("hh"))
    monkeypatch.setattr(services, "RemoteOKSource", lambda: FakeSource("remoteok"))
    monkeypatch.setattr(services, "ArbeitnowSource", lambda: FakeSource("arbeitnow"))
    monkeypatch.setattr(services, "JobBankSource", lambda: FakeSource("jobbank"))
    monkeypatch.setattr(services, "vacancy_allowed", lambda *a, **k: True)
    monkeypatch.setattr(services, "job_priority", lambda *a, **k: 0)
    services._DISCOVERY_CACHE.clear()

    summary = asyncio.run(services.scan_for_user(object(), 7, force_refresh=True))

    assert 1 < peak <= services.DISCOVERY_CONCURRENCY
    assert all("duration_ms" in item for item in summary["sources"].values())
