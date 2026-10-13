import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

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


async def post():
    return await watch.consume_channel_post(None, chat_id=-100123, username="devopsjobs",
                                            message_id=42, text="DevOps Engineer\nRemote worldwide\nLinux")


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
    asyncio.run(handlers.channels(message))
    change.assert_awaited_once_with(7, "add", "@devopsjobs", "relocation")
    assert message.answer.call_args.kwargs["parse_mode"] is None


def test_unregistered_user_cannot_create_watchlist(monkeypatch):
    from app.telegram import handlers
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=None))
    change = AsyncMock()
    monkeypatch.setattr(handlers, "change_subscription", change)
    asyncio.run(handlers.channels(SimpleNamespace(text="/channels add @devopsjobs")))
    change.assert_not_awaited()


def test_channel_caption_routes_into_watcher(monkeypatch):
    from app.telegram import handlers
    consume = AsyncMock()
    monkeypatch.setattr(handlers, "consume_channel_post", consume)
    message = SimpleNamespace(text=None, caption="DevOps role", chat=SimpleNamespace(id=-10042, username=None), message_id=2)
    asyncio.run(handlers.channel_post(message, None))
    consume.assert_awaited_once_with(None, chat_id=-10042, username=None, message_id=2, text="DevOps role")


def test_subscriber_failure_does_not_block_another_user(memory, monkeypatch):
    monkeypatch.setattr(watch.repo, "list_active_users", AsyncMock(return_value=[SimpleNamespace(id=1), SimpleNamespace(id=2)]))
    memory[0][(1, watch.STATE_KEY)] = "broken"
    async def run():
        await watch.change_subscription(2, "add", "@devopsjobs", "career")
        await post()
    asyncio.run(run())
    assert memory[2].await_count == 1
    assert memory[2].call_args.kwargs["only_user_id"] == 2


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
            await post()
            state = await watch.watch_state(user.id)
            assert state["channels"]["@devopsjobs"]["stats"]["processed"] == 2
            assert state["channels"]["@devopsjobs"]["stats"]["posts"] == 1
            watch._LOCKS.clear()
            await post()
            state = await watch.watch_state(user.id)
            assert state["channels"]["@devopsjobs"]["stats"]["posts"] == 1
            assert state["channels"]["@devopsjobs"]["stats"]["replays"] == 1
            rows = await watch.repo.latest_matches(user.id, limit=10, include_filtered=True)
            assert rows  # Real source persistence/matches, not a mocked scorer.
        finally:
            await engine.dispose()
    asyncio.run(run())
