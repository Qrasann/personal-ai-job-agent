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
  version v3.5.6 and cumulative changelog milestones are distinct from formal
  releases; publish one cumulative v3.5.6 release after acceptance.
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
- [x] Owner completed Telegram acceptance: unsupported ZIP rejected, duplicate
  resumes detected, TXT resume #6 saved after confirmation with zero facts
  proposed, and `/job 580` displayed Recommendation v2 with unsupported
  dimensions unknown.
- [x] Prepare one cumulative v3.5.6 release; keep v3.5.2–v3.5.5 as untagged
  milestones included in it rather than creating retroactive tags.
- [x] Push annotated tag `v3.5.6` on CI-verified commit `50afdab` and publish
  the bilingual GitHub Release after CI run `38138941745` passed.
- [ ] Monitor later scheduled EURES scans; the first clean run does not prove
  the underlying TLS cause is permanently resolved.
- [x] Change Job Bank pacing to enforce at least five seconds between request
  starts, without an extra wait when a slow response already consumes the
  interval. Requests remain serialized. Regression tests verify both fast and
  slow responses and concurrent callers.
- [x] Owner compared a post-update Telegram `/scan` and `/scanstatus` at
  20:42–20:44 Moscow: Job Bank returned 12 results in 71.2s, down from 100.7s
  in the earlier check; EURES returned 16 in 34.1s. The supplied scan log has
  no source failure. The retry/partial-recovery path remains verified by tests,
  since this live scan had no transport failure.

## v3.5.7 International Market Coverage — active candidate
- [x] Add jobs.ss.ge as a selected-Georgia manual-search destination after
  confirming that it exposes broad vacancy listings but no verified reusable
  public API or automated-collection permission. Keep it link-only. Targeted
  source tests: 5 passed; full suite: 443 passed, 3 skipped; isolated
  PostgreSQL suite: 446 passed; compileall, secret scan and diff check passed.
  Rebuild and Telegram check remain pending.
- [x] Skip HH immediately on public-search `httpx.ConnectError`; let source
  isolation finish other feeds. Keep the single retry for other transient
  transport errors. Targeted tests: 15 passed; full suite: 443 passed, 3
  skipped; isolated PostgreSQL suite: 446 passed; compileall, secret scan and
  diff check passed. Commit `5a815b5` rebuilt Compose `repo` at 00:43 Moscow;
  startup scan completed at 21:44:48 UTC with PostgreSQL healthy. Runtime logs
  show HH skipped on `ConnectError` while Himalayas, Remote OK, Arbeitnow,
  Job Bank, EURES, Greenhouse, Lever and HR.ge continued successfully.
- [x] Add one bounded retry for transient transport failures in the public HH
  API and web-search requests. This directly addresses the observed TLS
  `ConnectError`; it does not assume Yandex is the cause. Do not retry HTTP
  errors/CAPTCHA or change private applicant endpoints. Targeted HH tests: 13
  passed; full local suite: 441 passed, 3 skipped; isolated PostgreSQL: 444
  passed; compileall, secret scan and diff check passed.
- [x] Commit as `b427e96` and rebuild Compose `repo` without changing named
  volumes. Source/runtime report 3.5.7 and PostgreSQL is healthy. Startup scan
  completed at 00:25 Moscow; HH API 403 fell back to public search, where a
  TLS `ConnectError` triggered the new single retry. Later public HH requests
  returned HTTP 200 and `scan_all` completed successfully. No causal claim is
  made about Yandex infrastructure.
- [x] Recognize common remote-board requirement headings (`What we are
  looking for`, `What you'll bring`, `Nice-to-have skills`) so existing
  technical requirement coverage is not left unknown; label interview-risk
  as the technical-risk index (`100 − requirement coverage`) and leave
  nontechnical conditions unscored. Targeted suite: 37 passed; full isolated
  PostgreSQL suite: 442 passed; compileall, secret scan and diff check passed.
  Risk formula commit `a3a2494` and curly-apostrophe test commit `e382ddb` are
  applied in Compose 3.5.7; startup scan completed after an isolated source
  error. Telegram `/job 1273` confirmation remains open.
- [x] Keep the candidate's current self-assessed general English at B1 and
  retain B2 only as a technical-reading estimate in the fresh-profile defaults.
  Add regression coverage; do not overwrite facts on existing profiles.
- [x] Check the official Emerging Travel Group Junior DevOps listing and
  Workable's documented public jobs endpoint. The role currently names AM/GE,
  remote, 1.5+ years commercial DevOps, six months Kubernetes, and English
  B1+; endpoint returned 403. Add the employer's official posting as a
  link-only manual source and do not scrape or infer legal eligibility.
- [x] Commit the English distinction and ETG manual lead as `8ca977f` and
  `432d44c`; synchronize PROJECT_OS and private context to current Git state.
- [ ] After rebuild, owner verifies `/sources`, `/jobs relocation`, and
  `/jobs relocation below`; the supplied 21:13 Telegram lists predate the
  21:26 rebuild of the domestic-onsite filter.
- [x] Align the AI job-bot's bootstrap profile with the owner's current
  equal-priority GE/AM plan and add bounded lower-barrier Relocation-first
  role queries. Existing persisted user settings remain unchanged; add a
  configuration regression.
- [x] Audit bounded employer support evidence across preferences,
  recommendations, and source adapters. Preserve unknown values, distinguish
  separate support components, and prevent role requirements or guidance from
  being reported as offers.
- [x] Compare annual salary amounts with monthly profile minimums without
  changing source amount/period; display known annual/monthly/hourly/weekly
  periods. Hourly/weekly comparisons stay unknown without contracted hours.
- [x] Reset stale scan dashboard fields when a new manual scan begins and
  isolate independent source failures while retaining successful discoveries.
- [x] Preserve the original persisted Remotive response age across restarts and
  forced scans; show Himalayas timezone bounds as provider claims in details.
- [x] Resumed full validation: 424 local passed / 3 skipped; isolated
  PostgreSQL suite 427 passed, 73.22% branch coverage; compileall and
  `git diff --check` passed.
- [x] Publish the cumulative candidate as `8da96f8` on PR #18's existing
  feature branch; push CI `38280187127` and PR CI `38280191809` passed. Safely
  update/start Compose `repo`, verify source/runtime 3.5.7, healthy PostgreSQL,
  and the unchanged named PostgreSQL/storage volumes.
- [x] Diagnose the startup scan's EURES database failure: fixed-width source
  whitespace made `cityName` exceed the 256-character city column. Normalize
  whitespace; preserve genuinely overlong source text as raw evidence and
  keep city unknown. Full isolated PostgreSQL suite: 429 passed, 73.24% branch
  coverage; targeted EURES suite: 13 passed; compile and diff checks passed.
- [x] Publish EURES follow-up `159d510` to PR #18; push CI `38281187340` and
  PR CI `38281192380` passed. Safely update Compose `repo`, verify healthy
  runtime 3.5.7 and unchanged named volumes. The fresh startup scan completed
  at 17:04:14 UTC after EURES HTTP 200 responses with no database/source error,
  traceback, or repeated city-width insertion failure in the log window.
- [x] Add profile-specific `/jobs career|relocation [below]` lists using each
  enabled profile's own threshold; retain independent scores through detail
  and comparison buttons and explicit `/job`/`/compare` scope arguments.
- [x] Correct ordinary `hotel staff`/`warehouse staff` being classified as
  engineering Staff/Senior. Keep technical Staff, seniority, high-experience,
  management and user exclusions covered by regressions.
- [x] Verify selected-score isolation, user ownership, legacy callbacks and
  below-threshold scope. Full local suite: 319 passed, 3 skipped; all 3 isolated
  PostgreSQL repository tests passed; compilation and diff checks passed.
- [x] Add an at-a-glance roadmap showing completed, current and later stages;
  maintain the private relocation roadmap separately with current official
  legal references and progress.
- [ ] Verify the new scoped commands/cards in Telegram after local rebuild.
- [x] Evaluate bounded HH search for selected destinations. Verify HH's public
  `/areas` catalog: Russia is area `113`, Georgia is area `28`, and Armenia is
  not present. Search each represented current/target
  market independently, deduplicate results, and attribute country only from
  the scoped area query; do not guess an Armenia area. Local suite: 430 passed,
  3 skipped; isolated PostgreSQL suite: 433 passed; compileall, secret scan,
  and diff checks passed. This source change is committed locally as `552cb72`;
  Telegram/runtime acceptance remains pending.
- [x] Add the Himalayas documented public search API as a bounded remote
  source: up to four active-profile queries, three selected markets and one
  page of 20 jobs per query/market; cache for 24 hours and show source links
  and salary periods in Telegram.
- [x] Preserve provider country restrictions; missing restrictions remain
  unknown and no individual visa/work/payroll eligibility is inferred. Stop
  treating RemoteOK's unspecified hiring geography as worldwide.
- [x] Add regressions for country scope, unknown eligibility, salary periods,
  attribution, bounded requests, partial failures and cache isolation. Targeted
  suite: 41 passed.
- [x] Full local suite: 266 passed, 3 database tests skipped; isolated
  PostgreSQL suite: 269 passed; branch coverage 69.70% against the 55% gate.
  `compileall` and `git diff --check` passed.
- [x] Rebuild Compose project `repo`; app and PostgreSQL healthy, original
  named volumes `repo_jobagent_v3_pg` and `repo_jobagent_v3_files` remain
  attached. Startup scan completed at 17:35:32 UTC. Himalayas requests for GE
  and AM returned HTTP 200; the inspected log window showed no source errors.
  HH API returned 403 and public web fallback succeeded.
- [x] Owner verified `/sources`, `/scan`, `/scanstatus`, and `/jobs`: Himalayas
  returned 20 cached roles and appeared first with source links; Career-first
  processed 191 jobs and Relocation-first 67. Job Bank returned 12 in 71.2s,
  EURES 16 in 34.1s. Supplied log excerpt shows no source exception or SSL
  failure; HH API 403 recovered through the public-web fallback.
- [x] Owner verified Telegram `/job 1273` at 20:56 Moscow time: the card shows
  Himalayas' worldwide scope and explicitly says the employer must confirm
  hiring from the user's country. The listing had no salary. Logs show the
  Telegram update handled in 567ms without an error.
- [x] Add a curated Collectly Lever Postings API source for selected AM/GE
  profiles. Keep the Belgrade/RS source location separate from remote-country
  eligibility; require a remote workplace and a public timezone range covering
  UTC+4; preserve unknown country, visa, and relocation facts. Do not submit
  applications.
- [x] Add Lever regressions for role, remote mode, timezone scope, selected
  markets, salary metadata, attribution URL, malformed payloads, and source
  registration and safe timezone text in vacancy details. Full local suite:
  274 passed, 3 database tests skipped;
  `compileall` and `git diff --check` passed.
- [x] Rebuild local Compose `repo`; verify PostgreSQL healthy and startup
  `scan_all` completed at 18:06:21 UTC. Lever returned HTTP 200 for both
  profiles; inspected scan logs contain no source exception.
- [x] Owner verified `/sources` lists Lever for both profiles and ran
  `/scan`/`/scanstatus`: 1 live Lever vacancy in 9.6s; complete scan in 131s,
  266 processed, 37 Good, 33 Stretch, 196 filtered, 0 new notifications.
  Job Bank returned 12 in 71.4s; EURES 16 in 55.2s; no source error appeared
  in the supplied log excerpt.
- [x] Inspect the saved Collectly Lever match after `/jobs` omitted it. Read-only
  runtime query found job #1333 saved as `filtered`, score 0, because the
  Career-first profile explicitly excludes `senior devops`; this is expected
  filtering, not a source failure. The detail renderer's timezone/country
  caveat has regression coverage. Keep the explicit filter unless the owner
  chooses to change it.
- [x] Add an explicit remote-work processing preference to both independent
  profiles. It orders remote vacancies earlier within each source result batch,
  preserves each profile's role queries, leaves Match Score and notification
  thresholds untouched, and does not treat unknown remote scope as worldwide
  eligibility.
- [x] Add regressions for remote/onsite ordering across strategies, unknown
  scope, and negated remote labels. Full isolated PostgreSQL suite: 257 passed,
  68.59% branch coverage; local suite: 254 passed, 3 database-dependent tests
  skipped; compileall and `git diff --check` passed.
- [x] Verify remote work is surfaced to the owner after the candidate update:
  Telegram `/review` and `/stretch` showed remote CloudCops 88/Good and Sporty
  Group 72/Stretch. Regressions verify source-batch processing priority across
  strategies; source geography remains qualified and unknown eligibility is
  not inferred.
- [x] Keep vacancy priority aligned with match rating: `/review`, `/stretch`,
  and `/saved` already sort highest score first; `/jobs` now does the same and
  uses recency only to break ties. The owner confirmed that higher-rated jobs
  should always have higher priority. Keep the notification threshold at 65;
  do not promote lower-rated results ahead of higher-rated ones.
- [x] Add Remotive's official remote DevOps/Sysadmin feed with a single shared
  daily response cache in existing PostgreSQL runtime state. Link each listing
  to Remotive and show its name; retain explicit location scope, reject clear
  country-only mismatches, and leave free-text salary unstructured. Verify
  profile sharing, restart persistence, source attribution, parser behavior,
  and no application capability.
- [x] Owner confirmed `/sources` lists Remotive and `/scan` completes; record
  the actual count rather than treating HTTP 200 as usable results. The first
  scan returned 0 because category query parameters returned a general feed.
  The worktree now uses Remotive's official Devops RSS feed and bumps the cache
  key to v3. Targeted and full unit tests pass; rebuild returned a valid RSS
  response with zero items. Recheck after the cache expires and confirm `/jobs`
  attribution if the feed returns a match.
- [x] Add `/jobs below` as a manual-review view of nonzero scores below the
  configured threshold. Keep descending order; exclude duplicate and zero-score
  results; state that legal work and relocation eligibility require separate
  confirmation. Do not change Match Score or notification behavior.
- [x] Give the immediate startup `scan_all` job a five-minute scheduler
  misfire grace. A local restart showed the old one-second default could skip
  the first scan after a brief startup delay; regression test covers the job
  registration, and the rebuilt app started the scan immediately.
- [ ] Improve practical Relocation-first results while preserving the 65-point
  threshold, descending score order, independent search direction, and
  evidence-based visa/work eligibility. Current scans can complete with 0
  Good/Stretch; investigate relevance and source coverage without inflating
  scores or changing owner exclusions.
- [x] Review JOBS.GE and HR.ge robots guidance and add conservative request
  bounds. Terms/reuse permission remains unverified; owner must inspect scan
  quality before treating the sources as useful.
- [x] Review the official Armenian jobseeker registration guidance. Its PSN,
  national eID, and residence-card requirements describe registration with the
  state service; they do not establish a general ban on direct employer
  applications.
- [x] Check current official Armenian source candidates: the Unified Social
  Service lists e-work.am and workforall.am; both public search pages timed out,
  and no API/access terms were found. Online e-work registration requires PSN
  or national eID; the in-person foreign-citizen path requires a residence card.
- [x] Review the official `workpermit.am` employer-side foreign-hiring flow and
  EAEU exemption. Its FAQ lists a job-finding question, but the answer is not
  rendered; the official guide documents an employer-created vacancy and
  employer entry of the selected foreign worker. The lawful-residence
  certificate is separate and requires a Public Services Number to print. No
  anonymous job feed is verified.
- [x] Recheck the current Georgian Labour Migration Law: the new right-to-work
  process for covered foreign workers is in force from 2026-03-01.
- [x] Review current Staff.am and Job.am terms. Keep them as manual search
  destinations; do not automate collection or reuse without a permitted feed
  or written permission.
- [x] Defer cold outreach to the Unified Social Service and Migration Service:
  it is not a prerequisite for this release, and no documented public feed or
  API has been identified.
- [x] Add Armenia (`AM`) to the supported country catalog without implying a
  government-board integration or individual eligibility determination.
- [x] Connect Greenhouse's public Job Board GET API for the Lineate board when
  AM or GE is selected. Match active role queries and explicit locations;
  leave visa/relocation support unknown without direct posting evidence.
- [x] Add Greenhouse regressions for selected-country scoping, role matching,
  explicit support evidence and API contract errors. Targeted source/country/
  preference tests: 20 passed.
- [ ] Evaluate permitted employer career/ATS feeds, documented public APIs,
  and owner-selected Telegram channels for Armenia/Georgia. Verify role
  relevance, location, language, expiry, access conditions, and eligibility
  evidence before integration.
- [x] Confirm owner-visible `/sources`, `/jobs`, `/jobs relocation`, and
  `/jobs relocation below` rendering in Telegram. The output exposed Russian
  onsite jobs in the relocation lane; suppress same-current-country onsite
  jobs for Relocation-first unless domestic relocation is explicitly enabled.
  Keep explicit remote and unknown-country jobs; preserve Career-first and
  score semantics. Targeted tests 49 passed; full local suite 437 passed / 3
  skipped; isolated PostgreSQL 440 passed; compileall, secret scan and diff
  check passed. Rebuilt Compose 3.5.7; startup scan completed at 18:26:17 UTC,
  PostgreSQL healthy. One HeadHunter web request logged transient ConnectError.
  Owner confirmation of the filtered output remains open.
- [x] Add verified Armenia/Georgia manual-search links to `/sources` for ITA
  Jobs, Staff.am, Job.am, CareerCenter.am, Findjobs.ge and LeverX Careers.
  Manual entries are clickable, excluded from scanners and source toggles, and
  explicitly do not imply work eligibility. Findjobs.ge terms prohibit
  repeated/systematic extraction of substantial data without written
  permission, so no recurring adapter was added. Full local suite: 432 passed,
  3 skipped; isolated PostgreSQL suite: 435 passed; compileall, secret scan,
  and diff check passed. Rebuilt Compose `repo`; startup `scan_all` completed
  at 18:06:12 UTC, runtime is 3.5.7 and PostgreSQL is healthy. No manual
  portal was requested during the scan.
- [ ] Keep visa sponsorship, work authorization, relocation support, salary
  and language evidence separate; unknown remains unknown.
- [x] Run the full isolated PostgreSQL suite and compile checks for the v3.5.7
  candidate after the encoded-HTML fix: 241 passed, 68.23% branch coverage;
  `git diff --check` passed.
- [x] Preserve Job Bank results when an individual query or detail request
  exhausts its bounded transport retry; continue processing other queries and
  vacancy details. Keep the five-second request pacing and avoid parallel
  calls. Full PostgreSQL suite: 251 passed, 68.44% branch coverage.
- [x] Owner ran Telegram `/scan` and `/scanstatus` at 19:33–19:36 Moscow time.
  The scan completed with Job Bank 12, EURES 16, HR.ge 2, HH 209, Remote OK 3,
  Arbeitnow 2 and Greenhouse 1; Job Bank took 100.7 seconds. Supplied logs show
  Job Bank detail requests and EURES/HR.ge requests returning HTTP 200, with no
  Job Bank warning or source failure in the excerpt. This confirms a healthy
  live run; partial transport-failure recovery remains covered by regression
  tests because no failure occurred during this scan.
- [x] Push candidate commit `4ccae7f`; GitHub push CI run `38143185017` passed
  Python checks, Docker build and secret scan.
- [x] Push HTML-entity fix commit `5d6b00b`; push CI `38147877309` and PR CI
  `38147879757` passed Python checks, Docker build and secret scan.
- [x] Open draft PR #18; GitHub checks `38143909265` and `38143905027` passed.
  Keep it unmerged until the fixed Telegram detail card is confirmed.
- [x] Apply with the safe updater; verify source/runtime 3.5.7, healthy
  PostgreSQL, attached original volumes and completed startup scan.
- [x] Owner checked `/targets relocation GE,AM`, `/sources`, `/scan`, and
  `/scanstatus`. Greenhouse was enabled and its public API returned HTTP 200,
  with zero matching roles. This is expected for the current configuration:
  Career-first has no target markets, and Relocation-first searches broad
  non-technical roles.
- [x] Owner completed `/targets career GE,AM`, `/sources`, `/scan`, and
  `/scanstatus`. Greenhouse returned one Lineate Infrastructure Engineer for
  GE (67/100) and one new notification; EURES returned 16. The separate
  Relocation-first Job Bank request failed with `ConnectTimeout`; all other
  sources completed. The bot showed work mode as unknown.
- [x] Inspect the Lineate notification through `/jobs` and `/job 1091`. Salary,
  work mode and unsupported visa/relocation facts remain unknown. The official
  posting is for a Georgian office and requires 3+ years Linux administration,
  2+ years production AWS, and 24/7 shift participation; see
  https://job-boards.greenhouse.io/lineate/jobs/8018252. The owner found its
  description displayed as escaped HTML entities.
- [x] Safely deploy the HTML-entity decoding fix. Compose source/runtime is
  3.5.7, PostgreSQL remained healthy, and startup `scan_all` completed at
  14:40:12 UTC. EURES search/detail calls returned HTTP 200 without SSL errors.
- [x] Owner reopened `/job 1091`: the Greenhouse description is now readable;
  salary, work mode, visa/work authorization and relocation assistance remain
  unknown without explicit evidence.
- [x] Recognize English `Necessary`, `Required`, `Minimum`, and `Essential
  Qualifications` headings so their technical signals count as required rather
  than falling back to an unqualified role score. Cover the technical score
  and interview-risk breakdown with regressions.
- [x] Full isolated PostgreSQL suite after the scoring fix: 246 passed,
  68.29% branch coverage; compile and diff checks passed. Push CI `38149543660`
  and PR CI `38149546515` passed for commit `7a6901d`.
- [x] Apply `7a6901d` through the safe updater. Source/runtime 3.5.7, app
  polling and PostgreSQL healthy. Startup scan completed at 15:04:57 UTC;
  inspected logs show the expected HH public fallback and HTTP 200 responses
  from the active sources, with no source error.
- [x] Extract `Minimum N years` / `At least N years` and add Windows and
  Databricks to technical evidence matching; regression coverage includes the
  Lineate-style requirements and experience comparison. Full PostgreSQL suite:
  247 passed, 68.36%; compile and diff checks passed.
- [x] Push CI `38150088881` and PR CI `38150092577` passed on code commit
  `678ddfc`; docs commit `664c559` also passed push/PR CI `38150288518` and
  `38150292566`.
- [x] Apply the candidate through the safe updater. Source/runtime 3.5.7 and
  PostgreSQL healthy. Startup scan completed at 15:15:48 UTC; inspected logs
  show no source error, SSL failure, timeout or traceback.
- [x] Owner reopened `/job 1091` and reported Technical 100 and interview risk
  `н/д` despite “Minimum 3 years.” Inspection found the saved posting's singular
  `Necessary Qualification` heading, which the parser did not recognize.
- [x] Recognize singular and plural necessary/required/minimum/essential
  qualification headings. Regressions cover the real singular Greenhouse form,
  Technical Score v2, and Recommendation v2 interview risk. Full isolated
  PostgreSQL suite: 248 passed, 68.36% branch coverage; compile and diff checks
  passed.
- [x] Push code commit `e978d07`; push CI `38151153964` and PR CI `38151157085`
  passed. Deploy through the safe updater; Compose source/runtime 3.5.7 and
  PostgreSQL healthy. Startup scan completed at 15:28:27 UTC with no source
  errors, SSL errors, timeouts, or tracebacks in the inspected logs.
- [x] Owner reopened `/job 1091` after the singular-heading fix and reported
  Technical 42 but interview risk `н/д`. The detail route supplies decoded
  text to Technical Score while Recommendation v2 independently rescored the
  stored HTML; this isolated the remaining mismatch.
- [x] Pass the same normalized vacancy text into Recommendation v2 and add a
  regression for the encoded Lineate HTML. It verifies Technical 42 and an
  interview-risk score of 58 rather than `н/д`.
- [x] Full isolated PostgreSQL suite: 248 passed, 68.36% branch coverage;
  compileall and `git diff --check` passed. Commit `8a583c7` passed push CI
  `38151840822` and PR CI `38151843490`.
- [x] Deploy `8a583c7` with the safe updater. Compose source/runtime 3.5.7 and
  PostgreSQL healthy. Startup scan completed at 15:38:13 UTC; the five-minute
  log check found no source errors, SSL failures, timeouts, or tracebacks.
- [x] Owner reopened `/job 1091` in Telegram at 18:42 Moscow time and confirmed
  Technical 42 plus interview risk 58 with explicit required-skill coverage
  and `fit=good`. This score is a matching-gap indicator, not a calibrated
  probability.
- [x] Add one bounded retry for Job Bank `httpx.TransportError` only, preserve
  the existing five-second delay before each request and shared crawl lock, and
  leave HTTP status errors unretried. Regression tests cover recovery,
  exhaustion, status handling and pacing; full isolated PostgreSQL suite:
  244 passed, 68.26% branch coverage.
- [x] Push commit `36c425b`; push CI `38148615302` and PR CI `38148617896`
  passed Python checks, Docker build and secret scan.
- [x] Safely update Compose project `repo`; source/runtime is 3.5.7,
  PostgreSQL is healthy, and startup `scan_all` completed at 14:51:38 UTC.
  Job Bank search and 12 detail requests and EURES search/detail requests
  returned HTTP 200; no Job Bank, EURES or scan error appeared in the inspected
  logs. No runtime transport failure occurred, so retry recovery is verified by
  regressions, not by injecting a live failure.
- [ ] For the time-sensitive relocation search, verify each useful opening's
  active/closing status, application deadline, expected start timing, and work
  eligibility from public evidence; leave missing details unknown.

## Follow-up — salary floor semantics
- [ ] Decide whether `/salary minimum` should be a hard exclusion or a scoring
  reference. Current implementation uses it as a scoring input, but Telegram
  says “minimum for filter.” The owner's `/job 580` showed 90,000 RUB in the
  description with structured salary unknown, so the existing scorer cannot
  exclude it. Fix wording and/or behavior with tests before claiming a strict
  floor.

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
- [x] Owner opened `/job 580` and confirmed the Recommendation v2 components
  render; unavailable signals were shown as `н/д`.

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
- [x] Owner uploaded a TXT test resume; the confirmation flow saved it as #6
  with zero facts added. Unsupported ZIP was rejected and prior imports were
  detected as duplicates; acceptance is recorded in the latest handoff entry.

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
- [x] Consolidate v3.5.2 source milestones into cumulative release v3.5.6;
  do not publish a retroactive v3.5.2 tag.

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
- [x] Complete real-chat acceptance for the latest Telegram controls and
  source dashboard; include the untagged v3.5.2–v3.5.5 milestones in cumulative
  release v3.5.6 without retroactive tags.

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
