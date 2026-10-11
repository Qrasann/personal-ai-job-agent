# Development Log

## 2026-10-11 — Lineate description entity rendering fix
- Owner's Telegram `/job 1091` check confirmed the vacancy kept salary, work
  mode and unsupported visa/relocation claims unknown, but its description
  appeared as escaped HTML (`&lt;p&gt;`, `&lt;ul&gt;`).
- Updated `clean_html_text` to decode HTML entities before stripping markup.
  Regressions verify readable Telegram detail output and preserve explicit
  Greenhouse visa-support evidence extraction.
- Full isolated PostgreSQL suite: 241 passed, 68.23% branch coverage; Python
  compilation and `git diff --check` pass. The isolated test service is stopped
  after the run. Commit `5d6b00b` was pushed; push CI `38147877309` and PR CI
  `38147879757` passed. The safe updater deployed it to Compose project `repo`;
  source/runtime is 3.5.7, PostgreSQL is healthy, and startup `scan_all`
  completed at 14:40:12 UTC. EURES returned HTTP 200 without an SSL failure in
  the inspected log window. The owner reopened `/job 1091` and confirmed that
  the description is readable; salary, work mode and unsupported
  visa/relocation claims remain unknown. Telegram acceptance is complete.
- Stable `main` and the formal GitHub release remain v3.5.6. This fix stays on
  the draft v3.5.7 feature branch; no merge, tag, schema, credentials, runtime
  production data or Docker volume changes were made.

## 2026-10-11 — Job Bank bounded transport retry
- Added one retry for `httpx.TransportError` only, under the existing shared
  request lock and five-second delay before each attempt. HTTP status errors
  are raised without retrying.
- Targeted Job Bank tests pass (`15 passed`), including recovery after a
  transient connect timeout, one-retry exhaustion, no retry for HTTP 503, and
  the existing per-request delay checks. Full isolated PostgreSQL suite:
  `244 passed`, 68.26% branch coverage. Compileall and `git diff --check` pass;
  the isolated test service is stopped. Commit `36c425b` was pushed; push CI
  `38148615302` and PR CI `38148617896` passed Python checks, Docker build and
  secret scan.
- The safe updater applied the candidate to Compose project `repo`; source and
  runtime report 3.5.7, and PostgreSQL is healthy. Startup `scan_all` completed
  at 14:51:38 UTC. Job Bank search and 12 details, plus EURES search/details,
  returned HTTP 200. No Job Bank, EURES or scan error appeared in the inspected
  logs. The scan did not encounter a transport failure, so live retry recovery
  remains covered by regression tests rather than failure injection.
- PR #18 remains open and draft against `main`. Stable `main`, the formal
  release and latest tag remain v3.5.6; no v3.5.7 tag/release or merge was
  made. The owner confirmed the post-deploy `/job 1091` description is readable
  and leaves unsupported facts unknown.

## 2026-10-11 — v3.5.7 owner Telegram source check
- Owner set Relocation-first markets to GE and AM and shared `/sources`,
  `/scan`, `/scanstatus`, and app logs. Greenhouse · Lineate appeared as an
  enabled source; its public Job Board API returned HTTP 200, with zero jobs
  matching the active profile query list.
- The zero is explained by independent profile configuration: Career-first
  markets remain unset, while Relocation-first searches broad roles such as
  warehouse, production, hotel, kitchen, cleaning and construction work. The
  Lineate Infrastructure Engineer role is outside those relocation queries.
  The next live check should target GE/AM for Career-first while leaving the
  broad relocation search unchanged, then inspect any returned vacancy.
- The same manual scan completed from 14:03:57 to 14:06:34 UTC. It reported HH
  209, Remote OK 3, Arbeitnow 2, Job Bank 12, EURES 16, Greenhouse 0 and HR.ge
  2. EURES had no SSL warning/error in the supplied log; this single run does
  not prove permanent transport stability. Job Bank took about 100.5 seconds.
- Local Compose status remained source/runtime 3.5.7 with PostgreSQL healthy.
  No schema, `.env`, production data or Docker volume changes were made. PR #18
  remains a draft; GitHub checks `38143909265` and `38143905027` are green.

## 2026-10-11 — v3.5.7 Armenia and Lineate discovery candidate
- Added `AM` to the supported country catalog and connected Lineate's public
  Greenhouse Job Board GET API for profiles targeting Armenia or Georgia.
- Scoped results to selected countries and active role queries. The current
  board's Infrastructure Engineer posting is listed for a Georgian office;
  Yerevan data-engineering titles do not match the current DevOps/Infrastructure
  queries. Unknown visa/relocation evidence remains unknown.
- Greenhouse documents that public job-board GET endpoints need no
  authentication. The adapter uses `content=true`, does not submit applications,
  and does not treat ATS update timestamps as publication dates.
- Targeted Greenhouse, country-catalog, and preference tests: 20 passed. The
  full isolated PostgreSQL suite passed: 240 tests, 68.22% branch coverage
  (55% gate); compileall and `git diff --check` passed. GitHub push CI run
  `38143185017` passed all jobs. Draft PR #18 was opened and PR-CI run
  `38143789063` passed. The safe updater deployed source/runtime 3.5.7 to local
  Compose; PostgreSQL remains healthy and the existing
  `repo_jobagent_v3_pg` and `repo_jobagent_v3_files` volumes remain attached.
  Startup scan completed at 13:31:05 UTC; EURES returned HTTP 200 and no errors
  appeared in the inspected tail. No Greenhouse request appeared, so owner
  Telegram `/sources` and targeted `/scan` acceptance remain pending. No schema
  migration, `.env`, production database, or Docker-volume change has been
  made. `main` and the formal release remain 3.5.6.

## 2026-10-11 — v3.5.7 Armenia source priorities clarified
- Applied the owner's feedback: do not make cold emails to Armenian agencies a
  release prerequisite. No email was sent.
- Kept e-work.am/workforall.am and workpermit.am out of automated discovery
  while no relevant public feed/API or authorized route is verified. Clarified
  that state-service registration requirements do not establish a general ban
  on direct applications to employers.
- Recorded Staff.am and Job.am as manual search destinations under their
  current terms; bot collection remains out of scope without permission or an
  approved feed. Prioritize permitted employer ATS feeds, documented public
  APIs, and owner-selected Telegram channels.
- Documentation-only update. No app code, database, deployment, `.env`, or
  Docker volume changed; v3.5.7 remains a feature-branch candidate, not a
  release or tag.

## 2026-10-11 — v3.5.7 source and vacancy realism review
- Started `feature/v3.5.7-international-market-coverage` from clean main
  commit `02f582e`; no application code or database changes yet.
- Checked official Armenian `workpermit.am`: it supports an employer-led
  vacancy and foreign work/residence process and states EAEU workers are
  exempt from work-permit documents for the employment-contract period. The
  public FAQ lists a “How to find a job” question, but its answer and any
  anonymous public feed/access rules were not confirmed. The Unified Social
  Service says employers may also send vacancies in a prescribed format to
  `info@socservice.am`; this is a contact route, not permission to collect.
- Follow-up official-source check: the Unified Social Service's live
  [labor-market page](https://social.welfare.gov.am/labor-market-situation-in-armenia)
  explicitly directs jobseekers to e-work.am and workforall.am. Its public
  [e-work overview](https://social.welfare.gov.am/en/what-is-e-work) describes
  employer/jobseeker matching. Direct checks of the two portals still did not
  return usable vacancy pages, and no API/feed or automated-reuse terms were
  verified.
- Opened the [workpermit.am FAQ](https://workpermit.am/en/faq) and official
  [user guide](https://workpermit.am/files/Platform_User_Guide.pdf). The FAQ
  shows “How to find a job using this Platform?” but its answer is absent from
  the page response. The guide describes an employer-created vacancy case and
  says the employer enters the foreign worker's details before the worker's
  account is created. This supports the employer-side immigration workflow,
  not public vacancy discovery.
- The portal separately says EAEU workers are exempt from permission documents
  for the employment-contract period, while a certificate confirming lawful
  residence cannot be printed without a Public Services Number. Keep work
  authorization and residence registration distinct in future matching.
- Checked Georgia's current official Labour Migration Law. Its relevant
  foreign-worker changes took effect 2026-03-01: local paid work requires an
  employer-mediated right-to-work step, followed by the applicable D1/work
  residence process. The law has a limited completely-remote/no-entry
  exception to follow-up immigration documents; this does not establish
  eligibility for local employment.
- The current consolidated law says local paid employment requires an
  employment agreement, a right to work obtained through the local employer,
  and qualifying immigration status. This remains a candidate-specific legal
  check; a `GE` target does not establish eligibility.
- Reviewed the owner-provided `/job 580`: the description says 90,000 RUB,
  but structured salary remains unknown and `/jobs` shows no salary. `/salary`
  calls 100,000 RUB a filter minimum, while current code uses it only in
  scoring when structured salary is available. Recorded this product mismatch
  as a follow-up decision rather than silently changing scoring.
- Compose status reported source/runtime 3.5.6 and PostgreSQL healthy. The
  scheduled scan started at 12:40:11 and `scan_all` completed at 12:42:28 UTC.
  The inspected tail shows Arbeitnow and Remote OK HTTP 200, plus EURES search
  and detail responses and Job Bank search/detail responses returning HTTP 200;
  no error line appeared in the inspected tail. A broader raw Docker log
  command was denied by the local Docker socket sandbox, so inspection used the
  project helper. No app or data change was attempted.
- Verification on the documentation branch: isolated PostgreSQL suite
  `233 passed`, 67.67% branch coverage; `python -m compileall -q app tests`
  and `git diff --check` passed. No behavior changed.
- References and remaining source-access questions are in
  `docs/developer/INTERNATIONAL_SOURCES.md`. No contact was sent to any agency.

## 2026-10-11 — owner Telegram release acceptance
- `/import` showed the accepted file-type/size prompt, rejected an unsupported
  ZIP, and detected two previously imported documents as duplicates. The owner
  then imported `testcv.txt`; Telegram reported resume #6 saved with zero facts
  added. The implementation persists a resume only through the preview card's
  confirmation callback, so this successful save verifies the preview/save
  path. No resume content or credentials were copied into project documents.
- `/job 580` rendered Recommendation v2 details. Missing growth, fast-start,
  interview-risk, remote, security, infrastructure, and competition evidence
  remained `н/д`.
- The supplied application log tail shows scheduled `scan_all` completed at
  12:12:59 UTC and Telegram handled the follow-up update successfully.
- These checks close the final owner-acceptance gate for cumulative v3.5.6;
- Created and pushed annotated tag `v3.5.6` on release commit `50afdab` after
  main CI run `38138941745` passed. Published the bilingual GitHub Release:
  https://github.com/Qrasann/personal-ai-job-agent/releases/tag/v3.5.6.
- No application code or database schema changed during release publication;
  the running Compose app remains source/runtime 3.5.6.

## 2026-10-11 — merge source/language candidate into main
- Merged PR #16 into `main` at `874b37255e3bb223d2b49d83027f15b48acfe7c4`.
  PR push CI `38135381779`, PR CI `38135384930`, and main merge CI
  `38135649948` passed.
- `main` now contains the English `README.md` and Russian `README.ru.md`, the
  single canonical root roadmap, and the reconciled source/release map. The
  local checkout is on `main`; the merged feature branch is inactive.
- The application code deployed to Compose remains `170ed4e`, source/runtime
  3.5.6. Status reports the app up and PostgreSQL healthy. The latest inspected
  log tail shows Job Bank detail requests returning HTTP 200 and scheduled
  `scan_all` completing at 11:12:28 UTC; no failure appears in that excerpt.
- No application image rebuild or database migration was needed. The formal
  v3.5.6 release/tag remains pending `/import` preview/save and Recommendation
  v2 detail acceptance; no tag was created.

## 2026-10-11 — Telegram source dashboard and GitHub release map
- Owner confirmed `/sources` displays JOBS.GE as paused after its configured
  endpoint returned HTTP 410; HR.ge remains available for the selected GE
  market. The completed `/scanstatus` covered 09:47:54–09:50:36 UTC.
- Source counts were HH 209, Remote OK 3, Arbeitnow 2, Job Bank 12, EURES 16,
  and HR.ge 2. Discovery timings were HH 7.6s, Remote OK 1.5s, Arbeitnow
  17.1s, Job Bank 99.5s, EURES 14.5s, and HR.ge 13.0s. Job Bank is the largest
  measured contributor; keep its five-second request pacing while evaluating
  any safe improvement.
- The owner's later log tail shows scheduled `scan_all` completed and Telegram
  updates were handled within 117–677 ms; no errors appear in that excerpt.
- Clarified the current GitHub model: `main` is stable at source version 3.5.6;
  PR #16 carries the current market/source/docs candidate; the latest formal
  GitHub release/tag is v3.5.1. Changelog entries v3.5.2–v3.5.6 are cumulative
  source milestones. The intended next formal release is one cumulative v3.5.6
  tag after `/import` preview/save and Recommendation v2 detail acceptance;
  intermediate tags will not be backfilled.
- README and README.ru.md on the candidate branch were aligned bilingual entry
  points; the subsequent PR #16 merge put both on `main`. This documentation
  stage created no release tag.
- Removed the duplicate stale PROJECT_OS roadmap; the root `ROADMAP.md` is now
  the single maintained plan and the PROJECT_OS entry links to it.
- Verification after the documentation update: isolated PostgreSQL suite
  `233 passed`, 67.67% branch coverage (55% gate); unit-only suite
  `230 passed, 3 skipped`; `git diff --check` passed. No application code,
  schema, runtime, `.env`, or Docker volume was changed.

## 2026-10-11 — Armenia public-source access audit
- The Armenian Unified Social Service's current labor-market page identifies
  e-work.am and workforall.am as its vacancy platforms. The official e-work
  overview describes nationwide listings and employer/jobseeker matching.
- Direct browser checks of e-work's public search and workforall's vacancy
  page timed out. The reviewed official material documents no public API/feed
  or automated-reuse permission. Online e-work registration asks for a Public
  Services Number or national eID; the official foreign-citizen path for
  in-person jobseeker registration requires a residence card. This leaves
  anonymous browsing and pre-move candidate access unverified.
- No Armenia country/source adapter was added. The next source step is to ask
  the Unified Social Service (`info@socservice.am`) whether it offers an
  authorized public feed and supports foreign candidates before relocation.
  References: `docs/developer/INTERNATIONAL_SOURCES.md` and `ROADMAP.md`.

## 2026-10-11 — owner Georgia scan and source resilience
- The owner ran `/targets relocation GE`, `/sources`, and `/scan` in Telegram.
  EURES returned 16 vacancies, HR.ge returned 2, and JOBS.GE failed with HTTP
  410. Arbeitnow produced a `ReadTimeout` warning for Relocation-first.
- Marked JOBS.GE temporarily unavailable in the country source catalog after
  its configured homepage returned 410. `/sources` keeps the item visible,
  labels it paused, and includes the reason; `scan_for_user` excludes it from
  source discovery.
- Added one bounded retry for Arbeitnow transport failures, with a 15-second
  request timeout and short backoff. HTTP status failures are not retried.
- Added regression tests for timeout recovery, retry exhaustion, status-error
  behavior, and paused source availability. Targeted suite: 20 passed. Full
  isolated PostgreSQL suite: 233 passed, 67.67% branch coverage; `compileall`
  and `git diff --check` passed.
- No schema or application version change. Publication, safe deployment,
  Compose log inspection, and owner Telegram verification after update remain
  pending. Existing database and storage volumes must remain attached.

## 2026-10-11 — deploy public-source resilience candidate
- Published `170ed4e` to the existing PR #16 branch. Push CI run `38129138392`
  and PR CI run `38129141546` both passed, including Python tests, secret scan,
  and Docker build.
- Applied the candidate with `JOB_AGENT_COMPOSE_PROJECT=repo ./job-agent
  update`. `/status` reports source/runtime 3.5.6, app up, and PostgreSQL
  healthy. The startup `scan_all` completed successfully.
- Startup logs show Arbeitnow responses for both active search profiles,
  EURES searches and detail requests, and HR.ge listing/detail requests all
  returned HTTP 200. No JOBS.GE request, source failure, traceback, or
  `ReadTimeout` appeared in the inspected post-update log window.
- Mount inspection confirms `repo_jobagent_v3_pg` remains at PostgreSQL data
  and `repo_jobagent_v3_files` remains at `/app/storage`. No migration or
  database mutation was made.
- The clean startup scan does not exercise Arbeitnow's retry branch. Owner
  still needs to confirm `/sources` shows JOBS.GE paused and run one fresh
  `/scan` in Telegram to inspect source results after the update.

## 2026-10-11 — live retry and scan-duration verification
- Owner supplied a post-deployment Telegram log excerpt. Arbeitnow timed out
  once, logged `retry 1/1`, then returned HTTP 200, confirming retry recovery
  against the live source.
- EURES search/details, HR.ge listing/details, Job Bank searches/details, and
  HH public fallback requests shown in the excerpt returned success; JOBS.GE
  was not requested. No source error appears in the supplied excerpt.
- Telegram handled the update in 162,716 ms. Twelve Job Bank detail requests
  are visible, about 6.4 seconds apart, consistent with its five-second
  robots crawl delay plus network time. This is a material latency contributor,
  but `/scanstatus` source timings are needed to allocate the full duration.
  Do not weaken crawl limits before measuring.
- At the time of this log entry, the owner had not yet confirmed the paused
  source display or shared `/scanstatus`. The owner later supplied both and
  completed `/import` and Recommendation v2 acceptance, as recorded in the
  latest handoff entry.

## 2026-10-11 — Georgia source guardrails (v3.5.7 market-coverage work)
- Reviewed the two existing Georgia adapters and the reported need to target
  Georgia explicitly. JOBS.GE `/robots.txt` returned HTTP 410; HR.ge returned
  HTTP 200 with `Allow: /` and a sitemap URL. The HR sitemap is about 5.4 MB
  and is not used by the adapter. Robots files do not establish content-reuse
  permission; explicit terms authorizing recurring extraction were not
  verified.
- Capped each Georgia source at six matching detail pages, set 15-second
  request timeouts, and added a two-second delay before every detail request.
  Failed individual details no longer discard successful results; all-detail
  failure becomes a visible source failure.
- Set a six-hour discovery-cache TTL for scheduled Georgia scans; a Telegram
  `/scan` still bypasses the cache for a fresh result set.
- Tightened role matching so generic words such as “engineer” cannot by
  themselves qualify unrelated titles. HR.ge salary is structured only for a
  clearly labeled range with a single explicit currency and an explicit
  monthly period. Ambiguous dollar symbols, annual pay and unperiodized ranges
  remain raw source text and do not enter numeric salary scoring.
- Added five Georgia adapter regressions for role filtering, salary evidence,
  unknown work-mode/relocation, detail limits, and partial/total detail failures.
  Targeted tests: 5 passed; the scheduled-cache regression also passes. Full
  isolated PostgreSQL suite: 230 passed,
  67.46% branch coverage (55% gate). `compileall` and `git diff --check` pass.
- Published as commit `0110173` on the active feature branch/PR #16, following
  adapter commit `2963705`. Push CI `38127150025` and PR CI `38127152783`
  passed. Applied through `JOB_AGENT_COMPOSE_PROJECT=repo ./job-agent update`;
  status reports source/runtime 3.5.6, app up and PostgreSQL healthy. The
  startup dual-profile
  scan completed successfully; EURES search/detail requests returned HTTP 200
  and no EURES/Georgia source failures appeared in inspected post-update logs.
  Mount inspection confirmed `repo_jobagent_v3_pg` and
  `repo_jobagent_v3_files` remain attached. No schema migration or database
  change. Georgia still needs a targeted Telegram scan: owner should run
  `/targets relocation GE`, `/sources`, then `/scan` and send the result
  summary plus source warnings. Keep current version at 3.5.6 pending
  end-to-end source verification and existing release acceptance.

## 2026-10-11 — v3.5.6 EURES transport and Georgia profile controls

- Reproduced the reported EURES body-read failure from inside the running app
  container. A default compressed request raised an SSL `ReadError` after
  headers; disabling keep-alive alone did not help. The same public search with
  `Accept-Encoding: identity` returned a complete 50-result JSON body (160,781
  bytes).
- Added identity encoding to EURES requests and a regression test. The adapter
  continues using bounded transport retries and preserves partial results.
- Confirmed why JOBS.GE/HR.ge were missing from the supplied scan: country-local
  adapters are planned only when a profile targets GE, and `/targets` previously
  updated only the first active profile. The command now updates all active
  profiles by default, supports `career` and `relocation` scopes, and displays
  all active profiles when run without arguments. `/sources` now reports each
  profile's plan and source-setting state.
- Replaced the stale mixed-era README with `README.md` (English) and
  `README.ru.md`, aligned changelog version headings, and rewrote the roadmap
  around the actual v3.5.6 gate and the next Armenia/Georgia source stage.
- Added source-access notes: the official Armenian e-work portal could not be
  reached for API review; Staff.am prohibits automated scraping without express
  written permission; Job.am restricts unauthorized redistribution; recurring
  findjobs.ge collection is not suitable without permission under its current
  terms. No new country feed was added without a verified permitted contract.
- Full isolated PostgreSQL suite: 224 passed; branch coverage 66.33% (55%
  gate). `python -m compileall -q app tests` and `git diff --check` passed.
- Published commit `6fa3406` to
  `feature/v3.5.6-eures-identity-market-targets`; PR #16 CI run
  passed. Recorded the verified state in follow-up handoff commit `e43072c`;
  push and PR CI passed for that branch head. At that point GitHub `main` was
  still at `6294c2a`; PR #16 was merged later at `874b372` (see the entry at
  the top of this log).
- Applied the candidate with `JOB_AGENT_COMPOSE_PROJECT=repo ./job-agent
  update`. The app restarted, `/status` reports source/runtime 3.5.6, and
  PostgreSQL stayed healthy. Post-update startup EURES search and detail
  requests returned HTTP 200; the full startup dual-profile scan completed
  successfully with no EURES SSL warnings/errors. Mount inspection confirmed
  the existing `repo_jobagent_v3_pg` and `repo_jobagent_v3_files` volumes.
- No schema migration was needed. At the time of this deployment entry, the
  v3.5.6 tag was gated on owner-driven `/import` and Recommendation v2 checks;
  the owner later completed them and the cumulative release was published.
  The owner also set GE and inspected `/sources`/`/scan` for Relocation-first.

## 2026-10-11 — v3.5.6 Recommendation Model v2
- Added a persisted per-match JSON breakdown for technical, growth, fast-exit,
  interview-risk, salary, remote, relocation, security, infrastructure and
  competition signals; Telegram vacancy details show components and evidence.
- New signals use explicit vacancy text and Candidate Facts. Missing salary,
  support, security and competition evidence remains unknown. Negated growth or
  immediate-start phrases do not count as positive evidence.
- Added additive migration 4 for `job_matches.recommendation_scores`.
- Kept the existing composite score and notification thresholds unchanged:
  public feeds have no reliable competition metric, and no labeled outcomes
  are available to calibrate a new composite safely.
- Full isolated PostgreSQL suite: 220 passed, 65.66% branch coverage (55% gate).
- Published as `496c920` to `feature/v3.5.2-dual-search-modes` and applied via
  `JOB_AGENT_COMPOSE_PROJECT=repo ./job-agent update`. Runtime reports 3.5.6,
  schema 4/4, healthy PostgreSQL and active Telegram polling. Mount inspection
  confirmed `repo_jobagent_v3_pg` and `repo_jobagent_v3_files` remain attached.

## 2026-10-11 — v3.5.5 Candidate Import & Profile Sync
- Added bounded in-memory extraction for PDF, DOCX and UTF-8/Windows-1251 TXT;
  scanned PDFs without a text layer are reported rather than OCR-guessed.
- Added `/import` and a Telegram preview with save-resume, save-resume-and-facts,
  and cancel choices. The imported resume content is stored only after explicit
  confirmation; original filename and uploaded binary are not persisted.
- Facts are proposed only from recognized skills, experience/project and
  education sections. Exact duplicates are skipped; token overlaps are shown
  without overwriting. Imported experience type stays `unknown`.
- Added confidence and provenance columns through additive migration 3; old
  facts default to confidence 1.0 and provenance `manual`.
- Targeted importer/storage/Telegram tests: 14 passed. Full isolated PostgreSQL
  suite: 217 passed; branch coverage 65.15% (55% gate). Unit suite: 214 passed,
  3 skipped. Real Telegram acceptance remains owner-driven.
- Published as `8131e2e` to `feature/v3.5.2-dual-search-modes` and applied with
  `JOB_AGENT_COMPOSE_PROJECT=repo ./job-agent update`. Compose reports runtime
  3.5.5, schema 3/3 and healthy PostgreSQL; the Telegram bot is polling. Mount
  inspection confirmed `repo_jobagent_v3_pg` and `repo_jobagent_v3_files` remain
  attached. Startup EURES transport retry appeared while other public sources
  continued. Real-chat `/import` and pending command acceptance remain unverified.

## 2026-10-11 — handle raw EURES SSL failures
- New deployed logs showed that EURES still failed after the prior update. The
  traceback ended in a raw `ssl.SSLError`, which is not an `httpx.TransportError`
  and therefore bypassed the previous retry handler. Some EURES requests still
  returned HTTP 200, confirming an intermittent transport failure.
- Extended the bounded retry handler to catch raw SSL errors and log each retry
  by exception type without including request URLs. HTTP status failures remain
  non-retryable. Added a regression for the exact bare `ssl.SSLError` path.
- Targeted source tests: 24 passed. Full isolated PostgreSQL suite: 207 passed,
  64.49% branch coverage (55% gate). Published as `d5d78d3` and deployed;
  runtime logs then recorded retry warnings and successful HTTP 200 retries,
  while one profile still exhausted retries.

## 2026-10-11 — retain partial EURES results
- Updated EURES discovery to continue after a query or detail request exhausts
  retries, retaining results from successful requests. If every search fails,
  or every matching detail fails, the source still reports an error.
- Added a regression proving one failed query does not discard a successful
  query's vacancy. Targeted source tests: 25 passed. Full isolated PostgreSQL
  suite: 208 passed, 64.51% branch coverage. Published as `8a87604` and
  deployed through the safe tracked-branch update. Runtime remains 3.5.4;
  startup logs recorded retry recovery to HTTP 200, while one profile exhausted
  retries for every EURES search query and correctly reported the source as
  unavailable. Job Bank and other sources continued; PostgreSQL stayed healthy
  and existing named volumes remained attached.

## 2026-10-11 — source error resilience
- Inspected the running Compose project and latest logs after repeated Telegram
  alerts. Confirmed EURES requests can fail with `httpx.ReadTimeout` and an SSL
  record-layer error. Found that HTTP status exceptions could produce blank
  Telegram text because the notification formatted `str(exc)` directly.
- Added two bounded retries with short exponential backoff for EURES transport
  errors only; HTTP status responses are not retried. Source alerts now use the
  same normalized error text as the scan summary, including `HTTP <status>`.
- Added regressions for a transient EURES transport failure, HTTP status
  formatting and no-retry behavior for HTTP errors. Targeted tests: 23 passed.
  Full isolated PostgreSQL suite: 206 passed, 64.46% branch coverage (55% gate).
- The first full-suite attempt ran before `postgres-test` was started and had
  three connection-refused integration failures; after starting only the
  isolated test service, the complete suite passed (206 tests). Production
  Compose and its PostgreSQL/storage volumes were not changed during testing.
- Published as `f397f5855f9b22a610f7d043377071ed5a99fab0` and deployed with
  `JOB_AGENT_COMPOSE_PROJECT=repo ./job-agent update`. Runtime/source report
  3.5.4; the bot is polling as `@roma_job_agent_bot`, PostgreSQL is healthy,
  and the new startup scan's EURES search returned HTTP 200. Mount inspection
  confirmed `repo_jobagent_v3_pg` and `repo_jobagent_v3_files` remain attached.
- Real-chat acceptance of `/salary`, `/blacklist`, `/scanstatus`, and `/cancel`
  remains owner-driven and unverified.

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

# 2026-10-11 — merge v3.5.6 and owner Telegram smoke test
- Owner-provided Telegram results confirmed `/salary`, `/blacklist`,
  `/scanstatus`, `/cancel`, `/import` upload prompt, `/version` (3.5.6, schema
  4/4, migration OK), and `/status` (ACTIVE). The scan status was completed;
  EURES reported an error while HH, RemoteOK, Arbeitnow and Job Bank returned
  results. The uploaded-resume preview/save flow and Recommendation v2 vacancy
  details were not exercised.
- With full CI green and the command-level smoke test recorded, merged PR #15
  into `main` as `062eb253bdf8435782e5fcca6cfb1257b271ea86`. GitHub Actions
  runs `38121905782` and `38121908521` both passed.
- The running Telegram bot reported v3.5.6 and database schema 4/4; existing
  PostgreSQL and storage volumes were verified attached. No schema change or
  application-code change was made in the merge follow-up.
- Remaining release-tag gate: owner verifies `/import` with a test file through
  preview and explicit save/cancel, and opens a vacancy to check Recommendation
  v2 component details.

# 2026-10-11 — reconcile the release branch with GitHub main
- Checked the clean v3.5.6 release branch against `origin/main`: main is at
  `375af5f` (v3.5.1), while the release branch is at `466c676`; the branches
  diverged after the search-control PR was merged to main.
- Integrated the main commit into the feature branch without rewriting history;
  overlapping implementation files retain the later release-branch content.
  The merge produces no application-tree changes.
- Reran the full isolated PostgreSQL suite: 220 passed, 65.66% branch coverage.
- Runtime inspection reports source/runtime 3.5.6, app up, PostgreSQL healthy,
  and the existing `repo_jobagent_v3_pg` and `repo_jobagent_v3_files` volumes
  attached. Latest EURES logs still show intermittent SSL record-layer
  failures; bounded retries sometimes recover and the scheduled scan completed.
- PR #15 must remain unmerged until the owner records real-chat acceptance for
  the Telegram controls and Recommendation v2 details, as required by the
  current-state merge rule. Published merge commit `77379aa`; PR #15 reports
  `MERGEABLE`, and push run `38121809437` plus PR run `38121811653` both passed
  Python checks, Docker build and secret scan.

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
- At that stage, owner-driven real-chat acceptance of `/salary`, `/blacklist`,
  `/scanstatus`, and `/cancel` remained pending. The owner later verified these
  controls and the project consolidated the milestones into v3.5.6 rather than
  publishing a retroactive v3.5.2 tag.
- Release metadata `VERSION=3.5.3` is published in commit
  `e4fa198f63d07a5120f6e480b63a7be9cdb46efd`; CI run 108 passed. The bot was
  rebuilt and reports source/runtime 3.5.3. Its new startup scan completed
  successfully at 21:11:40 UTC on 2026-10-10 with Job Bank query/detail HTTP
  200 responses. At that stage, v3.5.2/v3.5.3 tags awaited real-chat
  acceptance; both milestones were later included in cumulative v3.5.6.

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

## 2026-10-11 — v3.5.7 Career-first Georgia live check
- Owner selected GE/AM for Career-first and supplied `/sources`, `/scan`, and
  `/scanstatus` output. Greenhouse returned one Lineate Infrastructure Engineer
  opening explicitly located in GE, scored 67/100, and generated one
  notification. Career-first processed 172 vacancies (31 Good, 33 Stretch);
  Relocation-first processed 61 (0 Good, 0 Stretch).
- Source counts: HH 209, Remote OK 3, Arbeitnow 2, Job Bank 0, EURES 16,
  Greenhouse 1, HR.ge 2. Job Bank failed only for Relocation-first with
  `httpx.ConnectTimeout` after 29.2 seconds; the scan completed and other
  sources continued. The supplied log excerpt showed EURES success without an
  SSL failure.
- Rechecked the current official Lineate posting: Georgian office, minimum 3
  years Linux system administration, minimum 2 years production AWS, and a
  24/7 shift schedule. The posting does not state salary, work mode, visa
  sponsorship, or relocation assistance. Those fields remain unknown.
- Updated README in English and Russian, roadmap, branch brief, task list,
  current state, and this handoff log. No application behavior, database,
  migration, or Docker volume changed. The remaining v3.5.7 Telegram check is
  `/jobs` followed by `/job <id>` for the Lineate result; PR #18 stays draft
  until the detail card is reviewed.
- Follow-up reliability task: add bounded Job Bank transport retries with
  regression coverage while preserving the five-second request spacing; do
  not retry HTTP status errors automatically.
