import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.telegram import handlers
from app.telegram.ui import jobs_keyboard


def _job(job_id: int, title: str):
    return SimpleNamespace(
        id=job_id,
        title=title,
        company="ACME",
        salary_from=None,
        salary_to=None,
        salary_currency=None,
        description="Linux Docker",
        city="Тверь",
        country="RU",
        work_mode="Удалённо",
    )


def test_jobs_keyboard_links_visible_jobs_to_details():
    rows = [
        (SimpleNamespace(total_score=82), _job(25, "DevOps")),
        (SimpleNamespace(total_score=78), _job(26, "Linux")),
        (SimpleNamespace(total_score=74), _job(27, "Platform")),
    ]
    keyboard = jobs_keyboard(rows)
    callbacks = [
        button.callback_data
        for row in keyboard.inline_keyboard
        for button in row
    ]
    assert callbacks == ["details:25", "details:26", "details:27"]

def test_jobs_command_adds_details_keyboard(monkeypatch):
    rows = [
        (SimpleNamespace(total_score=82), _job(25, "DevOps Engineer")),
        (SimpleNamespace(total_score=78), _job(26, "Linux Engineer")),
    ]
    message = SimpleNamespace(answer=AsyncMock())

    monkeypatch.setattr(
        handlers,
        "_require_user",
        AsyncMock(return_value=SimpleNamespace(id=7)),
    )
    monkeypatch.setattr(
        handlers,
        "_first_search",
        AsyncMock(return_value=(
            SimpleNamespace(id=3),
            SimpleNamespace(settings={"notify_min_score": 65}),
        )),
    )
    latest = AsyncMock(return_value=rows)
    monkeypatch.setattr(handlers.repo, "latest_matches", latest)

    asyncio.run(handlers.jobs(message))

    latest.assert_awaited_once_with(7, 10, min_score=65)
    assert "Последние совпадения" in message.answer.await_args.args[0]
    keyboard = message.answer.await_args.kwargs["reply_markup"]
    callbacks = [
        button.callback_data
        for row in keyboard.inline_keyboard
        for button in row
    ]
    assert callbacks == ["details:25", "details:26"]
