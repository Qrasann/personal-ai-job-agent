from types import SimpleNamespace

import pytest

from app.database.models import Job, SearchProfile
from app.domain.employer_policy import decision, update_policy
from app.domain.jobs import NormalizedJob
from app.domain.source_posting import snapshot_source_posting, source_posting_view
from app.matching.engine import MATCH_ASSESSMENT_VERSION, score_job
from app.services import _match_lane


@pytest.mark.parametrize("strategy", ["career_first", "relocation_first"])
@pytest.mark.parametrize("legacy_term", ["betting", "gambling", "букмек", "казино", "crypto casino"])
def test_betsson_is_not_blocked_by_old_sector_blacklist_or_industry_tag(strategy, legacy_term):
    normalized = NormalizedJob(
        source="employer_career_watch", source_job_id="betsson:1",
        title="Platform Core DevOps Engineer - Infra", company="Betsson Group",
        description="Kubernetes, Kafka and infrastructure as code", country="MT",
        raw={"industry_tags": ["betting", "gambling"]},
    )
    source_ref = SimpleNamespace(raw={
        **normalized.raw,
        "normalized_posting_v1": snapshot_source_posting(normalized),
    })
    job = source_posting_view(Job(
        fingerprint=normalized.canonical_fingerprint(), title=normalized.title,
        company=normalized.company, description=normalized.description, country=normalized.country,
    ), source_ref)
    search = SearchProfile(id=1, profile_id=1, settings={
        "queries": ["DevOps Engineer"], "relocation_queries": ["warehouse worker"],
        "search_strategy": strategy, "exclude_terms": [legacy_term],
        "modes": {"local_ru": True, "remote_international": True, "relocation": True},
    })

    result = score_job(job, search, [], [])

    assert MATCH_ASSESSMENT_VERSION == 3
    assert result.fit != "skip"
    assert _match_lane(result, 0) in {"qualified", "stretch"}


@pytest.mark.parametrize("name", ["Алабуга", "АО ОЭЗ ППТ АЛАБУГА", "AO OEZ PPT ALABUGA", "JOINT STOCK COMPANY SPECIAL ECONOMIC ZONE OF INDUSTRIAL PRODUCTION ALABUGA", "Военторг", "АО ВОЕНТОРГ", "AKTSIONERNOE OBSHCHESTVO VOENTORG", "JOINT STOCK COMPANY VOENTORG"])
def test_exact_named_employers_are_blocked(name):
    assert decision(name, [])[0] == "block"


@pytest.mark.parametrize("name", ["Алабуга Консалтинг", "Военторг сервисный партнёр", "РЖД", "Betsson Group"])
def test_no_substring_or_sector_block_for_other_employers(name):
    action, _ = decision(name, ["betting", "gambling", "civilian_state_owned"])
    assert action == "allow"


def test_manual_exact_employer_choice_overrides_owner_block_and_category():
    cfg = update_policy({}, "employer", "allow", "Алабуга")
    assert decision("Алабуга", ["russian_military_defense"], cfg)[0] == "allow"
    cfg = update_policy({}, "employer", "block", "Betsson Group")
    assert decision("Betsson Group", ["betting"], cfg)[0] == "block"


def test_manual_category_choice_overrides_owner_category_default():
    cfg = update_policy({}, "category", "allow", "russian_military_defense")
    assert decision("Civilian Name", ["russian_military_defense"], cfg)[0] == "allow"
    cfg = update_policy({}, "category", "block", "betting")
    assert decision("Betsson Group", ["betting"], cfg)[0] == "block"


def test_category_allow_does_not_override_separate_blocked_category():
    cfg = update_policy({}, "category", "allow", "betting")

    action, reason = decision(
        "Mixed Tags Employer", ["betting", "russian_military_defense"], cfg,
    )

    assert action == "block"
    assert "russian_military_defense" in reason


@pytest.mark.parametrize("strategy", ["career_first", "relocation_first"])
@pytest.mark.parametrize("category", ["russian_military_defense", "verified_direct_war_tie", "russian_government_body"])
def test_verified_russian_restriction_categories_apply_to_both_search_directions(strategy, category):
    job = source_posting_view(
        Job(fingerprint=f"blocked-{category}", title="DevOps Engineer", company="Ministry of Example", description="Linux Docker", country="RU"),
        SimpleNamespace(raw={"industry_tags": [category]}),
    )
    search = SearchProfile(id=1, profile_id=1, settings={
        "queries": ["DevOps Engineer"], "relocation_queries": ["warehouse worker"],
        "search_strategy": strategy,
        "modes": {"local_ru": True, "remote_international": True, "relocation": True},
    })
    result = score_job(job, search, [], [])
    assert result.fit == "skip"
    assert "политике работодателя" in result.reason


def test_civilian_state_owned_category_is_explicitly_allowed():
    assert decision("Russian Railways", ["civilian_state_owned"])[0] == "allow"


def test_crypto_category_warns_and_keeps_job_in_stretch_lane():
    job = Job(fingerprint="web3", title="DevOps Engineer", company="Web3 Co", description="Linux Docker", country="GE")
    search = SearchProfile(id=1, profile_id=1, settings={"queries": ["DevOps Engineer"], "modes": {"local_ru": True, "remote_international": True, "relocation": True}})
    result = score_job(job, search, [], [])
    action, _ = decision("Web3 Co", ["crypto"])
    assert action == "warn"
    assert result.fit == "stretch"
    cfg = update_policy({}, "employer", "allow", "Web3 Co")
    assert decision("Web3 Co", ["crypto"], cfg)[0] == "allow"
    search.settings["employer_policy_overrides"] = cfg["employer_policy_overrides"]
    assert score_job(job, search, [], []).fit == "good"


def test_unknown_employer_and_untrusted_incidental_words_are_not_blocked():
    assert decision("Civilian Co", [])[0] == "allow"
    assert decision("Army City Cafe", ["civilian_state_owned"])[0] == "allow"
