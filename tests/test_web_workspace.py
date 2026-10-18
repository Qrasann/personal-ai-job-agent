"""Security and workflow boundaries for the private web workspace."""

import io
from types import SimpleNamespace

import pytest
from aiohttp import CookieJar, FormData, web
from aiohttp.test_utils import TestClient, TestServer
from aiohttp.web_request import FileField

from app import web as gui


def test_web_requires_explicit_owner_and_token(monkeypatch):
    monkeypatch.setattr(gui.settings, "telegram_admin_chat_id", "")
    with pytest.raises(ValueError):
        gui.create_app(object(), "long-private-token-for-test")
    monkeypatch.setattr(gui.settings, "telegram_admin_chat_id", "123")
    with pytest.raises(ValueError):
        gui.create_app(object(), "")


def test_web_escapes_vacancy_text_and_rejects_unsafe_links():
    response = gui.layout("jobs", gui.e('<script>alert(1)</script>'))
    assert b"&lt;script&gt;" in response.body
    assert b"<script>" not in response.body
    assert gui.safe_link("javascript:alert(1)") == ""
    assert gui.safe_link("https://user:password@example.org/job") == ""
    assert gui.safe_link("https://example.org/job") == "https://example.org/job"


@pytest.mark.asyncio
async def test_web_login_and_csrf_gate(monkeypatch):
    monkeypatch.setattr(gui.settings, "telegram_admin_chat_id", "123")
    app = gui.create_app(object(), "long-private-token-for-test")

    async def fake_owner(_request):
        return SimpleNamespace(id=1)

    async def fake_profile(_user):
        return SimpleNamespace(id=7, target_role="SRE"), []

    async def empty(_profile_id):
        return []

    monkeypatch.setattr(gui, "owner", fake_owner)
    monkeypatch.setattr(gui, "profile_and_searches", fake_profile)
    monkeypatch.setattr(gui.repo, "list_resumes", empty)
    monkeypatch.setattr(gui.repo, "list_facts", empty)
    async with TestServer(app) as server, TestClient(server, cookie_jar=CookieJar(unsafe=True)) as client:
        anonymous = await client.get("/jobs", allow_redirects=False)
        assert anonymous.status == 303
        assert anonymous.headers["Location"] == "/login"
        signed_in = await client.post("/login", data={"token": "long-private-token-for-test"}, allow_redirects=False)
        assert signed_in.status == 303
        assert "HttpOnly" in signed_in.headers["Set-Cookie"]
        forbidden = await client.post("/action/profile", data={"csrf": "wrong", "role": "SRE"}, allow_redirects=False)
        assert forbidden.status == 403
        upload = FormData()
        upload.add_field("csrf", app["csrf"])
        upload.add_field("document", b"Skills\nLinux", filename="cv.txt", content_type="text/plain")
        preview_redirect = await client.post("/action/cv_upload", data=upload, allow_redirects=False)
        assert preview_redirect.status == 303
        assert preview_redirect.headers["Location"].startswith("/cv/preview/")


@pytest.mark.asyncio
async def test_web_rejects_mutation_of_another_users_match(monkeypatch):
    async def fake_owner(_request):
        return SimpleNamespace(id=1)

    async def fake_profile(_user):
        return SimpleNamespace(id=7), []

    async def fake_match(_id):
        return SimpleNamespace(id=42, user_id=2, status="notified")

    async def unexpected(*_args, **_kwargs):
        raise AssertionError("foreign match was changed")

    class Request:
        app = {"csrf": "csrf"}
        match_info = {"name": "match"}

        async def post(self):
            return {"csrf": "csrf", "id": "42", "status": "saved"}

    monkeypatch.setattr(gui, "owner", fake_owner)
    monkeypatch.setattr(gui, "profile_and_searches", fake_profile)
    monkeypatch.setattr(gui.repo, "get_match", fake_match)
    monkeypatch.setattr(gui.repo, "set_match_status", unexpected)
    with pytest.raises(web.HTTPNotFound):
        await gui.action(Request())


@pytest.mark.asyncio
async def test_web_scan_uses_real_scan_service_and_writes_dashboard(monkeypatch):
    calls = []

    async def fake_scan(bot, user_id, *, force_refresh):
        calls.append((bot, user_id, force_refresh))
        return {"processed": 2, "qualified": 1, "stretch": 1}

    async def fake_dashboard(user_id, **values):
        calls.append((user_id, values))

    monkeypatch.setattr(gui, "scan_for_user", fake_scan)
    monkeypatch.setattr(gui, "_save_scan_dashboard", fake_dashboard)
    app = {"bot": object(), "scan_state": {}}
    await gui.run_scan(app, 5)
    assert calls[1] == (app["bot"], 5, True)
    assert calls[-1][1]["summary"]["qualified"] == 1
    assert "готово" in app["scan_state"][5]


@pytest.mark.asyncio
async def test_job_detail_uses_owner_scoped_source_view(monkeypatch):
    calls = []

    async def fake_owner(_request):
        return SimpleNamespace(id=8)

    async def fake_details(user_id, job_id, *, search_profile_id):
        calls.append((user_id, job_id, search_profile_id))
        return {"match": SimpleNamespace(id=9, status="notified")}

    monkeypatch.setattr(gui, "owner", fake_owner)
    monkeypatch.setattr(gui, "get_vacancy_details", fake_details)
    monkeypatch.setattr(gui, "render_job_details", lambda _payload: "Source posting &amp; evidence")
    request = SimpleNamespace(
        match_info={"id": "17"}, query={"search": "4"}, app={"csrf": "csrf"}
    )
    response = await gui.job_detail(request)
    assert calls == [(8, 17, 4)]
    assert b"Source posting &amp; evidence" in response.body


@pytest.mark.asyncio
async def test_relocation_below_threshold_keeps_manual_leads_without_domestic_onsite(monkeypatch):
    calls = []
    search = SimpleNamespace(id=4, kind="relocation", settings={"notify_min_score": 65})

    async def fake_profile(_user):
        return SimpleNamespace(id=2), [search]

    async def fake_latest(user_id, limit, **kwargs):
        calls.append((user_id, limit, kwargs))
        match = SimpleNamespace(id=9, status="filtered", total_score=50, reason="geography unknown", search_profile_id=4)
        return [
            (match, SimpleNamespace(id=17, title="Warehouse worker", company="A", city="", country="GE")),
            (match, SimpleNamespace(id=18, title="Domestic onsite", company="B", city="", country="RU")),
        ]

    monkeypatch.setattr(gui, "profile_and_searches", fake_profile)
    monkeypatch.setattr(gui.repo, "latest_matches", fake_latest)
    monkeypatch.setattr(gui, "relocation_first_allows", lambda job, _settings, *, current_country: job.country == "GE")
    request = SimpleNamespace(query={"scope": "relocation", "below": "1"})
    body = await gui.page_content(request, SimpleNamespace(id=8, current_country="RU"), "jobs")
    assert calls == [(8, 80, {"search_profile_id": 4, "include_filtered": True, "min_score": 1, "max_score": 64})]
    assert "Warehouse worker" in body
    assert "Domestic onsite" not in body
    assert "geography unknown" in body


@pytest.mark.asyncio
async def test_candidate_fact_requires_owner_evidence(monkeypatch):
    recorded = []

    async def fake_owner(_request):
        return SimpleNamespace(id=8)

    async def fake_profile(_user):
        return SimpleNamespace(id=12), []

    async def fake_add(profile_id, value, **kwargs):
        recorded.append((profile_id, value, kwargs))

    class Request:
        app = {"csrf": "csrf"}
        match_info = {"name": "fact"}
        data = {"csrf": "csrf", "value": "Warehouse work", "experience_type": "commercial", "evidence": ""}

        async def post(self):
            return self.data

    monkeypatch.setattr(gui, "owner", fake_owner)
    monkeypatch.setattr(gui, "profile_and_searches", fake_profile)
    monkeypatch.setattr(gui.repo, "add_fact", fake_add)
    request = Request()
    with pytest.raises(web.HTTPBadRequest):
        await gui.action(request)
    assert recorded == []
    request.data["evidence"] = "Owner-confirmed work record"
    with pytest.raises(web.HTTPSeeOther):
        await gui.action(request)
    assert recorded == [(12, "Warehouse work", {"category": "experience", "experience_type": "commercial", "evidence": "Owner-confirmed work record", "provenance": "web_manual"})]


@pytest.mark.asyncio
async def test_application_detail_denies_another_users_package(monkeypatch):
    async def fake_owner(_request):
        return SimpleNamespace(id=8)

    async def fake_application(user_id, app_id):
        assert (user_id, app_id) == (8, 42)
        return None

    monkeypatch.setattr(gui, "owner", fake_owner)
    monkeypatch.setattr(gui.repo, "get_application", fake_application)
    request = SimpleNamespace(match_info={"id": "42"})
    with pytest.raises(web.HTTPNotFound):
        await gui.application_detail(request)


@pytest.mark.asyncio
async def test_candidate_fact_form_defaults_to_unknown_experience(monkeypatch):
    async def fake_profile(_user):
        return SimpleNamespace(id=2, name="Main", target_role="SRE", english_level=""), []

    async def no_facts(_profile_id):
        return []

    monkeypatch.setattr(gui, "profile_and_searches", fake_profile)
    monkeypatch.setattr(gui.repo, "list_facts", no_facts)
    body = await gui.page_content(SimpleNamespace(query={}), SimpleNamespace(id=1), "profiles")
    assert body.index('value="unknown"') < body.index('value="commercial"')


@pytest.mark.asyncio
async def test_cv_upload_requires_review_then_saves_without_unapproved_facts(monkeypatch):
    saved = []

    async def fake_owner(_request):
        return SimpleNamespace(id=8)

    async def fake_profile(_user):
        return SimpleNamespace(id=12, target_role="SRE"), []

    async def empty(_profile_id):
        return []

    async def fake_save(*args, **kwargs):
        saved.append((args, kwargs))

    monkeypatch.setattr(gui, "owner", fake_owner)
    monkeypatch.setattr(gui, "profile_and_searches", fake_profile)
    monkeypatch.setattr(gui.repo, "list_resumes", empty)
    monkeypatch.setattr(gui.repo, "list_facts", empty)
    monkeypatch.setattr(gui.repo, "add_imported_resume_with_facts", fake_save)
    app = {"csrf": "csrf", "cv_pending": {}}

    class Request:
        match_info = {"name": "cv_upload"}

        def __init__(self, data):
            self.app = app
            self.data = data

        async def post(self):
            return self.data

    file = FileField("document", "cv.txt", io.BytesIO(b"Skills\nLinux, Docker"), "text/plain", {})
    with pytest.raises(web.HTTPSeeOther) as redirect:
        await gui.action(Request({"csrf": "csrf", "document": file}))
    assert saved == []
    token = next(iter(app["cv_pending"]))
    assert f"/cv/preview/{token}" in redirect.value.location
    preview = await gui.cv_preview(SimpleNamespace(app=app, match_info={"token": token}))
    assert b"Linux, Docker" in preview.body
    request = Request({"csrf": "csrf", "token": token, "mode": "resume"})
    request.match_info = {"name": "cv_confirm"}
    with pytest.raises(web.HTTPSeeOther):
        await gui.action(request)
    assert saved[0][1]["replacements"] == []
    assert saved[0][0][6] == []
    assert token not in app["cv_pending"]


@pytest.mark.asyncio
async def test_cv_preview_is_owner_scoped(monkeypatch):
    async def fake_owner(_request):
        return SimpleNamespace(id=2)

    monkeypatch.setattr(gui, "owner", fake_owner)
    app = {"cv_pending": {"token": {"user_id": 1, "created_at": gui.time.monotonic()}}}
    with pytest.raises(web.HTTPNotFound):
        await gui.cv_preview(SimpleNamespace(app=app, match_info={"token": "token"}))


@pytest.mark.asyncio
async def test_cv_fact_confirmation_keeps_unknown_experience_and_is_single_use(monkeypatch):
    saved = []

    async def fake_owner(_request):
        return SimpleNamespace(id=8)

    async def fake_profile(_user):
        return SimpleNamespace(id=12), []

    async def fake_save(*args, **kwargs):
        saved.append((args, kwargs))

    monkeypatch.setattr(gui, "owner", fake_owner)
    monkeypatch.setattr(gui, "profile_and_searches", fake_profile)
    monkeypatch.setattr(gui.repo, "add_imported_resume_with_facts", fake_save)
    proposal = gui.propose_facts("Skills\nLinux")[0]
    pending = {"user_id": 8, "profile_id": 12, "created_at": gui.time.monotonic(), "proposals": (proposal,), "overlaps": (), "language": "en", "role": "SRE", "content": "Skills\nLinux", "fingerprint": "hash"}
    app = {"csrf": "csrf", "cv_pending": {"token": pending}}

    class Request:
        match_info = {"name": "cv_confirm"}

        async def post(self):
            return {"csrf": "csrf", "token": "token", "mode": "facts", "choice_0": "add"}

        def __init__(self):
            self.app = app

    request = Request()
    with pytest.raises(web.HTTPSeeOther):
        await gui.action(request)
    assert saved[0][0][6][0]["value"] == "Linux"
    assert "experience_type" not in saved[0][0][6][0]
    with pytest.raises(web.HTTPNotFound):
        await gui.action(request)
