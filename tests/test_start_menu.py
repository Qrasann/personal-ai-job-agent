import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

import inspect
from app.telegram import handlers
from app.telegram.handlers import start

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

