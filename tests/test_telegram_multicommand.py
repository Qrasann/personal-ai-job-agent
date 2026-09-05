import pytest

from app.telegram.multicommand import (
    MultiCommandError,
    looks_like_multi_command,
    parse_multi_commands,
)


def test_two_commands_are_detected():
    text = "/version\n/facts"

    assert looks_like_multi_command(text) is True
    assert parse_multi_commands(text) == [
        "/version",
        "/facts",
    ]


def test_command_arguments_are_preserved():
    text = "/fact type 8 learning\n/facts"

    assert parse_multi_commands(text) == [
        "/fact type 8 learning",
        "/facts",
    ]


def test_empty_lines_are_ignored():
    text = "/version\n\n/facts\n\n/compare 24"

    assert parse_multi_commands(text) == [
        "/version",
        "/facts",
        "/compare 24",
    ]


def test_single_command_is_not_multi_command():
    assert parse_multi_commands("/fact type 8 learning") is None


def test_semicolon_is_not_a_separator():
    assert parse_multi_commands("/version; /facts") is None


def test_mixed_text_is_rejected():
    text = "/version\nкакой-то текст\n/facts"

    with pytest.raises(MultiCommandError):
        parse_multi_commands(text)


def test_more_than_ten_commands_is_rejected():
    text = "\n".join("/version" for _ in range(11))

    with pytest.raises(MultiCommandError):
        parse_multi_commands(text)
