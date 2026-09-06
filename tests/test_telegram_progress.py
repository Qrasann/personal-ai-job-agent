import asyncio
from types import SimpleNamespace

from aiogram.enums import MessageEntityType

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
            "processed": 2,
            "qualified": 1,
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
    assert "HH: найдено 2 · анализ 2/2" in message.progress.edits[0][0]
    assert "⏱ Прошло:" in message.progress.edits[0][0]
    assert "Проход поиска завершён" in message.progress.edits[-1][0]
    assert "hh: 2 (live)" in message.progress.edits[-1][0]
