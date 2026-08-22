from __future__ import annotations

from sqlalchemy import func, select

from app.database.db import SessionLocal
from app.database.models import (
    Application,
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


async def ensure_default_profile(user_id: int, *, profile_name: str = "Main", target_role: str = "DevOps Engineer") -> CandidateProfile:
    async with SessionLocal() as session:
        existing = await session.scalar(select(CandidateProfile).where(CandidateProfile.user_id == user_id, CandidateProfile.active.is_(True), CandidateProfile.deleted_at.is_(None)))
        if existing:
            return existing
        profile = CandidateProfile(user_id=user_id, name=profile_name, target_role=target_role, english_level="B2")
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


async def list_profiles(user_id: int) -> list[CandidateProfile]:
    async with SessionLocal() as session:
        rows = await session.scalars(select(CandidateProfile).where(CandidateProfile.user_id == user_id, CandidateProfile.deleted_at.is_(None)).order_by(CandidateProfile.id))
        return list(rows)


async def add_fact(profile_id: int, value: str, *, category: str = "experience", key: str = "", commercial: bool = False, evidence: str = "") -> CandidateFact:
    async with SessionLocal() as session:
        item = CandidateFact(profile_id=profile_id, category=category, key=key, value=value, commercial=commercial, evidence=evidence)
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


async def list_resumes(profile_id: int) -> list[ResumeProfile]:
    async with SessionLocal() as session:
        rows = await session.scalars(select(ResumeProfile).where(ResumeProfile.profile_id == profile_id, ResumeProfile.active.is_(True), ResumeProfile.deleted_at.is_(None)).order_by(ResumeProfile.id))
        return list(rows)


async def list_search_profiles(profile_id: int) -> list[SearchProfile]:
    async with SessionLocal() as session:
        rows = await session.scalars(select(SearchProfile).where(SearchProfile.profile_id == profile_id, SearchProfile.enabled.is_(True), SearchProfile.deleted_at.is_(None)))
        return list(rows)


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
        source_ref = await session.scalar(select(JobSourceRef).where(JobSourceRef.source_id == job.source, JobSourceRef.source_job_id == job.source_job_id))
        if source_ref:
            existing = await session.get(Job, source_ref.job_id)
            return existing, False

        fingerprint = job.canonical_fingerprint()
        existing = await session.scalar(select(Job).where(Job.fingerprint == fingerprint))
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
        session.add(JobSourceRef(job_id=existing.id, source_id=job.source, source_job_id=job.source_job_id, url=job.url, raw=job.raw))
        await session.commit()
        await session.refresh(existing)
        return existing, created


async def source_ref(job_id: int, source_id: str | None = None) -> JobSourceRef | None:
    async with SessionLocal() as session:
        stmt = select(JobSourceRef).where(JobSourceRef.job_id == job_id)
        if source_id:
            stmt = stmt.where(JobSourceRef.source_id == source_id)
        return await session.scalar(stmt.order_by(JobSourceRef.id))


async def save_match(**kwargs) -> JobMatch:
    async with SessionLocal() as session:
        existing = await session.scalar(select(JobMatch).where(JobMatch.job_id == kwargs["job_id"], JobMatch.profile_id == kwargs["profile_id"], JobMatch.search_profile_id == kwargs["search_profile_id"]))
        if existing:
            for key, value in kwargs.items():
                setattr(existing, key, value)
            item = existing
        else:
            item = JobMatch(**kwargs)
            session.add(item)
        await session.commit()
        await session.refresh(item)
        return item


def _display_key(title: str, company: str) -> tuple[str, str]:
    def norm(value: str) -> str:
        return " ".join((value or "").casefold().split())
    return norm(title), norm(company)


async def latest_matches(
    user_id: int,
    limit: int = 10,
    *,
    include_filtered: bool = False,
    min_score: int | None = None,
) -> list[tuple[JobMatch, Job]]:
    """Latest useful matches, suppressing stale low-score rows and reposts in UI."""
    async with SessionLocal() as session:
        stmt = (
            select(JobMatch, Job)
            .join(Job, Job.id == JobMatch.job_id)
            .where(JobMatch.user_id == user_id)
            .order_by(JobMatch.created_at.desc())
            .limit(max(limit * 8, 40))
        )
        if not include_filtered:
            stmt = stmt.where(JobMatch.status.notin_(["filtered", "duplicate"]))
        if min_score is not None:
            stmt = stmt.where(JobMatch.total_score >= int(min_score))
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
                JobMatch.status.in_(["notified", "prepared", "applied"]),
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
        await session.commit()
        await session.refresh(item)
        return item


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


async def get_resume(resume_id: int) -> ResumeProfile | None:
    async with SessionLocal() as session:
        return await session.get(ResumeProfile, resume_id)


async def set_fact_commercial(profile_id: int, fact_id: int, commercial: bool) -> bool:
    async with SessionLocal() as session:
        item = await session.get(CandidateFact, fact_id)
        if not item or item.profile_id != profile_id:
            return False
        item.commercial = commercial
        await session.commit()
        return True


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
