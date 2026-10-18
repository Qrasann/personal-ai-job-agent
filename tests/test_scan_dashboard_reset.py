import asyncio
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.telegram import handlers
from app.services import ScanAlreadyRunning


class Message:
    def __init__(self, text):
        self.text = text
        self.answers = []
        self.edits = []

    async def answer(self, text, **kwargs):
        self.answers.append(text)
        return self

    async def edit_text(self, text, **kwargs):
        self.edits.append(text)


@pytest.mark.asyncio
async def test_busy_scan_does_not_replace_other_process_dashboard(monkeypatch):
    async def busy(*_args, **_kwargs):
        raise ScanAlreadyRunning

    state_write = AsyncMock()
    monkeypatch.setattr(handlers, "_ACTIVE_SCAN_TASKS", {})
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers, "coordinated_scan_for_user", busy)
    monkeypatch.setattr(handlers.repo, "set_state", state_write)
    message = Message("/scan")
    await handlers.scan(message, bot=object())
    state_write.assert_not_awaited()
    assert "другом процессе" in message.edits[-1]


@pytest.mark.parametrize("outcome", ["completed", "cancelled", "failed"])
def test_new_scan_does_not_display_previous_run_results(monkeypatch, outcome):
    stored = json.dumps({
        "status": "completed",
        "started_at": "PREVIOUS START",
        "finished_at": "PREVIOUS FINISH",
        "stage": "Готово",
        "summary": {"sources": {"old_source": {"found": 999, "duration_ms": 5000}}},
    })
    observed = []

    async def get_state(user_id, key, default=""):
        if key == "scheduled_scan_dashboard":
            return "{}"
        assert (user_id, key) == (7, "scan_dashboard")
        return stored

    async def set_state(user_id, key, value):
        nonlocal stored
        assert (user_id, key) == (7, "scan_dashboard")
        stored = value

    async def fake_scan(bot, user_id, progress_callback=None, force_refresh=False, on_start=None):
        await on_start()
        initial = json.loads(stored)
        assert initial["status"] == "running"
        assert initial["started_at"] != "PREVIOUS START"
        assert "finished_at" not in initial
        assert "summary" not in initial
        await progress_callback("⏳ HH: поиск текущего запуска…")
        running = Message("/scanstatus")
        await handlers.scan_status(running)
        observed.extend(running.answers)
        if outcome == "cancelled":
            raise asyncio.CancelledError
        if outcome == "failed":
            raise RuntimeError("current scan failed")
        return {"sources": {"hh": {"found": 2, "duration_ms": 1000}}}

    monkeypatch.setattr(handlers, "_ACTIVE_SCAN_TASKS", {})
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers.repo, "get_state", get_state)
    monkeypatch.setattr(handlers.repo, "set_state", set_state)
    monkeypatch.setattr(handlers, "coordinated_scan_for_user", fake_scan)

    async def scenario():
        await handlers.scan(Message("/scan"), bot=object())
        latest = Message("/scanstatus")
        await handlers.scan_status(latest)
        observed.extend(latest.answers)

    asyncio.run(scenario())

    state = json.loads(stored)
    assert state["status"] == outcome
    assert state["finished_at"] != "PREVIOUS FINISH"
    assert "PREVIOUS" not in "\n".join(observed)
    assert "old_source" not in "\n".join(observed)
    assert "999" not in "\n".join(observed)
    assert "Источники ещё не завершили поиск." in observed[0]
    if outcome == "completed":
        assert "hh: готово · 2 вакансий (1.0 с)" in observed[-1]
    else:
        assert "summary" not in state
    assert handlers._ACTIVE_SCAN_TASKS == {}


def test_progress_merge_keeps_current_run_start_and_summary(monkeypatch):
    stored = json.dumps({
        "status": "running",
        "started_at": "CURRENT START",
        "summary": {"sources": {"hh": {"found": 1}}},
    })

    async def set_state(user_id, key, value):
        nonlocal stored
        stored = value

    monkeypatch.setattr(handlers.repo, "get_state", AsyncMock(side_effect=lambda *a: stored))
    monkeypatch.setattr(handlers.repo, "set_state", set_state)
    asyncio.run(handlers._save_scan_dashboard(7, status="running", stage="Текущий этап"))

    state = json.loads(stored)
    assert state["started_at"] == "CURRENT START"
    assert state["summary"] == {"sources": {"hh": {"found": 1}}}
    assert state["stage"] == "Текущий этап"
