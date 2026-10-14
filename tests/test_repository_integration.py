import asyncio
import os

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.exc import DBAPIError

from app.database import repository as repo
from app.database.models import Base, CandidateFact
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
            status="notified",
        )

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
