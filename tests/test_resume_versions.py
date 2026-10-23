import asyncio
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.domain.resume_versions import approved_version_rules, draft_version_rules, version_metadata
from app.database.models import Job, ResumeProfile
from app.matching.engine import choose_resume
from app.telegram import handlers


def test_legacy_resume_is_compatible_and_new_version_requires_approval():
    assert version_metadata({}) == {"status": "approved", "legacy": True}
    rules = draft_version_rules({"format": "ats"}, parent_id=7)
    assert rules == {"format": "ats", "cv_version_v1": {"status": "draft", "parent_id": 7}}
    approved = approved_version_rules(rules, now=datetime(2026, 10, 23, tzinfo=UTC))
    assert approved["format"] == "ats"
    assert approved["cv_version_v1"] == {
        "status": "approved", "parent_id": 7, "approved_at": "2026-10-23T00:00:00Z",
    }


def test_draft_resume_is_never_selected_for_matching_or_application_preparation():
    job = Job(title="SRE", company="Example", description="Kubernetes", country="US")
    approved = ResumeProfile(id=1, profile_id=1, name="Base", role="DevOps", language="en", rules={})
    draft = ResumeProfile(
        id=2, profile_id=1, name="Tailored", role="SRE", language="en",
        content="Kubernetes", rules=draft_version_rules({}, parent_id=1),
    )
    assert choose_resume(job, [approved, draft]) == 1


def test_resume_list_discloses_draft_and_approved_state(monkeypatch):
    rows = [
        SimpleNamespace(id=1, name="Legacy", role="DevOps", language="en", source="imported", rules={}),
        SimpleNamespace(
            id=2, name="SRE draft", role="SRE", language="en", source="version",
            rules=draft_version_rules({}, parent_id=1),
        ),
    ]
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=5)))
    monkeypatch.setattr(handlers.repo, "active_profile", AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers.repo, "list_resumes", AsyncMock(return_value=rows))
    message = SimpleNamespace(answer=AsyncMock())

    asyncio.run(handlers.resumes(message))

    rendered = message.answer.await_args.args[0]
    assert "Legacy — DevOps — en — imported — ✅ approved" in rendered
    assert "SRE draft — SRE — en — version — 📝 draft" in rendered


def test_resume_duplicate_and_approve_are_owner_profile_scoped(monkeypatch):
    profile = SimpleNamespace(id=7)
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=5)))
    monkeypatch.setattr(handlers.repo, "active_profile", AsyncMock(return_value=profile))
    duplicate = AsyncMock(return_value=SimpleNamespace(id=12))
    approve = AsyncMock(return_value=True)
    monkeypatch.setattr(handlers.repo, "duplicate_resume_version", duplicate)
    monkeypatch.setattr(handlers.repo, "approve_resume_version", approve)

    duplicate_message = SimpleNamespace(text="/resumeduplicate 3 SRE EN", answer=AsyncMock())
    asyncio.run(handlers.resume_duplicate_command(duplicate_message))
    duplicate.assert_awaited_once_with(7, 3, "SRE EN")
    assert "/resumeapprove 12" in duplicate_message.answer.await_args.args[0]

    approve_message = SimpleNamespace(text="/resumeapprove 12", answer=AsyncMock())
    asyncio.run(handlers.resume_approve_command(approve_message))
    approve.assert_awaited_once_with(7, 12)
    assert "утверждена" in approve_message.answer.await_args.args[0]
