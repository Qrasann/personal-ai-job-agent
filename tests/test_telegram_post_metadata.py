import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.sources.adapters.telegram_ingest import parse_forwarded_job, parse_telegram_job
from app.sources import telegram_watch as watch
from app import services


def test_labeled_role_company_and_armenia_location_are_not_hashtag_titles():
    job = parse_telegram_job("#vacancy #jobs\nВакансия\n💼 Position: Linux Support Engineer\n🏢 Company: Example\n📍 Location: Remote - Yerevan, Armenia\nLinux skills", source_ref="fixture")
    assert job.title == "Linux Support Engineer"
    assert job.company == "Example"
    assert job.country == "AM" and job.city == "Yerevan"
    assert job.work_mode == "remote"
    assert job.remote_scope == "Remote - Yerevan, Armenia"
    assert job.relocation is None and job.visa_sponsorship is None
    assert job.raw["text"].startswith("#vacancy")


@pytest.mark.parametrize("location", ["Georgia, Armenia", "Georgia, USA", "Remote worldwide", "not disclosed",
                                      "Atlanta, Georgia", "Savannah, Georgia"])
def test_ambiguous_labeled_locations_do_not_invent_country(location):
    job = parse_telegram_job("Role: Support\nLocation: " + location, source_ref="fixture")
    assert job.country is None


def test_company_office_mentions_in_narrative_do_not_assign_location():
    job = parse_telegram_job("DevOps Engineer\nOur company has offices in Yerevan and Tbilisi.", source_ref="fixture")
    assert job.title == "DevOps Engineer"
    assert job.country is None and job.city is None and job.company == ""


def test_explicit_hybrid_mode_wins_over_remote_prose():
    job = parse_telegram_job("Role: Support\nWork mode: hybrid\nLocation: Tbilisi, Georgia\nFully remote tools", source_ref="fixture")
    assert job.work_mode == "hybrid"
    assert job.country == "GE"


def test_plain_title_skips_only_generic_headers_and_hashtag_lines():
    job = parse_telegram_job("#devops #jobs\nWe're hiring\nDevOps Engineer\nLinux", source_ref="fixture")
    assert job.title == "DevOps Engineer"


def test_channel_forward_preserves_original_identity_and_public_url():
    origin = SimpleNamespace(type="channel", chat=SimpleNamespace(id=-10042, username="devopsjobs"), message_id=99)
    forwarded = parse_forwarded_job("DevOps Engineer", chat_id=7, message_id=1, origin=origin)
    automatic = parse_telegram_job("DevOps Engineer", source_ref="channel:-10042:99", source_url="https://t.me/devopsjobs/99")
    assert forwarded.source_job_id == automatic.source_job_id
    assert forwarded.raw["source_ref"] == "channel:-10042:99"
    assert forwarded.url == "https://t.me/devopsjobs/99"


def test_hidden_forward_origin_does_not_fabricate_public_url():
    forwarded = parse_forwarded_job("DevOps Engineer", chat_id=7, message_id=1, origin=SimpleNamespace(type="hidden_user"))
    assert forwarded.url == ""
    assert forwarded.raw["source_ref"] == "forward:7:1"


def test_manual_and_automatic_same_channel_identity_share_replay_guard(monkeypatch):
    watch._LOCKS.clear()
    seen = set()
    async def already(user, identity, source):
        return identity in seen
    async def mark(user, identity, *args):
        seen.add(identity)
    monkeypatch.setattr(watch.repo, "message_seen", already)
    monkeypatch.setattr(watch.repo, "mark_message_seen", mark)
    ingest = AsyncMock(return_value={"processed": 2})
    monkeypatch.setattr(services, "ingest_and_match", ingest)
    job = parse_telegram_job("DevOps Engineer", source_ref="channel:-10042:99")
    async def run():
        results = await asyncio.gather(watch.consume_forwarded_job(None, 7, job), watch.consume_forwarded_job(None, 7, job))
        assert sorted(results) == [False, True]
    asyncio.run(run())
    ingest.assert_awaited_once()


def test_paused_manual_processing_does_not_consume_seen_identity(monkeypatch):
    watch._LOCKS.clear()
    monkeypatch.setattr(watch.repo, "message_seen", AsyncMock(return_value=False))
    mark = AsyncMock()
    monkeypatch.setattr(watch.repo, "mark_message_seen", mark)
    monkeypatch.setattr(services, "ingest_and_match", AsyncMock(return_value={"processed": 0}))
    asyncio.run(watch.consume_forwarded_job(None, 7, parse_telegram_job("Support", source_ref="channel:-10042:99")))
    mark.assert_not_awaited()
