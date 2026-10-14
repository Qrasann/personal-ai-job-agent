# Current State

## 2026-10-15 — source publication-date field coverage

Source summaries report nonempty publication-date-field coverage as a
provided/total count. Missing fields remain visible in the denominator. This
does not parse validity, measure age or change filtering. Focused tests: 55;
full isolated PostgreSQL: 912 passed.

## 2026-10-15 — display explicit salary period evidence

Vacancy salary display now shows explicit nearby periods such as monthly,
weekly, hourly or annual. Structured period fields take precedence. Missing or
ambiguous periods stay unknown, and filtering/scoring are unchanged. Focused
suite: 82 passed; isolated PostgreSQL suite: 910 passed.

## 2026-10-15 — application export audit trail

Application text exports now include the recorded status timeline. The handler
retrieves events through the same user-scoped repository function as the
history command; tests verify export content and ownership lookup. Focused
suite: 35 passed; full isolated PostgreSQL: 905 passed.

## 2026-10-15 — recruiter draft failure fallback

If recruiter-reply generation fails, the HH inbox scan stores an empty draft
and alerts the owner to reply manually. If explicitly enabled auto-reply fails
to send, the owner gets the grounded draft and a manual-fallback notice. Error
payloads are not logged; auto-reply defaults OFF. Focused suite: 9 passed; full
isolated PostgreSQL suite: 905 passed.

## 2026-10-15 — legacy application migration verification

Isolated PostgreSQL now verifies v5/v6 upgrades starting from v4 with a
preexisting application row. Migration adds snapshot columns and seeds one
history event from the recorded status/creation time; it does not fabricate
earlier transitions. Full isolated PostgreSQL suite: 903 passed.

## 2026-10-15 — disclose unknown salary-period behavior

`/salary`, its strict on/off response and `/settings` now state that a missing
or unsupported period is not compared and remains visible. Focused command and
filter tests: 41 passed; full isolated PostgreSQL suite: 902 passed.

## 2026-10-15 — strict salary filter requires a known period

An OFF-by-default strict floor now leaves structured salary values with no
recognized period eligible for review instead of assuming monthly. Explicit
monthly/yearly periods still compare against the monthly profile minimum.
Focused salary/scoring suite: 66 passed; full isolated PostgreSQL: 902 passed.

## 2026-10-15 — Interview Agent DNS/TLS/security coverage

Candidate Fact comparison now recognizes DNS, TLS and explicit Security
Operations terms; the interview planner has corresponding exercises for
resolver/cache diagnosis, certificate chain/SNI checks and safe incident
response/evidence preservation. Focused tests: 52 passed; isolated PostgreSQL
full suite: 901 passed. Broader security vocabulary is intentionally not inferred.

## 2026-10-15 — Interview Agent troubleshooting practice

`/interview <vacancy_id> [career|relocation]` returns up to five deterministic
troubleshooting exercises for recognized vacancy skills, ordered required then
preferred and labeled with the candidate's stored Candidate Fact type. Curated
topics include Linux, Docker, Kubernetes, Nginx, Networking, PostgreSQL, CI/CD
and Prometheus. No API/model call, answer grading or interview prediction.
Focused tests: 29 passed; isolated PostgreSQL full suite: 900 passed.

## 2026-10-15 — resume snapshot and explicit package export

Schema v6 adds local resume-text snapshot and optional external HH resume ID to
Application. Prepared and HH application records retain the selected local
text and the external ID used for HH. `/application <id> export` sends the
snapshot, saved cover letter and vacancy metadata only after user-scoped lookup
and explicit command. Legacy rows without a snapshot are labeled accurately.
Focused migration/export suite: 44 passed; full isolated PostgreSQL: 896 passed.
This is extracted text, not an original-format PDF/DOCX export.

## 2026-10-15 — append-only application status history

Schema v5 adds `application_status_events`. Saving a prepared draft and each
actual manual status change append a timestamped event. `/application <id>
history` checks ownership before listing the timeline; no-op status repeats do
not create an event. PostgreSQL integration covers migration, chronology,
ownership and repeated updates. Full isolated suite: 892 passed; focused set: 40
passed.

## 2026-10-15 — persisted draft versions and manual application status

Selecting “Prepare response” stores the cover-letter text, resume ID, source
URL, timestamp and `prepared` status as a new row in the existing applications
table. `/applications` lists the user's records and `/application <id> <status>`
sets only an allowlisted manual status after user-scoped ownership lookup. A
prepared or submitted status does not trigger any external action. PostgreSQL
integration covers snapshot persistence, owner isolation and status changes;
full isolated suite: 890 passed. No schema migration was required.

## 2026-10-15 — reviewed application package preview

Existing `/prepare` now includes the selected saved resume, grounded draft
cover letter, recognized vacancy skill comparison against Candidate Facts/CV,
and an HTTP(S)-only vacancy link. It highlights unconfirmed CV-only terms and
requirements unsupported by either source. Output is bounded and explicitly a
manual preview; it does not submit or save application status. Focused tests:
28 passed; isolated PostgreSQL: 888 passed. Export, exact sent version and
application tracking remain open.

## 2026-10-15 — read-only vacancy-to-resume diff

`/resumediff <vacancy_id> [resume_id]` compares recognized requirements with
the selected saved resume and active Candidate Facts. It identifies CV/fact
overlap and gaps in either direction without generating or changing CV text.
Resume selection is restricted to the authorized match profile. Also fixed
undefined diagnostic handling in `/job`, `/compare` and the compare callback.
Focused suites: 47 passed; isolated PostgreSQL full suite: 884 passed. Manual
Telegram acceptance remains open.

## 2026-10-15 — Candidate Fact traceability in vacancy comparison

`/compare` now shows the ID and provenance of the strongest Candidate Fact
behind each matched skill, plus existing `/facts` and `/fact` correction paths.
Provenance text is HTML-escaped; unmatched/missing skills are not given a
fabricated fact reference. Scoring is unchanged. Focused comparison tests: 23
passed; isolated PostgreSQL full suite: 879 passed.

## 2026-10-15 — opt-in strict salary floor

Implemented locally: strict structured salary filtering is OFF by default and
only rejects comparable monthly/yearly values whose upper bound is below the
minimum. Missing salary and unsupported currency/period remain eligible.
/salary strict on|off applies to both active search tracks. Focused 52 and full
isolated PostgreSQL 873 passed; compileall, diff-check and secret scan passed.

## 2026-10-15 — line-wrapped alternative requirement

The v3.6 Candidate + Vacancy Fit parser now groups an explicit isolated
two-skill `or/или` choice when the connector wraps across adjacent lines.
Repeated skills remain independent; additional independent skills remain
separate. Focused 43 and full isolated PostgreSQL 869 passed. Nested and
general multi-line requirement groups remain partial.

## 2026-10-14 — v3.6 language and relocation evidence increment

IMPLEMENTED locally: explicit English CEFR extraction/comparison, user-managed
`/english`, truthful fresh-profile bootstrap, and separate vacancy-card mobility
evidence. Language evidence does not alter scores. General fluency wording and
ambiguous CEFR ranges stay unknown. Visa/relocation/work-permit statements and
existing authorization requirements remain distinct and do not establish the
candidate's legal eligibility. Intermediate isolated PostgreSQL suites passed
at 863 and 865; production runtime and existing profile data are unchanged.


## 2026-10-14 — current model routing and fit regression

Session records confirm Main `gpt-6-sol/medium` and one read-only Scout turn
`gpt-6-luna/low`; Deep was not used. Scout's Greenhouse redirect suspicion was
false because the installed HTTPX client does not follow redirects by default.
Scout used 83,803 total tokens (56,576 cached input); the inherited history
made this small delegation costly, so net limit savings are not established.
AGENTS now matches actual Main and requires isolated context for justified
narrow Scout work. No models were switched. Required alternatives followed by
another sentence on one line now remain grouped; focused 55 and full isolated
PostgreSQL 856 passed. A further boundary fix keeps preferred alternatives
separate when one skill is independently required; latest focused 56 and full
isolated PostgreSQL 857 passed. Local runtime and production DB unchanged.


## 2026-10-14 — isolated database and v3.6 alternative choice

The separate `job-agent-tests` tmpfs PostgreSQL suite passed: 851 baseline,
then 855 with four new regressions. An explicit isolated required or preferred
`or/или` pair is now one scoring choice; Candidate Fact statuses remain visible.
Complex clauses still need a richer requirement model. Compileall, diff and
secret scan passed. Git HEAD and local production runtime are unchanged.
Local Codex CLI 0.162.1 config defaults Main to `gpt-6-sol/medium`;
`job_scout` is `gpt-6-luna/low`, `job_deep_review` is `gpt-6.1-sol/high`.
No active-session model switch or measured token/quota saving was verified.


## 2026-10-14 — verified local fit follow-up

The continuing workflow is recorded in `AGENTS.md`. Candidate + Vacancy Fit
remains PARTIAL: explicit adjacent headings in flattened vacancy text now keep
preferred skills optional, and a clearly qualified Devexperts language example
remains unknown instead of an individual Python must-have. These corrections
preserve the existing 85/15 structured score and do not change the 65-point
search threshold. General alternative groups are still PLANNED. Full local
suite 847 passed / 4 skipped; compileall, diff and secret scan passed. The
isolated PostgreSQL suite and authorized runtime acceptance have not run;
Git HEAD and deployed runtime are unchanged.

## 2026-10-14 — verified local observability/reliability checkpoint

IMPLEMENTED locally: uniform multi-profile source ledger; typed Russian safe
network/HTTP/schema/internal diagnostics; bounded, singly escaped HTML scan
views; per-pass issue grouping; persisted latest scheduled dashboard isolated
from manual state. Known HH outage cooldown remains quiet in notifications,
with diagnostics in the dashboard; certificate verification failures are
reported. Fallback history cannot hide a later connection failure.
Eight additional adapters mark explicit contract violations as response errors;
Arbeitnow/RemoteOK reject missing expected list shape. Himalayas and selected
ATS partial collection is visible, including source-budget expiry. Job Bank
retains verified detail results after HTTP/schema failures and stops 403/429;
existing pacing/cache limits remain. Real retries counted for HH, EURES,
Job Bank, Arbeitnow, SmartRecruiters; cache hits add no new retry count.
Source cache retains diagnostics/partial observations; processing failures have
independent attempt IDs. EURES reused collection failures are counted once.
Lightweight secret guard checks staged, worktree and history; synthetic tests
verify values never print. Progress exceptions and old failed scan stages are
sanitized. No actual credential exposure is asserted.
844 unit passed/4skipped; targeted 125, adapter-contract 152, telemetry 109/54 and
secret-guard 5 passed. compileall/diff/secret checks passed. PostgreSQL and live
Telegram/network acceptance remain BLOCKED; runtime/VERSION/Git HEAD unchanged.
Broader Relocation-first product utility and Candidate Fact DB acceptance remain
PARTIAL; scoring thresholds and eligibility/salary evidence were not changed.

HH failed connection probes and unattempted cooldown skips have distinct
failed/skipped counters; three regressions reproduced the prior miscount.

## 2026-10-14 — latest local candidate

Candidate Fact ADD/UPDATE/KEEP and safe network-cause diagnostics are locally
implemented. Final unit suite: 785 passed / 4 skipped; compileall/diff/history
secret checks passed. New PostgreSQL UPDATE/rollback/isolation paths remain
unverified because sandbox socket access is denied. HEAD is still d7a68d8,
53 ahead; .git remains read-only and nothing is staged. No runtime update.

## 2026-10-14 — Candidate Fact conflict review candidate

Per-overlap ADD/UPDATE/KEEP UI and deterministic import planner are implemented
locally. UPDATE retains the prior row inactive and creates an unknown fact with
replacement provenance; stale or foreign target rows are rejected. No migration.
769 unit/behavior tests passed, 4 skipped. New PostgreSQL regression paths were
not executed because socket creation is sandbox-denied. Checkpoint remains
uncommitted at d7a68d8 (53 ahead); git dry-run confirms .git is read-only.

## 2026-10-14 — final local verification

HEAD remains d7a68d8, branch feature/v3.5.7-international-market-coverage, 53 ahead.
Own pending atomic-import, EURES metrics and HH manual-owner changes remain
uncommitted because `.git/index.lock` cannot be created (read-only filesystem).
Source counters now preserve earlier processing errors and deduplicate actual
EURES discovery observations. Final unit suite: 750 passed / 4 skipped;
compileall/diff/history-secret checks pass. Isolated DB socket access is denied.

## 2026-10-14 — checked local candidate

Resume lookup failures now preserve the retry preview. Manual HH reply setup
requires the owner and stale non-owner pending state is cancelled. Unit suite:
748 passed / 4 skipped. Isolated DB revalidation is environment-blocked before
connection; no production inspection or change occurred in this stage.

## 2026-10-14 — EURES partial-failure visibility

EURES now counts query/detail HTTP, transport and parse failures when preserving
other results. Counts survive the discovery cache and profile aggregation and
appear in manual scan completion and `/scanstatus`. Tests confirm cached results
do not double-count failures across Career-first and Relocation-first profiles.
No scoring or source retry policy changed.

## 2026-10-14 — atomic resume import persistence

Imported resume content and selected proposed Candidate Facts now share one
PostgreSQL transaction. A failed transaction rolls back both; the one-time
preview token is restored for retry. Unit handler tests and isolated PostgreSQL
rollback/retry integration checks pass. No production data was accessed.
Per-conflict ADD/UPDATE/KEEP review remains open.

## 2026-10-14 — network log hygiene

Telegram startup retry and HH chat polling no longer print exception payloads
to application logs. They retain error classes for diagnosis; retry and
authorization behavior is unchanged.

## 2026-10-14 — dependency floors

`requirements.txt` now requires pypdf >=6.20.1 and python-multipart >=0.0.31.
The local test venv has the patched pypdf 6.20.1; production image was not
rebuilt. Broad dependency ranges remain a supply-chain reproducibility issue.

## 2026-10-14 — EURES partial responses

The adapter now preserves verified results after a single search/detail HTTP
error or malformed response and logs the failure class/status. Total search
or detail failure remains visible as a source error. No live endpoint probe or
runtime update was made for this change.

## 2026-10-14 — Job Bank performance candidate

Adjacent runtime scans requested the same twelve Job Bank detail IDs, with
roughly 55 seconds between first and last detail response due to permitted
five-second pacing. Local branch now keeps a one-hour, 256-entry in-memory
detail cache, only for IDs still present in a fresh listing. Explicit manual
refresh bypasses it. No post-change runtime timing is available until an
authorized update; the cache resets on restart.

## 2026-10-14 — Georgia detail URL boundary

HR.ge and JOBS.GE detail fetches now require HTTPS on the source's own host,
without alternate ports or URL credentials. Listing HTML cannot redirect the
adapter's direct detail request to another host. Live source behavior still
requires authorized runtime verification; JOBS.GE remains paused.

## 2026-10-14 — resume import callback replay

Import preview tokens are now one-time claims before resume persistence operations.
Concurrent duplicate callbacks cannot both write the resume. A transient
failure after the claim requires a new preview; transaction-level recovery of
partially written resume/facts is not yet implemented.

## 2026-10-14 — reliability and security follow-up

Local branch now isolates scheduled scans by user. Telegram user routes require
private chats; Bot API channel-post ingestion remains enabled for the selected
watcher. A global HH applicant token is restricted to the configured owner
profile at the service boundary. Transport exception messages and HH API error
bodies are no longer exposed in source alerts. Per-vacancy processing failures
now preserve later results and mark the source partial. These changes have local tests;
production runtime and external service behavior have not been revalidated.

## Night development checkpoint — 2026-10-14

Root roadmap reconciled with implementation and complete original product
intent; proposed v3.5.8/v3.5.9 numbering does not change active 3.5.7 source.
Watcher handles a failed pause/profile/retry-state lookup for one subscriber
without blocking later users (four regression cases).
Real channel access and deployment acceptance remain pending. Source and
runtime status recorded in older sections below is historical unless checked
again; see latest `HANDOFF.md` and `DEVELOPMENT_LOG.md`.

## Verified watcher checkpoint — cb1ba4a

All three watcher stages committed: a6d67fa,3dffc39,cb1ba4a. Full716 unit/4
skipped,720PostgreSQL; compileall/secret/diff passed. Separate Docker image
89380b6088b3 built and Python3.12 watcher import/compile/parser/scheduler smoke
passed without networking. No production/update/publication performed.
Actual next gate: select channels and establish Bot API access, then separately
approve runtime deployment and validate /channels, incoming post/replay/retry
and both profile results. Edited/history collection remains unimplemented.
Two new untracked owner proposal files appeared during work; preserved, not
committed/applied. Their headers explicitly label proposed roadmap numbering;
no VERSION or current task change inferred from embedded instructions. Next
documentation review should reconcile proposals against current720 tests,
not their historical429-test snapshot. No implementation edits remain.

## 2026-10-14 — Telegram watcher persistent retries

Failed deliveries persist in RuntimeState queue (max100 per user); retry job
every minute handles max5 posts, /channels retry scoped to invoking user. Off,
paused and source-disabled users stay protected. Existing queued entries never
evicted for overflow; overflow separately counted. Success/seen replay clears
queue; failures rotate; malformed entries preserved/logged. Real PostgreSQL
integration now verifies queue recovery after reload, real dual-profile matching
and replay suppression. Latest716unit/4skipped,720PostgreSQL; safety checks pass.
Stage1 a6d67fa and stage2 3dffc39 complete; current stage local/undeployed.
No schema/score change. Next separate Docker check then owner-approved runtime
and real selected-channel acceptance; edits/history are not claimed.

## Telegram watcher stage 2 — 2026-10-14

Labeled role/company/location/work-mode fields now parse conservatively; generic
headers/hashtags no longer hide the role. Narrative office mentions do not assign
country; ambiguous multi-country and Georgia/USA locations stay unknown.
Forwarded channel posts/captions preserve original public URL and numeric source
identity, sharing a serialized durable replay guard with automatic delivery.
Private/hidden forwards get no invented public link. No schema/score change.
Targeted51/1skipped; full unit710/4skipped, PostgreSQL714; safety checks passed.
Stage1 a6d67fa complete; next bounded persistent failed-post retry queue.
Production unchanged; Bot API access/history limitations still apply.

## Telegram watcher stage 1 — 2026-10-14

Implemented /channels subscriptions (add/on/off/remove, career/relocation/both),
Bot API post/caption routing for selected users only, persistent statistics and
SeenMessage replay suppression. Both profiles use existing scoring/persistence;
pause/source-disable respected. Alias subscriptions union scopes. No migration,
production change, account login/history scraping or external application.
Unit698/4skipped, PostgreSQL702; watcher targeted23 including real PostgreSQL
reload and dual-profile matches. Compileall/secret/diff passed. Help entry added;
see developer/TELEGRAM_WATCH for access/transaction/retry limitations.
Next safe stage: labeled role/company/location parsing and forwarded-channel
provenance; then edited-post/retry handling. Deployment approval remains separate.

Verified implementation06fe88c; separate Docker imagea80ee8bdf948 built,
Python3.12 compile/import/evidence smoke passed without networking. Latest676
unit/679PostgreSQL and safety checks passed. Owner deployment approval requested
for06fe88c, answer pending. Earlier11c07cc request is superseded; no runtime
update or publication performed. Actual following HEAD is docs-only.

## 2026-10-14 — Direct employer visa predicates

Shared evidence now handles employer sponsor-visa verb phrases, including
plural, can/will and explicit refusal. Conditional/advice/non-employer claims
remain unknown. Refusal wins over offers in either order, also in Telegram.
84 targeted tests; full unit676/3 skipped, PostgreSQL679; compileall/secret/diff
passed. No formulas, thresholds, migration or deployment. Prior stage02635d7
complete. Compact BRIEF/HANDOFF now replaces duplicate current snapshots;
original text remains Git history/DEVELOPMENT_LOG. Next mandatory gate: approved
runtime/Telegram acceptance; independent AM feed discovery stays open.


## Latest stage — 2026-10-14: Greenhouse evidence

Greenhouse uses shared tri-state support classification, so advice, conditional
support and prerequisites no longer become employer sponsorship offers.
Existing source snippets are retained only when consistent with the classified
value. Hybrid wins over mixed hybrid/remote labels; explicit remote locations
are preserved as bounded remote_scope. No new filters, weights or thresholds.
Validated 665 unit / 3 skipped, PostgreSQL 668, compileall/secret/diff passed.
Local implementation follows e4644b3; no deployment/publication. Next safe task:
shared explicit sponsor-visa verb phrases and refusal precedence. Mandatory
v3.5.7 runtime/Telegram acceptance remains pending; see HANDOFF.


Candidate 11c07cc also passed a separate Docker build (image8fc8cddae7d6)
and Python3.12 import/compile/evidence smoke in a network-disabled ephemeral
container. Repo runtime/volumes unchanged. Owner update approval requested for
11c07cc; unanswered at this checkpoint. Any following checkpoint is docs-only.

## Current checkpoint — 2026-10-14

Source 3.5.7, feature/v3.5.7-international-market-coverage. Previous six stages
remain complete. New stages: af1ff56 (source salary display and remote limit
precedence), 76b5661 (Telegram unknown/negative support and explicit salary
units), then malformed numeric salary bounds (obtain final HEAD from Git).
Latest complete candidate: 658 unit passed / 3 skipped, isolated PostgreSQL
661 passed; compileall, secret scan and git diff --check passed.
No scoring formula/weight/65-threshold changes or schema migrations.

See BRIEF/HANDOFF for implementation limits and pending deployment/acceptance.
Next: approved runtime validation; independent Armenian employer-feed research
remains open. Historical counts below belong to their recorded stages.
