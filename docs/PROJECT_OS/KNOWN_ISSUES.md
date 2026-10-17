# Known Issues

## 2026-10-17 — Telegram folder live access and yield unverified

The supplied 21-chat manifest has no numeric IDs, usernames, types or access proof. The optional user client has no local API credentials or authorized session in this development environment, so no real channel was read or joined. Folder preview alone does not prove joined access. Current intake is new-post only; downtime may miss posts, and edited posts are not replayed. The explicit non-vacancy filter is conservative; possible-vacancy counts are parser candidates, not verified job offers. Good/Stretch are profile assessments. Live 2–3-channel acceptance, false-positive review and rate-limit observation remain open.

## 2026-10-14 — remaining language and eligibility limits

Language fit recognizes only an explicit CEFR token near English/«английский».
It intentionally does not map “fluent”, “upper-intermediate”, interview ability,
or an ambiguous B1–B2 range. The stored profile level is self-reported and can
be cleared with `/english unknown`; it is not a certification claim. Mobility
lines report vacancy wording only. Absence of an explicit existing-authorization
requirement does not prove eligibility, and employer support does not determine
the candidate's legal route. Neither increment changes match scores.


## 2026-10-14 — additional local reliability/security fixes

Confirmed: Job Bank second-detail HTTP/schema errors previously discarded
already verified first-detail jobs. Two regressions reproduced both branches;
results now survive,403/429 stops further source calls. No retry expansion.
Confirmed: a dense 13-source HTML fixture produced 5940 characters before other
scan text, exceeding Telegram limits. Source section now caps at 2600 escaped
characters; full attempts remain in state and issue notices are separate.
Confirmed guard gap (Medium): secret scan checked only committed history and
missed new/staged content. It now checks index/worktree/history, including an
index secret hidden by a clean working copy. The pattern guard is lightweight,
not a comprehensive secret detector; no actual leaked credential is claimed.
Progress callback exception payloads and legacy failed-stage strings could
expose sensitive text in logs/status (Medium); synthetic regressions verify
safe class/code output. Certificate errors are not hidden by HH cooldown.
No production update; PostgreSQL and live source/Telegram acceptance remain
unverified. Partial collection metadata is local telemetry, not proof of hiring
eligibility, visa support or sufficient Relocation-first Good/Stretch coverage.


HH attempted connection failure versus unattempted cooldown skip was previously
miscounted; corrected locally with three reproduced count/status regressions.

## 2026-10-14 — production source alerts and remaining evidence

The historical aggregator is confirmed defective: error-only source state
followed by success raises KeyError('found'); success→error loses the error.
Both are reproduced and fixed locally by an attempt ledger. Production events
on Oct13/14 are consistent with this defect, but their actual trace was NOT
retrieved: read-only production-log query was blocked by Docker API permission.
Do not attribute those events to HH/RemoteOK availability without traceback.
RemoteOK ConnectTimeout confirms a connection deadline, not DNS, IP family,
TLS/proxy or blocking. All underlying causes remain externally unverified.
No live probe/retry-policy expansion or deployment was performed.
Latest scheduled summaries now persist independently of manual state. This is
a last-scan ledger, not unlimited historical retention or distributed tracing.


## 2026-10-14 — raw TLS/DNS messages (fixed locally)

Medium: source summaries/logs could expose raw SSL/DNS error payloads. Synthetic
URL-token regressions reproduced this; no actual credential exposure is claimed.
They now emit class/category only. Typed cause classification is bounded and
cycle-safe and does not guess from text. Live HH DNS/TLS/proxy/IP-family/source
blocking attribution remains open; unchanged retries/cooldown isolate failures.

## 2026-10-14 — Candidate Fact review acceptance boundary

Per-import conflict controls are implemented and unit-tested. Transactional
UPDATE/rollback/cross-profile integration assertions are prepared but require
isolated PostgreSQL access outside this sandbox. No runtime acceptance is claimed.
Review applies to new imports; already-imported fingerprints remain deduplicated.
Static source review found no listing-controlled detail URL fetch in EURES,
Himalayas or SmartRecruiters. EURES follows fixed-host API redirects; no
listing-controlled exploit was established, so no bypass/rewrite was added.

## 2026-10-14 — counter fixes and environment blockers

Fixed locally: a later successful search profile replaced earlier source
processing-error counts; distinct cached EURES queries also lost failures when
aggregation used max instead of per-discovery observations. Regressions cover
both defects and reuse of the same cached discovery. Git checkpoint is blocked
by read-only `.git`, DB revalidation by denied Docker/localhost sockets. Neither
blocker was worked around; no production or external source request occurred.

## 2026-10-14 — manual HH state and verification boundary

Fixed locally: non-owners could create pending manual HH routing state even
though sending was owner-gated. Setup is now owner-only and stale non-owner
state is cleared. No unauthorized send was reproduced; authorization/state
regressions use a mocked HH client. Import previews also survive lookup errors.
Current sandbox denies Docker and localhost sockets; this is a DB-test blocker,
not evidence of a PostgreSQL or application regression.

## 2026-10-14 — EURES partial failure counts (fixed locally)

The adapter preserved vacancies after individual search/detail failures but
reported only a generic partial label. It now carries the number of failed
requests through cached discovery and both search-profile summaries; `/scan`
and `/scanstatus` display the count. Total failure remains a source error.
Live/runtime acceptance remains pending deployment authorization.

## 2026-10-14 — resume import transaction (fixed locally)

Resume import previously committed the resume and each proposed Candidate Fact
separately, so a database error could leave a partial import. They now persist
in one transaction; a failed save leaves no partial rows and restores the
preview token for retry. Isolated PostgreSQL regression covers rollback and
successful retry. Explicit per-fact ADD/UPDATE/KEEP conflict choices remain
unimplemented. Running production code has not been updated.

## 2026-10-14 — network log hygiene

Fixed locally: Telegram startup and HH chat poll warnings logged raw exception
text, which could include URL parameters. They now record exception class only.
The running image is unchanged until separately authorized deployment.

## 2026-10-14 — dependency advisory review

Local pypdf 6.20.0 was below the upstream 6.20.1 fix for a possible infinite
loop in tree-item removal; our resume path reads/extracts text, so direct
reachability of that specific operation is unproven. `requirements.txt` now
requires the fixed floor and the test venv uses 6.20.1. The previous
python-multipart floor allowed versions affected by published parser DoS
advisories; it now requires >=0.0.31, with local 0.0.32 already present.
The running image remains unchanged and broad version ranges lack a lock.

## 2026-10-14 — EURES response isolation

Fixed locally: one EURES HTTP error or malformed search/detail response aborted
the entire source and could discard verified jobs from other queries/details.
The adapter now isolates those failures and still reports all-failed scans.
Partial failure counts appear in logs, not yet in `/scanstatus`.

## 2026-10-14 — Job Bank repeat details

Read-only runtime logs at 22:21 and 22:36 UTC showed the same twelve detail
IDs requested again; the latter detail span was about 55 seconds. A local
one-hour bounded cache now avoids that repeat work for scheduled scans while
retaining fresh listings and forced manual detail fetches. Actual runtime
improvement is unverified because no deployment occurred. Official pacing
remains five seconds between request starts.

## 2026-10-14 — Georgia detail URL review

Fixed locally: HR.ge and JOBS.GE accepted an absolute detail URL from listing
HTML and could request another host, including loopback. Same-host HTTPS URL
validation now blocks this SSRF path. Redirects are not followed by these
clients. Live acceptance remains pending; JOBS.GE is still paused.

## 2026-10-14 — resume import callback boundary

Concurrent duplicate confirmation callbacks previously could save the same
resume and facts twice. The token is now claimed before the first DB await.
If saving fails partway through, the preview is consumed and the user must
resend the document; an atomic resume-plus-facts transaction is still open.

## 2026-10-14 — security and reliability audit notes

- Fixed locally: a scheduled `scan_all` exception for one user aborted later
  users; Telegram user routes accepted group chat updates when bound to a chat
  ID; global HH applicant actions lacked owner-profile enforcement; source
  transport errors and HH API error bodies could expose untrusted response or
  URL text; one malformed vacancy aborted later results in its source. Each has
  a reproducing regression test.
- HH ConnectError remains an upstream/environment-dependent condition. The
  current app skips HH for a bounded cooldown and continues other sources;
  there is no evidence yet to attribute a live failure to DNS, TLS, proxy or
  HH itself. No bypass or retry loop was added.
- A complete production security review still needs a separately authorized
  runtime check. Local review covered Telegram routing, HH applicant boundary,
  source errors, watcher flow, Docker/CI configuration and relevant tests; it
  did not audit production credentials or run active external probes.

## Current gates — 2026-10-14

- Channel Watcher code is locally tested, but no actual selected-channel Bot
  API access or runtime acceptance is recorded. A pause/profile lookup failure
  skips that subscriber, leaving the event unseen and outside the retry queue
  because its scope cannot be verified. Bot API redelivery is not guaranteed.
- Edited posts, history backfill, cross-process exactly-once delivery and
  per-profile historical rescore remain unimplemented. They are not implied by
  a configured `/channels` entry.
- Relocation-first usefulness and eligibility remain open. Unknown country,
  visa, employer support, hiring scope or salary is not a confirmed refusal.
  A proposal document's 429-test snapshot is historical; use current tests.

Current-state correction (2026-10-13): HH selected-market discovery was
implemented in 61fe39d; older current-country-only notes below are historical.
HH ConnectError is a silent skip with cooldown; the pending local follow-up
corrects summary rendering and cache/concurrency recovery. Salary wording now
says assessment minimum, not hard filtering. Current runtime/remaining work is
in BRIEF.md; old deployed/uncommitted claims below are historical checkpoints.

## Current candidate follow-up — 2026-10-12
- Scoped `/jobs career|relocation [below]` now separates the two profile scores
  and thresholds. Cards and comparison callbacks preserve the selected profile.
  These commands still need owner Telegram acceptance. Legacy `/job <id>`
  chooses the latest profile match and now identifies that profile on the card;
  use a scoped command or the new list buttons for a specific direction.
- HH discovery currently uses `current_country` (`RU` → area 113), ignoring
  selected destination areas. Broader selected-market discovery remains open;
  do not relabel RU results as AM/GE.
- Owner-confirmed `/sources` and `/scan` show Remotive enabled, but the scan
  returned 0 jobs. A read-only probe found the cached API response held 18 jobs
  across unrelated categories. Live API checks for `category=devops`, `Devops`,
  and `software-development` all returned the same general feed. The official
  feed documentation links the category-specific RSS endpoint
  `https://remotive.com/remote-jobs/devops/feed`; the worktree now parses this
  feed and bumps the persisted cache key to v3. After rebuild, the endpoint
  returned HTTP 200 but only channel metadata and no `<item>` elements, so both
  profiles parsed 0. This is a valid empty feed response, not a parser or
  transport error. Recheck after the 24-hour cache expires and confirm `/jobs`
  attribution if the feed returns a matching listing.
- Remotive is a technical-role source and does not resolve the Relocation-first
  gap. Recent scans have returned 0 Good/Stretch for that profile under the
  existing 65-point threshold. `/jobs below` now shows nonzero matches
  under the threshold in descending score order for manual review; it does not
  turn them into Good/Stretch or notifications. Improve broad, legally reachable
  source coverage and relevance without lowering the threshold, inflating
  scores, changing explicit exclusions, or treating remote as worldwide
  eligibility.

## Resolved in the current development branch
- Ordinary `hotel staff` and `warehouse staff` were marked Senior by the broad
  `staff` title pattern. Only Staff qualifying technical titles now invokes
  that level; actual Senior/Lead/Principal, high experience, management and
  user exclusions remain restricted. Fifteen regressions cover these cases.
- Lineate's Greenhouse posting uses the singular `Necessary Qualification`
  heading. The parser previously recognized only the plural form, leaving the
  job on the fallback Technical score and interview risk `н/д`. Commit
  `e978d07` recognizes singular and plural qualification headings. A follow-up
  live card showed Technical 42 but interview risk still `н/д`, because
  Recommendation v2 used the stored encoded HTML while Technical used decoded
  text. Commit `8a583c7` shares the normalized vacancy description between both
  calculations and passed regression tests, CI, and deployment. The owner
  confirmed `/job 1091` in Telegram at 18:42 Moscow time: Technical 42 and
  interview risk 58, with explicit required-skill coverage and `fit=good`.
  The displayed risk score reflects the matching gap; it is not a calibrated
  probability of receiving an interview.
- Concurrent scheduled/manual scans could both observe a missing JobMatch and then race to insert the same `(job_id, profile_id, search_profile_id)`. `save_match` now uses an atomic PostgreSQL upsert and the fix passed a local scheduled/manual scan smoke test.
- Relocation discovery initially used `relocation_queries` while matching scored only career `queries`, filtering otherwise relevant broad-role results. Matching now uses the active strategy's discovery queries.
- Generic description text could be misread as a salary for non-HH sources. Notifications and details now use only structured salary values or explicit source salary/card text.

- EURES response bodies failed with a TLS record-layer error when the client
  negotiated compressed encoding. In a live container check, the default
  compressed request reproduced the failure, while `Accept-Encoding: identity`
  returned a full 50-result JSON response. The first complete post-update
  dual-profile scan returned EURES search and detail responses without SSL
  errors, and `scan_all` completed. The underlying network/server cause is not
  established; monitor later scheduled runs.

- work_permit, relocation_package and immigration_support are not separate Job columns yet; v3.5.2 infers them conservatively from vacancy text.
- Source/country priority affects processing order, not Recommendation Model v2 score yet.
- Both search profiles now give explicitly remote vacancies an extra
  processing priority. This affects order within each source's discovered
  batch; source processing still happens in source-priority order, and `/jobs`
  keeps its match-score ordering. `remote_scope` is often unknown, so this does
  not prove the employer permits work from the selected destination or any
  country.
- The Himalayas source in the uncommitted v3.5.7 candidate uses its public
  API with at most four role queries, three markets and one 20-result page per
  query/market. API rate limits are unspecified and provider data refreshes
  daily; the app caches for 24 hours. The owner accepted `/job 1273` in Telegram
  at 20:56 Moscow time: the card says the source marks the role worldwide while
  country-level hiring remains to be confirmed. Missing location
  restrictions remain unknown, while an empty list means worldwide according
  to the provider. Neither case
  establishes personal work authorization, payroll/tax availability, visa
  sponsorship or relocation support. RemoteOK also has unknown hiring-country
  scope even when its role is explicitly remote.
- The candidate now has a curated Collectly Lever source. Its active remote
  DevOps posting permits time zones through GMT+4 and the employer's hosted
  form states that onboarding takes place in Yerevan with travel/accommodation
  covered. The public posting lists Belgrade/RS; the adapter does not infer a
  country of hire, sponsorship, salary, or a relocation package from the
  temporary onboarding trip. The current worktree is rebuilt locally, and the
  owner confirmed `/sources` lists Lever for both profiles; a manual scan
  found one live Lever result in 9.6 seconds. The saved Collectly result is
  job #1333, filtered at score 0 because the Career-first profile excludes
  `senior devops`; this is expected profile behavior. The owner should decide
  before that explicit filter is changed. Lever's public-feed request limit
  and posting expiry are unspecified; the adapter is bounded to one page of
  100 and locally cached for six hours.
- The 2026-10-11 Telegram scan reported Relocation-first 74 processed and 0
  Good/Stretch. The profile's 65-point threshold leaves some lower-scoring
  remote and broad-role vacancies in `filtered`; an inspected remote match
  scored 54. This is a visibility/scoring limitation rather than a source
  outage. The owner confirmed that higher-rated vacancies must remain the
  priority. Keep lists sorted by score descending, retain the 65-point
  notification threshold, and do not promote lower-rated leads ahead of
  higher-scoring results. Continue improving evidence-based Relocation-first
  source coverage and relevance without inflating scores or changing owner
  exclusions.
- City priority exists in the preference engine but dedicated Telegram city-priority buttons are pending.
- Country picker is limited to data/countries.yaml.
- Only implemented adapters actually scan; future registered sources still need collectors.
- HH is primarily domestic and RemoteOK is tech-heavy. Arbeitnow adds Germany coverage but its current feed can legitimately contain no low-barrier role matches; additional legal-work/visa-capable country sources are still needed.
- Georgia adapters enter a profile's scan only when `GE` is selected. The owner
  confirmed a Relocation-first GE scan on 2026-10-11: EURES returned 16
  vacancies, HR.ge returned 2, JOBS.GE returned HTTP 410, and Arbeitnow had a
  transient `ReadTimeout`. JOBS.GE is paused in the source plan; HR.ge remains
  enabled while recurring reuse permission is unverified. The deployed
  follow-up adds one bounded retry for Arbeitnow transport failures. A later
  Telegram scan log confirmed a timeout recovered on retry with HTTP 200. The
  owner confirmed `/sources` displays JOBS.GE as paused and provided a completed
  `/scanstatus` report.
- On the v3.5.7 candidate, Armenia (`AM`) is selectable and Lineate's public
  Greenhouse board is connected for selected AM/GE markets. Its current
  DevOps/Infrastructure match is for a Georgian office; the Yerevan postings
  on that board are data-engineering roles and do not match current queries.
  The candidate is deployed to local Compose for owner acceptance, while
  `main` and the formal release remain v3.5.6. Its startup scan did not show a
  Greenhouse request; verify the effective market/source settings with
  `/sources` and a targeted Telegram `/scan`. The official e-work/workforall
  access contract remains unverified. Staff.am
  prohibits automated scraping without permission, and Job.am restricts
  unauthorized reuse and redistribution.
- The official Armenian `workpermit.am` portal describes employer-side
  foreign-hiring and work-residence processing, and states that EAEU citizens
  working in Armenia are exempt from work-permit documents. Its public UI has
  a job-finding FAQ, but the answer and anonymous job-discovery/feed access are
  unverified. Candidate nationality must not be inferred from profile country.
- Georgia's Labour Migration Law changes effective 2026-03-01 require covered
  foreign workers in local paid employment to obtain a right to work through
  the employer and follow the applicable immigration procedure. Search target
  `GE` does not establish individual work eligibility.
- `/salary minimum` currently affects scoring when a structured salary exists;
  it does not hard-filter. The Telegram text says “minimum for filter.” In the
  owner-provided `/job 580`, 90,000 RUB appeared in the description while
  structured salary stayed unknown, so the value was not used for scoring.
- Job Bank Canada adds international TFW coverage, but an LMIA request or
  permission to apply does not establish sponsorship or candidate eligibility.
  Initial coverage is one page, six queries and twelve details per profile.
  The candidate enforces a minimum five-second interval between request starts;
  for 18 fast requests, that interval can account for about 85 seconds before
  network time, while slow responses consume part or all of the interval.
  Decimal CAD/hour salaries are preserved as source text; structured salary
  normalization and display are pending. A Telegram update took 162.7 seconds
  with twelve Job Bank detail calls visible; `/scanstatus` measured Job Bank at
  99.5 seconds. The active v3.5.7 worktree now retains verified results and
  continues after an individual search/detail transport failure; it still
  reports a source error if all searches or all detail requests fail. HTTP
  status errors remain visible source failures. The pacing change is now
  applied to local Compose; compare live `/scanstatus` timing after the rebuild.
  Do not increase request volume or parallelize calls.
- Full CI is required before merge; live Telegram polling and dual-profile scan smoke tests passed on the local deployment.
