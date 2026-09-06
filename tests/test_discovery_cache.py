import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app import services

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
        search = SimpleNamespace(settings={"queries": ["DevOps"], "modes": {"local_ru": True, "remote_international": False, "relocation": False}})
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
