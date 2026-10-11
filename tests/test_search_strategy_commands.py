import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.telegram import settings_handlers
from app.telegram.settings_ui import strategy_keyboard


def _message(text: str):
    return SimpleNamespace(
        text=text,
        chat=SimpleNamespace(id=123),
        answer=AsyncMock(),
    )


def test_relocation_roles_command_saves_deduplicated_queries(monkeypatch):
    user = SimpleNamespace(id=1)
    profile = SimpleNamespace(id=2, target_role="DevOps Engineer")
    search = SimpleNamespace(id=3, settings={"search_strategy": "balanced", "queries": ["DevOps Engineer"]})
    message = _message("/relocationroles warehouse worker, hotel staff, warehouse worker")
    monkeypatch.setattr(settings_handlers, "_user_message", AsyncMock(return_value=user))
    select_search = AsyncMock(return_value=(profile, search))
    monkeypatch.setattr(settings_handlers, "_search_for_kind", select_search)
    save = AsyncMock()
    monkeypatch.setattr(settings_handlers, "_save", save)

    asyncio.run(settings_handlers.relocation_roles_command(message))

    saved = save.await_args.args[1]
    select_search.assert_awaited_once_with(1, "relocation")
    assert saved["relocation_queries"] == ["warehouse worker", "hotel staff"]
    assert "DevOps Engineer, warehouse worker, hotel staff" in message.answer.await_args.args[0]


def test_strategy_callback_persists_only_supported_value(monkeypatch):
    user = SimpleNamespace(id=1)
    search = SimpleNamespace(id=3, settings={})
    callback = SimpleNamespace(
        data="cfg:strategy:relocation_first",
        message=SimpleNamespace(chat=SimpleNamespace(id=123), edit_text=AsyncMock()),
        answer=AsyncMock(),
    )
    monkeypatch.setattr(settings_handlers, "_user_callback", AsyncMock(return_value=user))
    monkeypatch.setattr(settings_handlers, "_first_search", AsyncMock(return_value=(object(), search)))
    save = AsyncMock()
    monkeypatch.setattr(settings_handlers, "_save", save)
    redraw = AsyncMock()
    monkeypatch.setattr(settings_handlers, "strategy_callback", redraw)

    asyncio.run(settings_handlers.strategy_set_callback(callback))

    assert save.await_args.args[1]["search_strategy"] == "relocation_first"
    redraw.assert_awaited_once_with(callback)


def test_strategy_keyboard_marks_current_mode():
    keyboard = strategy_keyboard({"search_strategy": "career_first"})
    labels = [row[0].text for row in keyboard.inline_keyboard[:3]]
    assert labels == ["✅ Career-first", "▫️ Relocation-first", "▫️ Balanced"]


def test_parallel_search_command_enables_independent_profiles(monkeypatch):
    user = SimpleNamespace(id=1)
    profile = SimpleNamespace(id=2)
    searches = [
        SimpleNamespace(name="Career-first", kind="career"),
        SimpleNamespace(name="Relocation-first", kind="relocation"),
    ]
    message = _message("/parallelsearch on")
    monkeypatch.setattr(settings_handlers, "_user_message", AsyncMock(return_value=user))
    monkeypatch.setattr(settings_handlers.repo, "active_profile", AsyncMock(return_value=profile))
    configure = AsyncMock()
    monkeypatch.setattr(settings_handlers.repo, "configure_parallel_search_profiles", configure)
    monkeypatch.setattr(settings_handlers.repo, "list_search_profiles", AsyncMock(return_value=searches))

    asyncio.run(settings_handlers.parallel_search_command(message))

    configure.assert_awaited_once_with(2, enabled=True)
    assert "Параллельный поиск: ON" in message.answer.await_args.args[0]
