import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.telegram import handlers
from app.telegram.ui import jobs_keyboard


def _job(job_id: int, title: str):
    return SimpleNamespace(
        id=job_id,
        title=title,
        company="ACME",
        salary_from=None,
        salary_to=None,
        salary_currency=None,
        description="Linux Docker",
        city="Тверь",
        country="RU",
        work_mode="Удалённо",
    )


def test_jobs_keyboard_links_visible_jobs_to_details():
    rows = [
        (SimpleNamespace(total_score=82), _job(25, "DevOps")),
        (SimpleNamespace(total_score=78), _job(26, "Linux")),
        (SimpleNamespace(total_score=74), _job(27, "Platform")),
    ]
    keyboard = jobs_keyboard(rows)
    callbacks = [
        button.callback_data
        for row in keyboard.inline_keyboard
        for button in row
    ]
    assert callbacks == ["details:25", "details:26", "details:27"]

def test_jobs_command_adds_details_keyboard(monkeypatch):
    rows = [
        (SimpleNamespace(total_score=82), _job(25, "DevOps Engineer")),
        (SimpleNamespace(total_score=78), _job(26, "Linux Engineer")),
    ]
    message = SimpleNamespace(text="/jobs", answer=AsyncMock())

    monkeypatch.setattr(
        handlers,
        "_require_user",
        AsyncMock(return_value=SimpleNamespace(id=7)),
    )
    monkeypatch.setattr(
        handlers,
        "_first_search",
        AsyncMock(return_value=(
            SimpleNamespace(id=3),
            SimpleNamespace(settings={"notify_min_score": 65}),
        )),
    )
    latest = AsyncMock(return_value=rows)
    monkeypatch.setattr(handlers.repo, "latest_matches", latest)
    source_ref = AsyncMock(side_effect=lambda job_id, source_id: (
        SimpleNamespace(url="https://himalayas.app/jobs/25")
        if job_id == 25 and source_id == "himalayas"
        else None
    ))
    monkeypatch.setattr(handlers.repo, "source_ref", source_ref)

    asyncio.run(handlers.jobs(message))

    latest.assert_awaited_once_with(7, 10, min_score=65)
    assert "Совпадения по рейтингу" in message.answer.await_args.args[0]
    assert '<a href="https://himalayas.app/jobs/25">Himalayas</a>' in message.answer.await_args.args[0]
    keyboard = message.answer.await_args.kwargs["reply_markup"]
    callbacks = [
        button.callback_data
        for row in keyboard.inline_keyboard
        for button in row
    ]
    assert callbacks == ["details:25", "details:26"]


def test_jobs_below_command_shows_filtered_matches_without_changing_threshold(monkeypatch):
    rows = [(SimpleNamespace(total_score=64), _job(30, "Warehouse Worker"))]
    message = SimpleNamespace(text="/jobs below", answer=AsyncMock())

    monkeypatch.setattr(
        handlers,
        "_require_user",
        AsyncMock(return_value=SimpleNamespace(id=7)),
    )
    monkeypatch.setattr(
        handlers,
        "_first_search",
        AsyncMock(return_value=(
            SimpleNamespace(id=3),
            SimpleNamespace(settings={"notify_min_score": 65}),
        )),
    )
    latest = AsyncMock(return_value=rows)
    monkeypatch.setattr(handlers.repo, "latest_matches", latest)
    monkeypatch.setattr(handlers.repo, "source_ref", AsyncMock(return_value=None))

    asyncio.run(handlers.jobs(message))

    latest.assert_awaited_once_with(
        7,
        10,
        include_filtered=True,
        min_score=1,
        max_score=64,
    )
    rendered = message.answer.await_args.args[0]
    assert "Ниже порога 65" in rendered
    assert "не подтверждены автоматически" in rendered
    assert "#30 · 64/100" in rendered


def _mock_profiles(monkeypatch):
    searches = [
        SimpleNamespace(id=3, kind="career", name="Career-first", settings={"notify_min_score": 65}),
        SimpleNamespace(id=4, kind="relocation", name="Relocation-first", settings={"notify_min_score": 70, "search_strategy": "relocation_first", "target_countries": ["GE", "AM"]}),
    ]
    monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=SimpleNamespace(id=7, current_country="RU")))
    monkeypatch.setattr(handlers.repo, "active_profile", AsyncMock(return_value=SimpleNamespace(id=2)))
    monkeypatch.setattr(handlers.repo, "list_search_profiles", AsyncMock(return_value=searches))
    monkeypatch.setattr(handlers.repo, "source_ref", AsyncMock(return_value=None))
    return searches


@pytest.mark.parametrize("text", ["/jobs relocation below", "/jobs below relocation"])
def test_jobs_relocation_uses_its_own_threshold_and_scope(monkeypatch, text):
    searches = _mock_profiles(monkeypatch)
    rows = [(SimpleNamespace(total_score=54, search_profile_id=4), _job(30, "Warehouse Worker"))]
    latest = AsyncMock(return_value=rows)
    monkeypatch.setattr(handlers.repo, "latest_matches", latest)
    message = SimpleNamespace(text=text, answer=AsyncMock())

    asyncio.run(handlers.jobs(message))

    latest.assert_awaited_once_with(7, 80, include_filtered=True, min_score=1, max_score=69, search_profile_id=4)
    rendered = message.answer.await_args.args[0]
    assert "Relocation-first" in rendered
    assert "Ниже порога 70" in rendered
    assert "/job 30 relocation" in rendered
    assert message.answer.await_args.kwargs["reply_markup"].inline_keyboard[0][0].callback_data == "details:30:4"
    assert searches[0].settings == {"notify_min_score": 65}
    assert searches[1].settings["notify_min_score"] == 70


def test_jobs_career_scope_uses_score_ordered_query(monkeypatch):
    _mock_profiles(monkeypatch)
    latest = AsyncMock(return_value=[(SimpleNamespace(total_score=82), _job(25, "DevOps Engineer"))])
    monkeypatch.setattr(handlers.repo, "latest_matches", latest)
    message = SimpleNamespace(text="/jobs career", answer=AsyncMock())

    asyncio.run(handlers.jobs(message))

    latest.assert_awaited_once_with(7, 10, min_score=65, search_profile_id=3)
    assert "Career-first" in message.answer.await_args.args[0]


def test_jobs_relocation_empty_results_link_to_scoped_manual_review(monkeypatch):
    _mock_profiles(monkeypatch)
    monkeypatch.setattr(handlers.repo, "latest_matches", AsyncMock(return_value=[]))
    message = SimpleNamespace(text="/jobs relocation", answer=AsyncMock())

    asyncio.run(handlers.jobs(message))

    rendered = message.answer.await_args.args[0]
    assert "Relocation-first" in rendered
    assert "70/100" in rendered
    assert "/jobs relocation below" in rendered


def test_jobs_relocation_hides_stored_domestic_onsite_but_keeps_remote(monkeypatch):
    _mock_profiles(monkeypatch)
    onsite = SimpleNamespace(
        id=31, title="Chef", company="Local", salary_from=None, salary_to=None,
        salary_currency=None, description="", city="Tyumen", country="RU",
        work_mode="Офис", remote_scope=None,
    )
    remote = _job(32, "Remote Linux Support")
    rows = [
        (SimpleNamespace(total_score=90), onsite),
        (SimpleNamespace(total_score=80), remote),
    ]
    latest = AsyncMock(return_value=rows)
    monkeypatch.setattr(handlers.repo, "latest_matches", latest)
    message = SimpleNamespace(text="/jobs relocation", answer=AsyncMock())

    asyncio.run(handlers.jobs(message))

    rendered = message.answer.await_args.args[0]
    assert "Remote Linux Support" in rendered
    assert "Chef" not in rendered
    assert "/job 32 relocation" in rendered


def test_jobs_missing_relocation_profile_does_not_fall_back_to_career(monkeypatch):
    searches = _mock_profiles(monkeypatch)
    monkeypatch.setattr(handlers.repo, "list_search_profiles", AsyncMock(return_value=searches[:1]))
    latest = AsyncMock()
    monkeypatch.setattr(handlers.repo, "latest_matches", latest)
    message = SimpleNamespace(text="/jobs relocation below", answer=AsyncMock())

    asyncio.run(handlers.jobs(message))

    latest.assert_not_awaited()
    assert "/parallelsearch on" in message.answer.await_args.args[0]


def test_jobs_career_keeps_legacy_single_profile_available(monkeypatch):
    _mock_profiles(monkeypatch)
    legacy = SimpleNamespace(id=3, kind="employment", settings={"notify_min_score": 65})
    monkeypatch.setattr(handlers.repo, "list_search_profiles", AsyncMock(return_value=[legacy]))
    latest = AsyncMock(return_value=[])
    monkeypatch.setattr(handlers.repo, "latest_matches", latest)

    asyncio.run(handlers.jobs(SimpleNamespace(text="/jobs career", answer=AsyncMock())))

    latest.assert_awaited_once_with(7, 10, min_score=65, search_profile_id=3)


@pytest.mark.parametrize("arguments", ["career relocation", "below below", "1273", "relocation extra"])
def test_jobs_rejects_ambiguous_or_unknown_arguments(monkeypatch, arguments):
    _mock_profiles(monkeypatch)
    latest = AsyncMock()
    monkeypatch.setattr(handlers.repo, "latest_matches", latest)
    message = SimpleNamespace(text=f"/jobs {arguments}", answer=AsyncMock())

    asyncio.run(handlers.jobs(message))

    latest.assert_not_awaited()
    assert "Использование" in message.answer.await_args.args[0]


def test_jobs_keyboard_preserves_each_listed_match_profile():
    rows = [(SimpleNamespace(total_score=82, search_profile_id=3), _job(25, "Linux Support"))]
    assert jobs_keyboard(rows).inline_keyboard[0][0].callback_data == "details:25:3"


def test_details_callback_forwards_the_profile_that_produced_the_score(monkeypatch):
    _mock_profiles(monkeypatch)
    monkeypatch.setattr(handlers.repo, "get_user_by_chat", AsyncMock(return_value=SimpleNamespace(id=7)))
    details = AsyncMock(return_value={"job": SimpleNamespace(id=25)})
    monkeypatch.setattr(handlers, "get_vacancy_details", details)
    monkeypatch.setattr(handlers, "render_job_details", lambda payload: "Scoped card")
    callback = SimpleNamespace(
        data="details:25:4", answer=AsyncMock(),
        message=SimpleNamespace(chat=SimpleNamespace(id=10), answer=AsyncMock()),
    )

    asyncio.run(handlers.details_callback(callback))

    details.assert_awaited_once_with(7, 25, search_profile_id=4)
    assert callback.message.answer.await_args.args[0] == "Scoped card"
    keyboard = callback.message.answer.await_args.kwargs["reply_markup"]
    assert keyboard.inline_keyboard[0][0].callback_data == "compare:25:4"


def test_job_command_forwards_explicit_relocation_profile(monkeypatch):
    _mock_profiles(monkeypatch)
    details = AsyncMock(return_value={"job": SimpleNamespace(id=25)})
    monkeypatch.setattr(handlers, "get_vacancy_details", details)
    monkeypatch.setattr(handlers, "render_job_details", lambda payload: "Scoped card")
    progress = SimpleNamespace(edit_text=AsyncMock())
    message = SimpleNamespace(text="/job 25 relocation", answer=AsyncMock(return_value=progress))

    asyncio.run(handlers.job_details(message))

    details.assert_awaited_once_with(7, 25, search_profile_id=4)
    assert progress.edit_text.await_args.args[0] == "Scoped card"


def test_compare_callback_preserves_the_card_profile(monkeypatch):
    _mock_profiles(monkeypatch)
    monkeypatch.setattr(handlers.repo, "get_user_by_chat", AsyncMock(return_value=SimpleNamespace(id=7)))
    comparison = AsyncMock(return_value={})
    monkeypatch.setattr(handlers, "get_vacancy_comparison", comparison)
    monkeypatch.setattr(handlers, "render_fact_comparison", lambda payload: "Scoped comparison")
    callback = SimpleNamespace(
        data="compare:25:4", answer=AsyncMock(),
        message=SimpleNamespace(chat=SimpleNamespace(id=10), answer=AsyncMock()),
    )

    asyncio.run(handlers.compare_callback(callback))

    comparison.assert_awaited_once_with(7, 25, search_profile_id=4)
    assert callback.message.answer.await_args.args[0] == "Scoped comparison"


def test_compare_command_preserves_explicit_relocation_profile(monkeypatch):
    _mock_profiles(monkeypatch)
    comparison = AsyncMock(return_value={})
    monkeypatch.setattr(handlers, "get_vacancy_comparison", comparison)
    monkeypatch.setattr(handlers, "render_fact_comparison", lambda payload: "Scoped comparison")
    progress = SimpleNamespace(edit_text=AsyncMock())
    message = SimpleNamespace(text="/compare 25 relocation", answer=AsyncMock(return_value=progress))

    asyncio.run(handlers.compare_job(message))

    comparison.assert_awaited_once_with(7, 25, search_profile_id=4)
    assert progress.edit_text.await_args.args[0] == "Scoped comparison"


def test_interview_command_preserves_scoped_profile_and_renders_practice_plan(monkeypatch):
    _mock_profiles(monkeypatch)
    comparison = AsyncMock(return_value={"comparison": "comparison", "job": _job(25, "DevOps")})
    monkeypatch.setattr(handlers, "get_vacancy_comparison", comparison)
    monkeypatch.setattr(handlers, "build_interview_plan", lambda value: ("exercise",))
    monkeypatch.setattr(handlers, "render_interview_plan", lambda job, plan: "PRACTICE PLAN")
    progress = SimpleNamespace(edit_text=AsyncMock())
    message = SimpleNamespace(text="/interview 25 relocation", answer=AsyncMock(return_value=progress))

    asyncio.run(handlers.interview_command(message))

    comparison.assert_awaited_once_with(7, 25, search_profile_id=4)
    assert progress.edit_text.await_args.args[0] == "PRACTICE PLAN"


def test_compare_command_reports_sanitized_error_instead_of_undefined_issue(monkeypatch):
    _mock_profiles(monkeypatch)
    comparison = AsyncMock(side_effect=ValueError("sensitive internal detail"))
    monkeypatch.setattr(handlers, "get_vacancy_comparison", comparison)
    progress = SimpleNamespace(edit_text=AsyncMock())
    message = SimpleNamespace(text="/compare 25", answer=AsyncMock(return_value=progress))

    asyncio.run(handlers.compare_job(message))

    rendered = progress.edit_text.await_args.args[0]
    assert "SOURCE_PROCESSING_FAILED" in rendered
    assert "sensitive internal detail" not in rendered


def test_resume_diff_command_accepts_explicit_resume_and_renders_result(monkeypatch):
    _mock_profiles(monkeypatch)
    builder = AsyncMock(return_value={})
    monkeypatch.setattr(handlers, "get_resume_diff", builder)
    monkeypatch.setattr(handlers, "render_resume_diff", lambda payload: "CV DIFF")
    progress = SimpleNamespace(edit_text=AsyncMock())
    message = SimpleNamespace(text="/resumediff 25 9", answer=AsyncMock(return_value=progress))

    asyncio.run(handlers.resume_diff_command(message))

    builder.assert_awaited_once_with(7, 25, resume_id=9)
    assert progress.edit_text.await_args.args[0] == "CV DIFF"


def test_prepare_callback_sends_reviewable_preview_without_sending_application(monkeypatch):
    monkeypatch.setattr(handlers.repo, "get_user_by_chat", AsyncMock(return_value=SimpleNamespace(id=7)))
    prepare = AsyncMock(return_value={"job": _job(25, "DevOps"), "resume_diff": {}})
    monkeypatch.setattr(handlers, "prepare_match", prepare)
    save_application = AsyncMock(return_value=SimpleNamespace(id=3))
    monkeypatch.setattr(handlers.repo, "save_application", save_application)
    update_match = AsyncMock()
    monkeypatch.setattr(handlers.repo, "set_match_status", update_match)
    monkeypatch.setattr(handlers, "render_application_package", lambda payload: "REVIEW PREVIEW")
    answer = AsyncMock()
    callback = SimpleNamespace(
        data="prepare:51",
        answer=AsyncMock(),
        message=SimpleNamespace(chat=SimpleNamespace(id=10), answer=answer),
    )

    asyncio.run(handlers.prepare_callback(callback))

    prepare.assert_awaited_once_with(51, 7)
    save_application.assert_awaited_once_with(
        user_id=7, job_id=25, source_id="manual", source_application_id=None,
        external_url=None, resume_id=None, resume_snapshot="", resume_external_id=None,
        vacancy_snapshot={"title": "DevOps", "company": "ACME", "description": "Linux Docker", "source_url": ""},
        message="", status="prepared",
    )
    update_match.assert_awaited_once_with(51, "prepared")
    answer.assert_awaited_once()
    assert answer.await_args.args[0] == "REVIEW PREVIEW\n\n💾 Черновик письма сохранён как отклик #3. /applications"
    assert answer.await_args.kwargs["disable_web_page_preview"] is True


def test_application_status_command_uses_explicit_manual_status(monkeypatch):
    _mock_profiles(monkeypatch)
    update = AsyncMock(return_value=True)
    monkeypatch.setattr(handlers.repo, "set_application_status", update)
    message = SimpleNamespace(text="/application 42 submitted", answer=AsyncMock())

    asyncio.run(handlers.application_status_command(message))

    update.assert_awaited_once_with(7, 42, "submitted")
    assert "вручную" in message.answer.await_args.args[0]


def test_application_status_command_displays_owner_scoped_history(monkeypatch):
    _mock_profiles(monkeypatch)
    history = AsyncMock(return_value=[SimpleNamespace(status="prepared")])
    monkeypatch.setattr(handlers.repo, "application_status_history", history)
    monkeypatch.setattr(handlers, "render_application_history", lambda events: "HISTORY")
    message = SimpleNamespace(text="/application 42 history", answer=AsyncMock())

    asyncio.run(handlers.application_status_command(message))

    history.assert_awaited_once_with(7, 42)
    assert message.answer.await_args.args[0] == "HISTORY"


def test_application_export_command_sends_only_owner_scoped_text_snapshot(monkeypatch):
    _mock_profiles(monkeypatch)
    application = SimpleNamespace(
        id=42, job_id=25, status="prepared", created_at=None, source_id="manual",
        external_url=None, resume_id=5, resume_external_id=None,
        resume_snapshot="Saved CV", message="Cover draft",
    )
    lookup = AsyncMock(return_value=application)
    monkeypatch.setattr(handlers.repo, "get_application", lookup)
    live_job_lookup = AsyncMock(side_effect=AssertionError("Export must use the saved snapshot"))
    monkeypatch.setattr(handlers.repo, "get_job", live_job_lookup)
    history = AsyncMock(return_value=[SimpleNamespace(status="prepared", created_at=None)])
    monkeypatch.setattr(handlers.repo, "application_status_history", history)
    message = SimpleNamespace(
        text="/application 42 export",
        answer=AsyncMock(),
        answer_document=AsyncMock(),
    )

    asyncio.run(handlers.application_status_command(message))

    lookup.assert_awaited_once_with(7, 42)
    live_job_lookup.assert_not_awaited()
    history.assert_awaited_once_with(7, 42)
    document = message.answer_document.await_args.args[0]
    assert document.filename == "application-42.txt"
    assert "Пакет #42" in message.answer_document.await_args.kwargs["caption"]
