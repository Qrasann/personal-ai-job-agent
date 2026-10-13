# Roadmap

Last reviewed: 2026-10-14

Latest stages: source salary/remote evidence af1ff56, Telegram evidence
76b5661, numeric metadata resilience. Latest unit 658 / 3 skipped,
PostgreSQL 661; compileall/secret/diff passed. Runtime update/acceptance remains
pending; v3.5.7 stays active. No new Armenian feed verified yet.

Historical local work: HH recovery (`5c4b959`), expiry cards (`c516a77`), bounded
remote queries (`e7b56f6`), GE public feed (`5044e90`), requirement section parsing
(`5d02cb2`), and Unicode explicit role/resume tokens. Latest unit 606 / 3 skipped,
PostgreSQL 609 and safety checks passed; separate Docker/Python 3.12 validation
passed. New work is not deployed. Runtime c829a5f remains healthy; startup
completed 21:53:38 UTC. Draft PR #18 remains at remote f9ed986 with CI only for
that commit. Next gate is owner-approved runtime update and real source/scoped
Telegram acceptance before v3.6. Milestones below retain historical evidence.

## Progress at a glance

| Stage | Status | Completion criteria |
| --- | --- | --- |
| v3.5.6 — core personal workflow | Completed baseline | Independent profiles, candidate facts, manual resume import, review queues and scan status are implemented. |
| v3.5.7 — international coverage and relevance | **In progress: independent result review** | Useful GE/AM and remote leads, correct restrictions, profile-specific scores and broader lower-barrier coverage. |
| v3.6 — candidate and vacancy fit | Next | Evidence-based required-skill, language, work-eligibility and salary comparisons; personal affordability remains private. |
| v3.7 — application workspace | Planned | Tailored CVs and manually confirmed application stages. |
| v3.8 — recruiter and interview support | Planned | Grounded drafts and practice from confirmed facts and requirements. |
| v4.x — agent and productization | Planned after personal workflow | Safe automation, multi-user/dashboard scope and monetization preparation after v3.5.7–v3.8 obligations. |

The current v3.5.7 stage adds `/jobs career`, `/jobs relocation`, and
`/jobs relocation below`. Each scoped list keeps its profile's own threshold
and scores; opening a card retains that profile. The shared `/jobs` list still
orders highest rating first. Ordinary `hotel staff` and `warehouse staff`
titles no longer trigger the engineering `Staff` seniority exclusion; explicit
Senior/Lead/Principal, experience and management requirements still apply.

Still open in v3.5.7: useful local AM/GE employer coverage and post-fix
Telegram confirmation of the Relocation-first result list. Recent completed scans found no Relocation-first
Good/Stretch results. Unknown eligibility remains unknown and the threshold
stays at 65. Local commit `61fe39d` adds bounded HH searches for official
catalog areas RU `113` and GE `28`; Armenia is absent from HH's public catalog
and remains the responsibility of other sources. Runtime check is complete;
owner confirmed `/sources` and scoped list rendering on 2026-10-12. An enabled
source or HTTP 200 is not evidence of a usable opportunity.

`/sources` also contains link-only manual destinations for selected AM/GE
markets. These entries never enter automated scans; Findjobs.ge requires
written permission for recurring extraction of substantial data. Current
local validation is 432 passed / 3 skipped and the isolated PostgreSQL suite is
435 passed. Commit `ffabb1b` was rebuilt locally; its startup scan completed at
18:06:12 UTC with PostgreSQL healthy. Owner Telegram check of `/sources` passed
at 21:12 Moscow time.

Owner Telegram acceptance has now confirmed the manual links and scoped list
rendering. That live output exposed and prompted a Relocation-first filter fix:
current-country onsite vacancies are excluded unless domestic relocation is
explicitly enabled; remote and unknown-country listings remain. Unit and
PostgreSQL suites pass, and the rebuilt startup scan completed. Verify the
post-fix `/jobs relocation` output before closing the result-quality item.

An additional official Emerging Travel Group Junior DevOps opening currently
lists Armenia and Georgia as available remote locations and English B1+ as its
minimum stated language level. It is now a direct manual source link for both
markets. Workable's documented public endpoint returned HTTP 403, so the bot
does not scan it. The 21:13 Telegram output predates the 21:26 filter rebuild;
post-rebuild list acceptance is still needed. ETG's link-only entry is local
commit `432d44c`; the B1/general and B2/technical-reading distinction is
`8ca977f`. The candidate branch remains local and unpublished.

The candidate is local and unpublished. The personal departure timetable,
finances and legal-route decisions are kept in the separate private roadmap.

The 2026-10-13 review of Canonical's Himalayas card found an unrecognized
required-skills heading. Parsing now recognizes common remote-board requirement
sections, and the interview-risk dimension describes technical requirement
coverage explicitly. Education and language evidence remain separate and
unscored. Full unit and isolated PostgreSQL suites pass; rebuild and live card
confirmation remain before closing this small result-quality item.

## Latest release — v3.5.6

The `main` branch and latest formal GitHub tag/release are v3.5.6. Changelog
entries v3.5.2–v3.5.5 are cumulative milestones included in this release, not
separate releases or tags. The owner completed Telegram acceptance on
2026-10-11: TXT resume import saved after confirmation, unsupported ZIP rejected,
duplicates detected, and Recommendation v2 details displayed with unsupported
signals left unknown.

The v3.5.6 release also includes a focused EURES transport fix and clearer
per-profile market controls:

- EURES sends `Accept-Encoding: identity`; in the live container, a compressed
  response failed during TLS body reading while identity encoding returned the
  full 50-result JSON response.
- `/targets GE` applies the market to all active profiles. Use
  `/targets relocation GE` or `/targets career GE` to set one profile.
- `/sources` shows the source plan for each active profile.
- The owner verified the updated `/sources`, `/scanstatus`, and live scan in
  Telegram. EURES returned 16 parsed vacancies; the supplied later log tail
  shows a successful scheduled scan and responsive command handling. Continue
  monitoring scheduled EURES runs; one success does not establish permanent
  transport stability.
- The owner completed a Relocation-first GE scan: EURES returned 16 jobs,
  HR.ge returned 2, JOBS.GE returned HTTP 410, and Arbeitnow reported a
  transient read timeout. The candidate pauses JOBS.GE and retries one
  transient Arbeitnow transport failure. The owner confirmed the paused state
  in `/sources`; the fresh `/scan` and `/scanstatus` completed. Job Bank took
  99.5 seconds of the 162-second scan. Keep its five-second request pacing
  while evaluating latency improvements.

## Active candidate — v3.5.7 International Market Coverage

Focus on useful, legally reachable vacancies in Georgia and Armenia, while
preserving the separate Career-first and Relocation-first goals.

Remotive uses its official category RSS feed after its API ignored tested
category filters. The latest checked RSS response had channel metadata and no
job items; it is cached for 24 hours across profiles and restarts. Empty source
results remain distinct from a failed request. `/jobs below` and the scoped
commands above expose existing nonzero results for manual review, without
changing scores, thresholds or automatic notifications. Current verification
and runtime acceptance are recorded in `docs/PROJECT_OS/BRIEF.md` and
`HANDOFF.md`.

Next priority is practical Relocation-first coverage and relevance. Broaden
legally reachable work sources beyond technical remote feeds, then evaluate
results with explicit evidence. Keep Career-first independent, retain score
order and owner exclusions, and do not infer visa, hiring eligibility, housing,
or relocation support from missing data.

The active candidate adds selectable `AM` and a bounded Greenhouse Job Board
API connector for Lineate. It runs only for profiles targeting AM or GE,
filters by the profile's role queries and explicit posting location, and leaves
work mode, salary, visa and relocation unknown without direct evidence. The
owner completed Career-first GE/AM discovery and confirmed `/job 1091` renders
readable vacancy text while unsupported fields remain unknown. A follow-up
review found that the posting's `Necessary Qualifications` heading was not
classified as required, allowing an unqualified fallback score of 100. The
candidate recognizes common required-qualification headings, extracts
`Minimum N years` wording, and compares Windows and Databricks signals. The
owner then reported Technical 42 with interview risk `н/д`. The cause was a
second path: Recommendation v2 scored the raw stored HTML while Technical
scored the decoded text. The current candidate passes the same normalized
description to both calculations. A regression expects Technical 42 and risk
58 for the encoded Lineate-style posting. The latest full isolated PostgreSQL
suite passes with 251 tests and 68.44% branch coverage. The local unit run
passes 248 tests with three database-dependent tests skipped when the isolated
PostgreSQL URL is not configured. Commit `8a583c7` passed push CI
`38151840822` and PR CI `38151843490`. The owner confirmed `/job 1091` in
Telegram at 18:42 Moscow time: Technical 42, interview risk 58, and `fit=good`
from explicit required-skill coverage. This score is a matching-gap indicator,
not a calibrated probability. Salary, work mode, visa sponsorship and
relocation remain unknown without direct evidence.

The active `3.5.7` worktree keeps verified Job Bank results when one search or
detail request exhausts its bounded transport retry, while reporting a source
error if all searches or all requested details fail. Requests remain
serialized, with a minimum five-second interval between starts; a slow response
no longer adds an unnecessary full delay. Both profiles give explicitly
remote vacancies earlier processing priority, without changing Match Score or
interpreting unknown remote scope as worldwide eligibility. The current full
verification passes 266 local tests (3 database-dependent tests skipped) and
all 269 tests against isolated PostgreSQL at 69.70% branch coverage.

The owner accepted the Himalayas remote-scope detail card in Telegram at 20:56
Moscow time by opening `/job 1273` (Canonical Associate Linux Support
Engineer). It says the source marks the vacancy worldwide and reminds the user
that the employer must confirm hiring from their country. Salary is absent.
Earlier Telegram checks covered `/sources`, `/scan`, `/scanstatus` and `/jobs`;
20 cached Himalayas jobs were shown with source links at the top of `/jobs`.

The current uncommitted worktree adds a curated Collectly Lever Postings API
source for selected AM/GE profiles. Lever's documented public feed returns a
published remote Senior DevOps/DevSecOps role with a GMT-7 to GMT+4 timezone
range; its source metadata says Belgrade/RS. The adapter keeps country,
city-level hiring eligibility, salary (if not supplied), visa and relocation
unknown, and never submits applications. The employer's hosted form states
that onboarding requires one or two weeks in Yerevan with travel and lodging
covered; this is a lead, not proof that the employer can hire or relocate a
Russian citizen. The source runs only for selected AM/GE, only for explicit
remote DevOps matches whose listed timezone range includes UTC+4, fetches at
most 100 records, and caches results for six hours. Full local suite: 274
passed, 3 database-dependent tests skipped; compilation and diff checks pass.

The Compose `repo` bot was rebuilt from the current worktree at 21:04 Moscow
time, with PostgreSQL healthy and the existing deployment volumes preserved.
Startup `scan_all` completed successfully at 18:06:21 UTC (21:06:21 Moscow).
Lever returned HTTP 200 for both independent profiles. EURES, Job Bank, HR.ge,
Greenhouse, Himalayas, and HH public search also returned successful
responses in the inspected window; HH API 403 recovered through public-web
fallback. A detail-view regression confirms timezone scope is attributed to
the source and does not establish country-level hiring. Targeted detail/Lever
tests pass (16 tests); the full local suite passes (274 passed, 3 database
tests skipped). The owner verified in Telegram that `/sources` lists Lever
for both profiles and `/scan` found one live result in 9.6 seconds. The
completed scan processed 266 jobs (37 Good, 33 Stretch, 196 filtered) and sent
no new notifications; `/scanstatus` completed in 131 seconds. `/jobs` only
shows ten latest matches and omits Collectly. A read-only runtime query found
job #1333 saved as filtered with score 0 because Career-first explicitly
excludes `senior devops`; this is expected behavior, not a source failure. The
detail renderer's timezone and country-hiring caveat is covered by regressions.
PR #18 remains an unmerged draft; v3.5.7 is not tagged or formally released.

The [official Lineate posting](https://job-boards.greenhouse.io/lineate/jobs/8018252)
identifies a Georgian office, requires 3+ years of Linux system administration
and 2+ years of production AWS, and includes a 24/7 shift schedule. It does not
state salary, work mode, visa sponsorship or relocation assistance. The bot
must keep those unsupported facts unknown.

The owner has a near-term relocation objective. Prefer live vacancies with
clear application deadlines and start timing, and record candidate eligibility
only from vacancy or official-source evidence. Missing dates, visa support and
relocation benefits remain unknown. The specific personal timing estimate is
kept out of this public roadmap.

### Next work

1. Collectly was found as job #1333 but filtered by Career-first's explicit
   `senior devops` exclusion. Keep that filter until the owner decides whether
   to include senior roles. The timezone and country-hiring caveat is covered
   by vacancy-detail regression tests; this is not a source failure.
2. Continue auditing public, employer-authorized employer feeds in AM/GE.
   Record API terms, refresh behavior, location/timezone limits, languages,
   expiry, and evidence about international applicants. Keep boards that
   prohibit automated extraction (including Staff.am absent written
   permission) as manual-search destinations.
3. Recheck Lineate and broaden Career-first employer coverage beyond its
   current single Georgian infrastructure lead. Treat each live opening as a
   useful lead, not proof of general market coverage.
4. Improve practical Relocation-first coverage with verified lower-barrier
   roles and lawful eligibility evidence. For remote roles, confirm that the
   employer can hire from the destination country; timezone or worldwide
   labels alone do not establish that. The latest scan produced 74 processed
   and no Good/Stretch; a remote match scoring 54 was filtered by the current
   65-point threshold. The manual exploration view is now available through
   `/jobs relocation below`, preserving its independent scores and
   notifications. Keep local roles as a separate route.
5. Continue measuring Job Bank latency and preserve its five-second pacing.

PR #18 remains a draft awaiting the owner's decision to promote it for merge.
The Himalayas detail-card acceptance is complete. Collectly was discovered but
filtered by Career-first's explicit `senior devops` exclusion; the owner should
decide before changing it. Do not create a release tag until the PR is merged,
the complete candidate is tested, and owner acceptance is recorded.

The owner first checked `/targets relocation GE,AM`, `/sources`, `/scan`, and
`/scanstatus`. Greenhouse · Lineate was enabled and returned HTTP 200, but no
jobs matched the broad non-technical Relocation-first role queries. The owner
then selected GE/AM for Career-first and the live scan returned the Georgia
Infrastructure Engineer. The owner opened `/job 1091` and accepted the readable
description and conservative unknown fields. A bounded Job Bank transport
retry is implemented and deployed; it retries once under the shared crawl lock
with the existing five-second delay, and does not retry HTTP status errors.
After deployment, startup `scan_all` completed at 14:51:38 UTC. Job Bank search
and detail requests and EURES search/detail requests returned HTTP 200. No
transport failure occurred in that run, so runtime retry recovery remains
covered by regression tests rather than a live failure injection.

- The owner confirmed the active Relocation-first target `GE`, the paused JOBS.GE
  status, and a completed live scan: EURES returned 16 vacancies and HR.ge 2.
  Continue checking result relevance and access conditions before treating
  Georgia as validated recurring coverage. Georgia details remain capped and
  paced, scheduled results are cached for six hours, and `/scan` forces a fresh
  fetch.
- Georgia's Labour Migration Law now has 2026-03-01 changes in effect: for
  local paid work, an eligible foreign worker needs a right to work through a
  local employer and then the applicable immigration status. Recheck the
  candidate's case and current rules; selecting `GE` alone does not make a
  local vacancy legally actionable.
- Treat the Georgian adapters as limited personal discovery sources. JOBS.GE
  robots rules were unavailable (HTTP 410), HR.ge allows crawling in
  robots.txt, and neither board's recurring-reuse terms were confirmed. Keep
  request volume low and don't broaden collection without a clear source
  contract.
- Defer bot integration of Armenia's government-listed e-work.am and
  workforall.am: both search pages timed out in the current checks, and no
  public API/feed or automated-reuse terms were found. Manual accessibility
  also remains unverified. Do not
  make cold outreach to government agencies a release prerequisite. The
  official e-work registration requirements apply to registration with that
  service; they do not establish a general ban on applying directly to
  employers.
- The Lineate feed uses Greenhouse's documented unauthenticated public GET API.
  The selected-country scope prevents its other office listings from being
  labeled as Armenia/Georgia jobs. Keep expanding the employer list only when
  the employer's public ATS board and a relevant current role are verified.
- Staff.am has listings in the candidate's DevOps/Infrastructure area and may
  be useful for manual search. Its current terms prohibit automated scraping
  without written permission. Job.am terms restrict unauthorized reuse and
  redistribution. Do not add either as a bot collector unless the owner grants
  access through a documented feed or permission.
- The official Armenian `workpermit.am` portal provides an employer-side
  foreign-hiring/work-residence workflow and says EAEU citizens are exempt
  from work-permit documentation for the employment-contract period. It is
  not yet verified as anonymous job discovery or a public feed. Its FAQ
  question “How to find a job” is visible but the answer is not rendered; the
  official user guide describes an employer-led vacancy and foreign-worker
  account flow. Defer integration unless a relevant public feed or documented
  authorized access route is identified; no agency email is needed to continue
  the release.
- Keep Armenia's EAEU work-permit exemption separate from residence paperwork:
  the official portal says its lawful-residence certificate cannot be printed
  without a Public Services Number.
- Official e-work registration guidance requires a PSN or national eID online;
  its in-person path for foreign nationals requires a residence card. These
  are prerequisites for registering with that state employment service, not
  proof that a foreign candidate cannot apply directly to an employer. Keep
  portal access and individual legal eligibility as separate questions.
- Prefer permitted employer career feeds, documented public APIs, and
  owner-selected Telegram channels where available. Require a working
  posting URL, publication/expiry checks, location, language and eligibility
  evidence; do not mirror a whole job board.
- Expand role aliases for English, Russian, Georgian and Armenian searches
  where they improve real result coverage. Keep translations curated and
  deduplicate equivalent vacancies.
- Keep visa sponsorship, work authorization, relocation support, salary and
  language requirements as separate evidence fields. Never assume citizenship
  from the current country or turn missing evidence into a refusal.
- For Georgia, current law requires covered foreign workers in local paid work
  to hold the right to work, employment agreement and applicable immigration
  status; the employer submits the right-to-work application. Selecting `GE`
  must not be presented as proof that a candidate is eligible.
- `/salary minimum` currently contributes to scoring when salary is structured;
  it is not a hard exclusion rule. The bot's “minimum for filter” wording is
  misleading, and `/job 580` showed a 90,000 RUB amount only inside the
  description while the structured salary remained unknown. Clarify this
  behavior or implement a separately tested strict floor before relying on it
  to remove below-minimum vacancies.
- Measure EURES success by parsed search/detail results per profile, not by
  response status alone; retain partial results and keep retries bounded.
- At the start of this candidate, verify both independent target/query paths
  in Telegram. The owner completed the Relocation-first GE/AM source check;
  the live API returned HTTP 200 and zero role matches. Career-first GE/AM
  verification later found the Lineate role, and `/job 1091` was accepted with
  unsupported fields left unknown. See the dated handoff entries above.
- For near-term relocation decisions, keep opening status, application
  deadline, expected start date and work-eligibility evidence separate. Add
  these fields only when a source provides them; do not infer processing time.

## Later stages

- **v3.6 — Candidate and vacancy fit:** validate technical fit, relocation
  viability, salary normalization and affordability with explicit evidence.
- **v3.7 — Application workspace:** improve resume-to-vacancy tailoring and
  track manually confirmed application stages; no automatic application.
- **v3.8 — Recruiter and interview support:** prepare grounded recruiter replies
  and interview practice from the vacancy and confirmed candidate facts.
- **v4.x — Productization:** consider a dashboard or multi-user operation only
  after the personal workflow is stable and the owner wants that scope.

## Release rules

- Keep one release title format: `vX.Y.Z — Feature Name`.
- Publish a GitHub Release only for the tested version tag and include its test
  results, migration status and any owner acceptance still required.
- Keep `VERSION`, `CHANGELOG.md`, README status and the release tag aligned.
- Treat `VERSION` as the source-tree version and a Git tag/Release as the formal
  publication marker. When several cumulative milestones were never tagged,
  publish one tested cumulative release; do not create retroactive tags that
  imply separate releases were accepted.
- Never enable auto-apply, private HeadHunter actions or destructive database
  operations as part of a release.
