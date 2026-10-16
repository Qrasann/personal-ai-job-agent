"""Durable at-least-once job-alert delivery using existing RuntimeState rows.

Telegram has no provider idempotency key for sendMessage; if a response is lost,
a retry may create a second message. We prefer a possible duplicate over a
silently lost job, while fencing concurrent workers through PostgreSQL locks.
"""
from __future__ import annotations

import json
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import and_, case, cast, func, select, text
from sqlalchemy.dialects.postgresql import JSONB

from app.database.db import SessionLocal
from app.database.models import JobMatch, RuntimeState, User

_KEY_PREFIX = "jobnotify:"
LEASE_SECONDS = 120
RETRY_BASE_SECONDS = 60
RETRY_MAX_SECONDS = 3600
JOURNAL_EVENTS = 25


def _utc(now: datetime | None = None) -> datetime:
    now = now or datetime.now(UTC)
    return now.replace(tzinfo=UTC) if now.tzinfo is None else now.astimezone(UTC)


def _stamp(now: datetime) -> str:
    return now.isoformat(timespec="microseconds")


def _read(value: str) -> dict:
    try:
        data = json.loads(value)
    except (ValueError, TypeError):
        return {}
    return data if isinstance(data, dict) else {}


def _event(row: dict, kind: str, at: str, **fields) -> None:
    history = list(row.get("events") or [])
    history.append({"kind": kind, "at": at, **fields})
    row["events"] = history[-JOURNAL_EVENTS:]


async def claim_job_notification(
    *, user_id: int, match_id: int, payload: dict | None = None,
    now: datetime | None = None,
) -> dict | None:
    """Atomically claim a due notification; persist claim before network I/O.

    A per-user row lock serializes first insert across processes. An existing
    payload is immutable, so retries deliver the original observed vacancy.
    """
    now = _utc(now)
    stamp = _stamp(now)
    key = f"{_KEY_PREFIX}{match_id}"
    async with SessionLocal() as session:
        owner = await session.scalar(
            select(User).where(
                User.id == user_id, User.is_active.is_(True),
                User.deleted_at.is_(None),
            ).with_for_update()
        )
        if owner is None:
            return None
        match = await session.scalar(
            select(JobMatch).where(
                JobMatch.id == match_id, JobMatch.user_id == user_id,
            ).with_for_update()
        )
        if match is None or match.status != "new":
            return None
        entry = await session.scalar(
            select(RuntimeState).where(
                RuntimeState.user_id == user_id, RuntimeState.key == key,
            ).with_for_update()
        )
        state = _read(entry.value) if entry else {}
        if entry and not state:
            # Malformed persisted journal must not be silently overwritten.
            return None
        if state.get("status") == "sent":
            return None
        if entry and state.get("status") not in {"sending", "retry"}:
            return None
        if entry and state.get("next_attempt_at", "") > stamp:
            return None
        if entry:
            delivery_payload = state.get("payload")
        else:
            delivery_payload = payload
        if not isinstance(delivery_payload, dict) or not delivery_payload.get("text"):
            return None
        if not isinstance(delivery_payload.get("match_id"), int) or delivery_payload["match_id"] != match_id:
            return None
        attempts = int(state.get("attempts") or 0) + 1
        token = secrets.token_hex(12)
        state.update(
            status="sending", attempts=attempts, token=token,
            payload=delivery_payload,
            created_at=state.get("created_at") or stamp,
            updated_at=stamp,
            next_attempt_at=_stamp(now + timedelta(seconds=LEASE_SECONDS)),
        )
        _event(state, "claimed", stamp, attempt=attempts)
        if entry:
            entry.value = json.dumps(state, ensure_ascii=False, separators=(",", ":"))
        else:
            session.add(RuntimeState(
                user_id=user_id, key=key,
                value=json.dumps(state, ensure_ascii=False, separators=(",", ":")),
            ))
        await session.commit()
        return {
            "user_id": user_id, "match_id": match_id, "token": token,
            "chat_id": owner.telegram_chat_id, "payload": delivery_payload,
            "attempt": attempts,
        }


async def settle_job_notification(
    *, user_id: int, match_id: int, token: str,
    delivered: bool, message_id: int | None = None,
    now: datetime | None = None,
) -> bool:
    """Fence stale senders; atomically mark delivered and JobMatch notified.

    Failed sends retry with exponential backoff. A lost DB acknowledgment after
    Telegram success leaves the sending lease to expire and may cause a duplicate.
    """
    now = _utc(now)
    stamp = _stamp(now)
    async with SessionLocal() as session:
        owner = await session.scalar(
            select(User).where(User.id == user_id).with_for_update()
        )
        if owner is None:
            return False
        entry = await session.scalar(
            select(RuntimeState).where(
                RuntimeState.user_id == user_id,
                RuntimeState.key == f"{_KEY_PREFIX}{match_id}",
            ).with_for_update()
        )
        if not entry:
            return False
        state = _read(entry.value)
        if state.get("token") != token or state.get("status") != "sending":
            return False
        if delivered:
            match = await session.scalar(
                select(JobMatch).where(
                    JobMatch.id == match_id, JobMatch.user_id == user_id,
                ).with_for_update()
            )
            if match is not None and match.status == "new":
                match.status = "notified"
            state.update(status="sent", next_attempt_at=None, delivered_at=stamp)
            if isinstance(message_id, int):
                state["telegram_message_id"] = message_id
            _event(state, "sent", stamp, attempt=state["attempts"])
        else:
            attempts = int(state.get("attempts") or 1)
            delay = min(RETRY_BASE_SECONDS * 2 ** min(attempts - 1, 6), RETRY_MAX_SECONDS)
            state.update(status="retry", next_attempt_at=_stamp(now + timedelta(seconds=delay)))
            _event(state, "retry_scheduled", stamp, attempt=attempts, delay_seconds=delay)
        state["updated_at"] = stamp
        entry.value = json.dumps(state, ensure_ascii=False, separators=(",", ":"))
        await session.commit()
        return True


async def due_job_notifications(
    *, user_id: int | None = None, limit: int = 100,
    now: datetime | None = None,
) -> list[tuple[int, int]]:
    """Query only due rows; completed notifications never enter the retry scan."""
    now = _stamp(_utc(now))
    # RuntimeState contains unrelated plain-text settings, and a damaged
    # jobnotify row may contain malformed JSON. A WHERE predicate does not
    # guarantee evaluation order; guard the JSONB cast inside SQL CASE so one
    # corrupted journal entry cannot block every other due notification.
    # pg_input_is_valid() is available on the project's PostgreSQL 16 baseline.
    prefix = RuntimeState.key.like(f"{_KEY_PREFIX}%")
    valid_notification_json = and_(
        prefix,
        func.pg_input_is_valid(RuntimeState.value, text("'jsonb'::regtype")),
    )
    data = case(
        (valid_notification_json, cast(RuntimeState.value, JSONB)),
        else_=cast("{}", JSONB),
    )
    stmt = (
        select(RuntimeState.user_id, RuntimeState.key)
        .join(User, User.id == RuntimeState.user_id)
        .where(
            prefix,
            User.is_active.is_(True), User.deleted_at.is_(None),
            data["status"].astext.in_(("retry", "sending")),
            data["next_attempt_at"].astext <= now,
        )
        .order_by(RuntimeState.id)
        .limit(max(1, min(int(limit), 500)))
    )
    if user_id is not None:
        stmt = stmt.where(RuntimeState.user_id == user_id)
    async with SessionLocal() as session:
        result = await session.execute(stmt)
        out = []
        for owner_id, key in result:
            tail = key.removeprefix(_KEY_PREFIX)
            if tail.isdecimal():
                out.append((owner_id, int(tail)))
        return out


async def recent_job_notification_journal(user_id: int, *, limit: int = 10) -> list[dict]:
    """Expose delivery metadata only; never print job text or saved credentials."""
    async with SessionLocal() as session:
        rows = await session.scalars(
            select(RuntimeState)
            .where(
                RuntimeState.user_id == user_id,
                RuntimeState.key.like(f"{_KEY_PREFIX}%"),
            )
            .order_by(RuntimeState.id.desc())
            .limit(max(1, min(int(limit), 50)))
        )
        out = []
        for entry in rows:
            data = _read(entry.value)
            if data:
                out.append({
                    "match_id": entry.key.removeprefix(_KEY_PREFIX),
                    "status": data.get("status", "unknown"),
                    "attempts": data.get("attempts", 0),
                    "next_attempt_at": data.get("next_attempt_at"),
                    "delivered_at": data.get("delivered_at"),
                    "telegram_message_id": data.get("telegram_message_id"),
                })
        return out
