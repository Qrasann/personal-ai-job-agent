import asyncio
import ast
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

import inspect
from app.telegram import handlers
from app.telegram.handlers import start
from app.telegram.ui import main_reply_keyboard

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


def test_start_and_help_share_main_menu():
    assert "_main_menu_text()" in inspect.getsource(start)
    assert "_main_menu_text()" in inspect.getsource(handlers.help_command)


def test_main_reply_keyboard_is_compact_persistent_command_navigation():
    keyboard = main_reply_keyboard()

    assert keyboard.is_persistent is True
    assert keyboard.resize_keyboard is True
    assert keyboard.one_time_keyboard is not True
    assert [[button.text for button in row] for row in keyboard.keyboard] == [
        ["/scan", "/scanstatus"],
        ["/review", "/stretch"],
        ["/saved", "/jobs"],
        ["/settings", "/help"],
    ]


def test_reply_keyboard_commands_keep_registered_slash_handlers():
    source = inspect.getsource(handlers)
    tree = ast.parse(source)
    registered = {
        command.value
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        for decorator in node.decorator_list
        if (
            isinstance(decorator, ast.Call)
            and isinstance(decorator.func, ast.Attribute)
            and decorator.func.attr == "message"
        )
        for command_filter in decorator.args
        if (
            isinstance(command_filter, ast.Call)
            and isinstance(command_filter.func, ast.Name)
            and command_filter.func.id == "Command"
        )
        for command in command_filter.args
        if isinstance(command, ast.Constant) and isinstance(command.value, str)
    }
    button_commands = {
        button.text.removeprefix("/")
        for row in main_reply_keyboard().keyboard
        for button in row
    }

    assert button_commands <= registered


def test_start_and_help_attach_the_same_persistent_keyboard(monkeypatch):
    user = SimpleNamespace(telegram_chat_id=777, display_name="Owner")
    monkeypatch.setattr(handlers, "_user", AsyncMock(return_value=user))
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=user))
    monkeypatch.setattr(handlers, "bootstrap_user", AsyncMock(return_value=(user, object())))
    message = SimpleNamespace(
        chat=SimpleNamespace(id=777),
        from_user=SimpleNamespace(full_name="Owner"),
        answer=AsyncMock(),
    )

    asyncio.run(handlers.start(message))
    start_markup = message.answer.await_args.kwargs["reply_markup"]
    message.answer.reset_mock()

    asyncio.run(handlers.help_command(message))
    help_markup = message.answer.await_args.kwargs["reply_markup"]

    assert start_markup == main_reply_keyboard()
    assert help_markup == start_markup



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

