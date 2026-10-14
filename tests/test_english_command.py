import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.telegram import handlers


def _message(text: str):
    return SimpleNamespace(text=text, answer=AsyncMock())


def _setup(monkeypatch, *, current="B2"):
    monkeypatch.setattr(
        handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=7)),
    )
    profile = SimpleNamespace(id=3, english_level=current)
    monkeypatch.setattr(
        handlers.repo, "active_profile", AsyncMock(return_value=profile),
    )
    setter = AsyncMock()
    monkeypatch.setattr(handlers.repo, "set_profile_english_level", setter)
    return setter


def test_english_command_shows_and_updates_cefr_level(monkeypatch):
    setter = _setup(monkeypatch)
    show = _message("/english")
    asyncio.run(handlers.english_level(show))
    assert "<b>B2</b>" in show.answer.await_args.args[0]
    setter.assert_not_awaited()

    update = _message("/english b1 +")
    asyncio.run(handlers.english_level(update))
    setter.assert_awaited_once_with(3, "B1+")
    assert "<b>B1+</b>" in update.answer.await_args.args[0]


def test_english_command_rejects_unmapped_wording_and_can_clear(monkeypatch):
    setter = _setup(monkeypatch)
    invalid = _message("/english upper-intermediate")
    asyncio.run(handlers.english_level(invalid))
    setter.assert_not_awaited()
    assert "CEFR" in invalid.answer.await_args.args[0]

    clear = _message("/english unknown")
    asyncio.run(handlers.english_level(clear))
    setter.assert_awaited_once_with(3, "")
    assert "неизвестно" in clear.answer.await_args.args[0]
