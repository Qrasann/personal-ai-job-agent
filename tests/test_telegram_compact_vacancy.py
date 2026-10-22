import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.matching.fact_comparison import compare_facts
from app.telegram import handlers
from app.telegram.vacancy_view import render_job_section, render_job_summary


def _payload(*, applicant_count=None, country="DE", city="Berlin"):
    details = {
        "description": "Requirements: Linux and Docker. English B2 required.",
        "experience": "1–3 years",
        "applicant_location": "Germany",
        "published_at": "2026-10-18T08:00:00+00:00",
    }
    if applicant_count is not None:
        details.update({
            "applicant_count": applicant_count,
            "applicant_count_source": "https://careers.example/jobs/42",
            "applicant_count_observed_at": "2026-10-18T09:00:00+00:00",
        })
    return {
        "job": SimpleNamespace(
            id=42, title="Junior DevOps Engineer", company="Example",
            description="Linux Docker", city=city, country=country,
            work_mode="hybrid", remote_scope="Germany", published_at=None,
            salary_from=55000, salary_to=65000, salary_currency="EUR",
            salary_period="annual", relocation=None, visa_sponsorship=None,
        ),
        "match": SimpleNamespace(
            search_profile_id=4, total_score=81, technical_score=84,
            geography_score=90, salary_score=75, relocation_score=55,
            reason="совпадают Linux и Docker; junior scope",
            recommendation_scores={"competition": {"score": None, "evidence": "no public data"}},
        ),
        "details": details,
        "source": "greenhouse",
        "source_job_id": "42",
        "source_observed_at": "2026-10-18T09:00:00+00:00",
        "url": "https://careers.example/jobs/42",
    }


def test_job_summary_is_compact_and_moves_long_sections_behind_buttons():
    text = render_job_summary(_payload())

    assert "Junior DevOps Engineer" in text
    assert "81/100" in text
    assert "Отклики: <b>Нет открытых данных</b>" in text
    assert "Описание" not in text
    assert "Technical:" not in text
    assert len(text) < 900


def test_country_only_office_location_uses_country_name_instead_of_iso_code():
    text = render_job_summary(_payload(country="MT", city=None))

    assert "📍 Malta" in text
    assert "📍 MT" not in text


def test_competition_section_only_labels_confirmed_application_count():
    unknown = render_job_section(_payload(), "competition")
    confirmed = render_job_section(_payload(applicant_count=17), "competition")

    assert "Нет открытых данных" in unknown
    assert "Просмотры" in unknown
    assert "Подтверждённых откликов: <b>17</b>" in confirmed
    assert "18.10.2026 09:00 UTC" in confirmed


def test_terms_section_links_allowlisted_official_mobility_references():
    cases = {
        "AM": ("workpermit.am/en/home", 1),
        "DE": ("make-it-in-germany.com/en/looking-for-foreign-professionals", 1),
        "GE": ("sda.gov.ge/en/products/migration-residence-permits", 2),
        "MT": (
            "identita.gov.mt/expatriates-unit-main-page/noneu-nationals/"
            "employment-related-permits/single-permit",
            1,
        ),
    }
    for country, (url_fragment, link_count) in cases.items():
        terms = render_job_section(_payload(country=country), "terms")
        assert url_fragment in terms
        assert terms.count("<a href=") == link_count
        assert "не определяет право кандидата на работу" in terms
        assert "проверено 19.10.2026" in terms

    unsupported = render_job_section(_payload(country="RU"), "terms")
    assert "<a href=" not in unsupported


def test_requirements_section_shows_bounded_matched_and_missing_skill_summary():
    payload = _payload()
    payload["comparison"] = compare_facts(
        "Requirements: Linux, Docker and Kubernetes.",
        [SimpleNamespace(
            id=1,
            value="Commercial Linux operations",
            experience_type="commercial",
            active=True,
            deleted_at=None,
        )],
    )

    text = render_job_section(payload, "req")

    assert "Найдено в Candidate Facts: <b>1/3</b>" in text
    assert "✅ Есть в Candidate Facts: Linux" in text
    assert "❌ Не найдено в Candidate Facts: Docker, Kubernetes" in text
    assert "опыт не добавляется автоматически" in text


def test_requirements_tab_loads_profile_comparison(monkeypatch):
    payload = _payload()
    comparison = AsyncMock(return_value=payload)
    monkeypatch.setattr(
        handlers.repo,
        "get_user_by_chat",
        AsyncMock(return_value=SimpleNamespace(id=7)),
    )
    monkeypatch.setattr(handlers, "get_vacancy_comparison", comparison)
    monkeypatch.setattr(handlers, "render_job_section", lambda value, section: "REQ SUMMARY")
    message = SimpleNamespace(chat=SimpleNamespace(id=10), edit_text=AsyncMock())
    callback = SimpleNamespace(data="jobtab:req:42:4", message=message, answer=AsyncMock())

    asyncio.run(handlers.jobtab_callback(callback))

    comparison.assert_awaited_once_with(7, 42, search_profile_id=4)
    assert message.edit_text.await_args.args[0] == "REQ SUMMARY"


def test_jobtab_callback_edits_message_and_preserves_profile_scope(monkeypatch):
    payload = _payload()
    details = AsyncMock(return_value=payload)
    monkeypatch.setattr(handlers.repo, "get_user_by_chat", AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers, "get_vacancy_details", details)
    message = SimpleNamespace(chat=SimpleNamespace(id=10), edit_text=AsyncMock())
    callback = SimpleNamespace(data="jobtab:terms:42:4", message=message, answer=AsyncMock())

    asyncio.run(handlers.jobtab_callback(callback))

    details.assert_awaited_once_with(7, 42, search_profile_id=4)
    assert "Условия найма" in message.edit_text.await_args.args[0]
    keyboard = message.edit_text.await_args.kwargs["reply_markup"]
    assert keyboard.inline_keyboard[0][0].callback_data == "jobtab:summary:42:4"


def test_jobtab_callback_rejects_malformed_payload_before_lookup(monkeypatch):
    details = AsyncMock()
    monkeypatch.setattr(handlers.repo, "get_user_by_chat", AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers, "get_vacancy_details", details)
    callback = SimpleNamespace(
        data="jobtab:source:42:4:unexpected",
        message=SimpleNamespace(chat=SimpleNamespace(id=10)),
        answer=AsyncMock(),
    )

    asyncio.run(handlers.jobtab_callback(callback))

    details.assert_not_awaited()
    assert callback.answer.await_args.kwargs["show_alert"] is True


def test_scanstatus_details_callback_edits_same_message(monkeypatch):
    state = {"status": "completed", "summary": {"sources": {"hh": {"found": 2}}}}
    monkeypatch.setattr(handlers.repo, "get_user_by_chat", AsyncMock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(handlers, "_scan_dashboard_for_user", AsyncMock(return_value=state))
    message = SimpleNamespace(chat=SimpleNamespace(id=10), edit_text=AsyncMock())
    callback = SimpleNamespace(data="scanstatus:details", message=message, answer=AsyncMock())

    asyncio.run(handlers.scan_status_callback(callback))

    assert "hh: готово · 2 вакансий" in message.edit_text.await_args.args[0]
    keyboard = message.edit_text.await_args.kwargs["reply_markup"]
    assert keyboard.inline_keyboard[0][0].callback_data == "scanstatus:summary"
