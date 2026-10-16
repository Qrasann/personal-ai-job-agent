import asyncio
import os
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app import services
from app.database import notification_delivery as journal
from app.database import repository as repo
from app.database.models import Base, JobMatch, RuntimeState
from app.domain.jobs import NormalizedJob
from app.telegram import handlers


TEST_DATABASE_URL = os.getenv("JOB_AGENT_TEST_DATABASE_URL")


def _postgres_required():
    if TEST_DATABASE_URL:
        return
    if os.getenv("CI"):
        pytest.fail("CI requires JOB_AGENT_TEST_DATABASE_URL")
    pytest.skip("Isolated PostgreSQL URL is not configured")


def _payload(match_id: int, job_id: int = 42) -> dict:
    return {
        "match_id": match_id, "job_id": job_id, "text": "🔥 <b>Linux Engineer</b>",
        "url": "https://example.invalid/vacancy/42", "can_apply": False,
    }


@pytest.mark.integration
def test_real_postgres_notification_claim_concurrency_recovery_and_fencing(monkeypatch):
    _postgres_required()
    asyncio.run(_postgres_claim_flow(monkeypatch))


async def _postgres_claim_flow(monkeypatch):
    engine = create_async_engine(TEST_DATABASE_URL)
    sessions = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    monkeypatch.setattr(journal, "SessionLocal", sessions)
    monkeypatch.setattr(repo, "SessionLocal", sessions)
    base_time = datetime(2026, 10, 16, 12, 0, tzinfo=UTC)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        user = await repo.create_user("notification-owner-001", "Owner")
        profile = await repo.ensure_default_profile(user.id)
        searches = await repo.list_search_profiles(profile.id)
        job, _ = await repo.upsert_job(NormalizedJob(
            source="hh", source_job_id="notification-job-001", title="Linux Engineer",
            company="Test Company", description="Linux",
        ))
        match = await repo.save_match(
            job_id=job.id, user_id=user.id, profile_id=profile.id,
            search_profile_id=searches[0].id,
        )
        payload = _payload(match.id, job.id)
        attempts = await asyncio.gather(
            journal.claim_job_notification(
                user_id=user.id, match_id=match.id, payload=payload, now=base_time,
            ),
            journal.claim_job_notification(
                user_id=user.id, match_id=match.id, payload=payload, now=base_time,
            ),
        )
        accepted = [x for x in attempts if x]
        assert len(accepted) == 1
        first = accepted[0]
        assert first["payload"] == payload
        assert first["attempt"] == 1
        assert await journal.due_job_notifications(now=base_time + timedelta(seconds=119)) == []
        assert await journal.due_job_notifications(now=base_time + timedelta(seconds=121)) == [
            (user.id, match.id),
        ]
        second = await journal.claim_job_notification(
            user_id=user.id, match_id=match.id, payload={"text": "MUTATED", "match_id": match.id},
            now=base_time + timedelta(seconds=121),
        )
        assert second and second["attempt"] == 2
        assert second["payload"] == payload
        assert second["token"] != first["token"]
        assert not await journal.settle_job_notification(
            user_id=user.id, match_id=match.id, token=first["token"],
            delivered=True, now=base_time + timedelta(seconds=122),
        )
        assert await journal.settle_job_notification(
            user_id=user.id, match_id=match.id, token=second["token"],
            delivered=True, message_id=777,
            now=base_time + timedelta(seconds=123),
        )
        saved = await repo.get_match(match.id)
        assert saved.status == "notified"
        entries = await journal.recent_job_notification_journal(user.id)
        assert entries[0]["attempts"] == 2
        assert entries[0]["status"] == "sent"
        assert entries[0]["telegram_message_id"] == 777
        assert await journal.due_job_notifications(now=base_time + timedelta(days=1)) == []
        assert await journal.claim_job_notification(
            user_id=user.id, match_id=match.id, payload=payload,
            now=base_time + timedelta(days=1),
        ) is None
    finally:
        await engine.dispose()


@pytest.mark.integration
def test_postgres_failed_notification_retry_and_owner_scoping(monkeypatch):
    _postgres_required()
    asyncio.run(_postgres_retry_flow(monkeypatch))


async def _postgres_retry_flow(monkeypatch):
    engine = create_async_engine(TEST_DATABASE_URL)
    sessions = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    monkeypatch.setattr(journal, "SessionLocal", sessions)
    monkeypatch.setattr(repo, "SessionLocal", sessions)
    now = datetime(2026, 10, 16, 12, 0, tzinfo=UTC)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        owner = await repo.create_user("notification-owner-002", "Owner")
        other = await repo.create_user("notification-owner-003", "Other")
        # The shared runtime_state table contains arbitrary non-JSON settings.
        # A retry query must not attempt to cast unrelated values to JSONB.
        await repo.set_state(other.id, "unrelated_text_setting", "definitely not JSON")
        # A corrupt notification state must be quarantined by the due query,
        # never abort the entire user's retry queue.
        await repo.set_state(owner.id, "jobnotify:malformed", "{not-valid-json")
        # Completed entries can fill more than one query page. The later due
        # entry still must be found without parsing the corrupt one as JSONB.
        async with sessions() as session:
            session.add_all([
                RuntimeState(
                    user_id=owner.id, key=f"jobnotify:archived-{i:04d}",
                    value='{"status":"sent"}',
                )
                for i in range(275)
            ])
            await session.commit()
        profile = await repo.ensure_default_profile(owner.id)
        searches = await repo.list_search_profiles(profile.id)
        job, _ = await repo.upsert_job(NormalizedJob(
            source="remoteok", source_job_id="notification-job-002",
            title="Platform Engineer", company="Company",
        ))
        match = await repo.save_match(
            job_id=job.id, user_id=owner.id, profile_id=profile.id,
            search_profile_id=searches[0].id,
        )
        payload = _payload(match.id, job.id)
        assert await journal.claim_job_notification(
            user_id=other.id, match_id=match.id, payload=payload, now=now,
        ) is None
        sent = await journal.claim_job_notification(
            user_id=owner.id, match_id=match.id, payload=payload, now=now,
        )
        assert sent
        assert await journal.settle_job_notification(
            user_id=owner.id, match_id=match.id, token=sent["token"],
            delivered=False, now=now + timedelta(seconds=2),
        )
        assert await journal.due_job_notifications(
            user_id=owner.id, now=now + timedelta(seconds=61),
        ) == []
        assert await journal.due_job_notifications(
            user_id=owner.id, now=now + timedelta(seconds=62),
        ) == [(owner.id, match.id)]
        assert await journal.due_job_notifications(
            user_id=other.id, now=now + timedelta(seconds=65),
        ) == []
        attempt = await journal.claim_job_notification(
            user_id=owner.id, match_id=match.id, now=now + timedelta(seconds=62),
        )
        assert attempt["attempt"] == 2
        assert await journal.settle_job_notification(
            user_id=owner.id, match_id=match.id, token=attempt["token"],
            delivered=True, now=now + timedelta(seconds=63),
        )
        assert (await repo.get_match(match.id)).status == "notified"
        assert (await journal.recent_job_notification_journal(owner.id))[0]["status"] == "sent"
        assert await journal.recent_job_notification_journal(other.id) == []
    finally:
        await engine.dispose()


def test_deliver_success_commits_after_network_and_reconstructs_original_keyboard(monkeypatch):
    events = []
    async def send(_bot, chat_id, text, **kwargs):
        events.append("telegram")
        assert chat_id == "123"
        assert text == "Original posting"
        assert kwargs["reply_markup"].inline_keyboard
        return SimpleNamespace(message_id=57)

    async def settle(**kw):
        events.append("database")
        assert kw["delivered"] is True
        assert kw["message_id"] == 57
        return True

    monkeypatch.setattr(services, "notify_chat", send)
    monkeypatch.setattr(services.delivery_repo, "settle_job_notification", settle)
    claim = {
        "user_id": 4, "match_id": 7, "chat_id": "123", "token": "x",
        "payload": {**_payload(7), "text": "Original posting"},
    }
    assert asyncio.run(services._send_claimed_job_alert(object(), claim))
    assert events == ["telegram", "database"]


def test_lost_database_ack_after_telegram_send_preserves_lease(monkeypatch):
    send = AsyncMock(return_value=SimpleNamespace(message_id=1))
    mark = AsyncMock(side_effect=RuntimeError("database unreachable"))
    monkeypatch.setattr(services, "notify_chat", send)
    monkeypatch.setattr(services.delivery_repo, "settle_job_notification", mark)
    claim = {
        "user_id": 4, "match_id": 7, "chat_id": "123", "token": "x",
        "payload": _payload(7),
    }
    assert not asyncio.run(services._send_claimed_job_alert(object(), claim))
    send.assert_awaited_once()
    assert mark.await_count == 1
    assert mark.await_args.kwargs["delivered"] is True


def test_failed_telegram_send_schedules_retry_without_leaking_error(monkeypatch, caplog):
    fail = AsyncMock(side_effect=RuntimeError("Authorization Bearer secret"))
    mark = AsyncMock(return_value=True)
    monkeypatch.setattr(services, "notify_chat", fail)
    monkeypatch.setattr(services.delivery_repo, "settle_job_notification", mark)
    claim = {
        "user_id": 4, "match_id": 7, "chat_id": "123", "token": "x",
        "payload": _payload(7),
    }
    assert not asyncio.run(services._send_claimed_job_alert(object(), claim))
    assert mark.await_args.kwargs["delivered"] is False
    assert "Authorization Bearer secret" not in caplog.text


def test_scheduled_retry_does_not_need_provider_scan_and_skips_paused(monkeypatch):
    due = AsyncMock(return_value=[(2, 21), (3, 31)])
    state = AsyncMock(side_effect=lambda user_id, *_: "true" if user_id == 2 else "false")
    claim = AsyncMock(return_value={
        "user_id": 3, "match_id": 31, "chat_id": "123", "token": "xyz",
        "payload": _payload(31),
    })
    send = AsyncMock(return_value=True)
    monkeypatch.setattr(services.delivery_repo, "due_job_notifications", due)
    monkeypatch.setattr(services.repo, "get_state", state)
    monkeypatch.setattr(services.delivery_repo, "claim_job_notification", claim)
    monkeypatch.setattr(services, "_send_claimed_job_alert", send)
    asyncio.run(services.retry_job_notifications(object()))
    claim.assert_awaited_once_with(user_id=3, match_id=31)
    send.assert_awaited_once()


def test_delivery_command_shows_only_scoped_metadata(monkeypatch):
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=9)))
    scoped = AsyncMock(return_value=[
        {"match_id": "48", "status": "retry", "attempts": 2},
        {"match_id": "49", "status": "sent", "attempts": 1},
    ])
    monkeypatch.setattr(handlers.delivery_repo, "recent_job_notification_journal", scoped)
    message = SimpleNamespace(answer=AsyncMock())
    asyncio.run(handlers.delivery_status_command(message))
    scoped.assert_awaited_once_with(9)
    rendered = message.answer.await_args.args[0]
    assert "ожидает повтора" in rendered
    assert "#48" in rendered
    assert "#49" in rendered
    assert "secret" not in rendered



@pytest.mark.integration
def test_end_to_end_ingestion_alert_then_rescan_does_not_repeat_sent_message(monkeypatch):
    _postgres_required()
    asyncio.run(_ingestion_delivery_flow(monkeypatch))


async def _ingestion_delivery_flow(monkeypatch):
    engine = create_async_engine(TEST_DATABASE_URL)
    sessions = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    monkeypatch.setattr(repo, "SessionLocal", sessions)
    monkeypatch.setattr(journal, "SessionLocal", sessions)
    monkeypatch.setattr(services, "score_job", lambda *_args, **_kwargs: SimpleNamespace(
        technical_score=85, geography_score=90, salary_score=75,
        relocation_score=75, total_score=86,
        reason="Observed Linux requirements", track="career", fit="good",
        resume_id=None, recommendation_scores={},
    ))
    bot = SimpleNamespace(send_message=AsyncMock(return_value=SimpleNamespace(message_id=803)))
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        owner = await repo.create_user("987001", "Owner")
        await repo.ensure_default_profile(owner.id)
        normalized = NormalizedJob(
            source="arbeitnow", source_job_id="unique-posting-802",
            title="Linux Engineer", company="Employer", description="Linux Bash Docker",
            url="https://example.invalid/job/802",
        )
        first = await services.ingest_and_match(
            bot, normalized, only_user_id=owner.id,
        )
        second = await services.ingest_and_match(
            bot, normalized, only_user_id=owner.id,
        )
        assert first["notified"] == 1
        assert second["notified"] == 0
        bot.send_message.assert_awaited_once()
        assert bot.send_message.await_args.args[0] == 987001
        entry = (await journal.recent_job_notification_journal(owner.id))[0]
        assert entry["status"] == "sent"
        assert entry["attempts"] == 1
        assert entry["telegram_message_id"] == 803
        assert not await journal.due_job_notifications(user_id=owner.id)
    finally:
        await engine.dispose()
