# Development Log

## 2026-10-10 — v3.5.2 restart
- Confirmed main is v3.5.1 at 6f73110324fdf657f6695c25a5af540d2a94e72f.
- Confirmed the experimental branch is testsbuild.
- At restart testsbuild was 11 commits ahead and 0 behind main.
- Created feature/v3.5.2-search-control from main.
- Added configurable sources, geographic scope/priorities and relocation policies.
- Added PROJECT_OS handoff documentation.

## 2026-10-10 — dual search strategies
- Audited the supplied private context against live Git; no private candidate data was copied into the repository.
- Confirmed `feature/v3.5.2-search-control` now contains real implementation commits and used it as the parent instead of recreating Search Control.
- Added `career_first`, `relocation_first` and `balanced` strategies in `SearchProfile.settings` without a schema migration.
- Added a separate `relocation_queries` list and conservative evidence-based ordering.
- Added Search Control UI and `/relocationroles` plus unit tests.

## 2026-10-10 — parallel search profiles
- Added idempotent Career-first and Relocation-first SearchProfile configuration.
- Added `/parallelsearch on|off|status`; activation is explicit to avoid surprising broad searches.
- Refactored scan discovery to honor each active profile's queries, sources, geography and ordering independently.
- Restricted matching from each discovery pass to its originating SearchProfile while preserving separate JobMatch rows.
- Added aggregate and per-profile scan summaries plus unit and PostgreSQL integration coverage.
- Reproduced a production `uq_job_profile_search` race from local logs and made `save_match` an atomic PostgreSQL upsert.

## 2026-10-10 — local v3.5.2 smoke test
- Deployed commit `9007824` against the preserved v3.5.1 PostgreSQL volume and verified schema 2/2, polling and a successful scheduled scan.
- Enabled Career-first and Relocation-first profiles and completed a manual dual-profile `/scan` without concurrency errors.
- The live result exposed that relocation discovery used `relocation_queries` while scoring still used only career `queries`; aligned scoring with the active strategy and added regression coverage.
- Made `./job-agent update` follow the checked-out branch's configured upstream instead of refusing every non-main release branch; detached or untracked branches and dirty worktrees remain protected.
