import pytest

from app.database.models import Job, SearchProfile
from app.matching.engine import score_job
from app.search.user_preferences import (
    parse_salary_command,
    update_blacklist,
    update_salary,
)


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
