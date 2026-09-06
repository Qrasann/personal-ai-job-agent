from __future__ import annotations

from dataclasses import dataclass

from app.database.time_utils import utcnow_naive

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection


CURRENT_SCHEMA_VERSION = 2


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    statements: tuple[str, ...]


MIGRATIONS: tuple[Migration, ...] = (
    Migration(
        version=1,
        name="profile_storage_foundation",
        statements=(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITHOUT TIME ZONE NULL",
            "ALTER TABLE candidate_profiles ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "ALTER TABLE candidate_profiles ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITHOUT TIME ZONE NULL",
            "ALTER TABLE candidate_facts ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "ALTER TABLE candidate_facts ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITHOUT TIME ZONE NULL",
            "ALTER TABLE resume_profiles ADD COLUMN IF NOT EXISTS storage_path TEXT NOT NULL DEFAULT ''",
            "ALTER TABLE resume_profiles ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "ALTER TABLE resume_profiles ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "ALTER TABLE resume_profiles ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITHOUT TIME ZONE NULL",
            "ALTER TABLE search_profiles ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "ALTER TABLE search_profiles ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "ALTER TABLE search_profiles ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITHOUT TIME ZONE NULL",
        ),
    ),
    Migration(
        version=2,
        name="candidate_fact_experience_type",
        statements=(
            "ALTER TABLE candidate_facts ADD COLUMN IF NOT EXISTS experience_type VARCHAR(32) NOT NULL DEFAULT 'unknown'",
            "UPDATE candidate_facts SET experience_type = 'commercial' WHERE commercial IS TRUE AND experience_type = 'unknown'",
        ),
    ),
)


async def applied_versions(conn: AsyncConnection) -> set[int]:
    rows = await conn.execute(text("SELECT version FROM schema_migrations"))
    return {int(row[0]) for row in rows.fetchall()}


async def apply_migrations(conn: AsyncConnection) -> list[int]:
    """Apply additive, idempotent PostgreSQL migrations.

    v3.4.0 intentionally does not rename or drop existing columns/tables. This lets an
    existing v3.3.3 database be upgraded in place without losing Candidate Facts,
    search settings, jobs, matches or applications.
    """
    done = await applied_versions(conn)
    applied: list[int] = []
    for migration in MIGRATIONS:
        if migration.version in done:
            continue
        for statement in migration.statements:
            await conn.execute(text(statement))
        await conn.execute(
            text(
                "INSERT INTO schema_migrations (version, name, applied_at) "
                "VALUES (:version, :name, :applied_at)"
            ),
            {
                "version": migration.version,
                "name": migration.name,
                "applied_at": utcnow_naive(),
            },
        )
        applied.append(migration.version)
    return applied
