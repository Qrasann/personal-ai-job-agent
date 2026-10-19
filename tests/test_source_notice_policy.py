import json
from datetime import UTC, datetime, timedelta

import pytest

from app.search.source_summary import aggregate_source
from app.sources.notice_policy import (
    plan_source_notices,
    render_source_daily_digest,
    render_source_state_notice,
)


NOW = datetime(2026, 10, 19, 12, 0, tzinfo=UTC)


def failed(name="Source", code="NETWORK_CONNECT_ERROR") -> dict:
    return {
        "status": "failed", "name": name, "found": 0, "processed": 0,
        "diagnostics": [{"code": code, "action": "continue"}],
    }


def partial(name="Source", *, found=4, code="NETWORK_CONNECT_TIMEOUT", failed_count=1, attempts=4):
    return {
        "status": "partial", "name": name, "found": found, "processed": found,
        "attempts": attempts, "failed": failed_count,
        "successful_attempts": attempts - failed_count,
        "partial_failures": failed_count,
        "diagnostics": [{"code": code, "action": "continue"}],
    }


@pytest.mark.parametrize(
    ("source", "label", "first_code", "next_code"),
    [
        ("hh", "HeadHunter", "HTTP_403_FORBIDDEN", "NETWORK_CONNECT_TIMEOUT"),
        ("jobbank", "Job Bank Canada", "NETWORK_CONNECT_TIMEOUT", "NETWORK_CONNECT_ERROR"),
        ("remoteok", "Remote OK", "NETWORK_CONNECT_TIMEOUT", "NETWORK_TRANSPORT_FAILED"),
        ("greenhouse", "Greenhouse / Lineate", "NETWORK_CONNECT_TIMEOUT", "NETWORK_CONNECT_ERROR"),
    ],
)
def test_critical_failures_across_sources_alert_once_and_ignore_error_code_churn(
    source, label, first_code, next_code,
):
    first, state = plan_source_notices({source: failed(label, first_code)}, "", now=NOW)
    changed_code, state = plan_source_notices(
        {source: failed(label, next_code)}, state, now=NOW + timedelta(minutes=15),
    )
    too_soon, state = plan_source_notices(
        {source: failed(label, "NETWORK_READ_TIMEOUT")}, state, now=NOW + timedelta(hours=12),
    )
    daily, state = plan_source_notices(
        {source: failed(label, "NETWORK_CONNECT_ERROR")}, state, now=NOW + timedelta(hours=24),
    )
    quiet, _ = plan_source_notices(
        {source: failed(label, "NETWORK_CONNECT_TIMEOUT")}, state, now=NOW + timedelta(hours=25),
    )

    assert [(item["kind"], item["state"]) for item in first] == [("critical", "unavailable")]
    assert changed_code == [] and too_soon == []
    assert [item["kind"] for item in daily] == ["daily"]
    assert quiet == []
    assert "недоступен" in render_source_state_notice(first[0], failed(label, first_code))


def test_successful_fallback_from_any_provider_is_quiet_but_diagnostic_is_retained():
    info = {
        "status": "success", "name": "HeadHunter", "found": 4, "processed": 4,
        "diagnostics": [{"code": "HTTP_403_FORBIDDEN", "action": "fallback"}],
    }
    notices, state = plan_source_notices({"hh": info}, "", now=NOW)
    repeated, _ = plan_source_notices({"hh": info}, state, now=NOW + timedelta(days=2))

    assert notices == []
    assert repeated == []
    assert "HTTP_403_FORBIDDEN" in str(info["diagnostics"])

    generic = {**info, "name": "Other provider"}
    generic_notices, _ = plan_source_notices({"other": generic}, "", now=NOW)
    assert generic_notices == []


def test_limited_partial_results_are_quiet_until_one_daily_summary():
    sources = {"jobbank": partial("Job Bank Canada", failed_count=1, attempts=5)}
    first, state = plan_source_notices(sources, "", now=NOW)
    repeated, state = plan_source_notices(sources, state, now=NOW + timedelta(minutes=15))
    daily, state = plan_source_notices(sources, state, now=NOW + timedelta(hours=24))
    too_soon, _ = plan_source_notices(sources, state, now=NOW + timedelta(hours=25))

    assert first == []
    assert repeated == []
    assert [item["kind"] for item in daily] == ["daily"]
    assert too_soon == []
    text = render_source_daily_digest(daily, sources)
    assert "Ежедневная сводка" in text
    assert "Job Bank Canada" in text
    assert "NETWORK_CONNECT_TIMEOUT" not in text


def test_material_partial_loss_alerts_and_network_code_changes_do_not_realert():
    first, state = plan_source_notices(
        {"remoteok": partial("Remote OK", found=2, failed_count=2, attempts=3)},
        "", now=NOW,
    )
    code_change, state = plan_source_notices(
        {"remoteok": partial("Remote OK", found=2, code="NETWORK_CONNECT_ERROR",
                             failed_count=2, attempts=3)},
        state, now=NOW + timedelta(minutes=15),
    )
    recovered, state = plan_source_notices(
        {"remoteok": {"status": "success", "name": "Remote OK", "found": 3,
                      "processed": 3, "diagnostics": []}},
        state, now=NOW + timedelta(minutes=30),
    )

    assert [item["kind"] for item in first] == ["issue"]
    assert code_change == []
    assert [item["kind"] for item in recovered] == ["recovered"]
    assert "восстановился" in render_source_state_notice(recovered[0], {"name": "Remote OK"})


def test_multi_profile_attempts_are_aggregated_to_one_provider_notice():
    sources = {}
    aggregate_source(sources, "greenhouse", failed("Greenhouse / Lineate"))
    aggregate_source(sources, "greenhouse", {
        "status": "success", "name": "Greenhouse / Lineate", "found": 3, "processed": 3,
        "diagnostics": [],
    })
    notices, state = plan_source_notices(sources, "", now=NOW)
    next_scan, _ = plan_source_notices(sources, state, now=NOW + timedelta(minutes=15))

    assert len(sources) == 1
    assert sources["greenhouse"]["attempts"] == 2
    assert [item["kind"] for item in notices] == ["issue"]
    assert notices[0]["source_id"] == "greenhouse"
    assert next_scan == []


def test_multiple_daily_source_issues_render_as_one_compact_digest():
    sources = {
        "jobbank": partial("Job Bank Canada"),
        "remoteok": partial("Remote OK"),
    }
    _, state = plan_source_notices(sources, "", now=NOW)
    notices, _ = plan_source_notices(sources, state, now=NOW + timedelta(hours=24))

    assert [item["kind"] for item in notices] == ["daily", "daily"]
    text = render_source_daily_digest(notices, sources)
    assert "Job Bank Canada, Remote OK" in text
    assert "ошибка" not in text.casefold()


def test_suppression_state_is_persistable_and_reads_legacy_v1():
    first, encoded = plan_source_notices({"jobbank": failed("Job Bank")}, "", now=NOW)
    payload = json.loads(encoded)
    assert payload["version"] == 2
    assert first[0]["kind"] == "critical"

    legacy = json.dumps({
        "version": 1,
        "sources": {
            "jobbank": {
                "signature": "unavailable|NETWORK_CONNECT_ERROR",
                "state": "unavailable",
                "codes": ["NETWORK_CONNECT_ERROR"],
                "occurrences": 1,
                "first_seen_at": NOW.isoformat(),
                "last_seen_at": NOW.isoformat(),
                "last_notified_at": NOW.isoformat(),
            }
        },
    })
    no_duplicate, migrated = plan_source_notices(
        {"jobbank": failed("Job Bank", "NETWORK_CONNECT_TIMEOUT")},
        legacy,
        now=NOW + timedelta(minutes=15),
    )
    assert no_duplicate == []
    assert json.loads(migrated)["version"] == 2
