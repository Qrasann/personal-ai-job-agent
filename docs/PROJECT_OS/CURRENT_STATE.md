# Current State

## Latest state
- Stable GitHub `main` contains source version v3.5.6; PRs #15 and #16 are
  merged. Deployed application code is `170ed4e`; later commits in PR #16
  updated documentation. Merge CI run `38135649948` passed.
- `README.md` and `README.ru.md` provide English and Russian entry points on
  `main`. The merged v3.5.6 feature branch is inactive. Current work is on
  `feature/v3.5.7-international-market-coverage`, based on main `02f582e`.
- Latest formal GitHub Release/tag: v3.5.6, pointing to release commit
  `50afdab`. Changelog entries v3.5.2–v3.5.5 are cumulative milestones
  included in the release. Main CI run `38138941745` passed.
- Bilingual GitHub Release: https://github.com/Qrasann/personal-ai-job-agent/releases/tag/v3.5.6.
- local Compose project `repo` runs source/runtime 3.5.6; app is polling and
  PostgreSQL is healthy.
- the startup dual-profile scan completed successfully after the latest update.
  Arbeitnow, EURES, and HR.ge requests returned HTTP 200; no JOBS.GE request or
  source failure appeared. Existing named PostgreSQL/storage volumes remain
  attached.
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
- latest full PostgreSQL-backed suite: 233 passed, 67.67% branch coverage
  (55% gate).
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
  v3.5.6 remains the latest formal release and includes the untagged
  v3.5.2–v3.5.5 milestones.
- Job Bank is the measured latency bottleneck at 99.5 seconds. Preserve its
  five-second request pacing while evaluating any optimization.

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
- The owner has completed the Telegram acceptance required for cumulative
  release v3.5.6; no v3.5.7 source or runtime change has been made yet.

## Merge rule
main remains the stable source until full CI and manual Telegram smoke tests pass.
