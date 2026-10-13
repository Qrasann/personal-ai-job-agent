"""Owner-selected Bot API channel updates; no account login or history scraping."""
from __future__ import annotations

import asyncio
import json
import logging
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

from app.database import repository as repo
from app.search.preferences import search_strategy, source_enabled
from app.sources.adapters.telegram_ingest import parse_telegram_job

STATE_KEY = "telegram_channel_watch_v1"
MAX_CHANNELS = 50
_COUNTERS = ("posts", "processed", "qualified", "stretch", "filtered", "notified", "duplicate", "replays", "errors")
# One polling process, matching the existing deployment. Cross-process delivery
# coordination is a later multi-worker concern; PostgreSQL seen records survive restart.
_LOCKS: dict[int, asyncio.Lock] = {}
log = logging.getLogger(__name__)


def channel_key(value: str) -> str:
    value = value.strip()
    if value.startswith("https://"):
        url = urlparse(value)
        if url.hostname not in {"t.me", "www.t.me"} or url.query or url.fragment:
            raise ValueError("Используй @канал, https://t.me/канал или числовой ID канала")
        value = url.path.strip("/")
    value = value.removeprefix("@")
    if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{4,31}", value):
        return "@" + value.casefold()
    if re.fullmatch(r"-100\d{1,16}", value) and abs(int(value)) < 2**63:
        return value
    raise ValueError("Нужен публичный @канал или ID -100…; ссылки на посты и приглашения не подходят")


async def watch_state(user_id: int) -> dict:
    try:
        state = json.loads(await repo.get_state(user_id, STATE_KEY, '{"channels":{}}'))
    except (TypeError, ValueError) as exc:
        raise RuntimeError("Настройки Telegram Watch повреждены; требуется проверка, данные сохранены") from exc
    if not isinstance(state, dict) or not isinstance(state.get("channels"), dict):
        raise RuntimeError("Настройки Telegram Watch повреждены; данные сохранены")
    for key, item in state["channels"].items():
        if not isinstance(item, dict) or item.get("scope") not in {"career", "relocation", "both"}:
            raise RuntimeError("Настройки Telegram Watch повреждены; данные сохранены")
        try:
            valid_key = channel_key(key) == key
        except (ValueError, TypeError):
            valid_key = False
        stats = item.get("stats", {})
        if (not valid_key or not isinstance(item.get("enabled"), bool)
                or not isinstance(stats, dict)
                or any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in stats.values())):
            raise RuntimeError("Настройки Telegram Watch повреждены; данные сохранены")
    return state


async def _save(user_id: int, state: dict) -> None:
    await repo.set_state(user_id, STATE_KEY, json.dumps(state, ensure_ascii=False))


async def change_subscription(user_id: int, action: str, target: str, scope: str = "both") -> dict:
    key = channel_key(target)
    if scope not in {"career", "relocation", "both"}:
        raise ValueError("Профиль: career, relocation или both")
    if action not in {"add", "remove", "on", "off"}:
        raise ValueError("Действия: add, remove, on, off")
    async with _LOCKS.setdefault(user_id, asyncio.Lock()):
        state = await watch_state(user_id)
        channels = state["channels"]
        if action == "add":
            if key not in channels and len(channels) >= MAX_CHANNELS:
                raise ValueError(f"Максимум {MAX_CHANNELS} каналов")
            item = channels.setdefault(key, {"stats": {name: 0 for name in _COUNTERS}})
            item.update(enabled=True, scope=scope)
        else:
            if key not in channels:
                raise ValueError("Канал не найден в подписках")
            if action == "remove":
                # Keep persisted seen records; re-add must not replay old alerts.
                del channels[key]
            else:
                channels[key]["enabled"] = action == "on"
        await _save(user_id, state)
        return state


def render_subscriptions(state: dict) -> str:
    lines = ["📡 Telegram Channel Watch", "Новые посты через Bot API; история каналов не сканируется."]
    for key, item in state["channels"].items():
        stats = item.get("stats", {})
        lines.append(f"{'✅' if item.get('enabled') else '⏸'} {key} · {item.get('scope', 'both')}")
        lines.append(f"Постов: {stats.get('posts', 0)} · Good-оценок: {stats.get('qualified', 0)} · Stretch-оценок: {stats.get('stretch', 0)} · уведомлений: {stats.get('notified', 0)} · повторов: {stats.get('replays', 0)} · ошибок: {stats.get('errors', 0)}")
        if item.get("last_post_at"):
            lines.append("Последний принятый пост: " + item["last_post_at"])
    if not state["channels"]:
        lines.append("Подписок пока нет.")
    lines.extend(["", "/channels add @канал [career|relocation|both]", "/channels on|off|remove @канал", "Подписка сама не добавляет бота в канал. Для автоприёма добавьте бота в канал; иначе пересылайте посты вручную."])
    return "\n".join(lines)


async def consume_channel_post(bot, *, chat_id: int, username: str | None, message_id: int, text: str) -> dict:
    from app.services import ingest_and_match

    if not text.strip():
        return {"subscribers": 0}
    keys = {str(chat_id)}
    if username:
        keys.add("@" + username.casefold())
    identity = f"channel:{chat_id}:{message_id}"
    url = f"https://t.me/{username}/{message_id}" if username else ""
    normalized = parse_telegram_job(text, source_ref=identity, source_url=url)
    normalized.raw.update(channel_id=chat_id, channel_username=username, message_id=message_id)
    subscribers = 0
    for user in await repo.list_active_users():
        if await repo.get_state(user.id, "paused", "false") == "true":
            continue
        async with _LOCKS.setdefault(user.id, asyncio.Lock()):
            try:
                state = await watch_state(user.id)
            except RuntimeError:
                log.warning("Telegram watch configuration unavailable; subscriber skipped")
                continue
            items = [(key, item) for key, item in state["channels"].items()
                     if key in keys and item.get("enabled")]
            if not items:
                continue
            # A username and its numeric ID may both be subscribed: union scopes,
            # process each search once and account the same delivery per alias.
            scopes = {item.get("scope", "both") for _, item in items}
            profile = await repo.active_profile(user.id)
            searches = await repo.list_search_profiles(profile.id) if profile else []
            searches = [search for search in searches if source_enabled(search.settings, "telegram")
                        and ("both" in scopes or search.kind in scopes
                             or (search.kind == "employment" and
                                 ("relocation" if search_strategy(search.settings) == "relocation_first" else "career") in scopes))]
            if not searches:
                continue
            subscribers += 1
            if await repo.message_seen(user.id, identity, "telegram_watch"):
                for _, item in items:
                    item.setdefault("stats", {})["replays"] = item.get("stats", {}).get("replays", 0) + 1
                await _save(user.id, state)
                continue
            totals = {name: 0 for name in _COUNTERS}
            try:
                for search in searches:
                    result = await ingest_and_match(bot, normalized, only_user_id=user.id,
                                                    only_search_profile_id=search.id)
                    for name in totals:
                        totals[name] += result.get(name, 0)
                await repo.mark_message_seen(user.id, identity, str(chat_id), "", "telegram_watch")
            except Exception as exc:
                log.warning("Telegram watch processing failed (%s); retry remains available", type(exc).__name__)
                for _, item in items:
                    stats = item.setdefault("stats", {})
                    stats["errors"] = stats.get("errors", 0) + 1
                await _save(user.id, state)
                # No seen record on failure. Existing pipeline suppresses repeat
                # notifications if a retry follows partial profile success.
                continue
            totals["posts"] = 1
            for _, item in items:
                stats = item.setdefault("stats", {})
                for name, amount in totals.items():
                    stats[name] = stats.get(name, 0) + amount
                item["last_post_at"] = datetime.now(timezone.utc).isoformat()
            await _save(user.id, state)
    return {"subscribers": subscribers}
