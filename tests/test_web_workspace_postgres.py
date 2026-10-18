"""A real HTTP/PostgreSQL walk through the private web workspace."""

import asyncio
import os

import pytest
from aiohttp import CookieJar
from aiohttp.test_utils import TestClient, TestServer
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app import web as gui
from app.database import repository as repo
from app.database.models import Base
from app.domain.jobs import NormalizedJob


@pytest.mark.integration
def test_owner_web_route_actions_and_application_scope_use_postgres(monkeypatch):
    url = os.getenv("JOB_AGENT_TEST_DATABASE_URL")
    if not url:
        if os.getenv("CI"):
            pytest.fail("CI requires JOB_AGENT_TEST_DATABASE_URL")
        pytest.skip("isolated PostgreSQL is not configured")
    asyncio.run(_web_flow(url, monkeypatch))


async def _web_flow(url, monkeypatch):
    engine = create_async_engine(url, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    monkeypatch.setattr(repo, "SessionLocal", session_factory)
    monkeypatch.setattr(gui.settings, "telegram_admin_chat_id", "web-test-owner")
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
            await connection.run_sync(Base.metadata.create_all)

        owner = await repo.create_user("web-test-owner", "Owner")
        stranger = await repo.create_user("web-test-stranger", "Stranger")
        profile = await repo.ensure_default_profile(owner.id)
        search = (await repo.list_search_profiles(profile.id))[0]
        await repo.add_resume(profile.id, "Owner CV", "en", "SRE", "Linux operations", source="manual")
        job, _ = await repo.upsert_job(NormalizedJob(
            source="fixture", source_job_id="job-1", title="Platform Engineer",
            company="Example", country="GE", city="Tbilisi",
            description="Linux operations", url="https://example.invalid/job-1",
        ))
        match = await repo.save_match(
            job_id=job.id, user_id=owner.id, profile_id=profile.id,
            search_profile_id=search.id, total_score=80, reason="offline fit",
            status="notified",
        )
        package = await repo.save_application(
            user_id=owner.id, job_id=job.id, source_id="fixture", status="prepared",
            vacancy_snapshot={"title": "Platform Engineer", "source_id": "fixture"},
            message="Owner-reviewed draft",
        )
        foreign = await repo.save_application(
            user_id=stranger.id, job_id=job.id, source_id="fixture", status="prepared",
            vacancy_snapshot={"title": "Private other package"}, message="Other owner draft",
        )

        app = gui.create_app(object(), "web-test-token-long-enough")
        async with TestServer(app) as server, TestClient(server, cookie_jar=CookieJar(unsafe=True)) as client:
            login = await client.post("/login", data={"token": "web-test-token-long-enough"}, allow_redirects=False)
            assert login.status == 303
            for page in gui.PAGES:
                response = await client.get(f"/{page}")
                assert response.status == 200, page
                body = await response.text()
                assert "Private other package" not in body
            jobs = await (await client.get("/jobs")).text()
            assert "Platform Engineer" in jobs
            assert "offline fit" in jobs
            cv = await (await client.get("/cv")).text()
            assert "Owner CV" in cv

            saved = await client.post("/action/match", data={"csrf": app["csrf"], "id": str(match.id), "status": "saved"}, allow_redirects=False)
            assert saved.status == 303
            assert (await repo.get_match(match.id)).status == "saved"
            updated = await client.post("/action/application", data={"csrf": app["csrf"], "id": str(package.id), "status": "reviewed"}, allow_redirects=False)
            assert updated.status == 303
            assert (await repo.get_application(owner.id, package.id)).status == "reviewed"
            assert [event.status for event in await repo.application_status_history(owner.id, package.id)] == ["prepared", "reviewed"]
            detail = await client.get(f"/application/{package.id}")
            assert detail.status == 200
            assert "Owner-reviewed draft" in await detail.text()
            exported = await client.get(f"/application/{package.id}/export")
            assert exported.status == 200
            assert "Owner-reviewed draft" in await exported.text()
            assert (await client.get(f"/application/{foreign.id}")).status == 404
    finally:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine.dispose()
