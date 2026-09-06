import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.telegram import handlers
from app.telegram.ui import review_keyboard, saved_keyboard, stretch_keyboard


def _callbacks(keyboard):
    return [
        button.callback_data
        for row in keyboard.inline_keyboard
        for button in row
        if button.callback_data
    ]


def test_review_queues_have_back_and_next_buttons():
    assert "review_prev:301" in _callbacks(review_keyboard(301, 24))
    assert "review_next:301" in _callbacks(review_keyboard(301, 24))
    assert "stretch_prev:301" in _callbacks(stretch_keyboard(301, 24))
    assert "stretch_next:301" in _callbacks(stretch_keyboard(301, 24))
    assert "saved_prev:301" in _callbacks(saved_keyboard(301, 24))
    assert "saved_next:301" in _callbacks(saved_keyboard(301, 24))


def test_pick_previous_review_moves_back_and_stops_at_first():
    first = (SimpleNamespace(id=301), SimpleNamespace(id=24))
    second = (SimpleNamespace(id=302), SimpleNamespace(id=25))
    assert handlers._pick_previous_review([first, second], 302) == (0, first)
    assert handlers._pick_previous_review([first, second], 301) is None

@pytest.mark.parametrize(
    ("prefix", "queue_name", "callback_name", "expected_header"),
    [
        ("review", "review_matches", "review_prev_callback", "Разбор вакансий"),
        ("stretch", "stretch_matches", "stretch_prev_callback", "Stretch-вакансии"),
        ("saved", "saved_matches", "saved_prev_callback", "Сохранённые вакансии"),
    ],
)
def test_previous_callback_edits_to_previous_match(
    monkeypatch, prefix, queue_name, callback_name, expected_header
):
    previous = SimpleNamespace(id=301, user_id=7, total_score=88)
    current = SimpleNamespace(id=302, user_id=7, total_score=81)
    job1 = SimpleNamespace(id=24, title="First Engineer", company="ACME")
    job2 = SimpleNamespace(id=25, title="Second Engineer", company="Beta")
    message = SimpleNamespace(chat=SimpleNamespace(id=777), edit_text=AsyncMock())
    callback = SimpleNamespace(
        data=f"{prefix}_prev:302",
        message=message,
        answer=AsyncMock(),
    )

    monkeypatch.setattr(
        handlers.repo,
        "get_user_by_chat",
        AsyncMock(return_value=SimpleNamespace(id=7)),
    )
    monkeypatch.setattr(handlers.repo, "get_match", AsyncMock(return_value=current))
    queue = AsyncMock(return_value=[(previous, job1), (current, job2)])
    monkeypatch.setattr(handlers.repo, queue_name, queue)

    asyncio.run(getattr(handlers, callback_name)(callback))

    queue.assert_awaited_once_with(7, None)
    text = message.edit_text.await_args.args[0]
    assert expected_header in text
    assert "First Engineer" in text
    assert "88/100" in text
    assert "1 из 2" in text
    assert message.edit_text.await_args.kwargs["reply_markup"] is not None

