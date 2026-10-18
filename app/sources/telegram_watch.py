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
from app.sources.telegram_post import explicit_non_vacancy

STATE_KEY = "telegram_channel_watch_v1"
MAX_CHANNELS = 50
MAX_PENDING = 100
_COUNTERS = ("posts", "received", "vacancy_candidates", "non_vacancy", "processed", "qualified", "stretch", "filtered", "notified", "duplicate", "replays", "errors")
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
    if not isinstance(state.get("pending", {}), dict):
        raise RuntimeError("Очередь Telegram Watch повреждена; данные сохранены")
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
    lines = ["📡 Telegram Channel Watch", "Новые посты: Bot API или включённый локальный клиент; старая история каналов не сканируется."]
    for key, item in state["channels"].items():
        stats = item.get("stats", {})
        lines.append(f"{'✅' if item.get('enabled') else '⏸'} {key} · {item.get('scope', 'both')}")
        lines.append(f"Получено: {stats.get('received', 0)} · обработано: {stats.get('posts', 0)} · возможно вакансий: {stats.get('vacancy_candidates', 0)} · не вакансий: {stats.get('non_vacancy', 0)}")
        lines.append(f"Оценки: Good {stats.get('qualified', 0)} · Stretch {stats.get('stretch', 0)} · отсеиваний: {stats.get('filtered', 0)} · дубли оценок: {stats.get('duplicate', 0)}")
        lines.append(f"Уведомлений: {stats.get('notified', 0)} · повторов: {stats.get('replays', 0)} · ошибок: {stats.get('errors', 0)}")
        if item.get("last_post_at"):
            lines.append("Последний принятый пост: " + item["last_post_at"])
    if not state["channels"]:
        lines.append("Подписок пока нет.")
    lines.append(f"Ожидают повторной обработки: {len(state.get('pending', {}))}")
    if state.get("retry_overflow"):
        lines.append(f"Ошибок вне переполненной очереди: {state['retry_overflow']}")
    lines.extend(["", "/channels add @канал [career|relocation|both]", "/channels on|off|remove @канал", "/channels retry — повторить до 5 неуспешных постов", "Подписка сама не добавляет бота в канал. Для Bot API добавьте бота в канал; другой вариант — отдельный локальный клиент для разрешённых каналов или ручная пересылка."])
    return "\n".join(lines)


async def consume_forwarded_job(bot, user_id: int, job) -> bool:
    """Share replay coordination with automatic channel delivery."""
    from app.services import ingest_and_match
    identity = job.raw.get("source_ref", "")
    channel_origin = identity.startswith("channel:")
    async with _LOCKS.setdefault(user_id, asyncio.Lock()):
        if channel_origin and await repo.message_seen(user_id, identity, "telegram_watch"):
            return False
        result = await ingest_and_match(bot, job, only_user_id=user_id)
        if channel_origin and result.get("processed", 0):
            await repo.mark_message_seen(user_id, identity, identity.split(":")[1], "", "telegram_watch")
        return True


async def consume_channel_post(bot, *, chat_id: int, username: str | None, message_id: int, text: str,
                               only_user_id: int | None = None, published_at: datetime | None = None) -> dict:
    from app.services import ingest_and_match

    if not text.strip():
        return {"subscribers": 0}
    if username and not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{4,31}", username):
        username = None
    keys = {str(chat_id)}
    if username:
        keys.add("@" + username.casefold())
    identity = f"channel:{chat_id}:{message_id}"
    url = f"https://t.me/{username}/{message_id}" if username else ""
    normalized = parse_telegram_job(text, source_ref=identity, source_url=url)
    normalized.raw.update(channel_id=chat_id, channel_username=username, message_id=message_id)
    if published_at is not None:
        if published_at.tzinfo is None:
            raise ValueError("Telegram publication date must include timezone")
        normalized.published_at = published_at.astimezone(timezone.utc).isoformat()
        normalized.raw["telegram_published_at"] = normalized.published_at
    subscribers = 0
    for user in await repo.list_active_users():
        if only_user_id is not None and user.id != only_user_id:
            continue
        try:
            if await repo.get_state(user.id, "paused", "false") == "true":
                continue
        except Exception as exc:
            log.warning("Telegram watch pause state unavailable for subscriber %s (%s); skipped",
                        user.id, type(exc).__name__)
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
            try:
                profile = await repo.active_profile(user.id)
                searches = await repo.list_search_profiles(profile.id) if profile else []
            except Exception as exc:
                log.warning("Telegram watch search profiles unavailable for subscriber %s (%s); skipped",
                            user.id, type(exc).__name__)
                continue
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
                state.get("pending", {}).pop(identity, None)
                await _save(user.id, state)
                continue
            # A failed first attempt belongs to received yield too. Pending
            # retries must not inflate the number of distinct received posts.
            if identity not in state.get("pending", {}):
                for _, item in items:
                    stats = item.setdefault("stats", {})
                    stats["received"] = stats.get("received", 0) + 1
            if explicit_non_vacancy(text):
                try:
                    await repo.mark_message_seen(user.id, identity, str(chat_id), "", "telegram_watch")
                except Exception as exc:
                    log.warning("Telegram watch rejected-post marker failed (%s)", type(exc).__name__)
                    for _, item in items:
                        stats = item.setdefault("stats", {})
                        stats["errors"] = stats.get("errors", 0) + 1
                    await _save(user.id, state)
                    continue
                for _, item in items:
                    stats = item.setdefault("stats", {})
                    for name in ("posts", "non_vacancy", "filtered"):
                        stats[name] = stats.get(name, 0) + 1
                    item["last_post_at"] = datetime.now(timezone.utc).isoformat()
                await _save(user.id, state)
                continue
            totals = {name: 0 for name in _COUNTERS}
            try:
                for search in searches:
                    result = await ingest_and_match(bot, normalized, only_user_id=user.id,
                                                    only_search_profile_id=search.id)
                    for name in totals:
                        totals[name] += result.get(name, 0)
                if not totals["processed"]:
                    await _save(user.id, state)
                    continue
                await repo.mark_message_seen(user.id, identity, str(chat_id), "", "telegram_watch")
            except Exception as exc:
                log.warning("Telegram watch processing failed (%s); retry remains available", type(exc).__name__)
                for _, item in items:
                    stats = item.setdefault("stats", {})
                    stats["errors"] = stats.get("errors", 0) + 1
                pending = state.setdefault("pending", {})
                if identity in pending or len(pending) < MAX_PENDING:
                    # Rotate failures to avoid starving later queued posts.
                    pending.pop(identity, None)
                    pending[identity] = {"chat_id": chat_id, "username": username,
                                         "message_id": message_id, "text": text[:16384],
                                         "published_at": normalized.published_at}
                else:
                    state["retry_overflow"] = state.get("retry_overflow", 0) + 1
                    log.warning("Telegram watch retry queue full; failure counted outside queue")
                await _save(user.id, state)
                # No seen record on failure. Existing pipeline suppresses repeat
                # notifications if a retry follows partial profile success.
                continue
            totals["posts"] = 1
            totals["vacancy_candidates"] = 1
            state.get("pending", {}).pop(identity, None)
            for _, item in items:
                stats = item.setdefault("stats", {})
                for name, amount in totals.items():
                    stats[name] = stats.get(name, 0) + amount
                item["last_post_at"] = datetime.now(timezone.utc).isoformat()
            await _save(user.id, state)
    return {"subscribers": subscribers}


async def retry_pending(bot, *, user_id: int | None = None, limit: int = 5) -> int:
    """Bounded retry of previously subscribed deliveries, never history search."""
    attempted = 0
    for user in await repo.list_active_users():
        if user_id is not None and user.id != user_id:
            continue
        try:
            if await repo.get_state(user.id, "paused", "false") == "true":
                continue
            async with _LOCKS.setdefault(user.id, asyncio.Lock()):
                state = await watch_state(user.id)
                pending = list(state.get("pending", {}).values())
                enabled = {key for key, item in state["channels"].items() if item.get("enabled")}
        except Exception as exc:
            log.warning("Telegram watch retry state unavailable for subscriber %s (%s); skipped",
                        user.id, type(exc).__name__)
            continue
        for event in pending:
            if attempted >= min(max(limit, 0), 10):
                return attempted
            if not isinstance(event, dict) or not isinstance(event.get("chat_id"), int) or not isinstance(event.get("message_id"), int) or not isinstance(event.get("text"), str):
                log.warning("Telegram watch invalid retry entry preserved")
                continue
            keys = {str(event["chat_id"]), "@" + str(event.get("username") or "").casefold()}
            if not enabled & keys:
                continue
            attempted += 1
            published_at = None
            if event.get("published_at"):
                try:
                    published_at = datetime.fromisoformat(event["published_at"])
                    if published_at.tzinfo is None:
                        raise ValueError("missing timezone")
                except (TypeError, ValueError):
                    log.warning("Telegram watch invalid publication date preserved for retry")
                    continue
            await consume_channel_post(bot, chat_id=event["chat_id"], username=event.get("username"),
                                       message_id=event["message_id"], text=event["text"], only_user_id=user.id,
                                       published_at=published_at)
    return attempted


async def retry_telegram_watch(bot) -> None:
    await retry_pending(bot)
