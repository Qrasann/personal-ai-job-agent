from app.database import repository as repo


def test_review_decisions_suppress_reposts():
    assert "saved" in repo.REPOST_SUPPRESS_STATUSES
    assert "skipped" in repo.REPOST_SUPPRESS_STATUSES


def test_select_review_matches_keeps_only_notified_and_deduplicates():
    from types import SimpleNamespace

    rows = [
        (SimpleNamespace(id=1, status="notified"), SimpleNamespace(title="DevOps", company="ACME")),
        (SimpleNamespace(id=2, status="saved"), SimpleNamespace(title="Linux Admin", company="Beta")),
        (SimpleNamespace(id=3, status="notified"), SimpleNamespace(title="DevOps", company="ACME")),
        (SimpleNamespace(id=4, status="skipped"), SimpleNamespace(title="SRE", company="Gamma")),
        (SimpleNamespace(id=5, status="notified"), SimpleNamespace(title="Platform Engineer", company="Delta")),
    ]

    result = repo._select_review_matches(rows, limit=10)

    assert [match.id for match, job in result] == [1, 5]


def test_review_keyboard_contains_expected_actions():
    from app.telegram.ui import review_keyboard

    keyboard = review_keyboard(match_id=301, job_id=24)

    buttons = [
        button
        for row in keyboard.inline_keyboard
        for button in row
    ]

    data = {button.callback_data for button in buttons if button.callback_data}

    assert "review_save:301" in data
    assert "review_skip:301" in data
    assert "details:24" in data
    assert "review_next:301" in data


def test_review_command_shows_first_notified_match(monkeypatch):
    import asyncio
    from types import SimpleNamespace
    from app.telegram import handlers

    class Message:
        def __init__(self):
            self.answers = []

        async def answer(self, text, **kwargs):
            self.answers.append((text, kwargs))

    match = SimpleNamespace(id=301, total_score=78)
    job = SimpleNamespace(
        id=24,
        title="DevOps Engineer",
        company="Example",
        salary_from=None,
        salary_to=None,
        salary_currency=None,
        description="",
        city="Москва",
        country="RU",
        work_mode="Удалённо",
    )

    async def fake_require_user(message):
        return SimpleNamespace(id=7)

    async def fake_review_matches(user_id, limit=10):
        assert user_id == 7
        assert limit is None
        return [(match, job)]

    monkeypatch.setattr(handlers, "_require_user", fake_require_user)
    monkeypatch.setattr(handlers.repo, "review_matches", fake_review_matches)

    message = Message()
    asyncio.run(handlers.review(message))

    assert len(message.answers) == 1
    text, kwargs = message.answers[0]
    assert "DevOps Engineer" in text
    assert "78/100" in text
    assert "1 из 1" in text
    assert kwargs["reply_markup"] is not None


def test_review_command_handles_empty_queue(monkeypatch):
    import asyncio
    from types import SimpleNamespace
    from app.telegram import handlers

    class Message:
        def __init__(self):
            self.answers = []

        async def answer(self, text, **kwargs):
            self.answers.append((text, kwargs))

    async def fake_require_user(message):
        return SimpleNamespace(id=7)

    async def fake_review_matches(user_id, limit=10):
        return []

    monkeypatch.setattr(handlers, "_require_user", fake_require_user)
    monkeypatch.setattr(handlers.repo, "review_matches", fake_review_matches)

    message = Message()
    asyncio.run(handlers.review(message))

    assert len(message.answers) == 1
    assert "Очередь разобрана" in message.answers[0][0]


def test_review_save_callback_marks_own_match_saved(monkeypatch):
    import asyncio
    from types import SimpleNamespace
    from app.telegram import handlers

    statuses = []

    class Callback:
        data = "review_save:301"
        message = SimpleNamespace(chat=SimpleNamespace(id=777))

        def __init__(self):
            self.answers = []

        async def answer(self, text, **kwargs):
            self.answers.append((text, kwargs))

    async def fake_user(chat_id):
        return SimpleNamespace(id=7)

    async def fake_match(match_id):
        return SimpleNamespace(id=301, user_id=7)

    async def fake_status(match_id, status):
        statuses.append((match_id, status))

    monkeypatch.setattr(handlers.repo, "get_user_by_chat", fake_user)
    monkeypatch.setattr(handlers.repo, "get_match", fake_match)
    monkeypatch.setattr(handlers.repo, "set_match_status", fake_status)
    async def fake_advance(*args):
        return None
    monkeypatch.setattr(handlers, "_advance_review", fake_advance)

    callback = Callback()
    asyncio.run(handlers.review_save_callback(callback))

    assert statuses == [(301, "saved")]
    assert callback.answers[0][0] == "⭐ Сохранено"


def test_review_save_callback_rejects_foreign_match(monkeypatch):
    import asyncio
    from types import SimpleNamespace
    from app.telegram import handlers

    statuses = []

    class Callback:
        data = "review_save:301"
        message = SimpleNamespace(chat=SimpleNamespace(id=777))

        def __init__(self):
            self.answers = []

        async def answer(self, text, **kwargs):
            self.answers.append((text, kwargs))

    async def fake_user(chat_id):
        return SimpleNamespace(id=7)

    async def fake_match(match_id):
        return SimpleNamespace(id=301, user_id=99)

    async def fake_status(match_id, status):
        statuses.append((match_id, status))

    monkeypatch.setattr(handlers.repo, "get_user_by_chat", fake_user)
    monkeypatch.setattr(handlers.repo, "get_match", fake_match)
    monkeypatch.setattr(handlers.repo, "set_match_status", fake_status)

    callback = Callback()
    asyncio.run(handlers.review_save_callback(callback))

    assert statuses == []
    assert callback.answers[0][1]["show_alert"] is True


def test_review_skip_callback_marks_own_match_skipped(monkeypatch):
    import asyncio
    from types import SimpleNamespace
    from app.telegram import handlers

    statuses = []

    class Callback:
        data = "review_skip:301"
        message = SimpleNamespace(chat=SimpleNamespace(id=777))

        def __init__(self):
            self.answers = []

        async def answer(self, text, **kwargs):
            self.answers.append((text, kwargs))

    async def fake_user(chat_id):
        return SimpleNamespace(id=7)

    async def fake_match(match_id):
        return SimpleNamespace(id=301, user_id=7)

    async def fake_status(match_id, status):
        statuses.append((match_id, status))

    monkeypatch.setattr(handlers.repo, "get_user_by_chat", fake_user)
    monkeypatch.setattr(handlers.repo, "get_match", fake_match)
    monkeypatch.setattr(handlers.repo, "set_match_status", fake_status)
    async def fake_advance(*args):
        return None
    monkeypatch.setattr(handlers, "_advance_review", fake_advance)

    callback = Callback()
    asyncio.run(handlers.review_skip_callback(callback))

    assert statuses == [(301, "skipped")]
    assert callback.answers[0][0] == "❌ Пропущено"


def test_review_next_callback_exists():
    from app.telegram import handlers
    assert callable(handlers.review_next_callback)


def test_pick_next_review_skips_current():
    from types import SimpleNamespace
    from app.telegram.handlers import _pick_next_review
    a = (SimpleNamespace(id=301), SimpleNamespace(id=24))
    b = (SimpleNamespace(id=302), SimpleNamespace(id=25))
    assert _pick_next_review([a, b], 301) == (1, b)


def test_pick_next_review_uses_first_when_current_removed():
    from types import SimpleNamespace
    from app.telegram.handlers import _pick_next_review
    b = (SimpleNamespace(id=302), SimpleNamespace(id=25))
    assert _pick_next_review([b], 301) == (0, b)


def test_review_next_callback_edits_to_next_match(monkeypatch):
    import asyncio
    from types import SimpleNamespace
    from unittest.mock import AsyncMock
    from app.telegram import handlers
    cur = SimpleNamespace(id=301, user_id=7, total_score=90)
    nxt = SimpleNamespace(id=302, user_id=7, total_score=82)
    job1 = SimpleNamespace(id=24, title="DevOps Engineer", company="ACME")
    job2 = SimpleNamespace(id=25, title="Linux Engineer", company="Beta")
    message = SimpleNamespace(chat=SimpleNamespace(id=777), edit_text=AsyncMock())
    callback = SimpleNamespace(data="review_next:301", message=message, answer=AsyncMock())
    monkeypatch.setattr(handlers.repo, "get_user_by_chat", AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers.repo, "get_match", AsyncMock(return_value=cur))
    monkeypatch.setattr(handlers.repo, "review_matches", AsyncMock(return_value=[(cur, job1), (nxt, job2)]))
    asyncio.run(handlers.review_next_callback(callback))
    handlers.repo.review_matches.assert_awaited_once_with(7, None)
    text = message.edit_text.await_args.args[0]
    assert "Linux Engineer" in text
    assert "82/100" in text
    assert "2 из 2" in text


def test_pick_next_review_returns_none_for_last_item():
    from types import SimpleNamespace
    from app.telegram.handlers import _pick_next_review
    a = (SimpleNamespace(id=301), SimpleNamespace(id=24))
    assert _pick_next_review([a], 301) is None


def test_review_save_callback_shows_next_match(monkeypatch):
    import asyncio
    from types import SimpleNamespace
    from unittest.mock import AsyncMock
    from app.telegram import handlers
    cur = SimpleNamespace(id=301, user_id=7)
    nxt = SimpleNamespace(id=302, user_id=7, total_score=82)
    job = SimpleNamespace(id=25, title="Linux Engineer", company="Beta")
    message = SimpleNamespace(chat=SimpleNamespace(id=777), edit_text=AsyncMock())
    callback = SimpleNamespace(data="review_save:301", message=message, answer=AsyncMock())
    monkeypatch.setattr(handlers.repo, "get_user_by_chat", AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers.repo, "get_match", AsyncMock(return_value=cur))
    monkeypatch.setattr(handlers.repo, "set_match_status", AsyncMock())
    monkeypatch.setattr(handlers.repo, "review_matches", AsyncMock(return_value=[(nxt, job)]))
    asyncio.run(handlers.review_save_callback(callback))
    text = message.edit_text.await_args.args[0]
    assert "Linux Engineer" in text
    assert "82/100" in text
    assert "1 из 1" in text




def test_review_skip_callback_shows_next_match(monkeypatch):
    import asyncio
    from types import SimpleNamespace
    from unittest.mock import AsyncMock
    from app.telegram import handlers
    cur = SimpleNamespace(id=301, user_id=7)
    nxt = SimpleNamespace(id=302, user_id=7, total_score=82)
    job = SimpleNamespace(id=25, title="Linux Engineer", company="Beta")
    message = SimpleNamespace(chat=SimpleNamespace(id=777), edit_text=AsyncMock())
    callback = SimpleNamespace(data="review_skip:301", message=message, answer=AsyncMock())
    monkeypatch.setattr(handlers.repo, "get_user_by_chat", AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers.repo, "get_match", AsyncMock(return_value=cur))
    monkeypatch.setattr(handlers.repo, "set_match_status", AsyncMock())
    monkeypatch.setattr(handlers.repo, "review_matches", AsyncMock(return_value=[(nxt, job)]))
    asyncio.run(handlers.review_skip_callback(callback))
    text = message.edit_text.await_args.args[0]
    assert "Linux Engineer" in text
    assert "82/100" in text
    assert "1 из 1" in text


def test_advance_review_finishes_empty_queue(monkeypatch):
    import asyncio
    from types import SimpleNamespace
    from unittest.mock import AsyncMock
    from app.telegram import handlers
    message = SimpleNamespace(edit_text=AsyncMock())
    callback = SimpleNamespace(message=message)
    monkeypatch.setattr(handlers.repo, "review_matches", AsyncMock(return_value=[]))
    asyncio.run(handlers._advance_review(callback, 7, 301))
    handlers.repo.review_matches.assert_awaited_once_with(7, None)
    text = message.edit_text.await_args.args[0]
    assert "Очередь разобрана" in text


def test_review_card_labels_full_backlog():
    from types import SimpleNamespace
    from app.telegram.handlers import _render_review_card
    match = SimpleNamespace(total_score=80)
    job = SimpleNamespace(title="DevOps", company="ACME")
    text = _render_review_card(match, job, 2, 10)
    assert "2 из 10" in text
    assert "текущей пачке" not in text

def test_select_review_matches_can_return_full_backlog():
    from types import SimpleNamespace
    rows = [
        (SimpleNamespace(id=i, status="notified"), SimpleNamespace(title=f"Role {i}", company="ACME"))
        for i in range(1, 13)
    ]
    result = repo._select_review_matches(rows, limit=None)
    assert [match.id for match, job in result] == list(range(1, 13))


def test_select_saved_matches_keeps_only_saved_and_deduplicates():
    from types import SimpleNamespace
    rows = [
        (SimpleNamespace(id=1, status="notified"), SimpleNamespace(title="DevOps", company="ACME")),
        (SimpleNamespace(id=2, status="saved"), SimpleNamespace(title="Linux Admin", company="Beta")),
        (SimpleNamespace(id=3, status="saved"), SimpleNamespace(title="Linux Admin", company="Beta")),
        (SimpleNamespace(id=4, status="skipped"), SimpleNamespace(title="SRE", company="Gamma")),
        (SimpleNamespace(id=5, status="saved"), SimpleNamespace(title="Platform Engineer", company="Delta")),
    ]
    result = repo._select_saved_matches(rows, limit=None)
    assert [match.id for match, job in result] == [2, 5]
