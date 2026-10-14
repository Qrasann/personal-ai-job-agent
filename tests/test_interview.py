from types import SimpleNamespace

from app.agents.interview import build_interview_plan
from app.matching.fact_comparison import compare_facts
from app.telegram.vacancy_view import render_interview_plan


def _fact(fact_id, value, experience_type):
    return SimpleNamespace(
        id=fact_id, value=value, experience_type=experience_type,
        active=True, deleted_at=None,
    )


def test_interview_plan_uses_vacancy_importance_and_candidate_fact_state():
    facts = [_fact(1, "Linux system administration", "lab")]
    comparison = compare_facts(
        "Requirements: Linux, Docker. Nice to have: Nginx.",
        facts,
    )

    plan = build_interview_plan(comparison)

    assert [item["skill"] for item in plan] == ["Docker", "Linux", "Nginx"]
    assert [item["importance"] for item in plan] == ["required", "required", "preferred"]
    assert plan[0]["candidate_status"] == "missing"
    assert plan[1]["candidate_status"] == "lab"
    assert all(item["scenario"] and item["criteria"] for item in plan)


def test_interview_plan_is_bounded_and_only_uses_curated_exercises():
    comparison = compare_facts(
        "Requirements: Linux, Docker, Nginx, Kubernetes, PostgreSQL, Networking, CI/CD.",
        [],
    )

    plan = build_interview_plan(comparison, limit=3)

    assert len(plan) == 3
    assert {item["skill"] for item in plan} <= {
        "Linux", "Docker", "Nginx", "Kubernetes", "PostgreSQL", "Networking", "CI/CD",
    }


def test_interview_view_labels_templates_and_escapes_vacancy_title():
    text = render_interview_plan(
        SimpleNamespace(id=9, title="DevOps <Lead>"),
        ({
            "skill": "Linux", "importance": "required", "candidate_status": "commercial",
            "scenario": "Diagnose CPU pressure", "task": "Explain safe triage",
            "criteria": ("Inspect processes", "Check logs"),
        },),
    )

    assert "DevOps &lt;Lead&gt;" in text
    assert "Diagnose CPU pressure" in text
    assert "Candidate Fact: commercial" in text
    assert "не предсказание вопросов" in text
    assert "<Lead>" not in text


def test_interview_agent_covers_dns_tls_and_safe_security_response():
    comparison = compare_facts(
        "Requirements: DNS, TLS and cybersecurity.",
        [],
    )

    plan = build_interview_plan(comparison)
    by_skill = {item["skill"]: item for item in plan}

    assert {"DNS", "TLS", "Security Operations"} <= set(by_skill)
    assert "TTL" in by_skill["DNS"]["criteria"][1]
    assert "SNI" in by_skill["TLS"]["task"]
    assert any("Preserve logs" in item for item in by_skill["Security Operations"]["criteria"])


def test_interview_agent_has_curated_exercises_for_infrastructure_as_code_cloud_and_observability():
    comparison = compare_facts(
        "Requirements: Terraform, Ansible, AWS, Grafana and Helm.",
        [],
    )

    plan = build_interview_plan(comparison, limit=8)
    by_skill = {item["skill"]: item for item in plan}

    assert set(by_skill) == {"Terraform", "Ansible", "AWS", "Grafana", "Helm"}
    assert "Do not apply" in by_skill["Terraform"]["criteria"][0]
    assert "idempotent" in by_skill["Ansible"]["criteria"][2]
    assert "CloudTrail" in by_skill["AWS"]["criteria"][2]
    assert "missing samples" in by_skill["Grafana"]["criteria"][1]
    assert "rendered resources" in by_skill["Helm"]["criteria"][1]
