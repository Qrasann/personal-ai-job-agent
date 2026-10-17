from __future__ import annotations

import asyncio
import io
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.telegram import handlers
from app.candidates.importer import FactProposal, FactOverlap


def conflict_pending():
    proposal = FactProposal("skills", "Linux Docker Kubernetes", 0.92, "skills")
    return {
        "user_id": 7, "profile_id": 11, "content": "Skills\nLinux Docker Kubernetes", "fingerprint": "conflict-hash",
        "language": "en", "role": "DevOps", "proposals": (proposal,),
        "overlaps": (FactOverlap(proposal, 42, "Linux Docker"),), "choices": {},
        "created_at": time.time(),
    }


def test_pending_resume_previews_are_bounded_per_user(monkeypatch):
    now = 20_000.0
    monkeypatch.setattr(handlers.time, "time", lambda: now)
    pending = {
        f"owner-{index}": {"user_id": 7, "created_at": now - 100 + index, "content": "x" * 100_000}
        for index in range(8)
    }
    pending.update({
        "other-owner": {"user_id": 8, "created_at": now - 50, "content": "y" * 100_000},
        "expired": {"user_id": 9, "created_at": now - handlers._RESUME_IMPORT_TTL_SECONDS - 1, "content": "z" * 100_000},
    })
    monkeypatch.setattr(handlers, "_PENDING_RESUME_IMPORTS", pending)

    handlers._store_pending_resume_import("new-owner", {
        "user_id": 7, "created_at": now, "content": "new preview",
    })

    assert len([item for item in pending.values() if item["user_id"] == 7]) == 8
    assert "owner-0" not in pending
    assert pending["other-owner"]["user_id"] == 8
    assert "expired" not in pending


def test_pending_resume_previews_have_a_global_cap(monkeypatch):
    now = 30_000.0
    monkeypatch.setattr(handlers.time, "time", lambda: now)
    pending = {
        f"owner-{index}": {"user_id": index, "created_at": now - 100 + index}
        for index in range(handlers._MAX_PENDING_RESUME_IMPORTS)
    }
    monkeypatch.setattr(handlers, "_PENDING_RESUME_IMPORTS", pending)

    handlers._store_pending_resume_import("new-owner", {
        "user_id": handlers._MAX_PENDING_RESUME_IMPORTS, "created_at": now,
    })

    assert len(pending) == handlers._MAX_PENDING_RESUME_IMPORTS
    assert "owner-0" not in pending
    assert "new-owner" in pending


@pytest.mark.parametrize("choice", [None, "add", "update", "keep"])
def test_conflict_choice_waits_for_save_and_applies_only_selected_effect(monkeypatch, choice):
    token = "choice-test"
    pending = conflict_pending()
    handlers._PENDING_RESUME_IMPORTS[token] = pending
    monkeypatch.setattr(handlers.repo, "get_user_by_chat", AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers.repo, "list_resumes", AsyncMock(return_value=[]))
    save = AsyncMock(return_value=SimpleNamespace(id=22))
    monkeypatch.setattr(handlers.repo, "add_imported_resume_with_facts", save)
    message = SimpleNamespace(chat=SimpleNamespace(id=777), edit_text=AsyncMock())

    async def scenario():
        if choice:
            callback = SimpleNamespace(data=f"rchoice:{token}:0:{choice}", message=message, answer=AsyncMock())
            await handlers.choose_resume_fact(callback)
        save.assert_not_awaited()
        callback = SimpleNamespace(data=f"rimp:facts:{token}", message=message, answer=AsyncMock())
        await handlers.confirm_resume_import(callback)

    try:
        asyncio.run(scenario())
        save.assert_awaited_once()
        assert len(save.await_args.args[6]) == int(choice == "add")
        replacements = save.await_args.kwargs["replacements"]
        assert len(replacements) == int(choice == "update")
        if replacements:
            assert replacements[0]["existing_id"] == 42
            assert replacements[0]["expected_value"] == "Linux Docker"
        assert token not in handlers._PENDING_RESUME_IMPORTS
    finally:
        handlers._PENDING_RESUME_IMPORTS.pop(token, None)


def test_other_user_cannot_change_import_conflict_choice(monkeypatch):
    token = "foreign-choice"
    pending = conflict_pending()
    handlers._PENDING_RESUME_IMPORTS[token] = pending
    monkeypatch.setattr(handlers.repo, "get_user_by_chat", AsyncMock(return_value=SimpleNamespace(id=8)))
    message = SimpleNamespace(chat=SimpleNamespace(id=888), edit_text=AsyncMock())
    callback = SimpleNamespace(data=f"rchoice:{token}:0:update", message=message, answer=AsyncMock())
    try:
        asyncio.run(handlers.choose_resume_fact(callback))
        assert pending["choices"] == {}
        message.edit_text.assert_not_awaited()
        assert callback.answer.await_args.kwargs["show_alert"] is True
    finally:
        handlers._PENDING_RESUME_IMPORTS.pop(token, None)


@pytest.mark.parametrize("suffix", ["²:update", "99:update", "0:delete"])
def test_invalid_conflict_callbacks_leave_preview_unchanged(monkeypatch, suffix):
    token = "invalid-choice"
    pending = conflict_pending()
    handlers._PENDING_RESUME_IMPORTS[token] = pending
    monkeypatch.setattr(handlers.repo, "get_user_by_chat", AsyncMock(return_value=SimpleNamespace(id=7)))
    message = SimpleNamespace(chat=SimpleNamespace(id=777), edit_text=AsyncMock())
    callback = SimpleNamespace(data=f"rchoice:{token}:{suffix}", message=message, answer=AsyncMock())
    try:
        asyncio.run(handlers.choose_resume_fact(callback))
        assert pending["choices"] == {}
        assert handlers._PENDING_RESUME_IMPORTS[token] is pending
        message.edit_text.assert_not_awaited()
        assert callback.answer.await_args.kwargs["show_alert"] is True
    finally:
        handlers._PENDING_RESUME_IMPORTS.pop(token, None)


def test_choice_cannot_mutate_preview_already_claimed_by_save(monkeypatch):
    token = "claimed-choice"
    pending = conflict_pending()
    handlers._PENDING_RESUME_IMPORTS[token] = pending

    async def lookup(chat_id):
        handlers._PENDING_RESUME_IMPORTS.pop(token, None)
        return SimpleNamespace(id=7)

    monkeypatch.setattr(handlers.repo, "get_user_by_chat", lookup)
    message = SimpleNamespace(chat=SimpleNamespace(id=777), edit_text=AsyncMock())
    callback = SimpleNamespace(data=f"rchoice:{token}:0:update", message=message, answer=AsyncMock())
    asyncio.run(handlers.choose_resume_fact(callback))
    assert pending["choices"] == {}
    message.edit_text.assert_not_awaited()


def test_changed_database_fact_keeps_preview_for_keep_or_reupload(monkeypatch):
    token = "stale-fact"
    pending = conflict_pending()
    pending["choices"] = {0: "update"}
    handlers._PENDING_RESUME_IMPORTS[token] = pending
    monkeypatch.setattr(handlers.repo, "get_user_by_chat", AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers.repo, "list_resumes", AsyncMock(return_value=[]))
    monkeypatch.setattr(handlers.repo, "add_imported_resume_with_facts", AsyncMock(
        side_effect=handlers.repo.FactUpdateConflict("Факт изменился. Выбери KEEP.")))
    message = SimpleNamespace(chat=SimpleNamespace(id=777), edit_text=AsyncMock())
    callback = SimpleNamespace(data=f"rimp:facts:{token}", message=message, answer=AsyncMock())
    try:
        asyncio.run(handlers.confirm_resume_import(callback))
        assert handlers._PENDING_RESUME_IMPORTS[token] is pending
        assert "KEEP" in callback.answer.await_args.args[0]
    finally:
        handlers._PENDING_RESUME_IMPORTS.pop(token, None)


def test_resume_import_requires_confirmation_and_saves_generic_resume_and_facts(monkeypatch):
    user = SimpleNamespace(id=7)
    profile = SimpleNamespace(id=11, target_role="Platform Engineer")
    message = SimpleNamespace(
        document=SimpleNamespace(file_id="file-1", file_size=60, file_name="private-name.txt"),
        chat=SimpleNamespace(id=777),
        answer=AsyncMock(),
    )
    bot = SimpleNamespace(download=AsyncMock(return_value=io.BytesIO(b"Skills\nLinux and Docker\nExperience\nManaged Kubernetes")))
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=user))
    monkeypatch.setattr(handlers.repo, "active_profile", AsyncMock(return_value=profile))
    monkeypatch.setattr(handlers.repo, "list_resumes", AsyncMock(return_value=[]))
    monkeypatch.setattr(handlers.repo, "list_facts", AsyncMock(return_value=[]))
    save_import = AsyncMock(return_value=SimpleNamespace(id=22))
    monkeypatch.setattr(handlers.repo, "add_imported_resume_with_facts", save_import)

    asyncio.run(handlers.import_resume_document(message, bot))

    assert save_import.await_count == 0
    preview = message.answer.await_args
    assert "private-name" not in preview.args[0]
    callback_data = preview.kwargs["reply_markup"].inline_keyboard[1][0].callback_data
    token = callback_data.split(":", 2)[2]
    callback_message = SimpleNamespace(chat=SimpleNamespace(id=777), edit_text=AsyncMock(), edit_reply_markup=AsyncMock())
    callback = SimpleNamespace(data=f"rimp:facts:{token}", message=callback_message, answer=AsyncMock())
    monkeypatch.setattr(handlers.repo, "get_user_by_chat", AsyncMock(return_value=user))

    asyncio.run(handlers.confirm_resume_import(callback))

    save_import.assert_awaited_once()
    args = save_import.await_args.args
    assert args[1] == "Imported resume " + handlers.datetime.now().strftime("%Y-%m-%d")
    assert args[1] != "private-name.txt"
    assert args[4].startswith("Skills")
    assert len(args[6]) == 2
    assert all(fact["section"] for fact in args[6])
    assert token not in handlers._PENDING_RESUME_IMPORTS


def test_resume_import_rejects_oversized_telegram_document_without_download(monkeypatch):
    user = SimpleNamespace(id=7)
    message = SimpleNamespace(
        document=SimpleNamespace(file_id="file-1", file_size=handlers.MAX_DOCUMENT_BYTES + 1, file_name="resume.pdf"),
        answer=AsyncMock(),
    )
    bot = SimpleNamespace(download=AsyncMock())
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=user))

    asyncio.run(handlers.import_resume_document(message, bot))

    bot.download.assert_not_awaited()
    assert "8 МБ" in message.answer.await_args.args[0]


def test_concurrent_resume_confirmations_do_not_write_twice(monkeypatch):
    token = "concurrent-test"
    handlers._PENDING_RESUME_IMPORTS[token] = {
        "user_id": 7, "profile_id": 11, "content": "Skills\nLinux", "fingerprint": "hash",
        "language": "en", "role": "DevOps", "proposals": (), "overlaps": (),
        "created_at": time.time(),
    }
    monkeypatch.setattr(handlers.repo, "get_user_by_chat", AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers.repo, "list_resumes", AsyncMock(return_value=[]))

    async def add_resume(*_args, **_kwargs):
        await asyncio.sleep(0)
        return SimpleNamespace(id=22)

    save = AsyncMock(side_effect=add_resume)
    monkeypatch.setattr(handlers.repo, "add_imported_resume_with_facts", save)

    def callback():
        message = SimpleNamespace(chat=SimpleNamespace(id=777), edit_text=AsyncMock(), edit_reply_markup=AsyncMock())
        return SimpleNamespace(data=f"rimp:resume:{token}", message=message, answer=AsyncMock())

    async def confirm_both():
        await asyncio.gather(handlers.confirm_resume_import(callback()),
                             handlers.confirm_resume_import(callback()))

    try:
        asyncio.run(confirm_both())
    finally:
        handlers._PENDING_RESUME_IMPORTS.pop(token, None)

    save.assert_awaited_once()


@pytest.mark.parametrize("failure_stage", ["lookup", "save"])
def test_failed_atomic_resume_import_can_be_retried(monkeypatch, failure_stage):
    token = "retry-test"
    pending = {
        "user_id": 7, "profile_id": 11, "content": "Skills\nLinux", "fingerprint": "hash",
        "language": "en", "role": "DevOps", "proposals": (), "overlaps": (),
        "created_at": time.time(),
    }
    handlers._PENDING_RESUME_IMPORTS[token] = pending
    monkeypatch.setattr(handlers.repo, "get_user_by_chat", AsyncMock(return_value=SimpleNamespace(id=7)))
    lookup = AsyncMock(return_value=[])
    save = AsyncMock(return_value=SimpleNamespace(id=22))
    (lookup if failure_stage == "lookup" else save).side_effect = RuntimeError("database unavailable")
    monkeypatch.setattr(handlers.repo, "list_resumes", lookup)
    monkeypatch.setattr(handlers.repo, "add_imported_resume_with_facts", save)
    callback_message = SimpleNamespace(chat=SimpleNamespace(id=777), edit_text=AsyncMock(), edit_reply_markup=AsyncMock())
    callback = SimpleNamespace(data=f"rimp:facts:{token}", message=callback_message, answer=AsyncMock())

    try:
        asyncio.run(handlers.confirm_resume_import(callback))
        assert handlers._PENDING_RESUME_IMPORTS[token] is pending
        callback.answer.assert_awaited_once()
        assert callback.answer.await_args.kwargs["show_alert"] is True
    finally:
        handlers._PENDING_RESUME_IMPORTS.pop(token, None)
