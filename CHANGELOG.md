# Changelog

## 3.4.5

Candidate Facts vacancy-comparison release.

- Added deterministic vacancy ↔ Candidate Facts comparison.
- Preserves `commercial`, `lab`, `learning`, `unknown`, and `missing` levels.
- Added `/compare <id>`.
- Added the `🧩 Сравнить с профилем` button.
- Uses full vacancy details when available.
- Missing skills are never invented as candidate experience.
- Lab and learning skills are never promoted to commercial experience.
- Existing search scoring and notification thresholds are unchanged.
- Coverage currently means recognized technical signals, not required vs nice-to-have.
- No database migration is required.


## 3.4.4

Vacancy-details Telegram UX release.

- Added `/job <id>` with source vacancy details, location, work mode, experience, salary, link and Job Agent score breakdown.
- Added a `📋 Подробнее` button to new vacancy notifications.
- `/jobs` now shows job IDs and useful vacancy metadata instead of only title/company/status.
- HH public-web fallback can fetch one vacancy page on demand when the user opens details; regular `/scan` remains lightweight and does not fan out into per-vacancy detail requests.
- HH detail parsing uses public JSON-LD/DOM data and never attempts to bypass CAPTCHA.
- Fixed HH web salary extraction when the compensation selector contains payment-frequency text instead of the salary amount.
- Remote/source HTML is cleaned for Telegram display and common UTF-8/Latin-1 mojibake is repaired when safe.
- No database schema, scoring thresholds, auto-apply or private HH behavior changed.

## 3.4.3

Small manual runtime-control release.

- Added the `job-agent` command-line control utility.
- Added `start`, `stop`, `restart`, `rebuild`, `status`, `logs` and `update`.
- `job-agent logs` now shows recent logs and exits; `job-agent logs -f` follows them.
- Source and running-container versions are displayed separately.
- Job Agent and PostgreSQL no longer automatically start when Docker starts.
- Added a longer graceful shutdown timeout for the application.
- `job-agent update` refuses to run outside `main` or with an unclean working tree.
- Updating a stopped Job Agent keeps it stopped.

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
