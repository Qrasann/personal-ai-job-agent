# Tasks

## GitHub main synchronization
- [ ] Synchronize the release branch with GitHub `main` commit `375af5f` on PR
  #15 without rewriting feature history; run full PostgreSQL tests and publish
  the updated feature branch so the PR becomes mergeable.
- [ ] Do not merge PR #15 into `main` until owner-driven Telegram acceptance
  below is recorded, per the current-state merge rule.

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
- [ ] Owner-driven real-chat acceptance before tagging.

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
- [ ] Owner-driven real-chat acceptance for `/import` and existing controls before
  tagging.

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
