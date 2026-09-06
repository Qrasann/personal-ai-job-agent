import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.candidates import bootstrap


def _config():
    return {
        "candidate": {
            "facts": ["Linux experience", "Docker labs"],
            "hh_resume_id": "hh-123",
        },
        "geography": {
            "current_country": "ru",
            "target_countries": ["ES", "GE"],
            "remote_worldwide": True,
            "remote_regions": ["EMEA"],
            "relocation_enabled": True,
            "relocation_countries": ["ES"],
        },
        "search": {
            "queries": ["DevOps Engineer"],
            "minimum_salary_net_rub": 100000,
        },
    }


def test_bootstrap_creates_missing_candidate_data(monkeypatch):
    created_user = SimpleNamespace(id=1, current_country=None)
    refreshed_user = SimpleNamespace(id=1, current_country="RU")
    profile = SimpleNamespace(id=10)
    search = SimpleNamespace(id=20, settings={})

    monkeypatch.setattr(
        bootstrap.repo,
        "get_user_by_chat",
        AsyncMock(side_effect=[None, refreshed_user]),
    )
    monkeypatch.setattr(bootstrap.repo, "create_user", AsyncMock(return_value=created_user))
    monkeypatch.setattr(bootstrap.repo, "ensure_default_profile", AsyncMock(return_value=profile))
    monkeypatch.setattr(bootstrap.repo, "set_user_country", AsyncMock())
    monkeypatch.setattr(bootstrap.repo, "list_facts", AsyncMock(return_value=[]))
    monkeypatch.setattr(bootstrap.repo, "add_fact", AsyncMock())
    monkeypatch.setattr(bootstrap.repo, "list_search_profiles", AsyncMock(return_value=[search]))
    monkeypatch.setattr(bootstrap.repo, "update_search_settings", AsyncMock())
    monkeypatch.setattr(bootstrap.repo, "list_resumes", AsyncMock(return_value=[]))
    monkeypatch.setattr(bootstrap.repo, "add_resume", AsyncMock())
    monkeypatch.setattr(bootstrap, "load_profile", lambda: _config())

    user, returned_profile = asyncio.run(bootstrap.bootstrap_user(123, "Roma"))

    assert user is refreshed_user
    assert returned_profile is profile
    bootstrap.repo.create_user.assert_awaited_once_with(123, "Roma")
    bootstrap.repo.set_user_country.assert_awaited_once_with(1, "RU")
    assert bootstrap.repo.add_fact.await_count == 2
    assert bootstrap.repo.add_resume.await_count == 3
    bootstrap.repo.update_search_settings.assert_awaited_once()


def test_bootstrap_does_not_duplicate_existing_data(monkeypatch):
    user = SimpleNamespace(id=1, current_country="RU")
    profile = SimpleNamespace(id=10)
    search = SimpleNamespace(id=20, settings={"queries": ["DevOps Engineer"]})

    monkeypatch.setattr(bootstrap.repo, "get_user_by_chat", AsyncMock(return_value=user))
    monkeypatch.setattr(bootstrap.repo, "create_user", AsyncMock())
    monkeypatch.setattr(bootstrap.repo, "ensure_default_profile", AsyncMock(return_value=profile))
    monkeypatch.setattr(bootstrap.repo, "set_user_country", AsyncMock())
    monkeypatch.setattr(bootstrap.repo, "list_facts", AsyncMock(return_value=[object()]))
    monkeypatch.setattr(bootstrap.repo, "add_fact", AsyncMock())
    monkeypatch.setattr(bootstrap.repo, "list_search_profiles", AsyncMock(return_value=[search]))
    monkeypatch.setattr(bootstrap.repo, "update_search_settings", AsyncMock())
    monkeypatch.setattr(bootstrap.repo, "list_resumes", AsyncMock(return_value=[object()]))
    monkeypatch.setattr(bootstrap.repo, "add_resume", AsyncMock())
    monkeypatch.setattr(bootstrap, "load_profile", lambda: _config())

    asyncio.run(bootstrap.bootstrap_user(123, "Roma"))

    bootstrap.repo.create_user.assert_not_awaited()
    bootstrap.repo.set_user_country.assert_not_awaited()
    bootstrap.repo.add_fact.assert_not_awaited()
    bootstrap.repo.update_search_settings.assert_not_awaited()
    bootstrap.repo.add_resume.assert_not_awaited()
