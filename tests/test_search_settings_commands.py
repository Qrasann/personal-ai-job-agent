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


def test_blacklist_command_shows_adds_deduplicates_and_clears(monkeypatch):
    search = SimpleNamespace(id=9, settings={"exclude_terms": ["casino"]})
    profile = SimpleNamespace(id=3)
    user = SimpleNamespace(id=7)
    update = AsyncMock()

    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=user))
    monkeypatch.setattr(handlers, "_first_search", AsyncMock(return_value=(profile, search)))
    monkeypatch.setattr(handlers.repo, "update_search_settings", update)

    # 1. Show existing list
    show_msg = SimpleNamespace(text="/blacklist", answer=AsyncMock())
    asyncio.run(handlers.blacklist_command(show_msg))
    assert "casino" in show_msg.answer.await_args.args[0]

    # 2. Add new terms
    add_msg = SimpleNamespace(text="/blacklist Evil Corp, Gambling", answer=AsyncMock())
    asyncio.run(handlers.blacklist_command(add_msg))
    assert search.settings["exclude_terms"] == ["casino", "Evil Corp", "Gambling"]
    update.assert_awaited_with(9, {"exclude_terms": ["casino", "Evil Corp", "Gambling"]})

    # 3. Deduplication (case-insensitive)
    dup_msg = SimpleNamespace(text="/blacklist evil corp", answer=AsyncMock())
    asyncio.run(handlers.blacklist_command(dup_msg))
    assert "уже есть" in dup_msg.answer.await_args.args[0]
    assert len(search.settings["exclude_terms"]) == 3

    # 4. Clear
    clear_msg = SimpleNamespace(text="/blacklist clear", answer=AsyncMock())
    asyncio.run(handlers.blacklist_command(clear_msg))
    assert search.settings["exclude_terms"] == []
    assert "очищен" in clear_msg.answer.await_args.args[0].casefold()


def test_blacklist_job_callback_adds_company_and_marks_match_excluded(monkeypatch):
    user = SimpleNamespace(id=7)
    job = SimpleNamespace(id=42, company="Shady LLC", title="DevOps")
    search = SimpleNamespace(id=9, settings={"exclude_terms": ["gambling"]})
    profile = SimpleNamespace(id=3)
    match = SimpleNamespace(id=101, status="notified")

    update_settings = AsyncMock()
    set_status = AsyncMock()

    monkeypatch.setattr(handlers.repo, "get_user_by_chat", AsyncMock(return_value=user))
    monkeypatch.setattr(handlers.repo, "get_job", AsyncMock(return_value=job))
    monkeypatch.setattr(handlers, "_first_search", AsyncMock(return_value=(profile, search)))
    monkeypatch.setattr(handlers.repo, "update_search_settings", update_settings)
    monkeypatch.setattr(handlers.repo, "get_match_for_user_job", AsyncMock(return_value=match))
    monkeypatch.setattr(handlers.repo, "set_match_status", set_status)

    callback = SimpleNamespace(
        data="blacklist_job:42",
        message=SimpleNamespace(
            chat=SimpleNamespace(id=12345),
            edit_reply_markup=AsyncMock(),
        ),
        answer=AsyncMock(),
    )

    asyncio.run(handlers.blacklist_job_callback(callback))

    assert "Shady LLC" in search.settings["exclude_terms"]
    update_settings.assert_awaited_with(9, {"exclude_terms": ["gambling", "Shady LLC"]})
    set_status.assert_awaited_with(101, "excluded")
    assert callback.answer.await_args.kwargs.get("show_alert") is True
    callback.message.edit_reply_markup.assert_awaited_with(reply_markup=None)


def test_blacklist_command_remove_term_and_not_found(monkeypatch):
    search = SimpleNamespace(id=9, settings={"exclude_terms": ["casino", "Evil Corp", "Crypto"]})
    profile = SimpleNamespace(id=3)
    user = SimpleNamespace(id=7)
    update = AsyncMock()

    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=user))
    monkeypatch.setattr(handlers, "_first_search", AsyncMock(return_value=(profile, search)))
    monkeypatch.setattr(handlers.repo, "update_search_settings", update)

    # 1. Validation when no term provided
    empty_rem = SimpleNamespace(text="/blacklist remove", answer=AsyncMock())
    asyncio.run(handlers.blacklist_command(empty_rem))
    assert "Использование" in empty_rem.answer.await_args.args[0]

    # 2. Not found
    missing_msg = SimpleNamespace(text="/blacklist remove NonExistent", answer=AsyncMock())
    asyncio.run(handlers.blacklist_command(missing_msg))
    assert "не найдены" in missing_msg.answer.await_args.args[0]

    # 3. Successful removal (case-insensitive)
    rem_msg = SimpleNamespace(text="/blacklist remove evil corp", answer=AsyncMock())
    asyncio.run(handlers.blacklist_command(rem_msg))
    assert search.settings["exclude_terms"] == ["casino", "Crypto"]
    update.assert_awaited_with(9, {"exclude_terms": ["casino", "Crypto"]})
    assert "Evil Corp" in rem_msg.answer.await_args.args[0]
