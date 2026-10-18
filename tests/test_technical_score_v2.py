from types import SimpleNamespace

import pytest

from app.database.models import CandidateFact, Job, SearchProfile
from app.matching.engine import score_job
from app.matching.fact_comparison import compare_facts, extract_requirement_importance
from app.matching.technical_score import score_technical_v2


def test_opentelemetry_is_compared_only_when_explicitly_present():
    fact = SimpleNamespace(
        id=12, value="Commercial Open Telemetry deployment", experience_type="commercial",
        active=True, deleted_at=None,
    )
    vacancy = "Requirements: OpenTelemetry is required."

    assert score_technical_v2(vacancy, [fact]) == 100
    assert score_technical_v2(vacancy, []) == 0
    assert score_technical_v2("Requirements: OTel is required.", [fact]) is None


def test_generic_gitlab_repository_work_does_not_create_ci_fit_score():
    fact = SimpleNamespace(
        id=13, value="Commercial GitLab repository administration", experience_type="commercial",
        active=True, deleted_at=None,
    )
    vacancy = "Requirements: maintain GitLab projects and repositories."

    assert compare_facts(vacancy, [fact]).requirements == ()
    assert score_technical_v2(vacancy, [fact]) is None


def test_docker_compose_is_not_double_counted_as_a_separate_docker_requirement():
    vacancy = "Requirements: Linux and Docker Compose experience required."
    linux = SimpleNamespace(
        id=14, value="Commercial Linux administration", experience_type="commercial",
        active=True, deleted_at=None,
    )

    comparison = compare_facts(vacancy, [linux])

    assert [item.skill for item in comparison.requirements] == ["Linux", "Docker Compose"]
    assert score_technical_v2(vacancy, [linux]) == 50


def test_standalone_docker_remains_a_separate_requirement_from_docker_compose():
    comparison = compare_facts(
        "Requirements: Docker and Docker Compose administration required.", [],
    )

    assert {item.skill for item in comparison.requirements} == {"Docker", "Docker Compose"}


@pytest.mark.parametrize("phrase", [
    "an established network of industry contacts",
    "a network of professional contacts",
    "networking with key stakeholders",
    "a nationwide network of clinics and hospitals",
    "a network of medical professionals",
    "a network of physicians and nurses",
])
def test_professional_contact_network_does_not_create_technical_networking_requirement(phrase):
    vacancy = f"Requirements: {phrase} is required."

    assert compare_facts(vacancy, []).requirements == ()
    assert score_technical_v2(vacancy, []) is None


def test_technical_network_and_firewall_requirement_is_not_filtered_as_an_organization_network():
    result = compare_facts("Requirements: Configure network routing and firewall rules.", [])

    assert [(item.skill, item.importance) for item in result.requirements] == [("Networking", "required")]


def test_explicit_required_alternative_counts_as_one_scoring_choice():
    linux = SimpleNamespace(
        id=1, value="Commercial Linux administration", experience_type="commercial",
        active=True, deleted_at=None,
    )
    text = "Requirements: Linux or Windows.\nDocker."
    comparison = compare_facts(text, [linux])

    assert comparison.alternative_groups == (("Linux", "Windows"),)
    assert comparison.skills_for("missing") == ["Windows", "Docker"]
    assert score_technical_v2(text, [linux]) == 50
    assert score_technical_v2("Требования: Linux или Windows", [linux]) == 100
    assert score_technical_v2("Requirements: Linux and Windows", [linux]) == 50


def test_repeated_or_ambiguous_skills_remain_independent_requirements():
    linux = SimpleNamespace(
        id=1, value="Linux", experience_type="commercial",
        active=True, deleted_at=None,
    )
    repeated = "Requirements: Linux or Windows.\nWindows is also mandatory."
    ambiguous = "Requirements: Linux or Windows and Docker."

    assert compare_facts(repeated, [linux]).alternative_groups == ()
    assert score_technical_v2(repeated, [linux]) == 50
    assert compare_facts(ambiguous, [linux]).alternative_groups == ()
    assert score_technical_v2(ambiguous, [linux]) == 33


def test_preferred_alternative_uses_one_preferred_scoring_choice():
    linux = SimpleNamespace(
        id=1, value="Linux", experience_type="commercial", active=True,
        deleted_at=None,
    )
    docker = SimpleNamespace(
        id=2, value="Docker", experience_type="commercial", active=True,
        deleted_at=None,
    )
    vacancy = "Requirements: Linux. Nice to have: Docker or Kubernetes."

    comparison = compare_facts(vacancy, [linux, docker])
    assert comparison.preferred_alternative_groups == (("Docker", "Kubernetes"),)
    assert score_technical_v2(vacancy, [linux, docker]) == 100
    assert score_technical_v2(vacancy, [linux]) == 85
    assert score_technical_v2(
        "Requirements: Linux. Nice to have: Docker and Kubernetes.",
        [linux, docker],
    ) == 92


def test_required_alternative_before_another_sentence_keeps_one_choice():
    linux = SimpleNamespace(
        id=1, value="Linux", experience_type="commercial", active=True,
        deleted_at=None,
    )
    vacancy = "Requirements: Linux or Windows. Docker."

    assert compare_facts(vacancy, [linux]).alternative_groups == (("Linux", "Windows"),)
    assert score_technical_v2(vacancy, [linux]) == 50
    assert compare_facts(
        "Requirements: Linux or Windows. Windows is mandatory.", [linux]
    ).alternative_groups == ()


def test_explicit_multiline_alternative_groups_only_the_two_connected_skills():
    linux = SimpleNamespace(
        id=1, value="Linux", experience_type="commercial", active=True,
        deleted_at=None,
    )
    vacancy = "Requirements:\nLinux\nor Windows\nDocker"

    comparison = compare_facts(vacancy, [linux])

    assert comparison.alternative_groups == (("Linux", "Windows"),)
    assert comparison.skills_for("missing") == ["Windows", "Docker"]
    assert score_technical_v2(vacancy, [linux]) == 50


def test_multiline_alternative_with_repeated_skill_stays_independent():
    linux = SimpleNamespace(
        id=1, value="Linux", experience_type="commercial", active=True,
        deleted_at=None,
    )
    vacancy = "Requirements:\nLinux\nor Windows\nWindows also required"

    assert compare_facts(vacancy, [linux]).alternative_groups == ()


def _fact(skill: str, experience_type: str, *, fact_id: int = 1, active: bool = True, deleted=False):
    fact = CandidateFact(
        id=fact_id,
        profile_id=1,
        value=skill,
        experience_type=experience_type,
        active=active,
    )
    if deleted:
        from app.database.time_utils import utcnow_naive
        fact.deleted_at = utcnow_naive()
    return fact


def _search():
    return SearchProfile(
        id=1,
        profile_id=1,
        settings={
            "queries": ["DevOps Engineer"],
            "preferred_terms": ["linux", "docker", "nginx"],
            "strong_terms": ["linux", "docker"],
            "exclude_terms": ["gambling"],
            "modes": {
                "local_ru": True,
                "remote_international": True,
                "relocation": True,
            },
            "minimum_salary": {"RUR": 100000},
        },
    )


def test_required_commercial_is_full_technical_match():
    text = "Требования:\nLinux"
    assert score_technical_v2(text, [_fact("Linux", "commercial")]) == 100


def test_inline_preferred_section_uses_existing_preferred_weight():
    text = "Requirements: Linux. Nice to have: Docker."
    assert score_technical_v2(text, [_fact("Linux", "commercial")]) == 85


def test_required_experience_levels_have_strict_order():
    text = "Требования\nLinux"

    commercial = score_technical_v2(text, [_fact("Linux", "commercial")])
    lab = score_technical_v2(text, [_fact("Linux", "lab")])
    unknown = score_technical_v2(text, [_fact("Linux", "unknown")])
    learning = score_technical_v2(text, [_fact("Linux", "learning")])
    missing = score_technical_v2(text, [])

    assert (commercial, lab, unknown, learning, missing) == (100, 75, 60, 40, 0)


def test_required_partial_coverage_is_proportional():
    text = """Требования:
Linux
Docker
Kubernetes
Nginx
"""
    facts = [
        _fact("Linux", "commercial", fact_id=1),
        _fact("Docker", "lab", fact_id=2),
        _fact("Kubernetes", "learning", fact_id=3),
    ]
    assert score_technical_v2(text, facts) == 54


def test_preferred_requirements_cannot_compensate_for_missing_required():
    text = """Требования:
Linux
Приветствуется:
Docker
"""
    facts = [_fact("Docker", "commercial")]
    assert score_technical_v2(text, facts) == 15


def test_necessary_qualification_is_scored_as_required_requirements():
    text = """Necessary Qualification:
Minimum 3 years of hands-on Linux system administration experience.
Minimum 2 years of hands-on experience with AWS in a production environment.
Working familiarity with AWS Databricks.
At least 1 year of Windows system administration experience.
Working familiarity with Kubernetes.
Preferred:
Terraform or Ansible.
"""
    importance = extract_requirement_importance(text)

    assert importance["Linux"] == "required"
    assert importance["AWS"] == "required"
    assert importance["Kubernetes"] == "required"
    assert importance["Databricks"] == "required"
    assert importance["Windows"] == "required"
    assert importance["Terraform"] == "preferred"
    assert score_technical_v2(
        text,
        [_fact("Linux", "commercial"), _fact("Terraform", "commercial", fact_id=2)],
    ) < 100

    # Greenhouse retains this singular heading in the current Lineate posting;
    # older pages using the plural form must continue to classify identically.
    plural_heading = text.replace(
        "Necessary Qualification:", "Necessary Qualifications:"
    )
    assert extract_requirement_importance(plural_heading) == importance


def test_missing_preferred_requirement_only_reduces_small_bonus_lane():
    text = """Требования:
Linux
Приветствуется:
Docker
"""
    facts = [_fact("Linux", "commercial")]
    assert score_technical_v2(text, facts) == 85


def test_unknown_responsibility_signals_do_not_change_structured_score():
    text = """Обязанности:
Docker
Требования:
Linux
"""
    without_docker = [_fact("Linux", "commercial")]
    with_docker = [
        _fact("Linux", "commercial", fact_id=1),
        _fact("Docker", "commercial", fact_id=2),
    ]

    assert score_technical_v2(text, without_docker) == 100
    assert score_technical_v2(text, with_docker) == 100


def test_no_required_section_requests_legacy_fallback():
    assert score_technical_v2(
        "Linux Docker Nginx",
        [_fact("Linux Docker Nginx", "commercial")],
    ) is None

    assert score_technical_v2(
        "Приветствуется:\nDocker",
        [_fact("Docker", "commercial")],
    ) is None


def test_inactive_and_deleted_facts_are_not_counted():
    text = "Требования:\nLinux"
    facts = [
        _fact("Linux", "commercial", fact_id=1, active=False),
        _fact("Linux", "commercial", fact_id=2, deleted=True),
    ]
    assert score_technical_v2(text, facts) == 0


def test_skill_present_in_required_and_preferred_is_counted_as_required_only():
    text = """Требования:
Linux
Приветствуется:
Linux
Docker
"""
    facts = [_fact("Linux", "commercial")]
    # Linux is required (priority required > preferred), Docker is preferred and missing.
    assert score_technical_v2(text, facts) == 85


def test_score_job_uses_v2_for_structured_requirements():
    job = Job(
        fingerprint="structured-v2",
        title="DevOps Engineer",
        company="ACME",
        description="""Требования:
Linux
Docker
Приветствуется:
Kubernetes
""",
        country="RU",
        salary_to=150000,
        salary_currency="RUR",
        salary_period="monthly",
    )
    facts = [
        _fact("Linux", "commercial", fact_id=1),
        _fact("Docker", "lab", fact_id=2),
        _fact("Kubernetes", "learning", fact_id=3),
    ]

    result = score_job(job, _search(), facts, [])

    assert result.technical_score == 80
    assert result.geography_score == 95
    assert result.salary_score == 100
    assert result.relocation_score == 50


def test_score_job_keeps_legacy_technical_fallback_for_unstructured_jobs():
    job = Job(
        fingerprint="legacy-fallback",
        title="DevOps Engineer",
        company="ACME",
        description="Linux Docker",
        country="RU",
    )
    facts = [
        _fact("Linux", "commercial", fact_id=1),
        _fact("Docker", "commercial", fact_id=2),
    ]

    result = score_job(job, _search(), facts, [])

    assert result.technical_score == 86


def test_score_job_can_use_full_details_for_technical_only():
    job = Job(
        fingerprint="full-details-override",
        title="DevOps Engineer",
        company="ACME",
        description="Linux Docker DevOps Engineer",
        country="RU",
        salary_to=150000,
        salary_currency="RUR",
        salary_period="monthly",
    )
    facts = [
        _fact("Linux", "commercial", fact_id=1),
        _fact("Docker", "lab", fact_id=2),
        _fact("Kubernetes", "learning", fact_id=3),
    ]
    full_text = """Требования:
Linux
Docker
Приветствуется:
Kubernetes
"""

    result = score_job(
        job,
        _search(),
        facts,
        [],
        technical_text=full_text,
    )

    assert result.technical_score == 80
    assert result.geography_score == 95
    assert result.salary_score == 100
    assert result.relocation_score == 50


def test_structured_required_and_preferred_can_score_exactly_zero():
    text = "Требования:\nLinux\nПриветствуется:\nDocker\n"
    assert score_technical_v2(text, []) == 0

def test_score_job_classifies_good_stretch_and_skip():
    facts = [
        _fact("Linux", "commercial", fact_id=1),
        _fact("Docker", "lab", fact_id=2),
    ]
    good = Job(fingerprint="fit-good", title="DevOps Engineer", company="ACME", description="Опыт 1–3 года. Linux Docker", country="RU")
    stretch = Job(fingerprint="fit-stretch", title="DevOps Engineer", company="ACME", description="Опыт 3–6 лет. Linux Docker", country="RU")
    senior = Job(fingerprint="fit-senior", title="Senior DevOps Engineer", company="ACME", description="Linux Docker", country="RU")
    high_exp = Job(fingerprint="fit-5plus", title="DevOps Engineer", company="ACME", description="Опыт от 5 лет. Linux Docker", country="RU")

    assert score_job(good, _search(), facts, []).fit == "good"
    assert score_job(stretch, _search(), facts, []).fit == "stretch"
    assert score_job(senior, _search(), facts, []).fit == "skip"
    assert score_job(high_exp, _search(), facts, []).fit == "skip"


def test_explicit_volunteer_title_stays_visible_but_is_not_good():
    job = Job(
        fingerprint="volunteer-devops",
        title="DevOps Volunteer",
        company="Community Project",
        description="Linux Docker remote worldwide",
        work_mode="remote",
    )

    result = score_job(job, _search(), [_fact("Linux", "commercial", fact_id=1)], [])

    assert result.fit == "skip"
    assert result.total_score <= 58
    assert "волонтёрская/неоплачиваемая роль" in result.reason


def test_expression_of_interest_form_stays_visible_but_is_not_good():
    job = Job(
        fingerprint="sre-interest-form",
        title="Site Reliability Engineer Expression of Interest Form",
        company="Example",
        description="Linux Docker remote worldwide",
        work_mode="remote",
    )

    result = score_job(job, _search(), [_fact("Linux", "commercial", fact_id=1)], [])

    assert result.fit == "skip"
    assert result.total_score <= 58
    assert "не подтверждённая открытая вакансия" in result.reason

def test_score_job_skips_hard_production_skill_gap_only():
    learning = [_fact("Kubernetes", "learning", fact_id=1)]
    commercial = [_fact("Kubernetes", "commercial", fact_id=2)]

    hard = Job(
        fingerprint="prod-gap-hard",
        title="DevOps Engineer",
        company="ACME",
        description="Требования: обязателен опыт Kubernetes в production.",
        country="RU",
    )
    preferred = Job(
        fingerprint="prod-gap-preferred",
        title="DevOps Engineer",
        company="ACME",
        description="Будет плюсом: опыт Kubernetes в production.",
        country="RU",
    )

    assert score_job(hard, _search(), learning, []).fit == "skip"
    assert score_job(hard, _search(), commercial, []).fit == "good"
    assert score_job(preferred, _search(), learning, []).fit == "good"

def test_score_job_skips_hard_three_year_production_role_requirement_only():
    hard = Job(
        fingerprint="prod-role-hard",
        title="DevOps Engineer",
        company="ACME",
        description="Требования: от 3 лет опыта DevOps в production.",
        country="RU",
    )
    generic = Job(
        fingerprint="prod-role-generic",
        title="DevOps Engineer",
        company="ACME",
        description="Опыт 3–6 лет. Linux Docker.",
        country="RU",
    )
    preferred = Job(
        fingerprint="prod-role-preferred",
        title="DevOps Engineer",
        company="ACME",
        description="Будет плюсом: 3+ года DevOps опыта в production.",
        country="RU",
    )

    assert score_job(hard, _search(), [], []).fit == "skip"
    assert score_job(generic, _search(), [], []).fit == "stretch"
    assert score_job(preferred, _search(), [], []).fit != "skip"

def test_score_job_skips_hard_management_requirement_only():
    hard_ru = Job(
        fingerprint="management-hard-ru",
        title="DevOps Engineer",
        company="ACME",
        description="Обязанности: руководство командой DevOps-инженеров и постановка задач.",
        country="RU",
    )
    hard_en = Job(
        fingerprint="management-hard-en",
        title="SRE Engineer",
        company="ACME",
        description="Responsibilities: people management for a team of SRE engineers.",
        country="RU",
    )
    mentor = Job(
        fingerprint="management-mentor",
        title="DevOps Engineer",
        company="ACME",
        description="Обязанности: менторинг коллег, code review и помощь junior-инженерам.",
        country="RU",
    )
    preferred = Job(
        fingerprint="management-preferred",
        title="DevOps Engineer",
        company="ACME",
        description="Будет плюсом: опыт управления командой.",
        country="RU",
    )

    assert score_job(hard_ru, _search(), [], []).fit == "skip"
    assert score_job(hard_en, _search(), [], []).fit == "skip"
    assert score_job(mentor, _search(), [], []).fit != "skip"
    assert score_job(preferred, _search(), [], []).fit != "skip"
