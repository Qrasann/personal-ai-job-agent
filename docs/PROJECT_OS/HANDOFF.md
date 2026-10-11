# Handoff

## Current stage — v3.5.5 Candidate Import & Profile Sync (2026-10-11)

Implemented `/import` for PDF, DOCX and TXT. Uploads are read in memory and
bounded by size, page, text and DOCX archive limits. Telegram displays a safe
preview of proposed facts and requires an explicit save choice; only then does
the app store extracted resume text and, optionally, proposed facts. It does
not store uploaded binary data or original filenames. Fact proposals are
section-scoped, carry confidence and `resume_import` provenance, and retain
`unknown` experience type. Exact duplicates are skipped; overlaps are flagged
and never replace existing facts.

Migration 3 only adds `confidence` and `provenance` columns to `candidate_facts`;
existing rows receive defaults and are preserved. Full isolated PostgreSQL
suite: 217 passed, 65.15% branch coverage; unit suite: 214 passed, 3 skipped.
Commit `8131e2e` is published and applied with the safe tracked-branch update.
Compose reports runtime 3.5.5, schema 3/3, healthy PostgreSQL and active bot
polling. Inspection confirmed the existing `repo_jobagent_v3_pg` and
`repo_jobagent_v3_files` volumes remain attached. Startup logs showed an
intermittent EURES SSL retry while other sources continued.
Owner-driven Telegram acceptance for `/import` and the outstanding controls
(`/salary`, `/blacklist`, `/scanstatus`, `/cancel`) remains pending before
release tagging.

## Follow-up — raw EURES SSL error (2026-10-11)

The raw `ssl.SSLError` retry fix is published and deployed as `d5d78d3`; logs
showed retry warnings and HTTP 200 responses after retries, but one profile
still exhausted its attempts. Partial-result handling is published and
deployed as `8a87604`; it continues across failed queries/details and retains
successful results, while still reporting a source failure when all searches
or all matching detail requests fail. The full suite passes (208 tests,
64.51% branch coverage). The startup scan showed retry recovery to HTTP 200,
but one profile exhausted retries for every EURES search query and correctly
reported EURES unavailable; Job Bank and other sources continued. PostgreSQL
remained healthy and existing volumes remained attached. The next practical
task is owner-driven Telegram acceptance for `/salary`, `/blacklist`,
`/scanstatus`, and `/cancel`.

## Current stage — source error resilience (2026-10-11)

Latest runtime inspection found EURES transport failures (`ReadTimeout` and an
SSL record-layer error) and a blank Job Bank Telegram alert. EURES now retries
transport-level failures twice with short backoff; HTTP status responses are
not retried. Source failure alerts share the normalized text saved in the scan
summary, including HTTP status codes. Regression tests cover both behaviors.
The isolated PostgreSQL suite passed: 206 tests, 64.46% branch coverage.
Published as `f397f58` and applied with
`JOB_AGENT_COMPOSE_PROJECT=repo ./job-agent update`. Runtime/source report
3.5.4, PostgreSQL is healthy, the bot is polling, and the startup EURES search
returned HTTP 200. Inspection confirmed `repo_jobagent_v3_pg` and
`repo_jobagent_v3_files` remain attached. The update command fetches/pulls
fast-forward-only and rebuilds the currently running service without removing
the database or volumes.

The BRIEF's owner-driven Telegram acceptance remains outstanding for
`/salary`, `/blacklist`, `/scanstatus`, and `/cancel`; do not claim those real
chat commands passed or tag releases until the owner records the results.

## Current deployment — v3.5.4 EURES discovery

The working tree adds bounded EURES search for vacancies whose employer has
enabled the EURES cross-border recruitment flag. This flag is evidence of
interest in hiring across EURES countries only; it is not visa sponsorship,
relocation support, or third-country work authorization. The live public search
and detail endpoints returned HTTP 200. The implementation is published at
`1dc62366fcca46e778d6650928b1fd4c91c2d5cd`; GitHub Actions run 110 passed. The
full isolated PostgreSQL suite passed (203 tests; 64.39% branch coverage), and
Compose project `repo` reports source/runtime 3.5.4. The startup scan reached
EURES successfully. Existing PostgreSQL and storage volumes remain attached.
Telegram real-chat acceptance remains a separate owner task before tagging
v3.5.2/v3.5.3 releases.

The v3.5.3 public competition-signal item has been audited: HH response counts
require employer-side access, Job Bank applicant tables live in the employer
dashboard, and EURES exposes number of positions rather than applicant counts.
No connected public source currently supplies reliable per-vacancy applicant
counts, so the agent does not infer or fabricate one.

## Prior v3.5.3 deployed state — 2026-10-11

Code release commit: `e4fa198f63d07a5120f6e480b63a7be9cdb46efd` on
`feature/v3.5.2-dual-search-modes`. GitHub Actions runs 105–108 passed.
`VERSION` and `CHANGELOG.md` identify the implementation as 3.5.3. The `repo`
Compose app is polling as `@roma_job_agent_bot` on runtime version 3.5.3; the
startup dual-profile scan completed successfully at 21:11:40 UTC, including
live Job Bank queries/details. Existing named PostgreSQL and storage volumes
are preserved.
Latest PostgreSQL suite: 197 passed, 63.80% branch coverage. v3.5.3 Fast Scan
uses three concurrent discovery slots, source-level timing and 180-second
timeouts, sequential priority-ordered ingestion, persistent manual dashboard,
`/scanstatus`, and `/cancel`.

Remaining release acceptance is an owner-driven Telegram chat check for
`/salary`, `/blacklist`, `/scanstatus`, and `/cancel`. No real-chat command
verification was available in this session. Do not tag v3.5.2 or v3.5.3 until
this acceptance is complete.

## Latest stage — salary and blacklist controls

Telegram `/salary` and `/blacklist` were added in the published 3.5.2 stage.
Minimum salary uses the existing `minimum_salary` scoring setting; current and
desired salary are kept separately. Both controls apply to each active profile.
No schema migration is needed.

`testsbuild` is 11 commits ahead and one behind `main` (diverged). Saved queue
navigation is already present in this branch; do not merge testsbuild wholesale.

## v3.5.3 Fast Scan & Scan Dashboard implementation

Review current source-specific delays first, especially Job Bank's five-second
crawl delay. Fast Scan should bound concurrent discovery, keep database
ingestion and matching ordered, and retain per-source errors/timings. A
persistent latest-run dashboard can use `runtime_state` without a destructive
schema change. Add `/scanstatus` and ensure `/cancel` does not interrupt HH
message composition behavior. Verify with mocked concurrency/cancellation
tests, the full PostgreSQL suite, and local Compose logs.

### Implemented in the current working stage

- Discovery for independent adapters runs with a limit of three in parallel;
  ordering, filtering, and database ingestion remain sequential by source
  priority.
- Each source has a 180-second timeout. Failures are isolated and included in
  the source summary, and successful sources still finish processing.
- Manual scan state/progress/results persist in the existing `runtime_state`
  table. `/scanstatus` shows the latest state and source timings; `/cancel`
  stops an active manual scan and still clears the HH reply composer.
- Existing source discovery caching remains in place. Job Bank's internal
  crawl pacing is unchanged.

The full PostgreSQL test suite passed: 197 tests, 63.80% branch coverage.
The implementation is published and deployed. The live startup scan completed
at 21:04:51 UTC; the next check is the owner-driven Telegram command acceptance.

For v3.5.2 dual-mode review:
1. read CURRENT_STATE.md and TASKS.md;
2. inspect app/search/preferences.py;
3. inspect app/telegram/settings_handlers.py and settings_ui.py;
4. inspect the small integrations in app/services.py and app/main.py;
5. inspect `discovery_queries` and `search_strategy` in app/search/preferences.py;
6. run the full PostgreSQL-backed pytest suite;
7. launch the bot in a test Telegram chat;
8. verify `/settings`, all three strategies, `/relocationroles`, source/country/city controls and relocation policies;
9. verify `/scan` uses career queries in career-first, relocation queries in relocation-first, and both in balanced;
10. verify `/scan` behaves like v3.5.1 when no relocation roles or new geography controls are configured.
11. run `/parallelsearch on`, confirm two active profiles, then verify one `/scan` reports both profile names in progress;
12. run `/parallelsearch off`, confirm only Career-first remains active, then enable it again and confirm relocation settings survived.

Local release clones can update their tracked branch with `JOB_AGENT_COMPOSE_PROJECT=repo ./job-agent update`; the command refuses dirty worktrees, detached HEADs and branches without an upstream.

Current branch: `feature/v3.5.2-dual-search-modes`, based on `origin/feature/v3.5.2-search-control`.
No database migration is required; new keys are stored in the existing JSON settings field.
Rollback is limited to the dual-mode commit/files because legacy `queries` remain unchanged.

Earlier verification on 2026-10-10: 175 pytest tests passed against isolated
PostgreSQL 16; branch coverage 63.22% (gate 55%). Subsequent startup, parallel
profile activation and dual-profile scan smoke tests passed locally, as recorded
in DEVELOPMENT_LOG.md. Remote CI now passes for the later v3.5.4 stage;
comprehensive owner-driven Telegram control acceptance remains pending. Read
`BRIEF.md` first for the current concise state and priority.

Parallel search is opt-in. The existing profile becomes `Career-first`; one
`Relocation-first` profile is created and reused. Disabling parallel search
sets that profile inactive and does not delete its settings or JobMatch rows.

Do not merge testsbuild wholesale. Compare it with main and port selected functionality with tests.

## Job Bank source stage — 2026-10-10

Baseline HEAD: `7c987da`; this stage adds local changes on the same branch.
Review `app/sources/adapters/jobbank.py`, its service/registry integration,
`tests/test_jobbank.py` and `docs/developer/INTERNATIONAL_SOURCES.md`.
The adapter uses the active profile's queries and respects source/geography
controls and relocation mode. Eligibility restrictions are explicit exclusions;
missing support stays unknown. LMIA is never equated with sponsorship approval.
No schema migration, automated application or private HH action was added.
Live adapter check returned one international warehouse-worker vacancy with
LMIA requested and unknown sponsorship. DWP currently returns a service-error
page and was deferred.

Final local verification: 191 tests passed against isolated PostgreSQL 16,
64.16% branch coverage (gate 55%); Python compilation and `git diff --check`
passed. The local .venv uses Python 3.14; the deployment image remains Python
3.12. GitHub Actions CI run 102 passed for the Job Bank commit. Comprehensive
Telegram acceptance remains pending.

Local deployment was rebuilt with `JOB_AGENT_COMPOSE_PROJECT=repo ./job-agent
rebuild` from this worktree. Runtime remains v3.5.2; both Career-first and
Relocation-first are active. PostgreSQL stayed healthy and existing
`repo_jobagent_v3_pg` / `repo_jobagent_v3_files` volumes were preserved.
The startup scheduled scan fetched Job Bank search/detail pages with HTTP 200
and completed successfully at 20:44:49 UTC on 2026-10-10.
Changes are uncommitted; HEAD is still `7c987da`. No push, merge or PR occurred.
