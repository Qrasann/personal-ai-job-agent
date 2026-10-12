from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal


def source_datetime(value: object) -> datetime | None:
    """Parse explicit source timestamps without guessing a local timezone.

    Himalayas' primary references describe both epoch seconds and milliseconds;
    its API reference also describes timezone-aware ISO dates. Missing, malformed
    and timezone-less values remain unknown rather than becoming local dates.
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        try:
            timestamp = float(value)
            if not math.isfinite(timestamp) or timestamp <= 0:
                return None
            if timestamp > 100_000_000_000:
                timestamp /= 1000
            return datetime.fromtimestamp(timestamp, tz=UTC)
        except (OverflowError, OSError, ValueError):
            return None
    if not isinstance(value, str) or len(value) > 64:
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            return None
        return parsed.astimezone(UTC)
    except (OverflowError, ValueError):
        return None


def listing_expiry_metadata(value: object) -> dict:
    """Preserve a bounded source field separately from employer deadlines."""
    parsed = source_datetime(value)
    source_value = None
    if isinstance(value, str):
        source_value = value[:128]
    elif not isinstance(value, bool) and isinstance(value, (int, float)):
        try:
            if math.isfinite(float(value)):
                source_value = value
        except OverflowError:
            pass
    return {
        "source_field": "expiryDate",
        "source_value": source_value,
        "expires_at": parsed.isoformat() if parsed else None,
    }


@dataclass(frozen=True, slots=True)
class VacancyAvailability:
    status: Literal["unknown", "expired", "not_expired"]
    expires_at: datetime | None


def vacancy_availability(raw: dict | None, *, now: datetime | None = None) -> VacancyAvailability:
    """Assess source listing expiry only, never the employer's hiring status."""
    metadata = raw.get("availability") if isinstance(raw, dict) else None
    parsed = source_datetime(metadata.get("expires_at")) if isinstance(metadata, dict) else None
    if parsed is None:
        return VacancyAvailability("unknown", None)
    current = now if now is not None else datetime.now(UTC)
    if current.tzinfo is None or current.utcoffset() is None:
        raise ValueError("Availability comparison requires a timezone-aware current time")
    status = "expired" if parsed <= current.astimezone(UTC) else "not_expired"
    return VacancyAvailability(status, parsed)


def vacancy_availability_lines(raw: dict | None, *, now: datetime | None = None) -> list[str]:
    """Return safe Telegram text with source expiry and its practical limits."""
    availability = vacancy_availability(raw, now=now)
    if availability.expires_at is None:
        return ["📅 Срок размещения: не указан источником"]
    timestamp = availability.expires_at.strftime("%d.%m.%Y %H:%M UTC")
    if availability.status == "expired":
        line = f"⌛ Срок размещения по источнику истёк: {timestamp}"
    else:
        line = f"📅 Срок размещения по источнику: {timestamp}"
    return [line, "Статус найма и дедлайн отклика уточняйте у работодателя."]
