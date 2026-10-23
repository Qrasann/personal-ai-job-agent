from __future__ import annotations

from datetime import UTC, datetime


def parse_reminder_due(value: str, *, now: datetime | None = None) -> datetime:
    """Parse an explicit-offset ISO deadline and return naive UTC for storage."""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Срок должен быть ISO datetime с timezone, например 2026-11-01T09:00+03:00.") from exc
    if parsed.tzinfo is None:
        raise ValueError("Укажи timezone в сроке, например +03:00 или Z.")
    due = parsed.astimezone(UTC)
    observed = (now or datetime.now(UTC)).astimezone(UTC)
    if due <= observed:
        raise ValueError("Срок напоминания должен быть в будущем.")
    return due.replace(tzinfo=None)
