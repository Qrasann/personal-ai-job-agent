from types import SimpleNamespace

from app.matching.fact_comparison import (
    compare_facts,
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


def test_vacancy_details_keyboard_has_compare_button():
    from app.telegram.ui import vacancy_details_keyboard

    keyboard = vacancy_details_keyboard(24)

    button = keyboard.inline_keyboard[0][0]

    assert button.text == "🧩 Сравнить с профилем"
    assert button.callback_data == "compare:24"
