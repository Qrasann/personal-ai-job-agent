# Current State

## Latest state
- branch: `main` at merge commit `062eb25` (PR #15); source/runtime version
  3.5.6. PR #15 is merged and the main branch now contains the release.
- local Compose project `repo`: source/runtime 3.5.6; app container is up and
  PostgreSQL is healthy. The latest scheduled scan completed despite an EURES
  SSL record-layer failure on one profile.
- local Compose project `repo`: app polling as `@roma_job_agent_bot`; PostgreSQL
  healthy; original `repo_jobagent_v3_pg` and `repo_jobagent_v3_files` volumes
  preserved.
- Telegram `/salary` supports current, desired and minimum values by currency;
  minimum remains connected to scoring.
- Telegram `/blacklist` supports case-insensitive add/remove/clear across active
  Career-first and Relocation-first profiles.
- v3.5.6 full PostgreSQL-backed suite: 220 passed, 65.66% branch coverage.
- GitHub Actions runs `38121905782` (push) and `38121908521` (PR) passed.
- Public competition-data audit found no per-vacancy applicant counts in the
  connected public feeds; employer-only counts remain unknown in this app.
- v3.5.3 Fast Scan & Scan Dashboard: source discovery is bounded to three
  concurrent adapters; manual scans persist status/timings in `runtime_state`
  and expose `/scanstatus` and `/cancel`.

## Stable baseline
- main: v3.5.6
- release merge commit: `062eb253bdf8435782e5fcca6cfb1257b271ea86`

## Active development
- target: owner-driven end-to-end acceptance for `/import` file preview/save
  and Recommendation v2 vacancy details before release tagging. The owner has
  already smoke-tested the command entry points and `/status`/`/version`.

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
- v3.5.6 is running in Compose project `repo`; the latest logs include EURES
  SSL retries and a source failure after bounded retries, while the scheduled
  scan completed. Existing named volumes remain attached.

## Merge rule
main remains the stable source until full CI and manual Telegram smoke tests pass.
