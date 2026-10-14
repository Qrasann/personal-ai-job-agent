import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app import services
from app.telegram import handlers


def test_non_owner_cannot_start_manual_hh_reply(monkeypatch):
    monkeypatch.setattr(handlers.settings, "telegram_admin_chat_id", "111")
    monkeypatch.setattr(handlers.repo, "get_user_by_chat", AsyncMock(return_value=SimpleNamespace(id=2)))
    store = AsyncMock()
    monkeypatch.setattr(handlers.repo, "set_state", store)
    message = SimpleNamespace(chat=SimpleNamespace(id=222), answer=AsyncMock())
    callback = SimpleNamespace(data="manual:hh-chat:message", message=message, answer=AsyncMock())

    asyncio.run(handlers.manual(callback))

    store.assert_not_awaited()
    assert callback.answer.await_args.kwargs["show_alert"] is True


def test_non_owner_stale_manual_hh_reply_is_cleared_without_sending(monkeypatch):
    monkeypatch.setattr(handlers.settings, "telegram_admin_chat_id", "111")
    monkeypatch.setattr(handlers, "_user", AsyncMock(return_value=SimpleNamespace(id=2)))
    monkeypatch.setattr(handlers.repo, "get_state", AsyncMock(return_value="hh-chat:message"))
    store = AsyncMock()
    send = AsyncMock()
    monkeypatch.setattr(handlers.repo, "set_state", store)
    monkeypatch.setattr(handlers, "hh_client", SimpleNamespace(send_chat_message=send))
    message = SimpleNamespace(chat=SimpleNamespace(id=222), text="private text", answer=AsyncMock())

    asyncio.run(handlers.generic_text(message, object()))

    send.assert_not_awaited()
    store.assert_awaited_once_with(2, "manual_hh_reply", "")


def test_owner_manual_hh_reply_preserves_explicit_flow(monkeypatch):
    monkeypatch.setattr(handlers.settings, "telegram_admin_chat_id", "111")
    user = SimpleNamespace(id=1)
    monkeypatch.setattr(handlers.repo, "get_user_by_chat", AsyncMock(return_value=user))
    monkeypatch.setattr(handlers, "_user", AsyncMock(return_value=user))
    monkeypatch.setattr(handlers.repo, "get_state", AsyncMock(return_value="hh-chat:message"))
    store, send = AsyncMock(), AsyncMock()
    monkeypatch.setattr(handlers.repo, "set_state", store)
    monkeypatch.setattr(handlers, "hh_client", SimpleNamespace(send_chat_message=send))
    message = SimpleNamespace(chat=SimpleNamespace(id=111), text="approved text", answer=AsyncMock())
    callback = SimpleNamespace(data="manual:hh-chat:message", message=message, answer=AsyncMock())

    async def scenario():
        await handlers.manual(callback)
        await handlers.generic_text(message, object())

    asyncio.run(scenario())

    send.assert_awaited_once_with("hh-chat", "approved text")
    assert store.await_args_list[0].args == (1, "manual_hh_reply", "hh-chat:message")
    assert store.await_args_list[-1].args == (1, "manual_hh_reply", "")


def test_global_hh_applicant_credential_is_not_available_to_other_users(monkeypatch):
    monkeypatch.setattr(services.settings, "telegram_admin_chat_id", "owner-chat")
    monkeypatch.setattr(services.repo, "get_match", AsyncMock(return_value=SimpleNamespace(user_id=2)))
    monkeypatch.setattr(services.repo, "get_user_by_chat", AsyncMock(return_value=SimpleNamespace(id=1)))
    get_job = AsyncMock()
    monkeypatch.setattr(services.repo, "get_job", get_job)

    with pytest.raises(RuntimeError, match="owner"):
        asyncio.run(services.apply_match(object(), 17, 2))

    get_job.assert_not_awaited()


def test_owner_may_reach_normal_application_checks(monkeypatch):
    monkeypatch.setattr(services.settings, "telegram_admin_chat_id", "owner-chat")
    monkeypatch.setattr(services.repo, "get_match", AsyncMock(return_value=SimpleNamespace(user_id=1, job_id=42)))
    monkeypatch.setattr(services.repo, "get_user_by_chat", AsyncMock(return_value=SimpleNamespace(id=1)))
    get_job = AsyncMock(return_value=None)
    monkeypatch.setattr(services.repo, "get_job", get_job)

    with pytest.raises(RuntimeError, match="Вакансия не найдена"):
        asyncio.run(services.apply_match(object(), 17, 1))

    get_job.assert_awaited_once_with(42)


def test_hh_applicant_credential_requires_configured_owner(monkeypatch):
    monkeypatch.setattr(services.settings, "telegram_admin_chat_id", "")
    monkeypatch.setattr(services.repo, "get_match", AsyncMock(return_value=SimpleNamespace(user_id=1)))
    lookup = AsyncMock()
    monkeypatch.setattr(services.repo, "get_user_by_chat", lookup)

    with pytest.raises(RuntimeError, match="owner"):
        asyncio.run(services.apply_match(object(), 17, 1))

    lookup.assert_not_awaited()


def test_hh_chat_polling_log_does_not_include_exception_payload(monkeypatch, caplog):
    secret = "token=private-value"
    monkeypatch.setattr(services.settings, "telegram_admin_chat_id", "owner-chat")
    monkeypatch.setattr(services, "hh_client", SimpleNamespace(
        private_api_available=True,
        chats=AsyncMock(side_effect=RuntimeError(f"https://hh.test/?{secret}")),
    ))
    monkeypatch.setattr(services.repo, "get_user_by_chat", AsyncMock(return_value=SimpleNamespace(id=1)))
    monkeypatch.setattr(services.repo, "get_state", AsyncMock(return_value="false"))
    monkeypatch.setattr(services.repo, "active_profile", AsyncMock(return_value=SimpleNamespace(id=3)))
    monkeypatch.setattr(services.repo, "list_facts", AsyncMock(return_value=[]))

    asyncio.run(services.scan_hh_chats(object()))
    assert "HH chats failed" in caplog.text
    assert secret not in caplog.text
