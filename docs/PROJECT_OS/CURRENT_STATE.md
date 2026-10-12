# Current State

## Latest state
- **2026-10-12 — AM/GE manual search links:** the current candidate adds
  selected-market clickable links for ITA Jobs, Staff.am, Job.am,
  CareerCenter.am, Findjobs.ge and LeverX Careers. They are marked manual,
  excluded from toggles and never scanned. Findjobs.ge terms require written
  permission for repeated/systematic substantial extraction. Commit `ffabb1b`.
  Local tests: 432 passed, 3 skipped; isolated PostgreSQL: 435 passed;
  compileall, secret scan and diff check pass. Compose startup scan completed
  at 18:06:12 UTC; runtime 3.5.7 and PostgreSQL healthy, with no manual portal
  requests. Owner Telegram acceptance remains pending.
- **2026-10-12 — HeadHunter destination search:** commit `61fe39d` adds
  country-scoped public HH searches across the current and selected markets.
  Verified from HH's public area catalog: RU `113`, GE `28`; Armenia is not
  listed and no area is guessed. Per-profile role queries and bounds are
  preserved, cross-area duplicates are removed, and country metadata follows
  the area-scoped request. Local tests: 430 passed, 3 skipped; isolated
  PostgreSQL: 433 passed; compileall, secret scan, and diff check pass. Compose
  was rebuilt; startup scan completed at 17:56:41 UTC, HH public-web fallback
  returned HTTP 200 for areas 28 and 113, and PostgreSQL is healthy. Telegram
  acceptance remains pending. Bootstrap defaults are commit `00f1f0d`.
- **2026-10-12 — Independent vacancy review:** Added scoped `/jobs
  career|relocation [below]`, `/job <id> career|relocation` and
  `/compare <id> career|relocation`. Each direction retains its own scores and
  thresholds, including through detail/comparison callbacks; the card names
  the profile. User ownership is checked together with job and profile ids.
  Fixed `hotel staff` being treated as Senior solely because of `staff`;
  technical Staff roles, explicit Senior/Lead/Principal, experience, management
  and user exclusions remain restricted. Full unit suite: 319 passed, 3
  database-dependent tests skipped; all 3 repository integration tests passed
  against isolated PostgreSQL. Compilation and diff checks passed. Local
  rebuild completed at 01:36 Moscow; source/runtime report 3.5.7, app is up
  and PostgreSQL healthy. Startup source requests succeeded in the inspected
  window and `scan_all` completed at 01:37:50 Moscow. Telegram acceptance of
  the new commands remains pending. The
  roadmap identifies v3.5.7 as the active international-coverage stage.
  Useful lower-barrier AM/GE coverage remains open. No score inflation,
  threshold reduction or publication.
- **2026-10-12 Moscow — Remotive remote-source stage:** the active local
  worktree adds the official Remotive Devops public feed, shared
  across profiles and active users with a once-per-24-hour cache persisted in
  the existing `runtime_state` table. It preserves source location scope,
  rejects clear country-only mismatches, links back to Remotive, and does not
  infer numeric salary, visa, relocation, or country eligibility. The `/jobs`
  renderer shows Remotive attribution, including when a canonical vacancy also
  appears on Himalayas. The API ignored the tested category filters and
  returned a broad response, so the worktree uses the official category RSS
  feed at `https://remotive.com/remote-jobs/devops/feed` and a v3 cache key.
  Targeted Remotive/cache tests: 17 passed; full local suite: 286 passed, 3
  database-dependent tests skipped; all 3 repository PostgreSQL integration
  tests passed; `compileall` and `git diff --check` passed. Added `/jobs below`
  for manual review of nonzero results below the configured threshold; it
  leaves scores, notifications, threshold, and descending priority unchanged,
  and states that legal work/relocation eligibility needs confirmation. The RSS
  endpoint returned HTTP 200 but no `<item>` entries, so both profiles parsed
  0 jobs. That valid empty response is cached for 24 hours. Compose `repo` was
  rebuilt at 01:15 Moscow; source/runtime report 3.5.7, PostgreSQL is healthy,
  and the app is polling. The startup scan began immediately after the scheduler
  grace fix. Telegram acceptance of `/jobs below` is pending. No
  commit, push, tag, release, or merge was made. Keep the next stage focused on useful
  Relocation-first results while retaining score order,
  the 65-point threshold, independent profiles, and evidence-based eligibility.
- Stable GitHub `main` contains source version v3.5.6; PRs #15 and #16 are
  merged. Deployed application code is `170ed4e`; later commits in PR #16
  updated documentation. Merge CI run `38135649948` passed.
- The active feature branch is `feature/v3.5.7-international-market-coverage`,
  candidate version 3.5.7. HEAD is `d445c87`; uncommitted changes include
  Job Bank partial-result resilience and minimum-interval pacing, plus
  explicitly remote-work priority in both independent search profiles, a
  bounded Himalayas remote API adapter, a curated Collectly Lever public feed,
  salary-period display, source attribution, and explicit geography guidance
  in remote vacancy details.
  The owner verified `/sources`, `/scan`, `/scanstatus`, and `/jobs`: Himalayas
  returned 20 cached remote jobs and placed them first with source links;
  Job Bank returned 12 in 71.2 seconds and EURES 16 in 34.1 seconds. Full
  local suite before the new Lever connector: 267 passed, 3 skipped; isolated
  PostgreSQL suite: 270 passed; compile and diff checks passed. The owner
  verified `/job 1273` at 20:56 Moscow time: worldwide scope is attributed to
  Himalayas and the card says the employer must confirm hiring from the user's
  country; the vacancy has no salary.
  The earlier Recommendation v2 code commit `8a583c7` passed push CI
  `38151840822` and PR CI `38151843490`. PR #18 is an open draft against
  `main`; no merge or v3.5.7 tag/release has been made. The owner confirmed the
  Telegram result at 18:42 Moscow time: `/job 1091` showed Technical 42 and
  interview risk 58 with mandatory-skill coverage and `fit=good`. This is a
  matching-gap indicator, not a calibrated probability.
- Latest published PR #18 checks are green for Python, secret scan, and Docker
  build in runs `38152993495` and `38152990522`. They cover the published PR
  head, not the current uncommitted Job Bank and remote-priority changes.
- `README.md` and `README.ru.md` provide English and Russian entry points on
  `main`. The merged v3.5.6 feature branch is inactive. Current work is on
  `feature/v3.5.7-international-market-coverage`, based on main `02f582e`.
- Latest formal GitHub Release/tag: v3.5.6, pointing to release commit
  `50afdab`. Changelog entries v3.5.2–v3.5.5 are cumulative milestones
  included in the release. Main CI run `38138941745` passed.
- Bilingual GitHub Release: https://github.com/Qrasann/personal-ai-job-agent/releases/tag/v3.5.6.
- Local Compose project `repo` reports runtime 3.5.7; the app is up and
  PostgreSQL is healthy. After adding the curated Collectly Lever connector,
  it was rebuilt from the current worktree at 21:04 Moscow time. Startup
  `scan_all` completed successfully at 18:06:21 UTC (21:06:21 Moscow). Lever
  returned HTTP 200 for both independent profiles; Himalayas GE/AM, EURES, Job
  Bank, HR.ge, Greenhouse, and HH public search also returned successful
  responses in the inspected log window. HH API 403 recovered through its
  ordinary public-web fallback. Existing PostgreSQL remained healthy and
  attached; the rebuild reused the existing service and volumes.
- The owner verified `/sources`, `/scan`, and `/scanstatus` in Telegram at
  21:11–21:14 Moscow time. Lever is enabled for Career-first and Relocation-
  first and returned 1 live vacancy in 9.6 seconds. The manual scan completed
  at 18:14:01 UTC (21:14:01 Moscow): 266 processed, 37 Good, 33 Stretch, 196
  filtered, 0 new notifications. Job Bank returned 12 in 71.4 seconds; EURES
  returned 16 in 55.2 seconds; no source error is visible in the supplied log
  excerpt. A read-only lookup found Collectly as job #1333, but the Career-first
  profile saved it as `filtered` with score 0 because `senior devops` is in that
  profile's explicit exclusions. This is a profile filter, not a Lever failure;
  do not change the exclusion without the owner's choice. `/jobs` only shows ten
  latest useful matches, so its omission was expected for this filtered row.
- At 21:20 Moscow time the owner supplied `/review` and `/stretch` results.
  Their first cards were remote CloudCops (88, Good) and Sporty Group (72,
  Stretch); the latter's posting says applicants must be based in Europe, Asia,
  or LATAM. This confirms remote opportunities are visible in both queues, but
  source-batch ordering is verified by regression tests rather than those queue
  displays. The same scan reported Relocation-first 74 processed, 0 Good, and
  0 Stretch. The profile's configured threshold is 65; saved lower-barrier and
  remote matches remain below it (an inspected remote result scored 54 and was
  filtered). This is a scoring/visibility limitation, not a source outage.
- The owner clarified that higher-rated vacancies should have higher priority.
  `/review`, `/stretch`, and `/saved` already sorted descending by score, but
  `/jobs` used creation time. `/jobs` now sorts score descending, breaks ties
  by recency, and labels the list “Совпадения по рейтингу”. The threshold stays
  at 65; below-threshold jobs will not be promoted ahead of higher-rated jobs.
  A PostgreSQL regression covers an older 86-point result versus a newer
  72-point result.
- At 23:27 Moscow time, the owner confirmed the live `/jobs` list is now
  descending: CloudCops 88, SIL International 84, Canonical 82, followed by
  results at 78 and below. The supplied scheduled-scan log completed at
  20:25:14 UTC (23:25:14 Moscow). Its visible EURES, Job Bank, Arbeitnow,
  Remote OK and Greenhouse requests returned HTTP 200; no source error appears
  in the supplied excerpt.
- GitHub was checked directly: latest formal Release/tag is v3.5.6; the visible
  tags are v3.5.0, v3.5.1, and v3.5.6. Changelog milestones v3.5.2–v3.5.5
  have no separate tags/releases. PR #18 remains open and draft against `main`.
  The active local branch is still `feature/v3.5.7-international-market-coverage`
  (`VERSION=3.5.7`) with uncommitted changes; no commit, tag, or publication
  was made.
- Latest full verification for this worktree: 267 passed, 3 DB tests skipped
  locally before Lever; after the Lever adapter, 274 passed and 3 DB tests
  skipped locally, including the timezone-detail regression. `compileall` and
  `git diff --check` passed. PostgreSQL tests were not rerun because this
  change adds a read-only source adapter and does not change persistence or
  schema.
- After the score-ordering change, the local suite passes 274 tests with 3
  database tests skipped; the isolated PostgreSQL suite passes all 277 tests.
  `compileall` and `git diff --check` pass. Compose `repo` was rebuilt at 21:38
  Moscow time; source/runtime versions both report 3.5.7 and PostgreSQL is
  healthy. Startup scan completed at 18:40:25 UTC (21:40:25 Moscow); the
  inspected source requests succeeded, with HH API 403 recovering through its
  ordinary public-web fallback.
- Earlier candidate verification: the safe updater rebuilt the feature branch;
  read-only mount inspection
  confirms `repo_jobagent_v3_pg` and `repo_jobagent_v3_files` remain attached.
  Startup `scan_all` completed at 13:31:05 UTC; EURES returned HTTP 200 and no
  errors appeared in the inspected tail. The owner later confirmed Greenhouse
  returned HTTP 200 for Relocation-first GE/AM but matched no jobs because its
  selected role queries are non-technical. The subsequent Career-first GE/AM
  scan returned one Lineate Infrastructure Engineer vacancy explicitly marked
  GE (67/100); work mode was unknown. The owner reopened `/job 1091` after the
  decoder fix and confirmed the description is readable; unsupported salary,
  work-mode, visa and relocation facts remain unknown.
- Owner's later Telegram scan confirmed Arbeitnow retry recovery after a
  `ReadTimeout` (retry returned HTTP 200). Supplied logs show EURES, HR.ge, Job
  Bank, and HH requests succeeding; the Telegram update took 162.7 seconds.
  `/scanstatus` attributes 99.5 seconds to Job Bank, 17.1 to Arbeitnow, 14.5
  to EURES, 13.0 to HR.ge, 7.6 to HH, and 1.5 to Remote OK.
- Owner confirmed `/sources` marks JOBS.GE paused after HTTP 410. The completed
  scan returned HH 209, Remote OK 3, Arbeitnow 2, Job Bank 12, EURES 16, and
  HR.ge 2. Later log tail shows scheduled `scan_all` completed and Telegram
  updates were handled within 117–677 ms, with no errors in the excerpt.
- Owner completed the final Telegram release checks: `/import` rejected ZIP,
  recognized duplicate resumes and saved TXT resume #6 after confirmation
  (zero facts proposed); `/job 580` rendered Recommendation v2 and left
  unsupported dimensions unknown. The supplied latest log tail shows
  `scan_all` completed successfully at 12:12:59 UTC.
- local Compose project `repo`: app polling as `@roma_job_agent_bot`; PostgreSQL
  healthy; original `repo_jobagent_v3_pg` and `repo_jobagent_v3_files` volumes
  preserved.
- Telegram `/salary` supports current, desired and minimum values by currency;
  minimum remains connected to scoring.
- Telegram `/blacklist` supports case-insensitive add/remove/clear across active
  Career-first and Relocation-first profiles.
- Latest full isolated PostgreSQL suite: 257 passed, 68.59% branch coverage
  (55% gate); the local suite passes 254 with three database tests skipped;
  targeted Job Bank and preference tests pass 34.
  Compile and diff checks passed. The owner reopened `/job 1091`
  after the singular-heading fix and reported Technical 42 with interview risk
  `н/д`. Recommendation v2 was independently scoring the raw stored HTML while
  Technical used decoded text. Commit `8a583c7` passes the same normalized
  description to both paths; its regression expects Technical 42 and risk 58
  for the encoded Lineate posting. Push CI `38151840822` and PR CI
  `38151843490` passed; deployment, startup scan, and Telegram acceptance are
  complete. The owner confirmed Technical 42 and risk 58; the score is not a
  calibrated probability.
  Job Bank now continues across individual search/detail transport failures and
  preserves successfully verified vacancies; it keeps the one-retry budget,
  five-second minimum spacing between serialized request starts. The full database-backed suite
  covers partial recovery and all-detail failure. The owner supplied a fresh
  Telegram `/scan` and `/scanstatus` at 19:33–19:36 Moscow time: Job Bank
  returned 12 vacancies in 100.7 seconds, and the supplied log excerpt shows
  detail requests returning HTTP 200 without a Job Bank warning. This confirms
  a healthy normal run; no transport failure occurred to exercise partial
  recovery live.
- PR #16 push/PR checks `38135381779` and `38135384930` passed; merge commit
  CI run `38135649948` passed.
- Public competition-data audit found no per-vacancy applicant counts in the
  connected public feeds; employer-only counts remain unknown in this app.
- Official-source review found Armenia's `workpermit.am` employer-side
  foreign-hiring process and EAEU permit exemption; no public discovery feed or
  anonymous jobseeker flow is verified. Georgia's foreign-worker right-to-work
  changes are in force from 2026-03-01.
- Owner Telegram example showed a 90,000 RUB internship description although
  the configured minimum is 100,000 RUB. The app currently treats minimum
  salary as a scoring input, not a strict exclusion, and does not parse that
  description amount into structured salary fields. The `/salary` wording is
  misleading and needs a separate decision/test.
- v3.5.3 Fast Scan & Scan Dashboard: source discovery is bounded to three
  concurrent adapters; manual scans persist status/timings in `runtime_state`
  and expose `/scanstatus` and `/cancel`.

## Stable baseline
- GitHub `main` and the cumulative formal release: v3.5.6; tag target
  `50afdab`.
- PR #15 merge commit: `062eb253bdf8435782e5fcca6cfb1257b271ea86`.
- PR #16 merge commit: `874b37255e3bb223d2b49d83027f15b48acfe7c4`.

## Active development
- `main` is stable; the active candidate is
  `feature/v3.5.7-international-market-coverage`, branched from `02f582e`.
  Candidate `VERSION` and local Compose runtime are 3.5.7; v3.5.6 remains the
  latest version on `main` and the formal release. The v3.5.2–v3.5.5
  milestones remain cumulative entries within v3.5.6.
- Job Bank previously took 99.5 seconds; a Relocation-first scan lost the
  source after a `ConnectTimeout` at 29.2 seconds. The candidate now retains
  unaffected results and enforces a five-second minimum between request starts
  without an unnecessary extra delay after slow responses. Evaluate actual
  latency in Telegram; do not parallelize or increase request volume.

## Implemented on active branch
- enable/disable implemented job sources;
- per-source priority;
- multi-country selection and country priority;
- current city + selected cities + other cities + other countries + worldwide scope;
- relocation / visa / work permit / relocation package / immigration support policies;
- policies: any, prefer, require, exclude;
- generic pre-filter and processing priority before matching;
- button-driven Telegram Search Control Center;
- backward-compatible storage in SearchProfile.settings;
- unit tests for the preference engine.
- explicit `career_first`, `relocation_first` and `balanced` strategies;
- separate career and relocation discovery query lists, combined only in balanced mode;
- conservative relocation ordering: evidence raises priority, missing evidence remains unknown;
- explicitly remote vacancies receive a processing-priority bonus in both
  independent search profiles; this does not alter Match Score or assert that
  unknown geographic scope means worldwide eligibility;
- Telegram strategy selector and `/relocationroles` command.
- opt-in `/parallelsearch on|off|status` for independent Career-first and Relocation-first SearchProfiles;
- per-profile discovery, filtering, ordering, counters and matching in one scan;
- idempotent profile creation that preserves legacy profile IDs and saved relocation settings.
- strategy-aligned role scoring, so Relocation-first vacancies are evaluated against `relocation_queries` rather than the career role list.
- public Arbeitnow Germany discovery with English-to-German aliases for configured broad roles and conservative visa/relocation evidence extraction.
- public Job Bank Canada international TFW discovery with separate eligibility,
  LMIA status and explicit support evidence; Canada country selection.
- public EURES discovery restricted to employer-flagged cross-border vacancies;
  its recruitment flag never implies visa or relocation support.
- v3.5.7 candidate adds selectable Armenia (`AM`) and a public Greenhouse
  adapter for Lineate, scoped to profiles targeting Armenia or Georgia and
  filtered by role query and explicit listing location. The owner verified a
  live Career-first Georgia match. Visa and relocation stay unknown without
  direct evidence; inspect the Telegram detail card before release acceptance.

## Verified in the current development environment
- Parent feature baseline: 166 passed with isolated PostgreSQL 16, 62.57% branch coverage.
- Previous dual-mode suite: 173 passed with isolated PostgreSQL 16, 62.84% branch coverage.
- Full parallel-profile suite: 175 passed with isolated PostgreSQL 16, 63.22% branch coverage.
- Strategy-aligned scoring suite: 176 passed with isolated PostgreSQL 16.
- Python compilation, `git diff --check` and repository-history secret scan passed.
- Local manual Telegram smoke test passed for v3.5.2 startup, schema 2/2, parallel profile activation and dual-profile `/scan`.
- Job Bank source-stage verification and publication are recorded in
  DEVELOPMENT_LOG.md and HANDOFF.md.
- Job Bank source-stage full suite: 191 passed against isolated PostgreSQL 16,
  64.16% branch coverage (55% gate).
- Local Compose `repo` was rebuilt from the source-stage worktree; both profiles
  remained active and the startup scan including Job Bank completed successfully.
- Current fast-scan startup completed successfully at 21:04:51 UTC on 2026-10-10;
  public HH web fallback, RemoteOK, Arbeitnow, Job Bank searches and Job Bank
  detail fetches returned successfully. GitHub CI run 105 passed.
- Owner-provided real-chat smoke test confirmed `/salary`, `/blacklist`,
  `/scanstatus`, `/cancel`, `/import` prompt, `/version` (3.5.6, schema 4/4,
  migration OK), and `/status` (ACTIVE). Later acceptance covered a TXT resume
  import and Recommendation v2 vacancy details; see the latest state above.
- EURES now requests identity-encoded responses. A direct live check showed
  compressed response reads failing while identity encoding returned a complete
  50-result response. The first post-update scan showed successful EURES search
  and detail requests; continue monitoring subsequent runs.
- The updated `/targets` applies markets to all active profiles by default and
  supports explicit `career`/`relocation` scope. `/sources` lists plans per
  active profile. Owner has confirmed Relocation-first targets GE and reported
  a live scan; the follow-up pauses JOBS.GE after HTTP 410 and retries one
  transient Arbeitnow transport failure. A subsequent owner Telegram log
  confirms retry recovery; exact source timings remain pending `/scanstatus`.
- The owner completed Telegram acceptance for cumulative release v3.5.6.
  The v3.5.7 feature candidate now has source changes; its full test suite,
  CI, deployment and Telegram acceptance remain outstanding.

## Merge rule
main remains the stable source until full CI and manual Telegram smoke tests pass.
