# Tasks

## v3.5.6 candidate maintenance — EURES and target markets
- [x] Reproduce EURES TLS body-read failure with default compressed encoding
  inside the running container; verify that identity encoding reads the full
  50-result JSON response.
- [x] Add `Accept-Encoding: identity` to EURES and cover it with a regression
  test.
- [x] Make `/targets` apply countries to all active search profiles by default;
  support explicit `career` and `relocation` scopes.
- [x] Make `/sources` list each active profile's configured source plan.
- [x] Replace the mixed-language root README with linked English and Russian
  versions; align changelog headings and refresh the roadmap/source review.
- [x] Full isolated PostgreSQL suite: 224 passed; branch coverage 66.33%.
- [x] Push `6fa3406` to GitHub branch
  `feature/v3.5.6-eures-identity-market-targets` and pass GitHub CI.
- [x] Publish follow-up handoff commit `e43072c`; push and PR CI passed.
- [x] Apply the candidate through `JOB_AGENT_COMPOSE_PROJECT=repo ./job-agent
  update`; verify polling, healthy PostgreSQL, and unchanged
  `repo_jobagent_v3_pg` / `repo_jobagent_v3_files` volumes.
- [x] Verify the first post-update startup scan completed successfully; EURES
  search and detail requests returned HTTP 200 with no SSL retry/error.
- [x] Review Georgia robots endpoints: JOBS.GE returns 410 (no rules); HR.ge
  allows `/` and publishes a sitemap. Do not treat robots guidance as reuse
  permission; no explicit recurring-extraction permission was verified.
- [x] Bound JOBS.GE/HR.ge to six details per source, 15-second request timeout,
  and two-second pacing; preserve partial results and report total detail
  failure. Tighten role matching and require explicit currency plus a monthly
  period before HR.ge salary is structured for scoring. Cache scheduled
  Georgia results for six hours; manual `/scan` remains a force refresh.
- [x] Add Georgia source regressions and run the full isolated PostgreSQL suite:
  230 passed, 67.46% branch coverage; compileall and diff check passed.
- [x] Push commits `2963705` and `0110173` to PR #16; latest push CI
  `38127150025` and PR CI `38127152783` passed. Apply with the safe updater
  and verify the completed startup scan, EURES HTTP 200 responses, healthy
  PostgreSQL, and attached existing volumes.
- [x] Owner ran `/targets relocation GE`, `/sources`, and `/scan`; EURES found
  16 vacancies, HR.ge found 2, JOBS.GE returned HTTP 410, and Arbeitnow had a
  transient `ReadTimeout`.
- [x] Pause JOBS.GE in the source plan after its configured homepage returned
  HTTP 410; keep it visible in `/sources` with the reason.
- [x] Add one retry for Arbeitnow transport failures and cap its request timeout
  at 15 seconds; do not retry HTTP status responses.
- [x] Full isolated PostgreSQL suite after the source changes: 233 passed,
  67.67% branch coverage; `compileall` and `git diff --check` passed.
- [x] Publish `170ed4e` to PR #16; push CI `38129138392` and PR CI
  `38129141546` passed.
- [x] Clarify in the English/Russian README and changelog that `main` source
  version v3.5.6 and changelog milestones v3.5.2–v3.5.6 are distinct from the
  latest formal GitHub Release/tag, v3.5.1. Do not tag v3.5.6 before owner
  acceptance.
- [x] Push current branch handoff and README clarification in PR #16; latest
  push CI `38129983586` passed.
- [x] Merge PR #16 into `main` after candidate CI and owner source/scan checks;
  merge commit `874b372`, PR push/PR CI `38135381779` / `38135384930`, and main
  CI `38135649948` passed. `README.md` and `README.ru.md` are now both on main.
- [x] Apply through the safe updater; verify runtime 3.5.6, active app,
  healthy PostgreSQL, completed startup scan, and attached existing named
  PostgreSQL/storage volumes. Logs show Arbeitnow, EURES, and HR.ge HTTP 200s;
  JOBS.GE was not requested and no source error appeared.
- [x] Owner supplied a post-deploy Telegram scan log: Arbeitnow's single retry
  recovered from `ReadTimeout` with HTTP 200; EURES, HR.ge, Job Bank, and HH
  requests in the excerpt succeeded; JOBS.GE was not requested. Telegram
  handled the update in 162.7 seconds.
- [x] Owner confirmed `/sources` visibly marks JOBS.GE paused and shared
  `/scanstatus`: completed GE scan returned HH 209, Remote OK 3, Arbeitnow 2,
  Job Bank 12, EURES 16, and HR.ge 2. Timings: HH 7.6s, Remote OK 1.5s,
  Arbeitnow 17.1s, Job Bank 99.5s, EURES 14.5s, HR.ge 13.0s. Keep Job Bank's
  five-second request interval while evaluating latency.
- [ ] Owner completes `/import` file preview/save and Recommendation v2 vacancy
  detail checks before any v3.5.6 release tag.
- [ ] Monitor later scheduled EURES scans; the first clean run does not prove
  the underlying TLS cause is permanently resolved.
- [ ] Evaluate whether Job Bank pacing can avoid idle time while retaining at
  least five seconds between request starts and no overlapping requests; verify
  the effect with a fresh Telegram `/scan` before changing the runtime.

## v3.5.7 International Market Coverage — planned
- [x] Review JOBS.GE and HR.ge robots guidance and add conservative request
  bounds. Terms/reuse permission remains unverified; owner must inspect scan
  quality before treating the sources as useful.
- [ ] Verify an Armenian public API or obtain permission before adding a
  recurring local source; investigate the official e-work portal first.
- [x] Check current official Armenian source candidates: the Unified Social
  Service lists e-work.am and workforall.am; both public search pages timed out,
  and no API/access terms were found. Online e-work registration requires PSN
  or national eID; the in-person foreign-citizen path requires a residence card.
- [ ] Ask the Unified Social Service whether it offers an allowed public feed
  and whether foreign candidates can use it before relocating.
- [ ] Prefer permitted employer career/ATS feeds and verify location, language,
  expiry and candidate eligibility evidence.
- [ ] Add Armenian country selection only together with a tested local source.
- [ ] Keep visa sponsorship, work authorization, relocation support, salary
  and language evidence separate; unknown remains unknown.

## GitHub main synchronization
- [x] Integrate GitHub `main` commit `375af5f` into the release branch without
  rewriting history; full PostgreSQL suite passed (220 tests, 65.66%), commit
  `77379aa` was pushed, and both CI runs passed.
- [x] Owner supplied real-chat smoke results for `/salary`, `/blacklist`,
  `/scanstatus`, `/cancel`, `/import` prompt, `/version` and `/status`.
- [x] Merge PR #15 into `main`; GitHub main is v3.5.6 at `062eb25`.

## v3.5.6 Recommendation Model v2
- [x] Add persisted, explainable component scores for technical fit, growth,
  fast-exit, interview risk, salary, remote, relocation, security,
  infrastructure and competition.
- [x] Leave unsupported signals unknown, including public candidate counts.
- [x] Display component breakdown and evidence in vacancy details.
- [x] Keep existing total score/notification thresholds stable pending labeled
  outcomes; add additive JSONB migration 4.
- [x] Full isolated PostgreSQL suite: 220 passed, 65.66% branch coverage.
- [x] Publish `496c920`, deploy v3.5.6 and verify schema 4/4, polling and
  unchanged named volumes.
- [ ] Owner opens a vacancy and confirms Recommendation v2 components/evidence
  render correctly before tagging.

## v3.5.5 Candidate Import & Profile Sync
- [x] Extract text from PDF, DOCX and TXT with bounded input/resource limits.
- [x] Add Telegram `/import` with explicit preview, cancel and save choices.
- [x] Persist resume text only after confirmation; never persist raw upload bytes
  or original filename.
- [x] Add confidence/provenance to Candidate Facts through additive migration 3.
- [x] Detect exact duplicates and flag overlaps without replacing existing facts.
- [x] Full isolated PostgreSQL suite: 217 passed, 65.15% branch coverage.
- [x] Publish commit `8131e2e` and deploy with `./job-agent update`; verify
  runtime 3.5.5, schema 3/3, healthy PostgreSQL and unchanged named volumes.
- [x] Owner confirmed `/import` opens the upload prompt and existing command
  smoke tests respond.
- [ ] Owner uploads a test resume, reviews the preview, then confirms or cancels
  save; complete before tagging.

## v3.5.2
- [x] Search preference engine.
- [x] Source enable/disable.
- [x] Source priority.
- [x] Multi-country selection and priorities.
- [x] Multi-city scope.
- [x] Relocation/visa/work-permit/package/immigration policies.
- [x] Button-driven Telegram Control Center.
- [x] Integrate prefilter/order into scan pipeline.
- [x] Unit tests for preference engine.
- [x] Add career-first, relocation-first and balanced search strategies.
- [x] Keep career and relocation discovery queries independent.
- [x] Add Telegram strategy selection and `/relocationroles`.
- [x] Add unauthenticated Arbeitnow Germany discovery with conservative support signals.
- [x] Add further public international sources with explicit candidate-eligibility evidence.
- [x] Add public Job Bank Canada discovery for international candidates; keep
  LMIA, eligibility and explicit support evidence separate.
- [x] Add public EURES vacancies explicitly flagged for cross-border
  recruitment; keep this separate from visa and relocation support.
- [x] Add opt-in independent Career-first and Relocation-first SearchProfiles.
- [x] Make one scan discover and match each active SearchProfile independently.
- [x] Preserve profile settings and matches when parallel search is disabled.
- [x] Full CI green (GitHub Actions run 110 succeeded for v3.5.4; Fast Scan
  code run 105 also passed).
- [x] Add current/desired/minimum salary controls in Telegram; minimum feeds
  the existing per-currency scoring threshold.
- [x] Add Telegram blacklist controls with case-insensitive add/remove/clear,
  persisted across active search directions.
- [x] Compare testsbuild with main and selectively port useful behavior;
  Saved navigation already exists locally, and no broad branch merge was needed.
- [ ] Complete comprehensive Telegram acceptance in a real chat; local polling,
  dual-profile scheduled scan, and updated startup scan passed.
- [ ] Tag v3.5.2 after acceptance.

## Next
## Source alert resilience
- [x] Retry transient EURES transport failures with a bounded retry budget;
  do not retry HTTP status errors.
- [x] Ensure source failure notifications contain normalized error details;
  add regression coverage for transport retry and HTTP status formatting.
- [x] Full PostgreSQL suite: 206 passed, 64.46% branch coverage.
- [x] Publish as `f397f58`, run the safe tracked-branch update, verify runtime
  3.5.4 / healthy PostgreSQL / EURES HTTP 200, and confirm named volumes remain
  attached.
- [x] Extend EURES retries to raw `ssl.SSLError`; add a regression test and
  rerun the full suite (207 passed, 64.49% branch coverage).
- [x] Publish/deploy raw SSL retry as `d5d78d3`; runtime showed retry recovery
  on successful requests and one profile exhausting its retry budget.
- [x] Preserve successful EURES query/detail results if another exhausts
  retries; validate with a regression and the full suite (208 passed, 64.51%).
- [x] Publish/deploy partial-result handling as `8a87604`; verify retry-to-200
  behavior and confirm other sources continue when one profile exhausts all
  EURES search requests.

## v3.5.4 Multi-Source International Discovery
- [x] Add bounded EURES discovery for the employer's cross-border recruitment
  flag and support EURES destination-country selection.
- [x] Full PostgreSQL suite (203 passed) and coverage gate (64.39%) pass;
  GitHub Actions run 110 passes; Compose runtime updated to 3.5.4.
- [ ] Complete real-chat acceptance for the latest Telegram controls and
  source dashboard before tagging releases.

## v3.5.3 Fast Scan & Scan Dashboard
- [x] Run independent source discovery with a bounded concurrency of three;
  preserve source priority for sequential matching/ingestion.
- [x] Add source duration and isolated timeout/error reporting.
- [x] Reuse existing discovery cache; persist latest manual scan status and
  source summary in `runtime_state`.
- [x] Add `/scanstatus` and `/cancel` for in-flight manual scans.
- [x] Validate rebuilt Telegram bot polling and startup scan; real-chat command
  controls remain part of v3.5.2 acceptance above.
- [x] Audit competition/applicant signals in connected public sources. Per-vacancy
  applicant counts are employer-only (HH and Job Bank); EURES exposes positions,
  not applicant volume. Keep candidate counts unknown instead of estimating them.
