from types import SimpleNamespace

from app.domain.application_package import snapshot_vacancy
from app.telegram.vacancy_view import render_application_export


def test_export_retains_original_posting_after_live_job_changes():
    job = SimpleNamespace(title="Original role", company="Original company", description="Original requirements\nLinux")
    application = SimpleNamespace(
        id=7, created_at=None, status="prepared", source_id="hh",
        external_url="https://example.invalid/receipt", resume_id=None,
        resume_external_id=None, resume_snapshot="", message="Saved letter",
        vacancy_snapshot=snapshot_vacancy(job, source_url="https://example.invalid/vacancy"),
    )
    job.title, job.company, job.description = "Changed role", "Changed company", "Changed requirements"

    exported = render_application_export(application)

    assert "Saved vacancy: Original role — Original company" in exported
    assert "Original requirements\nLinux" in exported
    assert "Saved vacancy URL: https://example.invalid/vacancy" in exported
    assert "Recorded external URL: https://example.invalid/receipt" in exported
    assert "Changed" not in exported


def test_missing_posting_fields_remain_unknown_in_snapshot_export():
    application = SimpleNamespace(
        id=8, created_at=None, status="prepared", source_id="manual",
        external_url=None, resume_id=None, resume_external_id=None,
        resume_snapshot="", message="",
        vacancy_snapshot=snapshot_vacancy(SimpleNamespace(title="Role", company=None, description=None)),
    )
    exported = render_application_export(application)
    assert "Saved vacancy: Role — not recorded" in exported
    assert "Saved vacancy URL: not recorded" in exported
    assert "No vacancy description snapshot" in exported
