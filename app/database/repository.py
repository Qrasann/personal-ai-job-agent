from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import and_, func, or_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.database.db import SessionLocal
from app.database.models import (
    Application,
    ApplicationStatusEvent,
    CandidateFact,
    CandidateProfile,
    Job,
    JobMatch,
    JobSourceRef,
    ResumeProfile,
    RuntimeState,
    SearchProfile,
    SeenMessage,
    User,
)
from app.domain.jobs import NormalizedJob
from app.domain.relocation_evidence import build_relocation_evidence
from app.domain.source_posting import posting_snapshot_digest, snapshot_source_posting
from app.candidates.fact_types import normalize_experience_type

REPOST_SUPPRESS_STATUSES = frozenset({"notified", "prepared", "applied", "saved", "skipped"})
PREPARED_MATCH_SNAPSHOT_KEY = "_prepared_match_id"
MANUAL_APPLICATION_STATUSES = frozenset({
    "reviewed", "submitted", "interview", "offer", "rejected", "withdrawn",
})


class FactUpdateConflict(ValueError):
    """An import UPDATE no longer matches the reviewed active fact."""


async def get_user_by_chat(chat_id: int | str) -> User | None:
    async with SessionLocal() as session:
        return await session.scalar(select(User).where(User.telegram_chat_id == str(chat_id), User.deleted_at.is_(None)))


async def create_user(chat_id: int | str, display_name: str = "") -> User:
    async with SessionLocal() as session:
        item = User(telegram_chat_id=str(chat_id), display_name=display_name)
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return item


async def ensure_default_profile(
    user_id: int,
    *,
    profile_name: str = "Main",
    target_role: str = "DevOps Engineer",
    english_level: str = "",
) -> CandidateProfile:
    async with SessionLocal() as session:
        existing = await session.scalar(select(CandidateProfile).where(CandidateProfile.user_id == user_id, CandidateProfile.active.is_(True), CandidateProfile.deleted_at.is_(None)))
        if existing:
            return existing
        profile = CandidateProfile(
            user_id=user_id,
            name=profile_name,
            target_role=target_role,
            english_level=english_level,
        )
        session.add(profile)
        await session.flush()
        search = SearchProfile(profile_id=profile.id, name="Employment", kind="employment", settings={})
        session.add(search)
        await session.commit()
        await session.refresh(profile)
        return profile


async def active_profile(user_id: int) -> CandidateProfile | None:
    async with SessionLocal() as session:
        return await session.scalar(select(CandidateProfile).where(CandidateProfile.user_id == user_id, CandidateProfile.active.is_(True), CandidateProfile.deleted_at.is_(None)).order_by(CandidateProfile.id))


async def get_profile(profile_id: int) -> CandidateProfile | None:
    async with SessionLocal() as session:
        return await session.scalar(
            select(CandidateProfile).where(
                CandidateProfile.id == profile_id,
                CandidateProfile.deleted_at.is_(None),
            )
        )


async def list_profiles(user_id: int) -> list[CandidateProfile]:
    async with SessionLocal() as session:
        rows = await session.scalars(select(CandidateProfile).where(CandidateProfile.user_id == user_id, CandidateProfile.deleted_at.is_(None)).order_by(CandidateProfile.id))
        return list(rows)


async def add_fact(
    profile_id: int,
    value: str,
    *,
    category: str = "experience",
    key: str = "",
    commercial: bool = False,
    experience_type: str = "unknown",
    evidence: str = "",
    confidence: float = 1.0,
    provenance: str = "manual",
) -> CandidateFact:
    normalized_type = normalize_experience_type(experience_type) or "unknown"
    if commercial:
        normalized_type = "commercial"
    async with SessionLocal() as session:
        item = CandidateFact(
            profile_id=profile_id,
            category=category,
            key=key,
            value=value,
            experience_type=normalized_type,
            confidence=max(0.0, min(1.0, float(confidence))),
            provenance=str(provenance)[:64],
            commercial=normalized_type == "commercial",
            evidence=evidence,
        )
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return item


async def list_facts(profile_id: int) -> list[CandidateFact]:
    async with SessionLocal() as session:
        rows = await session.scalars(select(CandidateFact).where(CandidateFact.profile_id == profile_id, CandidateFact.active.is_(True), CandidateFact.deleted_at.is_(None)).order_by(CandidateFact.id))
        return list(rows)


async def add_resume(profile_id: int, name: str, language: str, role: str, content: str = "", source: str = "generated", external_id: str | None = None) -> ResumeProfile:
    async with SessionLocal() as session:
        item = ResumeProfile(profile_id=profile_id, name=name, language=language, role=role, content=content, source=source, external_id=external_id)
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return item


async def add_imported_resume_with_facts(
    profile_id: int,
    name: str,
    language: str,
    role: str,
    content: str,
    external_id: str,
    facts: list[dict],
    *,
    replacements: list[dict] | None = None,
) -> ResumeProfile:
    """Persist the resume, additions and reviewed replacements atomically."""
    replacements = replacements or []
    replacement_ids = [item["existing_id"] for item in replacements]
    if len(replacement_ids) != len(set(replacement_ids)):
        raise FactUpdateConflict("Для одного факта выбери только один UPDATE.")
    async with SessionLocal() as session:
        for replacement in sorted(replacements, key=lambda item: item["existing_id"]):
            existing = await session.scalar(
                select(CandidateFact).where(
                    CandidateFact.id == replacement["existing_id"],
                    CandidateFact.profile_id == profile_id,
                    CandidateFact.active.is_(True), CandidateFact.deleted_at.is_(None),
                ).with_for_update()
            )
            if existing is None or existing.value != replacement["expected_value"]:
                raise FactUpdateConflict("Факт изменился после предпросмотра. Выбери KEEP или загрузи резюме заново.")
            # Retain the old value and its evidence; imported replacement claims
            # are new unknown facts, never inherited commercial experience.
            existing.active = False
        resume = ResumeProfile(
            profile_id=profile_id, name=name, language=language, role=role,
            content=content, source="imported", external_id=external_id,
        )
        session.add(resume)
        await session.flush()
        for fact in [*facts, *replacements]:
            evidence = f"resume_import section={fact['section']}; confidence={fact['confidence']:.2f}"
            if "existing_id" in fact:
                evidence += f"; replaces_fact_id={fact['existing_id']}"
            session.add(CandidateFact(
                profile_id=profile_id,
                category=fact["category"],
                key=fact["category"],
                value=fact["value"],
                experience_type="unknown",
                commercial=False,
                confidence=max(0.0, min(1.0, float(fact["confidence"]))),
                provenance="resume_import",
                evidence=evidence,
            ))
        await session.commit()
        await session.refresh(resume)
        return resume


async def list_resumes(profile_id: int) -> list[ResumeProfile]:
    async with SessionLocal() as session:
        rows = await session.scalars(select(ResumeProfile).where(ResumeProfile.profile_id == profile_id, ResumeProfile.active.is_(True), ResumeProfile.deleted_at.is_(None)).order_by(ResumeProfile.id))
        return list(rows)


async def list_search_profiles(profile_id: int) -> list[SearchProfile]:
    async with SessionLocal() as session:
        rows = await session.scalars(select(SearchProfile).where(SearchProfile.profile_id == profile_id, SearchProfile.enabled.is_(True), SearchProfile.deleted_at.is_(None)).order_by(SearchProfile.id))
        return list(rows)


async def configure_parallel_search_profiles(profile_id: int, *, enabled: bool) -> list[SearchProfile]:
    """Idempotently configure independent career and relocation tracks."""
    async with SessionLocal() as session:
        rows = list(await session.scalars(
            select(SearchProfile)
            .where(SearchProfile.profile_id == profile_id, SearchProfile.deleted_at.is_(None))
            .order_by(SearchProfile.id)
        ))
        if not rows:
            return []

        career = next((item for item in rows if item.kind == "career"), rows[0])
        career_settings = dict(career.settings or {})
        career_settings["search_strategy"] = "career_first"
        career.settings = career_settings
        career.kind = "career"
        career.name = "Career-first"
        career.enabled = True

        relocation = next((item for item in rows if item.kind == "relocation"), None)
        if relocation is None:
            relocation_settings = dict(career_settings)
            relocation_settings["search_strategy"] = "relocation_first"
            relocation = SearchProfile(
                profile_id=profile_id,
                name="Relocation-first",
                kind="relocation",
                enabled=enabled,
                settings=relocation_settings,
            )
            session.add(relocation)
        else:
            relocation_settings = dict(relocation.settings or {})
            relocation_settings["search_strategy"] = "relocation_first"
            relocation.settings = relocation_settings
            relocation.name = "Relocation-first"
            relocation.enabled = enabled

        await session.commit()
        return [career, relocation]


async def update_search_settings(search_profile_id: int, settings: dict) -> None:
    async with SessionLocal() as session:
        item = await session.get(SearchProfile, search_profile_id)
        if item:
            item.settings = settings
            await session.commit()


async def set_user_country(user_id: int, code: str | None) -> None:
    async with SessionLocal() as session:
        item = await session.get(User, user_id)
        if item:
            item.current_country = code
            await session.commit()


async def upsert_job(job: NormalizedJob) -> tuple[Job, bool]:
    async with SessionLocal() as session:
        incoming_raw = dict(job.raw or {})
        incoming_raw["normalized_posting_v1"] = snapshot_source_posting(job)
        incoming_raw["relocation_evidence_v1"] = build_relocation_evidence(
            job, captured_at=datetime.now(timezone.utc)
        )
        fingerprint = job.canonical_fingerprint()
        # Serialize the two natural-key decisions (provider identity and
        # cross-provider fingerprint) before reading either row. Sorting keeps
        # lock acquisition order stable when both keys overlap across workers.
        lock_keys = sorted((
            f"source:{job.source}:{job.source_job_id}",
            f"fingerprint:{fingerprint}",
        ))
        for lock_key in lock_keys:
            await session.execute(
                select(func.pg_advisory_xact_lock(func.hashtextextended(lock_key, 0)))
            )

        source_ref = await session.scalar(
            select(JobSourceRef)
            .where(JobSourceRef.source_id == job.source, JobSourceRef.source_job_id == job.source_job_id)
            .with_for_update()
        )
        if source_ref:
            existing = await session.scalar(
                select(Job).where(Job.id == source_ref.job_id).with_for_update()
            )
            if existing:
                _refresh_job_from_source(existing, job)
                # A fully specified new identity can improve later cross-source
                # deduplication. Keep the old fingerprint when the normalized
                # identity is incomplete or already belongs to another Job;
                # reassignment/merging would require reconciling its matches.
                if _has_complete_identity(job):
                    collision = await session.scalar(
                        select(Job)
                        .where(Job.fingerprint == fingerprint, Job.id != existing.id)
                    )
                    if not collision:
                        existing.fingerprint = fingerprint
                old_raw = dict(source_ref.raw or {})
                cached_details = old_raw.get("details_cache_v1")
                if isinstance(cached_details, dict):
                    incoming_raw["details_cache_v1"] = cached_details
                cache_digest = old_raw.get("details_cache_posting_digest_v1")
                if isinstance(cache_digest, str):
                    incoming_raw["details_cache_posting_digest_v1"] = cache_digest
                source_ref.raw = incoming_raw
                if job.url:
                    source_ref.url = str(job.url)[:100000]
                await session.commit()
                await session.refresh(existing)
                return existing, False

        existing = await session.scalar(
            select(Job).where(Job.fingerprint == fingerprint).with_for_update()
        )
        created = False
        if not existing:
            existing = Job(
                fingerprint=fingerprint,
                title=job.title,
                company=job.company,
                description=job.description[:100000],
                country=job.country,
                city=job.city,
                work_mode=job.work_mode,
                remote_scope=job.remote_scope,
                relocation=job.relocation,
                visa_sponsorship=job.visa_sponsorship,
                salary_from=job.salary_from,
                salary_to=job.salary_to,
                salary_currency=job.salary_currency,
                salary_period=job.salary_period,
                published_at=job.published_at,
            )
            session.add(existing)
            await session.flush()
            created = True
        session.add(JobSourceRef(job_id=existing.id, source_id=job.source, source_job_id=job.source_job_id, url=job.url, raw=incoming_raw))
        await session.commit()
        await session.refresh(existing)
        return existing, created


def _refresh_job_from_source(existing: Job, incoming: NormalizedJob) -> None:
    """Apply known nonempty source fields without erasing other-source evidence."""
    string_limits = {
        "title": 512, "company": 512, "description": 100000,
        "country": 128, "city": 256, "work_mode": 64,
        "remote_scope": 128, "salary_currency": 16,
        "salary_period": 32, "published_at": 64,
    }
    for field, limit in string_limits.items():
        value = getattr(incoming, field)
        if value is not None and str(value).strip():
            setattr(existing, field, str(value)[:limit])
    for field in ("relocation", "visa_sponsorship", "salary_from", "salary_to"):
        value = getattr(incoming, field)
        if value is not None:
            setattr(existing, field, value)


def _has_complete_identity(job: NormalizedJob) -> bool:
    return bool(
        job.title.strip()
        and (job.company.strip() or job.description.strip())
        and job.country is not None
        and job.city is not None
    )


async def source_ref(
    job_id: int, source_id: str | None = None, *, source_job_id: str | None = None
) -> JobSourceRef | None:
    async with SessionLocal() as session:
        stmt = select(JobSourceRef).where(JobSourceRef.job_id == job_id)
        if source_id:
            stmt = stmt.where(JobSourceRef.source_id == source_id)
        if source_job_id is not None:
            stmt = stmt.where(JobSourceRef.source_job_id == source_job_id)
        return await session.scalar(stmt.order_by(JobSourceRef.id))


async def update_source_ref_raw(ref_id: int, raw: dict) -> None:
    async with SessionLocal() as session:
        item = await session.get(JobSourceRef, ref_id)
        if not item:
            return
        item.raw = dict(raw or {})
        await session.commit()


async def save_source_ref_detail_cache(
    ref_id: int, details: dict, *, expected_posting_digest: str | None = None
) -> bool:
    """Save verified details only for the expected posting; signal rejected writes."""
    async with SessionLocal() as session:
        item = await session.scalar(
            select(JobSourceRef).where(JobSourceRef.id == ref_id).with_for_update()
        )
        if not item:
            return False
        raw = dict(item.raw or {})
        current_digest = posting_snapshot_digest(raw.get("normalized_posting_v1"))
        if expected_posting_digest is not None and expected_posting_digest != current_digest:
            # A card refresh raced the network fetch. Do not label fetched
            # details as verified against a snapshot we did not request.
            return False
        raw["details_cache_v1"] = dict(details or {})
        if current_digest:
            raw["details_cache_posting_digest_v1"] = current_digest
        else:
            raw.pop("details_cache_posting_digest_v1", None)
        item.raw = raw
        await session.commit()
        return True


async def save_match(**kwargs) -> JobMatch:
    async with SessionLocal() as session:
        statement = pg_insert(JobMatch).values(**kwargs)
        update_values = {
            key: getattr(statement.excluded, key)
            for key in kwargs
            if key not in {"id", "job_id", "profile_id", "search_profile_id"}
        }
        statement = statement.on_conflict_do_update(
            constraint="uq_job_profile_search",
            set_=update_values,
        ).returning(JobMatch.id)
        item_id = await session.scalar(statement)
        await session.commit()
        item = await session.get(JobMatch, item_id)
        return item


def _display_key(title: str, company: str) -> tuple[str, str]:
    def norm(value: str) -> str:
        return " ".join((value or "").casefold().split())
    return norm(title), norm(company)


def _select_review_matches(rows, limit: int | None = 10):
    out = []
    seen = set()
    for match, job in rows:
        if match.status != "notified":
            continue
        key = _display_key(job.title, job.company)
        if key in seen:
            continue
        seen.add(key)
        out.append((match, job))
        if limit is not None and len(out) >= limit:
            break
    return out


def _select_stretch_matches(rows, limit: int | None = 10):
    out = []
    seen = set()
    for match, job in rows:
        if match.status != "stretch":
            continue
        key = _display_key(job.title, job.company)
        if key in seen:
            continue
        seen.add(key)
        out.append((match, job))
        if limit is not None and len(out) >= limit:
            break
    return out

def _select_saved_matches(rows, limit: int | None = 10):
    out = []
    seen = set()
    for match, job in rows:
        if match.status != "saved":
            continue
        key = _display_key(job.title, job.company)
        if key in seen:
            continue
        seen.add(key)
        out.append((match, job))
        if limit is not None and len(out) >= limit:
            break
    return out

async def review_matches(user_id: int, limit: int | None = 10) -> list[tuple[JobMatch, Job]]:
    if limit is not None and limit <= 0:
        return []
    async with SessionLocal() as session:
        stmt = (
            select(JobMatch, Job)
            .join(Job, Job.id == JobMatch.job_id)
            .where(JobMatch.user_id == user_id, JobMatch.status == "notified")
            .order_by(JobMatch.total_score.desc(), JobMatch.created_at.desc())
        )
        if limit is not None:
            stmt = stmt.limit(max(limit * 8, 40))
        rows = list((await session.execute(stmt)).all())
    return _select_review_matches(rows, limit=limit)


async def stretch_matches(user_id: int, limit: int | None = 10) -> list[tuple[JobMatch, Job]]:
    if limit is not None and limit <= 0:
        return []
    async with SessionLocal() as session:
        stmt = (
            select(JobMatch, Job)
            .join(Job, Job.id == JobMatch.job_id)
            .where(JobMatch.user_id == user_id, JobMatch.status == "stretch")
            .order_by(JobMatch.total_score.desc(), JobMatch.created_at.desc())
        )
        if limit is not None:
            stmt = stmt.limit(max(limit * 8, 40))
        rows = list((await session.execute(stmt)).all())
    return _select_stretch_matches(rows, limit=limit)


async def saved_matches(user_id: int, limit: int | None = 10) -> list[tuple[JobMatch, Job]]:
    if limit is not None and limit <= 0:
        return []
    async with SessionLocal() as session:
        stmt = (
            select(JobMatch, Job)
            .join(Job, Job.id == JobMatch.job_id)
            .where(JobMatch.user_id == user_id, JobMatch.status == "saved")
            .order_by(JobMatch.total_score.desc(), JobMatch.created_at.desc())
        )
        if limit is not None:
            stmt = stmt.limit(max(limit * 8, 40))
        rows = list((await session.execute(stmt)).all())
    return _select_saved_matches(rows, limit=limit)


async def latest_matches(
    user_id: int,
    limit: int = 10,
    *,
    include_filtered: bool = False,
    min_score: int | None = None,
    max_score: int | None = None,
    search_profile_id: int | None = None,
) -> list[tuple[JobMatch, Job]]:
    """Highest-scoring useful matches, with recent matches first on score ties."""
    async with SessionLocal() as session:
        stmt = (
            select(JobMatch, Job)
            .join(Job, Job.id == JobMatch.job_id)
            .where(JobMatch.user_id == user_id)
            .order_by(JobMatch.total_score.desc(), JobMatch.created_at.desc())
            .limit(max(limit * 8, 40))
        )
        if include_filtered:
            stmt = stmt.where(JobMatch.status != "duplicate")
        else:
            stmt = stmt.where(JobMatch.status.notin_(["filtered", "duplicate"]))
        if min_score is not None:
            stmt = stmt.where(JobMatch.total_score >= int(min_score))
        if max_score is not None:
            stmt = stmt.where(JobMatch.total_score <= int(max_score))
        if search_profile_id is not None:
            stmt = stmt.where(JobMatch.search_profile_id == search_profile_id)
        rows = list((await session.execute(stmt)).all())

    out: list[tuple[JobMatch, Job]] = []
    seen: set[tuple[str, str]] = set()
    for match, job in rows:
        key = _display_key(job.title, job.company)
        if key in seen:
            continue
        seen.add(key)
        out.append((match, job))
        if len(out) >= limit:
            break
    return out


async def has_notified_equivalent(user_id: int, job_id: int, title: str, company: str) -> bool:
    """Avoid notifying the same title/company reposted under another source job id."""
    title_key, company_key = _display_key(title, company)
    if not title_key:
        return False
    async with SessionLocal() as session:
        rows = await session.execute(
            select(JobMatch.status, Job.title, Job.company)
            .join(Job, Job.id == JobMatch.job_id)
            .where(
                JobMatch.user_id == user_id,
                Job.id != job_id,
                JobMatch.status.in_(REPOST_SUPPRESS_STATUSES),
            )
            .order_by(JobMatch.created_at.desc())
            .limit(200)
        )
        for status, other_title, other_company in rows.all():
            if _display_key(other_title, other_company) == (title_key, company_key):
                return True
    return False


async def set_match_status(match_id: int, status: str) -> None:
    async with SessionLocal() as session:
        item = await session.get(JobMatch, match_id)
        if item:
            item.status = status
            await session.commit()


async def save_application(**kwargs) -> Application:
    async with SessionLocal() as session:
        item = Application(**kwargs)
        session.add(item)
        await session.flush()
        session.add(ApplicationStatusEvent(
            application_id=item.id,
            user_id=item.user_id,
            status=item.status,
        ))
        await session.commit()
        await session.refresh(item)
        return item


async def prepared_application_for_match(match_id: int, user_id: int) -> Application | None:
    """Return the durable draft created for this exact user match, if any."""
    async with SessionLocal() as session:
        return await session.scalar(
            select(Application).where(
                Application.user_id == user_id,
                Application.status == "prepared",
                Application.vacancy_snapshot[PREPARED_MATCH_SNAPSHOT_KEY].astext == str(match_id),
            ).order_by(Application.created_at.desc(), Application.id.desc()).limit(1)
        )


async def save_prepared_application(
    match_id: int, user_id: int, **kwargs,
) -> tuple[Application, bool]:
    """Atomically save one reviewable draft per match; return (item, created)."""
    async with SessionLocal() as session:
        match = await session.scalar(
            select(JobMatch).where(
                JobMatch.id == match_id, JobMatch.user_id == user_id,
            ).with_for_update()
        )
        if match is None or match.job_id != kwargs.get("job_id"):
            raise ValueError("Match не найден для этого пользователя и вакансии")
        existing = await session.scalar(
            select(Application).where(
                Application.user_id == user_id,
                Application.status == "prepared",
                Application.vacancy_snapshot[PREPARED_MATCH_SNAPSHOT_KEY].astext == str(match_id),
            ).order_by(Application.created_at.desc(), Application.id.desc()).limit(1)
        )
        if existing is not None:
            if match.status != "prepared":
                match.status = "prepared"
                await session.commit()
            return existing, False
        snapshot = dict(kwargs.pop("vacancy_snapshot", {}) or {})
        snapshot[PREPARED_MATCH_SNAPSHOT_KEY] = match_id
        kwargs["vacancy_snapshot"] = snapshot
        item = Application(user_id=user_id, status="prepared", **kwargs)
        session.add(item)
        await session.flush()
        session.add(ApplicationStatusEvent(
            application_id=item.id, user_id=user_id, status="prepared",
        ))
        match.status = "prepared"
        await session.commit()
        await session.refresh(item)
        return item, True




async def reserve_hh_application(
    *, user_id: int, job_id: int, source_job_id: str, **snapshot_kwargs
) -> Application:
    """Record a non-retryable attempt before any external HH side effect.

    Serialize all HH claims for an owner through the user row lock. Check both
    canonical job id and provider posting id across independent search profiles
    and changed fingerprints. Existing prepared drafts are not submissions.
    """
    async with SessionLocal() as session:
        owner = await session.scalar(
            select(User).where(
                User.id == user_id, User.is_active.is_(True), User.deleted_at.is_(None)
            ).with_for_update()
        )
        if not owner:
            raise RuntimeError("HH owner не найден или отключён")
        # A user may have prepared and explicitly reviewed an unsent draft.
        # Permit that workflow only when the history proves it began as a draft
        # and contains no attempted/submitted outcome.
        had_draft = select(ApplicationStatusEvent.id).where(
            ApplicationStatusEvent.application_id == Application.id,
            ApplicationStatusEvent.status == "prepared",
        ).exists()
        had_outbound_status = select(ApplicationStatusEvent.id).where(
            ApplicationStatusEvent.application_id == Application.id,
            ApplicationStatusEvent.status.notin_(("prepared", "reviewed")),
        ).exists()
        safe_reviewed_draft = and_(
            Application.status == "reviewed", had_draft, ~had_outbound_status,
        )
        duplicate = await session.scalar(
            select(Application).where(
                Application.user_id == user_id,
                Application.source_id == "hh",
                ~or_(Application.status == "prepared", safe_reviewed_draft),
                or_(
                    Application.job_id == job_id,
                    Application.vacancy_snapshot["source_job_id"].astext == source_job_id,
                ),
            ).order_by(Application.created_at.desc(), Application.id.desc()).limit(1)
        )
        if duplicate:
            raise RuntimeError(
                f"Повторный HH-отклик заблокирован: запись #{duplicate.id}, "
                f"статус {duplicate.status}. Проверь /applications и кабинет HH; "
                "не отправляй повторно без ручной сверки."
            )
        item = Application(
            user_id=user_id, job_id=job_id, source_id="hh",
            status="sending", **snapshot_kwargs,
        )
        session.add(item)
        await session.flush()
        session.add(ApplicationStatusEvent(
            application_id=item.id, user_id=user_id, status="sending",
        ))
        await session.commit()
        await session.refresh(item)
        return item


async def finish_hh_application(
    *, user_id: int, application_id: int, match_id: int,
    status: str, source_application_id: str | None = None,
    external_url: str | None = None,
) -> None:
    """Record the provider outcome, history and confirmed match in one transaction.

    Unknown results remain in a blocking state. Never assume a failed response
    means HH did not receive the application.
    """
    status = status if status in {"sent", "external"} else "unknown"
    async with SessionLocal() as session:
        item = await session.scalar(
            select(Application).where(
                Application.id == application_id,
                Application.user_id == user_id,
                Application.source_id == "hh",
            ).with_for_update()
        )
        if not item or item.status != "sending":
            raise RuntimeError("HH-попытка отсутствует или уже обработана")
        if status == "sent":
            match = await session.scalar(
                select(JobMatch).where(
                    JobMatch.id == match_id,
                    JobMatch.user_id == user_id,
                    JobMatch.job_id == item.job_id,
                ).with_for_update()
            )
            if not match:
                raise RuntimeError("Исходный HH match отсутствует; проверь кабинет HH")
            match.status = "applied"
        item.status = status
        item.source_application_id = source_application_id if status == "sent" else None
        item.external_url = external_url
        session.add(ApplicationStatusEvent(
            application_id=item.id, user_id=user_id, status=status,
        ))
        await session.commit()


async def list_applications(user_id: int, limit: int = 20) -> list[Application]:
    async with SessionLocal() as session:
        rows = await session.scalars(
            select(Application)
            .where(Application.user_id == user_id)
            .order_by(Application.created_at.desc(), Application.id.desc())
            .limit(max(1, min(int(limit), 100)))
        )
        return list(rows)


async def get_application(user_id: int, application_id: int) -> Application | None:
    async with SessionLocal() as session:
        return await session.scalar(
            select(Application).where(
                Application.user_id == user_id,
                Application.id == application_id,
            )
        )


async def set_application_status(user_id: int, application_id: int, status: str) -> bool:
    if status not in MANUAL_APPLICATION_STATUSES:
        return False
    async with SessionLocal() as session:
        # Serialize the status check and event append for this application.
        item = await session.scalar(
            select(Application).where(
                Application.id == application_id,
                Application.user_id == user_id,
            ).with_for_update()
        )
        if not item:
            return False
        if item.status == status:
            return True
        item.status = status
        session.add(ApplicationStatusEvent(
            application_id=item.id,
            user_id=item.user_id,
            status=status,
        ))
        await session.commit()
        return True


async def application_status_history(user_id: int, application_id: int) -> list[ApplicationStatusEvent] | None:
    async with SessionLocal() as session:
        application = await session.scalar(
            select(Application.id).where(
                Application.id == application_id,
                Application.user_id == user_id,
            )
        )
        if application is None:
            return None
        rows = await session.scalars(
            select(ApplicationStatusEvent)
            .where(
                ApplicationStatusEvent.application_id == application_id,
                ApplicationStatusEvent.user_id == user_id,
            )
            .order_by(ApplicationStatusEvent.id)
        )
        return list(rows)


async def message_seen(user_id: int, message_id: str, source: str) -> bool:
    async with SessionLocal() as session:
        row = await session.scalar(select(SeenMessage).where(SeenMessage.user_id == user_id, SeenMessage.source == source, SeenMessage.message_id == message_id))
        return row is not None


async def mark_message_seen(user_id: int, message_id: str, conversation_id: str, text: str, source: str) -> None:
    async with SessionLocal() as session:
        session.add(SeenMessage(user_id=user_id, source=source, message_id=message_id, conversation_id=conversation_id, text=text))
        await session.commit()


async def set_state(user_id: int, key: str, value: str) -> None:
    async with SessionLocal() as session:
        item = await session.scalar(select(RuntimeState).where(RuntimeState.user_id == user_id, RuntimeState.key == key))
        if item:
            item.value = value
        else:
            session.add(RuntimeState(user_id=user_id, key=key, value=value))
        await session.commit()


async def get_state(user_id: int, key: str, default: str = "") -> str:
    async with SessionLocal() as session:
        item = await session.scalar(select(RuntimeState).where(RuntimeState.user_id == user_id, RuntimeState.key == key))
        return item.value if item else default


async def stats(user_id: int) -> dict:
    async with SessionLocal() as session:
        matches = await session.scalar(select(func.count()).select_from(JobMatch).where(JobMatch.user_id == user_id)) or 0
        notified = await session.scalar(
            select(func.count()).select_from(JobMatch).where(
                JobMatch.user_id == user_id,
                JobMatch.status.in_(["notified", "prepared", "applied"]),
            )
        ) or 0
        filtered = await session.scalar(
            select(func.count()).select_from(JobMatch).where(
                JobMatch.user_id == user_id,
                JobMatch.status.in_(["filtered", "duplicate"]),
            )
        ) or 0
        apps = await session.scalar(select(func.count()).select_from(Application).where(Application.user_id == user_id)) or 0
        return {"matches": matches, "notified": notified, "filtered": filtered, "applications": apps}


async def list_active_users() -> list[User]:
    async with SessionLocal() as session:
        rows = await session.scalars(select(User).where(User.is_active.is_(True), User.deleted_at.is_(None)).order_by(User.id))
        return list(rows)


async def get_job(job_id: int) -> Job | None:
    async with SessionLocal() as session:
        return await session.get(Job, job_id)


async def get_match(match_id: int) -> JobMatch | None:
    async with SessionLocal() as session:
        return await session.get(JobMatch, match_id)


async def get_match_for_user_job(
    user_id: int, job_id: int, *, search_profile_id: int | None = None
) -> JobMatch | None:
    async with SessionLocal() as session:
        stmt = (
            select(JobMatch)
            .where(JobMatch.user_id == user_id, JobMatch.job_id == job_id)
            .order_by(JobMatch.created_at.desc())
        )
        if search_profile_id is not None:
            stmt = stmt.where(JobMatch.search_profile_id == search_profile_id)
        return await session.scalar(stmt)


async def get_resume(resume_id: int) -> ResumeProfile | None:
    async with SessionLocal() as session:
        return await session.get(ResumeProfile, resume_id)


async def set_fact_experience_type(profile_id: int, fact_id: int, experience_type: str) -> bool:
    normalized_type = normalize_experience_type(experience_type)
    if not normalized_type:
        return False
    async with SessionLocal() as session:
        item = await session.get(CandidateFact, fact_id)
        if not item or item.profile_id != profile_id or item.deleted_at is not None:
            return False
        item.experience_type = normalized_type
        # Keep the legacy boolean in sync until all downstream consumers use experience_type.
        item.commercial = normalized_type == "commercial"
        await session.commit()
        return True


async def set_fact_commercial(profile_id: int, fact_id: int, commercial: bool) -> bool:
    # Backward-compatible command/API used by v3.3.x. Non-commercial is intentionally
    # mapped to unknown because the old boolean cannot distinguish lab from learning.
    return await set_fact_experience_type(
        profile_id,
        fact_id,
        "commercial" if commercial else "unknown",
    )


async def bind_resume_external(profile_id: int, resume_id: int, source: str, external_id: str) -> bool:
    async with SessionLocal() as session:
        item = await session.get(ResumeProfile, resume_id)
        if not item or item.profile_id != profile_id:
            return False
        item.source = source
        item.external_id = external_id
        await session.commit()
        return True


async def set_profile_target_role(profile_id: int, role: str) -> None:
    async with SessionLocal() as session:
        item = await session.get(CandidateProfile, profile_id)
        if item:
            item.target_role = role
            await session.commit()


async def set_profile_english_level(profile_id: int, level: str) -> None:
    async with SessionLocal() as session:
        item = await session.get(CandidateProfile, profile_id)
        if item and item.deleted_at is None:
            item.english_level = level
            await session.commit()
