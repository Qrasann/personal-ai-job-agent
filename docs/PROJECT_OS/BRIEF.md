# Codex Brief

Last updated: 2026-10-11 (Europe/Moscow)

## Mission

Continue the existing Personal AI Job Agent. Maintain two independent tracks:

1. **Career-first** — DevOps / Infrastructure / SRE growth.
2. **Relocation-first** — any legal, verifiable work that can enable a realistic move; career fit is secondary.

Never restart the project from scratch. Unknown visa, salary, citizenship, housing, or relocation facts remain unknown; never convert missing evidence into `false` or a positive claim.

## Current runtime

- Checked-out feature source and running Compose image runtime are `3.5.7`;
  database schema remains `4/4`.
- GitHub `main` contains source version `3.5.6`; PR #15 and PR #16 are merged.
  The deployed application code is `170ed4e`; PR #16's later commits only
  updated documentation. The merge is recorded at
  https://github.com/Qrasann/personal-ai-job-agent/pull/16.
- Branch map: `main` is the stable source at `02f582e`; the current working
  branch is `feature/v3.5.7-international-market-coverage`, created from that
  main commit. Its candidate `VERSION` is `3.5.7`; `main` and the deployed
  Compose app remain `3.5.6`. `feature/v3.5.6-eures-identity-market-targets`
  is merged and inactive; `feature/v3.5.2-dual-search-modes` is an older branch.
- Release map: `VERSION=3.5.6` and the latest formal GitHub tag/Release are
  v3.5.6. Changelog entries v3.5.2–v3.5.5 are cumulative milestones included
  in that release; do not backfill intermediate tags.
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
- Added explicit Telegram resume import for PDF/DOCX/TXT, plus fact confidence/provenance and overlap review.
- Added persisted Recommendation v2 component breakdown with unknown values
  left unset and displayed in vacancy details.
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
  pushed; push CI `38150088881` and PR CI `38150092577` passed. Deployment is
  pending. The live bot still runs `7a6901d` until the safe updater applies it.

## Verified

- Latest full isolated PostgreSQL suite: `247 passed`, 68.36% branch coverage
  (55% gate), including experience wording, required Windows/Databricks
  signals, and earlier regressions. Compilation and `git diff --check` pass.
  Required-section commit `7a6901d` passed push CI `38149543660` and PR CI
  `38149546515`; follow-up `678ddfc` passed push CI `38150088881` and PR CI
  `38150092577`.
- Local Compose check: source/runtime `3.5.7`, app polling, PostgreSQL healthy.
  Mount inspection confirms `repo_jobagent_v3_pg` and `repo_jobagent_v3_files`
  remain attached. The startup scan completed at 13:31:05 UTC; EURES returned
  HTTP 200 and no errors appeared in the inspected tail. The owner later
  confirmed `/sources` enabled Greenhouse for Relocation-first GE/AM; the
  Greenhouse request returned HTTP 200 and zero query-matched jobs. The
  currently selected relocation roles do not include Infrastructure Engineer.
- The safe updater applied `7a6901d` to Compose project `repo`; PostgreSQL is
  healthy. Its startup `scan_all` completed successfully from 15:02:28 to
  15:04:57 UTC. Commit `678ddfc` is not yet deployed; inspect its startup scan
  after CI passes and the safe updater applies it.
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
  of the rescored `/job 1091` is still needed. Keep PR #18 draft; v3.5.7 remains
  unmerged and unreleased. Latest PR head is `7a6901d`; push CI `38149543660`
  and PR CI `38149546515` passed.
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

Treat relocation search as time-sensitive: prioritize currently open roles,
clear application windows, realistic hiring/start timing, and explicit
country-specific work eligibility. Keep unverified dates and support unknown.
Do not copy the owner's personal relocation estimate into public repository
files.

Continue v3.5.7 on `feature/v3.5.7-international-market-coverage`. The bounded
Job Bank retry is fully tested, pushed and deployed. `main` and the latest
formal tag/release remain v3.5.6; PR #18 remains draft. The next product stage
is permitted source coverage for relevant Georgia/Armenia openings, followed
by verification of each live role's location, timing and eligibility evidence.
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
