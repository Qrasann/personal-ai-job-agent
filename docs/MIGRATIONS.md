# Database migrations

v3.4.0 introduces a small built-in additive migration runner.

- Existing v3.3.3 PostgreSQL data is upgraded in place.
- Migrations only use `ADD COLUMN IF NOT EXISTS` in this release.
- No tables or user data are dropped or renamed.
- Applied versions are recorded in `schema_migrations`.
- `/version` reports application and database schema versions.

Never use `docker compose down -v` during normal upgrades: `-v` removes named volumes.


## Schema 2 — Candidate Fact experience type (v3.4.1)

Adds `candidate_facts.experience_type` with one of `commercial`, `lab`, `learning`, or `unknown`.
Legacy rows with `commercial=true` are migrated to `commercial`. Legacy non-commercial rows remain `unknown`; the migration deliberately does not guess whether they are lab or learning experience.
The existing `commercial` boolean is retained and kept synchronized for compatibility with older code paths.
