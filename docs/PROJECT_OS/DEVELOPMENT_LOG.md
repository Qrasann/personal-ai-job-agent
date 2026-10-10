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
- Added the unauthenticated Arbeitnow Germany API as an international source, including broad-role German aliases and explicit-only visa/relocation signals.
- Live API contract check passed; the current feed contained no matches for the six configured broad roles, which remains a source-coverage limitation rather than a reason to relax relevance scoring.
- A live Arbeitnow notification exposed false salary extraction from arbitrary description numbers; salary fallback is now limited to explicit source salary/card fields, while queue/list views require structured salary data.
- Added root `AGENTS.md` so locally installed Codex starts with the correct repository, deployment, testing, data-safety and dual-search instructions.

## 2026-10-10 — public international source stage
- Audited HEAD `7c987da`, the clean release worktree, running Compose `repo`
  v3.5.2 and healthy PostgreSQL; read all PROJECT_OS documents.
- Validated public Job Bank Canada search/details and its five-second robots
  crawl delay. DWP public search returned a service-error page and was deferred.
- Added bounded international TFW discovery and Canada country selection,
  preserving independent profile queries and source/geography controls.
- Kept explicit eligibility, LMIA status and employer support offers separate;
  stored source URLs and evidence. Missing support remains unknown.
- Prevented decimal CAD/hour source text from entering the integer/USD salary
  fallback; no monthly salary or support claim is fabricated.
- Added parsing, refusal, eligibility, evidence, crawl-delay and independent
  profile/source-control regressions. Live adapter check found one warehouse
  worker vacancy open to international candidates with requested LMIA and
  unknown sponsorship; no data was ingested by this standalone check.
- Created local .venv and used the isolated PostgreSQL tmpfs test service.
- Final full suite: 191 passed, 64.16% branch coverage (55% gate); Python
  compilation and `git diff --check` passed. GitHub Actions CI run 102 passed.
- Rebuilt local Compose `repo`; runtime is v3.5.2, polling works, both search
  profiles remain active, and existing named PostgreSQL/storage volumes were
  preserved. Startup scan including Job Bank finished successfully at 20:44:49
  UTC. Changes remain uncommitted and unpublished; HEAD is `7c987da`.
