import asyncio
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.sources.telegram_folder_user import (
    connect_authorized_client, folder_inventory, folder_slug, load_cursors, load_local_config,
    poll_channel, sampled_posts, save_cursors, save_private_json, selected_channels,
)


def test_existing_session_guard_never_starts_login_flow():
    class FakeClient:
        def __init__(self, authorized):
            self.authorized = authorized
            self.connected = False
            self.disconnected = False

        async def connect(self):
            self.connected = True

        async def is_user_authorized(self):
            return self.authorized

        async def disconnect(self):
            self.disconnected = True

    unauthorized = FakeClient(False)
    with pytest.raises(RuntimeError, match="no login was attempted"):
        asyncio.run(connect_authorized_client(unauthorized))
    assert unauthorized.connected and unauthorized.disconnected

    authorized = FakeClient(True)
    asyncio.run(connect_authorized_client(authorized))
    assert authorized.connected and not authorized.disconnected


def test_folder_slug_accepts_only_exact_telegram_folder_link():
    assert folder_slug("https://t.me/addlist/abcdefgh") == "abcdefgh"
    for link in ("http://t.me/addlist/abcdefgh", "https://evil.test/addlist/abcdefgh",
                 "https://t.me/addlist/abcdefgh?join=1", "https://t.me/+abcdefgh",
                 "https://t.me/addlist/../../other"):
        with pytest.raises(ValueError):
            folder_slug(link)


def test_inventory_uses_peer_id_and_never_label_as_identity():
    chats = [
        SimpleNamespace(id=11, title="Same", username="devops_jobs", broadcast=True),
        SimpleNamespace(id=12, title="Same", username=None, broadcast=True),
        SimpleNamespace(id=13, title="Private discussion", username=None, megagroup=True),
    ]
    result = SimpleNamespace(chats=chats, peers=chats)
    inventory = folder_inventory(result, peer_id=lambda chat: -100000 - chat.id)
    assert [item["chat_id"] for item in inventory] == [-100011, -100012, -100013]
    assert all(not item["enabled"] and item["access"] == "not_probed" for item in inventory)
    assert inventory[2]["chat_type"] == "supergroup"


def test_selection_requires_current_folder_broadcast_id_and_explicit_opt_in():
    inventory = [
        {"chat_id": -10011, "chat_type": "broadcast", "username": "current"},
        {"chat_id": -10012, "chat_type": "supergroup", "username": None},
    ]
    selected = selected_channels({"chats": [
        {"chat_id": -10011, "username": "stale", "scope": "relocation", "enabled": True},
        {"chat_id": -10012, "scope": "career", "enabled": False},
    ]}, inventory)
    assert selected == {-10011: {**inventory[0], "scope": "relocation"}}
    for invalid_id in (-10012, -10013, True):
        with pytest.raises(ValueError):
            selected_channels({"chats": [{"chat_id": invalid_id, "scope": "both", "enabled": True}]}, inventory)


def test_left_channel_is_not_enabled_from_folder_preview():
    chat = SimpleNamespace(id=42, title="Jobs", username="jobs", broadcast=True, left=True)
    result = SimpleNamespace(chats=[chat], peers=[chat])
    inventory = folder_inventory(result, peer_id=lambda chat: -100000 - chat.id)
    assert inventory[0]["access"] == "left"
    with pytest.raises(ValueError):
        selected_channels({"chats": [{"chat_id": -100042, "scope": "both", "enabled": True}]}, inventory)


def test_inventory_excludes_chat_metadata_not_referenced_by_folder():
    permitted = SimpleNamespace(id=1, title="Approved", broadcast=True)
    unrelated = SimpleNamespace(id=2, title="Other", broadcast=True)
    inventory = folder_inventory(SimpleNamespace(chats=[permitted, unrelated], peers=[permitted]),
                                 peer_id=lambda chat: -100000 - chat.id)
    assert [item["chat_id"] for item in inventory] == [-100001]


def test_private_local_config_only(tmp_path: Path):
    path = tmp_path / "folder.json"
    path.write_text('{"folder_link":"https://t.me/addlist/abcdefgh","chats":[]}', encoding="utf-8")
    with pytest.raises(ValueError):
        load_local_config(path)
    path.chmod(0o600)
    assert load_local_config(path)["chats"] == []


def test_cursor_file_is_private_and_rejects_corruption(tmp_path: Path):
    path = tmp_path / "cursors.json"
    assert load_cursors(path) == {}
    save_cursors(path, {"-100123": 42})
    assert path.stat().st_mode & 0o077 == 0
    assert load_cursors(path) == {"-100123": 42}
    path.write_text('{"-100123":true}', encoding="utf-8")
    with pytest.raises(ValueError, match="original preserved"):
        load_cursors(path)


def test_poll_anchors_without_backfill_then_reads_only_new_selected_posts():
    class FakeClient:
        async def get_messages(self, peer, *, limit):
            assert peer == "approved" and limit == 1
            return [SimpleNamespace(id=100)]

        async def iter_messages(self, peer, *, min_id, reverse, limit):
            assert peer == "approved" and min_id == 100 and reverse and limit == 2
            for message_id in (101, 102):
                yield SimpleNamespace(id=message_id)

    async def run():
        observed = []
        async def accept(message):
            observed.append(message.id)
        anchor = await poll_channel(FakeClient(), "approved", None, accept)
        assert anchor == 100 and observed == []
        latest = await poll_channel(FakeClient(), "approved", anchor, accept, limit=2)
        assert latest == 102 and observed == [101, 102]

    asyncio.run(run())


def test_poll_failure_does_not_advance_cursor_past_failed_post():
    class FakeClient:
        async def iter_messages(self, peer, *, min_id, reverse, limit):
            assert peer == "approved" and min_id == 100
            for message_id in (101, 102):
                yield SimpleNamespace(id=message_id)

    async def run():
        async def accept(message):
            if message.id == 102:
                raise RuntimeError("temporary")

        with pytest.raises(RuntimeError, match="temporary"):
            await poll_channel(FakeClient(), "approved", 100, accept)

    asyncio.run(run())


def test_sampled_posts_keep_only_bounded_public_channel_evidence():
    messages = [
        SimpleNamespace(id=12, raw_text="Vacancy two", date=datetime(2026, 10, 18, 12, tzinfo=UTC)),
        SimpleNamespace(id=11, raw_text="Vacancy one", date=datetime(2026, 10, 18, 11)),
        SimpleNamespace(id=10, raw_text="", date=datetime(2026, 10, 18, 10, tzinfo=UTC)),
    ]

    rows = sampled_posts(messages, chat_id=-100123, username="jobs_feed")

    assert [row["message_id"] for row in rows] == [11, 12]
    assert rows[0]["published_at"].endswith("+00:00")
    assert rows[1]["url"] == "https://t.me/jobs_feed/12"
    assert {key for key in rows[0]} == {
        "channel_id", "username", "message_id", "text", "published_at", "url",
    }


def test_private_sample_write_is_atomic_and_mode_0600(tmp_path: Path):
    path = tmp_path / "pilot-sample.json"

    save_private_json(path, {"schema": 1, "posts": []})

    assert path.stat().st_mode & 0o077 == 0
    assert path.read_text(encoding="utf-8") == '{"schema": 1, "posts": []}'
