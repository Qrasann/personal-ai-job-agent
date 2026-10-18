"""Security and workflow boundaries for the private web workspace."""

from types import SimpleNamespace

import pytest
from aiohttp import CookieJar, web
from aiohttp.test_utils import TestClient, TestServer

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
        return SimpleNamespace(id=7), []

    monkeypatch.setattr(gui, "owner", fake_owner)
    monkeypatch.setattr(gui, "profile_and_searches", fake_profile)
    async with TestServer(app) as server, TestClient(server, cookie_jar=CookieJar(unsafe=True)) as client:
        anonymous = await client.get("/jobs", allow_redirects=False)
        assert anonymous.status == 303
        assert anonymous.headers["Location"] == "/login"
        signed_in = await client.post("/login", data={"token": "long-private-token-for-test"}, allow_redirects=False)
        assert signed_in.status == 303
        assert "HttpOnly" in signed_in.headers["Set-Cookie"]
        forbidden = await client.post("/action/profile", data={"csrf": "wrong", "role": "SRE"}, allow_redirects=False)
        assert forbidden.status == 403


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
