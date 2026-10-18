from pathlib import Path
from contextlib import asynccontextmanager

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.config import settings
from app.database.migrations import CURRENT_SCHEMA_VERSION, apply_migrations
from app.database.models import Base, SchemaMigration

engine = create_async_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

SCAN_LOCK_NAMESPACE = 0x4A4F42


@asynccontextmanager
async def user_scan_lease(user_id: int, *, scan_engine=None):
    """Hold one PostgreSQL transaction lock for a user's scan across processes.

    A process crash or cancelled task closes the transaction and releases the
    lock. Other repository work uses separate connections while it is held.
    """
    target = scan_engine or engine
    async with target.begin() as conn:
        acquired = await conn.scalar(
            text("SELECT pg_try_advisory_xact_lock(:namespace, :user_id)"),
            {"namespace": SCAN_LOCK_NAMESPACE, "user_id": int(user_id)},
        )
        yield bool(acquired)


async def init_db() -> None:
    """Create the baseline schema and apply safe additive migrations.

    `create_all()` is deliberately retained for fresh installations. On an existing
    v3.3.3 database it does not alter existing tables; `apply_migrations()` then adds
    only the new v3.4.0 columns. No destructive migration is performed.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await apply_migrations(conn)

    Path(settings.storage_path).mkdir(parents=True, exist_ok=True)


async def current_schema_version() -> int:
    async with SessionLocal() as session:
        version = await session.scalar(select(func.max(SchemaMigration.version)))
        return int(version or 0)


def expected_schema_version() -> int:
    return CURRENT_SCHEMA_VERSION
