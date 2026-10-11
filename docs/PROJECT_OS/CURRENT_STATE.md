# Current State

## Latest state
- stable GitHub `main`: `6294c2a` (source version 3.5.6). PR #15 is merged.
- active candidate branch: `feature/v3.5.6-eures-identity-market-targets` at
  `e43072c` (application change `6fa3406`), published as PR #16; push and
  pull-request CI passed for this branch head.
- local Compose project `repo` runs source/runtime 3.5.6 from the candidate;
  the app is polling and PostgreSQL is healthy.
- after the candidate update, the startup dual-profile scan completed
  successfully. EURES search and detail requests returned HTTP 200 without the
  previous SSL retries/errors.
- local Compose project `repo`: app polling as `@roma_job_agent_bot`; PostgreSQL
  healthy; original `repo_jobagent_v3_pg` and `repo_jobagent_v3_files` volumes
  preserved.
- Telegram `/salary` supports current, desired and minimum values by currency;
  minimum remains connected to scoring.
- Telegram `/blacklist` supports case-insensitive add/remove/clear across active
  Career-first and Relocation-first profiles.
- latest full PostgreSQL-backed suite: 224 passed, 66.33% branch coverage
  (55% gate).
- GitHub Actions runs `38121905782` (push) and `38121908521` (PR) passed.
- Public competition-data audit found no per-vacancy applicant counts in the
  connected public feeds; employer-only counts remain unknown in this app.
- v3.5.3 Fast Scan & Scan Dashboard: source discovery is bounded to three
  concurrent adapters; manual scans persist status/timings in `runtime_state`
  and expose `/scanstatus` and `/cancel`.

## Stable baseline
- GitHub `main` HEAD: v3.5.6 at `6294c2a`.
- PR #15 merge commit: `062eb253bdf8435782e5fcca6cfb1257b271ea86`.

## Active development
- target: owner verifies `/targets relocation GE`, `/sources` and `/scan` on the
  updated bot, then completes `/import` preview/save and Recommendation v2
  vacancy detail acceptance before release tagging. Core command entry points
  and `/status`/`/version` were already smoke-tested.

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
  migration OK), and `/status` (ACTIVE). The reported scan completed; EURES
  failed while HH, RemoteOK, Arbeitnow and Job Bank returned results. No
  resume file was uploaded and no Recommendation v2 vacancy details were shown.
- EURES now requests identity-encoded responses. A direct live check showed
  compressed response reads failing while identity encoding returned a complete
  50-result response. The first post-update scan showed successful EURES search
  and detail requests; continue monitoring subsequent runs.
- The updated `/targets` applies markets to all active profiles by default and
  supports explicit `career`/`relocation` scope. `/sources` lists plans per
  active profile. The owner still needs to set GE and confirm it in Telegram.
- The v3.5.6 release tag remains pending owner checks for `/import` preview/save
  and Recommendation v2 vacancy details. GitHub's latest published tag remains
  v3.5.1.

## Merge rule
main remains the stable source until full CI and manual Telegram smoke tests pass.
