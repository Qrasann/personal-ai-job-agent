import asyncio
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.sources.telegram_folder_user import (
    folder_inventory, folder_slug, load_cursors, load_local_config,
    poll_channel, save_cursors, selected_channels,
)


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
