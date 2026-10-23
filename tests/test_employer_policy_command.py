import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.telegram import handlers


def test_employer_policy_command_persists_exact_override_to_all_search_profiles(monkeypatch):
    searches = [
        SimpleNamespace(id=11, settings={"queries": ["DevOps"]}),
        SimpleNamespace(id=12, settings={"search_strategy": "relocation_first"}),
    ]
    writes = []
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=5)))
    monkeypatch.setattr(handlers.repo, "active_profile", AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers.repo, "list_search_profiles", AsyncMock(return_value=searches))

    async def update(search_id, settings):
        writes.append((search_id, settings))

    monkeypatch.setattr(handlers.repo, "update_search_settings", update)
    message = SimpleNamespace(text="/employerpolicy employer allow Betsson Group", answer=AsyncMock())

    asyncio.run(handlers.employer_policy_command(message))

    assert [search_id for search_id, _ in writes] == [11, 12]
    assert all(settings["employer_policy_overrides"]["employers"]["Betsson Group"] == "allow" for _, settings in writes)
    assert writes[0][1]["queries"] == ["DevOps"]
    assert writes[1][1]["search_strategy"] == "relocation_first"
    message.answer.assert_awaited_once_with("✅ Решение сохранено для всех поисковых профилей.")


def test_employer_policy_command_rejects_unknown_category_without_writing(monkeypatch):
    searches = [SimpleNamespace(id=11, settings={})]
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=5)))
    monkeypatch.setattr(handlers.repo, "active_profile", AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers.repo, "list_search_profiles", AsyncMock(return_value=searches))
    update = AsyncMock()
    monkeypatch.setattr(handlers.repo, "update_search_settings", update)
    message = SimpleNamespace(text="/employerpolicy category typo block", answer=AsyncMock())

    asyncio.run(handlers.employer_policy_command(message))

    update.assert_not_awaited()
    assert "Неизвестная категория" in message.answer.await_args.args[0]


def test_blacklist_view_does_not_claim_legacy_sector_terms_are_active(monkeypatch):
    searches = [SimpleNamespace(id=11, settings={"exclude_terms": ["gambling", "senior devops"]})]
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=5)))
    monkeypatch.setattr(handlers.repo, "active_profile", AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers.repo, "list_search_profiles", AsyncMock(return_value=searches))
    message = SimpleNamespace(text="/blacklist", answer=AsyncMock())

    asyncio.run(handlers.blacklist_command(message))

    response = message.answer.await_args.args[0]
    assert "senior devops" in response
    assert "gambling" not in response
    assert "/employerpolicy" in response


def test_blacklist_preview_does_not_write_and_exposes_confirmation(monkeypatch):
    searches = [SimpleNamespace(id=11, settings={"exclude_terms": ["Fraud"]})]
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=5)))
    monkeypatch.setattr(handlers.repo, "active_profile", AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers.repo, "list_search_profiles", AsyncMock(return_value=searches))
    update = AsyncMock()
    monkeypatch.setattr(handlers.repo, "update_search_settings", update)
    message = SimpleNamespace(text="/blacklist preview add Agency", answer=AsyncMock())

    asyncio.run(handlers.blacklist_command(message))

    update.assert_not_awaited()
    response = message.answer.await_args.args[0]
    assert "Было: Fraud" in response
    assert "Станет: Fraud, Agency" in response
    assert "Подтвердить: /blacklist add Agency" in response


def test_blacklist_undo_writes_all_search_profiles(monkeypatch):
    searches = [
        SimpleNamespace(id=11, settings={"exclude_terms": ["Fraud"], "_blacklist_undo": []}),
        SimpleNamespace(id=12, settings={"exclude_terms": ["Fraud"], "_blacklist_undo": []}),
    ]
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=5)))
    monkeypatch.setattr(handlers.repo, "active_profile", AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers.repo, "list_search_profiles", AsyncMock(return_value=searches))
    writes = []

    async def update(search_id, settings):
        writes.append((search_id, settings))

    monkeypatch.setattr(handlers.repo, "update_search_settings", update)
    message = SimpleNamespace(text="/blacklist undo", answer=AsyncMock())

    asyncio.run(handlers.blacklist_command(message))

    assert [search_id for search_id, _ in writes] == [11, 12]
    assert all(settings["exclude_terms"] == [] for _, settings in writes)
    assert all("_blacklist_undo" not in settings for _, settings in writes)
    assert "отменено" in message.answer.await_args.args[0]


def test_structured_blacklist_preview_lists_affected_jobs_without_writing(monkeypatch):
    searches = [SimpleNamespace(id=11, kind="career", name="Career-first", settings={})]
    job = SimpleNamespace(id=42, fingerprint="fp", title="DevOps Engineer", company="Example Corp", description="")
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=5)))
    monkeypatch.setattr(handlers.repo, "active_profile", AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers.repo, "list_search_profiles", AsyncMock(return_value=searches))
    monkeypatch.setattr(handlers.repo, "latest_matches", AsyncMock(return_value=[(SimpleNamespace(), job)]))
    update = AsyncMock()
    monkeypatch.setattr(handlers.repo, "update_search_settings", update)
    message = SimpleNamespace(
        text="/blacklist rule preview add company Example Corp --profile career", answer=AsyncMock(),
    )

    asyncio.run(handlers.blacklist_command(message))

    update.assert_not_awaited()
    response = message.answer.await_args.args[0]
    assert "затронуто среди последних 50/профиль: 1" in response
    assert "DevOps Engineer — Example Corp" in response
    assert "Подтвердить: /blacklist rule add company Example Corp --profile career" in response


def test_structured_blacklist_confirm_defaults_to_all_profiles_and_undo_is_scoped(monkeypatch):
    searches = [
        SimpleNamespace(id=11, kind="career", name="Career-first", settings={}),
        SimpleNamespace(id=12, kind="relocation", name="Relocation-first", settings={}),
    ]
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=5)))
    monkeypatch.setattr(handlers.repo, "active_profile", AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers.repo, "list_search_profiles", AsyncMock(return_value=searches))
    update = AsyncMock()
    monkeypatch.setattr(handlers.repo, "update_search_settings", update)

    asyncio.run(handlers.blacklist_command(SimpleNamespace(
        text="/blacklist rule add role DevOps Engineer", answer=AsyncMock(),
    )))
    assert [call.args[0] for call in update.await_args_list] == [11, 12]
    assert all(call.args[1]["blacklist_rules"][0]["value"] == "DevOps Engineer" for call in update.await_args_list)

    update.reset_mock()
    searches[0].settings = handlers.update_blacklist_rule({}, "add", "role", "DevOps Engineer")
    searches[1].settings = handlers.update_blacklist_rule({}, "add", "role", "DevOps Engineer")
    asyncio.run(handlers.blacklist_command(SimpleNamespace(
        text="/blacklist rule undo --profile relocation", answer=AsyncMock(),
    )))
    update.assert_awaited_once()
    assert update.await_args.args[0] == 12
    assert update.await_args.args[1]["blacklist_rules"] == []
