# Roadmap

Canonical product roadmap. Reviewed against local source and tests on 2026-10-14.
The active branch is `feature/v3.5.7-international-market-coverage` with
`VERSION=3.5.7`; the latest formal release is v3.5.6. Older observations below
are dated history, not current runtime or test claims. The two owner proposal
files are reference material and remain untracked.

## Product direction and evidence rules

The personal workflow is discover → normalize/deduplicate → evaluate → review →
prepare → approve → apply → track → interview → offer. Career-first for
DevOps/Infrastructure/SRE and Relocation-first for legally actionable work,
including suitable non-IT work, remain independently configured. Remote work,
country hiring, work authorization, visa support and relocation assistance are
different facts. Unknown evidence stays unknown; no candidate experience,
salary or employer promise is invented. A source registration or HTTP 200 is
not proof of useful collection. Employer ATS facts should retain source links
and provenance when later reconciled with board and Telegram copies.

## Capability and delivery map

| Stage | Verified state and remaining scope | Acceptance gate |
| --- | --- | --- |
| v3.5.1 foundation | Implemented baseline: bot, persistence, matching, review queues and source dedupe (`app/services.py`, `app/database`, `app/telegram`). | Maintain tests and working review flow. |
| v3.5.2 Search Control Center | Core implemented in `SearchProfile.settings`, settings handlers and tests: source/market controls, independent strategies, salary inputs and blacklist. An optional strict salary floor is OFF by default and excludes only known comparable structured values whose upper bound is below the monthly minimum; unknown evidence remains reviewable. Salary ranking likewise compares against a monthly minimum only for explicit monthly/yearly structured periods; missing or unsupported periods now use a neutral score. Vacancy display shows an explicitly stated salary period near a currency-bearing amount, but does not normalize unknown periods or use display text to change filtering/scoring. Per-source destination behavior is partial. | Test each source's actual market behavior; keep priority distinct from hard exclusion and explain that salary minimum is a scoring reference. |
| v3.5.3 Fast Scan | Core implemented: bounded concurrent discovery, cache, `/scanstatus`, `/cancel` (`app/search`, `app/telegram`). Adaptive detail fetching is planned. | Preserve rate limits and cancellation semantics; measure useful results and latency. |
| v3.5.4 Multi-Source vision | Historical v3.5.4 code milestone added EURES; broader original vision remains partial. Current branch also has HH, RemoteOK, Arbeitnow, Job Bank, HR.ge, selected ATS, Himalayas, Remotive and Telegram paths. JOBS.GE is paused. | Verify permitted, live, relevant results per source; expand only with an access contract. |
| v3.5.5 Candidate Import | PDF/DOCX/TXT preview, one-time confirmation, explicit save, provenance and overlap handling implemented (`app/candidates`, import tests). Resume plus proposed facts now commit atomically and can retry after a failed transaction; per-conflict ADD/UPDATE/KEEP now has a local preview/confirmation flow with retained history and unknown replacements. PostgreSQL UPDATE and runtime acceptance are pending. | Resolve conflicting facts visibly without upgrading lab or learning to commercial work. |
| v3.5.6 Recommendation v2 | Explainable heuristic breakdown implemented (`app/matching/recommendation.py`); interview-risk is a fit-gap score, not calibrated interview probability. | Validate signals and missing data; preserve established threshold/notifications until deliberately changed and tested. |
| v3.5.7 International / Relocation | Active candidate: GE/AM and remote adapters, scoped `/jobs`, conservative evidence parsing, 65-point threshold. Relocation Evidence v1 stores per-source work-country, citizenship/residence restriction, prior authorization, sponsorship, relocation, housing, language and start-timing signals with capture time, excerpt where observed, and bounded confidence; unknowns remain explicit. Work-country excerpts retain adapter structured location text when available. Housing is confirmed only for explicit provide/refuse wording; language records multiple languages independently as required/preferred/unspecified/conflicting and keeps CEFR separate. Start timing preserves the exact phrase and a bounded kind (immediate, relative, stated date, notice period, negotiable). Citizenship and residence excerpts retain distinct scope labels. Existing work authorization distinguishes explicit required/not-required, unknown and conflicting text. Sponsor/relocation cross-component parser ambiguity remains unknown rather than inheriting another component's refusal. Synthetic German conditions are covered; `Deutschland` is not misread as `Deutsch`. Vacancy details display source provenance and stay within Telegram's UTF-16 message budget by trimming long descriptions while preserving the evidence block. Useful coverage and runtime acceptance remain partial. | Continue source-specific country/hiring-scope extraction with fixtures; validate official dated legal references and live scoped Telegram acceptance separately. Do not make legal eligibility conclusions from posting text. |
| Proposed v3.5.8 Telegram Channel Watcher | Bot API selected-channel posts/captions, scoped subscriptions, provenance, replay guard and bounded persistent retry implemented locally (`app/sources/telegram_watch.py`, watcher tests). Edited posts, history and arbitrary channel monitoring are not implemented. | Owner selects channels and grants Bot API access; separately authorized runtime check of `/channels`, new post, replay/retry and both profiles. |
| Proposed v3.5.9 Source Intelligence | Partial: local typed diagnostics, per-profile attempt history, actual retry counters, incomplete outcomes, latest scheduled history, per-source received-before-preferences/excluded-by-preferences counters plus processed/Good/Stretch/filtered/duplicate yield and nonempty publication-date-field coverage implemented. Remotive timezone-aware RSS RFC 2822/API ISO dates and Arbeitnow numeric epoch seconds normalize to UTC; vacancy detail displays aware publication times in UTC, date-only fields as dates, and timezone-naive times explicitly as timezone-unknown. This does not infer freshness. Repeated discovery for an existing source ID now refreshes nonempty vacancy fields and current source raw payload while retaining verified detail cache and first-seen provenance; PostgreSQL advisory/row locks serialize same-source and canonical-fingerprint upserts. Complete changed identity fingerprints update only when they do not collide with another stored Job; conflicting records are not merged, preserving existing match ownership. More authorized ATS/official feeds, company watchlist, safe reconciliation of pre-existing cross-source duplicates and source-specific freshness/expiry metrics remain planned. | Attributed relevant vacancies and measurable source yield, not just enabled adapters. |
| v3.6 Candidate + Vacancy Fit | Partial: deterministic required/preferred/unknown skill sections and Candidate Fact comparison exist. Explicit “no <skill> [experience] required” / “<skill> not required” phrases no longer become technical must-haves solely because they appear beneath a Requirements heading; direct skill-specific “is a plus” / “будет плюсом” wording in that section is classified preferred, while separate requirements stay independent. The technical vocabulary now recognizes OpenShift independently, including “Red Hat OpenShift”. `/compare` links matched skills to the strongest Candidate Fact IDs and provenance, with `/facts` and `/fact` correction commands. `/resumediff <vacancy_id> [resume_id]` shows which recognized vacancy skills appear in the selected CV and/or active Candidate Facts; it is a read-only checklist and does not generate or modify claims. For an explicit `or/или` alternative group, the CV check now requires one same option to appear in both the CV and Candidate Facts, flags mismatched evidence, and still surfaces any extra CV option without a matching fact. Explicit two-or-more-skill `or/или` chains, Oxford-comma lists, and isolated or nested-flat parenthesized choices alongside an independent skill count as one scoring choice when unambiguous, including line-wrapped connectors; pure OR parentheses produce one nonoverlapping group; mixed nested `and/и` expressions and repeated requirements stay ungrouped; comma-only skill lists remain separate requirements. Explicit English CEFR evidence is compared separately with the user-controlled profile level and does not change score; fresh owner bootstrap uses general English rather than technical-reading level. Vacancy language cues distinguish explicitly required, preferred, and unspecified CEFR statements. Foreign vacancy details separate sponsorship, relocation, work-permit help and pre-existing authorization evidence. Broader language phrasing, candidate-specific legal eligibility, salary and private affordability, plus reviewed tailored RU/EN resume edits remain planned. | Every material CV assertion traces to a confirmed fact and user approval. |
| v3.7 Application Package / Workspace | Partial: `/prepare <vacancy_id> [career|relocation]` and the preparation button provide the selected saved CV, a grounded draft cover letter, vacancy link and Candidate Fact/CV skill consistency checklist; explicit scope resolves only against the owner's active search profile. LLM cover-letter generation uses separate developer instructions and JSON-encoded untrusted vacancy/resume/fact data; this reduces instruction-following risk but does not guarantee claim correctness, so manual review remains required. Empty skill extraction is disclosed as unrecognized rather than described as an absence of discrepancies. Each prepared draft is stored with exact cover-letter text, local resume-text snapshot, external resume ID when known, source URL, timestamp and `prepared` status; schema v7 freezes vacancy title/company/description/source URL, and the JSON snapshot now also freezes the source-scoped Relocation Evidence captured at preparation. HH applications preserve the same evidence snapshot. `/applications` lists records; `/application <id> <status>` supports owner-scoped manual updates, `/application <id> history` shows append-only status events serialized per application to avoid concurrent duplicates, and `/application <id> export` includes the saved text/evidence snapshots, cover-letter text, vacancy metadata and recorded status timeline on explicit user request. Exports clarify that owner-maintained status does not independently prove employer/provider receipt. v5–v7 upgrades and idempotency are tested from a v4 schema; older rows receive only their known current status at original creation time, not fabricated transition history. Export uses the saved vacancy/evidence snapshots without fetching the current Job. Old records without resume/vacancy/evidence snapshots disclose that fact and are not backfilled from current source data. The bounded preview flags unsupported CV-only mentions, shows employer mobility/prior-authorization evidence without personal eligibility claims, rejects unsafe or malformed links and never submits. Original-format CV export, reusable question answers, verifiable provider-side submission receipt and richer application history remain planned. | Human reviews every claim and approves each external action; distinguish saved local CV text from provider-side documents and retain exact package evidence. |
| v3.8 Application + Recruiter Agent | Partial: `/applications` and manual status/history are implemented; HH recruiter drafts are grounded in Candidate Facts, sensitive topics found in the question or supplied conversation context require a human, and the owner-only send route stays separate. Recruiter model calls use separate developer instructions with context/question/Candidate Facts passed as untrusted JSON data. Auto-reply defaults OFF and requires explicit configuration. Model generation and send failures now degrade to a private manual-response alert without logging exception payloads. Reminder scheduling, broader reply channels and follow-up management remain planned. | Correct transitions, no duplicate contact, explicit approval for outbound messages. |
| v3.9 Practical Interview Agent | Initial slice implemented: `/interview <vacancy_id> [career|relocation]` provides up to five curated troubleshooting exercises from recognized vacancy requirements, ordered required/preferred and labeled with the candidate's stored Fact type. Scenarios cover Linux, Nginx, Docker, DNS, TLS, Kubernetes, OpenShift, Helm, Terraform, Ansible, AWS, CI/CD, PostgreSQL, Prometheus, Grafana and safe security incident response. The OpenShift exercise covers rollout, image, probes and Route checks without weakening SCC/RBAC. It is deterministic, makes no model/API call, and does not claim to predict an interview or score the candidate. Interactive answers, feedback and gap-to-learning progression remain planned. | Reproducible scenarios and gap-to-learning feedback grounded in the vacancy. |
| v4.x Productization | Optional later: web UI, multi-user separation, AI router/local models, observability and monetization after personal utility. | Privacy, cost, quality and consent measured before broad rollout. |

The proposed v3.5.8/v3.5.9 numbers are planning labels only. `VERSION` and
release history do not change from this roadmap sync. Cross-cutting work:
official, dated relocation legal references with unknown/partial flags;
source/candidate provenance; privacy and safe backups; bounded collection;
AI Stack Watch with dated model/license/cost evidence; and an opt-in, reviewed,
idempotent context-delta import. Current Context Watch does not imply live
access to other chats. `docs/PROJECT_OS/` stays the portable handoff; this file
is its sole canonical roadmap.

Local reliability/security follow-up (2026-10-14): per-user scheduled scan
isolation, private-chat Telegram user routes, owner-only global HH applicant
actions and safe source error summaries are implemented with regressions.
One failed vacancy now preserves later results from the same source.
Georgia source detail requests now require their own HTTPS host.
Job Bank now has bounded one-hour detail reuse for repeated scheduled scans;
post-deployment latency and relevance measurement remains pending.
EURES now preserves partial results across individual HTTP and parse failures.
Query/detail failure counts travel with cached source results and appear in
scan summaries and `/scanstatus` without changing match scores. Discovery
observations distinguish reused caches from independent failures; earlier
profile processing-error counts survive subsequent successful profiles.
Dependency minimums now exclude checked pypdf/python-multipart advisory ranges;
a reproducible lock/constraints workflow remains planned.
Telegram/HH network warning logs now omit raw exception messages.
Typed transport-cause diagnostics and raw SSL/DNS sanitization are implemented
locally. Runtime acceptance and live HH ConnectError diagnosis remain open.

## Immediate gates

1. Validate selected Bot API channels and owner-approved runtime only after
   explicit authorization; local watcher tests do not prove actual access.
2. Review real Career-first and Relocation-first results, source permissions,
   time-sensitive eligibility and scoped Telegram cards before v3.5.7 release.
3. Expand permitted AM/GE and lower-barrier sources only after live relevance
   and access evidence; retain unknowns and 65-point scoring integrity.

Local source observability (2026-10-14): IMPLEMENTED attempt history, safe
Russian typed error classification, per-pass alert dedupe, incomplete manual
scan/status and RemoteOK schema validation. Production alert attribution,
network root causes and live acceptance remain BLOCKED on permitted evidence;
scheduled history persistence, bounded Telegram views, Job Bank HTTP/schema
response isolation and staged/worktree secret guard are IMPLEMENTED locally.
Final 844 unit/4 skipped; isolated DB and production acceptance remain BLOCKED.
No score/visa policy change; useful Relocation-first coverage stays PARTIAL.

## Historical v3.5.7 development notes

The following entries preserve the dated development record. Where their
phrasing says “current” or “next,” use the capability map and PROJECT_OS handoff
above for the present state.

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
