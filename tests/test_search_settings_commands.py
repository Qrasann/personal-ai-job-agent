import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.telegram import handlers


def test_city_command_sets_shows_and_clears_local_city(monkeypatch):
    search = SimpleNamespace(id=9, settings={"notify_min_score": 65})
    profile = SimpleNamespace(id=3)
    user = SimpleNamespace(id=7)
    update = AsyncMock()

    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=user))
    monkeypatch.setattr(handlers, "_first_search", AsyncMock(return_value=(profile, search)))
    monkeypatch.setattr(handlers.repo, "update_search_settings", update)

    set_message = SimpleNamespace(text="/city Тверь", answer=AsyncMock())
    asyncio.run(handlers.city(set_message))
    assert search.settings["local_city"] == "Тверь"
    update.assert_awaited_with(9, {"notify_min_score": 65, "local_city": "Тверь"})
    assert "Тверь" in set_message.answer.await_args.args[0]

    show_message = SimpleNamespace(text="/city", answer=AsyncMock())
    asyncio.run(handlers.city(show_message))
    assert "Тверь" in show_message.answer.await_args.args[0]

    clear_message = SimpleNamespace(text="/city clear", answer=AsyncMock())
    asyncio.run(handlers.city(clear_message))
    assert "local_city" not in search.settings
    assert "очищен" in clear_message.answer.await_args.args[0].casefold()
