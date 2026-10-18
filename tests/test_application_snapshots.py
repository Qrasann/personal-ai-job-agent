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
    assert "No source-scoped relocation evidence snapshot is available" in exported


def test_application_snapshot_freezes_relocation_evidence_and_exports_provenance():
    job = SimpleNamespace(title="Role", company="Example", description="Original posting")
    evidence = {
        "schema": "relocation_evidence_v1",
        "captured_at": "2026-10-15T12:30:00+00:00",
        "fields": {
            "visa_sponsorship": {
                "status": "confirmed", "value": False,
                "source_id": "synthetic_fixture", "source_url": "https://example.invalid/job",
                "excerpt": "Visa sponsorship is not available",
                "captured_at": "2026-10-15T12:30:00+00:00", "confidence": "explicit_text",
            },
        },
    }
    snapshot = snapshot_vacancy(
        job, source_url="https://example.invalid/job", relocation_evidence=evidence,
    )
    application = SimpleNamespace(
        id=9, created_at=None, status="prepared", source_id="synthetic_fixture",
        external_url=None, resume_id=None, resume_external_id=None,
        resume_snapshot="", message="Draft", vacancy_snapshot=snapshot,
    )
    evidence["fields"]["visa_sponsorship"]["excerpt"] = "changed after preparation"

    exported = render_application_export(application)

    assert "Visa sponsorship is not available" in exported
    assert "changed after preparation" not in exported
    assert "2026-10-15T12:30:00+00:00" in exported


def test_package_export_retains_selected_provider_posting_id():
    job = SimpleNamespace(title="Engineer", company="Example", description="Source text")
    snapshot = snapshot_vacancy(
        job, source_id="jobs_ge", source_job_id="posting-123",
        source_url="https://example.invalid/jobs_ge/posting-123",
    )
    application = SimpleNamespace(
        id=10, created_at=None, status="prepared", source_id="jobs_ge",
        external_url=None, resume_id=None, resume_external_id=None,
        resume_snapshot="", message="Draft", vacancy_snapshot=snapshot,
    )

    exported = render_application_export(application)

    assert "Saved posting source: jobs_ge" in exported
    assert "Saved provider posting ID: posting-123" in exported
    assert snapshot["source_id"] == "jobs_ge"
    assert snapshot["source_job_id"] == "posting-123"
