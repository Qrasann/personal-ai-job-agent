from app.matching.fact_comparison import extract_requirement_importance


def test_synergy_real_headings_classify_preferred_and_neutral_sections():
    text = """В ПРОЦЕССЕ РАБОТЫ НЕОБХОДИМО
Jitsi
Kubernetes
ЧТО БУДЕТ ВАШИМ ПРЕИМУЩЕСТВОМ
Linux
Docker
Ansible
Плюсом будет:
Nginx
Prometheus
Grafana
ДЛЯ ВАС МЫ ПРЕДЛАГАЕМ
PostgreSQL
"""

    importance = extract_requirement_importance(text)

    assert importance["Jitsi"] == "unknown"
    assert importance["Kubernetes"] == "unknown"

    assert importance["Linux"] == "preferred"
    assert importance["Docker"] == "preferred"
    assert importance["Ansible"] == "preferred"
    assert importance["Nginx"] == "preferred"
    assert importance["Prometheus"] == "preferred"
    assert importance["Grafana"] == "preferred"

    assert importance["PostgreSQL"] == "unknown"


def test_explicit_not_required_skill_inside_required_heading_is_not_a_must_have():
    importance = extract_requirement_importance(
        "Requirements: No Kubernetes experience required. Terraform is required."
    )
    assert importance["Kubernetes"] == "unknown"
    assert importance["Terraform"] == "required"


def test_no_skill_required_short_form_remains_unknown():
    importance = extract_requirement_importance(
        "Requirements: No Kubernetes required. Docker is required."
    )
    assert importance["Kubernetes"] == "unknown"
    assert importance["Docker"] == "required"


def test_inline_skill_level_negation_does_not_suppress_other_required_skill():
    importance = extract_requirement_importance(
        "Must have: Kubernetes is not required; Docker is mandatory."
    )
    assert importance["Kubernetes"] == "unknown"
    assert importance["Docker"] == "required"


def test_skill_specific_plus_language_in_requirements_heading_is_preferred():
    importance = extract_requirement_importance(
        "Requirements: Kubernetes is a plus. Terraform is required."
    )
    assert importance["Kubernetes"] == "preferred"
    assert importance["Terraform"] == "required"


def test_russian_skill_specific_preference_overrides_broad_requirements_heading():
    importance = extract_requirement_importance(
        "Требования: Kubernetes будет плюсом. Docker обязателен."
    )
    assert importance["Kubernetes"] == "preferred"
    assert importance["Docker"] == "required"
