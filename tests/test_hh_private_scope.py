import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app import services


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
