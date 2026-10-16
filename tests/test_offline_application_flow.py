"""One offline PostgreSQL path from source discovery to package export."""

import asyncio
import os

import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import repository as repo
from app.database.models import Base, JobMatch
from app.domain.application_package import snapshot_vacancy
from app.domain.jobs import NormalizedJob
from app.domain.source_posting import source_posting_view
from app.matching.technical_score import score_technical_v2
from app.telegram.vacancy_view import render_application_export


@pytest.mark.integration
def test_discovery_review_prepare_export_retains_selected_posting(monkeypatch):
    database_url = os.getenv("JOB_AGENT_TEST_DATABASE_URL")
    if not database_url:
        if os.getenv("CI"):
            pytest.fail("CI requires JOB_AGENT_TEST_DATABASE_URL")
        pytest.skip("JOB_AGENT_TEST_DATABASE_URL is not configured")
    asyncio.run(_offline_flow(database_url, monkeypatch))


async def _offline_flow(database_url, monkeypatch):
    engine = create_async_engine(database_url, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    monkeypatch.setattr(repo, "SessionLocal", session_factory)
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
            await connection.run_sync(Base.metadata.create_all)

        owner = await repo.create_user("offline-flow-owner", "Owner")
        stranger = await repo.create_user("offline-flow-stranger", "Stranger")
        profile = await repo.ensure_default_profile(owner.id)
        search = (await repo.list_search_profiles(profile.id))[0]
        linux = await repo.add_fact(
            profile.id, "Commercial Linux administration",
            experience_type="commercial", provenance="manual",
        )
        first, created = await repo.upsert_job(NormalizedJob(
            source="board_a", source_job_id="posting-a",
            title="Platform Engineer", company="Example", country="GE",
            city="Tbilisi", description="Requirements: Docker",
            url="https://example.invalid/a",
        ))
        assert created
        second, created = await repo.upsert_job(NormalizedJob(
            source="board_b", source_job_id="posting-b",
            title="Platform Engineer", company="Example", country="GE",
            city="Tbilisi", description="Requirements: Linux",
            url="https://example.invalid/b",
        ))
        assert not created and second.id == first.id
        ref_a = await repo.source_ref(first.id, "board_a", source_job_id="posting-a")
        ref_b = await repo.source_ref(first.id, "board_b", source_job_id="posting-b")
        selected = source_posting_view(second, ref_b)
        assert score_technical_v2(source_posting_view(second, ref_a).description, [linux]) == 0
        assert score_technical_v2(selected.description, [linux]) == 100

        match = await repo.save_match(
            job_id=second.id, user_id=owner.id, profile_id=profile.id,
            search_profile_id=search.id, technical_score=100,
            total_score=90, reason="offline selected posting", status="notified",
        )
        assert [item.id for item, _ in await repo.review_matches(owner.id)] == [match.id]
        assert await repo.review_matches(stranger.id) == []
        await repo.set_match_status(match.id, "saved")
        assert [item.id for item, _ in await repo.saved_matches(owner.id)] == [match.id]

        with pytest.raises(ValueError, match="Match не найден"):
            await repo.save_prepared_application(
                match.id, stranger.id, job_id=second.id, source_id="board_b",
            )

        def reject_match_update(session, flush_context, instances):
            if any(isinstance(item, JobMatch) and item.status == "prepared" for item in session.dirty):
                raise RuntimeError("injected match update failure")

        event.listen(AsyncSession.sync_session_class, "before_flush", reject_match_update)
        try:
            with pytest.raises(RuntimeError, match="injected match update failure"):
                await repo.save_prepared_application(
                    match.id, owner.id, job_id=second.id, source_id="board_b",
                )
        finally:
            event.remove(AsyncSession.sync_session_class, "before_flush", reject_match_update)
        assert (await repo.get_match(match.id)).status == "saved"
        assert await repo.list_applications(owner.id) == []

        async def save_package():
            return await repo.save_prepared_application(
                match.id, owner.id, job_id=second.id, source_id="board_b",
                message="Reviewable draft",
                vacancy_snapshot=snapshot_vacancy(
                    selected, source_id="board_b", source_job_id="posting-b",
                    source_url=ref_b.url,
                ),
            )

        first_save, retry_save = await asyncio.gather(save_package(), save_package())
        assert sorted((first_save[1], retry_save[1])) == [False, True]
        package = first_save[0]
        assert retry_save[0].id == package.id
        assert (await repo.get_match(match.id)).status == "prepared"
        same_package, created = await repo.save_prepared_application(
            match.id, owner.id, job_id=second.id, source_id="board_b",
            message="This regenerated text must not replace the durable draft",
            vacancy_snapshot={"title": "Changed after lost Telegram response"},
        )
        assert created is False
        assert same_package.id == package.id
        assert len(await repo.list_applications(owner.id)) == 1
        await repo.upsert_job(NormalizedJob(
            source="board_a", source_job_id="posting-a",
            title="Platform Engineer", company="Example", country="GE",
            city="Tbilisi", description="Requirements: Terraform",
            url="https://example.invalid/a-updated",
        ))

        saved = await repo.get_application(owner.id, package.id)
        exported = render_application_export(saved)
        assert "Saved posting source: board_b" in exported
        assert "Saved provider posting ID: posting-b" in exported
        assert "Requirements: Linux" in exported
        assert "https://example.invalid/b" in exported
        assert "Terraform" not in exported
        assert await repo.get_application(stranger.id, package.id) is None
        assert await repo.application_status_history(stranger.id, package.id) is None
        assert [event.status for event in await repo.application_status_history(owner.id, package.id)] == ["prepared"]
    finally:
        await engine.dispose()
