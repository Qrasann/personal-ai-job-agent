from types import SimpleNamespace

import pytest

from app.domain.job_text import clean_html_text
from app.matching.fact_comparison import (
    compare_facts,
    extract_requirement_importance,
    extract_technical_requirements,
)


def fact(
    fact_id: int,
    value: str,
    experience_type: str,
):
    return SimpleNamespace(
        id=fact_id,
        value=value,
        experience_type=experience_type,
        active=True,
        deleted_at=None,
    )


def test_extracts_canonical_devops_requirements_without_duplicates():
    text = """
    Требования:
    Linux, Docker, Kubernetes.
    Terraform и Terragrunt.
    Helm-чарты и ArgoCD.
    Мониторинг через Prometheus и Grafana.
    CI/CD на базе GitLab.
    """

    skills = extract_technical_requirements(text)

    assert "Linux" in skills
    assert "Docker" in skills
    assert "Kubernetes" in skills
    assert "Terraform" in skills
    assert "Terragrunt" in skills
    assert "Helm" in skills
    assert "ArgoCD" in skills
    assert "Prometheus" in skills
    assert "Grafana" in skills
    assert "GitLab CI" in skills
    assert len(skills) == len(set(skills))


def test_gitlab_repository_requirement_does_not_imply_gitlab_ci():
    assert "GitLab CI" not in extract_technical_requirements(
        "Requirements: experience managing GitLab projects and repositories."
    )


def test_gitlab_pipeline_requirement_recognizes_explicit_ci_context():
    assert "GitLab CI" in extract_technical_requirements(
        "Requirements: maintain GitLab pipelines and runners."
    )


@pytest.mark.parametrize("mention", ["OpenShift", "Red Hat OpenShift"])
def test_candidate_fit_recognizes_openshift_as_its_own_supported_skill(mention):
    comparison = compare_facts(
        f"Requirements: Experience operating {mention}.",
        [fact(7, "Commercial OpenShift cluster operations", "commercial")],
    )

    assert [(item.skill, item.status, item.importance) for item in comparison.requirements] == [
        ("OpenShift", "commercial", "required"),
    ]


@pytest.mark.parametrize("mention", ["OpenTelemetry", "Open Telemetry"])
def test_candidate_fit_recognizes_explicit_opentelemetry_variants(mention):
    comparison = compare_facts(
        f"Requirements: Production experience with {mention} is required.",
        [fact(8, "Commercial OpenTelemetry collector operations", "commercial")],
    )

    assert [(item.skill, item.status, item.importance) for item in comparison.requirements] == [
        ("OpenTelemetry", "commercial", "required"),
    ]


def test_candidate_fit_does_not_treat_ambiguous_otel_acronym_as_confirmed_skill():
    assert "OpenTelemetry" not in extract_technical_requirements("Requirements: OTel required.")


def test_recognizes_common_remote_job_board_requirement_headings():
    text = clean_html_text(
        """
        &lt;h3&gt;What we are looking for in you&lt;/h3&gt;
        &lt;ul&gt;
        &lt;li&gt;Experience with Linux troubleshooting&lt;/li&gt;
        &lt;li&gt;Bash scripting and networking&lt;/li&gt;
        &lt;/ul&gt;
        &lt;h3&gt;Nice-to-have skills&lt;/h3&gt;
        &lt;p&gt;Kubernetes&lt;/p&gt;
        """
    )

    importance = extract_requirement_importance(text)

    assert importance["Linux"] == "required"
    assert importance["Bash"] == "required"
    assert importance["Kubernetes"] == "preferred"

    curly_apostrophe = clean_html_text(
        "&lt;h3&gt;What you’ll bring&lt;/h3&gt;"
        "&lt;p&gt;Linux troubleshooting&lt;/p&gt;"
    )
    assert extract_requirement_importance(curly_apostrophe)["Linux"] == "required"


def test_comparison_preserves_candidate_fact_experience_types():
    vacancy = """
    Linux
    Docker
    Kubernetes
    Terraform
    Ansible
    Nginx
    Bash
    Prometheus
    Grafana
    Helm
    ArgoCD
    """

    facts = [
        fact(
            1,
            "More than two years of system administration experience with Windows and Linux.",
            "commercial",
        ),
        fact(
            2,
            "Practical Linux troubleshooting with systemd and logs.",
            "unknown",
        ),
        fact(
            3,
            "Practical Docker and Docker Compose experience in labs and personal projects.",
            "lab",
        ),
        fact(
            4,
            "Configured Nginx reverse proxy.",
            "unknown",
        ),
        fact(
            5,
            "Bash scripting experience and basic Python.",
            "unknown",
        ),
        fact(
            7,
            "Prometheus and Grafana are being developed through study and lab practice.",
            "learning",
        ),
        fact(
            8,
            "Kubernetes, Terraform and Ansible are developing skills.",
            "learning",
        ),
    ]

    result = compare_facts(vacancy, facts)

    assert result.skills_for("commercial") == ["Linux"]
    assert result.skills_for("lab") == ["Docker"]

    assert set(result.skills_for("learning")) == {
        "Kubernetes",
        "Ansible",
        "Terraform",
        "Prometheus",
        "Grafana",
    }

    assert set(result.skills_for("unknown")) == {
        "Nginx",
        "Bash",
    }

    assert set(result.skills_for("missing")) == {
        "Helm",
        "ArgoCD",
    }


def test_commercial_fact_wins_over_unknown_fact_for_same_skill():
    facts = [
        fact(
            1,
            "Commercial system administration with Linux.",
            "commercial",
        ),
        fact(
            2,
            "Linux troubleshooting practice.",
            "unknown",
        ),
    ]

    result = compare_facts("Requirements: Linux.", facts)

    assert result.total == 1
    assert result.present == 1
    assert result.skills_for("commercial") == ["Linux"]
    assert result.skills_for("unknown") == []


def test_missing_does_not_invent_candidate_experience():
    facts = [
        fact(
            1,
            "Linux system administration.",
            "commercial",
        ),
    ]

    result = compare_facts(
        "Requirements: Linux, Terraform, Helm and ArgoCD.",
        facts,
    )

    assert result.skills_for("commercial") == ["Linux"]
    assert set(result.skills_for("missing")) == {
        "Terraform",
        "Helm",
        "ArgoCD",
    }


def test_later_explicit_requirement_is_not_masked_by_earlier_negation_in_clause():
    comparison = compare_facts(
        "Requirements: Linux is not required, but Linux knowledge is mandatory.",
        [],
    )

    assert [(item.skill, item.status, item.importance) for item in comparison.requirements] == [
        ("Linux", "missing", "required"),
    ]


@pytest.mark.parametrize("phrase", [
    "Linux experience would be an advantage.",
    "Linux experience is beneficial.",
    "Linux будет преимуществом.",
])
def test_skill_experience_that_would_be_an_advantage_is_preferred(phrase):
    comparison = compare_facts(
        f"Requirements: {phrase}",
        [],
    )

    assert [(item.skill, item.importance) for item in comparison.requirements] == [
        ("Linux", "preferred"),
    ]


@pytest.mark.parametrize("phrase", [
    "Linux желательно.",
    "Знание Linux желательно.",
    "Желательно знание Linux.",
])
def test_russian_desirable_skill_wording_is_preferred(phrase):
    comparison = compare_facts(f"Requirements: {phrase}", [])

    assert [(item.skill, item.importance) for item in comparison.requirements] == [
        ("Linux", "preferred"),
    ]


def test_render_fact_comparison_separates_truth_levels():
    from app.telegram.vacancy_view import render_fact_comparison

    facts = [
        fact(1, "Commercial Linux administration.", "commercial"),
        fact(2, "Docker personal lab.", "lab"),
        fact(3, "Kubernetes study.", "learning"),
        fact(4, "Nginx configuration.", "unknown"),
    ]

    comparison = compare_facts(
        "Linux Docker Kubernetes Nginx Terraform",
        facts,
    )

    payload = {
        "job": SimpleNamespace(
            id=24,
            title="DevOps Engineer",
        ),
        "comparison": comparison,
    }

    text = render_fact_comparison(payload)

    assert "Сравнение с профилем" in text
    assert "Коммерческий опыт" in text
    assert "Lab / personal projects" in text
    assert "Изучается" in text
    assert "Тип опыта не указан" in text
    assert "Не подтверждено Candidate Facts" in text
    assert "Linux" in text
    assert "Docker" in text
    assert "Kubernetes" in text
    assert "Nginx" in text
    assert "Terraform" in text
    assert "4/5" in text


def test_comparison_links_matched_skills_to_fact_ids_and_escapes_provenance():
    from app.telegram.vacancy_view import render_fact_comparison

    source_fact = fact(42, "Commercial Linux administration.", "commercial")
    source_fact.provenance = "resume_import<script>"
    comparison = compare_facts("Requirements: Linux", [source_fact])
    text = render_fact_comparison({
        "job": SimpleNamespace(id=124, title="Linux Administrator"),
        "comparison": comparison,
        "facts": [source_fact],
    })

    assert "Linux <i>(факт #42 · resume_import&lt;script&gt;)</i>" in text
    assert "командами /facts и /fact" in text
    assert "<script>" not in text


def test_render_fact_comparison_explains_alternative_score():
    from app.telegram.vacancy_view import render_fact_comparison

    comparison = compare_facts("Requirements: Linux or Windows", [
        fact(1, "Linux administration", "commercial"),
    ])
    text = render_fact_comparison({
        "job": SimpleNamespace(id=25, title="Infrastructure Engineer"),
        "comparison": comparison,
    })

    assert "Linux или Windows" in text
    assert "отдельные упоминания навыков" in text

    preferred = compare_facts(
        "Requirements: Linux. Nice to have: Docker or Kubernetes.",
        [fact(1, "Linux administration", "commercial")],
    )
    preferred_text = render_fact_comparison({
        "job": SimpleNamespace(id=26, title="Infrastructure Engineer"),
        "comparison": preferred,
    })
    assert "Docker или Kubernetes" in preferred_text


def test_alternative_group_does_not_cross_importance_boundaries():
    comparison = compare_facts(
        "Nice to have: Linux or Windows.\nRequirements: Linux.",
        [],
    )

    assert comparison.preferred_alternative_groups == ()
    assert [(item.skill, item.importance) for item in comparison.requirements] == [
        ("Linux", "required"),
        ("Windows", "preferred"),
    ]


def test_three_explicit_alternatives_are_one_scoring_choice():
    from app.matching.technical_score import score_technical_v2

    text = "Requirements: Linux or Windows or Docker. Terraform is also required."
    comparison = compare_facts(text, [fact(1, "Commercial Linux administration", "commercial")])

    assert comparison.alternative_groups == (("Linux", "Windows", "Docker"),)
    assert score_technical_v2(text, [fact(1, "Commercial Linux administration", "commercial")]) == 50


def test_three_option_alternative_requires_each_skill_once():
    comparison = compare_facts(
        "Requirements: Linux or Windows or Linux.",
        [fact(1, "Commercial Linux administration", "commercial")],
    )

    assert comparison.alternative_groups == ()


def test_oxford_comma_skill_alternatives_are_one_choice():
    comparison = compare_facts(
        "Requirements: Linux, Windows, or Docker.",
        [fact(1, "Commercial Linux administration", "commercial")],
    )

    assert comparison.alternative_groups == (("Linux", "Windows", "Docker"),)


def test_comma_separated_required_skills_are_not_alternatives():
    comparison = compare_facts("Requirements: Linux, Kubernetes.", [])

    assert comparison.alternative_groups == ()


def test_parenthesized_alternative_can_coexist_with_an_independent_requirement():
    from app.matching.technical_score import score_technical_v2

    text = "Requirements: Linux and (Docker or Kubernetes)."
    comparison = compare_facts(text, [fact(1, "Commercial Linux and Docker administration", "commercial")])

    assert comparison.alternative_groups == (("Docker", "Kubernetes"),)
    assert score_technical_v2(
        text, [fact(1, "Commercial Linux and Docker administration", "commercial")]
    ) == 100


def test_nested_parenthesized_or_chain_is_one_choice_beside_an_independent_requirement():
    from app.matching.resume_diff import compare_resume_coverage
    from app.matching.technical_score import score_technical_v2

    text = "Requirements: Linux and (Docker or (Kubernetes or ArgoCD))."
    facts = [
        fact(1, "Commercial Linux administration", "commercial"),
        fact(2, "Commercial ArgoCD operations", "commercial"),
    ]
    comparison = compare_facts(text, facts)

    assert comparison.alternative_groups == (("Docker", "Kubernetes", "ArgoCD"),)
    assert score_technical_v2(text, facts) == 100
    coverage = compare_resume_coverage(comparison, "Linux administration and ArgoCD operations")
    assert len(coverage["alternative_groups"]) == 1
    assert coverage["alternative_groups"][0]["status"] == "confirmed"


@pytest.mark.parametrize("text", [
    "Requirements: Linux and (Docker or (Kubernetes and ArgoCD)).",
    "Requirements: Linux and (Docker or (Kubernetes or ArgoCD)); Kubernetes also required.",
])
def test_nested_compound_or_groups_stay_unclassified_when_ambiguous(text):
    assert compare_facts(text, []).alternative_groups == ()


@pytest.mark.parametrize("text", [
    "Requirements: Linux or (Docker or Kubernetes).",
    "Requirements: (Linux or Docker) or Kubernetes.",
    "Requirements: Linux or ((Docker or Kubernetes)).",
])
def test_pure_or_parentheses_form_one_nonoverlapping_scoring_choice(text):
    from app.matching.technical_score import score_technical_v2
    from app.matching.resume_diff import compare_resume_coverage

    facts = [fact(1, "Linux administration", "commercial")]
    comparison = compare_facts(text, facts)

    assert comparison.alternative_groups == (("Linux", "Docker", "Kubernetes"),)
    assert score_technical_v2(text, facts) == 100
    coverage = compare_resume_coverage(comparison, "Linux administration")
    assert len(coverage["alternative_groups"]) == 1
    assert coverage["alternative_groups"][0]["status"] == "confirmed"


@pytest.mark.parametrize("text", [
    "Requirements: Linux and (Docker/Kubernetes).",
    "Requirements: Linux and (Docker or Kubernetes or Docker).",
    "Requirements: Linux and (Docker or Kubernetes); Docker also required.",
    "Responsibilities: Linux and (Docker or Kubernetes).",
])
def test_parenthesized_alternatives_remain_conservative(text):
    comparison = compare_facts(text, [])

    assert comparison.alternative_groups == ()


def test_render_fact_comparison_shows_language_separately_from_technical_score():
    from app.matching.language_fit import compare_english_level
    from app.telegram.vacancy_view import render_fact_comparison

    payload = {
        "job": SimpleNamespace(id=27, title="Support Engineer"),
        "comparison": compare_facts("English level B2", []),
        "language_fit": compare_english_level("English level B2 preferred", "B1"),
    }

    text = render_fact_comparison(payload)

    assert "Явный уровень английского" in text
    assert "Уровень вакансии: <b>B2</b>" in text
    assert "Статус: указан как преимущество" in text
    assert "Профиль: <b>B1</b>" in text
    assert "уровень профиля ниже" in text
    assert "не меняет техническую оценку" in text


def test_vacancy_details_keyboard_has_compare_button():
    from app.telegram.ui import vacancy_details_keyboard

    keyboard = vacancy_details_keyboard(24)

    button = keyboard.inline_keyboard[0][0]

    assert button.text == "🧩 Сравнить с профилем"
    assert button.callback_data == "compare:24"


def test_requirement_importance_separates_sections():
    text = """
    Чем предстоит заниматься:
    GitLab CI и Helm.

    Требования:
    Linux
    Docker
    Kubernetes
    Terraform

    Приветствуется:
    Prometheus
    Grafana
    """

    importance = extract_requirement_importance(text)

    assert importance["Linux"] == "required"
    assert importance["Docker"] == "required"
    assert importance["Kubernetes"] == "required"
    assert importance["Terraform"] == "required"
    assert importance["Prometheus"] == "preferred"
    assert importance["Grafana"] == "preferred"
    assert importance["GitLab CI"] == "unknown"
    assert importance["Helm"] == "unknown"


def test_required_importance_wins_over_preferred():
    text = """
    Требования:
    Terraform

    Приветствуется:
    Terraform
    Grafana
    """

    importance = extract_requirement_importance(text)

    assert importance["Terraform"] == "required"
    assert importance["Grafana"] == "preferred"


def test_unstructured_technology_mentions_remain_unknown():
    importance = extract_requirement_importance(
        "Linux Docker Kubernetes"
    )

    assert importance["Linux"] == "unknown"
    assert importance["Docker"] == "unknown"
    assert importance["Kubernetes"] == "unknown"


def test_inline_requirement_headings_are_supported():
    text = """
    Requirements: Linux, Docker and Kubernetes
    Nice to have: Grafana and Prometheus
    """

    importance = extract_requirement_importance(text)

    assert importance["Linux"] == "required"
    assert importance["Docker"] == "required"
    assert importance["Kubernetes"] == "required"
    assert importance["Grafana"] == "preferred"
    assert importance["Prometheus"] == "preferred"


def test_multiple_section_headings_on_one_line_keep_preferred_skills_optional():
    english = extract_requirement_importance(
        "Requirements: Linux. Nice to have: Docker. Responsibilities: Kubernetes."
    )
    russian = extract_requirement_importance(
        "Требования: Linux; Будет плюсом: Docker; Обязанности: Kubernetes"
    )

    for importance in (english, russian):
        assert importance["Linux"] == "required"
        assert importance["Docker"] == "preferred"
        assert importance["Kubernetes"] == "unknown"


def test_common_separators_match_canonical_skills():
    skills = extract_technical_requirements("GitLab_CI Docker_Compose Active_Directory")
    assert "GitLab CI" in skills
    assert "Docker Compose" in skills
    assert "Active Directory" in skills


def test_docker_compose_alternative_is_one_choice_without_embedded_docker_duplicate():
    comparison = compare_facts("Requirements: Docker Compose or Kubernetes.", [])

    assert {item.skill for item in comparison.requirements} == {"Docker Compose", "Kubernetes"}
    assert comparison.alternative_groups == (("Docker Compose", "Kubernetes"),)


def test_wildlife_elk_mention_does_not_match_elk_stack_but_explicit_stack_does():
    wildlife = extract_technical_requirements("Requirements: knowledge of elk migration patterns.")
    technical = extract_technical_requirements(
        "Requirements: ELK Stack or Elasticsearch, Logstash and Kibana."
    )
    explicit_acronym = extract_technical_requirements("Requirements: ELK is used for log aggregation.")

    assert "ELK" not in wildlife
    assert "ELK" in technical
    assert "ELK" in explicit_acronym


def test_comparison_keeps_only_strongest_matching_fact_ids():
    facts = [
        fact(30, "Linux administration.", "commercial"),
        fact(20, "Linux troubleshooting.", "unknown"),
        fact(10, "Commercial Linux operations.", "commercial"),
    ]

    result = compare_facts("Requirements: Linux.", facts)
    item = result.requirements[0]

    assert item.status == "commercial"
    assert item.fact_ids == (10, 30)


def test_non_persisted_fact_id_is_not_reported():
    result = compare_facts(
        "Requirements: Linux.",
        [fact(0, "Linux administration.", "commercial")],
    )

    item = result.requirements[0]
    assert item.status == "commercial"
    assert item.fact_ids == ()
