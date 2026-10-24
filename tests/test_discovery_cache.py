import asyncio
import json
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app import services


def test_georgia_sources_use_a_long_scheduled_cache():
    assert services._cache_ttl("jobs_ge") == 6 * 60 * 60
    assert services._cache_ttl("hr_ge") == 6 * 60 * 60


def test_himalayas_uses_the_provider_daily_refresh_window():
    assert services._cache_ttl("himalayas") == 24 * 60 * 60


def test_curated_lever_board_uses_six_hour_cache():
    assert services._cache_ttl("lever") == 6 * 60 * 60


def test_remotive_uses_the_provider_daily_refresh_window():
    assert services._cache_ttl("remotive") == 24 * 60 * 60


def test_remotive_payload_is_shared_across_profiles_and_persisted_across_restarts(monkeypatch):
    from app.sources.adapters.remotive import RemotiveSource
    from app.sources.base import SourceContext

    calls = []
    persisted = {}
    # Ignore fresh caches populated by both former, unfiltered API queries.
    legacy_cache = json.dumps(
        {"fetched_at": datetime.now(UTC).isoformat(), "payload": {"jobs": []}}
    )
    persisted[(812, "source_cache.remotive")] = legacy_cache
    persisted[(812, "source_cache.remotive.v2")] = legacy_cache
    payload = {
        "jobs": [
            {
                "id": 101,
                "title": "DevOps Engineer",
                "company_name": "Example",
                "category": "Devops",
                "candidate_required_location": "Worldwide",
                "url": "https://remotive.com/remote/jobs/devops/101",
                "description": "Linux and Terraform",
            },
            {
                "id": 102,
                "title": "Linux Administrator",
                "company_name": "Example",
                "category": "Devops",
                "candidate_required_location": "Georgia",
                "url": "https://remotive.com/remote/jobs/devops/102",
                "description": "Linux administration",
            },
        ]
    }

    async def fetch(self):
        calls.append(1)
        return payload

    async def get_state(user_id, key, default=""):
        return persisted.get((user_id, key), default)

    async def set_state(user_id, key, value):
        persisted[(user_id, key)] = value

    async def list_active_users():
        return [SimpleNamespace(id=812), SimpleNamespace(id=913)]

    monkeypatch.setattr(RemotiveSource, "fetch_payload", fetch)
    monkeypatch.setattr(services.repo, "get_state", get_state)
    monkeypatch.setattr(services.repo, "set_state", set_state)
    monkeypatch.setattr(services.repo, "list_active_users", list_active_users)
    services._REMOTIVE_PAYLOAD_CACHE = None

    async def check():
        career, cache_hit, _ = await services._discover_remotive(
            RemotiveSource(),
            SourceContext(user_id=812, target_countries=["GE"], queries=["DevOps Engineer"]),
        )
        relocation, second_hit, _ = await services._discover_remotive(
            RemotiveSource(),
            SourceContext(user_id=812, target_countries=["GE"], queries=["Linux Administrator"]),
        )
        services._REMOTIVE_PAYLOAD_CACHE = None  # simulate a process restart
        restarted, restart_hit, _ = await services._discover_remotive(
            RemotiveSource(),
            SourceContext(user_id=812, target_countries=["GE"], queries=["DevOps Engineer"]),
        )
        return career, cache_hit, relocation, second_hit, restarted, restart_hit

    career, cache_hit, relocation, second_hit, restarted, restart_hit = asyncio.run(check())

    assert [job.source_job_id for job in career] == ["101"]
    assert [job.source_job_id for job in relocation] == ["102"]
    assert [job.source_job_id for job in restarted] == ["101"]
    assert cache_hit is False
    assert second_hit is True
    assert restart_hit is True
    assert len(calls) == 1
    assert (812, services.REMOTIVE_STATE_KEY) in persisted
    services._REMOTIVE_PAYLOAD_CACHE = None


@pytest.fixture
def remotive_daily_cache(monkeypatch):
    """A persisted feed fetched 23 hours ago, with controllable wall/elapsed time."""
    from app.sources.adapters.remotive import RemotiveSource
    from app.sources.base import SourceContext

    wall = [datetime(2026, 10, 12, 12, tzinfo=UTC)]
    monotonic = [1_000_000.0]
    calls = []
    persisted = {}

    def payload(identifier):
        return {"jobs": [{
            "id": identifier,
            "title": "DevOps Engineer",
            "company_name": "Example",
            "category": "Devops",
            "candidate_required_location": "Worldwide",
            "url": f"https://remotive.com/remote/jobs/devops/{identifier}",
            "description": "Linux and monitoring",
        }]}

    persisted[services.REMOTIVE_STATE_KEY] = json.dumps({
        "fetched_at": (wall[0] - timedelta(hours=23)).isoformat(),
        "payload": payload("old-feed"),
    })

    class ClockDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return wall[0].astimezone(tz) if tz else wall[0].replace(tzinfo=None)

    async def get_state(_user_id, key, default=""):
        return persisted.get(key, default)

    async def set_state(_user_id, key, value):
        persisted[key] = value

    async def fetch(_self):
        calls.append(wall[0])
        return payload("fresh-feed")

    def advance(seconds):
        wall[0] += timedelta(seconds=seconds)
        monotonic[0] += seconds

    monkeypatch.setattr(services, "datetime", ClockDateTime)
    monkeypatch.setattr(services.time, "monotonic", lambda: monotonic[0])
    monkeypatch.setattr(services, "_REMOTIVE_PAYLOAD_CACHE", None)
    monkeypatch.setattr(services, "_REMOTIVE_PAYLOAD_LOCK", asyncio.Lock())
    monkeypatch.setattr(services, "_DISCOVERY_CACHE", {})
    monkeypatch.setattr(services.repo, "get_state", get_state)
    monkeypatch.setattr(services.repo, "set_state", set_state)
    monkeypatch.setattr(services.repo, "list_active_users", AsyncMock(return_value=[SimpleNamespace(id=7)]))
    monkeypatch.setattr(RemotiveSource, "fetch_payload", fetch)
    return SimpleNamespace(
        adapter=RemotiveSource(),
        context=SourceContext(user_id=7, target_countries=["GE"], queries=["DevOps Engineer"]),
        advance=advance,
        calls=calls,
    )


@pytest.mark.parametrize("restart", [False, True])
def test_aged_remotive_payload_expires_at_its_original_deadline(remotive_daily_cache, restart):
    cache = remotive_daily_cache

    async def check():
        jobs, cached, _ = await services._discover_remotive(cache.adapter, cache.context)
        assert cached and [job.source_job_id for job in jobs] == ["old-feed"]
        cache.advance(3599)
        if restart:
            services._REMOTIVE_PAYLOAD_CACHE = None
        jobs, cached, _ = await services._discover_remotive(cache.adapter, cache.context)
        assert cached and [job.source_job_id for job in jobs] == ["old-feed"]
        assert cache.calls == []
        cache.advance(1)
        jobs, cached, _ = await services._discover_remotive(cache.adapter, cache.context)
        assert not cached and [job.source_job_id for job in jobs] == ["fresh-feed"]
        _, cached, _ = await services._discover_remotive(cache.adapter, cache.context)
        assert cached

    asyncio.run(check())

    assert len(cache.calls) == 1


def test_remotive_manual_scan_keeps_original_expiry_in_context_cache(monkeypatch, remotive_daily_cache):
    cache = remotive_daily_cache
    targets = ["GE"]
    ingested = []

    async def fake_context(_user_id):
        user = SimpleNamespace(id=7, current_country="RU", telegram_chat_id="123")
        profile = SimpleNamespace(target_role="DevOps Engineer")
        search = SimpleNamespace(id=11, name="Career-first", settings={
            "queries": ["DevOps Engineer"],
            "target_countries": list(targets),
            "modes": {"remote_international": True},
        })
        return user, profile, [search]

    async def ingest(_bot, job, **_kwargs):
        ingested.append(job.source_job_id)
        return {}

    monkeypatch.setattr(services, "_user_context", fake_context)
    monkeypatch.setattr(services, "build_source_plan", lambda *a, **k: [
        SimpleNamespace(source_id="remotive", implemented=True)
    ])
    monkeypatch.setattr(services, "vacancy_allowed", lambda *a, **k: True)
    monkeypatch.setattr(services, "job_priority", lambda *a, **k: 0)
    monkeypatch.setattr(services, "ingest_and_match", ingest)

    async def check():
        first = await services.scan_for_user(object(), 7, force_refresh=True)
        assert first["sources"]["remotive"]["cache"] is True
        cache.advance(3599)
        second = await services.scan_for_user(object(), 7, force_refresh=True)
        assert second["sources"]["remotive"]["cache"] is True
        targets[:] = ["AM"]
        other_market = await services.scan_for_user(object(), 7, force_refresh=True)
        assert other_market["sources"]["remotive"]["cache"] is True
        assert cache.calls == []
        cache.advance(1)
        # Both contexts used the aged response: neither may extend its expiry.
        targets[:] = ["GE"]
        expired = await services.scan_for_user(object(), 7, force_refresh=True)
        assert expired["sources"]["remotive"]["cache"] is False
        targets[:] = ["AM"]
        refreshed_market = await services.scan_for_user(object(), 7, force_refresh=True)
        assert refreshed_market["sources"]["remotive"]["cache"] is True

    asyncio.run(check())

    assert ingested == ["old-feed", "old-feed", "old-feed", "fresh-feed", "fresh-feed"]
    assert len(cache.calls) == 1


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


def test_himalayas_manual_refresh_respects_daily_cache_and_market_scope(monkeypatch):
    calls = []
    target = ["GE"]

    class FakeHimalayasSource:
        source_id = "himalayas"
        name = "Himalayas"

        async def discover(self, context):
            calls.append(list(context.target_countries or []))
            return []

    async def fake_context(user_id):
        user = SimpleNamespace(id=7, current_country="RU", telegram_chat_id="123")
        profile = SimpleNamespace(target_role="DevOps")
        search = SimpleNamespace(
            id=1,
            name="Career-first",
            settings={
                "queries": ["DevOps Engineer"],
                "target_countries": list(target),
                "modes": {"remote_international": True},
            },
        )
        return user, profile, [search]

    monkeypatch.setattr(services, "_user_context", fake_context)
    monkeypatch.setattr(services.repo, "get_state", AsyncMock(return_value="false"))
    monkeypatch.setattr(services, "build_source_plan", lambda *a, **k: [SimpleNamespace(source_id="himalayas", implemented=True)])
    monkeypatch.setattr(services, "HimalayasSource", FakeHimalayasSource)
    services._DISCOVERY_CACHE.clear()

    asyncio.run(services.scan_for_user(object(), 7, force_refresh=True))
    target[:] = ["AM"]
    asyncio.run(services.scan_for_user(object(), 7, force_refresh=True))
    asyncio.run(services.scan_for_user(object(), 7, force_refresh=True))

    assert calls == [["GE"], ["AM"]]
    services._DISCOVERY_CACHE.clear()


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

    assert contexts == [["SRE"], ["SRE", "warehouse"]]
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
    monkeypatch.setattr(services.repo, "set_state", AsyncMock())
    monkeypatch.setattr(services, "build_source_plan", lambda *a, **k: [SimpleNamespace(source_id="jobbank", implemented=True)])
    monkeypatch.setattr(services, "JobBankSource", FakeJobBank)
    monkeypatch.setattr(services, "vacancy_allowed", lambda *a, **k: True)
    monkeypatch.setattr(services, "job_priority", lambda *a, **k: 0)
    monkeypatch.setattr(services, "ingest_and_match", ingest)
    services._DISCOVERY_CACHE.clear()
    summary = asyncio.run(services.scan_for_user(object(), 7, force_refresh=True))
    assert contexts == [["SRE", "warehouse worker"]]
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
