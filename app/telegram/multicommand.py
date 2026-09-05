from __future__ import annotations

from aiogram.enums import MessageEntityType
from aiogram.filters import Filter
from aiogram.types import Message, MessageEntity


MAX_MULTI_COMMANDS = 10


class MultiCommandError(ValueError):
    pass


def _non_empty_lines(text: str | None) -> list[str]:
    return [
        line.strip()
        for line in (text or "").splitlines()
        if line.strip()
    ]


def looks_like_multi_command(text: str | None) -> bool:
    lines = _non_empty_lines(text)
    return sum(line.startswith("/") for line in lines) >= 2


def parse_multi_commands(text: str | None) -> list[str] | None:
    lines = _non_empty_lines(text)

    if sum(line.startswith("/") for line in lines) < 2:
        return None

    if any(not line.startswith("/") for line in lines):
        raise MultiCommandError(
            "В режиме нескольких команд каждая непустая строка должна начинаться с /."
        )

    if len(lines) > MAX_MULTI_COMMANDS:
        raise MultiCommandError(
            f"Максимум {MAX_MULTI_COMMANDS} команд в одном сообщении."
        )

    return lines


def build_child_message(message: Message, command_text: str) -> Message:
    # Keep synthetic Telegram entities consistent with the replaced child text.
    command_token = command_text.split(maxsplit=1)[0]
    entity = MessageEntity(
        type=MessageEntityType.BOT_COMMAND,
        offset=0,
        length=len(command_token),
    )
    return message.model_copy(
        update={
            "text": command_text,
            "entities": [entity],
        }
    )


class MultiCommandFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        return looks_like_multi_command(message.text)
