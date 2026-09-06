from datetime import UTC, datetime


def utcnow_naive() -> datetime:
    """Return current UTC time compatible with TIMESTAMP WITHOUT TIME ZONE."""
    return datetime.now(UTC).replace(tzinfo=None)
