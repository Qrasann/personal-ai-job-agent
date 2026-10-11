# Development Log

## 2026-10-11 — public competition-signal audit
- Reviewed the fields consumed from HH, Job Bank, EURES, Arbeitnow and RemoteOK.
- HH documents response counters for employer-authorized vacancy data; the
  public API request used for discovery currently returns HTTP 403 in this
  environment, and the public HH page parser exposes no applicant count.
- Job Bank explains that applications are shown in the employer's Applicants
  and matches dashboard, not in public vacancy details. EURES `numberOfPosts`
  counts positions rather than applicants. The public Arbeitnow and RemoteOK
  payloads consumed here contain no applicant-count field.
- Closed the v3.5.3 consideration item without adding a fabricated estimate;
  future implementation needs a public per-vacancy count field or an explicitly
  authorized employer integration.

## 2026-10-11 — EURES cross-border discovery (v3.5.4)
- Verified the public EURES search and detail endpoints against live responses.
  The search supports an employer cross-border recruitment flag and returns
  official vacancy detail/application instructions.
- Added a bounded EURES adapter for each active search profile, filtering out
  broad matches whose title does not match the active role query.
- Persisted the EURES flag and evidence URL as international-candidate signals;
  visa sponsorship and relocation support remain unknown.
- Added EURES member-country destinations to country selection and added
  parsing, request, role filter, unknown-support and registry tests.
- Public search/detail endpoints returned HTTP 200. Full isolated PostgreSQL
  suite: 203 passed, 64.39% branch coverage; GitHub Actions run 110 passed.
- Published as `1dc62366fcca46e778d6650928b1fd4c91c2d5cd` and rebuilt Compose
  project `repo`; runtime reports 3.5.4. Startup scan reached EURES search
  successfully. PostgreSQL and existing named storage volumes were preserved.
- A direct standalone `httpx` smoke request experienced a TLS record-layer
  error in the host environment; `curl` endpoint checks and the deployed
  startup search both succeeded. Automated tests cover parsing and detail
  enrichment. Real Telegram chat acceptance remains owner-driven.

## 2026-10-10 — Telegram salary and blacklist controls
- Added `/salary current|desired|minimum <currency> <amount|clear>` and a
  read-only summary; only `minimum` affects matching, preserving the current
  currency-aware scoring behavior.
- Added `/blacklist add|remove|clear` with case-insensitive deduplication and
  synchronization to every active search profile.
- Compared GitHub `testsbuild` with `main`: branches diverged (11 ahead, one
  behind). Saved navigation is already implemented here, so no wholesale
  port was necessary.
- Full isolated PostgreSQL suite: 194 passed, 63.65% branch coverage; initial
  attempt without the test-only postgres service had the expected connection
  failures, then passed once that isolated service was started.
- Local bot is still running v3.5.2 from the prior source stage; this change
  awaits commit, GitHub publication, and rebuild.

## 2026-10-11 — v3.5.3 Fast Scan & Scan Dashboard
- Source discovery now runs through a shared semaphore capped at three
  adapters; the existing priority order still controls sequential matching
  and ingestion, avoiding concurrent database-side notification races.
- Each source discovery has a 180-second bound and records `duration_ms`;
  source errors/timeouts are isolated so successful sources can still finish.
- Added a persistent manual-scan dashboard in `runtime_state`, `/scanstatus`,
  and `/cancel`; cancellation clears the HH reply composer as before.
- Added concurrency, scan progress/status, and cancellation regressions.
- Full isolated PostgreSQL suite: 197 passed, 63.80% branch coverage (55%
  gate). Initial sandboxed attempts could not connect to localhost; the same
  suite passed with the authorized local test database connection.
- Published as `9695c731c8aec59b5be715b89c267fff83ddc7cd`; GitHub Actions run
  105 passed. The local Compose bot was rebuilt and is polling as
  `@roma_job_agent_bot`. The startup scan ran HH public fallback, RemoteOK,
  Arbeitnow, and Job Bank discoveries with overlapping requests; Job Bank
  source/detail responses returned HTTP 200 and the scheduled scan completed
  successfully at 21:04:51 UTC. Existing named volumes were verified.
- Owner-driven real-chat acceptance of `/salary`, `/blacklist`, `/scanstatus`,
  and `/cancel` remains pending before tagging v3.5.2.
- Release metadata `VERSION=3.5.3` is published in commit
  `e4fa198f63d07a5120f6e480b63a7be9cdb46efd`; CI run 108 passed. The bot was
  rebuilt and reports source/runtime 3.5.3. Its new startup scan completed
  successfully at 21:11:40 UTC on 2026-10-10 with Job Bank query/detail HTTP
  200 responses. The v3.5.2 and v3.5.3 release tags both await real-chat
  command acceptance.

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

## 2026-10-11 — compact Codex context
- Replaced the need to paste the original long relocation prompt into every session with a compact, updateable `BRIEF.md`; refreshed stale handoff and smoke-test status.
