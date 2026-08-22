# Changelog

## 3.4.2

Small CI foundation release.

- Added GitHub Actions checks for Python compilation, pytest and Docker image build.
- Added `.dockerignore` so local virtual environments, Git metadata, secrets and runtime data are not sent in the Docker build context.
- Added a lightweight Git-history secret scan for obvious private keys and common token formats.
- Added `requirements-dev.txt` so local and CI test dependencies are reproducible without installing pytest globally.
- CI uses Python 3.12 to match the application Docker image.
- No runtime search, scoring, database schema, Telegram or AI behavior changed.

## 3.4.1

Small Candidate Facts typing release.

- Added structured `experience_type` to Candidate Facts: `commercial`, `lab`, `learning`, `unknown`.
- Added additive DB schema migration v2; existing `commercial=true` facts become `commercial`, other legacy facts remain `unknown` rather than being guessed.
- Added `/fact type <id> commercial|lab|learning|unknown`.
- `/facts` now always shows an explicit type tag.
- Kept `/fact commercial` and `/fact noncommercial` as backward-compatible aliases; `noncommercial` maps to `unknown` because the old boolean cannot distinguish lab from learning.
- Kept the legacy `commercial` boolean synchronized for existing downstream code.
- No vacancy search, scoring, HH, RemoteOK or application behavior changed.

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
