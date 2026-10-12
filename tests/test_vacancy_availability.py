from datetime import UTC, datetime

import pytest

from app.domain.vacancy_availability import (
    listing_expiry_metadata,
    source_datetime,
    vacancy_availability,
    vacancy_availability_lines,
)


NOW = datetime(2026, 10, 13, 12, tzinfo=UTC)


@pytest.mark.parametrize("value", [
    1893456000, 1893456000000,
    "2030-01-01T00:00:00Z", "2030-01-01T04:00:00+04:00",
])
def test_source_dates_normalize_documented_formats_to_utc(value):
    assert source_datetime(value) == datetime(2030, 1, 1, tzinfo=UTC)


@pytest.mark.parametrize("value", [
    None, True, False, 0, -1, float("nan"), float("inf"), 10**400,
    [], {}, "not a date", "2026-10-20", "2026-10-20T12:00:00",
    "2026-10-40T12:00:00Z", "1" * 200,
])
def test_missing_malformed_or_ambiguous_source_dates_remain_unknown(value):
    assert source_datetime(value) is None
    metadata = listing_expiry_metadata(value)
    assert metadata["expires_at"] is None
    availability = vacancy_availability({"availability": metadata}, now=NOW)
    assert availability.status == "unknown"
    assert availability.expires_at is None


def test_listing_expiry_preserves_bounded_source_evidence_without_inventing_deadlines():
    metadata = listing_expiry_metadata("2030-01-01T04:00:00+04:00")

    assert metadata == {
        "source_field": "expiryDate",
        "source_value": "2030-01-01T04:00:00+04:00",
        "expires_at": "2030-01-01T00:00:00+00:00",
    }
    assert "application_deadline" not in metadata
    assert "start_date" not in metadata
    assert len(listing_expiry_metadata("x" * 500)["source_value"]) == 128


@pytest.mark.parametrize("raw", [None, {}, {"published_at": "2026-10-13T12:00:00Z"},
                                     {"availability": "2026-10-20T12:00:00Z"}])
def test_publication_without_valid_expiry_cannot_confirm_current_hiring(raw):
    assert vacancy_availability(raw, now=NOW).status == "unknown"
    assert vacancy_availability_lines(raw, now=NOW) == [
        "📅 Срок размещения: не указан источником",
    ]


@pytest.mark.parametrize(("expiry", "status", "label"), [
    ("2026-10-12T12:00:00Z", "expired", "истёк"),
    ("2026-10-13T12:00:00Z", "expired", "истёк"),
    ("2026-10-14T12:00:00Z", "not_expired", "Срок размещения по источнику:"),
])
def test_expiry_is_evaluated_at_render_time_with_employer_status_separate(expiry, status, label):
    raw = {"availability": listing_expiry_metadata(expiry)}

    assert vacancy_availability(raw, now=NOW).status == status
    lines = vacancy_availability_lines(raw, now=NOW)
    assert label in lines[0]
    assert lines[0].endswith("12:00 UTC")
    assert lines[1] == "Статус найма и дедлайн отклика уточняйте у работодателя."
    assert "открыта" not in " ".join(lines)
    assert "закрыта" not in " ".join(lines)


def test_cached_listing_expiry_is_reassessed_without_mutating_stored_evidence():
    metadata = listing_expiry_metadata("2026-10-14T12:00:00Z")
    raw = {"availability": metadata.copy()}

    assert vacancy_availability(raw, now=NOW).status == "not_expired"
    assert vacancy_availability(raw, now=datetime(2026, 10, 15, tzinfo=UTC)).status == "expired"
    assert raw["availability"] == metadata


def test_availability_comparison_does_not_guess_timezone_of_naive_current_time():
    raw = {"availability": listing_expiry_metadata("2026-10-14T12:00:00Z")}
    with pytest.raises(ValueError, match="timezone-aware"):
        vacancy_availability(raw, now=datetime(2026, 10, 13))
