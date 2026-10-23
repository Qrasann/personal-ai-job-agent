from __future__ import annotations

from dataclasses import dataclass

from app.database.time_utils import utcnow_naive

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection


CURRENT_SCHEMA_VERSION = 9


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
    Migration(
        version=3,
        name="candidate_fact_confidence_provenance",
        statements=(
            "ALTER TABLE candidate_facts ADD COLUMN IF NOT EXISTS confidence FLOAT NOT NULL DEFAULT 1.0",
            "ALTER TABLE candidate_facts ADD COLUMN IF NOT EXISTS provenance VARCHAR(64) NOT NULL DEFAULT 'manual'",
        ),
    ),
    Migration(
        version=4,
        name="job_match_recommendation_scores",
        statements=(
            "ALTER TABLE job_matches ADD COLUMN IF NOT EXISTS recommendation_scores JSONB NOT NULL DEFAULT '{}'::jsonb",
        ),
    ),
    Migration(
        version=5,
        name="application_status_history",
        statements=(
            "CREATE TABLE IF NOT EXISTS application_status_events ("
            "id SERIAL PRIMARY KEY, "
            "application_id INTEGER NOT NULL REFERENCES applications(id) ON DELETE CASCADE, "
            "user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, "
            "status VARCHAR(64) NOT NULL, "
            "created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP"
            ")",
            "CREATE INDEX IF NOT EXISTS ix_application_status_events_application_id "
            "ON application_status_events(application_id)",
            "CREATE INDEX IF NOT EXISTS ix_application_status_events_user_id "
            "ON application_status_events(user_id)",
        ),
    ),
    Migration(
        version=6,
        name="application_resume_snapshot",
        statements=(
            "ALTER TABLE applications ADD COLUMN IF NOT EXISTS resume_snapshot TEXT NOT NULL DEFAULT ''",
            "ALTER TABLE applications ADD COLUMN IF NOT EXISTS resume_external_id VARCHAR(256) NULL",
            "INSERT INTO application_status_events (application_id, user_id, status, created_at) "
            "SELECT a.id, a.user_id, a.status, a.created_at FROM applications a "
            "WHERE NOT EXISTS (SELECT 1 FROM application_status_events e "
            "WHERE e.application_id = a.id)",
        ),
    ),
    Migration(
        version=7,
        name="application_vacancy_snapshot",
        statements=(
            "ALTER TABLE applications ADD COLUMN IF NOT EXISTS vacancy_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb",
        ),
    ),
    Migration(
        version=8,
        name="protect_application_history_on_job_delete",
        statements=(
            # Preserve stored application evidence when routine vacancy cleanup
            # attempts to remove a job. This changes a constraint only; no rows
            # are deleted or rewritten.
            "ALTER TABLE applications DROP CONSTRAINT IF EXISTS applications_job_id_fkey",
            "ALTER TABLE applications ADD CONSTRAINT applications_job_id_fkey "
            "FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE RESTRICT",
        ),
    ),
    Migration(
        version=9,
        name="application_event_provenance_immutability",
        statements=(
            "ALTER TABLE application_status_events ADD COLUMN IF NOT EXISTS provenance VARCHAR(32) NOT NULL DEFAULT 'legacy'",
            "ALTER TABLE application_status_events ADD COLUMN IF NOT EXISTS evidence JSONB NOT NULL DEFAULT '{}'::jsonb",
            "ALTER TABLE application_status_events ADD COLUMN IF NOT EXISTS event_key VARCHAR(128) NULL",
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_application_status_event_key "
            "ON application_status_events(application_id, event_key) WHERE event_key IS NOT NULL",
            "CREATE OR REPLACE FUNCTION reject_application_status_event_mutation() RETURNS trigger "
            "LANGUAGE plpgsql AS $$ BEGIN "
            "IF TG_OP = 'DELETE' AND NOT EXISTS (SELECT 1 FROM applications WHERE id = OLD.application_id) "
            "THEN RETURN OLD; END IF; "
            "RAISE EXCEPTION 'application status history is immutable'; END; $$",
            "DROP TRIGGER IF EXISTS application_status_events_immutable ON application_status_events",
            "CREATE TRIGGER application_status_events_immutable BEFORE UPDATE OR DELETE ON application_status_events "
            "FOR EACH ROW EXECUTE FUNCTION reject_application_status_event_mutation()",
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
