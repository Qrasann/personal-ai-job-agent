from __future__ import annotations

from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class SchemaMigration(Base):
    __tablename__ = "schema_migrations"

    version: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    applied_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_chat_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(256), default="")
    locale: Mapped[str] = mapped_column(String(16), default="ru")
    current_country: Mapped[str | None] = mapped_column(String(8), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    profiles: Mapped[list[CandidateProfile]] = relationship(back_populates="user", cascade="all, delete-orphan")


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(256), default="Main")
    target_role: Mapped[str] = mapped_column(String(256), default="")
    english_level: Mapped[str] = mapped_column(String(32), default="")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped[User] = relationship(back_populates="profiles")
    facts: Mapped[list[CandidateFact]] = relationship(back_populates="profile", cascade="all, delete-orphan")
    resumes: Mapped[list[ResumeProfile]] = relationship(back_populates="profile", cascade="all, delete-orphan")
    search_profiles: Mapped[list[SearchProfile]] = relationship(back_populates="profile", cascade="all, delete-orphan")


class CandidateFact(Base):
    __tablename__ = "candidate_facts"

    id: Mapped[int] = mapped_column(primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("candidate_profiles.id", ondelete="CASCADE"), index=True)
    category: Mapped[str] = mapped_column(String(64), default="experience")
    key: Mapped[str] = mapped_column(String(128), default="")
    value: Mapped[str] = mapped_column(Text)
    level: Mapped[str] = mapped_column(String(32), default="known")
    experience_type: Mapped[str] = mapped_column(String(32), default="unknown")
    commercial: Mapped[bool] = mapped_column(Boolean, default=False)
    evidence: Mapped[str] = mapped_column(Text, default="")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    profile: Mapped[CandidateProfile] = relationship(back_populates="facts")


class ResumeProfile(Base):
    __tablename__ = "resume_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("candidate_profiles.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(128))
    language: Mapped[str] = mapped_column(String(16), default="en")
    role: Mapped[str] = mapped_column(String(256), default="")
    source: Mapped[str] = mapped_column(String(32), default="generated")
    external_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    content: Mapped[str] = mapped_column(Text, default="")
    rules: Mapped[dict] = mapped_column(JSON, default=dict)
    storage_path: Mapped[str] = mapped_column(Text, default="")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    profile: Mapped[CandidateProfile] = relationship(back_populates="resumes")


class SearchProfile(Base):
    __tablename__ = "search_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("candidate_profiles.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(128), default="Employment")
    kind: Mapped[str] = mapped_column(String(32), default="employment")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    profile: Mapped[CandidateProfile] = relationship(back_populates="search_profiles")


class SourceAccount(Base):
    __tablename__ = "source_accounts"
    __table_args__ = (UniqueConstraint("user_id", "source_id", name="uq_user_source_account"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    source_id: Mapped[str] = mapped_column(String(64))
    credential_ref: Mapped[str] = mapped_column(String(512), default="")
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    fingerprint: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(512))
    company: Mapped[str] = mapped_column(String(512), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    country: Mapped[str | None] = mapped_column(String(128), nullable=True)
    city: Mapped[str | None] = mapped_column(String(256), nullable=True)
    work_mode: Mapped[str | None] = mapped_column(String(64), nullable=True)
    remote_scope: Mapped[str | None] = mapped_column(String(128), nullable=True)
    relocation: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    visa_sponsorship: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    salary_from: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_to: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str | None] = mapped_column(String(16), nullable=True)
    salary_period: Mapped[str | None] = mapped_column(String(32), nullable=True)
    published_at: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class JobSourceRef(Base):
    __tablename__ = "job_source_refs"
    __table_args__ = (UniqueConstraint("source_id", "source_job_id", name="uq_source_job"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    source_id: Mapped[str] = mapped_column(String(64), index=True)
    source_job_id: Mapped[str] = mapped_column(String(256))
    url: Mapped[str] = mapped_column(Text, default="")
    raw: Mapped[dict] = mapped_column(JSON, default=dict)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class JobMatch(Base):
    __tablename__ = "job_matches"
    __table_args__ = (UniqueConstraint("job_id", "profile_id", "search_profile_id", name="uq_job_profile_search"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("candidate_profiles.id", ondelete="CASCADE"), index=True)
    search_profile_id: Mapped[int] = mapped_column(ForeignKey("search_profiles.id", ondelete="CASCADE"), index=True)
    resume_id: Mapped[int | None] = mapped_column(ForeignKey("resume_profiles.id", ondelete="SET NULL"), nullable=True)
    technical_score: Mapped[int] = mapped_column(Integer, default=0)
    geography_score: Mapped[int] = mapped_column(Integer, default=0)
    salary_score: Mapped[int] = mapped_column(Integer, default=0)
    relocation_score: Mapped[int] = mapped_column(Integer, default=0)
    total_score: Mapped[int] = mapped_column(Integer, default=0)
    reason: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="new")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    source_id: Mapped[str] = mapped_column(String(64))
    source_application_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    external_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    resume_id: Mapped[int | None] = mapped_column(ForeignKey("resume_profiles.id", ondelete="SET NULL"), nullable=True)
    message: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(64), default="sent")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SeenMessage(Base):
    __tablename__ = "seen_messages"
    __table_args__ = (UniqueConstraint("user_id", "source", "message_id", name="uq_user_source_message"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    source: Mapped[str] = mapped_column(String(32))
    message_id: Mapped[str] = mapped_column(String(256))
    conversation_id: Mapped[str] = mapped_column(String(256), default="")
    text: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RuntimeState(Base):
    __tablename__ = "runtime_state"
    __table_args__ = (UniqueConstraint("user_id", "key", name="uq_user_state_key"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    key: Mapped[str] = mapped_column(String(128))
    value: Mapped[str] = mapped_column(Text, default="")
