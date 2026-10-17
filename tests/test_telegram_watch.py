import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from app import services
from app.sources import telegram_watch as watch


@pytest.fixture
def memory(monkeypatch):
    watch._LOCKS.clear()
    states, seen = {}, set()

    async def get_state(user, key, default=""):
        return states.get((user, key), default)

    async def set_state(user, key, value):
        states[user, key] = value

    async def message_seen(user, message, source):
        return (user, message, source) in seen

    async def mark_seen(user, message, conversation, text, source):
        seen.add((user, message, source))

    monkeypatch.setattr(watch.repo, "get_state", get_state)
    monkeypatch.setattr(watch.repo, "set_state", set_state)
    monkeypatch.setattr(watch.repo, "message_seen", message_seen)
    monkeypatch.setattr(watch.repo, "mark_message_seen", mark_seen)
    monkeypatch.setattr(watch.repo, "list_active_users", AsyncMock(return_value=[SimpleNamespace(id=1)]))
    monkeypatch.setattr(watch.repo, "active_profile", AsyncMock(return_value=SimpleNamespace(id=10)))
    monkeypatch.setattr(watch.repo, "list_search_profiles", AsyncMock(return_value=[
        SimpleNamespace(id=11, kind="career", settings={}),
        SimpleNamespace(id=12, kind="relocation", settings={}),
    ]))
    ingest = AsyncMock(return_value={"processed": 1, "qualified": 1, "notified": 0})
    monkeypatch.setattr(services, "ingest_and_match", ingest)
    return states, seen, ingest


@pytest.mark.parametrize("value,expected", [("@DevOpsJobs", "@devopsjobs"),
    ("https://t.me/DevOpsJobs", "@devopsjobs"), ("-100123456789", "-100123456789")])
def test_channel_identity_normalization(value, expected):
    assert watch.channel_key(value) == expected


@pytest.mark.parametrize("value", ["https://evil.test/channel", "https://t.me/jobsname/42", "https://t.me/+invite", "@a", "-42"])
def test_invalid_targets_do_not_create_subscriptions(value, memory):
    with pytest.raises(ValueError):
        asyncio.run(watch.change_subscription(1, "add", value))
    assert memory[0] == {}


async def post(published_at=None):
    return await watch.consume_channel_post(None, chat_id=-100123, username="devopsjobs",
                                            message_id=42, text="DevOps Engineer\nRemote worldwide\nLinux",
                                            published_at=published_at)


def test_subscription_delivery_is_scoped_persistent_and_replay_safe(memory):
    async def run():
        await watch.change_subscription(1, "add", "@DevOpsJobs", "relocation")
        await asyncio.gather(post(), post())
        watch._LOCKS.clear()  # Simulate restart of polling process.
        await post()
        state = await watch.watch_state(1)
        stats = state["channels"]["@devopsjobs"]["stats"]
        assert stats["posts"] == 1 and stats["replays"] == 2
        assert stats["processed"] == 1
        assert state["channels"]["@devopsjobs"]["last_post_at"]
    asyncio.run(run())
    ingest = memory[2]
    assert ingest.await_count == 1
    assert ingest.call_args.kwargs == {"only_user_id": 1, "only_search_profile_id": 12}
    normalized = ingest.call_args.args[1]
    assert normalized.url == "https://t.me/devopsjobs/42"
    assert normalized.raw["channel_id"] == -100123
    assert normalized.visa_sponsorship is None


def test_channel_publication_date_is_preserved(memory):
    async def run():
        await watch.change_subscription(1, "add", "@devopsjobs", "career")
        await watch.consume_channel_post(None, chat_id=-100123, username="devopsjobs", message_id=71,
                                         text="DevOps Engineer\nLinux", published_at=datetime(2026, 10, 17, 9, tzinfo=timezone.utc))
    asyncio.run(run())
    job = memory[2].call_args.args[1]
    assert job.published_at == "2026-10-17T09:00:00+00:00"
    assert job.raw["telegram_published_at"] == job.published_at


def test_invalid_channel_username_cannot_create_permalink(memory):
    async def run():
        await watch.change_subscription(1, "add", "-100123", "career")
        await watch.consume_channel_post(None, chat_id=-100123, username="bad/name", message_id=72,
                                         text="DevOps Engineer\nLinux")
    asyncio.run(run())
    job = memory[2].call_args.args[1]
    assert job.url == ""
    assert job.raw["channel_username"] is None


def test_explicit_candidate_and_ad_posts_are_counted_without_ingestion(memory):
    async def run():
        await watch.change_subscription(1, "add", "@devopsjobs", "both")
        for message_id, text in ((73, "Ищу работу: DevOps, 5 лет опыта"),
                                 (74, "#реклама курс по Docker")):
            await watch.consume_channel_post(None, chat_id=-100123, username="devopsjobs",
                                             message_id=message_id, text=text)
        state = await watch.watch_state(1)
        stats = state["channels"]["@devopsjobs"]["stats"]
        assert stats["received"] == stats["posts"] == stats["non_vacancy"] == 2
        assert stats["vacancy_candidates"] == 0
        await watch.consume_channel_post(None, chat_id=-100123, username="devopsjobs",
                                         message_id=73, text="Ищу работу: DevOps, 5 лет опыта")
        assert (await watch.watch_state(1))["channels"]["@devopsjobs"]["stats"]["replays"] == 1
    asyncio.run(run())
    memory[2].assert_not_awaited()


def test_rejected_post_marker_failure_does_not_block_another_subscriber(memory, monkeypatch):
    monkeypatch.setattr(watch.repo, "list_active_users", AsyncMock(return_value=[SimpleNamespace(id=1), SimpleNamespace(id=2)]))
    original_mark = watch.repo.mark_message_seen

    async def mark_seen(user, message, conversation, text, source):
        if user == 1:
            raise RuntimeError("temporary")
        await original_mark(user, message, conversation, text, source)

    monkeypatch.setattr(watch.repo, "mark_message_seen", mark_seen)

    async def run():
        await watch.change_subscription(1, "add", "@devopsjobs")
        await watch.change_subscription(2, "add", "@devopsjobs")
        await watch.consume_channel_post(None, chat_id=-100123, username="devopsjobs", message_id=96,
                                         text="Ищу работу: DevOps")
        assert (await watch.watch_state(1))["channels"]["@devopsjobs"]["stats"]["errors"] == 1
        assert (await watch.watch_state(2))["channels"]["@devopsjobs"]["stats"]["non_vacancy"] == 1

    asyncio.run(run())
    assert (2, "channel:-100123:96", "telegram_watch") in memory[1]


def test_vacancy_with_unknown_salary_or_resume_requirement_is_not_rejected(memory):
    async def run():
        await watch.change_subscription(1, "add", "@devopsjobs", "career")
        await watch.consume_channel_post(None, chat_id=-100123, username="devopsjobs", message_id=75,
                                         text="DevOps Engineer\nSend your resume\nSalary discussed later")
    asyncio.run(run())
    job = memory[2].call_args.args[1]
    assert job.salary_from is None and job.salary_currency is None
    assert memory[2].await_count == 1


def test_duplicate_subscription_aliases_union_profiles_once(memory):
    async def run():
        await watch.change_subscription(1, "add", "@devopsjobs", "career")
        await watch.change_subscription(1, "add", "-100123", "both")
        await post()
    asyncio.run(run())
    assert memory[2].await_count == 2
    assert {call.kwargs["only_search_profile_id"] for call in memory[2].call_args_list} == {11, 12}


@pytest.mark.parametrize("mode", ["off", "paused", "source_disabled", "unknown"])
def test_unselected_disabled_and_paused_users_are_not_processed(mode, memory, monkeypatch):
    async def run():
        if mode != "unknown":
            await watch.change_subscription(1, "add", "@devopsjobs")
        if mode == "off":
            await watch.change_subscription(1, "off", "@devopsjobs")
        elif mode == "paused":
            memory[0][(1, "paused")] = "true"
        elif mode == "source_disabled":
            monkeypatch.setattr(watch.repo, "list_search_profiles", AsyncMock(return_value=[
                SimpleNamespace(id=11, kind="career", settings={"disabled_sources": ["telegram"]}),
            ]))
        await post()
    asyncio.run(run())
    memory[2].assert_not_awaited()
    assert not memory[1]


def test_failed_processing_can_retry_without_consuming_seen_record(memory):
    memory[2].side_effect = [RuntimeError("temporary"), {"processed": 1}, {"processed": 1}]
    async def run():
        await watch.change_subscription(1, "add", "@devopsjobs")
        await post()
        assert not memory[1]
        await post()
        state = await watch.watch_state(1)
        stats = state["channels"]["@devopsjobs"]["stats"]
        assert stats["errors"] == 1 and stats["posts"] == 1
    asyncio.run(run())
    assert len(memory[1]) == 1


def test_pending_retry_preserves_original_publication_date(memory):
    original = datetime(2026, 10, 16, 12, tzinfo=timezone.utc)
    memory[2].side_effect = [RuntimeError("temporary"), {"processed": 1}]

    async def run():
        await watch.change_subscription(1, "add", "@devopsjobs", "career")
        await watch.consume_channel_post(None, chat_id=-100123, username="devopsjobs", message_id=95,
                                         text="DevOps Engineer\nLinux", published_at=original)
        assert (await watch.watch_state(1))["pending"]["channel:-100123:95"]["published_at"] == original.isoformat()
        assert await watch.retry_pending(None, user_id=1) == 1

    asyncio.run(run())
    assert memory[2].call_args.args[1].published_at == original.isoformat()


def test_configuration_preserves_stats_and_remove_keeps_seen_history(memory):
    async def run():
        await watch.change_subscription(1, "add", "@devopsjobs", "career")
        await post()
        await watch.change_subscription(1, "off", "@devopsjobs")
        await watch.change_subscription(1, "on", "@devopsjobs")
        state = await watch.watch_state(1)
        assert state["channels"]["@devopsjobs"]["stats"]["posts"] == 1
        await watch.change_subscription(1, "remove", "@devopsjobs")
        await watch.change_subscription(1, "add", "@devopsjobs")
        await post()
        assert (await watch.watch_state(1))["channels"]["@devopsjobs"]["stats"]["posts"] == 0
    asyncio.run(run())
    assert memory[2].await_count == 1


def test_corrupt_configuration_is_not_overwritten(memory):
    memory[0][(1, watch.STATE_KEY)] = "broken"
    with pytest.raises(RuntimeError, match="данные сохранены"):
        asyncio.run(watch.change_subscription(1, "add", "@devopsjobs"))
    assert memory[0][(1, watch.STATE_KEY)] == "broken"


def test_render_discloses_actual_bot_api_access_limits():
    text = watch.render_subscriptions({"channels": {}})
    assert "Подписок пока нет" in text
    assert "история каналов не сканируется" in text
    assert "сама не добавляет бота" in text


def test_channels_command_uses_only_registered_users_state(monkeypatch):
    from app.telegram import handlers
    message = SimpleNamespace(text="/channels add @devopsjobs relocation", answer=AsyncMock())
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=7)))
    change = AsyncMock(return_value={"channels": {}})
    monkeypatch.setattr(handlers, "change_subscription", change)
    asyncio.run(handlers.channels(message, None))
    change.assert_awaited_once_with(7, "add", "@devopsjobs", "relocation")
    assert message.answer.call_args.kwargs["parse_mode"] is None


def test_unregistered_user_cannot_create_watchlist(monkeypatch):
    from app.telegram import handlers
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=None))
    change = AsyncMock()
    monkeypatch.setattr(handlers, "change_subscription", change)
    asyncio.run(handlers.channels(SimpleNamespace(text="/channels add @devopsjobs"), None))
    change.assert_not_awaited()


def test_channel_caption_routes_into_watcher(monkeypatch):
    from app.telegram import handlers
    consume = AsyncMock()
    monkeypatch.setattr(handlers, "consume_channel_post", consume)
    date = datetime(2026, 10, 17, tzinfo=timezone.utc)
    message = SimpleNamespace(text=None, caption="DevOps role", chat=SimpleNamespace(id=-10042, username=None), message_id=2, date=date)
    asyncio.run(handlers.channel_post(message, None))
    consume.assert_awaited_once_with(None, chat_id=-10042, username=None, message_id=2, text="DevOps role", published_at=date)


def test_subscriber_failure_does_not_block_another_user(memory, monkeypatch):
    monkeypatch.setattr(watch.repo, "list_active_users", AsyncMock(return_value=[SimpleNamespace(id=1), SimpleNamespace(id=2)]))
    memory[0][(1, watch.STATE_KEY)] = "broken"
    async def run():
        await watch.change_subscription(2, "add", "@devopsjobs", "career")
        await post()
    asyncio.run(run())
    assert memory[2].await_count == 1
    assert memory[2].call_args.kwargs["only_user_id"] == 2


@pytest.mark.parametrize("failure", ["pause_state", "active_profile", "search_profiles"])
def test_subscriber_lookup_failure_does_not_block_other_users(failure, memory, monkeypatch):
    monkeypatch.setattr(watch.repo, "list_active_users", AsyncMock(return_value=[SimpleNamespace(id=1), SimpleNamespace(id=2)]))
    original_get_state = watch.repo.get_state
    original_search_profiles = watch.repo.list_search_profiles

    async def get_state(user, key, default=""):
        if failure == "pause_state" and user == 1 and key == "paused":
            raise RuntimeError("unavailable")
        return await original_get_state(user, key, default)

    async def search_profiles(profile):
        if failure == "search_profiles" and profile == 10:
            raise RuntimeError("unavailable")
        return await original_search_profiles(profile)

    async def run():
        await watch.change_subscription(1, "add", "@devopsjobs")
        await watch.change_subscription(2, "add", "@devopsjobs")
        await post()

    # Give the users distinct profile IDs so only user 1 fails the lookup.
    async def per_user_profile(user):
        if failure == "active_profile" and user == 1:
            raise RuntimeError("unavailable")
        return SimpleNamespace(id=10 if user == 1 else 20)

    monkeypatch.setattr(watch.repo, "get_state", get_state)
    monkeypatch.setattr(watch.repo, "active_profile", per_user_profile)
    monkeypatch.setattr(watch.repo, "list_search_profiles", search_profiles)
    asyncio.run(run())
    assert memory[2].await_count == 2
    assert all(call.kwargs["only_user_id"] == 2 for call in memory[2].call_args_list)


@pytest.mark.integration
def test_watchlist_and_replay_dedupe_survive_postgres_reload(monkeypatch):
    import os
    import uuid
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from app.database.models import Base

    url = os.getenv("JOB_AGENT_TEST_DATABASE_URL")
    if not url:
        if os.getenv("CI"):
            pytest.fail("CI requires JOB_AGENT_TEST_DATABASE_URL")
        pytest.skip("isolated PostgreSQL unavailable")

    async def run():
        engine = create_async_engine(url)
        monkeypatch.setattr(watch.repo, "SessionLocal", async_sessionmaker(engine, expire_on_commit=False))
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        try:
            user = await watch.repo.create_user("watch-test-" + uuid.uuid4().hex)
            profile = await watch.repo.ensure_default_profile(user.id)
            searches = await watch.repo.configure_parallel_search_profiles(profile.id, enabled=True)
            for search in searches:
                await watch.repo.update_search_settings(search.id, {**search.settings, "notify_min_score": 101})
            await watch.change_subscription(user.id, "add", "@devopsjobs")
            original_ingest = services.ingest_and_match
            monkeypatch.setattr(services, "ingest_and_match", AsyncMock(side_effect=RuntimeError("temporary")))
            published = datetime(2026, 10, 17, 10, tzinfo=timezone.utc)
            await post(published)
            assert (await watch.watch_state(user.id))["pending"]
            watch._LOCKS.clear()
            monkeypatch.setattr(services, "ingest_and_match", original_ingest)
            assert await watch.retry_pending(None, user_id=user.id) == 1
            state = await watch.watch_state(user.id)
            assert state["pending"] == {}
            assert state["channels"]["@devopsjobs"]["stats"]["processed"] == 2
            assert state["channels"]["@devopsjobs"]["stats"]["posts"] == 1
            watch._LOCKS.clear()
            await post()
            state = await watch.watch_state(user.id)
            assert state["channels"]["@devopsjobs"]["stats"]["posts"] == 1
            assert state["channels"]["@devopsjobs"]["stats"]["replays"] == 1
            rows = await watch.repo.latest_matches(user.id, limit=10, include_filtered=True)
            assert rows  # Real source persistence/matches, not a mocked scorer.
            assert all(job.published_at == published.isoformat() for _, job in rows)
        finally:
            await engine.dispose()
    asyncio.run(run())


def test_retry_queue_persists_failed_post_and_recovers_without_redelivery(memory):
    memory[2].side_effect = [RuntimeError("temporary"), {"processed": 1}, {"processed": 1}]
    async def run():
        await watch.change_subscription(1, "add", "@devopsjobs")
        await post()
        state = await watch.watch_state(1)
        assert list(state["pending"]) == ["channel:-100123:42"]
        watch._LOCKS.clear()
        assert await watch.retry_pending(None, user_id=1) == 1
        state = await watch.watch_state(1)
        assert state["pending"] == {}
        assert state["channels"]["@devopsjobs"]["stats"]["posts"] == 1
    asyncio.run(run())
    assert memory[2].await_count == 3


def test_retry_skips_unavailable_subscriber_and_continues(memory, monkeypatch):
    monkeypatch.setattr(watch.repo, "list_active_users", AsyncMock(return_value=[SimpleNamespace(id=1), SimpleNamespace(id=2)]))
    memory[2].side_effect = [RuntimeError("temporary"), {"processed": 1}, {"processed": 1}]

    async def prepare():
        await watch.change_subscription(2, "add", "@devopsjobs")
        await post()

    asyncio.run(prepare())
    original_get_state = watch.repo.get_state

    async def get_state(user, key, default=""):
        if user == 1 and key == "paused":
            raise RuntimeError("unavailable")
        return await original_get_state(user, key, default)

    monkeypatch.setattr(watch.repo, "get_state", get_state)
    assert asyncio.run(watch.retry_pending(None)) == 1
    assert asyncio.run(watch.watch_state(2))["pending"] == {}


@pytest.mark.parametrize("mode", ["off", "paused", "zero_limit"])
def test_retry_keeps_queue_when_processing_disabled(mode, memory):
    memory[2].side_effect = RuntimeError("temporary")
    async def run():
        await watch.change_subscription(1, "add", "@devopsjobs")
        await post()
        if mode == "off":
            await watch.change_subscription(1, "off", "@devopsjobs")
        elif mode == "paused":
            memory[0][(1, "paused")] = "true"
        assert await watch.retry_pending(None, user_id=1, limit=0 if mode == "zero_limit" else 5) == 0
        assert (await watch.watch_state(1))["pending"]
    asyncio.run(run())
    assert memory[2].await_count == 1


def test_retry_bound_retains_overflow_evidence_without_evicting_existing_queue(memory, monkeypatch):
    monkeypatch.setattr(watch, "MAX_PENDING", 1)
    memory[2].side_effect = RuntimeError("temporary")
    async def run():
        await watch.change_subscription(1, "add", "@devopsjobs")
        await post()
        await watch.consume_channel_post(None, chat_id=-100123, username="devopsjobs", message_id=43, text="Support")
        state = await watch.watch_state(1)
        assert list(state["pending"]) == ["channel:-100123:42"]
        assert state["retry_overflow"] == 1
        assert "переполненной очереди: 1" in watch.render_subscriptions(state)
    asyncio.run(run())


def test_retry_scheduler_is_bounded_and_nonoverlapping(monkeypatch):
    from app.main import _schedule_jobs
    from app.sources.telegram_watch import retry_telegram_watch
    from app.config import settings
    monkeypatch.setattr(settings, "hh_private_api_enabled", False)
    scheduler = SimpleNamespace(add_job=Mock())
    _schedule_jobs(scheduler, None)
    call = next(call for call in scheduler.add_job.call_args_list if call.args[0] is retry_telegram_watch)
    assert call.kwargs["max_instances"] == 1
    assert call.kwargs["coalesce"] is True
    assert call.kwargs["minutes"] == 1
