import asyncio
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.domain.application_reminders import parse_reminder_due
from app.telegram import handlers


def test_reminder_due_requires_explicit_timezone_and_normalizes_to_utc():
    now = datetime(2026, 10, 23, tzinfo=UTC)
    assert parse_reminder_due("2026-11-01T09:00+03:00", now=now) == datetime(2026, 11, 1, 6, 0)
    with pytest.raises(ValueError, match="timezone"):
        parse_reminder_due("2026-11-01T09:00", now=now)
    with pytest.raises(ValueError, match="будущем"):
        parse_reminder_due("2026-10-22T09:00Z", now=now)


def test_application_reminder_command_is_owner_scoped_and_shows_utc(monkeypatch):
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=7)))
    add = AsyncMock(return_value=SimpleNamespace(id=3, due_at=datetime(2026, 11, 1, 6, 0)))
    monkeypatch.setattr(handlers.repo, "add_application_reminder", add)
    message = SimpleNamespace(
        text="/application 42 remind 2026-11-01T09:00+03:00 Check employer reply",
        answer=AsyncMock(),
    )

    asyncio.run(handlers.application_status_command(message))

    add.assert_awaited_once_with(7, 42, datetime(2026, 11, 1, 6, 0), "Check employer reply")
    assert "2026-11-01 06:00 UTC" in message.answer.await_args.args[0]


def test_reminders_escape_notes_and_completion_is_owner_scoped(monkeypatch):
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers.repo, "list_application_reminders", AsyncMock(return_value=[SimpleNamespace(
        id=3, application_id=42, due_at=datetime(2026, 11, 1, 6, 0), note="Check <reply>",
    )]))
    complete = AsyncMock(return_value=True)
    monkeypatch.setattr(handlers.repo, "complete_application_reminder", complete)
    list_message = SimpleNamespace(answer=AsyncMock())
    asyncio.run(handlers.application_reminders_command(list_message))
    assert "Check &lt;reply&gt;" in list_message.answer.await_args.args[0]

    done_message = SimpleNamespace(text="/reminddone 3", answer=AsyncMock())
    asyncio.run(handlers.application_reminder_done_command(done_message))
    complete.assert_awaited_once_with(7, 3)
