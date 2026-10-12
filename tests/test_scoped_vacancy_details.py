import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app import services


def test_details_keep_the_selected_profiles_score_and_name(monkeypatch):
    match = SimpleNamespace(profile_id=2, search_profile_id=4, total_score=54)
    job = SimpleNamespace(id=25, description="Warehouse role")
    lookup = AsyncMock(return_value=match)
    monkeypatch.setattr(services.repo, "get_match_for_user_job", lookup)
    monkeypatch.setattr(services.repo, "get_job", AsyncMock(return_value=job))
    monkeypatch.setattr(services.repo, "source_ref", AsyncMock(return_value=None))
    refresh = AsyncMock(return_value=match)
    monkeypatch.setattr(services, "refresh_match_score", refresh)
    monkeypatch.setattr(services.repo, "list_search_profiles", AsyncMock(return_value=[
        SimpleNamespace(id=3, name="Career-first"),
        SimpleNamespace(id=4, name="Relocation-first"),
    ]))

    payload = asyncio.run(services.get_vacancy_details(7, 25, search_profile_id=4))

    lookup.assert_awaited_once_with(7, 25, search_profile_id=4)
    refresh.assert_awaited_once_with(match, job, technical_text="Warehouse role")
    assert payload["match"].total_score == 54
    assert payload["search_profile_name"] == "Relocation-first"


def test_details_do_not_fall_back_when_user_has_no_match_in_requested_profile(monkeypatch):
    lookup = AsyncMock(return_value=None)
    monkeypatch.setattr(services.repo, "get_match_for_user_job", lookup)
    job_lookup = AsyncMock()
    monkeypatch.setattr(services.repo, "get_job", job_lookup)

    with pytest.raises(RuntimeError, match="не найдена среди твоих совпадений"):
        asyncio.run(services.get_vacancy_details(7, 25, search_profile_id=4))

    lookup.assert_awaited_once_with(7, 25, search_profile_id=4)
    job_lookup.assert_not_awaited()


def test_comparison_uses_the_same_search_profile_as_the_details(monkeypatch):
    match = SimpleNamespace(profile_id=2, search_profile_id=4, total_score=54)
    details = AsyncMock(return_value={
        "job": SimpleNamespace(description="Warehouse role"),
        "match": match,
        "search_profile_name": "Relocation-first",
    })
    monkeypatch.setattr(services, "get_vacancy_details", details)
    monkeypatch.setattr(services.repo, "list_facts", AsyncMock(return_value=[]))

    result = asyncio.run(services.get_vacancy_comparison(7, 25, search_profile_id=4))

    details.assert_awaited_once_with(7, 25, search_profile_id=4)
    assert result["match"] is match
    assert result["search_profile_name"] == "Relocation-first"


@pytest.mark.parametrize("restrictions,expected", [
    (["UTC-5", " UTC+4 "], ["UTC-5", "UTC+4"]),
    ([], None),
    (None, None),
    ("UTC+4", None),
    ({"offset": "UTC+4"}, None),
    ([None, 4, {}, " "], None),
])
def test_himalayas_details_pass_known_timezones_without_changing_match(monkeypatch, restrictions, expected):
    match = SimpleNamespace(profile_id=2, search_profile_id=3, total_score=82, geography_score=100)
    job = SimpleNamespace(id=25, description="Globally remote Linux support", remote_scope="worldwide")
    ref = SimpleNamespace(source_id="himalayas", url="https://himalayas.app/jobs/25", raw={
        "timezone_restrictions": restrictions,
    })

    async def source_ref(_job_id, source_id=None):
        return ref if source_id == "himalayas" else None

    monkeypatch.setattr(services.repo, "get_match_for_user_job", AsyncMock(return_value=match))
    monkeypatch.setattr(services.repo, "get_job", AsyncMock(return_value=job))
    monkeypatch.setattr(services.repo, "source_ref", source_ref)
    refresh = AsyncMock(return_value=match)
    monkeypatch.setattr(services, "refresh_match_score", refresh)
    monkeypatch.setattr(services.repo, "list_search_profiles", AsyncMock(return_value=[
        SimpleNamespace(id=3, name="Career-first"),
    ]))

    payload = asyncio.run(services.get_vacancy_details(7, 25, search_profile_id=3))

    assert payload["details"].get("timezone_restrictions") == expected
    assert payload["job"].remote_scope == "worldwide"
    assert payload["match"].geography_score == 100
    assert payload["match"].total_score == 82
    refresh.assert_awaited_once_with(match, job, technical_text="Globally remote Linux support")
