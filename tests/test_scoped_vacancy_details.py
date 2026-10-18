import asyncio
from datetime import datetime
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


def test_details_use_selected_source_posting_for_text_and_rescore(monkeypatch):
    match = SimpleNamespace(profile_id=2, search_profile_id=4, total_score=54)
    canonical = SimpleNamespace(id=25, title="HR role", company="Example", description="HR-only Linux")
    ref = SimpleNamespace(source_id="jobs_ge", source_job_id="jobs-ge-42", url="https://example.invalid/jobs_ge",
        first_seen_at=datetime(2026, 10, 14, 9, 0), raw={
        "normalized_posting_v1": {
            "schema": "normalized_posting_v1", "title": "Jobs.ge role",
            "company": "Example", "description": "Jobs.ge Docker",
        },
        "relocation_evidence_v1": {"source": "jobs_ge", "captured_at": "2026-10-15T12:30:00+00:00"},
    })
    async def source_ref(_job_id, source_id=None):
        return ref if source_id == "jobs_ge" else None
    monkeypatch.setattr(services.repo, "get_match_for_user_job", AsyncMock(return_value=match))
    monkeypatch.setattr(services.repo, "get_job", AsyncMock(return_value=canonical))
    monkeypatch.setattr(services.repo, "source_ref", source_ref)
    refresh = AsyncMock(return_value=match)
    monkeypatch.setattr(services, "refresh_match_score", refresh)
    monkeypatch.setattr(services.repo, "list_search_profiles", AsyncMock(return_value=[]))

    payload = asyncio.run(services.get_vacancy_details(7, 25))

    assert payload["job"].title == "Jobs.ge role"
    assert payload["details"]["description"] == "Jobs.ge Docker"
    assert payload["relocation_evidence"] == {"source": "jobs_ge", "captured_at": "2026-10-15T12:30:00+00:00"}
    assert payload["source_job_id"] == "jobs-ge-42"
    assert payload["source_observed_at"] == "2026-10-14T09:00:00+00:00"
    assert refresh.await_args.kwargs["technical_text"] == "Jobs.ge Docker"
    assert canonical.description == "HR-only Linux"


@pytest.mark.parametrize("evidence, expected", [
    ({"kind": "applications", "value": 17, "source_id": "ats", "observed_at": "2026-10-18T09:00:00+00:00"}, 17),
    ({"kind": "views", "value": 170}, None),
    ({"kind": "applications", "value": True}, None),
    ({"kind": "applications", "value": -1}, None),
])
def test_details_only_expose_persisted_confirmed_application_counts(monkeypatch, evidence, expected):
    match = SimpleNamespace(profile_id=2, search_profile_id=4, total_score=54)
    job = SimpleNamespace(id=25, description="Linux")
    ref = SimpleNamespace(
        source_id="greenhouse", source_job_id="42", url="https://careers.example/jobs/42",
        first_seen_at=datetime(2026, 10, 18, 9, 0), raw={"applicant_count_v1": evidence},
    )
    monkeypatch.setattr(services.repo, "get_match_for_user_job", AsyncMock(return_value=match))
    monkeypatch.setattr(services.repo, "get_job", AsyncMock(return_value=job))
    monkeypatch.setattr(services.repo, "source_ref", AsyncMock(return_value=ref))
    monkeypatch.setattr(services, "refresh_match_score", AsyncMock(return_value=match))
    monkeypatch.setattr(services.repo, "list_search_profiles", AsyncMock(return_value=[]))

    payload = asyncio.run(services.get_vacancy_details(7, 25))

    assert payload["details"].get("applicant_count") == expected


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
    profile = SimpleNamespace(english_level="B2")
    profile_lookup = AsyncMock(return_value=profile)
    monkeypatch.setattr(services.repo, "get_profile", profile_lookup)

    result = asyncio.run(services.get_vacancy_comparison(7, 25, search_profile_id=4))

    details.assert_awaited_once_with(7, 25, search_profile_id=4)
    assert result["match"] is match
    assert result["search_profile_name"] == "Relocation-first"
    assert result["language_fit"] is None
    profile_lookup.assert_awaited_once_with(2)


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
        "availability": {"source_field": "expiryDate", "expires_at": "2030-01-01T00:00:00+00:00"},
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
    assert payload["details"]["availability"] == ref.raw["availability"]
    assert payload["details"]["availability"] is not ref.raw["availability"]
    assert payload["job"].remote_scope == "worldwide"
    assert payload["match"].geography_score == 100
    assert payload["match"].total_score == 82
    refresh.assert_awaited_once_with(match, job, technical_text="Globally remote Linux support")
