import asyncio
from html.parser import HTMLParser
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.domain.source_posting import posting_snapshot_digest
from app.matching.fact_comparison import compare_facts
from app.matching.resume_diff import compare_resume_coverage
from app.telegram.vacancy_view import render_application_export, render_application_package, render_applications, render_resume_diff
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
        "alternative_groups": (),
    }


def test_resume_diff_treats_alternative_skills_as_one_confirmed_requirement():
    comparison = compare_facts("Requirements: Linux or Docker.", [_fact(1, "Linux administration")])

    result = compare_resume_coverage(comparison, "Linux operations")

    assert result["supported_in_resume"] == ()
    assert result["missing_from_both"] == ()
    assert result["alternative_groups"] == ({
        "options": ("Linux", "Docker"),
        "status": "confirmed",
        "candidate_fact_options": ("Linux",),
        "resume_options": ("Linux",),
        "confirmed_options": ("Linux",),
        "unconfirmed_resume_options": (),
    },)


def test_resume_diff_does_not_cross_confirm_different_alternative_options():
    comparison = compare_facts("Requirements: Linux or Docker.", [_fact(1, "Linux administration")])

    result = compare_resume_coverage(comparison, "Docker operations")
    text = render_resume_diff({
        "job": SimpleNamespace(id=25, title="DevOps"),
        "resume": SimpleNamespace(id=7, name="CV"),
        "resume_diff": result,
    })

    group = result["alternative_groups"][0]
    assert group["status"] == "resume_unconfirmed"
    assert group["candidate_fact_options"] == ("Linux",)
    assert group["resume_options"] == ("Docker",)
    assert "совпадающего подтверждения нет" in text
    assert "Не найдено ни в резюме" not in text


def test_resume_diff_flags_extra_cv_option_without_matching_candidate_fact():
    comparison = compare_facts("Requirements: Linux or Docker.", [_fact(1, "Linux administration")])

    result = compare_resume_coverage(comparison, "Linux and Docker")
    text = render_resume_diff({
        "job": SimpleNamespace(id=25, title="DevOps"),
        "resume": SimpleNamespace(id=7, name="CV"),
        "resume_diff": result,
    })

    group = result["alternative_groups"][0]
    assert group["status"] == "confirmed"
    assert group["confirmed_options"] == ("Linux",)
    assert group["unconfirmed_resume_options"] == ("Docker",)
    assert "неподтверждённое: Docker" in text


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
    evidence = {"schema": "relocation_evidence_v1", "captured_at": "fixed", "fields": {}}
    monkeypatch.setattr(services.repo, "source_ref", AsyncMock(return_value=SimpleNamespace(
        raw={"relocation_evidence_v1": evidence}, url="https://example.invalid/job", source_id="fixture",
    )))
    save_application = AsyncMock()
    monkeypatch.setattr(services.repo, "save_application", save_application)
    monkeypatch.setattr(services, "make_cover_letter", lambda job, facts, chosen: "Grounded draft")

    result = asyncio.run(services.prepare_match(12, 8))

    assert result["cover_letter"] == "Grounded draft"
    assert result["resume_diff"]["supported_in_resume"] == ("Linux",)
    assert result["resume_diff"]["missing_from_both"] == ("Docker",)
    assert result["relocation_evidence"] == evidence
    save_application.assert_not_awaited()


def test_prepare_match_rejects_unapproved_cv_version(monkeypatch):
    from app.domain.resume_versions import draft_version_rules

    resume = SimpleNamespace(
        id=5, active=True, deleted_at=None, content="Linux", name="Draft",
        rules=draft_version_rules({}, parent_id=4),
    )
    monkeypatch.setattr(services.repo, "get_match", AsyncMock(return_value=SimpleNamespace(
        user_id=8, job_id=25, profile_id=3, resume_id=5,
    )))
    monkeypatch.setattr(services.repo, "get_job", AsyncMock(return_value=SimpleNamespace(
        id=25, title="Linux admin", company="Example", description="Linux",
    )))
    monkeypatch.setattr(services.repo, "source_ref", AsyncMock(return_value=None))
    monkeypatch.setattr(services.repo, "list_facts", AsyncMock(return_value=[]))
    monkeypatch.setattr(services.repo, "list_resumes", AsyncMock(return_value=[resume]))
    cover = AsyncMock()
    monkeypatch.setattr(services, "make_cover_letter", cover)

    with pytest.raises(RuntimeError, match="не утверждена"):
        asyncio.run(services.prepare_match(12, 8))
    cover.assert_not_awaited()


def test_prepare_match_uses_display_source_when_georgia_refs_share_a_job(monkeypatch):
    monkeypatch.setattr(services.repo, "get_match", AsyncMock(return_value=SimpleNamespace(
        user_id=8, job_id=25, profile_id=3, resume_id=None,
    )))
    monkeypatch.setattr(services.repo, "get_job", AsyncMock(return_value=SimpleNamespace(
        id=25, title="Engineer", company="Example", description="HR-only Linux",
    )))
    monkeypatch.setattr(services.repo, "list_facts", AsyncMock(return_value=[]))
    monkeypatch.setattr(services.repo, "list_resumes", AsyncMock(return_value=[]))
    refs = {
        source_id: SimpleNamespace(
            source_id=source_id, source_job_id=f"{source_id}-posting-25",
            url=f"https://example.invalid/{source_id}",
            raw={
                "relocation_evidence_v1": {"source": source_id},
                "normalized_posting_v1": {
                    "schema": "normalized_posting_v1",
                    "title": "Engineer", "company": "Example",
                    "description": f"{source_id} Docker requirements",
                },
            },
        )
        for source_id in ("hr_ge", "jobs_ge")
    }
    async def source_ref(_job_id, source_id=None):
        return refs.get(source_id) if source_id else refs["hr_ge"]
    monkeypatch.setattr(services.repo, "source_ref", source_ref)
    monkeypatch.setattr(services, "make_cover_letter", lambda job, *_: job.description)

    result = asyncio.run(services.prepare_match(12, 8))

    assert result["source"] == "jobs_ge"
    assert result["source_job_id"] == "jobs_ge-posting-25"
    assert result["url"] == "https://example.invalid/jobs_ge"
    assert result["relocation_evidence"] == {"source": "jobs_ge"}
    assert result["job"].description == "jobs_ge Docker requirements"
    assert result["cover_letter"] == "jobs_ge Docker requirements"


def test_prepare_match_uses_verified_hh_description_already_in_source_cache(monkeypatch):
    monkeypatch.setattr(services.repo, "get_match", AsyncMock(return_value=SimpleNamespace(
        user_id=8, job_id=25, profile_id=3, resume_id=None,
    )))
    monkeypatch.setattr(services.repo, "get_job", AsyncMock(return_value=SimpleNamespace(
        id=25, title="Engineer", company="Example", description="Canonical summary",
    )))
    monkeypatch.setattr(services.repo, "list_facts", AsyncMock(return_value=[]))
    monkeypatch.setattr(services.repo, "list_resumes", AsyncMock(return_value=[]))
    posting = {
        "schema": "normalized_posting_v1", "title": "Engineer",
        "company": "Example", "description": "HH card summary",
    }
    ref = SimpleNamespace(source_id="hh", url="https://hh.ru/vacancy/25", raw={
        "normalized_posting_v1": posting,
        "details_cache_v1": {"description": "Verified full HH requirements: Kubernetes"},
        "details_cache_posting_digest_v1": posting_snapshot_digest(posting),
    })
    monkeypatch.setattr(services.repo, "source_ref", AsyncMock(return_value=ref))
    monkeypatch.setattr(services, "make_cover_letter", lambda job, *_: job.description)

    result = asyncio.run(services.prepare_match(12, 8))

    assert result["job"].description == "Verified full HH requirements: Kubernetes"
    assert result["cover_letter"] == result["job"].description


@pytest.mark.parametrize("url", [
    "javascript:alert(1)", "https://[broken", "https://user:password@example.invalid/job",
    "https://example.invalid/" + "x" * 601,
])
def test_application_package_preview_escapes_and_rejects_unsafe_links(url):
    text = render_application_package({
        "job": SimpleNamespace(id=25, title="DevOps <Lead>", company="Example"),
        "resume": SimpleNamespace(id=5, name="CV"),
        "resume_diff": {
            "supported_in_resume": ("Linux",),
            "supported_missing_from_resume": (),
            "resume_only_unconfirmed": (),
            "missing_from_both": ("Docker",),
        },
        "url": url,
        "cover_letter": "Draft <script>",
    })

    assert "DevOps &lt;Lead&gt;" in text
    assert "<a href=" not in text
    assert "не отправлен" in text
    assert "Draft &lt;script&gt;" in text
    assert "Структурированный снимок условий источника не записан" in text


def test_application_package_preview_explains_alternative_group_consistency():
    text = render_application_package({
        "job": SimpleNamespace(id=25, title="DevOps", company="Example"),
        "resume": SimpleNamespace(id=5, name="CV"),
        "resume_diff": {
            "supported_in_resume": (),
            "supported_missing_from_resume": (),
            "resume_only_unconfirmed": (),
            "missing_from_both": (),
            "alternative_groups": ({
                "options": ("Linux", "Docker"),
                "status": "confirmed",
                "candidate_fact_options": ("Linux",),
                "resume_options": ("Linux",),
                "confirmed_options": ("Linux",),
            },),
        },
        "url": "https://example.com/job",
        "cover_letter": "Draft",
    })

    assert "один и тот же вариант есть в CV и Candidate Facts (Linux)" in text
    assert "Не найдено в CV и Candidate Facts: Linux, Docker" not in text


def test_application_package_does_not_claim_no_gaps_when_no_skills_were_recognized():
    text = render_application_package({
        "job": SimpleNamespace(id=25, title="Operations role", company="Example"),
        "resume": SimpleNamespace(id=5, name="CV"),
        "resume_diff": {},
        "url": "https://example.com/job",
        "cover_letter": "Draft",
    })

    assert "Технические требования из поддерживаемого словаря не распознаны" in text
    assert "Проверь полный текст вакансии вручную" in text
    assert "дополнительных расхождений нет" not in text


def test_application_package_preview_keeps_unconfirmed_extra_alternative_visible():
    text = render_application_package({
        "job": SimpleNamespace(id=25, title="DevOps", company="Example"),
        "resume": SimpleNamespace(id=5, name="CV"),
        "resume_diff": {
            "supported_in_resume": (),
            "supported_missing_from_resume": (),
            "resume_only_unconfirmed": (),
            "missing_from_both": (),
            "alternative_groups": ({
                "options": ("Linux", "Docker"),
                "status": "confirmed",
                "candidate_fact_options": ("Linux",),
                "resume_options": ("Linux", "Docker"),
                "confirmed_options": ("Linux",),
                "unconfirmed_resume_options": ("Docker",),
            },),
        },
        "url": "https://example.com/job",
        "cover_letter": "Draft",
    })

    assert "неподтверждённое: Docker" in text
    assert "дополнительных расхождений нет" not in text


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


def test_package_review_preserves_explicit_mobility_restrictions_and_unknowns():
    job = SimpleNamespace(
        id=25, title="Infrastructure role", company="Example", country="GE",
        description="No visa sponsorship. Must already have the right to work in Georgia.",
        visa_sponsorship=True, relocation=None,
    )
    text = render_application_package({"job": job, "resume_diff": {}})
    assert "Visa sponsorship: явно не предоставляется" in text
    assert "Помощь с переездом: не подтверждено вакансией" in text
    assert "Предварительное право на работу: явно требуется" in text
    assert "не подтверждают личную юридическую eligibility" in text
    assert "Черновик не отправлен" in text


def test_dense_package_review_keeps_selected_posting_link_and_identity():
    text = render_application_package({
        "job": SimpleNamespace(id=25, title="Engineer", company="Example", description="Role"),
        "resume": SimpleNamespace(id=5, name="CV"),
        "resume_diff": {"resume_only_unconfirmed": tuple("skill" * 40 for _ in range(40))},
        "source": "jobs_ge", "source_job_id": "posting-42",
        "url": "https://example.invalid/posting-42",
        "cover_letter": "Draft",
    })

    assert "Предпросмотр сокращён" in text
    assert "Выбранная публикация: jobs_ge · ID posting-42" in text
    assert '<a href="https://example.invalid/posting-42">' in text


def test_package_preview_respects_telegram_utf16_limit_with_emoji():
    alternative = {
        "options": ("Linux", "Docker"), "status": "resume_unconfirmed",
        "resume_options": ("😀" * 8,), "candidate_fact_options": ("Linux",),
    }
    text = render_application_package({
        "job": SimpleNamespace(id=25, title="Engineer", company="Example", description="Role"),
        "resume": SimpleNamespace(id=5, name="CV"),
        "resume_diff": {"alternative_groups": (alternative,) * 30},
        "source": "jobs_ge", "source_job_id": "posting-42",
        "url": "https://example.invalid/posting-42",
        "cover_letter": "😀" * 3000,
    })

    assert len(text.encode("utf-16-le")) // 2 <= 3700
    assert "Предпросмотр сокращён" in text
    assert "Черновик не отправлен" in text
    assert '<a href="https://example.invalid/posting-42">' in text


def test_package_preview_omits_link_when_html_escaping_makes_it_too_long():
    text = render_application_package({
        "job": SimpleNamespace(id=25, title="Engineer", company="Example", description="Role"),
        "resume_diff": {}, "cover_letter": "Draft",
        "url": "https://example.invalid/?" + "&" * 500,
    })

    assert "Ссылка слишком длинная для предпросмотра; открой /job 25" in text
    assert "<a href=" not in text
    assert len(text.encode("utf-16-le")) // 2 <= 3700


def test_dense_package_review_keeps_mobility_and_valid_html_within_message_limit():
    text = render_application_package({
        "job": SimpleNamespace(
            id=25, title="<&" * 100, company="<&" * 100, country="DE",
            description="We provide visa sponsorship and relocation assistance.",
        ),
        "resume": SimpleNamespace(id=5, name="<&" * 100),
        "resume_diff": {"resume_only_unconfirmed": tuple("<skill&>" * 50 for _ in range(20))},
        "cover_letter": "<draft&>" * 400,
        "url": "https://example.invalid/" + "a" * 2000,
    })
    assert len(text) <= 3700
    assert "Предпросмотр сокращён" in text
    assert "/resumediff 25" in text
    assert "Visa sponsorship: явно предлагается" in text
    assert "Помощь с переездом: явно предлагается" in text
    assert "Черновик не отправлен" in text

    class BalancedHTML(HTMLParser):
        def __init__(self):
            super().__init__()
            self.stack = []

        def handle_starttag(self, tag, attrs):
            self.stack.append(tag)

        def handle_endtag(self, tag):
            assert self.stack.pop() == tag

    parser = BalancedHTML()
    parser.feed(text)
    assert parser.stack == []


def test_application_list_shows_private_snapshot_metadata_and_escapes_text():
    text = render_applications([SimpleNamespace(
        id=3,
        job_id=25,
        status="prepared",
        created_at=None,
        resume_id=5,
        message="Draft <script>",
    )])

    assert "#3" in text and "вакансия #25" in text
    assert "черновик" in text and "Резюме ID 5" in text
    assert "Draft &lt;script&gt;" in text
    assert "<script>" not in text


def test_application_export_includes_exact_saved_resume_and_cover_text():
    text = render_application_export(
        SimpleNamespace(
            id=42, status="submitted", created_at=None, source_id="hh",
            external_url="https://example.com/job", resume_id=5,
            resume_external_id="hh-resume-5", resume_snapshot="Exact CV v1",
            message="Exact cover letter v1",
        ),
        [SimpleNamespace(status="prepared", created_at=None), SimpleNamespace(status="submitted", created_at=None)],
    )

    assert "Exact CV v1" in text
    assert "Exact cover letter v1" in text
    assert "hh-resume-5" in text
    assert "does not independently verify receipt by the employer or provider" in text
    assert "Recorded status history" in text
    assert "time unknown — prepared" in text
    assert "time unknown — submitted" in text


def test_old_application_export_says_when_resume_snapshot_is_unavailable():
    text = render_application_export(
        SimpleNamespace(
            id=42, status="sent", created_at=None, source_id="hh",
            external_url=None, resume_id=5, resume_external_id=None,
            resume_snapshot="", message="Legacy cover letter",
        ),
    )

    assert "No resume-content snapshot is available" in text
    assert "Vacancy metadata snapshot unavailable" in text
