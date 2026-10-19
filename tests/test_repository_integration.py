import asyncio
import os
from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import event, func, select, text
from sqlalchemy.exc import DBAPIError

from app.database import repository as repo
from app.database.migrations import apply_migrations
from app.database.models import Application, ApplicationStatusEvent, Base, CandidateFact, Job, JobSourceRef, ResumeProfile, SchemaMigration
from app.domain.jobs import NormalizedJob
from app.domain.application_package import snapshot_vacancy
from app.domain.source_posting import posting_snapshot_digest, source_posting_view


TEST_DATABASE_URL = os.getenv("JOB_AGENT_TEST_DATABASE_URL")

def _require_test_database():
    if TEST_DATABASE_URL:
        return
    if os.getenv("CI"):
        pytest.fail("CI requires JOB_AGENT_TEST_DATABASE_URL")
    pytest.skip("JOB_AGENT_TEST_DATABASE_URL is not configured")


@pytest.mark.integration
def test_concurrent_resume_import_fingerprint_is_persisted_only_once(monkeypatch):
    _require_test_database()
    asyncio.run(_concurrent_resume_import_flow(monkeypatch))


async def _concurrent_resume_import_flow(monkeypatch):
    engine = create_async_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    test_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    monkeypatch.setattr(repo, "SessionLocal", test_session)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        owner = await repo.create_user("resume-import-race", "Owner")
        profile = await repo.ensure_default_profile(owner.id)
        fact = {"category": "skills", "value": "Linux", "confidence": 0.9, "section": "Skills"}

        async def import_same_file():
            return await repo.add_imported_resume_with_facts(
                profile.id, "Concurrent import", "en", "DevOps", "Linux", "same-sha256", [fact],
            )

        outcomes = await asyncio.gather(import_same_file(), import_same_file(), return_exceptions=True)
        saved = [item for item in outcomes if isinstance(item, ResumeProfile)]
        assert len(saved) == 1, "concurrent uploads of one fingerprint created duplicate resume rows"
        duplicate = [item for item in outcomes if isinstance(item, repo.ResumeImportExists)]
        assert len(saved) == len(duplicate) == 1
        assert duplicate[0].resume_id == saved[0].id
        assert len(await repo.list_resumes(profile.id)) == 1
        imported_facts = [item for item in await repo.list_facts(profile.id) if item.provenance == "resume_import"]
        assert len(imported_facts) == 1
        assert imported_facts[0].value == "Linux"
    finally:
        await engine.dispose()


@pytest.mark.integration
def test_repository_review_flow_uses_real_postgres(monkeypatch):
    _require_test_database()

    asyncio.run(_repository_review_flow(monkeypatch))


@pytest.mark.integration
def test_application_migrations_upgrade_v4_schema_and_seed_current_status(monkeypatch):
    _require_test_database()

    asyncio.run(_application_migration_flow(monkeypatch))


async def _application_migration_flow(monkeypatch):
    engine = create_async_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    test_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    monkeypatch.setattr(repo, "SessionLocal", test_session)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    try:
        user = await repo.create_user("migration-user", "Migration User")
        job, _ = await repo.upsert_job(NormalizedJob(
            source="migration", source_job_id="legacy-job", title="Linux Admin",
            company="Legacy Co", url="https://example.invalid/legacy",
        ))
        async with test_session() as session:
            legacy = Application(
                user_id=user.id,
                job_id=job.id,
                source_id="hh",
                resume_id=None,
                message="Previously submitted draft",
                status="submitted",
                created_at=datetime(2025, 1, 2, 3, 4),
            )
            session.add(legacy)
            session.add_all([
                SchemaMigration(version=version, name=f"legacy_{version}")
                for version in (1, 2, 3, 4)
            ])
            await session.commit()
            await session.refresh(legacy)
            application_id = legacy.id

        async with engine.begin() as conn:
            await conn.execute(text("DROP TABLE application_status_events"))
            await conn.execute(text("ALTER TABLE applications DROP COLUMN resume_snapshot"))
            await conn.execute(text("ALTER TABLE applications DROP COLUMN resume_external_id"))
            await conn.execute(text("ALTER TABLE applications DROP COLUMN vacancy_snapshot"))
            applied = await apply_migrations(conn)

        assert applied == [5, 6, 7, 8]
        async with engine.begin() as conn:
            assert await apply_migrations(conn) == []
        events = await repo.application_status_history(user.id, application_id)
        assert events is not None
        assert [(event.status, event.created_at) for event in events] == [
            ("submitted", datetime(2025, 1, 2, 3, 4)),
        ]
        loaded = await repo.get_application(user.id, application_id)
        assert loaded.resume_snapshot == ""
        assert loaded.resume_external_id is None
        assert loaded.vacancy_snapshot == {}
    finally:
        await engine.dispose()


@pytest.mark.integration
def test_v7_to_v8_job_delete_protects_application_history(monkeypatch):
    _require_test_database()
    asyncio.run(_application_history_restrict_migration_flow(monkeypatch))


async def _application_history_restrict_migration_flow(monkeypatch):
    from sqlalchemy.exc import IntegrityError

    engine = create_async_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    test_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    monkeypatch.setattr(repo, "SessionLocal", test_session)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
            # Recreate the actual v7 cascade constraint for upgrade coverage.
            await conn.execute(text("ALTER TABLE applications DROP CONSTRAINT applications_job_id_fkey"))
            await conn.execute(text(
                "ALTER TABLE applications ADD CONSTRAINT applications_job_id_fkey "
                "FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE"
            ))
        owner = await repo.create_user("app-history-owner", "Owner")
        job, _ = await repo.upsert_job(NormalizedJob(
            source="hh", source_job_id="history-preserve-1", title="SRE",
            company="Example", description="Original description",
        ))
        application = await repo.save_application(
            user_id=owner.id, job_id=job.id, source_id="hh", status="submitted",
            message="Approved application text",
            vacancy_snapshot={"title": "SRE", "source_job_id": "history-preserve-1"},
        )
        async with engine.begin() as conn:
            for version in range(1, 8):
                await conn.execute(
                    text("INSERT INTO schema_migrations(version,name,applied_at) "
                         "VALUES (:version,:name,CURRENT_TIMESTAMP)"),
                    {"version": version, "name": f"v{version}"},
                )
            before = await conn.scalar(text(
                "SELECT pg_get_constraintdef(oid) FROM pg_constraint "
                "WHERE conname = 'applications_job_id_fkey' "
                "AND conrelid = 'applications'::regclass"
            ))
            assert "ON DELETE CASCADE" in before
            assert await apply_migrations(conn) == [8]
            after = await conn.scalar(text(
                "SELECT pg_get_constraintdef(oid) FROM pg_constraint "
                "WHERE conname = 'applications_job_id_fkey' "
                "AND conrelid = 'applications'::regclass"
            ))
            assert "ON DELETE RESTRICT" in after
            assert await apply_migrations(conn) == []

        with pytest.raises(IntegrityError):
            async with engine.begin() as conn:
                await conn.execute(text("DELETE FROM jobs WHERE id = :job_id"), {"job_id": job.id})
        saved = await repo.get_application(owner.id, application.id)
        assert saved is not None
        assert saved.message == "Approved application text"
        assert saved.vacancy_snapshot["title"] == "SRE"
        assert [item.status for item in await repo.application_status_history(owner.id, application.id)] == [
            "submitted",
        ]
        assert await repo.get_job(job.id) is not None
    finally:
        await engine.dispose()


@pytest.mark.integration
def test_saved_application_posting_survives_later_job_edits(monkeypatch):
    _require_test_database()
    asyncio.run(_application_snapshot_flow(monkeypatch))


async def _application_snapshot_flow(monkeypatch):
    from app.database.models import Job
    from app.domain.application_package import snapshot_vacancy
    from app.telegram.vacancy_view import render_application_export

    engine = create_async_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    test_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    monkeypatch.setattr(repo, "SessionLocal", test_session)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        user = await repo.create_user("snapshot-user", "Snapshot User")
        job, _ = await repo.upsert_job(NormalizedJob(
            source="snapshot", source_job_id="original", title="Original role",
            company="Original company", description="Original requirements",
        ))
        application = await repo.save_application(
            user_id=user.id, job_id=job.id, source_id="snapshot", status="prepared",
            vacancy_snapshot=snapshot_vacancy(job, source_url="https://example.invalid/original"),
        )
        async with test_session() as session:
            changed = await session.get(Job, job.id)
            changed.title = "Changed role"
            changed.company = "Changed company"
            changed.description = "Changed requirements"
            await session.commit()
        loaded = await repo.get_application(user.id, application.id)
        exported = render_application_export(loaded)
        assert "Original role — Original company" in exported
        assert "Original requirements" in exported
        assert "https://example.invalid/original" in exported
        assert "Changed" not in exported
        assert (await repo.get_job(job.id)).title == "Changed role"
    finally:
        await engine.dispose()


@pytest.mark.integration
def test_concurrent_identical_status_updates_append_one_event(monkeypatch):
    _require_test_database()
    asyncio.run(_concurrent_application_status_flow(monkeypatch))


async def _concurrent_application_status_flow(monkeypatch):
    engine = create_async_engine(TEST_DATABASE_URL, connect_args={"server_settings": {
        "application_name": "jobagent-status-concurrency-test", "lock_timeout": "5s",
    }})
    test_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    monkeypatch.setattr(repo, "SessionLocal", test_session)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        user = await repo.create_user("concurrent-status-user", "Status User")
        job, _ = await repo.upsert_job(NormalizedJob(
            source="status-test", source_job_id="1", title="Linux role",
        ))
        application = await repo.save_application(
            user_id=user.id, job_id=job.id, source_id="status-test", status="prepared",
        )

        async def wait_for_both_updates_to_block():
            async with engine.connect() as conn:
                while True:
                    count = await conn.scalar(text(
                        "SELECT count(*) FROM pg_stat_activity WHERE datname = current_database() "
                        "AND application_name = 'jobagent-status-concurrency-test' AND wait_event_type = 'Lock'"
                    ))
                    if count == 2:
                        return
                    await asyncio.sleep(0.01)

        async with test_session() as blocker:
            await blocker.execute(text("SELECT id FROM applications WHERE id = :id FOR UPDATE"), {"id": application.id})
            updates = [asyncio.create_task(repo.set_application_status(user.id, application.id, "reviewed")) for _ in range(2)]
            try:
                # Both requests must reach the DB while the row is locked;
                # this reproduces the old read-then-write race deterministically.
                await asyncio.wait_for(wait_for_both_updates_to_block(), timeout=3)
            finally:
                await blocker.rollback()
                results = await asyncio.gather(*updates, return_exceptions=True)
        assert results == [True, True]
        assert [event.status for event in await repo.application_status_history(user.id, application.id)] == [
            "prepared", "reviewed",
        ]
        assert (await repo.get_application(user.id, application.id)).status == "reviewed"
    finally:
        await engine.dispose()


@pytest.mark.integration
def test_application_status_and_history_roll_back_together_on_event_failure(monkeypatch):
    _require_test_database()
    asyncio.run(_application_status_rollback_flow(monkeypatch))


async def _application_status_rollback_flow(monkeypatch):
    engine = create_async_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    test_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    monkeypatch.setattr(repo, "SessionLocal", test_session)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        user = await repo.create_user("status-rollback-user", "Status Rollback")
        job, _ = await repo.upsert_job(NormalizedJob(
            source="status-rollback", source_job_id="1", title="Linux role",
        ))
        application = await repo.save_application(
            user_id=user.id, job_id=job.id, source_id="status-rollback", status="prepared",
        )

        def reject_interview_event(session, flush_context, instances):
            if any(
                isinstance(item, ApplicationStatusEvent) and item.status == "interview"
                for item in session.new
            ):
                raise RuntimeError("injected status history failure")

        event.listen(AsyncSession.sync_session_class, "before_flush", reject_interview_event)
        try:
            with pytest.raises(RuntimeError, match="injected status history failure"):
                await repo.set_application_status(user.id, application.id, "interview")
        finally:
            event.remove(AsyncSession.sync_session_class, "before_flush", reject_interview_event)

        saved = await repo.get_application(user.id, application.id)
        history = await repo.application_status_history(user.id, application.id)
        assert saved.status == "prepared"
        assert [item.status for item in history] == ["prepared"]
    finally:
        await engine.dispose()


@pytest.mark.integration
def test_incomplete_source_location_does_not_replace_canonical_fingerprint(monkeypatch):
    _require_test_database()
    asyncio.run(_incomplete_source_identity_flow(monkeypatch))


async def _incomplete_source_identity_flow(monkeypatch):
    from app.database.models import Job

    engine = create_async_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    test_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    monkeypatch.setattr(repo, "SessionLocal", test_session)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        job, created = await repo.upsert_job(NormalizedJob(
            source="identity-test", source_job_id="posting-1",
            title="Platform Engineer", company="Example",
            country="GE", city="Tbilisi",
        ))
        assert created
        canonical_fingerprint = job.fingerprint

        refreshed, created = await repo.upsert_job(NormalizedJob(
            source="identity-test", source_job_id="posting-1",
            title="Platform Engineer", company="Example",
            country="  ", city="",
        ))

        assert not created
        assert refreshed.id == job.id
        assert refreshed.fingerprint == canonical_fingerprint
        assert await repo.get_job(job.id) is not None
        async with test_session() as session:
            saved = await session.get(Job, job.id)
            assert saved.country == "GE"
            assert saved.city == "Tbilisi"
    finally:
        await engine.dispose()


@pytest.mark.integration
def test_concurrent_cross_source_ingestion_creates_one_canonical_job(monkeypatch):
    _require_test_database()
    asyncio.run(_concurrent_source_identity_flow(monkeypatch))


async def _concurrent_source_identity_flow(monkeypatch):
    engine = create_async_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    test_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    monkeypatch.setattr(repo, "SessionLocal", test_session)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        jobs = [NormalizedJob(
            source=source, source_job_id=f"posting-{source}",
            title="Platform Engineer", company="Example Corp",
            country="GE", city="Tbilisi",
        ) for source in ("board_a", "board_b")]
        results = await asyncio.gather(*(repo.upsert_job(job) for job in jobs))

        assert len({job.id for job, _ in results}) == 1
        assert sum(int(created) for _, created in results) == 1
        async with test_session() as session:
            assert await session.scalar(select(func.count()).select_from(Job)) == 1
            refs = list(await session.scalars(select(JobSourceRef).order_by(JobSourceRef.source_id)))
        assert [(ref.source_id, ref.source_job_id) for ref in refs] == [
            ("board_a", "posting-board_a"), ("board_b", "posting-board_b"),
        ]
    finally:
        await engine.dispose()


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
        assert (await repo.get_profile(profile.id)).english_level == ""
        await repo.set_profile_english_level(profile.id, "C1")
        assert (await repo.get_profile(profile.id)).english_level == "C1"
        searches = await repo.list_search_profiles(profile.id)
        assert len(searches) == 1
        await repo.configure_parallel_search_profiles(profile.id, enabled=True)
        searches = await repo.list_search_profiles(profile.id)
        assert [item.kind for item in searches] == ["career", "relocation"]
        assert [item.settings["search_strategy"] for item in searches] == ["career_first", "relocation_first"]
        await repo.configure_parallel_search_profiles(profile.id, enabled=True)
        assert len(await repo.list_search_profiles(profile.id)) == 2
        await repo.configure_parallel_search_profiles(profile.id, enabled=False)
        assert [item.kind for item in await repo.list_search_profiles(profile.id)] == ["career"]
        await repo.configure_parallel_search_profiles(profile.id, enabled=True)
        search = (await repo.list_search_profiles(profile.id))[0]

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

        imported = await repo.add_imported_resume_with_facts(
            profile.id, "Atomic import", "en", "DevOps", "Linux", "fingerprint-ok",
            [{"category": "skill", "value": "Linux", "confidence": 0.9, "section": "Skills"}],
        )
        assert imported.external_id == "fingerprint-ok"
        assert any(item.value == "Linux" and item.provenance == "resume_import"
                   for item in await repo.list_facts(profile.id))

        with pytest.raises(DBAPIError):
            await repo.add_imported_resume_with_facts(
                profile.id, "Rollback import", "en", "DevOps", "Docker", "fingerprint-rollback",
                [{"category": "x" * 65, "value": "Docker", "confidence": 1.0, "section": "Skills"}],
            )
        assert all(item.external_id != "fingerprint-rollback" for item in await repo.list_resumes(profile.id))
        retried = await repo.add_imported_resume_with_facts(
            profile.id, "Retry import", "en", "DevOps", "Docker", "fingerprint-rollback",
            [{"category": "skill", "value": "Docker", "confidence": 1.0, "section": "Skills"}],
        )
        assert retried.external_id == "fingerprint-rollback"

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
            recommendation_scores={"_meta": {"match_assessment_version": 1}},
            status="notified",
        )
        assert match.recommendation_scores["_meta"]["match_assessment_version"] == 1

        package = await repo.save_application(
            user_id=user.id,
            job_id=job.id,
            source_id="integration",
            source_application_id=None,
            external_url="https://example.invalid/job-1001",
            resume_id=resume.id,
            resume_snapshot="Saved resume snapshot text",
            resume_external_id="hh-resume-42",
            message="Exact reviewed draft text",
            status="prepared",
        )
        assert package.status == "prepared"
        assert package.message == "Exact reviewed draft text"
        assert package.resume_snapshot == "Saved resume snapshot text"
        assert package.resume_external_id == "hh-resume-42"
        assert [item.id for item in await repo.list_applications(user.id)] == [package.id]
        assert (await repo.get_application(user.id, package.id)).id == package.id
        assert await repo.get_application(user.id + 1, package.id) is None
        assert [item.status for item in await repo.application_status_history(user.id, package.id)] == ["prepared"]
        assert await repo.set_application_status(user.id + 1, package.id, "submitted") is False
        assert await repo.application_status_history(user.id + 1, package.id) is None
        assert await repo.set_application_status(user.id, package.id, "invalid") is False
        assert await repo.set_application_status(user.id, package.id, "reviewed") is True
        assert (await repo.list_applications(user.id))[0].status == "reviewed"
        assert await repo.set_application_status(user.id, package.id, "reviewed") is True
        assert [item.status for item in await repo.application_status_history(user.id, package.id)] == ["prepared", "reviewed"]
        assert await repo.set_application_status(user.id, package.id, "submitted") is True
        assert (await repo.list_applications(user.id))[0].message == "Exact reviewed draft text"
        assert [item.status for item in await repo.application_status_history(user.id, package.id)] == ["prepared", "reviewed", "submitted"]
        assert await repo.list_applications(user.id + 1) == []

        concurrent = await asyncio.gather(*[
            repo.save_match(
                job_id=job.id,
                user_id=user.id,
                profile_id=profile.id,
                search_profile_id=search.id,
                resume_id=resume.id,
                technical_score=80 + index,
                geography_score=90,
                salary_score=70,
                relocation_score=50,
                total_score=78,
                reason=f"concurrent update {index}",
            )
            for index in range(5)
        ])
        assert {item.id for item in concurrent} == {match.id}

        review = await repo.review_matches(user.id, 10)
        assert len(review) == 1
        assert review[0][0].id == match.id
        assert review[0][1].id == job.id
        full_review = await repo.review_matches(user.id, None)
        assert [item[0].id for item in full_review] == [match.id]

        await repo.set_match_status(match.id, "stretch")
        assert await repo.review_matches(user.id, 10) == []
        stretch = await repo.stretch_matches(user.id, None)
        assert [item[0].id for item in stretch] == [match.id]
        assert stretch[0][1].id == job.id


        await repo.set_match_status(match.id, "saved")

        assert await repo.review_matches(user.id, 10) == []
        saved = await repo.saved_matches(user.id, None)
        assert [item[0].id for item in saved] == [match.id]
        assert saved[0][1].id == job.id

        below_job, _ = await repo.upsert_job(NormalizedJob(
            source="integration",
            source_job_id="job-below-threshold",
            title="Warehouse Worker",
            company="Manual Review Logistics",
            description="Warehouse role in Georgia",
            url="https://example.invalid/job-below-threshold",
            country="GE",
        ))
        below_match = await repo.save_match(
            job_id=below_job.id,
            user_id=user.id,
            profile_id=profile.id,
            search_profile_id=search.id,
            technical_score=40,
            geography_score=85,
            salary_score=58,
            relocation_score=42,
            total_score=54,
            reason="below-threshold regression",
            status="filtered",
        )
        lower_job, _ = await repo.upsert_job(NormalizedJob(
            source="integration",
            source_job_id="job-below-threshold-lower",
            title="Kitchen Assistant",
            company="Lower Score Catering",
            description="Kitchen support role in Armenia",
            url="https://example.invalid/job-below-threshold-lower",
            country="AM",
        ))
        lower_match = await repo.save_match(
            job_id=lower_job.id,
            user_id=user.id,
            profile_id=profile.id,
            search_profile_id=search.id,
            technical_score=30,
            geography_score=85,
            salary_score=58,
            relocation_score=42,
            total_score=41,
            reason="lower-score regression",
            status="filtered",
        )
        below_rows = await repo.latest_matches(
            user.id,
            10,
            include_filtered=True,
            min_score=1,
            max_score=64,
        )
        assert [(item.id, listed_job.id) for item, listed_job in below_rows] == [
            (below_match.id, below_job.id),
            (lower_match.id, lower_job.id),
        ]
        above_rows = await repo.latest_matches(user.id, 10, min_score=65)
        assert [(item.id, listed_job.id) for item, listed_job in above_rows] == [
            (match.id, job.id)
        ]

        relocation = next(item for item in await repo.list_search_profiles(profile.id) if item.kind == "relocation")
        relocation_matches = []
        for listed_job, score in ((below_job, 62), (lower_job, 60)):
            relocation_matches.append(await repo.save_match(
                job_id=listed_job.id,
                user_id=user.id,
                profile_id=profile.id,
                search_profile_id=relocation.id,
                technical_score=40,
                geography_score=85,
                salary_score=58,
                relocation_score=42,
                total_score=score,
                reason="independent relocation score",
                status="filtered",
            ))
        scoped_rows = await repo.latest_matches(
            user.id, 10, include_filtered=True, min_score=1, max_score=64,
            search_profile_id=relocation.id,
        )
        assert [item.id for item, _ in scoped_rows] == [item.id for item in relocation_matches]
        career_rows = await repo.latest_matches(
            user.id, 10, include_filtered=True, min_score=1, max_score=64,
            search_profile_id=search.id,
        )
        assert [item.id for item, _ in career_rows] == [below_match.id, lower_match.id]
        assert (await repo.get_match_for_user_job(
            user.id, below_job.id, search_profile_id=relocation.id,
        )).id == relocation_matches[0].id
        assert (await repo.get_match_for_user_job(
            user.id, below_job.id, search_profile_id=search.id,
        )).id == below_match.id
        assert await repo.get_match_for_user_job(user.id, job.id, search_profile_id=relocation.id) is None
        assert await repo.get_match_for_user_job(user.id + 100, below_job.id, search_profile_id=relocation.id) is None
        assert await repo.latest_matches(user.id + 100, search_profile_id=relocation.id) == []

        relocation_settings = {**relocation.settings, "target_countries": ["AM", "GE"], "notify_min_score": 71}
        await repo.update_search_settings(relocation.id, relocation_settings)
        await repo.configure_parallel_search_profiles(profile.id, enabled=False)
        assert [item.kind for item in await repo.list_search_profiles(profile.id)] == ["career"]
        for item in relocation_matches:
            assert (await repo.get_match(item.id)).search_profile_id == relocation.id
        await repo.configure_parallel_search_profiles(profile.id, enabled=True)
        restored = next(item for item in await repo.list_search_profiles(profile.id) if item.kind == "relocation")
        assert restored.id == relocation.id
        assert restored.settings == relocation_settings
        restored_matches = await repo.latest_matches(
            user.id, include_filtered=True, min_score=1, max_score=70,
            search_profile_id=restored.id,
        )
        assert [item.id for item, _ in restored_matches] == [item.id for item in relocation_matches]

        reviewed_fact = await repo.add_fact(profile.id, "Linux Docker", experience_type="commercial")
        replacement = {"existing_id": reviewed_fact.id, "expected_value": "Linux Docker",
                       "category": "skills", "value": "Linux Docker Kubernetes",
                       "confidence": 0.92, "section": "skills"}
        with pytest.raises(repo.FactUpdateConflict):
            await repo.add_imported_resume_with_facts(
                profile.id, "Stale update", "en", "DevOps", "Linux", "stale-update", [],
                replacements=[{**replacement, "expected_value": "unreviewed text"}],
            )
        with pytest.raises(DBAPIError):
            await repo.add_imported_resume_with_facts(
                profile.id, "Failed update", "en", "DevOps", "Linux", "failed-update", [],
                replacements=[{**replacement, "category": "x" * 65}],
            )
        assert reviewed_fact.id in {item.id for item in await repo.list_facts(profile.id)}
        assert all(item.external_id not in {"stale-update", "failed-update"}
                   for item in await repo.list_resumes(profile.id))
        await repo.add_imported_resume_with_facts(
            profile.id, "Reviewed update", "en", "DevOps", "Linux", "reviewed-update", [],
            replacements=[replacement],
        )
        active_facts = await repo.list_facts(profile.id)
        assert reviewed_fact.id not in {item.id for item in active_facts}
        new_fact = next(item for item in active_facts if item.value == replacement["value"])
        assert new_fact.experience_type == "unknown" and new_fact.commercial is False
        assert new_fact.provenance == "resume_import"
        async with test_session() as session:
            retained = await session.get(CandidateFact, reviewed_fact.id)
            assert retained.value == "Linux Docker" and retained.experience_type == "commercial"
            assert retained.active is False

        other_user = await repo.create_user("integration-import-other")
        other_profile = await repo.ensure_default_profile(other_user.id)
        other_fact = await repo.add_fact(other_profile.id, "Other Linux Docker")
        with pytest.raises(repo.FactUpdateConflict):
            await repo.add_imported_resume_with_facts(
                profile.id, "Foreign update", "en", "DevOps", "Linux", "foreign-update", [],
                replacements=[{**replacement, "existing_id": other_fact.id, "expected_value": other_fact.value}],
            )
        assert other_fact.id in {item.id for item in await repo.list_facts(other_profile.id)}
        assert all(item.external_id != "foreign-update" for item in await repo.list_resumes(profile.id))

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
            recommendation_scores={"competition": {"score": None, "evidence": "unknown"}},
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
            recommendation_scores={"technical": {"score": 90, "evidence": "rescored"}},
            total_score=86,
            reason="rescored",
            status="skipped",
        )
        assert updated.id == match.id
        assert updated.total_score == 86
        assert updated.recommendation_scores == {"technical": {"score": 90, "evidence": "rescored"}}
        assert updated.status == "skipped"

        stored = await repo.get_match_for_user_job(user.id, job1.id)
        assert stored is not None
        assert stored.id == match.id
        assert stored.status == "skipped"

        assert await repo.review_matches(user.id, 10) == []

        latest = await repo.latest_matches(user.id, 10)
        assert len(latest) == 1
        assert latest[0][0].id == match.id

        lower_scored_job, lower_created = await repo.upsert_job(
            NormalizedJob(
                source="integration-c",
                source_job_id="job-c",
                title="Linux Administrator",
                company="Different Corp",
                city="Tver",
                country="RU",
            )
        )
        assert lower_created is True
        lower_match = await repo.save_match(
            job_id=lower_scored_job.id,
            user_id=user.id,
            profile_id=profile.id,
            search_profile_id=search.id,
            technical_score=70,
            geography_score=70,
            salary_score=60,
            relocation_score=50,
            total_score=72,
            reason="lower score but newer row",
            status="notified",
        )
        ranked = await repo.latest_matches(user.id, 10)
        assert [item[0].id for item in ranked] == [match.id, lower_match.id]

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


@pytest.mark.integration
def test_repeated_source_upsert_refreshes_job_without_losing_cache_or_application_snapshot(monkeypatch):
    _require_test_database()
    asyncio.run(_repeated_source_upsert_flow(monkeypatch))


@pytest.mark.integration
def test_remotive_candidate_location_stays_remote_scope_after_provider_rediscovery(monkeypatch):
    _require_test_database()
    asyncio.run(_remotive_remote_scope_rediscovery_flow(monkeypatch))


async def _remotive_remote_scope_rediscovery_flow(monkeypatch):
    engine = create_async_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    test_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    monkeypatch.setattr(repo, "SessionLocal", test_session)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        original = NormalizedJob(
            source="remotive", source_job_id="remotive-posting-old",
            title="DevOps Engineer", company="Example Corp",
            description="Remote infrastructure role", country="GE",
            work_mode="remote", remote_scope="Georgia",
            raw={"candidate_required_location": "Georgia"},
        )
        job, created = await repo.upsert_job(original)
        assert created
        first_ref = await repo.source_ref(job.id, "remotive", source_job_id="remotive-posting-old")
        first_evidence = first_ref.raw["relocation_evidence_v1"]["fields"]["work_country"]
        assert first_ref.raw["normalized_posting_v1"]["remote_scope"] == "Georgia"
        assert first_evidence["status"] == "unknown"
        assert first_evidence["value"] is None

        rediscovered = NormalizedJob(
            source="remotive", source_job_id="remotive-posting-new",
            title="DevOps Engineer", company="Example Corp",
            description="Remote infrastructure role, refreshed", country="GE",
            work_mode="remote", remote_scope="Georgia",
            raw={"candidate_required_location": "Georgia", "revision": "new"},
        )
        same_job, created = await repo.upsert_job(rediscovered)
        assert not created and same_job.id == job.id
        new_ref = await repo.source_ref(job.id, "remotive", source_job_id="remotive-posting-new")
        selected_ref = await repo.source_ref(job.id, "remotive")
        assert new_ref.source_job_id == "remotive-posting-new"
        assert new_ref.raw["revision"] == "new"
        assert new_ref.raw["normalized_posting_v1"]["remote_scope"] == "Georgia"
        assert new_ref.raw["relocation_evidence_v1"]["fields"]["work_country"]["status"] == "unknown"
        assert selected_ref.source_job_id == "remotive-posting-new"
        assert source_posting_view(same_job, selected_ref).remote_scope == "Georgia"
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


async def _repeated_source_upsert_flow(monkeypatch):
    engine = create_async_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    test_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    monkeypatch.setattr(repo, "SessionLocal", test_session)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    try:
        user = await repo.create_user("refresh-owner", "Refresh Owner")
        original = NormalizedJob(
            source="refresh-source", source_job_id="stable-posting-id",
            title="Linux Engineer", company="Refresh Co", description="Old summary",
            url="https://jobs.example/old", city="Tbilisi", country="GE",
            salary_from=1000, salary_currency="USD", salary_period="monthly",
            visa_sponsorship=True,
            raw={
                "listing_revision": "old",
                "source_location": "Tbilisi, Georgia (synthetic fixture)",
                "details_cache_v1": {"description": "Verified full details"},
            },
        )
        job, created = await repo.upsert_job(original)
        assert created is True
        first_ref = await repo.source_ref(job.id, "refresh-source")
        saved_evidence = first_ref.raw["relocation_evidence_v1"]
        assert first_ref.raw["normalized_posting_v1"]["description"] == "Old summary"
        assert await repo.save_source_ref_detail_cache(first_ref.id, {"description": "Verified full details"}) is True
        first_ref = await repo.source_ref(job.id, "refresh-source")
        old_digest = posting_snapshot_digest(first_ref.raw["normalized_posting_v1"])
        assert first_ref.raw["details_cache_posting_digest_v1"] == old_digest
        application = await repo.save_application(
            user_id=user.id, job_id=job.id, source_id="refresh-source",
            source_application_id=None, external_url=original.url, resume_id=None,
            resume_snapshot="Saved CV", resume_external_id=None,
            vacancy_snapshot=snapshot_vacancy(
                job, source_url=original.url, relocation_evidence=saved_evidence,
            ),
            message="Saved cover letter", status="prepared",
        )
        assert saved_evidence["schema"] == "relocation_evidence_v1"
        assert saved_evidence["fields"]["work_country"]["value"] == "GE"
        assert saved_evidence["fields"]["work_country"]["excerpt"] == "Tbilisi, Georgia (synthetic fixture)"
        assert saved_evidence["fields"]["visa_sponsorship"]["value"] is None
        assert saved_evidence["fields"]["visa_sponsorship"]["status"] == "unknown"

        refreshed = NormalizedJob(
            source="refresh-source", source_job_id="stable-posting-id",
            title="Senior Linux Engineer", company="Refresh Co", description="Updated summary with Kubernetes",
            url="https://jobs.example/current", city="Tbilisi", country="GE",
            salary_from=2400, salary_currency="USD", salary_period="monthly",
            visa_sponsorship=None,
            raw={
                "listing_revision": "new", "new_provenance": "present in latest response",
                "source_location": "Updated Tbilisi, Georgia (synthetic fixture)",
            },
        )
        same_job, created_again = await repo.upsert_job(refreshed)

        assert same_job.id == job.id
        assert created_again is False
        assert same_job.title == "Senior Linux Engineer"
        assert same_job.description == refreshed.description
        assert same_job.salary_from == 2400
        assert same_job.salary_period == "monthly"
        assert same_job.visa_sponsorship is True
        latest_ref = await repo.source_ref(job.id, "refresh-source")
        assert latest_ref.url == refreshed.url
        assert latest_ref.raw["listing_revision"] == "new"
        assert latest_ref.raw["new_provenance"] == "present in latest response"
        assert latest_ref.raw["normalized_posting_v1"]["description"] == refreshed.description
        assert latest_ref.raw["details_cache_v1"] == {"description": "Verified full details"}
        assert latest_ref.raw["details_cache_posting_digest_v1"] == old_digest
        assert source_posting_view(same_job, latest_ref).description == refreshed.description
        updated_evidence = latest_ref.raw["relocation_evidence_v1"]
        assert updated_evidence["fields"]["work_country"]["value"] == "GE"
        assert updated_evidence["fields"]["work_country"]["excerpt"] == "Updated Tbilisi, Georgia (synthetic fixture)"
        assert updated_evidence["fields"]["visa_sponsorship"]["status"] == "unknown"
        assert updated_evidence["captured_at"]
        assert latest_ref.first_seen_at == first_ref.first_seen_at

        saved = await repo.get_application(user.id, application.id)
        assert saved.vacancy_snapshot == {
            "title": "Linux Engineer", "company": "Refresh Co",
            "description": "Old summary", "source_url": original.url,
            "relocation_evidence": saved_evidence,
        }
        assert saved.vacancy_snapshot["relocation_evidence"]["fields"]["work_country"]["excerpt"] == "Tbilisi, Georgia (synthetic fixture)"
        assert saved.resume_snapshot == "Saved CV"
        assert saved.message == "Saved cover letter"

        cache_race_job = NormalizedJob(
            source="refresh-source", source_job_id="stable-posting-id",
            title="Senior Linux Engineer", company="Refresh Co",
            description="Another refreshed summary", city="Tbilisi", country="GE",
            raw={"listing_revision": "newest"},
        )
        await asyncio.gather(
            repo.upsert_job(cache_race_job),
            repo.save_source_ref_detail_cache(
                latest_ref.id, {"description": "Newly verified full details"}
            ),
        )
        raced_ref = await repo.source_ref(job.id, "refresh-source")
        assert raced_ref.raw["listing_revision"] == "newest"
        assert raced_ref.raw["details_cache_v1"] == {
            "description": "Newly verified full details"
        }
        rejected = await repo.save_source_ref_detail_cache(
            raced_ref.id, {"description": "Raced old details"},
            expected_posting_digest=posting_snapshot_digest(latest_ref.raw["normalized_posting_v1"]),
        )
        assert rejected is False
        assert (await repo.source_ref(job.id, "refresh-source")).raw["details_cache_v1"] == {
            "description": "Newly verified full details"
        }

        cross_source, cross_source_created = await repo.upsert_job(NormalizedJob(
            source="second-board", source_job_id="same-role",
            title="Senior Linux Engineer", company="Refresh Co", description="Cross-post",
            city="Tbilisi", country="GE",
        ))
        assert cross_source.id == job.id
        assert cross_source_created is False
        second_ref = await repo.source_ref(job.id, "second-board")
        assert second_ref.raw["normalized_posting_v1"]["description"] == "Cross-post"
        assert (await repo.source_ref(job.id, "refresh-source")).raw["normalized_posting_v1"]["description"] == "Another refreshed summary"
        await asyncio.sleep(0.01)
        second_listing, second_created = await repo.upsert_job(NormalizedJob(
            source="second-board", source_job_id="same-role-2",
            title="Senior Linux Engineer", company="Refresh Co", description="A different listing",
            city="Tbilisi", country="GE",
        ))
        assert second_listing.id == job.id and second_created is False
        exact_ref = await repo.source_ref(job.id, "second-board", source_job_id="same-role-2")
        assert exact_ref.source_job_id == "same-role-2"
        assert exact_ref.raw["normalized_posting_v1"]["description"] == "A different listing"
        assert (await repo.source_ref(job.id, "second-board", source_job_id="same-role")).id == second_ref.id
        selected_ref = await repo.source_ref(job.id, "second-board")
        assert selected_ref.source_job_id == "same-role-2"
        assert source_posting_view(second_listing, selected_ref).description == "A different listing"
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest.mark.integration
def test_parallel_cross_source_upserts_share_one_canonical_job(monkeypatch):
    _require_test_database()
    asyncio.run(_parallel_cross_source_upsert_flow(monkeypatch))


async def _parallel_cross_source_upsert_flow(monkeypatch):
    engine = create_async_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    test_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    monkeypatch.setattr(repo, "SessionLocal", test_session)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    try:
        postings = [
            NormalizedJob(
                source=f"parallel-board-{index}", source_job_id=f"posting-{index}",
                title="Platform Engineer", company="Parallel Co",
                description=f"Listing from board {index}", country="GE", city="Tbilisi",
            )
            for index in range(2)
        ]
        results = await asyncio.gather(*(repo.upsert_job(posting) for posting in postings))
        assert results[0][0].id == results[1][0].id
        assert sorted(created for _, created in results) == [False, True]
        refs = [await repo.source_ref(results[0][0].id, posting.source) for posting in postings]
        assert all(ref is not None for ref in refs)
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest.mark.integration
def test_review_and_saved_backlogs_exceed_ten_real_postgres(monkeypatch):
    _require_test_database()
    asyncio.run(_review_saved_backlog_flow(monkeypatch))


async def _review_saved_backlog_flow(monkeypatch):
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
        user = await repo.create_user("integration-3001", "Backlog User")
        profile = await repo.ensure_default_profile(user.id)
        search = (await repo.list_search_profiles(profile.id))[0]
        resume = await repo.add_resume(
            profile.id,
            "Backlog Resume",
            "en",
            "DevOps Engineer",
        )

        match_ids = []
        for index in range(12):
            normalized = NormalizedJob(
                source="integration-backlog",
                source_job_id=f"job-{index}",
                title=f"Role {index}",
                company=f"Company {index}",
                country="RU",
            )
            job, _ = await repo.upsert_job(normalized)
            match = await repo.save_match(
                job_id=job.id,
                user_id=user.id,
                profile_id=profile.id,
                search_profile_id=search.id,
                resume_id=resume.id,
                technical_score=80,
                geography_score=80,
                salary_score=60,
                relocation_score=50,
                total_score=90 - index,
                reason="backlog test",
                status="notified",
            )
            match_ids.append(match.id)

        limited_review = await repo.review_matches(user.id, 10)
        full_review = await repo.review_matches(user.id, None)

        assert len(limited_review) == 10
        assert len(full_review) == 12
        assert [item[0].id for item in full_review] == match_ids

        for match_id in match_ids:
            await repo.set_match_status(match_id, "saved")

        assert await repo.review_matches(user.id, None) == []

        full_saved = await repo.saved_matches(user.id, None)
        assert len(full_saved) == 12
        assert [item[0].id for item in full_saved] == match_ids
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()



@pytest.mark.integration
def test_hh_submission_reservation_blocks_concurrent_owner_attempts(monkeypatch):
    _require_test_database()
    asyncio.run(_hh_submission_reservation_flow(monkeypatch))


async def _hh_submission_reservation_flow(monkeypatch):
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"server_settings": {
            "application_name": "jobagent-hh-reservation-test",
            "lock_timeout": "5s",
        }},
    )
    test_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    monkeypatch.setattr(repo, "SessionLocal", test_session)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        user = await repo.create_user("hh-reserve-owner", "HH Owner")
        profile = await repo.ensure_default_profile(user.id)
        searches = await repo.list_search_profiles(profile.id)
        job, _ = await repo.upsert_job(NormalizedJob(
            source="hh", source_job_id="hh-posting-44",
            title="SRE", company="Company", description="Current job",
            url="https://hh.ru/vacancy/hh-posting-44",
        ))
        match = await repo.save_match(
            job_id=job.id, user_id=user.id,
            profile_id=profile.id, search_profile_id=searches[0].id,
        )
        snapshot = snapshot_vacancy(
            job, source_id="hh", source_job_id="hh-posting-44",
        )
        kwargs = dict(
            user_id=user.id, job_id=job.id, source_job_id="hh-posting-44",
            resume_snapshot="Saved CV", message="Grounded letter",
            vacancy_snapshot=snapshot,
        )
        # Reviewed-but-unsent packages must not block the initial submission.
        draft = await repo.save_application(
            user_id=user.id, job_id=job.id, source_id="hh",
            status="prepared", vacancy_snapshot=snapshot,
        )
        assert await repo.set_application_status(user.id, draft.id, "reviewed")
        outcomes = await asyncio.gather(
            repo.reserve_hh_application(**kwargs),
            repo.reserve_hh_application(**kwargs),
            return_exceptions=True,
        )
        successes = [x for x in outcomes if isinstance(x, Application)]
        failures = [x for x in outcomes if isinstance(x, RuntimeError)]
        assert len(successes) == 1
        assert len(failures) == 1
        assert "заблокирован" in str(failures[0])
        reserved = successes[0]
        assert reserved.status == "sending"
        assert [e.status for e in await repo.application_status_history(user.id, reserved.id)] == ["sending"]

        # No second attempt after an ambiguous result or after a success.
        await repo.finish_hh_application(
            user_id=user.id, application_id=reserved.id,
            match_id=match.id, status="unknown",
        )
        with pytest.raises(RuntimeError, match="заблокирован"):
            await repo.reserve_hh_application(**kwargs)
        assert [e.status for e in await repo.application_status_history(user.id, reserved.id)] == [
            "sending", "unknown",
        ]

        # A fresh independent job can complete and update JobMatch atomically.
        second, _ = await repo.upsert_job(NormalizedJob(
            source="hh", source_job_id="hh-posting-45",
            title="Linux Administrator", company="Another employer",
            url="https://hh.ru/vacancy/hh-posting-45",
        ))
        other_match = await repo.save_match(
            job_id=second.id, user_id=user.id,
            profile_id=profile.id, search_profile_id=searches[0].id,
        )
        accepted = await repo.reserve_hh_application(
            user_id=user.id, job_id=second.id, source_job_id="hh-posting-45",
            vacancy_snapshot=snapshot_vacancy(
                second, source_id="hh", source_job_id="hh-posting-45",
            ),
            message="Supported draft",
        )
        await repo.finish_hh_application(
            user_id=user.id, application_id=accepted.id, match_id=other_match.id,
            status="sent", source_application_id="receipt-45",
        )
        latest = await repo.get_application(user.id, accepted.id)
        assert latest.status == "sent"
        assert latest.source_application_id == "receipt-45"
        assert (await repo.get_match(other_match.id)).status == "applied"
        assert [e.status for e in await repo.application_status_history(user.id, accepted.id)] == [
            "sending", "sent",
        ]
        with pytest.raises(RuntimeError, match="заблокирован"):
            await repo.reserve_hh_application(**kwargs)
        with pytest.raises(RuntimeError, match="заблокирован"):
            await repo.reserve_hh_application(
                user_id=user.id, job_id=second.id, source_job_id="hh-posting-45",
            )
    finally:
        await engine.dispose()

