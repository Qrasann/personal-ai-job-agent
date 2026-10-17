"""Optional, local MTProto intake for explicitly selected folder channels.

This module never joins chats or sends user-account messages. Telethon is an
optional dependency and is imported only by the local command-line runner.
"""
from __future__ import annotations

import json
import re
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
