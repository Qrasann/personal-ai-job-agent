"""Optional, local MTProto intake for explicitly selected folder channels.

This module never joins chats or sends user-account messages. Telethon is an
optional dependency and is imported only by the local command-line runner.
"""
from __future__ import annotations

import json
import re
import os
import tempfile
from pathlib import Path
from urllib.parse import urlparse


def folder_slug(link: str) -> str:
    if not isinstance(link, str):
        raise ValueError("Invalid Telegram folder link")
    parsed = urlparse(link.strip())
    if parsed.scheme != "https" or parsed.hostname not in {"t.me", "www.t.me"}:
        raise ValueError("Expected an HTTPS t.me/addlist folder link")
    if parsed.query or parsed.fragment or not re.fullmatch(r"/addlist/[A-Za-z0-9_-]{8,128}", parsed.path):
        raise ValueError("Invalid Telegram folder link")
    return parsed.path.rsplit("/", 1)[1]


def folder_inventory(result, *, peer_id) -> list[dict]:
    """Inventory only chats returned by Telegram's folder-preview method.

    Preview membership is not proof of joined status or history access.
    """
    inventory = []
    seen = set()
    for chat in result.chats:
        chat_id = peer_id(chat)
        if chat_id in seen:
            continue
        seen.add(chat_id)
        kind = ("broadcast" if getattr(chat, "broadcast", False) else
                "supergroup" if getattr(chat, "megagroup", False) else "group")
        inventory.append({
            "chat_id": chat_id,
            "username": getattr(chat, "username", None),
            "chat_type": kind,
            "title": getattr(chat, "title", ""),
            "access": "left" if getattr(chat, "left", False) else "not_probed",
            "enabled": False,
            "scope": "both",
        })
    return inventory


def selected_channels(config: dict, inventory: list[dict]) -> dict[int, dict]:
    """Reject stale/foreign/private peers before registering any intake."""
    if not isinstance(config, dict) or not isinstance(config.get("chats"), list):
        raise ValueError("Invalid local folder configuration")
    verified = {item["chat_id"]: item for item in inventory
                if item["chat_type"] == "broadcast" and item.get("access") != "left"}
    selected = {}
    for item in config["chats"]:
        if not isinstance(item, dict) or not isinstance(item.get("enabled"), bool):
            raise ValueError("Invalid channel selection")
        if not item["enabled"]:
            continue
        chat_id = item.get("chat_id")
        if not isinstance(chat_id, int) or isinstance(chat_id, bool) or chat_id not in verified:
            raise ValueError("Enabled chat is not a verified broadcast channel in this folder")
        if chat_id in selected or item.get("scope") not in {"career", "relocation", "both"}:
            raise ValueError("Duplicate channel or invalid search scope")
        # Never trust a stale configured username; use the current Telegram peer.
        selected[chat_id] = {**verified[chat_id], "scope": item["scope"]}
    return selected


def load_local_config(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_mode & 0o077:
        raise ValueError("Folder configuration must be a private regular file (mode 0600)")
    data = json.loads(path.read_text(encoding="utf-8"))
    folder_slug(data.get("folder_link", ""))
    return data


def load_cursors(path: Path) -> dict[str, int]:
    if not path.exists():
        return {}
    if path.is_symlink() or not path.is_file() or path.stat().st_mode & 0o077:
        raise ValueError("Telegram cursor file must be private (mode 0600)")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or any(
        not isinstance(key, str) or not re.fullmatch(r"-100\d{1,16}", key)
        or not isinstance(value, int) or isinstance(value, bool) or value < 0
        for key, value in data.items()
    ):
        raise ValueError("Invalid Telegram cursor file; original preserved")
    return data


def save_cursors(path: Path, cursors: dict[str, int]) -> None:
    """Atomically save selected-channel offsets without exposing session data."""
    descriptor, name = tempfile.mkstemp(prefix="cursor-", dir=path.parent)
    temp = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(cursors, handle)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


async def poll_channel(client, peer, previous_id: int | None, accept, *, limit: int = 20) -> int:
    """Only query one approved channel; first poll anchors without backfill."""
    if previous_id is None:
        latest = await client.get_messages(peer, limit=1)
        return latest[0].id if latest else 0
    current = previous_id
    async for message in client.iter_messages(peer, min_id=previous_id, reverse=True, limit=limit):
        if message.id <= current:
            continue
        await accept(message)
        current = message.id
    return current
