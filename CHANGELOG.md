# Changelog

> The source tree on GitHub `main` and the latest formal release/tag are v3.5.6.
> Changelog entries v3.5.2–v3.5.5 are cumulative source milestones included
> in v3.5.6; they were not published as individual releases or tags.
> The active feature branch is preparing v3.5.7; `main` and the latest formal
> release remain v3.5.6 until candidate checks and acceptance are complete.

## v3.5.7 — Candidate: Armenia and Georgia ATS Discovery

- Add Armenia (`AM`) to the selectable country catalog.
- Connect a bounded discovery-only Greenhouse Job Board API adapter for
  Lineate, scoped to selected Armenia/Georgia markets and matching role titles.
- Keep work mode, salary, visa sponsorship and relocation unknown unless the
  public posting explicitly provides evidence. No private API or application
  submission is used.
- Greenhouse's documented public GET endpoint requires no authentication.
  Current Lineate listings include an Infrastructure Engineer role for its
  Georgian office; current role fit and eligibility still require vacancy-level
  matching and review.
- Decode HTML entities in vacancy details before stripping markup, so Greenhouse
  descriptions render as readable Telegram text.
- Recognize `Necessary Qualifications`, `Required Qualifications`, `Minimum
  Qualifications`, and `Essential Qualifications` as explicit required
  sections. This lets Recommendation v2 assess interview risk from the vacancy's
  mandatory technical signals instead of falling back to an unqualified role
  score.
- Extract English `Minimum N years` / `At least N years` experience wording and
  compare it with commercial Candidate Facts. Add Windows and Databricks to the
  technical evidence vocabulary so explicit Lineate requirements are visible.
- Use the same decoded vacancy description for Technical Score v2 and
  Recommendation v2 interview-risk analysis. This fixes stored Greenhouse HTML
  rows where Technical had a score but interview risk stayed unknown.
- Retry one Job Bank transport failure under the shared request lock, retaining
  the five-second delay before each attempt; do not retry HTTP status errors.
- Full isolated PostgreSQL suite: 248 passed; branch coverage 68.36% (55%
  gate). Compilation and `git diff --check` pass. Latest code commit `8a583c7`
  passed push CI `38151840822` and PR CI `38151843490`. Compose project `repo`
  runs candidate 3.5.7; its startup scan completed at 15:38:13 UTC without a
  source error, SSL error, timeout, or traceback in the inspected logs. The
  owner still needs to review the interview-risk line in Telegram. Draft PR #18
  remains unmerged; no v3.5.7 tag or release has been published.

## v3.5.6 — Recommendation Model v2, Candidate Import & Search Reliability

Recommendation Model v2 evidence breakdown.

- Store an explainable per-vacancy breakdown for technical fit, growth,
  fast-start, interview risk, salary, remote, relocation, security,
  infrastructure and competition.
- Keep unsupported dimensions unknown (`null`), including competition counts
  and employer security signals that public sources do not expose.
- Show the breakdown in Telegram vacancy details. Existing total scoring and
  notification thresholds remain unchanged pending labeled outcome data.
- Additive PostgreSQL migration 4 stores recommendation dimensions as JSONB.
- Full isolated PostgreSQL suite: 220 passed; branch coverage 65.66%.
- GitHub PR #15 merged this version into `main`; push and PR CI passed.
- Owner completed Telegram acceptance: unsupported ZIP was rejected, already
  imported files were detected, a TXT resume was saved after the preview
  confirmation, and `/job 580` displayed Recommendation v2 with unsupported
  dimensions left unknown.
- EURES requests use identity encoding after a live container test reproduced
  TLS read failures with the default compressed response and successfully read
  the full 50-result JSON with identity encoding.
- `/targets` now updates all active search profiles by default and supports
  explicit `career` or `relocation` scope. `/sources` lists each active
  profile's configured source plan.
- Updated-candidate isolated PostgreSQL suite: 224 passed; branch coverage
  66.33% (55% gate).
- PR #16 merged into `main` at `874b372` as part of the cumulative v3.5.6
  release: pause JOBS.GE after the configured homepage returned HTTP 410; show
  its status in `/sources`.
  Add one retry for transient Arbeitnow transport failures with a 15-second
  timeout. Verification: 233 isolated PostgreSQL tests passed, push/PR CI
  passed, and the safe updater confirmed runtime 3.5.6 with a successful
  startup scan. The owner confirmed `/sources` shows JOBS.GE paused and a fresh
  GE scan returned EURES 16 and HR.ge 2. `/scanstatus` measured Job Bank at
  99.5 seconds of a 162-second scan; its five-second request pacing remains.

## v3.5.5 — Candidate Import & Profile Sync

Candidate Import & Profile Sync.

- Add bounded PDF, DOCX and TXT resume import with text extraction only; raw
  uploaded documents are never written to disk.
- Preview imported content metadata and evidence-scoped fact proposals in
  Telegram; resume and optional facts are saved only after explicit confirmation.
- Record fact confidence and provenance, mark experience type unknown, skip
  exact duplicates and flag overlaps without overwriting existing facts.
- Add additive PostgreSQL migration 3; all existing candidate facts receive
  confidence `1.0` and provenance `manual`.
- Full isolated PostgreSQL suite: 217 passed; branch coverage 65.15%.
- This source milestone is included in cumulative release v3.5.6; it was not
  tagged as an individual v3.5.5 release.

## v3.5.4 — EURES Cross-border Discovery

EURES cross-border vacancy discovery.

- Add public EURES search restricted to vacancies with the employer's
  cross-border recruitment flag, bounded by active profile queries.
- Preserve the EURES eligibility signal and evidence URL; do not infer visa
  sponsorship, relocation benefits, or third-country work authorization.
- Add EURES countries to destination selection and retain employer application
  links from the source vacancy details.
- No database migration is required.

## v3.5.3 — Fast Scan & Scan Dashboard

Fast Scan & Scan Dashboard.

- Run independent source discovery with a bounded concurrency of three while
  keeping source-priority ingestion sequential.
- Record per-source discovery timings and isolate source failures/timeouts.
- Persist manual scan state and summary in `runtime_state`; add `/scanstatus`
  and `/cancel` controls.
- Preserve Job Bank's five-second crawl pacing and existing source cache.
- Full PostgreSQL suite: 197 passed; branch coverage 63.80% (55% gate).
- GitHub Actions CI run 105 passed; local Compose startup scan completed.
- No database migration is required.

## v3.5.2 — Search Control Center & Dual Search Modes

Search Control Center, dual search profiles, and international relocation sources.

- Add independent Career-first and Relocation-first query profiles and balanced
  search strategy.
- Add source/geography controls, salary preferences and blacklist commands.
- Add public Arbeitnow Germany and Job Bank Canada discovery with conservative
  visa, eligibility and relocation evidence handling.
- Full PostgreSQL suite at final v3.5.2 feature stage: 194 passed.
- No database migration is required.

## v3.5.1 — Search Quality & Telegram UX

Search Quality & Telegram UX release.

- Manual `/scan` now forces fresh discovery instead of reusing the discovery cache.
- Expanded HeadHunter discovery across separate role queries and multiple result pages.
- Added Good / Stretch / Skip vacancy fit lanes and Stretch review workflow.
- Added hard filtering for seniority, production skill/role experience and management requirements.
- Added Candidate Facts-based commercial experience fit.
- Resume selection now considers active resume content while remaining score-neutral.
- Added local city/work-mode policy and optional domestic relocation within Russia.
- Normalized RUB/RUR aliases for salary-fit calculation.
- Added richer review, Stretch and saved vacancy cards with Back/Next navigation.
- `/jobs` now includes inline vacancy detail buttons.
- `/start` and `/help` share the complete command menu.
- Scan summaries expose discovery freshness and Good/Stretch lane counts.
- Full local suite baseline is 157 passing tests with 3 skipped.
- CI coverage gate remains 55%.
- No database migration is required.


## v3.5.0 — Review & Saved Workflow

Review and saved workflow release.

- /review now operates on the full notified vacancy backlog instead of a 10-item batch.
- Review cards show the real position in the full backlog.
- Save, skip and next actions continue across the full review queue.
- Added /saved for browsing saved vacancies.
- Saved vacancies support details and next navigation.
- Added saved empty-state and end-of-list handling.
- Review and saved lists deduplicate equivalent title/company rows.
- Added PostgreSQL integration coverage for review and saved backlogs larger than 10 items.
- Full suite baseline is 125 passing tests.
- CI coverage gate remains 55%; local v3.5.0 coverage baseline is 58.58%.
- No database migration is required.


## v3.4.9 — Quality Foundation

Quality-foundation release.

- Added isolated PostgreSQL integration tests.
- GitHub CI now starts PostgreSQL 16 for repository integration tests.
- CI fails if the test database is missing instead of silently skipping integration tests.
- Added branch coverage reporting and a 55% minimum CI gate.
- Full suite baseline is 117 passing tests with 58% total application coverage.
- Database repository coverage increased to 65%.
- Candidate bootstrap coverage increased to 100%.
- Added mutmut-based mutation testing for Technical Score v2 and Candidate Facts comparison.
- Mutation baseline: 249 generated, 240 killed, 9 reviewed equivalent/redundant survivors, 0 meaningful survivors.
- Added boundary tests for zero Technical Score, strongest fact IDs, separator normalization and non-persisted fact IDs.
- Simplified CandidateFact attribute handling and removed redundant requirement-heading sorting.
- Removed unused app/geo/runtime.py.
- Replaced deprecated datetime.utcnow usage while preserving TIMESTAMP WITHOUT TIME ZONE semantics.
- Added docs/developer/TESTING.md.
- No database migration is required.

## v3.4.8 — Vacancy Review Queue

Vacancy Review Queue release.

- Added /review for browsing notified vacancies.
- Added saved match status and reused skipped status.
- Added Save, Skip, Details and Next review actions.
- Save and Skip automatically advance the current review batch.
- Saved and skipped matches suppress future title/company repost notifications.
- Review queue sorts by score/newness and suppresses duplicate title/company entries.
- Saved matches are protected from later filtered-status downgrade.
- Review position is presented as the current batch rather than the entire backlog.
- No database migration is required.


## v3.4.7 — Technical Score v2 & Live Scan Progress

Technical Score v2, full vacancy details and scan-progress release.

- Added structured Technical Score v2 for required and preferred requirements.
- Candidate Facts experience types now affect technical scoring.
- Legacy Technical scoring remains the fallback when no required requirements are recognized.
- HeadHunter full vacancy details are selectively fetched and cached.
- Full-detail rescoring preserves existing match workflow status.
- Added more vacancy section-heading classifications.
- Improved source error diagnostics.
- /scan now shows source and analysis progress.
- /scan now includes a live spinner and elapsed-time heartbeat.
- Geography, salary, relocation, caps and notification thresholds remain unchanged.
- No database migration is required.


## v3.4.6 — Telegram UX & Requirement Classification

Telegram UX, requirement-classification and startup-resilience release.

- Added support for multiple Telegram commands in one message, one command per line.
- Multi-command batches execute sequentially.
- Empty lines are ignored; mixed command/plain-text batches are rejected.
- Multi-command batches are limited to 10 commands.
- Vacancy comparison now separates required, preferred and other technical signals.
- Candidate experience remains commercial, lab, learning, unknown or missing.
- Technologies mentioned only in responsibilities are not promoted to mandatory requirements.
- Added separate coverage counts for required, preferred and other signals.
- Added Telegram startup retry with capped exponential backoff for temporary network failures.
- Authentication/configuration errors still fail fast.
- Docker Compose remains manual-start with restart: "no".
- Existing scoring and notification thresholds are unchanged.
- No database migration is required.


## v3.4.5 — Candidate Facts Vacancy Comparison

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


## v3.4.4 — Vacancy Details

Vacancy-details Telegram UX release.

- Added `/job <id>` with source vacancy details, location, work mode, experience, salary, link and Job Agent score breakdown.
- Added a `📋 Подробнее` button to new vacancy notifications.
- `/jobs` now shows job IDs and useful vacancy metadata instead of only title/company/status.
- HH public-web fallback can fetch one vacancy page on demand when the user opens details; regular `/scan` remains lightweight and does not fan out into per-vacancy detail requests.
- HH detail parsing uses public JSON-LD/DOM data and never attempts to bypass CAPTCHA.
- Fixed HH web salary extraction when the compensation selector contains payment-frequency text instead of the salary amount.
- Remote/source HTML is cleaned for Telegram display and common UTF-8/Latin-1 mojibake is repaired when safe.
- No database schema, scoring thresholds, auto-apply or private HH behavior changed.

## v3.4.3 — Runtime Controls

Small manual runtime-control release.

- Added the `job-agent` command-line control utility.
- Added `start`, `stop`, `restart`, `rebuild`, `status`, `logs` and `update`.
- `job-agent logs` now shows recent logs and exits; `job-agent logs -f` follows them.
- Source and running-container versions are displayed separately.
- Job Agent and PostgreSQL no longer automatically start when Docker starts.
- Added a longer graceful shutdown timeout for the application.
- `job-agent update` refuses to run outside `main` or with an unclean working tree.
- Updating a stopped Job Agent keeps it stopped.

## v3.4.2 — CI Foundation

Small CI foundation release.

- Added GitHub Actions checks for Python compilation, pytest and Docker image build.
- Added `.dockerignore` so local virtual environments, Git metadata, secrets and runtime data are not sent in the Docker build context.
- Added a lightweight Git-history secret scan for obvious private keys and common token formats.
- Added `requirements-dev.txt` so local and CI test dependencies are reproducible without installing pytest globally.
- CI uses Python 3.12 to match the application Docker image.
- No runtime search, scoring, database schema, Telegram or AI behavior changed.

## v3.4.1 — Candidate Fact Types

Small Candidate Facts typing release.

- Added structured `experience_type` to Candidate Facts: `commercial`, `lab`, `learning`, `unknown`.
- Added additive DB schema migration v2; existing `commercial=true` facts become `commercial`, other legacy facts remain `unknown` rather than being guessed.
- Added `/fact type <id> commercial|lab|learning|unknown`.
- `/facts` now always shows an explicit type tag.
- Kept `/fact commercial` and `/fact noncommercial` as backward-compatible aliases; `noncommercial` maps to `unknown` because the old boolean cannot distinguish lab from learning.
- Kept the legacy `commercial` boolean synchronized for existing downstream code.
- No vacancy search, scoring, HH, RemoteOK or application behavior changed.

## v3.4.0 — Storage Foundation

Small storage-foundation release based on 3.3.3.

- Added database schema version tracking in `schema_migrations`.
- Added an idempotent additive migration for profile/resume/search metadata.
- Added soft-delete metadata fields for future admin/data-management features; no delete UI is enabled yet.
- Added persistent `/app/storage` Docker volume for future uploaded/generated resume files.
- Added `ResumeProfile.storage_path` metadata.
- Added `/version` with application + DB schema status.
- Existing job search, HH fallback, RemoteOK, scoring and Candidate Facts behavior is intentionally unchanged.
- No table/column is dropped or renamed in this release.
