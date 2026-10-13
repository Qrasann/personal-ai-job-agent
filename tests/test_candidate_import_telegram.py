from __future__ import annotations

import asyncio
import io
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.telegram import handlers


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
    add_resume = AsyncMock(return_value=SimpleNamespace(id=22))
    add_fact = AsyncMock(return_value=SimpleNamespace(id=1))
    monkeypatch.setattr(handlers.repo, "add_resume", add_resume)
    monkeypatch.setattr(handlers.repo, "add_fact", add_fact)

    asyncio.run(handlers.import_resume_document(message, bot))

    assert add_resume.await_count == 0
    assert add_fact.await_count == 0
    preview = message.answer.await_args
    assert "private-name" not in preview.args[0]
    callback_data = preview.kwargs["reply_markup"].inline_keyboard[1][0].callback_data
    token = callback_data.split(":", 2)[2]
    callback_message = SimpleNamespace(chat=SimpleNamespace(id=777), edit_text=AsyncMock(), edit_reply_markup=AsyncMock())
    callback = SimpleNamespace(data=f"rimp:facts:{token}", message=callback_message, answer=AsyncMock())
    monkeypatch.setattr(handlers.repo, "get_user_by_chat", AsyncMock(return_value=user))

    asyncio.run(handlers.confirm_resume_import(callback))

    add_resume.assert_awaited_once()
    args = add_resume.await_args.args
    kwargs = add_resume.await_args.kwargs
    assert args[1] == "Imported resume " + handlers.datetime.now().strftime("%Y-%m-%d")
    assert args[1] != "private-name.txt"
    assert kwargs["source"] == "imported"
    assert kwargs["content"].startswith("Skills")
    assert add_fact.await_count == 2
    assert all(call.kwargs["provenance"] == "resume_import" for call in add_fact.await_args_list)
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
    monkeypatch.setattr(handlers.repo, "add_resume", save)

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
