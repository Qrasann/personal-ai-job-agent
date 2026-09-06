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
