# Current State

## Stable baseline
- main: v3.5.1
- baseline commit: 6f73110324fdf657f6695c25a5af540d2a94e72f
- testsbuild: experimental branch; at restart it was 11 commits ahead and 0 behind main.

## Active development
- branch: feature/v3.5.2-dual-search-modes
- target: v3.5.2 Search Control Center

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

## Verified in the current development environment
- Parent feature baseline: 166 passed with isolated PostgreSQL 16, 62.57% branch coverage.
- Previous dual-mode suite: 173 passed with isolated PostgreSQL 16, 62.84% branch coverage.
- Full parallel-profile suite: 175 passed with isolated PostgreSQL 16, 63.22% branch coverage.
- Python compilation, `git diff --check` and repository-history secret scan passed.
- Manual Telegram smoke test is still pending because this environment has no bot token.

## Merge rule
main remains the stable source until full CI and manual Telegram smoke tests pass.
