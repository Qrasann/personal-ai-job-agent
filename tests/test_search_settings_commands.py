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

def test_domestic_relocation_command_sets_shows_and_clears(monkeypatch):
    search = SimpleNamespace(id=9, settings={"local_city": "Тверь"})
    profile = SimpleNamespace(id=3)
    user = SimpleNamespace(id=7)
    update = AsyncMock()

    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=user))
    monkeypatch.setattr(handlers, "_first_search", AsyncMock(return_value=(profile, search)))
    monkeypatch.setattr(handlers.repo, "update_search_settings", update)

    on_message = SimpleNamespace(text="/domestic_relocation on", answer=AsyncMock())
    asyncio.run(handlers.domestic_relocation(on_message))
    assert search.settings["domestic_relocation"] is True
    update.assert_awaited_with(9, {"local_city": "Тверь", "domestic_relocation": True})

    show_message = SimpleNamespace(text="/domestic_relocation", answer=AsyncMock())
    asyncio.run(handlers.domestic_relocation(show_message))
    assert "ON" in show_message.answer.await_args.args[0]

    off_message = SimpleNamespace(text="/domestic_relocation off", answer=AsyncMock())
    asyncio.run(handlers.domestic_relocation(off_message))
    assert search.settings["domestic_relocation"] is False
    assert "OFF" in off_message.answer.await_args.args[0]


def test_targets_can_configure_only_relocation_profile(monkeypatch):
    user = SimpleNamespace(id=7)
    profile = SimpleNamespace(id=3)
    career = SimpleNamespace(id=9, name="Career-first", kind="career", settings={"notify_min_score": 65})
    relocation = SimpleNamespace(id=10, name="Relocation-first", kind="relocation", settings={"relocation_queries": ["hotel staff"]})
    update = AsyncMock()
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=user))
    monkeypatch.setattr(handlers.repo, "active_profile", AsyncMock(return_value=profile))
    monkeypatch.setattr(handlers.repo, "list_search_profiles", AsyncMock(return_value=[career, relocation]))
    monkeypatch.setattr(handlers.repo, "update_search_settings", update)

    message = SimpleNamespace(text="/targets relocation GE", answer=AsyncMock())
    asyncio.run(handlers.targets(message))

    update.assert_awaited_once_with(10, {"relocation_queries": ["hotel staff"], "target_countries": ["GE"]})
    assert career.settings == {"notify_min_score": 65}
    assert relocation.settings["target_countries"] == ["GE"]
    assert "Relocation-first" in message.answer.await_args.args[0]


def test_targets_without_scope_apply_to_all_active_profiles(monkeypatch):
    user = SimpleNamespace(id=7)
    profile = SimpleNamespace(id=3)
    searches = [
        SimpleNamespace(id=9, name="Career-first", kind="career", settings={}),
        SimpleNamespace(id=10, name="Relocation-first", kind="relocation", settings={}),
    ]
    update = AsyncMock()
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=user))
    monkeypatch.setattr(handlers.repo, "active_profile", AsyncMock(return_value=profile))
    monkeypatch.setattr(handlers.repo, "list_search_profiles", AsyncMock(return_value=searches))
    monkeypatch.setattr(handlers.repo, "update_search_settings", update)

    message = SimpleNamespace(text="/targets GE", answer=AsyncMock())
    asyncio.run(handlers.targets(message))

    assert update.await_count == 2
    assert [call.args[0] for call in update.await_args_list] == [9, 10]
    assert all(item.settings["target_countries"] == ["GE"] for item in searches)


def test_sources_shows_market_sources_for_each_active_profile(monkeypatch):
    user = SimpleNamespace(id=7, current_country="RU")
    profile = SimpleNamespace(id=3)
    searches = [
        SimpleNamespace(name="Career-first", kind="career", settings={"target_countries": []}),
        SimpleNamespace(name="Relocation-first", kind="relocation", settings={"target_countries": ["GE"]}),
    ]
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=user))
    monkeypatch.setattr(handlers.repo, "active_profile", AsyncMock(return_value=profile))
    monkeypatch.setattr(handlers.repo, "list_search_profiles", AsyncMock(return_value=searches))
    message = SimpleNamespace(answer=AsyncMock())

    asyncio.run(handlers.sources(message))

    text = message.answer.await_args.args[0]
    assert "Career-first" in text
    assert "Relocation-first" in text
    assert "JOBS.GE" in text
    assert "временно приостановлен" in text
    assert "HTTP 410 Gone" in text
