# Codex Brief

Last updated: 2026-10-11 (Europe/Moscow)

## Mission

Continue the existing Personal AI Job Agent. Maintain two independent tracks:

1. **Career-first** — DevOps / Infrastructure / SRE growth.
2. **Relocation-first** — any legal, verifiable work that can enable a realistic move; career fit is secondary.

Never restart the project from scratch. Unknown visa, salary, citizenship, housing, or relocation facts remain unknown; never convert missing evidence into `false` or a positive claim.

## Current runtime

- Source/runtime: `v3.5.6`, database schema `4/4`.
- GitHub `main`: `6294c2a` (`v3.5.6`). Deployed application commit `170ed4e`
  is on candidate branch `feature/v3.5.6-eures-identity-market-targets`.
- GitHub PR #16 is open on `main`. Candidate branch tip is `2166e0c`; the
  deployed application code is `170ed4e`. Latest push CI `38129983586` passed;
  current PR details are at
  https://github.com/Qrasann/personal-ai-job-agent/pull/16.
- Branch map: `main` is the stable source; `feature/v3.5.6-eures-identity-market-targets`
  is the active PR #16 branch and is where current changes are pushed. The
  remote `feature/v3.5.2-dual-search-modes` branch remains from earlier work
  but is not the active development branch.
- Release map: the source `VERSION` on `main` is v3.5.6, while the latest
  published GitHub tag/Release is v3.5.1. Changelog entries v3.5.2–v3.5.6 are
  untagged source milestones; v3.5.6 still awaits owner Telegram acceptance.
- Local release directory: `~/job-agent-release-v352`.
- Docker Compose project: `repo`.
- Career-first and Relocation-first SearchProfiles are enabled independently.
- Working sources include HH public fallback, RemoteOK, Arbeitnow, Job Bank Canada, EURES, HR.ge, and configured Telegram ingestion. JOBS.GE is temporarily paused after its configured endpoint returned HTTP 410.
- Auto-apply and HH private actions remain off.

## Recently completed

- Added bounded retries for EURES transport failures, including raw
  `ssl.SSLError`, and made source alerts report HTTP status / exception type.
- Added `/parallelsearch on|off|status` and `/relocationroles`.
- Each profile now discovers, scores, stores, and reports results independently.
- Fixed concurrent `JobMatch` inserts with an atomic PostgreSQL upsert.
- Fixed Relocation-first scoring to use `relocation_queries`.
- Added public Arbeitnow Germany discovery with conservative evidence handling.
- Stopped inferring salary from arbitrary description numbers.
- Added safe tracked-branch updates through `./job-agent update`.
- Added Job Bank Canada discovery with separate international eligibility, LMIA, and support evidence.
- Added bounded EURES discovery using the employer cross-border recruitment flag without treating it as visa sponsorship.
- Added explicit Telegram resume import for PDF/DOCX/TXT, plus fact confidence/provenance and overlap review.
- Added persisted Recommendation v2 component breakdown with unknown values
  left unset and displayed in vacancy details.
- Added `/salary`, `/blacklist`, `/scanstatus`, `/cancel`, bounded concurrent discovery, source timings, and persistent manual-scan state.
- Set EURES `Accept-Encoding: identity` after reproducing TLS body-read failure
  with the default compressed response and reading the complete 50-result JSON
  with identity encoding.
- Updated `/targets` to configure all active search profiles by default, with
  explicit `career` and `relocation` scope; `/sources` now shows each profile's
  configured source plan.
- Bounded JOBS.GE and HR.ge detail fetching to six listings per source, with
  conservative pacing and timeouts; tightened role matching and require an
  explicit currency plus monthly period before HR.ge salary enters scoring.
  Partial detail results survive individual request failures; total failure is
  reported to the scan. Scheduled Georgia discovery now uses a six-hour cache;
  manual `/scan` still forces a refresh.
- Processed the owner’s live Georgia scan: EURES returned 16, HR.ge returned 2,
  JOBS.GE returned HTTP 410, and Arbeitnow emitted a transient ReadTimeout.
  The candidate pauses JOBS.GE with its reason visible in `/sources` and adds
  one bounded retry for Arbeitnow transport failures.
- Replaced the mixed-language README with English and Russian entry points,
  aligned changelog headings, refreshed the roadmap, and documented current
  Armenia/Georgia source-access constraints.
- Confirmed the Armenian Unified Social Service lists e-work.am and
  workforall.am as vacancy platforms. Their public search pages timed out;
  API/access terms are unverified, and official registration rules do not yet
  establish pre-move foreign-candidate access.
- Audited public applicant-count signals; connected feeds do not expose reliable candidate-side competition counts.
- Merged release PR #15 into GitHub `main`; CI passed and the owner supplied
  a real-chat smoke test for the core Telegram commands.

## Verified

- Latest full PostgreSQL-backed suite: `233 passed`, 67.67% branch coverage
  (rerun on 2026-10-11; 55% gate).
- Georgia adapter regressions: `5 passed`; a scheduled-cache regression also
  passes. Compilation and `git diff --check` passed. The six-detail cap,
  per-request timeout, inter-request delay, partial-failure behavior and salary
  evidence rules are covered.
- Source-resilience targeted tests: `20 passed`; the full suite includes the
  Arbeitnow retry and source-availability cases.
- Targeted EURES, Job Bank and source-error regressions: `25 passed`.
- GitHub Actions run 110 passed.
- Commit `496c920` and its release are on `main` at merge commit `062eb25`;
  Compose reports source/runtime
  3.5.6, PostgreSQL healthy, schema 4/4, and the bot polling. Mount inspection
  confirms the existing `repo_jobagent_v3_pg` and `repo_jobagent_v3_files`
  volumes remain attached. Startup scan began on HH public fallback, Arbeitnow
  and RemoteOK; no startup errors were present in the inspected log tail.
- Candidate `170ed4e` is pushed to PR #16, passes push and PR CI, and is applied
  to Compose project `repo`. Runtime remains 3.5.6; app is up and PostgreSQL is
  healthy. The startup scan completed successfully. Both Arbeitnow requests,
  EURES searches/details, and HR.ge listing/detail requests returned HTTP 200;
  no JOBS.GE request or source error appeared. Named
  `repo_jobagent_v3_pg` and `repo_jobagent_v3_files` volumes remain attached.
- Owner's follow-up Telegram scan exercised the deployed Arbeitnow retry:
  Relocation-first received a `ReadTimeout`, the single retry returned HTTP
  200, and the supplied log excerpt shows EURES, HR.ge, Job Bank, and HH
  requests succeeding. JOBS.GE was not requested. Telegram handled the update
  in 162.7 seconds; Job Bank's five-second public crawl delay and twelve detail
  requests account for a substantial part, but exact per-source timing needs
  `/scanstatus` to measure.
- EURES now preserves partial results when only some requests fail. Existing PostgreSQL and storage volumes remain attached.
- Polling, schema check, scheduled/manual dual-profile scans, and concurrent scan protection passed locally.
- GitHub PR #15 is merged. PR #16 contains the current EURES/market/docs update;
  push and pull-request CI passed for handoff commit `e43072c`.
- Owner-provided Telegram smoke test on 2026-10-11 confirmed `/salary`,
  `/blacklist`, `/scanstatus`, `/cancel`, `/import` prompt, `/version` and
  `/status`. The scan completed with an EURES error while other sources
  returned results. `/import` file preview/save and Recommendation v2 vacancy
  details still need end-to-end acceptance before release tagging.
- After the safe update, the 2026-10-11 startup scan completed successfully.
  EURES search and detail requests returned HTTP 200 without SSL retry/error
  logs. Continue monitoring subsequent scheduled scans; one successful run
  does not establish the underlying TLS cause.
- Runtime status after update: source/runtime `3.5.6`, app polling, PostgreSQL
  healthy. The existing `repo_jobagent_v3_pg` and `repo_jobagent_v3_files`
  volumes remain attached.

## Current priority

Have the owner confirm the updated `/sources` view shows JOBS.GE as paused and
share `/scanstatus` for the 162.7-second scan, so source timings can guide any
latency work without weakening public-site crawl limits. The live scan already
verified Arbeitnow recovery after a timeout. Continue `/import` preview/save
and Recommendation v2 detail acceptance before tagging v3.5.6.

## Open limitations

- Source coverage remains the main Relocation-first bottleneck, especially Armenia and low-barrier legal work.
- Georgia adapters run only when `GE` is selected for a search profile.
  JOBS.GE's configured homepage returned HTTP 410 and is paused; HR.ge returned
  two live vacancies in the owner’s scan. Its robots file allows `/` and links
  a large sitemap, but recurring reuse permission remains unverified. Armenia
  has no catalog entry or connected local source yet.
- Armenia has two government-listed vacancy platforms (e-work.am and
  workforall.am), but their public pages timed out and no API/access terms were
  verified. Request a permitted feed and confirm foreign-candidate access;
  Staff.am prohibits automated scraping without permission, while Job.am
  restricts unauthorized reuse and redistribution. See
  `docs/developer/INTERNATIONAL_SOURCES.md`.
- Arbeitnow may contain no low-barrier role matches. A later owner-provided
  Telegram scan confirmed the deployed single retry recovered from a
  `ReadTimeout` with HTTP 200. Continue monitoring future runs.
- A later scan update took 162.7 seconds. Supplied logs show twelve Job Bank
  detail requests spaced around the public crawl delay; exact source-level
  timings are still needed before considering latency changes.
- HH is mostly domestic and can return `403`; public fallback is expected, CAPTCHA must not be bypassed.
- EURES's compressed-response TLS failure did not recur in the first complete
  post-update scan using identity encoding. Monitor additional runs; do not
  claim the root cause is permanently resolved yet.
- The EURES cross-border flag is not proof of visa sponsorship, relocation support, or third-country work authorization.
- Public applicant counts are unavailable in the connected candidate-facing feeds and remain unknown.
- Dedicated Career Score and Relocation Score, affordability calculation, migration knowledge base, and application tracker are later phases—not completed features.
- Full remote control of the user's Arch machine exists only in a Codex CLI session started on that machine; cloud Codex cannot access `/home/roma`.

## Update protocol

After every completed stage, update this file—not the entire original long prompt:

1. change `Last updated`;
2. move delivered work into **Recently completed**;
3. replace verification counts/results with evidence from the latest run;
4. keep only unresolved items in **Open limitations**;
5. set exactly one practical **Current priority**;
6. add detailed chronology to `DEVELOPMENT_LOG.md` and durable follow-up items to `TASKS.md`.

Do not put secrets, exact passport data, private employment details, or other sensitive candidate information in this public repository.

## Compact startup request

```text
Read AGENTS.md and docs/PROJECT_OS/BRIEF.md first. Then inspect git status,
the latest commits, and only the detailed PROJECT_OS documents relevant to the
current priority. Verify claims against the code; do not restart or broadly
rewrite the project. Preserve .env, Docker volumes, the database, and dirty
user work. Continue the Current priority with tests. After a completed stage,
update BRIEF.md, DEVELOPMENT_LOG.md, TASKS.md, and HANDOFF.md with verified
facts. Report what changed, checks run, remaining limitations, and the exact
safe local deployment command.
```
