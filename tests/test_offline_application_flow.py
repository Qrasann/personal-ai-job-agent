"""One offline PostgreSQL path from source discovery to package export."""

import asyncio
import os
from types import SimpleNamespace
from unittest.mock import AsyncMock

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
from app.telegram import handlers


@pytest.mark.integration
def test_discovery_review_prepare_export_retains_selected_posting(monkeypatch):
    database_url = os.getenv("JOB_AGENT_TEST_DATABASE_URL")
    if not database_url:
        if os.getenv("CI"):
            pytest.fail("CI requires JOB_AGENT_TEST_DATABASE_URL")
        pytest.skip("JOB_AGENT_TEST_DATABASE_URL is not configured")
    asyncio.run(_offline_flow(database_url, monkeypatch))


@pytest.mark.integration
def test_prepare_telegram_delivery_failure_then_retry_reuses_postgres_package(monkeypatch):
    database_url = os.getenv("JOB_AGENT_TEST_DATABASE_URL")
    if not database_url:
        if os.getenv("CI"):
            pytest.fail("CI requires JOB_AGENT_TEST_DATABASE_URL")
        pytest.skip("JOB_AGENT_TEST_DATABASE_URL is not configured")
    asyncio.run(_prepare_delivery_retry_flow(database_url, monkeypatch))


async def _prepare_delivery_retry_flow(database_url, monkeypatch):
    engine = create_async_engine(database_url, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    monkeypatch.setattr(repo, "SessionLocal", session_factory)
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
            await connection.run_sync(Base.metadata.create_all)

        owner = await repo.create_user("prepare-retry-owner", "Prepare Retry Owner")
        profile = await repo.ensure_default_profile(owner.id)
        search = (await repo.list_search_profiles(profile.id))[0]
        job, created = await repo.upsert_job(NormalizedJob(
            source="board_retry", source_job_id="posting-retry",
            title="Platform Engineer", company="Example", country="GE",
            city="Tbilisi", description="Requirements: Linux",
            url="https://example.invalid/platform",
        ))
        assert created
        match = await repo.save_match(
            job_id=job.id, user_id=owner.id, profile_id=profile.id,
            search_profile_id=search.id, total_score=80,
            reason="offline retry fixture", status="notified",
        )

        monkeypatch.setattr(handlers, "_require_user", AsyncMock(return_value=owner))
        prepare = AsyncMock(return_value={
            "job": job, "source": "board_retry", "source_job_id": "posting-retry",
            "url": "https://example.invalid/platform", "cover_letter": "Grounded draft",
            "resume": None, "relocation_evidence": None,
        })
        monkeypatch.setattr(handlers, "prepare_match", prepare)
        monkeypatch.setattr(handlers, "render_application_package", lambda _payload: "REVIEW PREVIEW")

        first_progress = SimpleNamespace(edit_text=AsyncMock(side_effect=RuntimeError("Telegram timeout")))
        first_message = SimpleNamespace(
            text=f"/prepare {job.id}", answer=AsyncMock(return_value=first_progress),
        )
        await handlers.prepare_command(first_message)

        saved = await repo.list_applications(owner.id)
        assert len(saved) == 1
        package = saved[0]
        assert package.message == "Grounded draft"
        assert package.source_id == "board_retry"
        assert package.vacancy_snapshot["source_id"] == "board_retry"
        assert package.vacancy_snapshot["source_job_id"] == "posting-retry"
        assert (await repo.get_match(match.id)).status == "prepared"
        assert [item.status for item in await repo.application_status_history(owner.id, package.id)] == ["prepared"]
        notice = first_message.answer.await_args_list[-1].args[0]
        assert "Пакет уже сохранён" in notice
        assert "Telegram timeout" not in notice

        second_progress = SimpleNamespace(edit_text=AsyncMock())
        second_message = SimpleNamespace(
            text=f"/prepare {job.id}", answer=AsyncMock(return_value=second_progress),
        )
        await handlers.prepare_command(second_message)

        assert len(await repo.list_applications(owner.id)) == 1
        assert (await repo.get_application(owner.id, package.id)).message == "Grounded draft"
        assert "уже сохранён" in second_progress.edit_text.await_args.args[0]
        prepare.assert_awaited_once_with(match.id, owner.id)
    finally:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine.dispose()


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

        package, created = await repo.save_prepared_application(
            match.id, owner.id, job_id=second.id, source_id="board_b",
            message="Reviewable draft",
            vacancy_snapshot=snapshot_vacancy(
                selected, source_id="board_b", source_job_id="posting-b",
                source_url=ref_b.url,
            ),
        )
        assert created
        assert package.vacancy_snapshot[repo.PREPARED_MATCH_SNAPSHOT_KEY] == match.id
        assert (await repo.prepared_application_for_match(match.id, owner.id)).id == package.id
        assert (await repo.get_match(match.id)).status == "prepared"

        # A Telegram delivery failure followed by a retry must reuse this exact
        # durable package, even if its status changed after the first save.
        assert await repo.set_application_status(owner.id, package.id, "reviewed")
        duplicate, created = await repo.save_prepared_application(
            match.id, owner.id, job_id=second.id, source_id="board_a",
            message="Must not replace the reviewed package",
            vacancy_snapshot=snapshot_vacancy(
                second, source_id="board_a", source_job_id="posting-a",
            ),
        )
        assert not created
        assert duplicate.id == package.id
        assert duplicate.source_id == "board_b"
        assert duplicate.message == "Reviewable draft"
        assert duplicate.status == "reviewed"
        assert len(await repo.list_applications(owner.id)) == 1
        assert [event.status for event in await repo.application_status_history(owner.id, package.id)] == [
            "prepared", "reviewed",
        ]

        # The match-row lock serializes simultaneous retries too.
        concurrent_job, _ = await repo.upsert_job(NormalizedJob(
            source="board_b", source_job_id="concurrent-posting",
            title="SRE", company="Another Example", description="Linux",
        ))
        concurrent_match = await repo.save_match(
            job_id=concurrent_job.id, user_id=owner.id, profile_id=profile.id,
            search_profile_id=search.id, status="saved",
        )
        concurrent = await asyncio.gather(*[
            repo.save_prepared_application(
                concurrent_match.id, owner.id, job_id=concurrent_job.id, source_id="board_b",
                message="Concurrent retry",
                vacancy_snapshot=snapshot_vacancy(concurrent_job, source_id="board_b"),
            )
            for _ in range(2)
        ])
        assert sorted(created for _, created in concurrent) == [False, True]
        assert concurrent[0][0].id == concurrent[1][0].id
        assert len(await repo.list_applications(owner.id)) == 2
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
        assert [event.status for event in await repo.application_status_history(owner.id, package.id)] == [
            "prepared", "reviewed",
        ]
    finally:
        await engine.dispose()
