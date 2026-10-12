# Codex Brief

Last updated: 2026-10-13 (Europe/Moscow)

**Current checkpoint — 2026-10-13.** Review of the Canonical Himalayas listing
found a common requirements-heading gap that left technical requirements and
interview-risk unknown. The parser now handles `What we are looking for`,
`What you'll bring`, and `Nice-to-have skills`, including curly apostrophes;
the risk evidence explicitly says technical requirements only. Targeted tests:
**37 passed**; full suite: **439 passed, 3 skipped**; isolated PostgreSQL:
**442 passed**; compileall, secret scan and diff check passed. Commit `b42d47c`
is local. Compose `repo` was rebuilt at 00:14 Moscow on Oct 13; app and
PostgreSQL are healthy, and startup `scan_all` completed at 21:15:52 UTC after
one isolated `ConnectError`. Telegram `/job 1273` confirmation remains next.
Do not interpret technical fit as a full interview
probability or include unsupported education/language judgments.

**Current checkpoint — 2026-10-12.** Reviewed the official Emerging Travel
Group Junior DevOps opening: it names Armenia and Georgia as available remote
locations, and asks for 1.5+ years commercial DevOps, six months of Kubernetes,
and English B1+. Workable's own docs describe public published-job endpoints,
but the documented ETG endpoint currently returns HTTP 403 from this network.
Added the official role as a link-only manual entry under both AM and GE; no
scraper or scan was added. Telegram's 21:13 Moscow result showing a Tyumen
onsite vacancy predates the 21:26 rebuild containing the current-country
filter. The next owner command should verify `/jobs relocation` and
`/jobs relocation below` against that rebuilt runtime. Targeted source display
tests: **5 passed**; full unit suite: **437 passed, 3 skipped**. Compileall,
secret scan, and diff check pass. Compose `repo` was rebuilt at 21:37 Moscow;
PostgreSQL stayed healthy and startup scan completed at 21:38:46 UTC. The scan
logged one transient HeadHunter `ConnectError` for search 2 and completed
successfully with source isolation. The role is not evidence of a Russian
citizen's individual hiring, visa, or right-to-work eligibility. Local commit
`432d44c`; Telegram post-filter list confirmation remains pending.

Both this lead and the English bootstrap correction are committed locally:
`432d44c` (ETG manual lead) and `8ca977f` (English distinction). Current
branch remains local and unpublished; no publication is authorized. The last
verified container rebuild predates
this checkpoint; a fresh Docker status check is still needed because sandbox
access to the Docker socket was denied.

The AI job-bot bootstrap profile now records general self-assessed English as
B1 and keeps B2 only as a technical-reading estimate. Bootstrap does not use
either language field to overwrite persisted candidate data. A regression
test covers the distinction. Targeted bootstrap tests: **3 passed**; full suite:
**437 passed, 3 skipped**; compileall, secret scan, and diff check pass. The
follow-up commit is `8ca977f`.

**Current checkpoint — 2026-10-12.** A fresh Telegram check confirmed
`/sources`, `/jobs relocation`, and `/jobs relocation below` render correctly.
It exposed that ordinary onsite jobs in the current country (RU) could appear
in Relocation-first. The filter now excludes those jobs unless the owner
explicitly enables `domestic_relocation`; explicit remote jobs and unknown-
country vacancies remain visible, and Career-first is unchanged. Regression
coverage includes all four cases. Local suite: **437 passed, 3 skipped**;
isolated PostgreSQL suite: **440 passed**; compileall, secret scan, and diff
check pass. Compose `repo` was rebuilt without replacing PostgreSQL or its
volumes; runtime 3.5.7 and PostgreSQL are healthy, and startup `scan_all`
completed at 18:26:17 UTC. One HeadHunter public-web request logged a
transient `ConnectError`; the scheduler scan completed. Telegram verification
of the filtered list remains pending. The bootstrap GE/AM defaults were committed locally as
`00f1f0d`. HeadHunter's official public area directory
confirms RU `113` and GE `28`, but contains no Armenia area. The HH adapter now
searches each represented current/target market independently, deduplicates
results, and attributes country only to the scoped request; Armenia is left to
other sources. Verification: local suite **429 passed, 3 skipped**; isolated
PostgreSQL suite **433 passed**; compileall, secret scan, and diff checks pass.
This HH follow-up is committed locally as `61fe39d`; Compose was rebuilt from
the branch and its startup scan completed at 17:56:41 UTC. Logs show successful
public-web HH requests for both `area=28` and `area=113`; PostgreSQL is healthy.
Telegram acceptance remains pending; no publication was made. The EURES padded-location fix is published
as `159d510` on draft PR #18; push CI `38281187340` and PR CI `38281192380`
passed. Full isolated PostgreSQL validation: **429 passed, 73.24% branch
coverage**; 13 targeted EURES tests, `compileall`, secret scan, and diff checks
also pass. Compose `repo` now runs the fixed source/runtime 3.5.7 with healthy
PostgreSQL and the unchanged `repo_jobagent_v3_pg` / `repo_jobagent_v3_files`
volumes. The post-update startup scan reached EURES search/details with HTTP
200 and completed successfully at 17:04:14 UTC; its log window contains no
database/source error, traceback, or repeated city-width failure. Continue the
open practical Relocation-first coverage and latest scoped-command Telegram
acceptance; do not merge/tag/release v3.5.7 yet. See `HANDOFF.md`.

The current worktree adds clickable manual-search links for verified AM/GE
portals in `/sources`. These links do not enter automated scans or source
toggles; Findjobs.ge's current terms require written permission for repeated or
systematic extraction of substantial data. Local validation: **432 passed,
3 skipped**; isolated PostgreSQL **435 passed**; compileall, secret scan, and
diff check pass. Manual-link stage is commit `ffabb1b`. Compose was rebuilt
from this branch; startup scan completed at 18:06:12 UTC with PostgreSQL
healthy and no request to any manual portal. Owner confirmed `/sources`
rendering at 21:12 Moscow time; the manual links appear for both profiles.

The AI job-bot bootstrap profile now defaults to equal-priority `GE` and `AM`
and bounded lower-barrier Relocation-first queries. This affects only fresh
profile initialization; persisted user settings are preserved.

## Mission

Continue the existing Personal AI Job Agent. Maintain two independent tracks:

1. **Career-first** — DevOps / Infrastructure / SRE growth.
2. **Relocation-first** — any legal, verifiable work that can enable a realistic move; career fit is secondary.

Never restart the project from scratch. Unknown visa, salary, citizenship, housing, or relocation facts remain unknown; never convert missing evidence into `false` or a positive claim.

## Current runtime

- **Latest stage (Oct 12): independent results and correct Staff handling.**
  `/jobs career`, `/jobs relocation` and `/jobs relocation below` query only
  the requested enabled search profile and its own threshold. The list-to-card
  and comparison-button paths retain `search_profile_id`; cards name the
  selected profile. Legacy command/callback formats remain supported. Ordinary
  Hotel/Kitchen/Warehouse Staff no longer trigger the technical Staff seniority
  exclusion; actual Staff technical roles and explicit seniority, experience,
  management and owner exclusions retain their restrictions. Scores and the
  default threshold of 65 are unchanged. Full local suite: 319 passed, 3
  database tests skipped; all 3 isolated PostgreSQL repository tests passed.
  Compilation and diff checks pass. Compose `repo` was rebuilt at 01:36
  Moscow: source/runtime 3.5.7, app up and PostgreSQL healthy; startup scan
  completed successfully at 01:37:50 Moscow. Telegram acceptance
  of the new scoped commands remains pending. Next:
  bounded HH discovery for selected destinations has now been implemented for
  catalogued markets; official HH has no Armenia area. Continue verified AM/GE
  employer feeds; no assumption that this correction alone produces
  Good/Stretch.
  `ROADMAP.md` now has a stage/status overview; the private relocation roadmap
  has its own progress and a current official-law review. No publication.
- **Latest candidate stage (Oct 12 Moscow):** Added the official Remotive
  Devops RSS feed with required provider attribution, a shared persisted
  24-hour cache, country-scope handling, and Remotive links in `/jobs`. The API
  ignored tested category filters and returned a broad feed, so the adapter
  now uses the documented category feed and cache key v3. Targeted Remotive and
  cache tests: 17 passed; full local suite: 286 passed, 3 database tests
  skipped; all 3 repository PostgreSQL integration tests passed. Compilation
  and `git diff --check` passed. Added `/jobs below` for descending manual
  review of nonzero results below the configured threshold; scores,
  notifications, and the threshold stay unchanged, and unknown work/relocation
  eligibility is explicit. The Remotive RSS request returned HTTP 200 but no
  job items, so both profiles correctly found 0 Remotive jobs. The provider
  response is cached for 24 hours; recheck after expiry. Compose `repo` was
  rebuilt at 01:15 Moscow Oct 12; source/runtime report 3.5.7, PostgreSQL is
  healthy, and the app is polling. The startup scan began immediately, and
  Telegram acceptance of `/jobs below` is pending. Keep 3.5.7 local and
  unpublished; next,
  improve practical Relocation-first source coverage without changing the
  65-point threshold or score ordering.
- Checked-out feature source is `3.5.7` on `d445c87`; the worktree has
  uncommitted changes. Compose project `repo` also reports runtime `3.5.7`
  with schema `4/4`. The current worktree, including the Collectly Lever
  source, passed 274 local tests (3 database tests skipped), `compileall`, and
  `git diff --check`. The image was rebuilt at 21:04 Moscow time and PostgreSQL
  is healthy; startup `scan_all` completed successfully at 18:06:21 UTC
  (21:06:21 Moscow). Lever returned HTTP 200 for both profiles; Himalayas,
  EURES, Job Bank, HR.ge, Greenhouse and HH public search also returned
  successful responses in the inspected log window. HH's API 403 recovered
  through its public-web fallback. Previous mount inspection confirmed the
  named data volumes remain attached. The owner accepted the Himalayas
  `/job 1273` geography card at 20:56. Collectly job #1333 was found in the
  runtime database as filtered by the Career-first `senior devops` exclusion;
  this is expected profile behavior, not a missing source result.
- At 21:11–21:14 Moscow time the owner confirmed `/sources` lists Lever for
  both profiles, then ran `/scan` and `/scanstatus`: Lever returned 1 live
  vacancy in 9.6s; the scan completed in 131s with no source error in the
  supplied log excerpt. Job Bank returned 12 in 71.4s and EURES 16 in 55.2s.
  A read-only lookup found Collectly as job #1333, filtered at score 0 because
  Career-first explicitly excludes `senior devops`; this is expected profile
  behavior, not a source failure. Do not change that exclusion without the
  owner's choice. At 21:20 the owner showed remote CloudCops (Good, 88) and
  Sporty Group (Stretch, 72) at the top of `/review` and `/stretch`.
- The same scan reported Relocation-first 74 processed, 0 Good, 0 Stretch.
  That profile has broad lower-barrier queries and a 65-point threshold; an
  inspected remote result scored 54 and was filtered. Treat this as a
  relocation-result visibility issue, not an adapter outage. The owner
  confirmed higher-rated results must remain first; keep `/jobs` sorted by
  score, retain the 65-point threshold, and do not promote lower-scoring
  results into a higher-priority queue. Continue source-coverage and relevance
  work without score inflation or changing owner exclusions.
- GitHub check on 2026-10-11: latest formal tag/release v3.5.6; visible tags
  are v3.5.0, v3.5.1, and v3.5.6. v3.5.2–v3.5.5 are cumulative changelog
  milestones, not separately tagged releases. PR #18 is open/draft. Local
  branch `feature/v3.5.7-international-market-coverage` remains at
  `d445c87`/`VERSION=3.5.7` with uncommitted changes; no publication action.
- GitHub `main` contains source version `3.5.6`; PR #15 and PR #16 are merged.
  The deployed application code is `170ed4e`; PR #16's later commits only
  updated documentation. The merge is recorded at
  https://github.com/Qrasann/personal-ai-job-agent/pull/16.
- Branch map: `main` is the stable source at `02f582e`; the current working
  branch is `feature/v3.5.7-international-market-coverage`, currently at
  `d445c87` with uncommitted local work, created from that main commit. Its
  candidate `VERSION` is
  `3.5.7`; `main` remains `3.5.6`, while local Compose project `repo` runs
  candidate 3.5.7. `feature/v3.5.6-eures-identity-market-targets`
  is merged and inactive; `feature/v3.5.2-dual-search-modes` is an older branch.
- Version map: the stable source on GitHub `main` is v3.5.6; the checked-out
  feature branch and runtime report v3.5.7. The latest formal GitHub tag and
  Release are v3.5.6. Changelog entries v3.5.2–v3.5.5 are cumulative milestones
  included in that release; do not backfill intermediate tags.
- GitHub CI passed for merge commit `874b372` (run `38135649948`); the PR #16
  push and PR checks also passed (runs `38135381779` and `38135384930`).
- The cumulative v3.5.6 tag points to release commit `50afdab`; main CI run
  `38138941745` passed. The bilingual release is published at
  https://github.com/Qrasann/personal-ai-job-agent/releases/tag/v3.5.6.
- Local release directory: `~/job-agent-release-v352`.
- Docker Compose project: `repo`.
- Career-first and Relocation-first SearchProfiles are enabled independently.
- Working sources include HH public fallback, RemoteOK, Arbeitnow, Job Bank Canada, EURES, HR.ge, and configured Telegram ingestion. JOBS.GE is temporarily paused after its configured endpoint returned HTTP 410.
- Auto-apply and HH private actions remain off.

## Recently completed

- Added bounded retries for EURES transport failures, including raw
  `ssl.SSLError`, and made source alerts report HTTP status / exception type.
- Added `/parallelsearch on|off|status` and `/relocationroles`.
- Each profile now discovers, scores, stores, and reports results independently.
- Fixed concurrent `JobMatch` inserts with an atomic PostgreSQL upsert.
- Fixed Relocation-first scoring to use `relocation_queries`.
- Added public Arbeitnow Germany discovery with conservative evidence handling.
- Stopped inferring salary from arbitrary description numbers.
- Added safe tracked-branch updates through `./job-agent update`.
- Added Job Bank Canada discovery with separate international eligibility, LMIA, and support evidence.
- Added bounded EURES discovery using the employer cross-border recruitment flag without treating it as visa sponsorship.
- Job Bank preserves verified results after individual transport failures and
  now enforces a five-second minimum between serialized request starts without
  an unnecessary full wait after slow responses. The owner verified 12 live
  results in 71.2s on the post-update scan, compared with 100.7s previously;
  no source failure appeared in the supplied log excerpt.
- Added explicit Telegram resume import for PDF/DOCX/TXT, plus fact confidence/provenance and overlap review.
- Added persisted Recommendation v2 component breakdown with unknown values
  left unset and displayed in vacancy details.
- Both independent search profiles now process vacancies explicitly marked
  remote earlier within each source batch. This does not alter Match Score,
  raise score thresholds, or establish that the employer allows work from the
  target country; unknown remote scope remains unknown.
- The current v3.5.7 worktree adds Himalayas' documented public remote-job
  API. It searches up to four active-profile queries across at most three
  selected markets, one page of 20 jobs per query/market, and caches results
  for 24 hours. Cards link to and attribute Himalayas; salary includes its pay
  period. The provider's location limits are preserved and missing limits stay
  unknown. The owner verified the source in Telegram and accepted `/job 1273`:
  worldwide is presented as the provider's claim, with employer confirmation
  required for country-level hiring.
- Added a curated Lever Postings API adapter for Collectly's published remote
  DevOps role. It is enabled only for selected AM/GE profiles and only while
  the role states a timezone band covering UTC+4. The job source's Belgrade/RS
  metadata is preserved separately while normalized country, salary, visa,
  and relocation remain unknown unless supported by the current posting.
  Current local suite: 274 passed, 3 database tests skipped; source-specific
  regression tests and compilation pass. Compose has been rebuilt. The owner
  later verified `/sources`, `/scan`, and `/scanstatus`; Lever returned one
  result. The saved Collectly match is filtered by the explicit Career-first
  exclusion, so no review-queue detail card is expected unless that filter is
  changed.
- Job Bank preserves verified results after individual transport failures and
  enforces a five-second minimum between serialized request starts without an
  extra full wait after a slow response. The owner compared live timings in
  Telegram `/scanstatus`: 71.2s for 12 results, down from 100.7s previously.
- Added `/salary`, `/blacklist`, `/scanstatus`, `/cancel`, bounded concurrent discovery, source timings, and persistent manual-scan state.
- Set EURES `Accept-Encoding: identity` after reproducing TLS body-read failure
  with the default compressed response and reading the complete 50-result JSON
  with identity encoding.
- Updated `/targets` to configure all active search profiles by default, with
  explicit `career` and `relocation` scope; `/sources` now shows each profile's
  configured source plan.
- Bounded JOBS.GE and HR.ge detail fetching to six listings per source, with
  conservative pacing and timeouts; tightened role matching and require an
  explicit currency plus monthly period before HR.ge salary enters scoring.
  Partial detail results survive individual request failures; total failure is
  reported to the scan. Scheduled Georgia discovery now uses a six-hour cache;
  manual `/scan` still forces a refresh.
- Processed the owner’s live Georgia scan: EURES returned 16, HR.ge returned 2,
  JOBS.GE returned HTTP 410, and Arbeitnow emitted a transient ReadTimeout.
  The candidate pauses JOBS.GE with its reason visible in `/sources` and adds
  one bounded retry for Arbeitnow transport failures.
- Replaced the mixed-language README with English and Russian entry points,
  aligned changelog headings, refreshed the roadmap, and documented current
  Armenia/Georgia source-access constraints.
- Confirmed the Armenian Unified Social Service lists e-work.am and
  workforall.am as vacancy platforms. Their public search pages timed out;
  API/access terms are unverified, and official registration rules do not yet
  establish pre-move foreign-candidate access.
- Checked the official Armenian `workpermit.am` foreign-hiring portal: it
  documents an employer registration/vacancy/work-residence workflow and says
  EAEU citizens working in Armenia are exempt from work-permit documentation.
  The FAQ lists a job-finding question, but its answer and anonymous/public
  feed access remain unverified. The current-country setting does not establish
  citizenship, so EAEU eligibility must remain candidate-specific.
- Rechecked Georgia's official Labour Migration Law: the foreign-worker right-
  to-work requirement took effect 2026-03-01. Local paid work is employer-led;
  check the subsequent D1/work-residence steps and limited remote-work rule.
- Audited public applicant-count signals; connected feeds do not expose reliable candidate-side competition counts.
- Merged release PR #15 and candidate PR #16 into GitHub `main`; CI passed and
  the owner supplied real-chat smoke checks for core commands and the updated
  source plan/scan.
- Owner completed release acceptance in Telegram: the unsupported ZIP was
  rejected, duplicate resumes were detected, TXT resume #6 was saved through
  the confirmation flow with zero proposed facts, and `/job 580` displayed
  Recommendation v2 with unsupported signals as `н/д`.
- Published the cumulative v3.5.6 GitHub release after Telegram acceptance of
  TXT resume import and Recommendation v2 vacancy details.
- Added Armenia (`AM`) to the country catalog and a Greenhouse public GET
  adapter for Lineate. The source runs only for profiles selecting AM or GE,
  matches active role queries, and requires explicit location evidence. It
  keeps visa/relocation unknown absent an employer statement. This v3.5.7
  candidate is deployed to the local Compose bot, but is not merged or released.
- Owner ran the v3.5.7 Telegram source check for Relocation-first GE/AM. The
  Lineate Greenhouse endpoint returned HTTP 200 but yielded zero role matches:
  Career-first has no selected markets, while Relocation-first uses broad
  non-technical role queries. EURES returned 16 live vacancies with no SSL
  failure in the supplied scan. This earlier check preceded the successful
  Career-first GE/AM role/location scan recorded below.
- Owner completed the Career-first GE/AM scan and opened Lineate vacancy
  `/job 1091`. Salary, work mode, and unsupported visa/relocation facts stayed
  unknown as intended. The description displayed escaped markup such as
  `&lt;p&gt;`; a regression-tested fix now decodes entities before stripping
  tags. The owner confirmed the deployed description is readable while those
  unsupported facts remain unknown.
- Review of the [official Lineate posting](https://job-boards.greenhouse.io/lineate/jobs/8018252)
  found required qualifications for 3+ years Linux system administration and
  2+ years AWS in production, plus a 24/7 shift schedule. The old parser missed
  its `Necessary Qualifications` heading, which allowed Technical 100 through
  fallback role/keyword matching and left interview risk `н/д`. Commit
  `7a6901d` recognizes common English required-qualification headings and uses
  their technical signals in Recommendation v2. It is deployed; the startup
  scan completed successfully from 15:02:28 to 15:04:57 UTC, and the owner
  should review the rescored `/job 1091` card in Telegram.
- Follow-up commit `678ddfc` extracts `Minimum N years` / `At least N years`
  wording for experience fit and adds Windows and Databricks to technical
  evidence matching. The full isolated PostgreSQL suite passes: 247 tests,
  68.36% branch coverage; compilation and diff checks pass. The commit is
  pushed; push CI `38150088881` and PR CI `38150092577` passed. Documentation
  commit `664c559` passed push CI `38150288518` and PR CI `38150292566`. The
  safe updater deployed the candidate; its startup scan ran from 15:13:24 to
  15:15:48 UTC and completed without source errors. The owner should now review
  the recalculated `/job 1091` card in Telegram.
- Owner then reported `/job 1091` Technical 42 but interview risk `н/д`. The
  detail flow passed decoded HTML to Technical Score, while Recommendation v2
  scored the raw stored HTML. Commit `8a583c7` now passes the same normalized
  description into both calculations; its regression expects Technical 42 and
  interview risk 58. Push CI `38151840822` and PR CI `38151843490` passed.
  The safe updater deployed it to Compose; startup scan completed at 15:38:13
  UTC without source errors, SSL failures, timeouts, or tracebacks in the
  inspected five-minute window. The owner later confirmed Technical 42 and risk
  58 in Telegram; see the acceptance record above.
- The uncommitted candidate now prioritizes explicit remote work inside each
  source batch in both independent profiles. This changes processing order
  only; geographic eligibility stays separate and unknown scope is not treated
  as worldwide. The local suite passes 266 tests with 3 PostgreSQL tests
  skipped; the isolated PostgreSQL suite passes all 269 tests at 69.70% branch
  coverage. Job Bank enforces minimum five-second spacing between request
  starts without adding a full delay after slow responses. The candidate was
  rebuilt into local Compose at 20:33 Moscow time; startup scan completed, and
  Himalayas returned HTTP 200 for GE and AM. Telegram acceptance is pending.

## Verified

- Latest full isolated PostgreSQL suite: `269 passed`, 69.70% branch coverage
  (55% gate), including encoded Greenhouse HTML, Recommendation v2 interview
  risk, remote priority, Job Bank pacing, and Himalayas regressions. Compilation and
  `git diff --check` pass. The currently published code commit `8a583c7` passed
  push CI `38151840822` and PR CI `38151843490`; those checks do not include the
  current uncommitted changes.
- Local Compose check: source/runtime `3.5.7`, app polling, PostgreSQL healthy.
  Mount inspection confirms `repo_jobagent_v3_pg` and `repo_jobagent_v3_files`
  remain attached. The startup scan completed at 13:31:05 UTC; EURES returned
  HTTP 200 and no errors appeared in the inspected tail. The owner later
  confirmed `/sources` enabled Greenhouse for Relocation-first GE/AM; the
  Greenhouse request returned HTTP 200 and zero query-matched jobs. The
  currently selected relocation roles do not include Infrastructure Engineer.
- The safe updater applied the candidate to Compose project `repo`; source and
  runtime report 3.5.7 and PostgreSQL is healthy. The latest startup
  `scan_all` ran from 15:35:45 to 15:38:13 UTC and completed successfully. HH's
  API returned 403 before its ordinary public web fallback succeeded; the
  five-minute error scan found no source failure, SSL error, timeout or
  traceback.
- The owner supplied a fresh Telegram `/scan` and `/scanstatus` at 19:33–19:36
  Moscow time: Job Bank returned 12 vacancies in 100.7 seconds; EURES 16,
  HR.ge 2, HH 209, Remote OK 3, Arbeitnow 2 and Greenhouse 1. The supplied log
  excerpt shows Job Bank details, EURES and HR.ge returning HTTP 200, without a
  Job Bank warning or source error. This confirms a normal live run; it did not
  exercise the partial-transport-failure path covered by regressions.
- Georgia adapter regressions: `5 passed`; a scheduled-cache regression also
  passes. Compilation and `git diff --check` passed. The six-detail cap,
  per-request timeout, inter-request delay, partial-failure behavior and salary
  evidence rules are covered.
- Greenhouse/country/preference targeted tests: `20 passed`; the full suite
  includes the source adapter and availability regressions.
- Targeted EURES, Job Bank and source-error regressions: `25 passed`.
- GitHub Actions passed for PR #16 and merge commit `874b372` (main run
  `38135649948`).
- Draft PR #18 is open for the v3.5.7 candidate. Career-first GE/AM role and
  location acceptance and readable detail-card check are complete; owner review
  of the corrected interview-risk line in `/job 1091` is still needed. Keep PR
  #18 draft; v3.5.7 remains unmerged and unreleased. Latest code commit is
  `8a583c7`; push CI `38151840822` and PR CI `38151843490` passed.
- Commit `496c920` and its release are on `main` at merge commit `062eb25`;
  Compose reports source/runtime
  3.5.6, PostgreSQL healthy, schema 4/4, and the bot polling. Mount inspection
  confirms the existing `repo_jobagent_v3_pg` and `repo_jobagent_v3_files`
  volumes remain attached. Startup scan began on HH public fallback, Arbeitnow
  and RemoteOK; no startup errors were present in the inspected log tail.
- Application commit `170ed4e` was merged to `main` through PR #16 and remains
  applied to Compose project `repo`. Runtime is 3.5.6; app is up and PostgreSQL
  is healthy. The startup scan completed successfully. Both Arbeitnow requests,
  EURES searches/details, and HR.ge listing/detail requests returned HTTP 200;
  no JOBS.GE request or source error appeared. Named
  `repo_jobagent_v3_pg` and `repo_jobagent_v3_files` volumes remain attached.
- Owner's follow-up Telegram scan exercised the deployed Arbeitnow retry:
  Relocation-first received a `ReadTimeout`, the single retry returned HTTP
  200, and the supplied log excerpt shows EURES, HR.ge, Job Bank, and HH
  requests succeeding. JOBS.GE was not requested. Telegram handled the update
  in 162.7 seconds. The later `/scanstatus` attributed 99.5 seconds to Job
  Bank, 17.1 to Arbeitnow, 14.5 to EURES, 13.0 to HR.ge, 7.6 to HH, and 1.5
  to RemoteOK. Job Bank's five-second request pacing remains in place.
- EURES now preserves partial results when only some requests fail. Existing PostgreSQL and storage volumes remain attached.
- Polling, schema check, scheduled/manual dual-profile scans, and concurrent scan protection passed locally.
- GitHub PRs #15 and #16 are merged. PR #16 added EURES/market/source
  reliability and bilingual documentation; its push/PR CI and the merge-commit
  CI passed.
- Owner-provided Telegram smoke test on 2026-10-11 confirmed `/salary`,
  `/blacklist`, `/scanstatus`, `/cancel`, `/import` prompt, `/version` and
  `/status`. The earlier scan completed with an EURES error while other sources
  returned results. The owner later completed the `/import` and Recommendation
  v2 checks described above.
- After the earlier v3.5.6 safe update, the 2026-10-11 startup scan completed
  successfully.
  EURES search and detail requests returned HTTP 200 without SSL retry/error
  logs. Continue monitoring subsequent scheduled scans; one successful run
  does not establish the underlying TLS cause.
- That earlier v3.5.6 runtime check reported source/runtime `3.5.6`, app
  polling, PostgreSQL healthy, and the existing named volumes attached; the
  current v3.5.7 candidate runtime is recorded above.
- Owner confirmed `/sources` marks JOBS.GE temporarily paused after HTTP 410
  and shared `/scanstatus`: the GE scan completed from 09:47:54 to 09:50:36
  UTC. EURES returned 16 vacancies, HR.ge 2, Job Bank 12, Arbeitnow 2, HH 209,
  and Remote OK 3. A later app-log tail shows `scan_all` completed and Telegram
  updates were handled in 117–677 ms; no errors appear in that excerpt.
- Owner ran `/targets career GE,AM`, `/sources`, `/scan`, and `/scanstatus`.
  Career-first returned one Greenhouse Lineate Infrastructure Engineer opening
  explicitly marked `GE` (67/100); the bot reported work mode as unknown. The
  scan returned HH 209, Remote OK 3, Arbeitnow 2, Job Bank 0, EURES 16,
  Greenhouse 1, and HR.ge 2. Job Bank's Relocation-first request failed with a
  transient `ConnectTimeout` after 29.2 seconds; the other sources completed.
  No EURES SSL failure appeared in the supplied excerpt. The owner opened
  `/job 1091`; unsupported visa/relocation claims stayed unknown, and the
  owner confirmed the deployed decoder now renders the description readably.

## Current priority

Treat relocation search as time-sensitive. The Relocation-first profile now
processes explicitly remote vacancies earlier within each source batch; verify
that the posting permits work from the intended country before treating it as a
usable route. Keep local roles visible and verify open status, application
window, start timing, and country-specific work eligibility. Missing evidence
remains unknown.
Order visible vacancy lists by match score descending, using recency to break
ties. The owner confirmed that higher-rated vacancies should receive higher
priority; keep the 65-point notification threshold and do not promote
below-threshold roles ahead of higher-scoring results.
Do not copy the owner's personal relocation estimate into public repository
files.

Continue v3.5.7 on `feature/v3.5.7-international-market-coverage`. The owner
confirmed the Collectly Lever source through Telegram `/sources`, `/scan`, and
`/scanstatus`; next locate its result through `/review` or `/stretch` and
verify the `/job <id>` card's timezone and country-hiring caveat. `main` and
the latest formal tag/release remain v3.5.6; PR #18 remains a draft, and
current changes are not published. Continue auditing permitted remote and
Armenia/Georgia employer feeds after this card check.
The owner completed the Career-first GE/AM source check: Greenhouse returned
one Lineate Infrastructure Engineer vacancy for Georgia and sent one new
notification. `/job 1091` now displays a readable description and keeps
unsupported evidence unknown, as confirmed by the owner in Telegram. The official
posting requires at least 3 years of Linux system administration and 2 years
of production AWS, and includes a 24/7 shift schedule; it does not state
salary, work mode, visa sponsorship, or relocation assistance. Keep the
broad Relocation-first search intact. Do not claim visa or relocation support
without posting evidence. Do not make cold government emails a prerequisite.
Keep e-work/workforall and
`workpermit.am` out of automated collection until a relevant public feed or
authorized route appears. Staff.am and Job.am remain manual search
destinations under their current terms. Continue evaluating other permitted
employer ATS/public APIs and owner-selected Telegram channels. Georgia country
targeting alone does not establish legal eligibility. Do not store personal
citizenship details in public documents. Track the 90,000 RUB internship that
appeared despite the 100,000 RUB minimum: `/salary minimum` affects scoring,
not hard filtering, and that amount appeared only in description text. Resolve
that semantics/UI issue in a separate tested salary stage. Preserve source
pacing. The bounded Job Bank retry is already tested, deployed and recorded in
the current feature candidate; continue with permitted source coverage for
relevant Georgia/Armenia openings.

## Open limitations

- Source coverage remains the main Relocation-first bottleneck, especially Armenia and low-barrier legal work.
- Georgia adapters run only when `GE` is selected for a search profile.
  JOBS.GE's configured homepage returned HTTP 410 and is paused; HR.ge returned
  two live vacancies in the owner’s scan. Its robots file allows `/` and links
  a large sitemap, but recurring reuse permission remains unverified. On the
  v3.5.7 candidate Armenia is selectable and one Lineate Greenhouse board is
  connected for explicit AM/GE locations; broader Armenian source coverage
  remains open.
- Armenia has two government-listed vacancy platforms (e-work.am and
  workforall.am), but their public pages timed out and no API/access terms were
  verified. Automated integration is deferred; no agency email is required for
  this stage. Official registration prerequisites do not establish that
  foreigners are barred from applying directly to employers. Staff.am and
  Job.am remain manual search destinations unless their terms or an approved
  feed permit automated reuse. See `docs/developer/INTERNATIONAL_SOURCES.md`.
- The v3.5.7 candidate makes AM selectable and connects one current Lineate
  Greenhouse board for explicit Armenia/Georgia locations. The owner now
  confirmed one Career-first Infrastructure Engineer match in Georgia and
  accepted the readable `/job 1091` detail card. Broader Armenia source
  coverage remains open; the candidate stays on draft PR #18.
- Official Armenia `workpermit.am` enables employer-side processing for
  foreign hires and documents an EAEU work-permit exemption, but no anonymous
  vacancy feed/API is verified. Its FAQ question is visible but the answer is
  not rendered; the public guide documents employer-created vacancies and
  employer entry of the selected foreign worker. The portal says an EAEU
  worker may register for a lawful-residence certificate, but printing it
  requires a Public Services Number; this is separate from work-permit
  exemption. The app has no citizenship field and does not decide individual
  legal eligibility.
- Under Georgia's current Labour Migration Law, covered local paid work requires
  an employment agreement, a right to work obtained through the local employer,
  and the applicable D1/work-residence/other status. Country targeting does not
  establish eligibility. The bot does not currently decide individual legal
  eligibility.
- Arbeitnow may contain no low-barrier role matches. A later owner-provided
  Telegram scan confirmed the deployed single retry recovered from a
  `ReadTimeout` with HTTP 200. Continue monitoring future runs.
- The latest `/scanstatus` reports Job Bank at 99.5 seconds of a 162-second
  scan. Its five-second request pacing is intentional; any optimization must
  preserve the public crawl interval and be measured in a fresh Telegram scan.
- HH is mostly domestic and can return `403`; public fallback is expected, CAPTCHA must not be bypassed.
- `/salary minimum` is not currently a hard filter, despite the Telegram label.
  A detail view can mention a below-minimum amount in description text while
  the structured salary and salary score remain unknown; see the next salary
  semantics task in `ROADMAP.md`.
- EURES returned 16 vacancies in the owner-provided follow-up scan, with no SSL
  error reported for that run. Monitor additional scheduled runs; do not claim
  the transport cause is permanently resolved yet.
- The EURES cross-border flag is not proof of visa sponsorship, relocation support, or third-country work authorization.
- Public applicant counts are unavailable in the connected candidate-facing feeds and remain unknown.
- Dedicated Career Score and Relocation Score, affordability calculation, migration knowledge base, and application tracker are later phases—not completed features.
- Full remote control of the user's Arch machine exists only in a Codex CLI session started on that machine; cloud Codex cannot access `/home/roma`.

## Update protocol

After every completed stage, update this file—not the entire original long prompt:

1. change `Last updated`;
2. move delivered work into **Recently completed**;
3. replace verification counts/results with evidence from the latest run;
4. keep only unresolved items in **Open limitations**;
5. set exactly one practical **Current priority**;
6. add detailed chronology to `DEVELOPMENT_LOG.md` and durable follow-up items to `TASKS.md`.

Do not put secrets, exact passport data, private employment details, or other sensitive candidate information in this public repository.

## Compact startup request

```text
Read AGENTS.md and docs/PROJECT_OS/BRIEF.md first. Then inspect git status,
the latest commits, and only the detailed PROJECT_OS documents relevant to the
current priority. Verify claims against the code; do not restart or broadly
rewrite the project. Preserve .env, Docker volumes, the database, and dirty
user work. Continue the Current priority with tests. After a completed stage,
update BRIEF.md, DEVELOPMENT_LOG.md, TASKS.md, and HANDOFF.md with verified
facts. Report what changed, checks run, remaining limitations, and the exact
safe local deployment command.
```
