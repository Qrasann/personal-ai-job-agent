# Handoff

## Himalayas requirement-section parsing — 2026-10-13

The owner previously shared `/job 1273` for Canonical's Associate Linux
Support Engineer. Checking the live Himalayas listing showed requirement
sections headed `What we are looking for in you`, along with a separate
`Nice-to-have skills` section. The parser recognized neither structure, so
technical requirement coverage and the interview-risk dimension were shown as
unknown. The parser now classifies common `What we are looking for`,
`What you'll bring`, and `Nice-to-have skills` headings; ASCII and curly
apostrophes are accepted. A regression mirrors the escaped-HTML source shape,
and a score-level test verifies required versus preferred classification.

The interview-risk evidence is now explicitly labelled as technical
requirements coverage. It does not assess education, general English,
communication, background checks, or every other interview condition. The
Himalayas listing currently says all-country scope and a Nov 19, 2026 apply
deadline; its own text also requests either a bachelor's degree or a compelling
alternative path and strong written/verbal English. Those are source claims
to verify with the employer and are not added to the technical score.

Verification: targeted tests **37 passed**; full unit suite **439 passed, 3
skipped**; isolated PostgreSQL suite **442 passed**; compileall, secret scan,
and `git diff --check` passed. The running Compose app is on source/runtime
3.5.7 with healthy PostgreSQL; rebuild the app after commit, preserving both
named volumes, then ask the owner to reopen `/job 1273` and verify technical
interview-risk is populated while nontechnical conditions remain separate.
Do not apply or send any application.

## Candidate English bootstrap default — 2026-10-12

The tracked fresh-profile template previously said `english: B2`, which
collapsed the owner's current general self-assessment (B1) with a separate
technical-reading estimate (B2). The current work changes the default to
`english: B1` and records `technical_reading_english: B2`. Bootstrap currently
does not use these language fields to rewrite an existing profile, and its
candidate facts continue to be inserted only when none exist. A regression
asserts the split. Targeted tests: 3 passed; full suite: 437 passed, 3 skipped;
compileall, secret scan and diff check pass. Committed locally as `8ca977f`.
The existing Telegram/runtime user profile remains intact.

## Emerging Travel Group official AM/GE lead — 2026-10-12

The current Emerging Travel Group careers page lists a remote Junior DevOps
Engineer position and names Armenia and Georgia among available locations.
The listed requirements include 1.5+ years commercial DevOps experience,
Linux, Ansible, Docker, six months Kubernetes, and English B1+. This is a
useful manual lead against the owner's stated B1 level, but no candidate facts
confirm the commercial DevOps or Kubernetes duration. The role does not
establish eligibility to hire a Russian citizen, visa support, or a relocation
package.

Workable's official help page documents public jobs endpoints for published
roles. The ETG account endpoint returned HTTP 403 when checked, so an automated
connector is not justified. Added the official posting as a manual source link
for both selected markets; it does not enter toggles or scans. Targeted tests:
5 passed; full unit suite: 437 passed, 3 skipped; compileall, secret scan, and
diff check passed. Compose `repo` rebuilt at 21:37 Moscow, PostgreSQL stayed
healthy, and startup scan completed at 21:38:46 UTC. One isolated HH search
logged a transient `ConnectError`; scheduler scan completed. Commit:
`432d44c`.

The Telegram `/jobs relocation` output shared at 21:13 Moscow time showed a
Tyumen onsite job, but it predates the 21:26 rebuild that introduced the
current-country onsite filter. Re-run `/sources`, `/jobs relocation`, and
`/jobs relocation below` after the current source-link rebuild. The filter
must hide same-country onsite results unless domestic relocation is explicitly
enabled, while leaving explicit remote and unknown-country results visible.

## Relocation-first current-country onsite filter — 2026-10-12

Owner Telegram output at 21:12–21:13 Moscow confirmed the manual source links
and scoped job views. The Relocation-first list showed a chef job in Tyumen at
70/100, while the below-threshold list included several Moscow-area onsite
jobs. Root cause: the profile allowed `local_ru`, and location filtering only
ran when geography had been explicitly configured, so same-country onsite
vacancies were not excluded from the relocation review lane.

`vacancy_allowed` now suppresses a vacancy only when all are true: strategy is
Relocation-first, the vacancy country is explicitly the user's current country,
the role is not explicitly remote, and `domestic_relocation` is not enabled.
Unknown country remains unknown. Remote roles in RU remain visible because
remote hiring from a destination still needs verification in the vacancy card.
Career-first and the global score/threshold are unchanged. Setting
`domestic_relocation: true` is an explicit opt-in to domestic moves.
The scoped Telegram list also filters persisted older matches and fetches an
expanded candidate set before applying the same rule, so old onsite rows do not
occupy the first ten result slots after a settings or code change.

Verification: targeted tests **49 passed**; full local suite **437 passed,
3 skipped**; isolated PostgreSQL suite **440 passed**. `compileall`, secret
scan, and `git diff --check` passed. Compose `repo` was rebuilt, reports source
and runtime 3.5.7, app is up, PostgreSQL is healthy, and startup scan completed
at 18:26:17 UTC. One HeadHunter public-web request logged a transient
`ConnectError`, while the scheduler scan completed. Existing PostgreSQL/storage
volumes were preserved. The
owner should run `/jobs relocation` and `/jobs relocation below` once more to
confirm current-country onsite vacancies are gone while remote/GE/AM results
remain. Do not change the 65 threshold or scores based on this fix.


## AM/GE manual source links — 2026-10-12

The current candidate adds clickable manual-search entries to `/sources` for
ITA Jobs, Staff.am, Job.am, CareerCenter.am, Findjobs.ge, and LeverX Careers.
Entries appear only when their market is selected, are marked `manual`, and
are excluded from source toggles and scan execution. The `/sources` footnote
states that these links do not prove work eligibility. Existing automated
adapters and profile settings are unchanged.

The 2026-09-27 Findjobs.ge terms welcome search engines and AI assistants but
prohibit repeated/systematic extraction or reuse of substantial board data
without written permission. No collector was added. ITA Jobs describes itself
as a reference directory linking back to employer/academy pages, but publishes
no reusable jobs API. LeverX's current Support Engineer opening is office-based
in Georgia and asks for English B2+, making it a manual lead with a known
language gap against the owner's current B1 estimate.

Verification: local suite **432 passed, 3 skipped**; isolated PostgreSQL suite
**435 passed**; compileall, secret scan, and `git diff --check` passed. Commit
`ffabb1b` adds the feature. Compose `repo` was rebuilt from this branch;
startup `scan_all` completed at 18:06:12 UTC, runtime is 3.5.7 and PostgreSQL
is healthy. The inspected scan logs contain requests only to existing adapters;
manual portals were not queried. Owner confirmed `/sources` link rendering at
21:12 Moscow time; the manual links appear for both markets and profiles. Do
not publish v3.5.7.

## HeadHunter selected-market discovery — 2026-10-12

The fresh-profile GE/AM defaults and lower-barrier relocation queries are
committed locally as `00f1f0d`. The follow-up HH coverage change is committed
locally as `552cb72`. The official public HH `/areas` catalog confirms
Russia area `113` and Georgia area `28`; Armenia is absent. The adapter now
searches current/selected markets independently, retains the original role
queries and result bounds, deduplicates results across areas, and assigns the
requested country only for the corresponding area-filtered results. It does
not invent or approximate an Armenia area. Armenia coverage remains with other
sources.

Verification: local suite **430 passed, 3 skipped**; isolated PostgreSQL suite
**433 passed**; `compileall`, secret scan, and `git diff --check` passed. The
test database is isolated. Rebuilt the local Compose app from this branch;
runtime reports 3.5.7, PostgreSQL remains healthy, and startup `scan_all`
completed at 17:56:41 UTC. Logs show HH's public-web fallback using area `28`
for Georgia and area `113` for Russia; both returned HTTP 200. This change has
not been pushed or published; owner Telegram acceptance remains pending. Keep
PR #18 draft. No application actions or private HH endpoints were used.

## AI job-bot GE/AM bootstrap defaults — 2026-10-12

The current unpublished follow-up aligns fresh AI job-bot profiles with the
owner's equal-priority Georgia and Armenia plan. `data/profile.yaml` now sets
both `target_countries` and `relocation_countries` to `GE, AM`, and defines
bounded lower-barrier Relocation-first queries for warehouse, production,
hotel, kitchen, cleaning, construction and customer support roles. This is
bootstrap configuration only; existing persisted search settings are not
rewritten. Career-first queries, the score threshold of 65, score ordering,
source access limits and evidence rules remain as before.

Added `tests/test_profile_defaults.py` and updated `BRIEF.md`, `TASKS.md`, and
`DEVELOPMENT_LOG.md` so this stage can be handed off with its rationale.
Verification: local suite **427 passed, 3 skipped**; full suite against the
isolated PostgreSQL test database **430 passed**; `compileall` and
`git diff --check` passed. Test PostgreSQL is separate from the personal
runtime database.

The stage is verified and is being recorded in the current feature branch.
Production Compose `repo` was left running without a rebuild; named data
volumes were not changed. The stage consists of `data/profile.yaml`,
`tests/test_profile_defaults.py`, and the four PROJECT_OS documents. Continue
v3.5.7 coverage and Telegram acceptance from this point. Do not merge/tag/
release PR #18 at this point.

## EURES padded-location production follow-up — 2026-10-12

The cumulative v3.5.7 candidate is published at `8da96f8` on
`feature/v3.5.7-international-market-coverage`. Both GitHub Actions runs passed
(push `38280187127`, PR `38280191809`). Compose project `repo` was safely
updated and is currently running source/runtime 3.5.7 with healthy PostgreSQL;
the existing PostgreSQL and storage volume names were preserved.

The first startup scan reached all inspected public sources, but one EURES
vacancy failed during database insertion with `value too long for type
character varying(256)`. The source supplied an Ireland location with large
fixed-width whitespace padding. The scheduler completed, but that row was not
persisted, so the scan must not be described as fully clean.

The current worktree adds a bounded adapter fix and two regressions:

- collapse all EURES `cityName` whitespace before assigning `jobs.city`;
- if meaningful normalized text still exceeds 256 characters, leave city
  unknown and preserve the exact source value in `raw.location_text`;
- keep the source country unchanged and make no visa or relocation inference.

Verification: full isolated PostgreSQL suite **429 passed**, branch coverage
**73.24%**; targeted EURES suite **13 passed**; `compileall` and
`git diff --check` pass. No schema or data migration is required.

Published as `159d510`. Push CI `38281187340` and PR CI `38281192380`
passed. The safe updater rebuilt/restarted only the running application;
PostgreSQL remained healthy and the same `repo_jobagent_v3_pg` and
`repo_jobagent_v3_files` volumes stayed attached. The fresh startup scan
reached EURES searches/details with HTTP 200 and completed successfully at
17:04:14 UTC. Its complete filtered log window contains no database/source
error, traceback, or repeated city-width failure. Source/runtime remain 3.5.7.

Next: keep PR #18 draft and continue practical Relocation-first coverage and
owner acceptance of the latest profile-scoped Telegram commands. Do not
merge, tag, or release v3.5.7 in this stage.

## Resumed verification checkpoint — 2026-10-12

The owner resumed the saved objective. The current candidate has completed
local and isolated-PostgreSQL validation, but is not yet published or deployed
from this worktree. No test/build process is pending. The isolated test
PostgreSQL is healthy; production Compose `repo` app and PostgreSQL are
stopped cleanly (`Exited (0)`).

### New work and verification
- Bounded employer support evidence now distinguishes offers, explicit
  refusals, prerequisites, guidance, and unknown statements across the named
  support components. Independent offers/refusals remain separate.
- Annual salary scoring uses a monthly equivalent for monthly profile floors;
  source amounts and periods remain intact. Vacancy salary text shows a known
  pay period. Hourly and weekly amounts remain incomparable without work-hour
  assumptions.
- Technical Staff seniority no longer catches ordinary hotel/warehouse staff.
- A new manual scan clears stale dashboard completion data; independent source
  errors do not discard successful source results.
- Remotive's persistent cache retains its original fetch time; Himalayas
  timezone bounds appear as source-attributed details.
- Full local suite: **424 passed, 3 skipped**. Full isolated PostgreSQL suite:
  **427 passed, 73.22% branch coverage**. `compileall` and `git diff --check`
  pass.
- `VERSION` and source version are 3.5.7. Branch is
  `feature/v3.5.7-international-market-coverage`, local HEAD `d445c87` with
  unpublished worktree changes. PR #18 is OPEN/DRAFT at that commit.
- The previous shutdown's mount inspection recorded `repo_jobagent_v3_pg`
  and `repo_jobagent_v3_files`; verify those exact mounts again after restart.

### Next steps
1. Review the final diff and stage only intended source, tests, and public
   PROJECT_OS files; keep `.env`, credentials, `.private/`, and external
   private context outside Git.
2. Commit and push to the already authorized current feature branch; update
   PR #18's description and watch CI for the pushed head.
3. Once CI passes, rebuild/start Compose project `repo` with the existing
   volumes. Verify runtime 3.5.7, PostgreSQL health, unchanged mount names,
   completed startup scan, and logs.
4. Keep Telegram live acceptance of scoped commands pending until the owner
   verifies them. Continue the open v3.5.7 relocation-source work afterward.

## Previous shutdown checkpoint — 2026-10-12

Before the owner powered off, the previously deployed runtime was 3.5.7 with
the app and PostgreSQL healthy; that runtime stopped cleanly during shutdown.
Its earlier test counts describe that earlier checkpoint, not the resumed
candidate validation above.

### Saved work
- Independent `/jobs career`, `/jobs relocation` and `/jobs relocation below`
  views; optional profile scopes for `/job` and `/compare`. Detail and
  comparison buttons retain the selected profile and its own score/threshold.
- Corrected the ordinary Hotel/Kitchen/Warehouse Staff seniority false
  positive; technical Staff and explicit seniority, experience, management and
  owner exclusions remain restricted.
- Updated the public roadmap and the separate private relocation progress
  file. The private file is still ignored by Git; keep personal facts there.
- The current working tree also retains the earlier source adapters,
  Job Bank resilience, remote priority and below-threshold review changes.
  All tracked modifications and new untracked source/test files are saved.

### Verification already completed
- Full local pytest suite: **319 passed, 3 database tests skipped**.
- Isolated PostgreSQL repository suite: **3 passed**, including profile-specific
  scores for the same vacancy, ownership and scope-aware sorting/details.
- `compileall` and `git diff --check` passed; the latter is checked again after
  this documentation-only checkpoint. No tests or rebuild were restarted.
- Compose rebuilt at 01:36 Moscow; startup `scan_all` completed successfully
  at **01:37:50 Moscow**. Existing production PostgreSQL/storage volumes remain
  in use; no data-removal operation was performed.

### Remaining work and exact resume step
1. After power-on, read this checkpoint and `BRIEF.md`; inspect `git status`
   and run `JOB_AGENT_COMPOSE_PROJECT=repo ./job-agent status`. Start existing
   services if needed, preserving the existing named volumes.
2. Verify the new scoped commands and detail/comparison buttons in Telegram.
   This acceptance is still pending; unit/integration tests do not substitute
   for owner verification of the live UI.
3. Continue v3.5.7 with bounded HH discovery for selected destinations after
   verifying official area data, or permitted AM/GE employer feeds. Current
   HH discovery only searches the current-country area. Useful Relocation-first
   coverage remains open; do not inflate scores or lower the threshold of 65.
4. Recheck Remotive only after its 24-hour persisted cache expires. Its last
   category RSS response was a valid empty feed.

Repository: `/home/roma/job-agent-release-v352`; branch
`feature/v3.5.7-international-market-coverage`; HEAD `d445c87`.
Changes are **uncommitted**, including new untracked adapter/test files. Do
not reset/clean them or run the updater against the dirty worktree. No commit,
push, merge, PR update, tag or release was made during these local steps.
Private roadmap: `.private/relocation-roadmap.md` (ignored; never publish).

## Current stage — independent vacancy review — 2026-10-12

Added `/jobs career`, `/jobs relocation` and `/jobs relocation below`. Scope
filters the actual SearchProfile id and uses that profile's threshold; it does
not combine query lists or change scoring. Cards and comparison buttons retain
the selected profile, and explicit `/job <id> career|relocation` and
`/compare <id> career|relocation` are supported. Old commands/callbacks work.
Default `/job <id>` still chooses the latest match; the card identifies its
profile, while new list buttons preserve the match that produced the displayed
score. Disabled/missing Relocation-first does not fall back to Career-first.

Fixed the `staff` seniority false positive for ordinary Hotel/Kitchen/Warehouse
Staff. Technical Staff roles and explicit Senior/Lead/Principal, experience,
management and user exclusions still apply. Missing support remains unknown;
even a correctly classified role can stay below 65. This alone does not prove
Relocation-first coverage is solved.

Verification: 319 passed, 3 database tests skipped locally; all 3 repository
integration tests passed against isolated PostgreSQL, including two scores for
one job, scope-specific sorting/details and user isolation. Compilation and
diff checks passed. Compose `repo` was rebuilt at 01:36 Moscow: source/runtime
3.5.7, app up and PostgreSQL healthy. Startup `scan_all` completed successfully
at 01:37:50 Moscow. Telegram acceptance of the scoped
commands is pending. Public roadmap now includes current-stage status;
private route progress and official-law corrections remain in the ignored file.
No publication action was made.

Next: bounded HH discovery using verified areas for selected destinations or
permitted AM/GE employer feeds. Current HH discovery uses the current-country
area and does not search selected GE/AM. Keep profile queries, score ordering,
threshold 65 and exclusions. A completed scan with zero useful relocation
matches is a coverage/fit result, not proof of a hiring refusal.

## Previous stage — below-threshold manual review — 2026-10-12 Moscow

Added `/jobs below` to show nonzero scores from 1 through one point below the
configured notification threshold for manual review. Normal `/jobs`,
Good/Stretch queues, notifications, Match Score, and descending score priority
stay unchanged. Duplicate matches and zero-score exclusions are omitted. The
list explicitly says that work authorization and relocation support are not
automatically confirmed.

Verification: 286 local tests passed and 3 database-dependent tests were
skipped; all 3 repository integration tests passed against the isolated
PostgreSQL database. Compilation and `git diff --check` passed. Compose `repo`
was rebuilt at 01:15 Moscow on Oct 12; source/runtime report 3.5.7, PostgreSQL
is healthy, and the app is polling. The startup scan began immediately; on the
previous rebuild it had been missed by 4 seconds, so `scan_all` now has a
five-minute misfire grace. Telegram acceptance of `/jobs below` is pending;
the owner's pasted scan at 00:39 preceded both rebuilds. No threshold or score
was changed.

Next: continue practical Relocation-first source coverage and relevance while
keeping legal eligibility evidence separate and the 65-point threshold intact.
The private relocation roadmap remains outside Git.

## Previous stage — Remotive category RSS feed — 2026-10-12 Moscow

Added Remotive's official public Devops feed as a discovery-only
source. It fetches at most 250 results once per 24 hours, shares one response
across active users and both search profiles, and persists the cache using the
existing PostgreSQL `runtime_state` table. Each displayed listing links to
Remotive and names the source, including duplicate/canonical results shared
with Himalayas. Clear country-only mismatches are excluded for a selected
market; region and unknown scopes stay explicit. Salary text remains
unstructured, and the adapter does not apply or contact employers. Provider
terms and the feed contract are documented in
`docs/developer/INTERNATIONAL_SOURCES.md`.

The first API-based implementation passed 28 targeted tests and a 282-pass
local suite (3 database tests skipped); the earlier isolated PostgreSQL run
passed 285 tests. Owner-confirmed scans showed 0 Remotive jobs. A read-only
cache probe found 18 general-feed rows and no Devops rows. Three live API checks
using `category=devops`, `Devops`, and `software-development` all returned the
same general feed. The official Remotive documentation lists a category feed
at `https://remotive.com/remote-jobs/devops/feed`, so the adapter now parses
that RSS feed and uses a v3 cache key to bypass stale API results.

Latest Remotive-stage verification: 17 Remotive/cache tests passed; the full
local suite then passed 283 tests with 3 database tests skipped. The isolated
PostgreSQL result predates the RSS-only change. Compose was rebuilt at 00:53
Moscow on Oct 12; source/runtime report 3.5.7 and PostgreSQL is healthy. The
RSS request returned HTTP 200 with
channel metadata but no `<item>` entries, so both profiles currently parse
zero Remotive jobs. Recheck after the daily cache expires; keep an empty feed
distinct from a transport failure.

Next: recheck the category feed after its cache window, then continue practical
Relocation-first source-coverage and relevance. Preserve the separate career
and relocation directions, the 65-point
threshold, descending Match Score priority, and explicit unknowns for visa,
employer eligibility, housing, and relocation support. Do not change owner
exclusions or promote lower-rated roles ahead of higher-rated roles. The
private relocation roadmap stays outside Git.

The candidate remains local and uncommitted on
`feature/v3.5.7-international-market-coverage`, `VERSION=3.5.7`; GitHub `main`
and the latest formal release/tag remain v3.5.6, with draft PR #18 open. No
publication action was made.

## Latest owner clarification — score priority in `/jobs` — 2026-10-11

The owner confirmed that higher-rated vacancies should receive higher
priority. `/review`, `/stretch`, and `/saved` already order by score descending;
`/jobs` previously ordered by creation time, which could put a 69-point result
above an 84-point result. `/jobs` now orders by score descending and uses
recency only to break ties; its heading says “Совпадения по рейтингу”. The
notification threshold remains 65 and lower-scoring roles are not promoted.
A PostgreSQL integration regression checks that a newer 72-point match stays
below an older 86-point match. Relocation-first practical coverage remains an
open task; investigate relevance and source coverage without inflating scores
or changing exclusions. Local suite: 274 passed, 3 database tests skipped;
isolated PostgreSQL suite: 277 passed. Compilation and `git diff --check` pass.
Compose `repo` was rebuilt at 21:38 Moscow time; source/runtime versions both
report 3.5.7 and PostgreSQL is healthy. The startup scan completed at 18:40:25
UTC (21:40:25 Moscow); the inspected logs show HH public-web fallback after
API 403 and successful requests from Himalayas, HR.ge, EURES, Job Bank,
Greenhouse, Lever, Remote OK, and HH.
At 23:27 Moscow time the owner confirmed the live `/jobs` order: 88, 84, 82,
then 78 and below. The later scheduled scan completed at 20:25:14 UTC
(23:25:14 Moscow); the visible EURES, Job Bank, Arbeitnow, Remote OK and
Greenhouse requests returned HTTP 200, with no source error in the supplied
excerpt.

## Latest owner check — remote search and geography in details — 2026-10-11

The owner ran `/sources`, `/scan`, `/scanstatus`, and `/jobs` at 20:42–20:44
Moscow time. Himalayas returned 20 cached results and its remote roles appeared
at the top of `/jobs` with source links. Career-first processed 191 jobs
(37 Good, 33 Stretch); Relocation-first processed 67 (0 Good/Stretch). Job
Bank returned 12 in 71.2 seconds, compared with the prior 100.7-second scan;
EURES returned 16 in 34.1 seconds. The supplied 17:42–17:44 UTC log excerpt
shows normal source responses, HH's public-web fallback after API 403, and no
source exception or SSL failure.

Reviewing the live card path found that `/jobs` said “remote” but `/job` did
not show Himalayas' saved country scope. The detail card now displays whether
the source says worldwide, names specific countries, or leaves hiring
geography unspecified, with a reminder that hiring in the user's country must
be confirmed. Regression coverage passed. Local suite: 267 passed, 3 skipped;
isolated PostgreSQL suite: 270 passed; `compileall` and `git diff --check`
passed. Compose `repo` was rebuilt at 20:51 Moscow; app is up, PostgreSQL is
healthy, and its scheduled scan completed at 17:53:37 UTC (20:53:37 Moscow).
The inspected logs show Himalayas requests for GE and AM, EURES, Job Bank,
HR.ge, Greenhouse, and HH public-web fallback succeeding; no source exception,
SSL failure, or timeout appeared. At 20:56 Moscow time, the owner opened
`/job 1273` and accepted the new geography line: Himalayas' worldwide claim is
attributed to the provider, and the employer must confirm hiring from the
user's country. The vacancy has no salary. The Telegram update completed in
567ms without an error.

Work remains uncommitted on `feature/v3.5.7-international-market-coverage`
(`VERSION=3.5.7`). GitHub `main` and the latest formal release/tag remain
v3.5.6; draft PR #18 targets `main`. No publication action was taken.

## Current follow-up — Collectly Lever source — 2026-10-11

The owner accepted the Himalayas `/job 1273` geography card. The next roadmap
stage now adds a narrowly scoped Collectly source through Lever's documented,
public Postings API. An authorized read-only GET to the public Collectly board
returned its current `Senior DevOps/DevSecOps Engineer` post. The listing is
remote and says GMT-7 to GMT+4; the API lists Belgrade/RS. The adapter runs only
for selected AM/GE, requires a remote post and a stated timezone range covering
UTC+4, stores the Belgrade/RS metadata separately, and leaves normalized
country, salary (when absent), visa, and relocation unknown. The hosted form
states that required Yerevan onboarding lasts one or two weeks and travel and
accommodation are covered. That is a possible lead, not proof that the
employer can hire a Russian citizen in Armenia or Georgia.

The source is bounded to one 100-record page and a six-hour local cache; it
does not use Lever's authenticated data API or apply endpoint. Regressions
cover timezone, remote mode, role matching, country ambiguity, salary metadata,
malformed responses, and source registration. A detail-view regression now
also checks that timezone scope carries a country-level hiring caveat. The
targeted detail/Lever tests pass (16 tests); the full local suite passes (274
passed, 3 database tests skipped). Compose `repo` was rebuilt at 21:04 Moscow time;
PostgreSQL remained healthy. Startup `scan_all` completed successfully at
18:06:21 UTC (21:06:21 Moscow). The inspected log window shows Lever returning
HTTP 200 for both profiles, successful responses from the other queried
sources, and HH recovery through its public-web fallback after API 403. No
source exception appears in that startup scan window.

At 21:11–21:14 Moscow time, the owner confirmed `/sources` lists Lever for both
profiles and ran `/scan` plus `/scanstatus`. Lever returned 1 live result in
9.6s; the complete scan finished at 18:14:01 UTC (21:14:01 Moscow) with 266
processed, 37 Good, 33 Stretch, 196 filtered, and no new notifications. Job
Bank returned 12 in 71.4s; EURES returned 16 in 55.2s. The supplied logs show
Lever HTTP 200 for both profile requests, HH recovering through public web
after API 403, and no source error. `/jobs` returned its latest ten rows and
did not show Collectly. A read-only query of the saved match found Collectly
job #1333 as `filtered`, score 0, with reason `senior devops` matched the
Career-first profile's explicit exclusion list. This is expected filtering,
not a missing adapter result; leave the exclusion unchanged unless the owner
chooses otherwise. The tested detail renderer already attributes timezone
scope and warns that it does not establish country-level hiring.

At 21:20 Moscow time, the owner supplied `/review` and `/stretch` output. The
first result in each was remote (CloudCops 88/Good and Sporty Group 72/Stretch).
This confirms remote opportunities are visible in both review lanes; code
regression tests cover processing priority within both profiles' source
batches. The `/scan` reported Relocation-first 74 processed and 0 Good/Stretch.
Its current queries include broad lower-barrier work, but its notification
threshold is 65; an inspected remote result scored 54 and was filtered. This is
a result-visibility/scoring issue, not source health. The owner later clarified
that higher-rated vacancies must receive higher priority. Keep this threshold
and do not place lower-rated leads ahead of higher-scoring jobs.

The branch remains `feature/v3.5.7-international-market-coverage` at source
version 3.5.7 with uncommitted local work. GitHub `main` and the latest formal
tag/release remain v3.5.6; draft PR #18 targets `main`. No merge, tag, or
release has been made. A current GitHub check shows visible tags v3.5.0,
v3.5.1, and v3.5.6; v3.5.2–v3.5.5 are cumulative changelog milestones, with
no separate tags/releases. Preserve the user's worktree and keep the private
relocation roadmap outside Git.

## Current stage — Himalayas remote-source candidate — 2026-10-11

The active worktree is `feature/v3.5.7-international-market-coverage`, at
`d445c87`, with `VERSION=3.5.7`. This stage adds Himalayas' documented public
remote-jobs API, queried by each profile's active role queries and up to three
selected markets. Requests are bounded to four queries, one 20-result page per
query/market, serialized with a short delay, and cached for 24 hours. Telegram
cards visibly attribute Himalayas and link to the source. Salary periods are
shown when available. Missing country restrictions remain unknown; remote
availability does not establish work authorization, payroll or tax eligibility.

RemoteOK also no longer labels unspecified work geography as worldwide. The
existing remote-work processing priority remains separate from match score and
from country eligibility. The source and profile regressions pass (41 targeted
tests). Full local/PostgreSQL suites, compilation, diff checks, Compose rebuild
and startup-log inspection are complete; results are recorded below.

The change is uncommitted and has not been published. GitHub `main` and its
latest formal tag/release remain v3.5.6; candidate `VERSION` is 3.5.7. Draft PR
#18 targets `main`, but its published green checks do not include this worktree.
Verification passed: 266 local tests with 3 database tests skipped; 269 tests
with isolated PostgreSQL; branch coverage 69.70% (55% CI minimum); compileall
and `git diff --check`. Compose `repo` was rebuilt at 20:33 Moscow time. Its
startup scan completed at 17:35:32 UTC (20:35:32 Moscow): Himalayas filtered
requests for GE and AM returned HTTP 200; EURES and other shown sources also
returned HTTP 200. HH API returned 403 and the ordinary public-search fallback
succeeded. PostgreSQL is healthy and the original named volumes
`repo_jobagent_v3_pg` and `repo_jobagent_v3_files` remain attached.

The owner has completed `/sources`, `/scan`, `/scanstatus`, and `/jobs`; the
remote results and attribution are visible. Telegram `/job 1273` acceptance
is complete: the source's worldwide label is qualified by a country-level
hiring confirmation reminder. The vacancy has no salary; no individual
eligibility claim is inferred.

## Current stage — Remote-work priority and Job Bank pacing — 2026-10-11

The active branch remains `feature/v3.5.7-international-market-coverage`
(`VERSION=3.5.7`, HEAD `d445c87`). The local change gives explicitly remote
vacancies a processing-priority bonus inside source batches in both
independent search profiles, while each profile retains its own role queries.
Match Score and notification thresholds are unchanged. A remote label or
`remote_scope=unspecified` does not establish worldwide eligibility.

Job Bank now enforces at least five seconds between serialized request starts.
If a response itself takes five seconds or longer, the next request starts
without an extra full wait. Bounded transport retry and partial-result recovery
remain in place; HTTP status errors are not retried.

Regressions cover remote versus onsite across strategies, unknown scope, and
negated remote labels. Job Bank regressions cover partial failure, start
spacing after fast and slow responses, and concurrent callers. Targeted tests
pass 34; the local suite passes 254 tests with 3 database tests skipped; the
isolated PostgreSQL suite passes 257 with 68.59% branch coverage. Compilation
and `git diff --check` pass. These changes are uncommitted and have not been
applied to GitHub. They were rebuilt into local Compose at 17:09 UTC. The app
reports 3.5.7 and PostgreSQL is healthy; the first inspected post-rebuild log
only shows scheduler setup, so the live scan is still pending.

Telegram acceptance remains needed after the candidate update: compare Job
Bank timing using `/scanstatus`, confirm sources finish without errors, and
review remote-first processing in both profiles. Remote scope and employer
permission to work from the destination remain unknown unless the posting
states them.

GitHub `main` and the latest formal tag/release remain v3.5.6. Draft PR #18
targets `main`. The latest published PR head has green Python, secret-scan, and
Docker-build checks in runs `38152993495` and `38152990522`; those checks do not
include the current uncommitted changes. No push, merge, tag, or release has
been made. Keep the local gitignored relocation roadmap private.

## Earlier stage — Job Bank partial-result resilience — 2026-10-11

The active worktree is `feature/v3.5.7-international-market-coverage` at
`d445c87`; the Job Bank code and documentation changes for this stage are
currently uncommitted. The candidate and local Compose runtime both report
3.5.7. GitHub `main` and its latest formal tag/release remain v3.5.6; PR #18
is still an unmerged draft. No publication action has been taken.

Job Bank now continues after an individual query or detail request exhausts
the existing one transport retry, retaining details it did verify. If all
searches or all fetched details fail, it still reports the source error. Its
five-second request delay, serialized requests, query/detail limits and lack
of HTTP-status retries are unchanged. Targeted tests pass (18); full isolated
PostgreSQL suite passes (251, 68.44% branch coverage), and compilation passes.
The rebuilt local service's startup scan completed at 16:25:19 UTC. The owner
then supplied a fresh Telegram `/scan` and `/scanstatus` from 19:33–19:36 Moscow
time: Job Bank returned 12 vacancies in 100.7 seconds; EURES 16, HR.ge 2, HH
209, Remote OK 3, Arbeitnow 2 and Greenhouse 1. Supplied logs show the Job Bank
detail, EURES and HR.ge requests returning HTTP 200, with no Job Bank warning
or source failure in the excerpt. This confirms the source works in a normal
run; it does not reproduce a transport failure, so regression tests remain the
evidence for partial-failure recovery.

A separate local, gitignored personal relocation plan was updated with current
leads. Keep that file and its personal details out of repository history.

## Owner acceptance — Lineate Recommendation v2 — 2026-10-11

At 18:42 Moscow time, the owner reopened `/job 1091` in Telegram and confirmed
Technical 42 and interview risk 58, with explicit required-skill coverage and
`fit=good`. The bot handled the update in 607 ms. This closes the final
Telegram acceptance check for the normalization fix in `8a583c7`.

The risk score is a matching-gap indicator, not a calibrated probability of an
interview. Salary, work mode, visa sponsorship, and relocation assistance
remain unknown without explicit posting evidence. The inspected Compose scan
completed successfully at 15:38:13 UTC; its checked log window had no source
errors, SSL failures, timeouts, or tracebacks. Runtime source/version are
3.5.7, PostgreSQL is healthy, branch
`feature/v3.5.7-international-market-coverage` is active, and draft PR #18
targets `main`. `main` and the latest formal release/tag remain v3.5.6. No
merge, v3.5.7 tag/release, schema migration, credential change, or volume
change was made.

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

At the time of this handoff entry, Telegram verification was still needed. The
owner subsequently confirmed Technical 42 and interview risk 58; see the
acceptance record above. The risk is a matching-gap indicator, not a calibrated
probability. Salary, work mode, visa sponsorship and relocation support remain
unknown without direct posting evidence.

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
At this handoff stage, the owner had not yet reopened `/job 1091`; the later
18:42 Telegram acceptance is recorded at the top of this file.

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
HTTP 200. No source error appeared in the inspected scan tail. Owner review was
pending at that stage and was completed later; see the acceptance record above.

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
