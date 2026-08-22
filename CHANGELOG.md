# Changelog

## 3.4.0

Small storage-foundation release based on 3.3.3.

- Added database schema version tracking in `schema_migrations`.
- Added an idempotent additive migration for profile/resume/search metadata.
- Added soft-delete metadata fields for future admin/data-management features; no delete UI is enabled yet.
- Added persistent `/app/storage` Docker volume for future uploaded/generated resume files.
- Added `ResumeProfile.storage_path` metadata.
- Added `/version` with application + DB schema status.
- Existing job search, HH fallback, RemoteOK, scoring and Candidate Facts behavior is intentionally unchanged.
- No table/column is dropped or renamed in this release.
