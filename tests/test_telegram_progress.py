import asyncio
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

from aiogram.enums import MessageEntityType
import pytest

from app.telegram import handlers
from app.telegram.multicommand import (
    build_child_message,
    parse_multi_commands,
)


class FakeParentMessage:
    def __init__(self, text: str):
        self.text = text
        self.entities = [
            SimpleNamespace(
                type=MessageEntityType.BOT_COMMAND,
                offset=0,
                length=8,
            )
        ]

    def model_copy(self, *, update):
        return SimpleNamespace(**update)


class ProgressMessage:
    def __init__(self):
        self.edits = []

    async def edit_text(self, text, **kwargs):
        self.edits.append((text, kwargs))


class IncomingMessage:
    def __init__(self, text: str):
        self.text = text
        self.answers = []
        self.progress = ProgressMessage()

    async def answer(self, text, **kwargs):
        self.answers.append((text, kwargs))
        return self.progress


def test_parse_multi_commands_keeps_each_command_once():
    text = "/job 24\n/compare 24\n/job 25\n/compare 25"
    assert parse_multi_commands(text) == [
        "/job 24",
        "/compare 24",
        "/job 25",
        "/compare 25",
    ]


def test_build_child_message_replaces_stale_entities():
    child = build_child_message(
        FakeParentMessage("/version\n/compare 24"),
        "/compare 24",
    )

    assert child.text == "/compare 24"
    assert len(child.entities) == 1

    entity = child.entities[0]
    assert entity.type == MessageEntityType.BOT_COMMAND
    assert entity.offset == 0
    assert entity.length == len("/compare")


def test_multi_command_dispatches_each_child_once(monkeypatch):
    calls = []

    async def fake_propagate(event_type, child_message, **kwargs):
        calls.append((event_type, child_message.text))

    monkeypatch.setattr(
        handlers.router,
        "propagate_event",
        fake_propagate,
    )

    message = FakeParentMessage(
        "/job 24\n/compare 24\n/job 25\n/compare 25"
    )

    asyncio.run(
        handlers.multi_command(
            message,
            bot=object(),
        )
    )

    assert calls == [
        ("message", "/job 24"),
        ("message", "/compare 24"),
        ("message", "/job 25"),
        ("message", "/compare 25"),
    ]


def test_compare_command_shows_progress_then_edits_same_message(monkeypatch):
    async def fake_require_user(message):
        return SimpleNamespace(id=7)

    async def fake_comparison(user_id, job_id):
        assert user_id == 7
        assert job_id == 24
        return {"job": SimpleNamespace(id=24)}

    monkeypatch.setattr(
        handlers,
        "_require_user",
        fake_require_user,
    )
    monkeypatch.setattr(
        handlers,
        "get_vacancy_comparison",
        fake_comparison,
    )
    monkeypatch.setattr(
        handlers,
        "render_fact_comparison",
        lambda payload: "FINAL COMPARE",
    )

    message = IncomingMessage("/compare 24")
    asyncio.run(handlers.compare_job(message))

    assert [x[0] for x in message.answers] == [
        "⏳ Сравниваю требования вакансии с Candidate Facts…"
    ]
    assert [x[0] for x in message.progress.edits] == [
        "FINAL COMPARE"
    ]


def test_job_command_shows_progress_then_edits_same_message(monkeypatch):
    async def fake_require_user(message):
        return SimpleNamespace(id=7)

    async def fake_details(user_id, job_id):
        assert user_id == 7
        assert job_id == 24
        return {"job": SimpleNamespace(id=24)}

    monkeypatch.setattr(
        handlers,
        "_require_user",
        fake_require_user,
    )
    monkeypatch.setattr(
        handlers,
        "get_vacancy_details",
        fake_details,
    )
    monkeypatch.setattr(
        handlers,
        "render_job_details",
        lambda payload: "FINAL JOB",
    )
    monkeypatch.setattr(
        handlers,
        "vacancy_details_keyboard",
        lambda job_id: None,
    )

    message = IncomingMessage("/job 24")
    asyncio.run(handlers.job_details(message))

    assert [x[0] for x in message.answers] == [
        "⏳ Загружаю полное описание вакансии…"
    ]
    assert [x[0] for x in message.progress.edits] == [
        "FINAL JOB"
    ]


def test_scan_command_shows_progress_then_edits_same_message(monkeypatch):
    async def fake_require_user(message):
        return SimpleNamespace(id=7)

    async def fake_scan(bot, user_id, progress_callback=None, force_refresh=False):
        assert user_id == 7
        assert force_refresh is True
        assert progress_callback is not None
        await progress_callback("⏳ HH: поиск…")
        await progress_callback("⏳ HH: найдено 2 · анализ 2/2")
        await asyncio.sleep(0)
        return {
            "sources": {
                "hh": {
                    "found": 2,
                    "cache": False,
                }
            },
            "searches": {
                "11": {
                    "name": "Career-first",
                    "processed": 1,
                    "qualified": 1,
                    "stretch": 0,
                },
                "12": {
                    "name": "Relocation-first",
                    "processed": 1,
                    "qualified": 0,
                    "stretch": 1,
                },
            },
            "processed": 2,
            "qualified": 1,
            "stretch": 1,
            "filtered": 0,
            "notified": 1,
            "duplicate": 0,
        }

    monkeypatch.setattr(
        handlers,
        "_require_user",
        fake_require_user,
    )
    monkeypatch.setattr(
        handlers,
        "scan_for_user",
        fake_scan,
    )
    monkeypatch.setattr(handlers.repo, "get_state", AsyncMock(return_value="{}"))
    monkeypatch.setattr(handlers.repo, "set_state", AsyncMock())

    message = IncomingMessage("/scan")
    asyncio.run(
        handlers.scan(
            message,
            bot=object(),
        )
    )

    assert [x[0] for x in message.answers] == [
        "⏳ Ищу вакансии по активным источникам…"
    ]
    assert len(message.progress.edits) == 2
    assert "⏱ Прошло:" in message.progress.edits[0][0]
    assert "Проход поиска завершён" in message.progress.edits[-1][0]
    assert "hh: 2 (live," in message.progress.edits[-1][0]
    assert "Career-first: 1 обработано, 1 Good, 0 Stretch" in message.progress.edits[-1][0]
    assert "Relocation-first: 1 обработано, 0 Good, 1 Stretch" in message.progress.edits[-1][0]
    assert "🟢 Good: 1" in message.progress.edits[-1][0]
    assert "🟡 Stretch: 1" in message.progress.edits[-1][0]
    assert "⚪ Отфильтровано: 0" in message.progress.edits[-1][0]
    assert "📨 Новых уведомлений: 1" in message.progress.edits[-1][0]


def test_scan_status_renders_persisted_source_timing(monkeypatch):
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(
        handlers.repo,
        "get_state",
        AsyncMock(return_value='{"status":"completed","started_at":"2026-10-11 10:00 UTC","finished_at":"2026-10-11 10:01 UTC","stage":"Готово","summary":{"sources":{"jobbank":{"found":2,"duration_ms":12000}}}}'),
    )
    message = IncomingMessage("/scanstatus")

    asyncio.run(handlers.scan_status(message))

    rendered = message.answers[0][0]
    assert "completed" in rendered
    assert "2026-10-11 10:01 UTC" in rendered
    assert "jobbank: 2 вакансий (12.0 с)" in rendered


@pytest.mark.parametrize("skip_reason", ["ConnectError", "connection cooldown"])
def test_scan_and_persisted_status_show_quiet_source_skip(monkeypatch, skip_reason):
    stored = "{}"
    summary = {
        "sources": {
            "hh": {"skipped": skip_reason, "duration_ms": 2000},
            "remoteok": {"found": 0, "cache": False, "duration_ms": 1000},
            "jobbank": {"error": "ReadTimeout", "duration_ms": 3000},
        }
    }

    async def set_state(user_id, key, value):
        nonlocal stored
        assert (user_id, key) == (7, "scan_dashboard")
        stored = value

    monkeypatch.setattr(handlers, "_ACTIVE_SCAN_TASKS", {})
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers, "scan_for_user", AsyncMock(return_value=summary))
    monkeypatch.setattr(handlers.repo, "get_state", AsyncMock(side_effect=lambda *a: stored))
    monkeypatch.setattr(handlers.repo, "set_state", set_state)

    scan_message = IncomingMessage("/scan")
    status_message = IncomingMessage("/scanstatus")

    async def scenario():
        await handlers.scan(scan_message, bot=object())
        await handlers.scan_status(status_message)

    asyncio.run(scenario())

    completed = scan_message.progress.edits[-1][0]
    persisted = status_message.answers[0][0]
    for rendered in (completed, persisted):
        assert "• hh: пропущен" in rendered
        assert "hh: 0" not in rendered
        assert skip_reason not in rendered
        assert "• jobbank: ошибка" in rendered
    assert "remoteok: 0 (live, 1.0 с)" in completed
    assert "remoteok: 0 вакансий (1.0 с)" in persisted
    assert json.loads(stored)["summary"] == summary
    assert len(scan_message.answers) == 1
    assert handlers._ACTIVE_SCAN_TASKS == {}


def test_scan_and_status_keep_successful_count_for_partial_source(monkeypatch):
    summary = {
        "sources": {
            "hh": {"found": 4, "cache": False, "duration_ms": 1000, "partial": True},
            "remoteok": {"found": 2, "cache": True, "duration_ms": 0},
        }
    }
    state = json.dumps({"status": "completed", "summary": summary})
    monkeypatch.setattr(handlers, "_ACTIVE_SCAN_TASKS", {})
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers, "scan_for_user", AsyncMock(return_value=summary))
    monkeypatch.setattr(handlers.repo, "get_state", AsyncMock(return_value=state))
    monkeypatch.setattr(handlers.repo, "set_state", AsyncMock())
    scan_message = IncomingMessage("/scan")
    status_message = IncomingMessage("/scanstatus")

    async def scenario():
        await handlers.scan(scan_message, bot=object())
        await handlers.scan_status(status_message)

    asyncio.run(scenario())

    completed = scan_message.progress.edits[-1][0]
    persisted = status_message.answers[0][0]
    assert "hh: 4 (live, 1.0 с) · частично" in completed
    assert "hh: 4 вакансий (1.0 с) · частично" in persisted
    assert "remoteok: 2 (кэш, 0.0 с)" in completed
    assert "remoteok: 2 вакансий (0.0 с)" in persisted
    for rendered in (completed, persisted):
        assert rendered.count("частично") == 1
        assert "hh: ошибка" not in rendered
        assert "hh: пропущен" not in rendered


def test_cancel_stops_only_the_active_manual_scan(monkeypatch):
    async def scenario():
        monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=7)))
        monkeypatch.setattr(handlers.repo, "set_state", AsyncMock())
        waiting = asyncio.Event()
        task = asyncio.create_task(waiting.wait())
        handlers._ACTIVE_SCAN_TASKS[7] = task
        await asyncio.sleep(0)
        message = IncomingMessage("/cancel")
        await handlers.cancel(message)
        try:
            await task
        except asyncio.CancelledError:
            pass
        assert task.cancelled()
        assert "Останавливаю текущий скан" in message.answers[0][0]
        handlers._ACTIVE_SCAN_TASKS.pop(7, None)

    asyncio.run(scenario())
