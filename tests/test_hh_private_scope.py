import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app import services
from app.telegram import handlers


def _configure_unread_hh_message(monkeypatch, *, auto_reply=False):
    owner = SimpleNamespace(id=1, telegram_chat_id="111")
    message = {
        "id": "message-123",
        "sender_display_info": {"is_current_participant": False},
        "payload": {"text": "Can you describe your Linux experience?"},
    }
    client = SimpleNamespace(
        private_api_available=True,
        chats=AsyncMock(return_value={"items": [{"id": "chat-42", "unread_message_count": 1}]}),
        chat_messages=AsyncMock(return_value={"display": {"title": "Recruiter"}, "messages": [message]}),
        send_chat_message=AsyncMock(),
    )
    monkeypatch.setattr(services.settings, "telegram_admin_chat_id", "111")
    monkeypatch.setattr(services.settings, "auto_reply", auto_reply)
    monkeypatch.setattr(services.settings, "auto_reply_min_confidence", 0.8)
    monkeypatch.setattr(services, "hh_client", client)
    monkeypatch.setattr(services.repo, "get_user_by_chat", AsyncMock(return_value=owner))
    monkeypatch.setattr(services.repo, "get_state", AsyncMock(return_value="false"))
    monkeypatch.setattr(services.repo, "active_profile", AsyncMock(return_value=SimpleNamespace(id=3)))
    monkeypatch.setattr(services.repo, "list_facts", AsyncMock(return_value=[]))
    monkeypatch.setattr(services.repo, "message_seen", AsyncMock(return_value=False))
    mark_seen = AsyncMock()
    set_state = AsyncMock()
    notify = AsyncMock()
    monkeypatch.setattr(services.repo, "mark_message_seen", mark_seen)
    monkeypatch.setattr(services.repo, "set_state", set_state)
    monkeypatch.setattr(services, "notify_chat", notify)
    return client, mark_seen, set_state, notify


def test_hh_reply_generation_error_notifies_owner_for_manual_response(monkeypatch, caplog):
    client, mark_seen, set_state, notify = _configure_unread_hh_message(monkeypatch)
    secret = "private-model-payload"

    def failed_draft(*args):
        raise RuntimeError(secret)

    monkeypatch.setattr(services, "recruiter_reply", failed_draft)

    asyncio.run(services.scan_hh_chats(object()))

    mark_seen.assert_awaited_once()
    set_state.assert_awaited_once_with(1, "draft:chat-42:message-123", "")
    client.send_chat_message.assert_not_awaited()
    assert "Нужен ручной ответ" in notify.await_args.args[2]
    assert "ответь вручную" in notify.await_args.args[2]
    assert secret not in caplog.text


def test_hh_auto_reply_transport_error_notifies_owner_for_manual_response(monkeypatch, caplog):
    client, mark_seen, set_state, notify = _configure_unread_hh_message(monkeypatch, auto_reply=True)
    secret = "private-transport-payload"
    client.send_chat_message.side_effect = RuntimeError(secret)
    monkeypatch.setattr(
        services,
        "recruiter_reply",
        lambda *args: ("Grounded reply", 0.99, False, "Based on facts"),
    )

    asyncio.run(services.scan_hh_chats(object()))

    client.send_chat_message.assert_awaited_once_with("chat-42", "Grounded reply")
    assert "Автоответ не отправлен" in notify.await_args.args[2]
    assert secret not in caplog.text
    assert mark_seen.await_count == 1
    assert set_state.await_args.args == (1, "draft:chat-42:message-123", "Grounded reply")


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


def test_mocked_hh_application_preserves_posting_and_receipt_separately(monkeypatch):
    monkeypatch.setattr(services.settings, "telegram_admin_chat_id", "owner-chat")
    monkeypatch.setattr(services.repo, "get_match", AsyncMock(return_value=SimpleNamespace(
        id=17, user_id=1, job_id=42, profile_id=3, resume_id=5,
    )))
    monkeypatch.setattr(services.repo, "get_user_by_chat", AsyncMock(return_value=SimpleNamespace(id=1)))
    monkeypatch.setattr(services.repo, "get_job", AsyncMock(return_value=SimpleNamespace(
        id=42, title="Saved role", company="Saved employer", description="Saved requirements",
    )))
    monkeypatch.setattr(services.repo, "source_ref", AsyncMock(return_value=SimpleNamespace(
        source_job_id="hh-job", url="https://example.invalid/posting",
        raw={
            "relocation_evidence_v1": {"schema": "relocation_evidence_v1", "captured_at": "fixed", "fields": {}},
            "normalized_posting_v1": {
                "schema": "normalized_posting_v1", "title": "HH role", "company": "Saved employer",
                "description": "HH source requirements",
            },
        },
    )))
    monkeypatch.setattr(services.repo, "list_facts", AsyncMock(return_value=[]))
    monkeypatch.setattr(services.repo, "list_resumes", AsyncMock(return_value=[SimpleNamespace(
        id=5, source="hh", external_id="hh-resume", content="Saved resume",
    )]))
    monkeypatch.setattr(services, "make_cover_letter", lambda job, *_: job.description)
    send = AsyncMock(return_value={"negotiation_id": "receipt-1", "external_url": "https://example.invalid/receipt"})
    monkeypatch.setattr(services, "hh_client", SimpleNamespace(private_api_available=True, apply=send))
    save = AsyncMock()
    monkeypatch.setattr(services.repo, "save_application", save)
    monkeypatch.setattr(services.repo, "set_match_status", AsyncMock())

    asyncio.run(services.apply_match(object(), 17, 1))

    send.assert_awaited_once_with("hh-job", "hh-resume", "HH source requirements")
    saved = save.await_args.kwargs
    assert saved["vacancy_snapshot"] == {
        "title": "HH role", "company": "Saved employer",
        "description": "HH source requirements", "source_url": "https://example.invalid/posting",
        "source_id": "hh", "source_job_id": "hh-job",
        "relocation_evidence": {"schema": "relocation_evidence_v1", "captured_at": "fixed", "fields": {}},
    }
    assert saved["external_url"] == "https://example.invalid/receipt"
    assert saved["source_application_id"] == "receipt-1"


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
