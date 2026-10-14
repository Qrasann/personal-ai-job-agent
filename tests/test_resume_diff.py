import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.matching.fact_comparison import compare_facts
from app.matching.resume_diff import compare_resume_coverage
from app.telegram.vacancy_view import render_resume_diff
from app import services


def _fact(fact_id, value, experience_type="commercial"):
    return SimpleNamespace(
        id=fact_id,
        value=value,
        experience_type=experience_type,
        active=True,
        deleted_at=None,
    )


def test_resume_diff_separates_confirmed_resume_and_unconfirmed_evidence():
    facts = [
        _fact(1, "Commercial Linux administration"),
        _fact(2, "Terraform learning", "learning"),
    ]
    comparison = compare_facts(
        "Requirements: Linux, Docker, Terraform and Kubernetes.", facts
    )

    result = compare_resume_coverage(comparison, "Linux administrator; Kubernetes")

    assert result == {
        "supported_in_resume": ("Linux",),
        "supported_missing_from_resume": ("Terraform",),
        "resume_only_unconfirmed": ("Kubernetes",),
        "missing_from_both": ("Docker",),
    }


def test_resume_diff_view_escapes_labels_and_disclaims_generated_claims():
    text = render_resume_diff({
        "job": SimpleNamespace(id=25, title="DevOps <Lead>"),
        "resume": SimpleNamespace(id=7, name="CV <draft>"),
        "resume_diff": {
            "supported_in_resume": ("Linux",),
            "supported_missing_from_resume": ("Terraform",),
            "resume_only_unconfirmed": ("Kubernetes",),
            "missing_from_both": (),
        },
    })

    assert "DevOps &lt;Lead&gt;" in text
    assert "CV &lt;draft&gt;" in text
    assert "не редактирует резюме" in text
    assert "<draft>" not in text


def test_resume_diff_service_uses_only_selected_active_profile_resume(monkeypatch):
    match = SimpleNamespace(profile_id=3, resume_id=5)
    payload = {
        "match": match,
        "comparison": compare_facts("Requirements: Linux", [_fact(1, "Linux")]),
    }
    monkeypatch.setattr(services, "get_vacancy_comparison", AsyncMock(return_value=payload))
    monkeypatch.setattr(services.repo, "list_resumes", AsyncMock(return_value=[
        SimpleNamespace(id=4, active=True, deleted_at=None, content="Linux", name="other"),
        SimpleNamespace(id=5, active=True, deleted_at=None, content="Linux", name="selected"),
        SimpleNamespace(id=6, active=False, deleted_at=None, content="Linux", name="inactive"),
    ]))

    result = asyncio.run(services.get_resume_diff(8, 25))

    assert result["resume"].id == 5
    assert result["resume_diff"]["supported_in_resume"] == ("Linux",)
