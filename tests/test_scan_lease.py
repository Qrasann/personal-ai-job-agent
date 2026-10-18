"""Cross-process scan exclusion without touching the personal database."""

import asyncio
import json
import os
from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from app import services
from app.database.db import user_scan_lease
from app.search.source_summary import select_scan_dashboard


@pytest.mark.integration
def test_postgres_scan_lease_is_scoped_to_one_user_and_released():
    url = os.getenv("JOB_AGENT_TEST_DATABASE_URL")
    if not url:
        if os.getenv("CI"):
            pytest.fail("CI requires JOB_AGENT_TEST_DATABASE_URL")
        pytest.skip("isolated PostgreSQL is not configured")

    async def scenario():
        engine = create_async_engine(url, pool_pre_ping=True)
        try:
            async with user_scan_lease(7001, scan_engine=engine) as first:
                assert first
                async with user_scan_lease(7001, scan_engine=engine) as second:
                    assert not second
                async with user_scan_lease(7002, scan_engine=engine) as different_user:
                    assert different_user
            async with user_scan_lease(7001, scan_engine=engine) as released:
                assert released
            try:
                async with user_scan_lease(7001, scan_engine=engine) as acquired:
                    assert acquired
                    raise asyncio.CancelledError
            except asyncio.CancelledError:
                pass
            async with user_scan_lease(7001, scan_engine=engine) as after_cancel:
                assert after_cancel
        finally:
            await engine.dispose()

    asyncio.run(scenario())


@pytest.mark.asyncio
async def test_coordinator_does_not_start_or_journal_a_busy_scan(monkeypatch):
    @asynccontextmanager
    async def busy(_user_id):
        yield False

    async def unexpected(*_args, **_kwargs):
        raise AssertionError("busy scan performed work")

    monkeypatch.setattr(services, "user_scan_lease", busy)
    monkeypatch.setattr(services, "scan_for_user", unexpected)
    with pytest.raises(services.ScanAlreadyRunning):
        await services.coordinated_scan_for_user(object(), 7, on_start=unexpected)


@pytest.mark.asyncio
async def test_scheduled_scan_records_busy_without_running_duplicate(monkeypatch):
    monkeypatch.setattr(services.repo, "list_active_users", AsyncMock(return_value=[SimpleNamespace(id=7)]))
    monkeypatch.setattr(services, "coordinated_scan_for_user", AsyncMock(side_effect=services.ScanAlreadyRunning))
    save = AsyncMock()
    monkeypatch.setattr(services.repo, "set_state", save)
    await services.scan_all(object())
    assert save.await_count == 1
    state = json.loads(save.await_args.args[2])
    assert state["status"] == "skipped"
    assert "summary" not in state


def test_skipped_schedule_does_not_hide_completed_manual_scan():
    manual = {"status": "completed", "started_at": "2026-10-18 10:00", "summary": {"qualified": 2}}
    scheduled = {"status": "skipped", "started_at": "2026-10-18 10:01"}
    assert select_scan_dashboard(manual, scheduled) == manual
