# Current State

## Latest state
- branch: `feature/v3.5.2-dual-search-modes`
- local and GitHub head: `ad81a21d3273eee1f659b9b8ff1360e2e5b4ae6a`
- tracked release version: 3.5.3; feature branch is deployed pending real-chat
  command acceptance and release tag.
- local Compose project `repo`: app polling as `@roma_job_agent_bot`; PostgreSQL
  healthy; original `repo_jobagent_v3_pg` and `repo_jobagent_v3_files` volumes
  preserved.
- Telegram `/salary` supports current, desired and minimum values by currency;
  minimum remains connected to scoring.
- Telegram `/blacklist` supports case-insensitive add/remove/clear across active
  Career-first and Relocation-first profiles.
- Latest PostgreSQL-backed suite: 197 passed, 63.80% branch coverage (55% gate).
- v3.5.3 Fast Scan & Scan Dashboard: source discovery is bounded to three
  concurrent adapters; manual scans persist status/timings in `runtime_state`
  and expose `/scanstatus` and `/cancel`.

## Stable baseline
- main: v3.5.1
- baseline commit: 6f73110324fdf657f6695c25a5af540d2a94e72f
- testsbuild: experimental branch; at restart it was 11 commits ahead and 0 behind main.

## Active development
- target: v3.5.3 Fast Scan & Scan Dashboard acceptance

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
- Manual Telegram `/scanstatus`, `/cancel`, `/salary` and `/blacklist` commands
  still need an owner-driven real-chat acceptance. No real-chat test message
  was sent from this session.

## Merge rule
main remains the stable source until full CI and manual Telegram smoke tests pass.
