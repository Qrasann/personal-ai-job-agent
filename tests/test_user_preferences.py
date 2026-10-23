import pytest
from datetime import UTC, datetime

from app.database.models import Job, SearchProfile
from app.matching.engine import score_job
from app.search.user_preferences import (
    parse_salary_command,
    preview_blacklist,
    update_blacklist,
    update_salary,
)
from app.domain.blacklist import matching_blacklist_rule


def test_salary_command_validates_and_updates_scoring_minimum():
    kind, currency, amount = parse_salary_command("/salary minimum usd 3000")
    assert (kind, currency, amount) == ("minimum", "USD", 3000)
    updated = update_salary({"minimum_salary": {"RUB": 100000}}, kind, currency, amount)
    assert updated["minimum_salary"] == {"RUB": 100000, "USD": 3000}
    assert update_salary(updated, kind, currency, None)["minimum_salary"] == {"RUB": 100000}
    with pytest.raises(ValueError):
        parse_salary_command("/salary minimum USD -1")


def test_current_and_desired_salary_values_are_kept_separately():
    settings = update_salary({}, "current", "EUR", 2500)
    settings = update_salary(settings, "desired", "EUR", 3500)
    assert settings["current_salary"] == {"EUR": 2500}
    assert settings["desired_salary"] == {"EUR": 3500}
    assert "minimum_salary" not in settings


def test_blacklist_is_case_insensitive_and_applies_to_job_scoring():
    settings = update_blacklist({}, "add", "Fraud")
    settings = update_blacklist(settings, "add", "fraud")
    assert settings["exclude_terms"] == ["Fraud"]
    search = SearchProfile(id=1, profile_id=1, settings=settings)
    job = Job(
        fingerprint="blacklist",
        title="DevOps Engineer",
        company="Example",
        description="Infrastructure role at a fraud company",
        country="US",
    )
    result = score_job(job, search, [], [])
    assert result.fit == "skip"
    assert "fraud" in result.reason.casefold()
    assert update_blacklist(settings, "remove", "FRAUD")["exclude_terms"] == []


def test_sector_preferences_use_allow_warn_block_policy_instead_of_blacklist_terms():
    with pytest.raises(ValueError, match="employerpolicy"):
        update_blacklist({}, "add", "gambling")
    from app.domain.employer_policy import decision, update_policy

    settings = update_policy({}, "category", "block", "betting")
    assert decision("Betsson", ["betting"], settings)[0] == "block"
    settings = update_policy(settings, "category", "allow", "betting")
    assert decision("Betsson", ["betting"], settings)[0] == "allow"
    settings = update_policy(settings, "employer", "warn", "Betsson Group")
    assert decision("Betsson Group", ["betting"], settings)[0] == "warn"


def test_blacklist_preview_is_non_mutating_and_undo_restores_previous_terms():
    settings = update_blacklist({}, "add", "Fraud")
    preview = preview_blacklist(settings, "add", "Agency")

    assert preview["before"] == ["Fraud"]
    assert preview["after"] == ["Fraud", "Agency"]
    assert settings["exclude_terms"] == ["Fraud"]
    assert update_blacklist(settings, "add", "Agency")["exclude_terms"] == ["Fraud", "Agency"]
    assert update_blacklist(update_blacklist(settings, "add", "Agency"), "undo")["exclude_terms"] == ["Fraud"]


def test_blacklist_preview_and_undo_are_safe_when_no_previous_change_exists():
    settings = {"exclude_terms": ["Fraud"]}
    preview = preview_blacklist(settings, "undo")

    assert preview["before"] == preview["after"] == ["Fraud"]
    assert update_blacklist(settings, "undo")["exclude_terms"] == ["Fraud"]


@pytest.mark.parametrize("kind,value", [
    ("vacancy", "job-fingerprint"),
    ("company", "Example Corp"),
    ("company_role", "Example Corp|DevOps Engineer"),
    ("role", "DevOps Engineer"),
    ("phrase", "night shifts only"),
])
def test_structured_blacklist_five_levels_block_only_explicit_matches(kind, value):
    job = Job(
        id=42, fingerprint="job-fingerprint", title="DevOps Engineer",
        company="Example Corp", description="Linux. Night shifts only.", country="US",
    )
    settings = {"blacklist_rules": [{"kind": kind, "value": value}]}
    assert matching_blacklist_rule(job, settings)["kind"] == kind
    assert score_job(job, SearchProfile(id=1, profile_id=1, settings=settings), [], []).fit == "skip"


def test_structured_blacklist_exact_rules_do_not_use_accidental_substrings():
    job = Job(
        fingerprint="job-1234", title="Senior DevOps Engineer",
        company="Example Corporation", description="Ordinary role", country="US",
    )
    settings = {"blacklist_rules": [
        {"kind": "vacancy", "value": "job-12"},
        {"kind": "company", "value": "Example"},
        {"kind": "role", "value": "DevOps Engineer"},
        {"kind": "company_role", "value": "Example|Senior DevOps Engineer"},
    ]}
    assert matching_blacklist_rule(job, settings) is None


def test_structured_blacklist_ignores_disabled_expired_and_invalid_rules():
    job = Job(fingerprint="job", title="DevOps Engineer", company="Example", description="blocked phrase")
    settings = {"blacklist_rules": [
        {"kind": "phrase", "value": "blocked phrase", "enabled": False},
        {"kind": "phrase", "value": "blocked phrase", "expires_at": "2026-10-22T00:00:00Z"},
        {"kind": "phrase", "value": "blocked phrase", "expires_at": "invalid"},
    ]}
    assert matching_blacklist_rule(job, settings, now=datetime(2026, 10, 23, tzinfo=UTC)) is None
