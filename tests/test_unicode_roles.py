import re

import pytest

from app.database.models import Job, ResumeProfile, SearchProfile
from app.matching.engine import choose_resume, score_job
from app.sources.adapters import georgia


def _score(title, query):
    return score_job(
        Job(fingerprint="unicode-role", title=title, company="Example", description="", country="AM"),
        SearchProfile(id=1, profile_id=1, settings={
            "search_strategy": "relocation_first", "relocation_queries": [query],
            "notify_min_score": 65,
        }),
        [], [],
    )


def test_georgia_discovery_accepts_an_explicit_georgian_query_without_translation():
    role = "მომხმარებელთა მხარდაჭერა"

    assert georgia._tokens(role) == {"მომხმარებელთა", "მხარდაჭერა"}
    assert georgia._matches(role, [role])
    assert not georgia._matches("დამლაგებელი", [role])
    assert not georgia._matches(role, ["customer support"])


@pytest.mark.parametrize("role", ["მომხმარებელთა მხარდაჭერა", "հաճախորդների աջակցություն"])
def test_matching_uses_owner_selected_georgian_and_armenian_text_with_existing_role_bonus(role):
    result = _score(role.upper(), role)
    ordinary = _score("Customer Support", "customer support")

    assert result.technical_score == ordinary.technical_score == 60
    assert result.total_score == ordinary.total_score
    assert result.fit == ordinary.fit
    assert f"роль: {role.casefold()}" in result.reason
    assert result.total_score < 65
    assert _score(role, "customer support").technical_score == 22


@pytest.mark.parametrize(("title", "query", "matched"), [
    ("DevOps Engineer", "DevOps Engineer", True),
    ("Electrical Engineer", "DevOps Engineer", False),
    ("Инженер Linux", "Инженер Linux", True),
    ("Электрический инженер", "Инженер Linux", False),
    ("Системный администратор Linux", "Системный администратор Linux", True),
    ("DevOps инженер", "DevOps инженер", True),
    ("Linux Administrator", "Linux_Administrator", True),
    ("C++ Developer", "C++ Developer", True),
])
def test_existing_english_russian_generic_exclusions_and_score_bonus_are_unchanged(title, query, matched):
    result = _score(title, query)

    assert result.technical_score == (60 if matched else 22)
    assert ("роль:" in result.reason) is matched
    assert result.total_score == (48 if matched else 30)


@pytest.mark.parametrize("text", [
    "DevOps Engineer", "Linux_Administrator", "Инженер Linux", "C++ Developer",
    "C# .NET Engineer", "Системный-администратор", "Docker 123", "Ёлка",
])
def test_georgia_existing_tokens_and_technical_punctuation_remain_identical(text):
    historical = set(re.findall(r"[a-zа-яё0-9+#.-]+", text.casefold()))
    assert georgia._tokens(text) == historical


def test_matching_does_not_treat_arbitrary_short_fragments_as_roles():
    assert _score("აბ", "აბ").technical_score == 22
    assert _score("աբ", "աբ").technical_score == 22


@pytest.mark.parametrize(("query", "matching", "unrelated"), [
    ("QA Engineer", "QA Engineer", "Platform Engineer"),
    ("Go Developer", "Go Developer", "Google Cloud Developer"),
    ("HR", "HR Specialist", "Threat Analyst"),
    ("C# Developer", "C# Developer", "C++ Developer"),
    ("Java Developer", "Java Engineer", "JavaScript Developer"),
    ("IT Support", "IT Support", "Customer Support"),
    ("UX Designer", "UX Designer", "Graphic Designer"),
    ("System Administrator", "Systems Administrator", "Network Administrator"),
])
def test_fallback_role_bonus_requires_exact_specific_terms(query, matching, unrelated):
    matched = _score(matching, query)
    other = _score(unrelated, query)
    assert matched.technical_score == 60
    assert other.technical_score == 22
    assert "роль:" in matched.reason
    assert "роль:" not in other.reason
    # Fix role identity, not the global scoring weights or notification bar.
    assert matched.total_score < 65


def test_short_role_bonus_uses_each_search_strategy_queries():
    job = Job(title="HR Specialist", company="Example", description="", country="AM")
    settings = {"queries": ["DevOps Engineer"], "relocation_queries": ["HR"]}
    career = score_job(job, SearchProfile(settings={**settings, "search_strategy": "career_first"}), [], [])
    relocation = score_job(job, SearchProfile(settings={**settings, "search_strategy": "relocation_first"}), [], [])
    assert career.technical_score == 22
    assert relocation.technical_score == 60


def test_unicode_resume_role_and_content_overlap_reuse_existing_selection_weights():
    role = "հաճախորդների աջակցություն"
    job = Job(fingerprint="unicode-resume", title=role, description="տեխնիկական", country="AM")
    unrelated = ResumeProfile(id=2, profile_id=1, role="warehouse", name="Other", language="en", content="", active=True)
    selected = ResumeProfile(id=1, profile_id=1, role=role, name="Selected", language="en", content="տեխնիկական", active=True)

    assert choose_resume(job, [selected, unrelated]) == 1
    assert _score(role, role).technical_score == 60
