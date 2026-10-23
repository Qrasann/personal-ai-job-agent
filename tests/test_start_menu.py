import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardRemove

import inspect
from app import main
from app.telegram import handlers
from app.telegram.handlers import start
from app.telegram.ui import LEGACY_REPLY_KEYBOARD_REMOVED_STATE, main_menu_keyboard

def test_start_message_has_no_unsupported_html_placeholders():
    source = inspect.getsource(start)
    assert "<id>" not in source

def test_main_menu_contains_core_commands():
    text = handlers._main_menu_text()
    commands = (
        "/scan",
        "/review",
        "/stretch",
        "/saved",
        "/jobs",
        "/delivery",
        "/city",
        "/domestic_relocation",
        "/settings",
        "/facts",
        "/sources",
        "/help",
    )
    for command in commands:
        assert command in text


def test_start_and_menu_share_inline_main_menu_entrypoint():
    assert "_send_main_menu" in inspect.getsource(start)
    assert "_send_main_menu" in inspect.getsource(handlers.menu_command)


def test_main_inline_keyboard_has_six_sections_and_search_status():
    keyboard = main_menu_keyboard()

    assert isinstance(keyboard, InlineKeyboardMarkup)
    assert [[button.callback_data for button in row] for row in keyboard.inline_keyboard] == [
        ["menu:vacancies", "menu:relocation"],
        ["menu:applications", "menu:cv"],
        ["menu:profile", "menu:settings"],
        ["menu:search"],
    ]


def test_bot_command_menu_is_current_and_uses_native_menu_button():
    bot = SimpleNamespace(set_my_commands=AsyncMock(), set_chat_menu_button=AsyncMock())

    asyncio.run(main.configure_telegram_ui(bot))

    commands = [item.command for item in bot.set_my_commands.await_args.args[0]]
    assert commands == [
        "menu", "scan", "scanstatus", "review", "stretch", "saved", "jobs",
        "applications", "resumes", "facts", "settings", "help",
    ]
    assert bot.set_chat_menu_button.await_count == 1


def test_start_removes_legacy_keyboard_then_opens_inline_menu_once(monkeypatch):
    user = SimpleNamespace(id=5, telegram_chat_id=777, display_name="Owner")
    monkeypatch.setattr(handlers, "_user", AsyncMock(return_value=user))
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=user))
    monkeypatch.setattr(handlers, "bootstrap_user", AsyncMock(return_value=(user, object())))
    monkeypatch.setattr(handlers.repo, "get_state", AsyncMock(return_value="false"))
    set_state = AsyncMock()
    monkeypatch.setattr(handlers.repo, "set_state", set_state)
    message = SimpleNamespace(
        chat=SimpleNamespace(id=777),
        from_user=SimpleNamespace(full_name="Owner"),
        answer=AsyncMock(),
    )

    asyncio.run(handlers.start(message))
    assert message.answer.await_count == 2
    assert isinstance(message.answer.await_args_list[0].kwargs["reply_markup"], ReplyKeyboardRemove)
    assert message.answer.await_args_list[1].kwargs["reply_markup"] == main_menu_keyboard()
    set_state.assert_awaited_once_with(5, LEGACY_REPLY_KEYBOARD_REMOVED_STATE, "true")


def test_menu_does_not_repeat_keyboard_cleanup_after_migration(monkeypatch):
    user = SimpleNamespace(id=5)
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=user))
    monkeypatch.setattr(handlers.repo, "get_state", AsyncMock(return_value="true"))
    monkeypatch.setattr(handlers.repo, "set_state", AsyncMock())
    message = SimpleNamespace(answer=AsyncMock())

    asyncio.run(handlers.menu_command(message))

    assert message.answer.await_count == 1
    assert message.answer.await_args.kwargs["reply_markup"] == main_menu_keyboard()


@pytest.mark.parametrize("handler", [handlers.scan_status, handlers.jobs, handlers.review])
def test_scan_jobs_review_never_restore_reply_keyboard(handler):
    source = inspect.getsource(handler)
    assert "ReplyKeyboard" not in source
    assert "main_reply_keyboard" not in source


def test_menu_navigation_edits_one_authorized_message(monkeypatch):
    monkeypatch.setattr(handlers.repo, "get_user_by_chat", AsyncMock(return_value=SimpleNamespace(id=5)))
    message = SimpleNamespace(chat=SimpleNamespace(id=777), message_id=10, edit_text=AsyncMock())
    callback = SimpleNamespace(data="menu:cv", message=message, answer=AsyncMock())

    asyncio.run(handlers.main_menu_callback(callback))

    message.edit_text.assert_awaited_once()
    assert "CV Studio" in message.edit_text.await_args.args[0]
    callbacks = [button.callback_data for row in message.edit_text.await_args.kwargs["reply_markup"].inline_keyboard for button in row]
    assert callbacks == ["menu:main", "menu:main"]
    callback.answer.assert_awaited_once_with()


def test_menu_callback_rejects_unknown_user(monkeypatch):
    monkeypatch.setattr(handlers.repo, "get_user_by_chat", AsyncMock(return_value=None))
    message = SimpleNamespace(chat=SimpleNamespace(id=999), message_id=10, edit_text=AsyncMock())
    callback = SimpleNamespace(data="menu:main", message=message, answer=AsyncMock())

    asyncio.run(handlers.main_menu_callback(callback))

    message.edit_text.assert_not_awaited()
    callback.answer.assert_awaited_once_with("Нет доступа", show_alert=True)


def test_startup_removes_legacy_keyboard_once_for_active_users(monkeypatch):
    users = [SimpleNamespace(id=5, telegram_chat_id="777"), SimpleNamespace(id=6, telegram_chat_id="888")]
    monkeypatch.setattr(main.repo, "list_active_users", AsyncMock(return_value=users))
    monkeypatch.setattr(main.repo, "get_state", AsyncMock(side_effect=["false", "true"]))
    set_state = AsyncMock()
    monkeypatch.setattr(main.repo, "set_state", set_state)
    bot = SimpleNamespace(send_message=AsyncMock())

    asyncio.run(main.remove_legacy_reply_keyboards(bot))

    bot.send_message.assert_awaited_once()
    assert bot.send_message.await_args.args[0] == "777"
    assert isinstance(bot.send_message.await_args.kwargs["reply_markup"], ReplyKeyboardRemove)
    set_state.assert_awaited_once_with(5, LEGACY_REPLY_KEYBOARD_REMOVED_STATE, "true")


def test_failed_startup_cleanup_is_retriable(monkeypatch):
    user = SimpleNamespace(id=5, telegram_chat_id="777")
    monkeypatch.setattr(main.repo, "list_active_users", AsyncMock(return_value=[user]))
    monkeypatch.setattr(main.repo, "get_state", AsyncMock(return_value="false"))
    set_state = AsyncMock()
    monkeypatch.setattr(main.repo, "set_state", set_state)
    bot = SimpleNamespace(send_message=AsyncMock(side_effect=RuntimeError("unavailable")))

    asyncio.run(main.remove_legacy_reply_keyboards(bot))

    set_state.assert_not_awaited()



@pytest.mark.parametrize("flag_enabled", [False, True])
def test_status_never_claims_unimplemented_auto_apply_is_active(monkeypatch, flag_enabled):
    monkeypatch.setattr(handlers.settings, "auto_apply", flag_enabled)
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(
        id=7, current_country="RU",
    )))
    monkeypatch.setattr(handlers.repo, "stats", AsyncMock(return_value={
        "matches": 0, "notified": 0, "filtered": 0, "applications": 0,
    }))
    monkeypatch.setattr(handlers.repo, "get_state", AsyncMock(return_value="false"))
    monkeypatch.setattr(handlers.repo, "active_profile", AsyncMock(return_value=SimpleNamespace(
        name="Main", target_role="DevOps", english_level="",
    )))
    message = SimpleNamespace(answer=AsyncMock())

    asyncio.run(handlers.status(message))

    rendered = message.answer.await_args.args[0]
    assert "Автоотклик: не реализован; отправка только вручную" in rendered
    assert ("AUTO_APPLY=true" in rendered) == flag_enabled
    assert "Auto apply: ON" not in rendered

