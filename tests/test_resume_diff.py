import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.matching.fact_comparison import compare_facts
from app.matching.resume_diff import compare_resume_coverage
from app.telegram.vacancy_view import render_application_package, render_resume_diff
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


def test_prepare_match_returns_evidence_checklist_without_external_submission(monkeypatch):
    resume = SimpleNamespace(id=5, active=True, deleted_at=None, content="Linux", name="CV")
    monkeypatch.setattr(services.repo, "get_match", AsyncMock(return_value=SimpleNamespace(
        user_id=8, job_id=25, profile_id=3, resume_id=5,
    )))
    monkeypatch.setattr(services.repo, "get_job", AsyncMock(return_value=SimpleNamespace(
        id=25, title="Linux admin", company="Example", description="Requirements: Linux and Docker",
    )))
    monkeypatch.setattr(services.repo, "list_facts", AsyncMock(return_value=[_fact(1, "Linux administration")]))
    monkeypatch.setattr(services.repo, "list_resumes", AsyncMock(return_value=[resume]))
    monkeypatch.setattr(services.repo, "source_ref", AsyncMock(return_value=None))
    save_application = AsyncMock()
    monkeypatch.setattr(services.repo, "save_application", save_application)
    monkeypatch.setattr(services, "make_cover_letter", lambda job, facts, chosen: "Grounded draft")

    result = asyncio.run(services.prepare_match(12, 8))

    assert result["cover_letter"] == "Grounded draft"
    assert result["resume_diff"]["supported_in_resume"] == ("Linux",)
    assert result["resume_diff"]["missing_from_both"] == ("Docker",)
    save_application.assert_not_awaited()


def test_application_package_preview_escapes_and_rejects_unsafe_links():
    text = render_application_package({
        "job": SimpleNamespace(id=25, title="DevOps <Lead>", company="Example"),
        "resume": SimpleNamespace(id=5, name="CV"),
        "resume_diff": {
            "supported_in_resume": ("Linux",),
            "supported_missing_from_resume": (),
            "resume_only_unconfirmed": (),
            "missing_from_both": ("Docker",),
        },
        "url": "javascript:alert(1)",
        "cover_letter": "Draft <script>",
    })

    assert "DevOps &lt;Lead&gt;" in text
    assert "<a href=\"javascript:" not in text
    assert "не отправлен" in text
    assert "Draft &lt;script&gt;" in text


def test_application_package_preview_is_bounded_for_telegram():
    text = render_application_package({
        "job": SimpleNamespace(id=25, title="D" * 500, company="C" * 500),
        "resume": SimpleNamespace(id=5, name="R" * 500),
        "resume_diff": {
            "supported_in_resume": (),
            "supported_missing_from_resume": (),
            "resume_only_unconfirmed": (),
            "missing_from_both": (),
        },
        "url": "https://example.com/" + "x" * 2000,
        "cover_letter": "draft " * 2000,
    })

    assert len(text) < 4096
