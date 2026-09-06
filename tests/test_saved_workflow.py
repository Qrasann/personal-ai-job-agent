from types import SimpleNamespace
from unittest.mock import AsyncMock
import asyncio

from app.telegram import handlers


def test_saved_command_shows_first_saved_match(monkeypatch):
    first = SimpleNamespace(id=401, total_score=88)
    second = SimpleNamespace(id=402, total_score=81)
    job1 = SimpleNamespace(id=31, title="Platform Engineer", company="ACME")
    job2 = SimpleNamespace(id=32, title="Linux Engineer", company="Beta")

    message = SimpleNamespace(answer=AsyncMock())

    monkeypatch.setattr(
        handlers,
        "_require_user",
        AsyncMock(return_value=SimpleNamespace(id=7)),
    )
    monkeypatch.setattr(
        handlers.repo,
        "saved_matches",
        AsyncMock(return_value=[(first, job1), (second, job2)]),
    )

    asyncio.run(handlers.saved(message))

    handlers.repo.saved_matches.assert_awaited_once_with(7, None)
    text = message.answer.await_args.args[0]
    assert "Platform Engineer" in text
    assert "88/100" in text
    assert "1 из 2" in text
    assert message.answer.await_args.kwargs["reply_markup"] is not None


def test_saved_next_callback_shows_next_match(monkeypatch):
    current = SimpleNamespace(id=401, user_id=7, total_score=88)
    next_match = SimpleNamespace(id=402, user_id=7, total_score=81)
    job1 = SimpleNamespace(id=31, title="Platform Engineer", company="ACME")
    job2 = SimpleNamespace(id=32, title="Linux Engineer", company="Beta")

    message = SimpleNamespace(
        chat=SimpleNamespace(id=777),
        edit_text=AsyncMock(),
    )
    callback = SimpleNamespace(
        data="saved_next:401",
        message=message,
        answer=AsyncMock(),
    )

    monkeypatch.setattr(
        handlers.repo,
        "get_user_by_chat",
        AsyncMock(return_value=SimpleNamespace(id=7)),
    )
    monkeypatch.setattr(
        handlers.repo,
        "get_match",
        AsyncMock(return_value=current),
    )
    monkeypatch.setattr(
        handlers.repo,
        "saved_matches",
        AsyncMock(return_value=[(current, job1), (next_match, job2)]),
    )

    asyncio.run(handlers.saved_next_callback(callback))

    handlers.repo.saved_matches.assert_awaited_once_with(7, None)
    text = message.edit_text.await_args.args[0]
    assert "Linux Engineer" in text
    assert "81/100" in text
    assert "2 из 2" in text
    assert message.edit_text.await_args.kwargs["reply_markup"] is not None


def test_saved_command_handles_empty_list(monkeypatch):
    message = SimpleNamespace(answer=AsyncMock())
    monkeypatch.setattr(
        handlers,
        "_require_user",
        AsyncMock(return_value=SimpleNamespace(id=7)),
    )
    monkeypatch.setattr(
        handlers.repo,
        "saved_matches",
        AsyncMock(return_value=[]),
    )
    asyncio.run(handlers.saved(message))
    handlers.repo.saved_matches.assert_awaited_once_with(7, None)
    text = message.answer.await_args.args[0]
    assert "Сохранённых вакансий пока нет" in text


def test_saved_next_callback_handles_last_item(monkeypatch):
    current = SimpleNamespace(id=401, user_id=7, total_score=88)
    job = SimpleNamespace(id=31, title="Platform Engineer", company="ACME")
    message = SimpleNamespace(
        chat=SimpleNamespace(id=777),
        edit_text=AsyncMock(),
    )
    callback = SimpleNamespace(
        data="saved_next:401",
        message=message,
        answer=AsyncMock(),
    )
    monkeypatch.setattr(
        handlers.repo,
        "get_user_by_chat",
        AsyncMock(return_value=SimpleNamespace(id=7)),
    )
    monkeypatch.setattr(
        handlers.repo,
        "get_match",
        AsyncMock(return_value=current),
    )
    monkeypatch.setattr(
        handlers.repo,
        "saved_matches",
        AsyncMock(return_value=[(current, job)]),
    )
    asyncio.run(handlers.saved_next_callback(callback))
    handlers.repo.saved_matches.assert_awaited_once_with(7, None)
    callback.answer.assert_awaited_once_with(
        "Больше сохранённых вакансий нет",
        show_alert=True,
    )
    message.edit_text.assert_not_awaited()


def test_saved_keyboard_has_details_back_and_next():
    from app.telegram.ui import saved_keyboard

    keyboard = saved_keyboard(401, 31)
    callbacks = [
        button.callback_data
        for row in keyboard.inline_keyboard
        for button in row
    ]
    assert callbacks == ["details:31", "saved_prev:401", "saved_next:401"]
