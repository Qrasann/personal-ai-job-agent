from datetime import UTC, datetime, timedelta

from app.sources.notice_policy import plan_source_notices, render_source_state_notice


NOW = datetime(2026, 10, 18, 12, 0, tzinfo=UTC)


def failed(code="NETWORK_CONNECT_ERROR") -> dict:
    return {
        "status": "failed", "name": "Remote OK", "found": 0, "processed": 0,
        "diagnostics": [{"code": code, "action": "continue"}],
    }


def test_identical_source_failures_are_suppressed_then_summarized() -> None:
    first, state = plan_source_notices({"remoteok": failed()}, "", now=NOW)
    second, state = plan_source_notices({"remoteok": failed()}, state, now=NOW + timedelta(minutes=15))
    summary, state = plan_source_notices({"remoteok": failed()}, state, now=NOW + timedelta(hours=6))

    assert [(item["kind"], item["occurrences"]) for item in first] == [("issue", 1)]
    assert second == []
    assert [(item["kind"], item["occurrences"]) for item in summary] == [("repeat", 3)]
    assert "одинаковых наблюдений: 3" in render_source_state_notice(summary[0], failed())


def test_changed_code_and_recovery_are_state_changes_only_once() -> None:
    _, state = plan_source_notices({"jobbank": failed()}, "", now=NOW)
    changed, state = plan_source_notices(
        {"jobbank": failed("NETWORK_READ_TIMEOUT")}, state, now=NOW + timedelta(minutes=15),
    )
    recovered, state = plan_source_notices(
        {"jobbank": {"status": "success", "name": "Job Bank", "found": 2, "processed": 2, "diagnostics": []}},
        state,
        now=NOW + timedelta(minutes=30),
    )
    quiet, _ = plan_source_notices(
        {"jobbank": {"status": "success", "name": "Job Bank", "found": 1, "processed": 1, "diagnostics": []}},
        state,
        now=NOW + timedelta(minutes=45),
    )

    assert changed[0]["kind"] == "issue"
    assert changed[0]["codes"] == ["NETWORK_READ_TIMEOUT"]
    assert recovered[0]["kind"] == "recovered"
    assert recovered[0]["previous_codes"] == ["NETWORK_READ_TIMEOUT"]
    assert quiet == []


def test_successful_hh_403_fallback_stays_in_diagnostics_without_chat_alert() -> None:
    info = {
        "status": "success", "name": "HeadHunter", "found": 4, "processed": 4,
        "diagnostics": [{"code": "HTTP_403_FORBIDDEN", "action": "fallback"}],
    }
    notices, state = plan_source_notices({"hh": info}, "", now=NOW)
    repeated, _ = plan_source_notices({"hh": info}, state, now=NOW + timedelta(minutes=15))

    assert notices == []
    assert repeated == []
    assert "HTTP_403_FORBIDDEN" in str(info)


def test_hh_fallback_failure_notifies_only_material_network_loss() -> None:
    info = {
        "status": "failed", "name": "HeadHunter", "found": 0, "processed": 0,
        "diagnostics": [
            {"code": "HTTP_403_FORBIDDEN", "action": "fallback"},
            {"code": "NETWORK_CONNECT_TIMEOUT", "action": "continue"},
        ],
    }
    notices, _ = plan_source_notices({"hh": info}, "", now=NOW)

    assert len(notices) == 1
    assert notices[0]["codes"] == ["NETWORK_CONNECT_TIMEOUT"]


def test_cooldown_does_not_create_a_new_state_or_recovery() -> None:
    _, state = plan_source_notices({"hh": failed("NETWORK_CONNECT_ERROR")}, "", now=NOW)
    notices, same_state = plan_source_notices({"hh": {
        "status": "skipped", "name": "HeadHunter", "found": 0, "processed": 0,
        "diagnostics": [{"code": "SOURCE_CONNECTION_COOLDOWN", "action": "cooldown"}],
    }}, state, now=NOW + timedelta(minutes=15))

    assert notices == []
    assert "NETWORK_CONNECT_ERROR" in same_state
