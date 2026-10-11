# Handoff

## v3.5.7 Lineate Recommendation v2 HTML normalization — 2026-10-11

The owner reopened `/job 1091` after the singular qualification-heading fix
and reported Technical 42 but interview risk `н/д`. The detail route calculated
Technical Score using decoded vacancy text, while Recommendation v2 rescored
the raw stored HTML. This second path therefore missed the required section.

Commit `8a583c7` passes the same normalized description into both calculations.
The encoded Greenhouse regression expects Technical 42 and interview risk 58.
Verification passed: 245 local unit tests (3 PostgreSQL tests skipped), 248
tests with isolated PostgreSQL, 68.36% branch coverage, `compileall`, and
`git diff --check`. Push CI `38151840822` and PR CI `38151843490` passed.

The safe updater deployed the candidate to Compose project `repo`. Source and
runtime report 3.5.7; PostgreSQL is healthy. Startup `scan_all` ran from
15:35:45 to 15:38:13 UTC and completed successfully. The five-minute log check
found no source errors, SSL errors, timeouts, or tracebacks. HH API returned
403, then the ordinary public web fallback succeeded.

**Telegram check still needed:** reopen `/job 1091` and share the Technical and
interview-risk lines. The regression expects the risk to be 58 for the current
stored Lineate requirements. Salary, work mode, visa sponsorship and relocation
support remain unknown without direct posting evidence.

The active branch is `feature/v3.5.7-international-market-coverage`; PR #18
remains an unmerged draft against `main`. Stable `main` and the latest formal
release/tag remain v3.5.6. No v3.5.7 tag or release has been made. No schema,
credential or Docker-volume changes were made.

## v3.5.7 Lineate singular qualification heading — 2026-10-11

The owner reopened `/job 1091` at 18:20 Moscow time. The card still showed
Technical 100 and interview risk `н/д` even though it displayed “Minimum 3
years.” Inspection of the saved public Greenhouse description identified the
exact cause: it uses `Necessary Qualification` (singular), while the parser
recognized only `Necessary Qualifications` (plural). The unqualified fallback
therefore produced the technical score and no interview-risk evidence.

Commit `e978d07` adds singular and plural English qualification headings. The
regressions cover the singular Lineate text after Greenhouse HTML-entity
decoding, Technical Score v2, and Recommendation v2 interview risk. Local
tests: 245 passed, 3 PostgreSQL tests skipped; full isolated PostgreSQL suite:
248 passed, 68.36% branch coverage. Compile and `git diff --check` passed.
Push CI `38151153964` and PR CI `38151157085` passed.

The safe updater deployed the candidate to Compose project `repo` at 18:25:57
Moscow time. Source/runtime is 3.5.7 and PostgreSQL is healthy. Startup
`scan_all` ran from 15:26:05 to 15:28:27 UTC and completed successfully.
Greenhouse, EURES search/details, HR.ge, and Job Bank requests shown in the
log window returned HTTP 200. HH API returned 403, then the ordinary public
web fallback succeeded. The inspected scan logs contain no source errors,
SSL failures, timeouts, or tracebacks.

The owner should now reopen `/job 1091` and share the Technical score and
interview-risk line to verify the live result. Salary, work mode, visa
sponsorship, and relocation assistance remain unknown unless the posting
provides explicit evidence. The active branch is
`feature/v3.5.7-international-market-coverage`; PR #18 remains an unmerged
draft against `main`. Stable `main`, the formal release, and latest tag remain
v3.5.6. No schema migration, credential change, or volume change was made.

## v3.5.7 Lineate minimum experience and required signals — 2026-10-11

The follow-up to the Lineate card review is committed as `678ddfc` and pushed
on `feature/v3.5.7-international-market-coverage`. It extracts English
`Minimum N years` / `At least N years` text, recognizes Windows and Databricks
in vacancy technical evidence, and checks that a 3-year Lineate-style
requirement is compared with commercial candidate experience. Candidate Facts
remain the source of claims about the candidate; the parser does not invent
AWS-specific years or assert visa/relocation details.

Verification passes: 247 PostgreSQL-backed tests, 68.36% branch coverage,
compileall, and `git diff --check`. Push CI `38150088881` and PR CI
`38150092577` passed. Docs commit `664c559` passed push CI `38150288518` and
PR CI `38150292566`. The safe updater deployed the candidate to Compose project
`repo`: source/runtime 3.5.7 and PostgreSQL healthy. Startup scan completed at
15:15:48 UTC. The inspected logs show the expected HH API 403 followed by the
public fallback and no source errors, SSL failures, timeouts or tracebacks.
The owner still needs to reopen `/job 1091` and share the updated score,
experience signal and interview-risk details.

PR #18 remains an unmerged draft against `main`. The active candidate is v3.5.7;
stable `main` and the formal tag/release remain v3.5.6.

## v3.5.7 Lineate required-qualification scoring — 2026-10-11

The official [Lineate Infrastructure Engineer posting](https://job-boards.greenhouse.io/lineate/jobs/8018252)
is for the Georgian office and explicitly requires at least 3 years of Linux
system administration, 2 years of AWS in production, and participation in a
24/7 shift schedule. The previous card showed Technical 100 because the
deterministic parser did not classify the posting's `Necessary Qualifications`
heading as required; interview risk therefore appeared as `н/д`.

Commit `7a6901d` adds the common English required-qualification headings to the
section parser. Technical Score v2 and Recommendation v2 now use recognized
required technical signals, while absent Candidate Facts stay unknown. The
full isolated PostgreSQL suite passes (246 tests, 68.29% branch coverage), and
compile plus `git diff --check` pass. Push CI `38149543660` and PR CI
`38149546515` passed.

The safe updater deployed the candidate to Compose project `repo`; source and
runtime report 3.5.7, the app is polling, and PostgreSQL is healthy. Startup
`scan_all` ran from 15:02:28 to 15:04:57 UTC and completed successfully. HH's
API returned 403 before the public web fallback succeeded; Greenhouse, EURES,
HR.ge, Job Bank, Arbeitnow and Remote OK requests shown in the logs returned
HTTP 200. No source error appeared in the inspected scan tail. Owner review of
the rescored `/job 1091` remains pending.

The candidate remains on `feature/v3.5.7-international-market-coverage` with
PR #18 open as a draft against `main`. Stable `main` and the latest formal
release/tag remain v3.5.6. No merge or release has been made.

## v3.5.7 Job Bank transport resilience — 2026-10-11

The owner opened `/job 1091` for Lineate's Infrastructure Engineer opening.
The card correctly left salary, work mode, and unsupported visa/relocation
claims unknown, but displayed the Greenhouse description as escaped markup
(`&lt;p&gt;`, `&lt;ul&gt;`). `clean_html_text` now decodes HTML entities before
stripping tags; regressions cover both Greenhouse evidence extraction and the
Telegram detail renderer. The full isolated PostgreSQL suite passes: 241
tests, 68.23% branch coverage. Compilation and `git diff --check` pass.

Commit `5d6b00b` is pushed on
`feature/v3.5.7-international-market-coverage`; push CI `38147877309` and PR
CI `38147879757` passed. The safe `./job-agent update` deployed it to Compose
project `repo`. Source/runtime is 3.5.7, PostgreSQL stayed healthy, and startup
`scan_all` completed at 14:40:12 UTC. EURES search/detail requests returned
HTTP 200; the inspected log window had no source errors or SSL failures.

The owner reopened `/job 1091` after deployment and confirmed that the
description is readable. Salary, work mode, and unsupported visa/relocation
claims remain unknown. Telegram acceptance for the Lineate discovery and detail
rendering is complete.

To handle the earlier Relocation-first Job Bank `ConnectTimeout`, commit
`36c425b` adds one retry for `httpx.TransportError` under the existing shared
request lock, with the existing five-second delay before each attempt. HTTP
status errors are not retried. Job Bank tests pass (15); the full isolated
PostgreSQL suite passes (244 tests, 68.26% branch coverage), as do compilation
and `git diff --check`. Push CI `38148615302` and PR CI `38148617896` passed.

The safe updater deployed commit `36c425b` to Compose project `repo`. Source
and runtime report 3.5.7; PostgreSQL is healthy. Startup `scan_all` completed
at 14:51:38 UTC. Job Bank search and 12 detail requests and EURES search/detail
requests returned HTTP 200; no source or scan errors appeared in the inspected
logs. No transport error occurred during this scan, so live retry recovery was
not triggered; the bounded behavior is covered by regressions. No schema,
credential, production-data or Docker-volume changes were made.

The checked-out candidate is on
`feature/v3.5.7-international-market-coverage`; PR #18 remains open and draft
against `main`. Stable `main`, the formal release and latest tag remain
v3.5.6. No v3.5.7 merge, tag or release has been made. The next product stage
is to review permitted employer ATS feeds and owner-selected Telegram sources
for relevant Georgia/Armenia openings, while preserving the separate search
profiles and evidence rules.

## v3.5.7 owner Career-first GE/AM scan — 2026-10-11

The owner ran `/targets career GE,AM`, `/sources`, `/scan`, and `/scanstatus`.
Career-first used GE/AM and received one new notification: Lineate,
Infrastructure Engineer, source `greenhouse`, market `GE`, Match 67/100. The
bot labeled work mode `unknown`. Scan counts were HH 209, Remote OK 3,
Arbeitnow 2, Job Bank 0, EURES 16, Greenhouse 1, and HR.ge 2. Career-first
processed 172 vacancies (31 Good, 33 Stretch); Relocation-first processed 61
(0 Good, 0 Stretch). EURES worked without an SSL error in the supplied logs.
Job Bank failed only for Relocation-first with `httpx.ConnectTimeout` and took
29.2 seconds; the scan completed and other sources continued.

The current [official Lineate posting](https://job-boards.greenhouse.io/lineate/jobs/8018252)
identifies a Georgian office, requires at least 3 years of Linux system
administration and 2 years of AWS in production, and includes a 24/7 shift
schedule. The posting does not state salary, work mode, visa sponsorship, or
relocation assistance. These remain unknown. The bot sent one notification.
The owner later opened `/job 1091` and confirmed the deployed description is
readable while unsupported facts remain unknown; the result is recorded at the
top of this handoff. PR #18 remains a draft. No database/schema or volume
change was made.

## v3.5.7 owner Telegram source check — 2026-10-11

The owner checked Relocation-first GE/AM with `/sources`, `/scan`, and
`/scanstatus`. Greenhouse · Lineate was enabled and the public endpoint returned
HTTP 200, but produced zero role matches. This is consistent with the profile
settings: Career-first has no selected markets, while Relocation-first is
searching broad non-technical roles. EURES returned 16 vacancies and the
supplied scan log contains no EURES SSL failure; keep monitoring later scans.
The full scan ran from 14:03:57 to 14:06:34 UTC and returned HH 209, Remote OK
3, Arbeitnow 2, Job Bank 12, EURES 16, Greenhouse 0, and HR.ge 2. Job Bank took
about 100.5 seconds.

The owner subsequently ran `/targets career GE,AM`, `/sources`, `/scan`, and
`/scanstatus`, then inspected Lineate with `/job 1091`; see the current
acceptance result above. This added Georgia/Armenia only to Career-first and
preserved Relocation-first's broad role search. Do not infer visa or relocation
support from country targeting or the Greenhouse source. PR #18 remains a draft.
No database schema or Docker-volume change was made.

## v3.5.7 source and vacancy realism review — 2026-10-11

The active branch `feature/v3.5.7-international-market-coverage` starts from
main commit `02f582e`; application commit `4ccae7f` was pushed. Stable `main`
and the formal tag/Release remain v3.5.6. Draft PR #18 is open; GitHub push CI
`38143185017` and PR-CI `38143789063` passed all jobs at that earlier head. The
latest PR checks are recorded above. The safe updater applied
candidate source/runtime 3.5.7 to
local Compose. The app is polling, PostgreSQL is healthy, and read-only mount
inspection confirms `repo_jobagent_v3_pg` and `repo_jobagent_v3_files` remain
attached. Startup scan completed at 13:31:05 UTC; EURES returned HTTP 200 and
no errors appeared in the inspected tail. The owner's later Telegram scan
confirmed Greenhouse is enabled for Relocation-first GE/AM and returned HTTP
200; zero vacancies matched the broad relocation role queries.

The v3.5.7 candidate adds selectable country AM and a bounded public
Greenhouse Job Board API adapter for Lineate. It scans only when the active
profile selects Armenia or Georgia, filters by role query and explicit posting
location, and does not infer salary, work mode, visa sponsorship or relocation
support. Targeted source/country/preference tests pass: 20. The full isolated
PostgreSQL suite passes: 240 tests, 68.22% branch coverage; compileall and
`git diff --check` pass. Deployment is complete; owner Telegram acceptance
for live technical role/location matching remains outstanding. No schema
migration was made.

Official Armenian `workpermit.am` describes an employer-led vacancy and
foreign-hiring/work-residence procedure and states that EAEU citizens working
in Armenia are exempt from work-permit documentation for the employment
contract period. The FAQ displays “How to find a job using this Platform?” but
its answer is absent from the public response; the official guide documents an
employer-created vacancy and employer entry of the selected foreign worker.
The portal separately says an EAEU worker may register for a lawful-residence
certificate, but printing it requires a Public Services Number; this does not
cancel the work-permit exemption and should be handled as a separate residence
step.
The Unified Social Service's labor-market page explicitly lists e-work.am and
workforall.am for vacancies, but their public search pages were not readable in
the checks and no feed/reuse permission is confirmed. Defer automated
integration and do not make cold outreach to the agencies a release
prerequisite. Official state-service registration requirements do not establish
a general ban on direct applications to employers. Georgia's current Labour
Migration Law requires, for covered local paid work, an employment agreement,
a right to work via the local employer, and the applicable immigration status.
Country targeting does not establish individual eligibility.

The owner also showed `/job 580`: the full description contains 90,000 RUB,
while structured salary stays unknown and `/jobs` displays “not specified.”
`/salary` calls 100,000 RUB a minimum “for filter,” but current matching uses
that value as a scoring input when structured salary exists; it is not a hard
floor. This should be clarified or deliberately implemented as a separate
tested change before the bot claims to filter below-minimum jobs.

No agency contact was sent, and none is required for this release. Keep
e-work/workforall and workpermit.am out of automated discovery until a relevant
public feed or authorized access route is identified. Staff.am and Job.am are
manual search destinations under their current terms. Continue source work
with permitted employer ATS feeds, documented APIs, and owner-selected
Telegram channels. Source references and constraints are in
`docs/developer/INTERNATIONAL_SOURCES.md`. Personal citizenship details are
not copied into public repository documents.

## GitHub branches and release labels — 2026-10-11

- `main` is the stable source branch at v3.5.6. PR #15 and
  [PR #16](https://github.com/Qrasann/personal-ai-job-agent/pull/16) are merged;
  merge CI run `38135649948` passed.
- The local checkout is on `feature/v3.5.7-international-market-coverage`,
  created from stable `main` commit `02f582e`. Application commit `170ed4e` is
  deployed to Compose project `repo`; later PR #16 commits updated
  documentation only.
- `feature/v3.5.2-dual-search-modes` remains on the remote from earlier work;
  it is not the active branch for new changes.
- The merged `feature/v3.5.6-eures-identity-market-targets` branch is inactive.
  The v3.5.7 source and market-coverage work stays on the current feature
  branch until it is reviewed, tested, and merged into `main`.
- Latest formal GitHub Release/tag: v3.5.6 on release commit `50afdab`. Main CI
  run `38138941745` passed. Changelog entries v3.5.2–v3.5.5 are cumulative
  milestones included in the release; no intermediate tags were backfilled.
- Bilingual release notes: https://github.com/Qrasann/personal-ai-job-agent/releases/tag/v3.5.6.
- README.md and README.ru.md provide English and Russian entry points on `main`.

## Owner Telegram acceptance — 2026-10-11

The owner completed `/import` and Recommendation v2 smoke checks. The upload
prompt appeared, ZIP was rejected, and two previously imported documents were
recognized as duplicates. `testcv.txt` was saved as resume #6 with zero facts
added. In the implementation, a resume is persisted only from the callback on
the preview card, so the successful save response confirms the confirmation
path was exercised. `/job 580` displayed the Recommendation v2 breakdown;
unsupported growth, fast-start, interview-risk, remote, security,
infrastructure, and competition signals remained `н/д`. The supplied app log
shows the scheduled scan completed at 12:12:59 UTC and the Telegram update was
handled successfully.

These checks close the final v3.5.6 release gate. Future source work starts
from `main` on a new v3.5.7 feature branch.

## Owner Telegram scan and source-resilience follow-up — 2026-10-11

Post-deployment logs confirmed Arbeitnow's Relocation-first retry recovered
from `ReadTimeout` with HTTP 200; EURES, HR.ge, Job Bank, and HH requests shown
also succeeded. JOBS.GE was not requested. The 162.7-second Telegram update is
now attributed by `/scanstatus`: Job Bank took 99.5 seconds, Arbeitnow 17.1,
EURES 14.5, HR.ge 13.0, HH 7.6, and Remote OK 1.5. Keep the current Job Bank
request pacing until a safe optimization is verified against its source rules.

The owner ran `/targets relocation GE`, `/sources`, `/scan`, and `/scanstatus`.
`/sources` visibly marks JOBS.GE temporarily paused after HTTP 410; HR.ge remains
enabled for GE. The completed scan returned HH 209, Remote OK 3, Arbeitnow 2,
Job Bank 12, EURES 16, and HR.ge 2. Source timings were HH 7.6s, Remote OK
1.5s, Arbeitnow 17.1s, Job Bank 99.5s, EURES 14.5s, and HR.ge 13.0s. The scan
ran from 09:47:54 to 09:50:36 UTC. The prior log's 162.7-second Telegram
update is consistent with the scan duration; Job Bank is the main measured
latency contributor.

The candidate adds regressions for transient timeout recovery, retry
exhaustion, non-retry of HTTP status failures, and the paused source-plan state.
Full isolated PostgreSQL suite: 233 passed, 67.67% branch coverage;
`compileall` and `git diff --check` passed. Commit `170ed4e` is published on PR
#16; push CI `38129138392` and PR CI `38129141546` passed. The safe updater
applied it. Runtime remains 3.5.6, the app is up, PostgreSQL is healthy, and
the startup scan completed. Arbeitnow, EURES, and HR.ge requests returned HTTP
200; no JOBS.GE request or source error appeared. Mount inspection confirms
`repo_jobagent_v3_pg` and `repo_jobagent_v3_files` remain attached. No schema
change was made.

The manual scan exercised and verified Arbeitnow retry recovery. A later log
tail showed scheduled `scan_all` completed and Telegram updates were handled in
117–677 ms, with no errors in that excerpt. Keep Job Bank's five-second
request pacing until a measured optimization is tested. Keep `.env`, the
database, and existing Compose volumes untouched.

Prior Georgia guardrail commits are published on PR #16 at `0110173`,
following adapter change `2963705`. Push CI `38127150025` and PR CI
`38127152783` passed for that prior head, and its safe updater deployment was
verified before the owner scan. The owner supplied the live Georgia source
result described above. Georgia detail collection is capped at six per source,
uses 15-second timeouts and two-second pacing, preserves partial detail results,
and caches scheduled scans for six hours. Manual `/scan` forces fresh
discovery. Role matching requires a specific query token; HR.ge salary enters
scoring only with an explicit currency and monthly period. Work mode and
relocation remain unknown without source evidence.

Access review: JOBS.GE `/robots.txt` returned HTTP 410, so crawl rules are not
available. HR.ge `/robots.txt` returned HTTP 200 and allows `/`, with a link to
a 5.4 MB sitemap that the adapter does not download. These results do not
grant permission to reuse listings; recurring automated extraction terms
remain unverified. The adapters stay limited to Georgia-targeted profiles.

The source/runtime version remains 3.5.6 while v3.5.7 market-coverage work is
planned. JOBS.GE access and HR.ge
reuse terms remain unresolved; do not treat the boards as validated recurring
sources until access conditions are reviewed.

The release map is intentional: `VERSION=3.5.6` describes source code, and
v3.5.6 is the cumulative formal release. Entries v3.5.2–v3.5.5 are included
milestones; do not backfill intermediate tags.

## v3.5.6 candidate update — PR #16 (2026-10-11)

Candidate commit `6fa3406` is published on
`feature/v3.5.6-eures-identity-market-targets` as [PR #16](https://github.com/Qrasann/personal-ai-job-agent/pull/16).
At the time of this candidate update, the application and handoff changes
passed push and PR CI while GitHub `main` remained at `6294c2a`. PR #16 was
later merged into `main` at `874b372`; that merge and its CI are recorded at
the top of this handoff. The candidate and deployed app report source/runtime
v3.5.6. At that point the latest release/tag was v3.5.1; the owner later
completed acceptance and v3.5.6 was published as recorded above.

EURES failed while reading compressed response bodies in the running container.
A direct request reproduced the TLS record-layer error with default encoding;
the same request using `Accept-Encoding: identity` read all 50 result records.
The adapter now requests identity encoding. After the safe update, the first
startup dual-profile scan completed (`scan_all` executed successfully); EURES
search and detail requests returned HTTP 200, with no SSL retries/errors in the
run. Continue monitoring later scheduled scans because the underlying network
cause is not yet established.

`/targets GE` now applies target countries to all active profiles;
`/targets relocation GE` and `/targets career GE` scope the change. `/sources`
lists each active profile's configured source plan. Georgia adapters are
included only for profiles targeting GE. The owner subsequently ran the GE
scan; the latest result and post-update source checks are recorded above.
The candidate adds AM to the country catalog and connects Lineate's public
Greenhouse board for AM/GE. Its current Infrastructure Engineer vacancy is
listed for a Georgian office; no current Armenia vacancy matches the active
DevOps/Infrastructure queries on that board. The Unified Social Service lists
e-work.am and workforall.am, but both public search pages timed out and no
public API/feed or automated-access terms were verified. Official registration
requirements apply to the state service and do not establish a general ban on
direct employer applications. Government outreach is deferred, not a release
prerequisite. Staff.am prohibits automated scraping without permission;
Job.am restricts unauthorized reuse and redistribution, so both remain manual
search destinations. See
`docs/developer/INTERNATIONAL_SOURCES.md` and the v3.5.7 plan in `ROADMAP.md`.

The full isolated PostgreSQL suite passed: 224 tests, 66.33% branch coverage;
compileall and `git diff --check` passed. Compose reports the app polling and
PostgreSQL healthy. Mount inspection confirms `repo_jobagent_v3_pg` and
`repo_jobagent_v3_files` remain attached. No database migration was added.

At the time of this candidate note, owner acceptance was still outstanding.
The owner later completed the resume-import and Recommendation v2 checks above.

## v3.5.6 main merge and Telegram smoke test — 2026-10-11

GitHub PR #15 is merged into `main` at `062eb253bdf8435782e5fcca6cfb1257b271ea86`;
the branch now contains v3.5.6. The full PostgreSQL suite passes (220 tests,
65.66% branch coverage), and final push/PR CI runs `38121905782` and
`38121908521` passed.

Owner-provided real-chat smoke results confirm `/salary`, `/blacklist`,
`/scanstatus`, `/cancel`, the `/import` upload prompt, `/version` (v3.5.6,
schema 4/4, migration OK), and `/status` (ACTIVE). The reported scan completed;
EURES failed after retries while the other configured sources returned results.
At this point in the release history, file-based `/import` and Recommendation
v2 details had not yet been exercised in the owner's chat; both were completed
later, as recorded at the top of this handoff.

The running Compose app reports source/runtime 3.5.6 and PostgreSQL healthy;
the existing `repo_jobagent_v3_pg` and `repo_jobagent_v3_files` volumes remain
attached. Recent logs show intermittent EURES TLS record-layer failures mixed
with successful HTTP 200 responses. Retries and partial-result handling work,
but EURES is still an occasional source-level failure; the latest scheduled
scan completed and other sources continued.

## Current stage — v3.5.6 Recommendation Model v2 (2026-10-11)

Each new or refreshed match stores a JSONB evidence breakdown for technical,
growth, fast-exit, interview-risk, salary, remote, relocation, security,
infrastructure and competition signals. Vacancy details show the components
and evidence. Missing evidence stays `null`; public candidate counts and
employer security signals are not fabricated. The old composite score and
notification thresholds remain unchanged until labeled outcomes are available
for calibration. Migration 4 adds only `job_matches.recommendation_scores`.
Full isolated PostgreSQL suite: 220 passed, 65.66% branch coverage. Commit
`496c920` is published and deployed; runtime reports 3.5.6, schema 4/4, healthy
PostgreSQL and active polling. Existing PostgreSQL and storage volumes remain
attached. Real-chat acceptance was still required at this stage and was
completed later, as recorded at the top of this handoff.

## Current stage — v3.5.5 Candidate Import & Profile Sync (2026-10-11)

Implemented `/import` for PDF, DOCX and TXT. Uploads are read in memory and
bounded by size, page, text and DOCX archive limits. Telegram displays a safe
preview of proposed facts and requires an explicit save choice; only then does
the app store extracted resume text and, optionally, proposed facts. It does
not store uploaded binary data or original filenames. Fact proposals are
section-scoped, carry confidence and `resume_import` provenance, and retain
`unknown` experience type. Exact duplicates are skipped; overlaps are flagged
and never replace existing facts.

Migration 3 only adds `confidence` and `provenance` columns to `candidate_facts`;
existing rows receive defaults and are preserved. Full isolated PostgreSQL
suite: 217 passed, 65.15% branch coverage; unit suite: 214 passed, 3 skipped.
Commit `8131e2e` is published and applied with the safe tracked-branch update.
Compose reports runtime 3.5.5, schema 3/3, healthy PostgreSQL and active bot
polling. Inspection confirmed the existing `repo_jobagent_v3_pg` and
`repo_jobagent_v3_files` volumes remain attached. Startup logs showed an
intermittent EURES SSL retry while other sources continued.
Owner-driven Telegram acceptance for `/import` and the outstanding controls
(`/salary`, `/blacklist`, `/scanstatus`, `/cancel`) remains pending before
release tagging.

## Follow-up — raw EURES SSL error (2026-10-11)

The raw `ssl.SSLError` retry fix is published and deployed as `d5d78d3`; logs
showed retry warnings and HTTP 200 responses after retries, but one profile
still exhausted its attempts. Partial-result handling is published and
deployed as `8a87604`; it continues across failed queries/details and retains
successful results, while still reporting a source failure when all searches
or all matching detail requests fail. The full suite passes (208 tests,
64.51% branch coverage). The startup scan showed retry recovery to HTTP 200,
but one profile exhausted retries for every EURES search query and correctly
reported EURES unavailable; Job Bank and other sources continued. PostgreSQL
remained healthy and existing volumes remained attached. The next practical
task is owner-driven Telegram acceptance for `/salary`, `/blacklist`,
`/scanstatus`, and `/cancel`.

## Current stage — source error resilience (2026-10-11)

Latest runtime inspection found EURES transport failures (`ReadTimeout` and an
SSL record-layer error) and a blank Job Bank Telegram alert. EURES now retries
transport-level failures twice with short backoff; HTTP status responses are
not retried. Source failure alerts share the normalized text saved in the scan
summary, including HTTP status codes. Regression tests cover both behaviors.
The isolated PostgreSQL suite passed: 206 tests, 64.46% branch coverage.
Published as `f397f58` and applied with
`JOB_AGENT_COMPOSE_PROJECT=repo ./job-agent update`. Runtime/source report
3.5.4, PostgreSQL is healthy, the bot is polling, and the startup EURES search
returned HTTP 200. Inspection confirmed `repo_jobagent_v3_pg` and
`repo_jobagent_v3_files` remain attached. The update command fetches/pulls
fast-forward-only and rebuilds the currently running service without removing
the database or volumes.

At the time of this v3.5.4 note, owner-driven Telegram acceptance for
`/salary`, `/blacklist`, `/scanstatus`, and `/cancel` remained outstanding. The
owner later supplied those real-chat results; the acceptance is recorded in
the v3.5.6 handoff above.

## Current deployment — v3.5.4 EURES discovery

The working tree adds bounded EURES search for vacancies whose employer has
enabled the EURES cross-border recruitment flag. This flag is evidence of
interest in hiring across EURES countries only; it is not visa sponsorship,
relocation support, or third-country work authorization. The live public search
and detail endpoints returned HTTP 200. The implementation is published at
`1dc62366fcca46e778d6650928b1fd4c91c2d5cd`; GitHub Actions run 110 passed. The
full isolated PostgreSQL suite passed (203 tests; 64.39% branch coverage), and
Compose project `repo` reports source/runtime 3.5.4. The startup scan reached
EURES successfully. Existing PostgreSQL and storage volumes remain attached.
At that stage Telegram acceptance remained a separate owner task. It was later
completed and the cumulative v3.5.6 release includes these untagged milestones.

The v3.5.3 public competition-signal item has been audited: HH response counts
require employer-side access, Job Bank applicant tables live in the employer
dashboard, and EURES exposes number of positions rather than applicant counts.
No connected public source currently supplies reliable per-vacancy applicant
counts, so the agent does not infer or fabricate one.

## Prior v3.5.3 deployed state — 2026-10-11

Code release commit: `e4fa198f63d07a5120f6e480b63a7be9cdb46efd` on
`feature/v3.5.2-dual-search-modes`. GitHub Actions runs 105–108 passed.
`VERSION` and `CHANGELOG.md` identify the implementation as 3.5.3. The `repo`
Compose app is polling as `@roma_job_agent_bot` on runtime version 3.5.3; the
startup dual-profile scan completed successfully at 21:11:40 UTC, including
live Job Bank queries/details. Existing named PostgreSQL and storage volumes
are preserved.
Latest PostgreSQL suite: 197 passed, 63.80% branch coverage. v3.5.3 Fast Scan
uses three concurrent discovery slots, source-level timing and 180-second
timeouts, sequential priority-ordered ingestion, persistent manual dashboard,
`/scanstatus`, and `/cancel`.

Remaining release acceptance is an owner-driven Telegram chat check for
`/salary`, `/blacklist`, `/scanstatus`, and `/cancel`. No real-chat command
verification was available in this session. Do not tag v3.5.2 or v3.5.3 until
this acceptance is complete.

## Latest stage — salary and blacklist controls

Telegram `/salary` and `/blacklist` were added in the published 3.5.2 stage.
Minimum salary uses the existing `minimum_salary` scoring setting; current and
desired salary are kept separately. Both controls apply to each active profile.
No schema migration is needed.

`testsbuild` is 11 commits ahead and one behind `main` (diverged). Saved queue
navigation is already present in this branch; do not merge testsbuild wholesale.

## v3.5.3 Fast Scan & Scan Dashboard implementation

Review current source-specific delays first, especially Job Bank's five-second
crawl delay. Fast Scan should bound concurrent discovery, keep database
ingestion and matching ordered, and retain per-source errors/timings. A
persistent latest-run dashboard can use `runtime_state` without a destructive
schema change. Add `/scanstatus` and ensure `/cancel` does not interrupt HH
message composition behavior. Verify with mocked concurrency/cancellation
tests, the full PostgreSQL suite, and local Compose logs.

### Implemented in the current working stage

- Discovery for independent adapters runs with a limit of three in parallel;
  ordering, filtering, and database ingestion remain sequential by source
  priority.
- Each source has a 180-second timeout. Failures are isolated and included in
  the source summary, and successful sources still finish processing.
- Manual scan state/progress/results persist in the existing `runtime_state`
  table. `/scanstatus` shows the latest state and source timings; `/cancel`
  stops an active manual scan and still clears the HH reply composer.
- Existing source discovery caching remains in place. Job Bank's internal
  crawl pacing is unchanged.

The full PostgreSQL test suite passed: 197 tests, 63.80% branch coverage.
The implementation is published and deployed. The live startup scan completed
at 21:04:51 UTC; the next check is the owner-driven Telegram command acceptance.

For v3.5.2 dual-mode review:
1. read CURRENT_STATE.md and TASKS.md;
2. inspect app/search/preferences.py;
3. inspect app/telegram/settings_handlers.py and settings_ui.py;
4. inspect the small integrations in app/services.py and app/main.py;
5. inspect `discovery_queries` and `search_strategy` in app/search/preferences.py;
6. run the full PostgreSQL-backed pytest suite;
7. launch the bot in a test Telegram chat;
8. verify `/settings`, all three strategies, `/relocationroles`, source/country/city controls and relocation policies;
9. verify `/scan` uses career queries in career-first, relocation queries in relocation-first, and both in balanced;
10. verify `/scan` behaves like v3.5.1 when no relocation roles or new geography controls are configured.
11. run `/parallelsearch on`, confirm two active profiles, then verify one `/scan` reports both profile names in progress;
12. run `/parallelsearch off`, confirm only Career-first remains active, then enable it again and confirm relocation settings survived.

Local release clones can update their tracked branch with `JOB_AGENT_COMPOSE_PROJECT=repo ./job-agent update`; the command refuses dirty worktrees, detached HEADs and branches without an upstream.

Current branch: `feature/v3.5.2-dual-search-modes`, based on `origin/feature/v3.5.2-search-control`.
No database migration is required; new keys are stored in the existing JSON settings field.
Rollback is limited to the dual-mode commit/files because legacy `queries` remain unchanged.

Earlier verification on 2026-10-10: 175 pytest tests passed against isolated
PostgreSQL 16; branch coverage 63.22% (gate 55%). Subsequent startup, parallel
profile activation and dual-profile scan smoke tests passed locally, as recorded
in DEVELOPMENT_LOG.md. Remote CI and Telegram acceptance were completed in
later release stages; read `BRIEF.md` first for the current concise state.

Parallel search is opt-in. The existing profile becomes `Career-first`; one
`Relocation-first` profile is created and reused. Disabling parallel search
sets that profile inactive and does not delete its settings or JobMatch rows.

Do not merge testsbuild wholesale. Compare it with main and port selected functionality with tests.

## Job Bank source stage — 2026-10-10

Baseline HEAD: `7c987da`; this stage adds local changes on the same branch.
Review `app/sources/adapters/jobbank.py`, its service/registry integration,
`tests/test_jobbank.py` and `docs/developer/INTERNATIONAL_SOURCES.md`.
The adapter uses the active profile's queries and respects source/geography
controls and relocation mode. Eligibility restrictions are explicit exclusions;
missing support stays unknown. LMIA is never equated with sponsorship approval.
No schema migration, automated application or private HH action was added.
Live adapter check returned one international warehouse-worker vacancy with
LMIA requested and unknown sponsorship. DWP currently returns a service-error
page and was deferred.

Final local verification: 191 tests passed against isolated PostgreSQL 16,
64.16% branch coverage (gate 55%); Python compilation and `git diff --check`
passed. The local .venv uses Python 3.14; the deployment image remains Python
3.12. GitHub Actions CI run 102 passed for the Job Bank commit. Telegram
acceptance was pending at this stage; the owner later confirmed the core
commands, resume import and Recommendation v2 detail flow (see the v3.5.6
acceptance entry above).

Local deployment was rebuilt with `JOB_AGENT_COMPOSE_PROJECT=repo ./job-agent
rebuild` from this worktree. Runtime remains v3.5.2; both Career-first and
Relocation-first are active. PostgreSQL stayed healthy and existing
`repo_jobagent_v3_pg` / `repo_jobagent_v3_files` volumes were preserved.
The startup scheduled scan fetched Job Bank search/detail pages with HTTP 200
and completed successfully at 20:44:49 UTC on 2026-10-10.
Changes are uncommitted; HEAD is still `7c987da`. No push, merge or PR occurred.
