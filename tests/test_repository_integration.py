import asyncio
import os

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import repository as repo
from app.database.models import Base
from app.domain.jobs import NormalizedJob


TEST_DATABASE_URL = os.getenv("JOB_AGENT_TEST_DATABASE_URL")

def _require_test_database():
    if TEST_DATABASE_URL:
        return
    if os.getenv("CI"):
        pytest.fail("CI requires JOB_AGENT_TEST_DATABASE_URL")
    pytest.skip("JOB_AGENT_TEST_DATABASE_URL is not configured")


@pytest.mark.integration
def test_repository_review_flow_uses_real_postgres(monkeypatch):
    _require_test_database()

    asyncio.run(_repository_review_flow(monkeypatch))


async def _repository_review_flow(monkeypatch):
    engine = create_async_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    test_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    monkeypatch.setattr(repo, "SessionLocal", test_session)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    try:
        user = await repo.create_user("integration-1001", "Integration User")
        loaded_user = await repo.get_user_by_chat("integration-1001")
        assert loaded_user is not None
        assert loaded_user.id == user.id

        profile = await repo.ensure_default_profile(user.id)
        searches = await repo.list_search_profiles(profile.id)
        assert len(searches) == 1
        search = searches[0]

        fact = await repo.add_fact(
            profile.id,
            "Commercial Linux administration",
            experience_type="commercial",
        )
        facts = await repo.list_facts(profile.id)
        assert [item.id for item in facts] == [fact.id]
        assert facts[0].experience_type == "commercial"

        resume = await repo.add_resume(
            profile.id,
            "Integration Resume",
            "en",
            "DevOps Engineer",
        )
        resumes = await repo.list_resumes(profile.id)
        assert [item.id for item in resumes] == [resume.id]

        normalized = NormalizedJob(
            source="integration",
            source_job_id="job-1001",
            title="DevOps Engineer",
            company="Integration Corp",
            description="Linux Docker Terraform",
            url="https://example.invalid/job-1001",
            country="RU",
            work_mode="remote",
        )

        job, created = await repo.upsert_job(normalized)
        assert created is True

        same_job, created_again = await repo.upsert_job(normalized)
        assert created_again is False
        assert same_job.id == job.id

        match = await repo.save_match(
            job_id=job.id,
            user_id=user.id,
            profile_id=profile.id,
            search_profile_id=search.id,
            resume_id=resume.id,
            technical_score=80,
            geography_score=90,
            salary_score=70,
            relocation_score=50,
            total_score=78,
            reason="integration test",
            status="notified",
        )

        review = await repo.review_matches(user.id, 10)
        assert len(review) == 1
        assert review[0][0].id == match.id
        assert review[0][1].id == job.id

        await repo.set_match_status(match.id, "saved")

        assert await repo.review_matches(user.id, 10) == []

        stored_match = await repo.get_match(match.id)
        assert stored_match is not None
        assert stored_match.status == "saved"
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest.mark.integration
def test_repository_repost_and_match_update_use_real_postgres(monkeypatch):
    _require_test_database()

    asyncio.run(_repository_repost_flow(monkeypatch))


async def _repository_repost_flow(monkeypatch):
    engine = create_async_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    test_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    monkeypatch.setattr(repo, "SessionLocal", test_session)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    try:
        user = await repo.create_user("integration-2001", "Repost User")
        profile = await repo.ensure_default_profile(user.id)
        search = (await repo.list_search_profiles(profile.id))[0]

        original = NormalizedJob(
            source="integration-a",
            source_job_id="job-a",
            title="DevOps Engineer",
            company="Example Corp",
            city="Moscow",
            country="RU",
            raw={"stage": "original"},
        )
        job1, created = await repo.upsert_job(original)
        assert created is True

        match = await repo.save_match(
            job_id=job1.id,
            user_id=user.id,
            profile_id=profile.id,
            search_profile_id=search.id,
            technical_score=70,
            geography_score=80,
            salary_score=60,
            relocation_score=50,
            total_score=68,
            reason="first score",
            status="notified",
        )

        await repo.set_match_status(match.id, "saved")

        repost = NormalizedJob(
            source="integration-b",
            source_job_id="job-b",
            title="  DEVOPS   ENGINEER ",
            company=" example corp ",
            city="Tver",
            country="RU",
        )
        job2, created = await repo.upsert_job(repost)
        assert created is True
        assert job2.id != job1.id

        assert await repo.has_notified_equivalent(
            user.id, job2.id, repost.title, repost.company
        ) is True

        updated = await repo.save_match(
            job_id=job1.id,
            user_id=user.id,
            profile_id=profile.id,
            search_profile_id=search.id,
            technical_score=90,
            geography_score=90,
            salary_score=80,
            relocation_score=60,
            total_score=86,
            reason="rescored",
            status="skipped",
        )
        assert updated.id == match.id
        assert updated.total_score == 86
        assert updated.status == "skipped"

        stored = await repo.get_match_for_user_job(user.id, job1.id)
        assert stored is not None
        assert stored.id == match.id
        assert stored.status == "skipped"

        assert await repo.review_matches(user.id, 10) == []

        latest = await repo.latest_matches(user.id, 10)
        assert len(latest) == 1
        assert latest[0][0].id == match.id

        ref = await repo.source_ref(job1.id, "integration-a")
        assert ref is not None
        await repo.update_source_ref_raw(ref.id, {"cached": True})

        refreshed_ref = await repo.source_ref(job1.id, "integration-a")
        assert refreshed_ref is not None
        assert refreshed_ref.raw == {"cached": True}

        assert await repo.has_notified_equivalent(
            user.id, job2.id, "", repost.company
        ) is False
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()
