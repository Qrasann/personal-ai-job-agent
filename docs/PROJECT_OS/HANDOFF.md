# Handoff

## GitHub branches and release labels — 2026-10-11

- `main` is the stable source branch at merge commit `874b372`, with `VERSION`
  set to v3.5.6. PR #15 and [PR #16](https://github.com/Qrasann/personal-ai-job-agent/pull/16)
  are merged. Main CI run `38135649948` passed.
- The local checkout is on `main`. Application commit `170ed4e` is deployed to
  Compose project `repo`; later PR #16 commits updated documentation only.
- `feature/v3.5.2-dual-search-modes` remains on the remote from earlier work;
  it is not the active branch for new changes.
- The merged `feature/v3.5.6-eures-identity-market-targets` branch is inactive.
  Create the next implementation branch from `main` for v3.5.7.
- GitHub Releases and version tags currently stop at v3.5.1. The v3.5.2–v3.5.6
  changelog entries are cumulative source milestones, not formal releases.
  Publish one cumulative v3.5.6 release after resume-import and Recommendation
  v2 Telegram acceptance; do not backfill tags for intermediate milestones.
- README.md and README.ru.md provide English and Russian entry points on `main`.

## Owner Telegram scan and source-resilience follow-up — 2026-10-11

Post-deployment logs confirmed Arbeitnow's Relocation-first retry recovered
from `ReadTimeout` with HTTP 200; EURES, HR.ge, Job Bank, and HH requests shown
also succeeded. JOBS.GE was not requested. The 162.7-second Telegram update is
now attributed by `/scanstatus`: Job Bank took 99.5 seconds, Arbeitnow 17.1,
EURES 14.5, HR.ge 13.0, HH 7.6, and Remote OK 1.5. Keep the current Job Bank
request pacing until a safe optimization is verified against its source rules.

The owner ran `/targets relocation GE`, `/sources`, `/scan`, and `/scanstatus`.
`/sources` visibly marks JOBS.GE temporarily paused after HTTP 410; HR.ge remains
enabled for GE. The completed scan returned HH 209, Remote OK 3, Arbeitnow 2,
Job Bank 12, EURES 16, and HR.ge 2. Source timings were HH 7.6s, Remote OK
1.5s, Arbeitnow 17.1s, Job Bank 99.5s, EURES 14.5s, and HR.ge 13.0s. The scan
ran from 09:47:54 to 09:50:36 UTC. The prior log's 162.7-second Telegram
update is consistent with the scan duration; Job Bank is the main measured
latency contributor.

The candidate adds regressions for transient timeout recovery, retry
exhaustion, non-retry of HTTP status failures, and the paused source-plan state.
Full isolated PostgreSQL suite: 233 passed, 67.67% branch coverage;
`compileall` and `git diff --check` passed. Commit `170ed4e` is published on PR
#16; push CI `38129138392` and PR CI `38129141546` passed. The safe updater
applied it. Runtime remains 3.5.6, the app is up, PostgreSQL is healthy, and
the startup scan completed. Arbeitnow, EURES, and HR.ge requests returned HTTP
200; no JOBS.GE request or source error appeared. Mount inspection confirms
`repo_jobagent_v3_pg` and `repo_jobagent_v3_files` remain attached. No schema
change was made.

The manual scan exercised and verified Arbeitnow retry recovery. A later log
tail showed scheduled `scan_all` completed and Telegram updates were handled in
117–677 ms, with no errors in that excerpt. Keep Job Bank's five-second
request pacing until a measured optimization is tested. Keep `.env`, the
database, and existing Compose volumes untouched.

Prior Georgia guardrail commits are published on PR #16 at `0110173`,
following adapter change `2963705`. Push CI `38127150025` and PR CI
`38127152783` passed for that prior head, and its safe updater deployment was
verified before the owner scan. The owner supplied the live Georgia source
result described above. Georgia detail collection is capped at six per source,
uses 15-second timeouts and two-second pacing, preserves partial detail results,
and caches scheduled scans for six hours. Manual `/scan` forces fresh
discovery. Role matching requires a specific query token; HR.ge salary enters
scoring only with an explicit currency and monthly period. Work mode and
relocation remain unknown without source evidence.

Access review: JOBS.GE `/robots.txt` returned HTTP 410, so crawl rules are not
available. HR.ge `/robots.txt` returned HTTP 200 and allows `/`, with a link to
a 5.4 MB sitemap that the adapter does not download. These results do not
grant permission to reuse listings; recurring automated extraction terms
remain unverified. The adapters stay limited to Georgia-targeted profiles.

The source/runtime version remains 3.5.6 while v3.5.7 market-coverage work is
planned. JOBS.GE access and HR.ge
reuse terms remain unresolved; do not treat the boards as validated recurring
sources until access conditions are reviewed. The prior
`/import` preview/save and Recommendation v2 detail acceptance remains a
separate gate before release tagging.

The release map is intentional: `VERSION=3.5.6` describes source code, while
the latest formal GitHub release/tag remains v3.5.1. Entries v3.5.2–v3.5.6 in
the changelog are cumulative milestones. Once `/import` preview/save and a
vacancy's Recommendation v2 details are accepted in Telegram, publish one
cumulative v3.5.6 tag/release. Do not backfill intermediate tags.

## v3.5.6 candidate update — PR #16 (2026-10-11)

Candidate commit `6fa3406` is published on
`feature/v3.5.6-eures-identity-market-targets` as [PR #16](https://github.com/Qrasann/personal-ai-job-agent/pull/16).
At the time of this candidate update, the application and handoff changes
passed push and PR CI while GitHub `main` remained at `6294c2a`. PR #16 was
later merged into `main` at `874b372`; that merge and its CI are recorded at
the top of this handoff. The candidate and deployed app report source/runtime
v3.5.6. The latest published GitHub release/tag remains v3.5.1; do not tag
v3.5.6 until owner acceptance is recorded.

EURES failed while reading compressed response bodies in the running container.
A direct request reproduced the TLS record-layer error with default encoding;
the same request using `Accept-Encoding: identity` read all 50 result records.
The adapter now requests identity encoding. After the safe update, the first
startup dual-profile scan completed (`scan_all` executed successfully); EURES
search and detail requests returned HTTP 200, with no SSL retries/errors in the
run. Continue monitoring later scheduled scans because the underlying network
cause is not yet established.

`/targets GE` now applies target countries to all active profiles;
`/targets relocation GE` and `/targets career GE` scope the change. `/sources`
lists each active profile's configured source plan. Georgia adapters are
included only for profiles targeting GE. The owner subsequently ran the GE
scan; the latest result and post-update source checks are recorded above.
Armenia is not yet in
the country catalog and has no connected adapter. The Unified Social Service
lists e-work.am and workforall.am as vacancy platforms, but both public search
pages timed out and no public API/feed or automated-access terms were verified.
Official registration guidance leaves pre-move foreign-candidate access
unclear. The next source step is to request a permitted feed from
`info@socservice.am`. Staff.am prohibits automated scraping without permission;
Job.am restricts unauthorized reuse and redistribution. See
`docs/developer/INTERNATIONAL_SOURCES.md` and the v3.5.7 plan in `ROADMAP.md`.

The full isolated PostgreSQL suite passed: 224 tests, 66.33% branch coverage;
compileall and `git diff --check` passed. Compose reports the app polling and
PostgreSQL healthy. Mount inspection confirms `repo_jobagent_v3_pg` and
`repo_jobagent_v3_files` remain attached. No database migration was added.

Remaining owner acceptance before release tagging: upload a test resume and
review/cancel or confirm the `/import` preview/save flow; open a vacancy and
inspect Recommendation v2 details. Do not publish a v3.5.6 tag before these
checks.

## v3.5.6 main merge and Telegram smoke test — 2026-10-11

GitHub PR #15 is merged into `main` at `062eb253bdf8435782e5fcca6cfb1257b271ea86`;
the branch now contains v3.5.6. The full PostgreSQL suite passes (220 tests,
65.66% branch coverage), and final push/PR CI runs `38121905782` and
`38121908521` passed.

Owner-provided real-chat smoke results confirm `/salary`, `/blacklist`,
`/scanstatus`, `/cancel`, the `/import` upload prompt, `/version` (v3.5.6,
schema 4/4, migration OK), and `/status` (ACTIVE). The reported scan completed;
EURES failed after retries while the other configured sources returned results.
The owner has not yet exercised `/import` with a file through preview/save or
opened a vacancy to review Recommendation v2 details; both remain required
before release tagging.

The running Compose app reports source/runtime 3.5.6 and PostgreSQL healthy;
the existing `repo_jobagent_v3_pg` and `repo_jobagent_v3_files` volumes remain
attached. Recent logs show intermittent EURES TLS record-layer failures mixed
with successful HTTP 200 responses. Retries and partial-result handling work,
but EURES is still an occasional source-level failure; the latest scheduled
scan completed and other sources continued.

## Current stage — v3.5.6 Recommendation Model v2 (2026-10-11)

Each new or refreshed match stores a JSONB evidence breakdown for technical,
growth, fast-exit, interview-risk, salary, remote, relocation, security,
infrastructure and competition signals. Vacancy details show the components
and evidence. Missing evidence stays `null`; public candidate counts and
employer security signals are not fabricated. The old composite score and
notification thresholds remain unchanged until labeled outcomes are available
for calibration. Migration 4 adds only `job_matches.recommendation_scores`.
Full isolated PostgreSQL suite: 220 passed, 65.66% branch coverage. Commit
`496c920` is published and deployed; runtime reports 3.5.6, schema 4/4, healthy
PostgreSQL and active polling. Existing PostgreSQL and storage volumes remain
attached. Real-chat acceptance remains required before release tagging.

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
