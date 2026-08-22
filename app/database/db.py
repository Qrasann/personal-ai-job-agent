from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.config import settings
from app.database.migrations import CURRENT_SCHEMA_VERSION, apply_migrations
from app.database.models import Base, SchemaMigration

engine = create_async_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


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
