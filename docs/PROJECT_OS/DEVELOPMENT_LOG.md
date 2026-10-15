## 2026-10-15 — keep Arbeitnow remote location unconfirmed

Arbeitnow no longer assigns Germany as the work country or a city to every remote posting. Its free-form `location` is retained as `source_location`; Relocation Evidence keeps the work country unknown for a synthetic remote “Worldwide” fixture. Onsite source behavior is unchanged. Focused adapter/evidence/preferences tests: 63 passed; full isolated PostgreSQL: 993 passed.

## 2026-10-15 — recognize explicit “provide no housing” refusals

Relocation Evidence now treats “We provide no housing” and “We offer no accommodation” as explicit refusals. A regression showed these phrases were previously marked as provision because the positive verb rule matched across `no`. Focused evidence/detail tests: 50 passed; full isolated PostgreSQL: 992 passed.

## 2026-10-15 — distinguish housing denial from an information offer

Relocation Evidence now recognizes explicit employer verb-first refusals such as “We do not provide housing” and “We cannot offer accommodation”. It no longer reads “housing details are provided” as accommodation provision, and a refusal to provide housing details remains unknown. Synthetic regression reproduced the previous false offer. Focused evidence/detail tests: 50 passed; full isolated PostgreSQL: 992 passed.

## 2026-10-15 — preserve conflicting housing evidence

Relocation Evidence now marks contradictory explicit housing provision/refusal statements as `unknown` with `conflicting_text` confidence and both source excerpts. A single explicit provision or refusal keeps its prior classification. Synthetic regression reproduced the previous false refusal. Focused evidence/detail tests: 49 passed; full isolated PostgreSQL: 991 passed.

## 2026-10-15 — keep RemoteOK free-form location out of country claims

RemoteOK's free-form `location` is no longer persisted as normalized `country`: labels such as “Worldwide” or an office location do not establish the employee's work country or hiring eligibility. The original text is retained as `source_location`, so Relocation Evidence shows it as an excerpt while the country value remains unknown. Remote scope remains unspecified. Focused source/location tests: 54 passed; full isolated PostgreSQL: 990 passed.

## 2026-10-15 — keep preferred experience out of hard fit threshold

Candidate Fit now ignores explicitly preferred/desirable years when deriving the minimum required experience. When a required minimum is also stated, only required/unlabelled bands determine the threshold; a preferred-only band does not create a mandatory years-of-experience gap. Regression reproduced a 3-year minimum plus 5 years preferred being misread as 5. Focused fit/resume tests: 60 passed; full isolated PostgreSQL: 990 passed.

## 2026-10-15 — recognize Russian negotiable start timing

The source evidence excerpt matcher now includes “Выход на работу” so the existing conservative negotiable classifier can classify “Выход на работу по договорённости”. “Начать можно сразу” is also regression-covered as immediate. No candidate availability, scoring or legal eligibility is inferred. Full isolated PostgreSQL suite: 988 passed.

## 2026-10-15 — mobility evidence in package review

Prepared packages now show the existing visa/relocation/work-permit evidence
and prior-authorization requirement, with unknowns and personal-eligibility
limits preserved. Preview HTML is bounded to 3700 characters, keeps the mobility
block, and points to full CV review when details are omitted. Malformed,
credential-bearing and overlong URLs do not break previews or become truncated
links. Focused tests: 116; full isolated PostgreSQL: 948 passed.

## 2026-10-15 — source yield before preference filters

Per-source attempts now retain received-result and preference-exclusion counts.
The dashboard distinguishes an empty source from results removed by settings,
separately from scoring filters and processing errors. Counts cover adapter
results per profile/attempt (including cache reuse), not unique global jobs.
Focused source/preferences tests: 91; isolated PostgreSQL: 943 passed.

## 2026-10-15 — serialize manual application status changes

A deterministic isolated PostgreSQL regression reproduced duplicate status
events from simultaneous identical updates. A row lock now serializes the
status check and append for the owning application. Focused DB/handler tests:
32 passed; full isolated PostgreSQL: 941 passed. No schema migration.

## 2026-10-15 — immutable vacancy snapshot in Application Package

Schema v7 adds an additive vacancy snapshot: title, company, original stored
description and source vacancy URL. Prepared and HH packages capture it beside
the CV/letter; export no longer queries the mutable Job. Provider/application
URLs remain separate. Old rows disclose missing snapshots without backfilling
current data as historical fact. Focused package/migration tests: 64 passed;
full isolated PostgreSQL: 940 passed, including v4-to-v7 upgrade/idempotency
and export after later Job edits. Production schema remains untouched.

## 2026-10-15 — nonoverlapping Candidate Fit alternatives

Pure OR expressions such as `Linux or (Docker or Kubernetes)` now produce
one alternative group. Previously the inner group was counted twice, lowering
Linux-only coverage and showing a spurious missing group in resume review.
Three regressions failed before the fix. Focused fit/score/resume: 70 passed;
full isolated PostgreSQL: 936 passed.

## 2026-10-15 — normalize Arbeitnow epoch publication dates

Converted numeric Arbeitnow `created_at` values from Unix epoch seconds to
UTC ISO; rejected malformed values instead of displaying raw strings/numbers.
Focused source/detail tests: 46; isolated PostgreSQL suite: 933 passed.

## 2026-10-15 — clarify application status provenance in exports

Added an explicit local-tracker provenance sentence beside the exported
application status. It avoids treating an owner-maintained status as verified
employer/provider receipt. Focused package/handler tests: 40; isolated
PostgreSQL suite: 929 passed.

## 2026-10-15 — normalize Remotive publication timestamps

Normalize explicit timezone-aware RFC 2822 RSS dates and ISO API dates to UTC
ISO format before persistence/display. Malformed or timezone-less values remain
unknown. Focused Remotive tests: 8 passed; isolated PostgreSQL: 929 passed.

## 2026-10-15 — isolated parenthesized skill alternatives

Extended alternative parsing to a narrowly scoped parenthesized group when
each option maps to exactly one known skill and appears only once. Independent
skills in the same clause stay separate; repeated skills outside the group and
ambiguous punctuation remain ungrouped. Focused Candidate Fit tests: 67;
isolated PostgreSQL: 928 passed.

## 2026-10-15 — keep extra alternative CV claims reviewable

Added explicit handling for a confirmed OR group with additional unsupported
CV options. The group remains satisfied, while the extra claim stays visible
in resume diff and package preview. Focused tests: 63; isolated PostgreSQL: 923.

## 2026-10-15 — recruiter sensitive-context fallback

Expanded sensitive-topic detection to include the full recruiter context and
English passport references; parse JSON booleans without treating the string
`false` as true. Tests cover sensitive context and non-sensitive false response.
Focused tests: 13; isolated PostgreSQL: 921 passed.

## 2026-10-15 — preserve alternatives in resume comparison

Fixed a mismatch where scoring recognized an explicit alternative requirement
but CV review treated every option independently. Resume diff and prepare now
show a group as confirmed only when one same option is supported in both
sources. Focused tests: 61; isolated PostgreSQL: 917 passed.

## 2026-10-15 — tighten salary-period text boundary

Follow-up regression narrowed explicit salary-period recognition to the
adjacent suffix, rejecting unrelated time phrases. Focused salary tests: 83;
full isolated PostgreSQL: 914 passed.

## 2026-10-15 — Interview Agent IaC/cloud/observability exercises

Expanded curated exercises to match already recognized requirements for
Terraform, Ansible, AWS, Grafana and Helm. Scenarios emphasize reviewed plans,
idempotence, least privilege, telemetry gaps and reversible release checks.
Focused interview/command tests: 31; isolated PostgreSQL: 913 passed.

## 2026-10-15 — source publication-date field coverage

Added per-source `publication_date_provided` and `publication_date_missing`
counts over discovered eligible vacancies. Dashboard describes field coverage
without inferring date validity or vacancy freshness. Focused source tests: 55;
isolated PostgreSQL suite: 912 passed.

## 2026-10-15 — display explicit salary period evidence

Added conservative display-only extraction of explicit salary periods near a
currency-bearing value. Structured period fields win; unknown evidence is not
normalized or used by the strict filter. Focused tests: 82 passed; isolated
PostgreSQL suite: 910 passed.

## 2026-10-15 — application export audit trail

Added recorded status events to explicit application-package text exports.
Export uses the owner-scoped status-history repository lookup; missing history
is labeled rather than inferred. Focused tests: 35 passed; isolated PostgreSQL
suite: 905 passed. No schema change.

## 2026-10-15 — per-source Stretch yield

Per-source scan output now displays the existing processed, Good, Stretch,
filtered and duplicate counters. Added rendering coverage; scan selection,
deduplication and scores are unchanged. Source diagnostics: 30 passed. Full
isolated PostgreSQL suite: 878 passed. No personal runtime database or volume
was used.

## 2026-10-15 — conservative multi-option Candidate/Vacancy fit

Expanded the existing explicit alternatives parser from exactly two skills to
an explicit chain of two or more `or/или` options. Each option must contain one
known skill; repeated skills remain ambiguous and ungrouped. Added regressions
showing a three-option choice counts as one scoring item while an independent
required skill remains separate. Existing score weights and thresholds are
unchanged. Added conservative Oxford-comma support; comma-only skill lists
remain separate. A full suite initially exposed that boundary regression, which
was fixed and retained as a regression test. Focused matching/scoring/
Recommendation v2 tests: 52 passed; full local suite: 874 passed, 4 PostgreSQL
tests skipped. Isolated PostgreSQL rerun is blocked by Docker API permission
denial. Compileall, staged/worktree diff checks and staged/worktree/history
secret scan passed.

## 2026-10-14 — flattened requirement sections

Reproduced one-line `Requirements: Linux. Nice to have: Docker.` being treated
as two required skills, which reduced the existing structured technical score
from the intended 85 to 50 for a candidate with commercial Linux evidence.
Added English/Russian section and scoring regressions before the fix. Split
only at explicit punctuated known headings, preserving neutral sections and
the existing 85/15 weighting. Added the continuing engineering workflow to
`AGENTS.md` without removing project safeguards. Broader v3.6 fit remains
partial. Followed with a real Devexperts alternative-language sentence:
the extractor had treated Python as individually required, causing a 75
technical score instead of 100 for confirmed Linux/Bash/networking. A narrow
qualified-clause guard leaves that mention unknown, while an independent
Python must-have remains required. Regression covers both outcomes; general
alternative group semantics remain planned.

## 2026-10-14 — safe network cause classification

## 2026-10-14 — continued source reliability/security increments

After the core source fix, implemented independent follow-ups: latest scheduled
ledger persistence, active-manual/latest-finished dashboard selection; bounded
HTML source rendering after measuring 5940-character dense fixture; explicit
schema exceptions across 8 adapters (Arbeitnow previously silently returned0);
actual retry telemetry across existing bounded loops; partial collection and
budget-expiry metadata for Himalayas/SmartRecruiters/Job Bank with cache reuse.
Independent cached profile processing errors retain separate observations while
EURES collection IDs deduplicate. Public HH retry delta is measured around its
serialized discovery; retry policy unchanged. Fallback observation cannot hide
subsequent timeout, and certificate failure still alerts during HH cooldown.
Reproduced Job Bank loss after a successful detail followed by 503 or malformed
HTML; moved parse/enrich into request-isolation boundaries. Valid jobs remain,
independent queries proceed;403/429 stops further source calls. No source probe.
Strengthened secret guard to inspect staged/worktree/history, print paths only
and fail inspection errors. Five synthetic temporary-Git tests passed. Sanitized
progress exception logging and old failed-stage display; no real leak claimed.
Final targeted source/dashboard/Job Bank/EURES/guard 125 passed; full 844 passed,
4skipped (4.82s). compileall, git diff --check, expanded secret scan passed.
Test Compose still denied at Docker API, before test DB startup; PostgreSQL
integration assertions were NOT executed. All prior dirty edits retained;
HEAD d7a68d8/53 ahead and runtime unchanged; no staging/commit/publication.
Next safe roadmap increment: targeted existing requirements/fact comparison;
owner gates: isolated DB and local checkpoint, authorized live source/Telegram.


Final counter review reproduced 3 HH miscounts: attempted connection failure
was labelled skipped. Failed and unattempted cooldown counts are now separated,
with recovery retaining history. Focused 70 passed, full 844/4skipped (4.82s);
compileall/diff/secret guard/bash syntax passed after the correction.

## 2026-10-14 — source diagnostics and attempt ledger

Reviewed historical commit9007824 aggregation and reproduced its missing-found
contract after a failed first profile; local helper from5c4b959 already guarded
that field but dropped failure history. Added `search/source_summary.py` with
uniform attempt counters/status/history, cache/EURES observation dedupe, safe
legacy-error rendering and scan outcome. Added `sources/diagnostics.py` typed
Russian categories without exception URLs/messages; source-loop failures now
have discovery/processing/summary stages. Prefilter failures preserve valid
jobs; telemetry failures rebuild from per-profile ledgers. Alerts grouped by
source/code/stage/action per scan use explicit plain parse mode; HTML dashboards
escape once and show incomplete outcomes. RemoteOK validates top-level list
and explicit connect/read/write/pool30s, with no speculative retry. EURES records
actual retries and query/detail diagnostics; HH records permitted API403 fallback.
Targeted source+Telegram+adapter suite79 passed, new loop/RemoteOK19 passed;
full810 passed/4skipped, then compatibility-helper+HH/EURES52 passed.
compileall/diff/history secret scan passed. Isolated test Compose denied before
startup (Docker API permission); no production DB/runtime change, no commit.
Next independent task: scheduled history persistence and dashboard selection.


Added bounded typed-cause classification for transport failures. HH logs and
skip metadata now preserve a safe category; no messages/URLs or guessed IP
family are used. Regression reproduced raw SSL/DNS payload disclosure in
source summaries; sanitized summary, warning and alert paths. Network/source/HH
targeted suite: 48 passed. Final full unit suite: 785 passed / 4 skipped;
compileall/diff/history-secret guard passed. PostgreSQL and Git checkpoint
remain sandbox-blocked; no production, external request or publication occurred.

## 2026-10-14 — Candidate Fact ADD/UPDATE/KEEP

Added a deterministic plan and private Telegram per-overlap choices, KEEP by
default. Choices do not write until final confirmation. UPDATE retains the old
fact inactive with its value/type/evidence and inserts an unknown replacement
in the resume transaction. Snapshot/profile validation and ordered row locks
prevent replacing a changed or foreign fact. Tests cover all choices, invalid
callbacks, another user, consumed previews and safe stale-target feedback.
Targeted import/private-route tests: 34 passed; full unit suite: 769 passed /
4 skipped; compileall/diff/history-secret guard passed. PostgreSQL integration
assertions added but environment-blocked before connecting. Git dry-run failed
because .git is read-only. No production or external action occurred.

## 2026-10-14 — source counter aggregation and checkpoint blockers

Regressions reproduced loss of earlier profile processing errors and loss of
independent cached EURES failures (2 + 3 displayed as 3). Aggregation preserves
processing counts and merges failure observations by discovery identity.
Targeted EURES/scan-isolation/Telegram suite: 41 passed. Final full unit suite:
750 passed / 4 skipped; compileall/diff/history-secret guard passed. Isolated
PostgreSQL revalidation was attempted but sandbox denied local sockets before
connection; Docker access was also denied. git add then failed because .git is
read-only. Checkpoint remains preserved in the worktree, with no publication.

## 2026-10-14 — resume retry boundary and manual HH authorization

A new regression reproduced loss of the import preview when list_resumes
failed before atomic persistence; the retry boundary now includes this read.
job_scout traced the legacy manual HH flow: unauthorized setup retained routing
state despite an owner-gated sender. Main reproduced both state defects and
added owner-only setup and stale-state cleanup; the authorized owner flow is
covered with a mock HH client. Full unit suite: 748 passed / 4 skipped;
compileall and diff check passed. Isolated PostgreSQL revalidation attempted
but blocked by Docker permission denial and localhost socket PermissionError.
No production or external action occurred. Existing prior DB results were not
presented as a new run.

## 2026-10-14 — Telegram/HH network log payloads

After `921caf4`, tests reproduced that `wait_for_telegram` and
`scan_hh_chats` logged raw exception messages containing URL parameters.
Changed both warnings to report exception class only. Telegram bounded
backoff, HH chat polling gate, private actions and runtime settings were not
changed. No external request or production action. Final checks: 741 unit
passed / 4 isolated-DB skips; 745 passed with isolated PostgreSQL; compileall,
secret scan and `git diff --check` passed.

## 2026-10-14 — dependency advisory floors

After `292e6d2`, local `pip list` showed pypdf 6.20.0 and python-multipart
0.0.32. Official pypdf advisory GHSA-9mx8-4j7g-633p affects <6.20.1 with a
possible infinite loop during tree-item removal; pypdf 6.20.1 was published
Oct 12. Our PDF resume path uses `PdfReader` and text extraction, so this
specific tree-item operation is not proven reachable. Official
python-multipart advisory GHSA-v9pg-7xvm-68hf affects <0.0.31, and other
published parser advisories affect older versions. Raised the minimums in
`requirements.txt` to pypdf 6.20.1 and python-multipart 0.0.31, then installed
pypdf 6.20.1 into the local test venv. The running Docker image and all data
remained unchanged. Sources:
https://github.com/py-pdf/pypdf/security/advisories/GHSA-9mx8-4j7g-633p
and https://github.com/advisories/GHSA-v9pg-7xvm-68hf.
Final checks on local pypdf 6.20.1: 739 unit passed / 4 isolated-DB skips,
743 isolated PostgreSQL passed, `pip check` found no broken requirements,
compileall/secret scan/`git diff --check` passed.

## 2026-10-14 — EURES per-query and per-detail failures

After `7581903`, tests reproduced whole-source failure on one EURES search
HTTP 503 and one detail HTTP 404, losing verified results from other units.
The adapter now catches transport, HTTP and malformed-response failures at
each independent query/detail boundary, logs only class or HTTP status, and
continues. If every search fails or every attempted detail fails, it still
raises the last error. Existing bounded transport retry remains; HTTP statuses
are not retried. Added regressions for partial HTTP, malformed search contract
and total HTTP failure. No live EURES request, score change or deployment.
Final checks: 739 unit passed / 4 isolated-DB skips; 743 passed with isolated
PostgreSQL; compileall, secret scan and `git diff --check` passed.

## 2026-10-14 — Job Bank repeated detail cache

After `c6fb2b7`, read-only `JOB_AGENT_COMPOSE_PROJECT=repo ./job-agent status`
showed 3.5.7 runtime healthy; last 120 app log lines showed HH API 403 followed
by public web ConnectError in one scan, and another HH ConnectError on the next
scan. The 900-second HH cooldown activated while EURES, Job Bank, RemoteOK,
Arbeitnow and Greenhouse continued. The logs do not identify DNS/TLS/proxy as
the root cause. No production state or external service was changed.

The same twelve Job Bank detail IDs appeared in adjacent scans at 22:21 and
22:36 UTC; in the later pass the first/last detail responses span about 55
seconds. Added a bounded one-hour in-memory HTML cache, max 256 details,
looked up only after a fresh listing includes the ID. Forced manual scans
bypass detail cache, and expired entries refetch. A regression first showed
two detail requests in adjacent scans, then one after the change. Existing
five-second pacing and source/result limits remain. No post-change runtime
timing or eligibility claim is made. Final checks: 735 unit passed / 4
isolated-DB skips; 739 passed with isolated PostgreSQL; compileall, secret
scan and `git diff --check` passed.

## 2026-10-14 — Georgia source detail host boundary

After `d3a949b`, reviewed all active source detail fetch paths. HR.ge and
JOBS.GE parsed listing hrefs, joined them to a base URL and fetched the result
without verifying the host. A malicious absolute URL in either listing could
send a request to loopback or an unrelated host. Two unit regressions reproduced
the cross-host fetch before the fix. Added `_source_detail_url` to require HTTPS,
the exact source host, standard port and no URL credentials. Relative same-host
links still work. No live source or production access was used. Final checks:
733 unit passed / 4 isolated-DB skips; 737 passed with isolated PostgreSQL;
compileall, secret scan and `git diff --check` passed.

## 2026-10-14 — one-time resume confirmation

After `7778de3`, reviewed candidate import and found duplicate Telegram
callbacks could both pass the pending preview check and write the same resume
and facts. A concurrent regression reproduced two writes. The callback now
claims the token before resume persistence; only one callback can proceed.
No schema, profile facts or production data were touched. A mid-write failure
still requires reupload and may leave a partial resume/facts set; transactional
recovery is recorded as a separate task. Final checks: 731 unit passed / 4
isolated-DB skips, 735 passed with documented isolated PostgreSQL; compileall,
secret scan and `git diff --check` passed.

## 2026-10-14 — scheduled scan and security boundaries

Started at `99ea166` on `feature/v3.5.7-international-market-coverage`, 46
commits ahead of origin; tracked tree clean, two owner roadmap proposals
untracked and preserved. Read BRIEF, current state/handoff/tasks/known issues,
canonical roadmap and proposals; inspected source adapters, scan orchestration,
watcher, Telegram routes, HH private actions, test DB configuration and CI.

Reproduced four local failures before fixing them: `scan_all` stopped at the
first failing user; group chat updates could reach candidate commands/callbacks
through a registered chat ID; an arbitrary registered user could invoke
`apply_match` with the global HH applicant credential when the private API was
enabled; and a bad vacancy stopped processing later vacancies from its source.
Transport exceptions could also place a full URL/query in source alerts, and
HH API error bodies were forwarded into errors. Added regressions, then fixed
each at the narrowest service/router boundary. Source summaries now show
`partial` and `processing_errors` while preserving successful counts. HH
ConnectError remains an isolated bounded cooldown; no unsupported network
root cause or CAPTCHA bypass is claimed.

Final local checks: 730 unit passed / 4 isolated-DB skips; 734 passed with
documented isolated PostgreSQL on `docker-compose.test.yml`; `compileall`,
secret scan and `git diff --check` passed. No production Compose/DB/volumes,
Telegram runtime, external HH action, deployment, VERSION or publication was
changed. Real Bot API channel acceptance, authorized runtime verification and
upstream HH ConnectError diagnosis remain open. The canonical roadmap was
annotated without changing proposed version labels.

## 2026-10-14 — night development: watcher isolation and roadmap sync

Starting branch `feature/v3.5.7-international-market-coverage` at `8781081`,
ahead of its tracked remote by 45 commits. Tracked tree was clean; two
untracked owner proposal Markdown files were preserved and excluded. Read
BRIEF, root/PROJECT_OS roadmaps, proposal/prompt, watcher code/tests and
relevant handoff/task history before editing.

Stage 1: watcher baseline targeted suite passed 44, skipped 1. One user's
pause state or active search-profile lookup could abort delivery to later
subscribers; retry-state lookup could abort the retry tick. These lookups now
skip only the affected user, log the exception type without post content, and
continue. Four regression cases cover live pause/profile and retry isolation.
Skipped live lookup events are not marked seen or queued because scope could
not be verified; Bot API redelivery is not guaranteed. Existing queued retry
entries are preserved. No score, schema, threshold or notification changes.

Stage 2: canonical root ROADMAP now maps v3.5.1–v4.x complete vision to current
implemented/partial/planned evidence and acceptance gates. Historical v3.5.4
EURES milestone stays distinct from its broad Multi-Source vision; proposed
v3.5.8/v3.5.9 numbers do not change `VERSION=3.5.7`. PROJECT_OS decisions,
tasks, current state, brief, known issues, ideas and handoff synchronized.
Relocation-first source expansion is pending a verified lawful feed and useful
live results; no unsupported adapter or legal claim added.

Verification after final code change: 720 unit passed / 4 isolated-DB skips;
724 isolated PostgreSQL passed using `docker-compose.test.yml` postgres-test
and the documented test URL. `compileall`, secret scan and `git diff --check`
passed. Test PostgreSQL only; production Compose, volumes, Telegram runtime,
VERSION, publication and external applications untouched. Real selected
channels/Bot API access and separately authorized runtime acceptance remain
owner gates. The two proposal files stay untracked and are not commit inputs.

## 2026-10-12 — Relocation-first excludes domestic onsite vacancies

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

## Next priority correction — Telegram vacancy channels

Owner explicitly restored Telegram channel discovery as a priority. Current
implementation accepts channel_post updates and user-forwarded posts only;
there is no configured channel watchlist or arbitrary-channel history/search
collector. A registry label is not proof of automatic coverage. Existing
Telegram evidence-parser fixes are completed; do not repeat them. Next stage:
identify owner-selected remote/DevOps and AM/GE channels, distinguish actual
Bot API access from manual-forward destinations, implement truthful configuration
and visibility with regressions. Requested @names/links or permission to curate
a list; response pending. No user-account login/MTProto collection authorized.
Keep deployment gate separate; Telegram discovery task is independent.

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


## 2026-10-14 — Tested candidate and runtime gate

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

Optional NaN/infinite/fractional/out-of-storage-range source amounts now remain
unknown instead of aborting source batches or overflowing PostgreSQL Integer.
Telegram huge integers likewise remain source text. Valid adjacent jobs and
representable whole amounts survive. New numeric regressions: 12 cases.
Earlier explicit residence/country constraints outrank broad worldwide prose;
source salary text is bounded/escaped and display-only. Telegram support
absence is unknown and explicit refusals remain false.

Existing Compose repo app up/PostgreSQL healthy at last read; no rebuild,
update or publication performed. Last identified runtime build c829a5f.
Deployment approval/real startup/source/scoped Telegram acceptance remain
pending. Do not close v3.5.7 or skip to v3.6 until mandatory acceptance.
Next decision: owner approval for the latest tested candidate, then recheck
clean Git, update only approved source and validate startup plus /sources,
/jobs relocation, /jobs relocation below and detailed cards. Independent
AM employer-feed research remains open; prior researcher hit usage limit
without delivering a verified integration candidate, so none was invented.
Context Watch placeholder hash recorded privately; no new synchronized delta
or live ChatGPT access. MODEL_ROUTING was read; supported job_scout performed
read-only sync audit. No expensive reviewer was needed.

## 2026-10-14 — Telegram source evidence

Telegram ingestion now uses shared tri-state support evidence: absence unknown,
explicit refusal false, affirmative employer support true. Negated remote and
remote-server experience do not set remote work mode. Ambiguous currency,
missing period and decimal salary remain source text; only explicit whole
amounts/currency/period populate salary fields. No scoring formulas/threshold
changes or migration. Updated the old parser fixture to explicit USD/monthly.
21 targeted tests passed, full unit 646 / 3 skipped, PostgreSQL 649;
compileall/secret/diff passed. Local stage follows af1ff56, not deployed.
Next: bound malformed numeric source values to avoid losing valid source jobs.
Runtime/deployment and Telegram acceptance gate remain as recorded in HANDOFF.

## 2026-10-14 — Source salary and remote evidence

Resumed from b228ea5 and preserved interrupted local edits. Source 3.5.7,
branch feature/v3.5.7-international-market-coverage. Completed source-evidence
quality stage: explicit residence/country limits outrank worldwide boilerplate
in signals and cards, including old cached rows; Himalayas keeps the stated
residence clause without mapping regions to countries. Existing weights,
threshold 65 and explicit US/EU rules remain unchanged. Unsupported country
hiring/work authorization remains uncertain.

Source salary text now reaches /job as bounded, escaped display-only evidence.
Decimal/hourly or ambiguous amounts do not enter the legacy numeric salary
parser or monthly scoring; structured salary wins when present. Regression
coverage includes Job Bank decimal hourly text, unchanged match score, malformed
metadata, HTML escaping, structured precedence and remote restriction examples.
46 targeted passed; full unit 631 passed / 3 skipped, PostgreSQL 634 passed;
compileall, secret scan and diff check passed. No migrations or provider calls
added. This stage is local and undeployed; read actual commit HEAD from Git.

Read-only runtime check: existing repo app up ~2h/PostgreSQL healthy. No runtime
update performed here; previous c829a5f build remains the last identified build.
The earlier startup/CI records below are historical, not new acceptance.
Deployment agreement remains pending. Context Watch is an unsynchronized
placeholder (no meaningful delta); no live ChatGPT access was claimed.

Next independent v3.5.7 task: fix Telegram ingestion's unknown/negative support
and ambiguous decimal salary parsing, then tests/security/docs/local commit.
After approved runtime update, validate startup/source/Telegram acceptance
before closing v3.5.7 and beginning v3.6. Keep old six stages complete.


Owner Telegram output showed ordinary onsite vacancies in Russia inside the
Relocation-first list, although the intended route prioritizes work abroad or
remote work that can continue after moving. Root cause was permissive current-
country handling when explicit geography settings were absent. The strategy
filter now excludes a same-country onsite vacancy from Relocation-first unless
`domestic_relocation` is explicitly enabled. Explicit remote roles and unknown-
country jobs remain discoverable; Career-first is untouched. No score, score
ordering, threshold, or visa/work-eligibility inference changed.

Regression tests cover current-country onsite exclusion, remote and unknown-
country retention, explicit domestic-move opt-in, and Career-first compatibility.
Targeted suite: 49 passed. Full local suite: 437 passed, 3 skipped. Isolated
PostgreSQL suite: 440 passed. `compileall`, secret scan, and `git diff --check`
passed. Compose `repo` rebuilt on runtime 3.5.7; PostgreSQL healthy and startup
scan completed at 18:26:17 UTC. One HH public-web request logged a
transient `ConnectError`; the scheduler scan completed. User-visible
confirmation after the fix remains pending.

# Development Log

## 2026-10-13 — Owner-requested shutdown checkpoint

At 08:28 Moscow inspected clean Git at bacdcc7 on the existing v3.5.7 branch.
Application/data/build inputs match tested implementation 443aaeb; no unfinished
code edits. Read-only Compose status confirms repo app up/PostgreSQL healthy
and separate postgres-test healthy. Updated BRIEF, CURRENT_STATE, TASKS,
ROADMAP and HANDOFF with stop/resume instructions, pending deployment approval,
and earlier verified results: 606 unit / 3 skipped, 609 PostgreSQL, compileall,
secret/diff and separate Docker/Python 3.12 validation. No full suite rerun for
documentation-only stop. Corrected two stale stage descriptions; detailed
history remains in Git and previous snapshots. No deployment, publication,
service stop, data/volume removal or new long task. Private context refreshed
outside Git, retaining 600 file permissions. Next gate remains approved runtime
update and real source/Telegram acceptance before closing v3.5.7.
Shutdown documentation validation: secret scan and git diff --check passed.

## 2026-10-13 — Live confirmation of old HH aggregate recovery bug

Fresh read-only repo logs show HH source 2 failed at 05:08:33.606 UTC with
KeyError found in aggregate["found"] += len(jobs), running the old c829a5f
build. Scheduler scan completed 05:08:34.949, but the recovered source batch
was not processed. The exact skip/error→success transition is already fixed
and regression-tested in 5c4b959, included in validated implementation 443aaeb.
No new code change needed; recorded live evidence and kept pending owner
deployment approval. Runtime app remains up and PostgreSQL healthy.

## 2026-10-13 — Transfer checkpoint after six local stages

Implementation HEAD 443aaeb, source 3.5.7 on existing feature branch, all six
stages committed. Latest unit 606 / 3 skipped, PostgreSQL 609, safety checks and
separate Python 3.12/Docker validation passed. Private index/current context
updated outside Git, old snapshots preserved and document modes 700/600 applied.
Requested owner approval to deploy implementation 443aaeb under the latest
production-deployment gate; response pending. Working runtime remains c829a5f.
No push, merge, release, deployment, migration or employer contact performed.
Next: consume the owner decision, verify the tested app/data tree and apply only
if approved, then startup/source/Telegram acceptance before closing v3.5.7.

## 2026-10-13 — Unicode explicit role/resume tokens and candidate build

ASCII/Cyrillic tokenization made explicitly selected Georgian/Armenian query
text empty in local discovery/matching. Switched those tokens and existing
resume overlap/role selection to Unicode words, keeping original technical
punctuation/underscore boundaries, generic exclusions, min length and all
scoring weights/caps/threshold. No translations/aliases or stored preferences
were changed. Regressions prove same role bonus/total as English for explicit
local-language queries, no cross-language inference, retained English/Russian
behavior and resume selection.

Targeted Unicode/Georgia/resume/Staff 48 passed. Full unit 606 passed / 3 skipped;
PostgreSQL 609 passed; compileall, secret scan, diff check passed. Built separate
job-agent-validation:3.5.7-local image; Python 3.12 imports/compile passed in an
ephemeral network-disabled container. Running repo services/volumes were not
changed. Latest request requires explicit production deployment agreement; the
working runtime is still c829a5f. Next gate is owner-approved runtime update,
startup source-quality review and real scoped Telegram acceptance before v3.6.

## 2026-10-13 — Exact Devexperts qualification section boundaries

The verified public support posting uses `What we expect from candidates:` and
`As a Plus:`. Exact section matching did not recognize either longer required
label or preferred label. Added the two variants, preserving existing weights,
skill vocabulary and thresholds. Regressions cover cleaned HTML, case/inline
forms, negative near-matches, repeated required skills, and optional CI/CD in
an explicitly synthetic example. The real posting is not claimed to mention
CI/Jenkins. Nontechnical conditions remain unscored and no candidate facts are
created. Existing alternative-language lists are not modeled yet; Python's
required-section mention must not be presented as individually mandatory.

Targeted parser/technical/source 80 passed; full shared unit 585 / 3 skipped,
PostgreSQL 588 passed; compileall, secret scan and diff checks pass. Runtime
remains c829a5f; no deployment/publication/applications. Next Unicode matching
for explicitly selected local queries, then owner acceptance of v3.5.7.

## 2026-10-13 — Curated GE SmartRecruiters/Devexperts public feed

Verified SmartRecruiters' documented public Posting API and an active Georgia
Devexperts Application Support Engineer Level1 posting. Added GE-only curated
adapter, catalog/registry/service wiring, six-hour scheduled cache and source
controls. Each profile uses its own selected queries; no roles are injected.
One PUBLIC/country=ge list page (max 100), max 10 relevant details, request 10s and
whole 60s budget, one transport retry only. Strict ID/URL validation avoids
feed-provided request targets. Partial verified details survive later request
failure or own budget expiry; external cancellation propagates. Structured
hybrid outranks prose about possible remote work; GE-only remote never becomes
worldwide. Missing salary, visa and relocation remain unknown.

Live read-only adapter execution found one support-related GE/hybrid posting
with visa/relocation unknown. No employer/candidate contact or runtime deploy.
Targeted source/catalog/service/cache 59 passed; full shared candidate unit 585
passed / 3 skipped and PostgreSQL 588 passed; compileall/secret/diff passed.
Prepared exact-heading parser tests are included but committed independently.
Primary contract https://developers.smartrecruiters.com/reference/v1listpostings
and https://developers.smartrecruiters.com/docs/authentication.

## 2026-10-13 — Bounded remote support query coverage

Himalayas previously truncated the default Relocation-first seven roles to
four requests, omitting selected customer support. Added stable conservative
remote-role planning for this remote-only source. Supplied support/IT roles get
request slots before physical-work roles; no query text is invented, stored
settings changed, or role/score promoted. Query budget remains four with the
same markets and daily cache. Parser still matches the original complete role
list. AM and GE request/result regression passes; career order is preserved.
Live read-only primary API probes during research returned support listings for
both country filters, not proof of candidate hiring or work eligibility.

Targeted planner/source/cache 73 passed; full shared candidate unit 568 passed
/ 3 skipped, isolated PostgreSQL 571 passed; compileall/secret/diff pass.
Prepared SmartRecruiters module tests are included but not wired yet. Runtime
remains c829a5f; no deploy/publication/outreach. Next connect that curated feed.

## 2026-10-13 — Source listing expiry in vacancy cards

Himalayas public API documents expiryDate; its primary references differ on
seconds/milliseconds/ISO representation. Added conservative finite epoch
seconds/ms and timezone-aware ISO parsing, bounded raw evidence, and UTC source
listing-expiry display through existing source-ref JSON and the /job renderer.
Past expiry is visible without relabeling an employer opening as closed; future
expiry does not establish active hiring or an employer application deadline.
Missing, malformed or ambiguous dates remain unknown. No database migration,
score, threshold, discovery filter, or provider request-volume change.

Targeted parser/source/service/card suite 76 passed. Full shared worktree unit
563 passed / 3 skipped, PostgreSQL 566 passed; compileall, secret scan and diff
check passed. Independently prepared query-plan/ATS module tests are included
in full totals and are not yet wired. Runtime remains c829a5f; no deployment,
publication, external application or messaging was performed. Next implement
bounded remote support query planning.
Primary references: https://himalayas.app/api and
https://himalayas.app/docs/openapi.json.

## 2026-10-13 — HH recovery/summary completion and context reconciliation

Resumed clean c829a5f on feature/v3.5.7-international-market-coverage. Read-only
Compose check confirms the previous startup scan completed at 21:53:38 UTC /
00:53:38 Moscow, with HH isolated and PostgreSQL healthy. Draft PR #18 remains
open at remote f9ed986; its Python/Docker/secret CI passed, covering only that
remote commit. No push, production deployment, merge or release was performed.

Fixed follow-up regressions: skipped HH now displays quietly as `пропущен`,
not zero live vacancies; mixed-profile results display `частично` with their
successful counts. HH probes serialize across concurrent scans, invalidate
stale HH caches immediately on ConnectError, and genuinely retry after cooldown
rather than returning the old anonymous-hour cache. Aggregate recovery cannot
raise KeyError after an earlier skipped/error result. Per-profile evidence is
preserved; other provider errors retain their existing alert path.

Targeted HH/cache/Telegram tests: 49 passed. Shared candidate full unit suite:
486 passed / 3 skipped; isolated PostgreSQL: 489 passed; compileall, secret scan
and diff check passed. Prepared independent source-expiry parser tests are also
present in this shared worktree and will be committed with their separate
card-rendering stage. New changes are not deployed; running build is c829a5f.

Compact BRIEF/HANDOFF/CURRENT_STATE replace accumulated startup snapshots;
exact prior files are preserved in PROJECT_OS/history with c829a5f anchors.
Aligned reading order with AGENTS.md and corrected stale runtime/CI/salary
wording claims. Historical AI job-bot's original search→evaluate→CV→application
→conversation pipeline remains the roadmap origin; latest approval gates apply.

## 2026-10-13 — Silently skip HH ConnectError and retry periodically

The owner clarified that a HeadHunter `ConnectError` warning must not be sent
to Telegram. Scan-level source handling now logs it locally, records it as a
skipped source, and continues other adapters without a chat alert. A
process-local 15-minute cooldown prevents the second search profile from
repeating the failed request and lets the next scheduled/manual scan probe HH
again after the cooldown. Other provider errors still generate their existing
warning. The HH-only bounded retry behavior for other transport errors remains
unchanged. Regression coverage checks silence, cross-profile cooldown, and
recheck after expiry. Targeted suite: **18 passed**; local suite: **444 passed,
3 skipped**; isolated PostgreSQL suite: **447 passed**; compileall, secret scan
and diff check passed. Compose `repo` rebuilt at 00:52 Moscow; runtime 3.5.7
is up and PostgreSQL healthy. The startup scan reproduced one HH
`ConnectError`: the app logged a single cooldown warning, sent no source-error
chat notification, and proceeded with the next profile and other providers.
Himalayas, Remote OK, Arbeitnow, Job Bank, EURES, Greenhouse, Lever and HR.ge
returned successful responses in the inspected window. The full startup scan
had not completed at this log check. Commit remains pending; no publication.

## 2026-10-13 — Add Georgian lower-barrier manual job portal

The local-market audit found `jobs.ss.ge`, a Georgian-language vacancy board
with categories for cleaning, worker/loader, hotel/tourism, factory/production,
and no-experience roles. Public pages provide listing details, but this review
did not establish a reusable public job API or permission for repeated
automated extraction. Added a market-scoped, clickable manual-search entry to
`/sources`; it remains excluded from automated source toggles and scans. The
entry explicitly notes the missing API/automation permission. Targeted source
tests: **5 passed**; full suite: **443 passed, 3 skipped**; isolated
PostgreSQL suite: **446 passed**; compileall, secret scan and diff check passed.
Compose rebuild and Telegram `/sources` check remain pending. The board's
Georgian-language content and any employer-specific language/work-
authorization requirements still need manual review.

## 2026-10-13 — Skip public HeadHunter connection errors

The owner requested that a public HH `httpx.ConnectError` be skipped
immediately while the scan continues through other enabled sources. HH public
search now re-raises connection-establishment failures without retrying; the
existing scan-level adapter isolation records the error and continues with
the other discovered adapters. Other `httpx.TransportError` types retain one
bounded retry. HTTP status behavior, CAPTCHA handling, and private applicant
methods are unchanged. Regression tests cover API and ordinary public-web
search; targeted suite passes **15 tests**. Full suite, isolated PostgreSQL
suite, compileall, secret scan and diff check pass (**443 passed, 3 skipped**;
PostgreSQL **446 passed**). Committed as `5a815b5`. Compose `repo` rebuilt at
00:43 Moscow; runtime 3.5.7 and PostgreSQL remained healthy. Startup `scan_all`
completed at 21:44:48 UTC / 00:44:48 Moscow. Live logs show HH
`ConnectError` skipped without retry while Himalayas, Remote OK, Arbeitnow, Job
Bank, EURES, Greenhouse, Lever and HR.ge continued successfully. No other
source errors were visible in this scan.

## 2026-10-13 — Recognize remote-board requirement sections

Reviewing the Himalayas Canonical Associate Linux Support Engineer card
showed that the source's `What we are looking for in you` heading was not
recognized. The technical requirement score and interview-risk dimension
therefore fell back to unknown despite visible Linux and Bash requirements.
The deterministic section parser now recognizes common `What we are looking
for`, `What you'll bring`, and `Nice-to-have skills` headings, including
curly apostrophes. The interview-risk evidence now states explicitly that its
coverage is for technical requirements only; non-technical education and
language conditions remain outside that score.

Regression coverage uses escaped HTML like the source payload and a score-level
case with required and preferred skills. Targeted tests: **37 passed**; full
unit suite: **439 passed, 3 skipped**; isolated PostgreSQL suite: **442
passed**. `compileall`, secret scan, and `git diff --check` passed. The live
Himalayas page currently lists the Canonical role's deadline as Nov 19, 2026,
claims all-country hiring scope, and separately states a bachelor's degree or
an alternative narrative plus strong written and spoken English; this source
content is not treated as verified employer eligibility or incorporated into
the technical-only score. Telegram confirmation of `/job 1273` after rebuild
remains pending.

Compose `repo` was rebuilt at 00:14 Moscow on Oct 13 with both existing named
volumes preserved. Source/runtime report 3.5.7, PostgreSQL is healthy, and
startup `scan_all` completed at 21:15:52 UTC. One isolated HTTP `ConnectError`
occurred during discovery; the scheduled scan completed successfully.

A final wording check found that the displayed interview-risk value is `100 −
technical requirement coverage`, so “coverage” alone described the opposite
direction from the number. The evidence now gives that formula and says the
index is unavailable when no technical requirements were extracted. It does
not assess education or language. Targeted recommendation tests: **5 passed**;
full isolated PostgreSQL suite: **442 passed**; compileall, secret scan, and
diff check passed. The runtime checkpoint is recorded below.
Committed locally as `a3a2494`; added explicit curly-apostrophe regression in
`e382ddb`. Rebuilt Compose `repo` at 00:17 Moscow Oct 13, preserving named
volumes. Source/runtime remain 3.5.7, PostgreSQL is healthy, and startup
`scan_all` completed at 21:19:29 UTC after an isolated `ConnectError`.

## 2026-10-12 — Separate current English level from technical reading

Updated the candidate bootstrap template to store general English as B1 and
retain B2 as a technical-reading estimate, matching the owner's current
self-assessment and earlier distinction. Bootstrap does not consume either
language key to overwrite persisted candidate data. Added a configuration
regression. Targeted tests: 3 passed; full suite: 437 passed, 3 skipped;
compileall, secret scan, and diff check passed. Committed locally as
`8ca977f`.

## 2026-10-12 — Emerging Travel Group manual AM/GE lead

Reviewed the official Emerging Travel Group posting for Junior DevOps
Engineer. It is marked remote and lists Armenia and Georgia as available
locations; stated requirements include 1.5+ years commercial DevOps, Linux,
Ansible, Docker, six months of Kubernetes, and English B1+. Workable's own
help page documents public endpoints for published job listings, but the ETG
account endpoint returned HTTP 403 in verification. Added the official ETG
listing as a manual link for both AM and GE; it is excluded from scans and
source toggles. No eligibility, visa, or relocation support is inferred.
Targeted tests: 5 passed; full suite: 437 passed, 3 skipped; compileall,
secret scan, and diff check passed. Compose `repo` rebuilt at 21:37 Moscow,
PostgreSQL healthy, startup scan completed at 21:38:46 UTC. One HH search had
a transient isolated `ConnectError`; the scheduler scan completed.

The owner's 21:13 Telegram list with a Tyumen onsite result preceded the 21:26
runtime rebuild containing the current-country Relocation-first filter. The
owner should confirm `/sources`, `/jobs relocation`, and `/jobs relocation
below` on the current runtime. Committed locally as `432d44c`.

## 2026-10-12 — AM/GE manual source discovery links

Reviewed current public AM/GE candidate boards. Added selected-market,
clickable manual-search entries for ITA Jobs, Staff.am, Job.am,
CareerCenter.am, Findjobs.ge and LeverX Careers to `/sources`. Manual entries
do not appear in source toggles or adapter execution. This gives the owner
direct paths to local listings without mirroring data where terms or feed
permission do not support recurring extraction.

Findjobs.ge terms dated 2026-09-27 welcome AI assistants but prohibit
repeated/systematic extraction or reuse of substantial board data without
written permission. ITA Jobs describes its listings as a reference directory
linking to employer/academy applications but documents no reusable public job
API. Current LeverX Support Engineer is in-office in Georgia and asks for
English B2+; this remains a manual lead and the owner's B1 estimate is a known
gap, not a hard exclusion.

Verification: local suite **432 passed, 3 skipped**; isolated PostgreSQL suite
**435 passed**; compileall, secret scan, and `git diff --check` passed.
Committed as `ffabb1b`. Rebuilt local Compose project `repo`; startup
`scan_all` completed at 18:06:12 UTC with runtime 3.5.7 and healthy PostgreSQL.
The inspected log window has no request to a manual portal.

## 2026-10-12 — HeadHunter selected-market discovery

Verified the official public `/areas` catalog: RU is area `113`, GE is area
`28`, and Armenia is not listed. Added bounded HH searches for each represented
current/target market while preserving the profile's deduplicated role query
list. Results are deduplicated across markets and receive country attribution
from their area-scoped request. No unsupported Armenia area is guessed; other
sources remain responsible for AM listings.

Local suite: **430 passed, 3 skipped**. Full isolated PostgreSQL suite:
**433 passed**. `compileall`, secret scan, and `git diff --check` passed. The
change is committed as `61fe39d`. Compose was rebuilt from the branch; HH's
public-web fallback returned HTTP 200 for areas 28 and 113, and startup
`scan_all` completed at 17:56:41 UTC with PostgreSQL healthy. Owner Telegram
acceptance remains pending.

## 2026-10-12 — AI job-bot GE/AM bootstrap defaults

Updated the private-use bootstrap profile so a fresh AI job-bot setup selects
Georgia and Armenia in parallel and starts Relocation-first discovery with
bounded warehouse, production, hotel, kitchen, cleaning, construction and
customer-support queries. This does not overwrite existing database settings,
change the 65-point threshold, alter ranking, or infer work eligibility.
Added a configuration regression. Existing source restrictions, unknown legal
evidence and manual-only application flow remain unchanged.

## 2026-10-12 — EURES padded location persistence guard
- Published the accumulated v3.5.7 candidate as `8da96f8`; push CI
  `38280187127` and PR CI `38280191809` passed. Updated Compose `repo` without
  deleting data; source/runtime report 3.5.7 and PostgreSQL is healthy.
- The resulting startup scan found a production-only EURES data shape: an
  Ireland `cityName` contained large fixed-width whitespace blocks and exceeded
  the 256-character database column. The insert failed for that vacancy while
  the scheduler continued.
- Normalize EURES location whitespace before persistence. A normalized value
  still over 256 characters is kept as raw source evidence and the city stays
  unknown. Country, visa, and relocation semantics are unchanged.
- Added regressions for padded and genuinely overlong source locations. Full
  isolated PostgreSQL suite: 429 passed, 73.24% branch coverage. Targeted
  EURES suite: 13 passed. Compilation, secret, and diff checks pass.
- Published as `159d510`; push CI `38281187340` and PR CI `38281192380`
  passed. The safe updater preserved both existing named volumes. Runtime is
  3.5.7, PostgreSQL is healthy, and the fresh startup scan completed at
  17:04:14 UTC after successful EURES search/detail responses. No database or
  source error, traceback, or repeated city-width failure appears in that log
  window.

## 2026-10-12 — Owner shutdown checkpoint
- Stopped at the completed independent-review stage at the owner's request;
  no new long operation was started. Saved completed work, remaining tasks,
  verification results, dirty-worktree details and the exact resume sequence
  at the top of `HANDOFF.md`, with a pointer from `BRIEF.md`.
- Read-only runtime check: source/runtime 3.5.7, app up and PostgreSQL healthy.
  Latest completed checks remain 319 local passes / 3 skipped and 3 repository
  PostgreSQL integration passes; compilation and diff checks passed. Startup
  scan completed at 01:37:50 Moscow. No publication or data-removal action.

## 2026-10-12 — Independent vacancy review and ordinary Staff roles
- Added `/jobs career`, `/jobs relocation` and `/jobs relocation below` with
  enabled-profile selection and the selected profile's own threshold. Lists
  keep descending score order. Explicit `/job` and `/compare` scopes and new
  callbacks preserve that profile through details and comparisons; cards name
  it. Existing commands and callback formats remain accepted.
- Fixed the matching rule that treated `hotel staff` as an engineering Staff
  level. Ordinary staff roles retain normal fit evaluation; technical Staff
  roles, explicit Senior/Lead/Principal, high experience, mandatory management
  and owner exclusions still restrict matches. Unknown sponsorship remains
  unknown; this does not guarantee a Good/Stretch result at the unchanged 65.
- Added behavioral, ownership, independent-score and real PostgreSQL scope
  regressions. Read-only peer review caught a lost comparison-button scope,
  which was corrected and covered before final verification. Full local suite:
  319 passed, 3 skipped; all 3 repository integration tests passed on isolated
  PostgreSQL. Compilation and `git diff --check` pass.
- Updated the canonical public roadmap with explicit completed/current/next
  stages. Reviewed the separate ignored private relocation roadmap against
  current official sources; personal facts remain outside public documents.
  Rebuilt Compose `repo` at 01:36 Moscow: source/runtime 3.5.7, app up and
  PostgreSQL healthy. Startup HH fallback, EURES, Job Bank, Greenhouse, Lever
  and HR.ge requests succeeded in the inspected log window. Telegram acceptance
  remains pending; `scan_all` completed at 01:37:50 Moscow. No commit, push,
  merge or release.

## 2026-10-12 — Below-threshold manual review
- Added `/jobs below` for nonzero matches under the configured
  threshold, sorted by score descending. The normal `/jobs` list, Match Score,
  threshold, notification behavior, and priority order are unchanged. Duplicate
  and zero-score results are omitted; the list warns that work authorization
  and relocation support still need confirmation.
- Regression coverage verifies the query range, descending score order,
  user-facing note, and real repository query. Targeted tests: 14 passed; all 3
  repository PostgreSQL integration tests passed. Full local suite: 286 passed,
  3 database tests skipped. Compilation and `git diff --check` passed.
- The first rebuilt app logged that the immediate startup scan missed its
  1-second grace by 4 seconds. Added a five-minute `misfire_grace_time` to the
  scheduled `scan_all` job and a regression test. Rebuilt Compose `repo` at
  01:15 Moscow on Oct 12; startup logs now show `scan_all` running immediately.
  Source/runtime report 3.5.7, PostgreSQL is healthy, and the app is polling.
  Telegram acceptance of `/jobs below` is pending; no publication or merge was
  made.

## 2026-10-12 — Remotive category RSS feed
- Investigated the owner's `/scan` result of `remotive: 0 (кэш)`. A read-only
  probe found 18 cached jobs, all from unrelated categories, confirming that
  the endpoint returned a broad feed instead of the requested DevOps category.
- Live API checks with three documented category values all returned the same
  18-job general response. Replaced the API request with Remotive's official
  Devops category RSS feed and bumped the persisted cache key to v3 so stale
  API results are bypassed after rebuild. Added XML parsing/request tests and
  fixtures. Seventeen targeted tests and the full suite (283 passed, 3 skipped)
  pass. Rebuilt Compose at 00:53 Moscow; the RSS endpoint returned HTTP 200
  with channel metadata and zero items. Both profiles therefore parsed zero.
- Official references: https://github.com/remotive-com/remote-jobs-api,
  https://github.com/remotive-com/remote-jobs-feed, and
  https://remotive.com/remote-jobs/devops/feed.

## 2026-10-12 — Remotive remote DevOps/Sysadmin feed
- Added the official Remotive public feed for DevOps/Sysadmin vacancies. One
  request of up to 250 postings is shared across both active profiles and users
  and cached for 24 hours in the existing PostgreSQL `runtime_state` table;
  `/scan` does not force a refresh. Cards and `/jobs` link back to Remotive and
  display its attribution. The adapter retains `candidate_required_location`,
  filters clear country-only mismatches for selected markets, and leaves
  regional/unknown scope and unstructured salary text unconverted. It performs
  discovery only.
- Reviewed the provider API terms and docs: listings are delayed by 24 hours,
  source attribution/direct links are required, and the provider recommends no
  more than four requests per day. The implementation fetches at most once per
  day. The source parser, location filtering, attribution, shared daily cache,
  and cache persistence across simulated restarts are covered by tests.
- Targeted tests: 28 passed. Full local suite: 282 passed, 3 database tests
  skipped; isolated PostgreSQL suite: 285 passed. `compileall` and
  `git diff --check` passed.
- Rebuilt Compose project `repo` at 23:42 Moscow on Oct 11. Source/runtime
  report 3.5.7 and PostgreSQL is healthy. Remotive returned HTTP 200 at
  20:42:47 UTC (23:42:47 Moscow); scheduled scans completed through
  21:29:30 UTC (00:29:30 Moscow Oct 12) without another Remotive request or a
  visible source error. Telegram acceptance of `/sources`, `/scan`, and `/jobs`
  for this addition remains pending. No commit, push, tag, release, or merge
  was made. The next active stage is practical Relocation-first coverage and
  relevance, preserving score order and the threshold of 65.

## 2026-10-11 — Score priority in `/jobs`
- The owner clarified that higher-rated vacancies must receive higher
  priority. `/review`, `/stretch`, and `/saved` already sort score descending,
  while `/jobs` was ordered by recency. Changed `/jobs` to rank by total score
  descending, then creation time descending, and renamed its heading to
  “Совпадения по рейтингу”.
- Added a PostgreSQL integration regression ensuring a newer 72-point match
  appears below an older 86-point match. The notification threshold and
  eligibility handling remain unchanged. Local suite: 274 passed, 3 database
  tests skipped; isolated PostgreSQL suite: 277 passed. `compileall` and
  `git diff --check` passed. Compose `repo` was rebuilt at 21:38 Moscow time;
  source/runtime versions both report 3.5.7 and PostgreSQL is healthy. The
  startup scan completed at 18:40:25 UTC (21:40:25 Moscow). Its logs show HH
  public-web fallback after API 403 and successful Himalayas, HR.ge, EURES,
  Job Bank, Greenhouse, Lever, Remote OK and HH requests; no source error
  appeared in the inspected tail.
- The owner confirmed `/jobs` ranking in Telegram at 23:27 Moscow time: 88,
  84, 82, then 78 and lower. A later supplied scheduled-scan log completed at
  20:25:14 UTC (23:25:14 Moscow); visible EURES, Job Bank, Arbeitnow, Remote
  OK and Greenhouse requests returned HTTP 200, with no error in the excerpt.

## 2026-10-11 — Curated Collectly Lever source
- Audited Lever's official Postings API and fetched the current Collectly
  published board using its unauthenticated read-only endpoint. The current
  Senior DevOps/DevSecOps role is explicitly remote and states GMT-7 to GMT+4;
  Lever lists Belgrade/RS as source location. The employer's hosted application
  form requires one or two weeks of onsite Yerevan onboarding and says travel
  and accommodation are covered. It does not verify hiring eligibility from
  Armenia/Georgia, Russian-citizen eligibility, salary, visa sponsorship, or a
  relocation package.
- Added a bounded Collectly-only adapter for selected AM/GE profiles. It
  requires explicit remote mode, a DevOps role match, a timezone band including
  UTC+4, and an official Lever-hosted URL. It retains the source office and
  country separately while leaving normalized country unknown; no application
  endpoint is called. The public board is limited to one page of 100 records
  and cached locally for six hours.
- Regression coverage includes remote-only and timezone filtering, role query,
  country ambiguity, salary fields, malformed payload, source registration,
  cache policy, and Telegram rendering of timezone scope with a hiring-country
  caveat. The targeted detail/Lever tests pass (16 tests); full local suite:
  274 passed, 3 database tests skipped. `compileall` and `git diff --check`
  passed. The PostgreSQL suite was not rerun because the change adds no
  database behavior or schema change.
- Compose `repo` was rebuilt at 21:04 Moscow time with PostgreSQL healthy. The
  startup `scan_all` completed successfully at 18:06:21 UTC (21:06:21 Moscow).
  Lever returned HTTP 200 for both independent profiles. EURES, Job Bank,
  HR.ge, Greenhouse, Himalayas and HH public search returned successful
  responses in the inspected log window; HH API 403 recovered through the
  ordinary public-web fallback. At initial deployment, Telegram acceptance
  was pending; the owner later verified the source plan and live scan below.
- Owner Telegram verification at 21:11–21:14 Moscow confirmed `/sources` lists
  Lever for both profiles. `/scan` found 1 live Lever vacancy in 9.6s; the
  completed scan processed 266 jobs (37 Good, 33 Stretch, 196 filtered) and
  sent 0 new notifications. Job Bank returned 12 in 71.4s and EURES 16 in
  55.2s. The supplied log excerpt shows Lever HTTP 200 for both profile calls,
  successful source requests, and no source exception. A read-only runtime DB
  lookup found Collectly job #1333 saved as filtered with score 0 because the
  Career-first profile explicitly excludes `senior devops`; this is not an
  adapter failure. At 21:20 the owner supplied review queues whose first cards
  were remote CloudCops (Good, 88) and Sporty Group (Stretch, 72).
- The same scan reported Relocation-first 74 processed and no Good/Stretch
  results. Its configured 65-point threshold filters lower-scoring leads; an
  inspected remote result scored 54. At the time, a manual-only
  below-threshold exploratory queue was noted as a possible UX stage. The owner
  later clarified that higher-rated results must remain first and confirmed
  descending `/jobs` order; do not promote below-threshold results ahead of
  higher ratings. Keep the 65-point threshold and continue source-coverage work
  without score inflation or exclusion changes.
- Current GitHub check: latest formal tag/release v3.5.6; only v3.5.0,
  v3.5.1, and v3.5.6 are formal version tags. Changelog milestones v3.5.2–
  v3.5.5 are cumulative and untagged. PR #18 remains an open draft. Local
  candidate `VERSION=3.5.7` is uncommitted and unpublished.

## 2026-10-11 — Remote eligibility scope in vacancy details
- The owner's live scan confirmed 20 cached Himalayas listings, visible source
  links, and remote results at the top of `/jobs`. Job Bank returned 12 in
  71.2s and EURES 16 in 34.1s; the supplied logs contained no source failure.
- Show saved remote hiring geography in `/job`: worldwide, listed countries,
  or unknown. Each state reminds the reader that remote availability alone
  does not confirm hiring eligibility in their country.
- Targeted regressions: 32 passed. Full local suite: 267 passed, 3 skipped;
  isolated PostgreSQL suite: 270 passed. `compileall` and `git diff --check`
  passed. Compose `repo` was rebuilt at 20:51 Moscow; app and PostgreSQL are
  healthy and the startup scan completed at 17:53:37 UTC. The inspected logs
  show Himalayas, EURES, Job Bank, HR.ge, Greenhouse, and HH fallback requests
  succeeding, without source exceptions, SSL failures, or timeouts. Owner
  acceptance of `/job 1273` completed at 20:56 Moscow time: worldwide is
  attributed to Himalayas and country-level hiring must be confirmed; salary
  is absent.
- Changes remain uncommitted on
  `feature/v3.5.7-international-market-coverage`. GitHub `main` and the latest
  formal tag/release remain v3.5.6; no publication action was taken.

## 2026-10-11 — Himalayas remote-source candidate
- Added the documented public Himalayas API as a remote-job source, scoped to
  each profile's role queries and selected/current country. Requests are
  bounded to four queries, three markets, one page of 20 jobs per pair, and a
  24-hour cache; source attribution and listing links are shown in Telegram.
- Preserve explicit country restrictions and keep missing restrictions
  unknown. Worldwide remote is not evidence of an individual's right to work,
  employer payroll, tax handling, visa sponsorship, or relocation support.
  Salary displays include the API's pay period.
- RemoteOK no longer maps missing hiring geography to worldwide. Explicit
  remote work can still receive processing priority while country eligibility
  remains uncertain.
- Targeted source, cache, preference, geo, and detail-view tests: 41 passed.
  Full local suite: 266 passed, 3 database tests skipped. Isolated PostgreSQL
  suite: 269 passed; branch coverage 69.70% (55% gate). `compileall` and
  `git diff --check` passed.
- Rebuilt Compose `repo` at 20:33 Moscow time. App is polling and PostgreSQL is
  healthy; named volumes `repo_jobagent_v3_pg` and `repo_jobagent_v3_files`
  remain attached. Startup scan completed at 17:35:32 UTC. Himalayas filtered
  requests for GE and AM, EURES, HR.ge, Greenhouse and Job Bank returned HTTP
  200 in the inspected logs. HH API returned 403 and the ordinary public web
  fallback succeeded; no source error appeared in the inspected window.
- At the time of this entry, Telegram acceptance of `/sources`, `/scan`,
  `/scanstatus`, `/jobs` and a Himalayas `/job <id>` card remained pending; the
  owner later accepted `/job 1273` as recorded in the newer handoff above.
  Work is uncommitted on
  `feature/v3.5.7-international-market-coverage`; GitHub `main` and the latest
  formal release remain v3.5.6.

## 2026-10-11 — Remote priority and Job Bank pacing regressions
- Keep the 30-point remote-work processing bonus active in both independent
  profiles. Job ordering changes within a source result batch; Match Score,
  notification thresholds, and per-profile role queries remain unchanged.
- Replace Job Bank's unconditional five-second pre-request sleep with a
  minimum five-second interval between serialized request starts. A slow
  response consumes that interval; fast responses wait only the remaining
  time. The bounded retry and partial-result behavior are unchanged.
- Regression tests cover both profiles, unknown/negated remote indicators,
  fast and slow Job Bank responses, and concurrent request serialization.
  Targeted tests: 34 passed. Local suite: 254 passed, 3 database tests skipped.
  Full isolated PostgreSQL suite: 257 passed, 68.59% branch coverage.
  Compilation and `git diff --check` pass.
- Compose project `repo` reports source/runtime 3.5.7 with the app up and
  PostgreSQL healthy. Rebuilt the current worktree into Compose at 17:09 UTC.
  The first inspected post-rebuild log only shows scheduler setup; Telegram
  timing and remote-order acceptance remain pending.
- Work remains uncommitted on
  `feature/v3.5.7-international-market-coverage`. GitHub `main` and the latest
  formal tag/release remain v3.5.6; PR #18 remains an open draft. Published PR
  checks do not cover this worktree. No push, merge, tag, or release was made.

## 2026-10-11 — Remote-work priority across profiles
- The owner asked to prioritize remote roles because a remote job may remain
  workable after relocation. Added a 30-point processing-priority bonus for
  explicit remote work in both independent profiles; each profile keeps its
  own role-query track. Match Score and notification thresholds are unchanged.
- A populated `remote_scope` is treated as evidence that the role is remote,
  but values such as `unspecified` do not mean worldwide. The feature does not
  infer country permission, visa, work authorization, payroll availability,
  or relocation support. Remote/onsite ordering, profile isolation, unknown
  scope, and negated labels have regression coverage across search strategies.
- Preference tests: 13 passed. Local suite: 251 passed, 3 PostgreSQL tests
  skipped. Full isolated PostgreSQL suite: 254 passed, 68.52% branch coverage.
  `compileall` and `git diff --check` passed. The first sandboxed PostgreSQL
  attempt could not open loopback sockets; rerunning with the approved local
  test-database access passed.
- The runtime remains on the earlier v3.5.7 build; the current uncommitted
  changes are not deployed. Telegram acceptance is pending a safe candidate
  update. Stable `main` and the latest formal tag/release remain v3.5.6; draft
  PR #18 remains against `main`. No push, merge, tag, or release was made.
- The separate local `.private/relocation-roadmap.md` now includes remote
  employment as a parallel priority and the checks needed to confirm that a
  specific employer supports work from the destination country.

## 2026-10-11 — Owner's live Job Bank scan check
- The owner supplied the result of `/scan` and `/scanstatus` from 19:33–19:36
  Moscow time. The scan completed with HH 209, Remote OK 3, Arbeitnow 2, Job
  Bank 12, EURES 16, Greenhouse 1 and HR.ge 2; Job Bank took 100.7 seconds.
- The supplied log excerpt shows Job Bank detail requests and EURES/HR.ge
  requests returning HTTP 200. It contains no Job Bank warning or source error.
  This verifies an ordinary live scan; it did not reproduce a transport failure,
  so partial-result recovery remains verified by regression tests.
- Personal relocation facts remain only in the ignored local plan and are not
  copied into tracked project documentation.

## 2026-10-11 — Job Bank partial-result resilience
- The owner's supplied scan logs showed `httpx.ConnectTimeout` while fetching
  a Job Bank detail page. That transport error failed the whole source after
  roughly 29 seconds, discarding already discovered/verified listings.
- Updated discovery to continue with remaining queries and detail pages after
  an individual request exhausts the existing single transport retry. Verified
  vacancies are retained; if every search or every requested detail fails, the
  source still reports an error. HTTP status errors remain failures. The
  five-second inter-request delay and serialized access are unchanged.
- Added regressions for partial detail success, all-detail failure, and
  continuing after a search query failure. Targeted Job Bank tests: 18 passed;
  full local suite: 248 passed, 3 PostgreSQL tests skipped; full isolated
  PostgreSQL suite: 251 passed, 68.44% branch coverage. `compileall` and
  `git diff --check` passed.
- Rebuilt Compose project `repo`; source and runtime both report 3.5.7, app is
  up, and the existing PostgreSQL service is healthy. Startup `scan_all`
  completed successfully at 16:25:19 UTC. Arbeitnow had one `ReadTimeout`,
  retried, then returned HTTP 200; the remaining displayed Job Bank, EURES,
  Greenhouse, and HR.ge requests also returned HTTP 200. No unrecovered source
  failure or traceback appeared. Job Bank did not hit a transport failure, so
  live failure recovery still needs a Telegram scan that exercises one;
  regression tests cover that path deterministically.
- Work remains uncommitted on
  `feature/v3.5.7-international-market-coverage`. GitHub `main` and its latest
  formal tag/release remain v3.5.6; PR #18 remains a draft. No push, merge,
  release, schema, credential, or volume change was made.
- Updated both README language entry points and the v3.5.7 candidate changelog
  status to the current 251-test baseline, documenting that the development
  changelog is English-only while published release notes are bilingual.

## 2026-10-11 — Owner acceptance of Lineate Recommendation v2 repair
- At 18:42 Moscow time the owner reopened `/job 1091` in Telegram. The live
  card showed Technical 42 and interview risk 58, with explicit required-skill
  coverage and `fit=good`; the previous acceptance gate is closed.
- The bot handled the Telegram update in 607 ms. The runtime was 3.5.7 on the
  active feature branch; the inspected startup scan had completed and its
  source logs contained no errors, SSL failures, timeouts, or tracebacks.
- The risk score is a matching-gap indicator, not a calibrated probability.
  Salary, work mode, visa sponsorship, and relocation support remain unknown
  unless the posting provides direct evidence. PR #18 remains a draft against
  `main`; no merge, tag, or release was made.

## 2026-10-11 — Lineate Recommendation v2 HTML normalization
- Owner reopened `/job 1091` after the singular qualification-heading fix and
  reported Technical 42 while interview risk remained `н/д`. The detail route
  gave Technical Score the decoded Greenhouse text, but Recommendation v2
  independently analyzed the stored encoded HTML.
- `score_job` now passes its normalized technical description into
  Recommendation v2. The regression reproduces the saved encoded HTML and
  verifies Technical 42 and interview risk 58.
- Local unit suite: 245 passed, 3 PostgreSQL tests skipped. Full isolated
  PostgreSQL suite: 248 passed, 68.36% branch coverage. Compileall and
  `git diff --check` passed. Commit `8a583c7` passed push CI `38151840822` and
  PR CI `38151843490`.
- The safe updater deployed the candidate to Compose project `repo`; source and
  runtime report 3.5.7 and PostgreSQL is healthy. Startup `scan_all` completed
  from 15:35:45 to 15:38:13 UTC. The five-minute log check found no source
  errors, SSL failures, timeouts, or tracebacks. HH's API returned 403 and its
  normal public web fallback succeeded.
- At this entry's timestamp, owner verification was still pending; the owner
  later confirmed the corrected values as recorded above. `main` and the formal
  release/tag remain v3.5.6; PR #18 is a draft. No merge, tag, release, schema
  migration, credential or volume change was made.

## 2026-10-11 — Lineate singular qualification heading
- Owner's latest `/job 1091` card still showed Technical 100 and interview
  risk `н/д`. Runtime inspection found that the saved Greenhouse description
  says `Necessary Qualification` (singular), while the prior parser only
  handled the plural form.
- Commit `e978d07` recognizes singular and plural necessary/required/minimum/
  essential qualification headings. Regression tests cover Greenhouse HTML
  entity decoding, required technical skills, and interview-risk scoring.
- Local suite: 245 passed, 3 PostgreSQL tests skipped. Full isolated
  PostgreSQL suite: 248 passed, 68.36% branch coverage. Compile and
  `git diff --check` passed. Push CI `38151153964` and PR CI `38151157085`
  passed.
- The safe updater deployed source/runtime 3.5.7 to Compose project `repo` at
  18:25:57 Moscow time; PostgreSQL is healthy. Startup scan completed at
  15:28:27 UTC. Greenhouse, EURES, HR.ge, and Job Bank requests in the
  inspected log window returned HTTP 200. HH API 403 fell back to public web
  search; no source errors, SSL errors, timeouts, or tracebacks appeared.
- At this stage, Telegram review remained pending; the owner later confirmed
  the recalculated values, as recorded in the newest log entry above. Stable
  `main` and formal release/tag remain v3.5.6; PR #18 is still a draft. No
  merge or v3.5.7 tag/release was made.

## 2026-10-11 — Lineate experience and technical evidence follow-up
- The official Lineate posting lists 3+ years Linux system administration,
  2+ years production AWS, Windows administration, AWS Databricks familiarity,
  and a 24/7 shift. The earlier section-heading fix exposed its hard technical
  requirements, but the general experience extractor still missed the
  `Minimum 3 years` wording and Windows/Databricks were absent from the evidence
  vocabulary.
- Commit `678ddfc` recognizes `Minimum N years` and `At least N years`, adds
  Windows and Databricks to the technical comparison vocabulary, and tests the
  required-skill and experience-fit behavior. These signals identify posting
  requirements; they do not invent candidate experience or separately assert
  AWS years from unrelated facts.
- Full isolated PostgreSQL suite: 247 passed, 68.36% branch coverage. Compile
  and `git diff --check` pass. The commit is pushed and passed push CI
  `38150088881` and PR CI `38150092577`. Docs commit `664c559` passed push CI
  `38150288518` and PR CI `38150292566`. The safe updater deployed the candidate
  to Compose project `repo`; startup `scan_all` ran from 15:13:24 to 15:15:48
  UTC and completed successfully. The log filter found the expected HH API 403
  and successful public fallback, with no source errors, SSL errors, timeouts
  or tracebacks. At that stage the owner was asked to review `/job 1091`; the
  later acceptance is recorded at the top of this log.

## 2026-10-11 — Required qualification scoring for Lineate
- The official Lineate listing uses `Necessary Qualifications` for hard
  requirements, including 3+ years of Linux system administration, 2+ years of
  production AWS, and a 24/7 shift schedule. The previous requirement parser did
  not recognize that section heading, so the Technical score used a fallback
  based on role and keyword overlap while interview risk showed `н/д`.
- Added common English required-qualification headings to the deterministic
  section parser. Required Linux/AWS/Kubernetes signals now feed Technical
  Score v2 and Recommendation v2 interview-risk evidence. Missing candidate
  facts remain unknown rather than being treated as confirmed experience.
- Regression tests cover section classification, the technical score, and the
  interview-risk breakdown. Full isolated PostgreSQL suite: 246 passed, 68.29%
  branch coverage; compileall and `git diff --check` pass. Commit `7a6901d` was
  pushed; push CI `38149543660` and PR CI `38149546515` passed.
- The safe updater applied `7a6901d` to Compose project `repo`; source/runtime
  is 3.5.7, app polling and PostgreSQL are healthy. The post-deploy startup scan
  ran from 15:02:28 to 15:04:57 UTC and completed successfully. HH's API
  returned 403 before the public web fallback succeeded; Greenhouse, EURES,
  HR.ge, Job Bank, Arbeitnow and Remote OK requests shown in the inspected logs
  returned HTTP 200, and no source error appeared in the scan tail. At that
  stage the owner had not yet reviewed `/job 1091`; the later 18:42 acceptance
  is recorded at the top of this log.
- PR #18 remains open and draft against `main`; stable `main` and the latest
  formal release/tag remain v3.5.6. No merge or v3.5.7 release was made.

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
## 2026-10-12 — Resumed candidate verification and regression fixes

Resumed the saved v3.5.7 worktree without discarding prior changes. Added
explicit tri-state employer support evidence so incidental mentions,
requirements, conditions, and serialized metadata do not become offers or
refusals; shared refusals apply to each named component while independent
offers remain distinct. Salary scoring now compares explicitly annual amounts
to monthly profile floors without rewriting source pay, and displays known
salary periods. Technical Staff seniority excludes ordinary service-staff
titles while retaining technical Staff roles.

The scan dashboard now resets stale completion fields at the start of a new
manual scan. Source discovery errors remain isolated, and a failing source
does not prevent successful source results from ingestion. Remotive's
persistent cache retains the original fetch age across restarts and manual
refreshes. Himalayas timezone restrictions from the public provider are shown
as source claims in vacancy details, with country-level hiring still requiring
employer confirmation.

Verification on the resumed worktree: local pytest **424 passed, 3 skipped**;
full isolated PostgreSQL suite **427 passed**, branch coverage **73.22%**
(55% gate); `python -m compileall -q app tests` and `git diff --check` pass.
The isolated test PostgreSQL is separate and healthy. Production Compose
`repo` is currently stopped (`Exited (0)`); no rebuild or startup scan has yet
been performed from this resumed candidate. PR #18 is open/draft at
`d445c87`; these worktree changes are not published. Preserve PostgreSQL and
storage volumes when rebuilding. Telegram acceptance for the scoped list and
detail controls remains pending.

The v3.5.2 milestones and v3.5.3 Fast Scan & Scan Dashboard remain cumulative
features in v3.5.6; no retroactive tags are planned. Open v3.5.7 work remains
useful Relocation-first coverage and live acceptance. The owner export was
handled separately outside Git; no private candidate information was copied
into this repository.
# 2026-10-13 — Retry transient public HeadHunter search failures

The owner suggested that a recent `ConnectError` could coincide with Yandex
data-center outages. The current Compose log confirms the failure arose during
TLS connection setup for `hh.ru` public-web search. Yandex's Oct 9 statement
confirms damage to its Sasovo and Kaluga data centers; this establishes a
plausible network context but does not prove a direct HH/Yandex dependency.
References: [Yandex's data-center update](https://www.yandex.com/company/news/2026-10-09)
and [Yandex Cloud status dashboard](https://status.yandex.cloud/ru/).

Added one retry after `httpx.TransportError` for the public HH API search and
public web-search request paths. HTTP status responses, including the API's
403 fallback trigger, and CAPTCHA detection are untouched. No private
applicant endpoint behavior changed. Regressions exercise each transport path.

Verification: 13 targeted tests; full local suite 441 passed / 3 skipped;
isolated PostgreSQL suite 444 passed; compileall, secret scan and
`git diff --check` passed. Committed as `b427e96`. Compose `repo` was rebuilt
at 00:23 Moscow without replacing volumes. Runtime reports 3.5.7; PostgreSQL
is healthy. Startup `scan_all` completed at 00:25 Moscow. Logs show HH API 403
fallback, a single `ConnectError`, the bounded retry, subsequent HTTP 200
public-web requests, and successful scan completion. Leave owner Telegram
acceptance of relocation lists and the Canonical technical-risk card open.
## 2026-10-14 — atomic resume import and retry

Moved imported resume plus proposed Candidate Facts into one repository
transaction. The callback retains its claimed one-time preview after a failed
save so the user can retry; a completed transaction remains protected by the
resume fingerprint duplicate check. A PostgreSQL integration regression forces
a fact-column failure, verifies no resume was left behind, then retries the
same fingerprint successfully. Verification: candidate-import tests 4 passed;
repository integration tests 3 passed on the isolated PostgreSQL database;
compileall and diff check passed. No production or external action occurred.
Per-conflict ADD/UPDATE/KEEP remains open.

## 2026-10-14 — atomic resume import and retry

Moved imported resume plus proposed Candidate Facts into one repository
transaction. The callback retains its claimed one-time preview after a failed
save so the user can retry; a completed transaction remains protected by the
resume fingerprint duplicate check. A PostgreSQL integration regression forces
a fact-column failure, verifies no resume was left behind, then retries the
same fingerprint successfully. Verification: candidate-import tests 4 passed;
repository integration tests 3 passed on the isolated PostgreSQL database;
compileall and diff check passed. No production or external action occurred.
Per-conflict ADD/UPDATE/KEEP remains open.
## 2026-10-14 — EURES partial failure counts

Added request-level partial-failure counts for EURES query and detail errors;
retained successful vacancies and the existing bounded retry behavior. Counts
are carried through cache entries and per-profile/source aggregation, with a
cache regression ensuring Career-first plus Relocation-first does not count
one failed request twice. `/scan` completion and `/scanstatus` now show the
count. Combined candidate-import, isolated repository, EURES, scan-isolation
and Telegram progress tests: 46 passed; compileall and `git diff --check`
passed. No live endpoint was contacted.
## 2026-10-14 — isolated DB gate and explicit alternative pair

Preserved the pre-existing dirty worktree and two untracked owner proposals.
Started only `docker-compose.test.yml` as project `job-agent-tests`; its tmpfs
PostgreSQL on localhost 55432 is separate from production. Baseline unit
847 passed/4 skipped; isolated suite 851 passed. Added explicit two-skill
required and preferred `or/или` pair recognition and maximum fact weight for
one scoring unit; four regressions cover both weights, conservative exclusions
and Telegram explanation. Final isolated suite 855 passed, focused matching
54 passed; compileall, `git diff --check` and staged/worktree/history secret
scan passed.

No production DB/runtime, Git publication or external source request.
`codex-cli 0.162.1` local Main default is `gpt-6-sol/medium`, while AGENTS
states intended `gpt-6.1-sol/medium`. Fast/Deep role TOMLs specify Luna/low
and 6.1 Sol/high. No actual session routing/usage meter was available, so
automatic switches and quota savings are not claimed. Current edits remain
unstaged pending review of the existing large dirty tree.
## 2026-10-14 — routing audit, one Scout task, and fit follow-up

Verified `~/.codex/config.toml` and current session `turn_context` both say
Main `gpt-6-sol/medium`. One read-only `job_scout` inspected Greenhouse URL
handling; its actual own turn was `gpt-6-luna/low`. It incorrectly claimed an
SSRF redirect: installed HTTPX 0.28.1 has `follow_redirects=False` by default,
and the listing URL is stored rather than fetched. No source code changed on
that report. Scout thread usage was 83,803 total tokens, 56,576 cached input;
no counterfactual or quota meter proves savings. AGENTS/AI_INSTRUCTIONS now
prefer self-contained isolated context for justified narrow Scout calls. Deep
was not started and no model config was changed.
Then reproduced `Requirements: Linux or Windows. Docker.` losing the explicit
choice because the second sentence shared a line. Alternative detection now
splits punctuated clauses while preserving independent/repeated requirements.
Then reproduced a preferred `Linux or Windows` pair still grouped after Linux
became independently required; compare groups with final importance before
display or scoring. Focused matching 56 passed, full isolated PostgreSQL 857
passed, compileall and secret scan passed. No runtime, production DB or
publication action.
## 2026-10-14 — explicit language and mobility evidence

Implemented a bounded CEFR parser for English/Russian vacancy phrases. It
requires one unambiguous A1–C2 token near the English-language phrase; B1–B2,
“fluent” and B2B false positives remain unknown. Vacancy comparison loads the
matched candidate profile and renders meets/below/unknown separately from the
technical score. Added `/english` view/set/clear and repository persistence.
This exposed a confirmed default mismatch: generic profile creation hard-coded
B2 while the tracked owner template separates general B1 from technical-reading
B2. Generic defaults are now unknown; personalized fresh bootstrap passes B1.
Existing rows are not rewritten.

Then exposed existing conservative support evidence in foreign vacancy cards:
visa sponsorship, relocation, work-permit assistance and explicit prerequisite
authorization are separate. Missing support stays “не подтверждено”, and the
card says this is not personal legal eligibility. No scoring/filter change.
Focused language/comparison 32 and mobility/support 87 passed. Full isolated
PostgreSQL passed at 863 after language and 865 after mobility; compileall,
diff and secret checks passed at the second gate. Final documented gate follows.
No production/runtime/publication action.
## 2026-10-15 — salary reference wording

Revisited the roadmap's confirmed `/salary minimum` wording gap. `/salary` now
explains that the monthly minimum affects scoring only for structured vacancy
salary and does not hide vacancies; amounts found only in text are not compared.
`/settings` calls it an evaluation reference rather than a filter. A regression
covers both views. Full isolated PostgreSQL: 866 passed; compileall and secret
scan passed. Strict salary-floor policy remains a separate owner decision.

## 2026-10-15 — CEFR requirement wording

CEFR comparison now classifies explicit required/preferred cues separately;
missing, contradictory and negated cues remain unspecified. The vacancy view
does not frame an unqualified CEFR mention as mandatory. Comparison remains
evidence-only and does not affect scoring. Focused language/comparison: 22 passed.
Full isolated PostgreSQL suite: 867 passed; compileall, diff-check and secret
scan passed.

## 2026-10-15 — line-wrapped alternative requirements

Extended conservative alternative extraction for a two-skill `or/или` choice
whose connector wraps to an adjacent line. Other independent skills remain
independent, and repeated skill mentions leave the choice ungrouped. Focused
comparison/matching: 43 passed; isolated PostgreSQL: 869 passed. Compileall and
diff-check passed. No scoring weights or thresholds changed.

## 2026-10-15 — opt-in strict salary floor

Added an OFF-by-default strict salary floor and a /salary strict on|off
setting for both active search directions. Filter exclusions require a
structured same-currency value, supported monthly/yearly period and an upper
bound below the configured minimum. Unknown and incomplete evidence stays
eligible. Focused salary/preferences tests: 52 passed; full isolated PostgreSQL
suite: 873 passed. Compileall, diff-check and secret scan passed. Provider
tax-basis remains a review item.

## 2026-10-15 — recoverable version snapshot

Verified the current feature branch at `37633fc` (65 commits ahead of its
tracked origin), with VERSION 3.5.7 and two untracked owner proposal files.
Refreshed HANDOFF with the exact verification/checkpoint history and preserved
the proposals outside Git. Dedicated local and GitHub backup branch
`backup/v3.5.7-20261015` points to the verified snapshot; no release, tag, merge
or deployment is involved.

## 2026-10-15 — Candidate Fact traceability

Vacancy `/compare` now cites the strongest matched Candidate Fact ID and its
provenance label beside each skill, and points to `/facts` and `/fact` for
review/correction. Unknown or missing skills remain uncited. Provenance output
is HTML-escaped; scoring is unchanged. Focused comparison suite: 23 passed;
full isolated PostgreSQL suite: 879 passed. Compileall, diff-check and secret
scan passed.

## 2026-10-15 — read-only vacancy-to-resume diff

Added `/resumediff <vacancy_id> [resume_id]`, which classifies recognized
vacancy skills by appearance in the chosen saved resume and active Candidate
Facts. It exposes only a checklist and does not produce or edit claims. Resume
IDs are looked up inside the authorized match profile. Fixed confirmed
undefined error diagnostic references in `/job`, `/compare`, and the compare
callback. Focused suites: 47 passed; full isolated PostgreSQL: 884 passed.

## 2026-10-15 — reviewed application package preview

Extended `/prepare` to return a selected-resume/Candidate Fact checklist with
the existing grounded cover-letter draft and source link. Review flags cover
skills found only in the CV and recognized job requirements missing from both
CV and facts. The link renderer accepts only credential-free HTTP(S) URLs and
the preview stays within Telegram's message limit. No submit/status write was
added. Focused tests: 28 passed; full isolated PostgreSQL: 888 passed.

## 2026-10-15 — persisted draft versions and manual application status

The prepare callback now persists each cover-letter draft as a separate
`Application` row, linked to its selected resume and source vacancy, and marks
the match `prepared`. `/applications` displays the user's saved records;
`/application <id> <status>` changes only an allowlisted, user-owned manual
status. Integration tests verify stored text, status transitions and isolation
from another user. Existing schema reused; no migration or outbound action.
Full isolated PostgreSQL suite: 890 passed.

## 2026-10-15 — append-only application status history

Schema v5 adds an additive `application_status_events` table. Initial prepared
status and real manual transitions append events; owner-scoped `/application
<id> history` reads them in order. Repeating the current status creates no
duplicate event. Isolated PostgreSQL integration verifies the migration, event
chronology, ownership and updates. Full suite: 892 passed; focused: 40 passed.

## 2026-10-15 — resume snapshot and explicit package export

Additive schema v6 stores the selected local resume-text snapshot and optional
external HH resume ID on Application. Prepared and HH flows populate these
along with the saved cover letter. `/application <id> export` performs
user-scoped lookup and emits the snapshot, letter and vacancy metadata as a
bounded UTF-8 text document on explicit command; records predating v6 disclose
that their resume snapshot is unavailable. Original-format export is not
implemented. Focused tests: 44 passed; full isolated PostgreSQL suite: 896.

## 2026-10-15 — Interview Agent troubleshooting practice

Added `/interview <vacancy_id> [career|relocation]`, which maps recognized job
requirements to at most five curated troubleshooting prompts, tasks and
checklists. Mandatory requirements precede preferred ones, and each item shows
the stored Candidate Fact type. No model/API request, persisted answer,
prediction or candidate score is involved. Focused tests: 29 passed; full
isolated PostgreSQL suite: 900 passed.

## 2026-10-15 — Interview Agent DNS/TLS/security coverage

Extended the technical vocabulary with DNS, TLS and explicit Security
Operations aliases and added corresponding practice scenarios. Prompts focus on
resolver/TTL diagnosis, certificate chain/SNI verification and proportionate
incident response preserving logs. No broad generic security inference.
Focused fit/scoring/interview tests: 52 passed; full isolated PostgreSQL: 901.

## 2026-10-15 — strict salary filter requires a known period

Removed the strict-floor fallback that treated any missing `salary_period` as
monthly. Values from adapters without explicit period evidence remain eligible;
known monthly and annual comparisons are unchanged. Focused salary/scoring
tests: 66 passed; full isolated PostgreSQL suite: 902 passed.

## 2026-10-15 — disclose unknown salary-period behavior

Updated `/salary`, the strict-toggle response and `/settings` to explicitly say
that a missing/unsupported period is not compared by the strict floor and stays
visible. Focused command/filter tests: 41 passed; full isolated PostgreSQL:
902 passed.

## 2026-10-15 — legacy application migration verification

Migration v6 seeds one status-history event for each preexisting application
without events, preserving only the current recorded status and original
created_at. Added a real PostgreSQL v4-to-v6 migration test covering the table,
columns, and legacy row; no prior transition history is invented. Full isolated
suite: 903 passed.

## 2026-10-15 — recruiter draft failure fallback

HH inbox handling now degrades model-generation errors to an empty draft and
manual owner alert; explicitly enabled auto-send errors preserve the draft and
notify the owner for manual follow-up. Only exception class is logged. Auto
reply defaults OFF. Focused private-HH suite: 9 passed; full isolated
PostgreSQL: 905 passed.
## 2026-10-15 — scoped `/prepare` command

Completed the previously button-only Application Package entry point as
`/prepare <vacancy_id> [career|relocation]`. The handler requires an owned
match, resolves optional scope against active user searches, and reuses the
same package snapshot/status path as the callback. Added tests for both scopes,
unmatched vacancies, unavailable scopes and sanitized errors. Focused tests:
31 passed; full isolated PostgreSQL suite: 953 passed. The first DB attempt
found the isolated container lacked its configured localhost port; the
test-only container was recreated with the declared port mapping and rerun.
No production service or database was used.
## 2026-10-15 — disclose unrecognized requirements in package review

An empty Candidate Fit diff previously rendered as “no additional
discrepancies” even when the supported skill vocabulary had recognized nothing.
The package preview now discloses that state and directs manual review of the
full posting. Focused package tests: 20 passed.
## 2026-10-15 — do not infer a salary period in match scoring

Fixed a source-agnostic assumption that a structured salary with no period was
monthly. Monthly profile references now compare only against explicit
monthly/per-month or annual/yearly/per-year values; unsupported or missing
periods remain reviewable and receive the neutral 58 salary score. Existing
fixtures that intend monthly semantics now state that period explicitly.
Focused salary, technical-score, personal-scope and recommendation tests: 61
passed.
## 2026-10-15 — refresh repeated source postings safely

PostgreSQL regressions reproduced stale Job fields on repeat discovery and
covered competing cross-source inserts. `upsert_job` now serializes source and
canonical natural keys with transaction advisory locks; existing refs/Jobs are
row-locked before refreshing. Only supplied nonempty values replace Job data,
so unknown fields do not erase evidence. Current raw provider data is retained
with the verified details cache; source key and first-seen timestamp remain
stable. A complete new fingerprint is adopted only if it is unclaimed; the
code does not merge conflicting Jobs or reassign their matches. Application
snapshots are unchanged. Focused HH-cache and database regressions passed; full
isolated PostgreSQL suite: 957 passed.
## 2026-10-15 — nested Candidate Fit alternatives

Extended parenthesis scanning to keep a balanced outer expression intact.
Unambiguous nested flat choices such as `Linux and (Docker or (Kubernetes or
ArgoCD))` now become one alternative group; the independent Linux requirement
stays separate. Mixed nested AND/OR and skills repeated elsewhere in the same
section are not promoted to alternatives. Scoring and resume-coverage
regressions pass; focused fit/resume/score tests: 79 passed.
## 2026-10-15 — preserve timezone evidence in vacancy dates

Vacancy detail rendering previously removed the offset from timezone-aware
ISO dates, making them look like local wall-clock time. It now converts them
to UTC with an explicit label; date-only values remain dates, and naive
date-times disclose an unknown timezone. Focused detail/source tests: 68
passed; full isolated PostgreSQL suite: 964 passed.
## 2026-10-15 — add OpenShift to Fit and Interview practice

Added a distinct OpenShift Candidate Fact skill alias and a deterministic
`/interview` exercise for image rollout/readiness/Route troubleshooting. The
exercise discourages broad SCC/RBAC changes and uses no model call. Focused
fit/interview/resume/score tests: 87 passed; full isolated PostgreSQL suite:
967 passed.
## 2026-10-15 — isolate cover-letter instructions from vacancy content

Moved cover-letter rules into the Responses API `instructions` field and
passed Candidate Facts, résumé metadata and vacancy fields as JSON input.
Explicitly treat all input values as data and disallow embedded instructions,
unfounded candidate claims or external actions. The output remains an
unverified draft for user review. Focused tests: 5 passed; isolated PostgreSQL
suite: 968 passed.
## 2026-10-15 — isolate recruiter instructions from message content

Moved recruiter response rules to the Responses API `instructions` field and
passed Candidate Facts, prior context and the latest question as JSON. Inputs
cannot override the factual constraints or sensitive-topic human-review rule.
Default auto-reply remains OFF. Focused recruiter/private-HH tests: 16 passed;
full isolated PostgreSQL: 969 passed.
# 2026-10-15 — source-scoped Relocation Evidence v1

Persisted a versioned evidence packet in each source ref at upsert time and
rendered provenance in vacancy details. It records the source-reported country
and independently tracks hiring restrictions, existing work authorization,
visa sponsorship, relocation support, and observed housing/language/start
phrases. Each signal has source identity/URL, capture time, excerpt when
observed and categorical confidence. Missing conditions remain unknown;
text snippets for housing/language/start do not assert a benefit or mandate.
Fixtures are synthetic and marked as such; Candidate Facts and scoring are
untouched. Regression also fixed “No relocation details” to remain unknown.
Focused tests: 6 passed, 1 PostgreSQL test passed; full isolated PostgreSQL:
973 passed.

## 2026-10-15 — classify housing and language evidence

Housing becomes confirmed provided/refused only with explicit wording.
Language evidence retains required/preferred/unspecified status; explicit
English CEFR is a separate value. Vacancy detail cards display those
distinctions and excerpts. Ambiguous conditions remain observed/unknown.
Focused relocation/language/detail suite: 85 passed; full isolated
PostgreSQL: 974 passed.

## 2026-10-15 — distinguish citizenship and residence restrictions

Explicit hiring-scope excerpts now retain a bounded category for citizenship
versus residence/location restrictions, and the detail card states that the
category reflects source text only. No legal eligibility inference is made.
Focused evidence/detail tests: 41 passed; isolated PostgreSQL: 975 passed.

## 2026-10-15 — retain source work-location excerpt

Work-country evidence now uses the adapter's structured source location/country
text as its supporting excerpt when available, and details show it beside the
normalized code. It does not infer a country from arbitrary posting prose.
Focused tests: 41 passed; isolated PostgreSQL: 975 passed.

## 2026-10-15 — freeze Relocation Evidence in Application Package

Prepared snapshots now deep-copy the selected source's evidence packet,
including source identity, excerpts, confidence and capture time. The Package
export reads this saved evidence after later source refresh; HH snapshots share
the path. No database migration. Focused package/service/HH tests: 20 passed;
repeat-source PostgreSQL regression passed; full isolated PostgreSQL: 976.

## 2026-10-15 — explicit work-authorization non-requirement

Prior work authorization now distinguishes explicit required/not-required
statements from missing evidence. Contradictory statements remain unknown and
are tagged as conflicting. Focused tests: 82 passed; isolated PostgreSQL:
977 passed.

## 2026-10-15 — multiple per-language source conditions

Extracted multiple supported languages from a posting independently, each
with requirement status and excerpt. Conflicting explicit required/preferred
statements stay reviewable as conflicting, and English CEFR remains separate.
Focused tests: 87 passed; full isolated PostgreSQL: 978 passed.

## 2026-10-15 — classify source start-timing phrases

Start-timing evidence retains the original quote and identifies immediate,
relative-window, stated-date, notice-period or negotiable phrases. This does
not assess candidate availability. Focused tests: 44 passed; isolated
PostgreSQL: 979 passed.

## 2026-10-15 — keep support-component ambiguity unknown

Source evidence no longer assigns a sentence-level support refusal to a
different visa/relocation component when focused parsing disagrees. It retains
unknown status and an excerpt; scoring behavior is untouched. Focused tests:
46 passed; isolated PostgreSQL: 981 passed.

## 2026-10-15 — synthetic German relocation evidence

Added explicit German fixture coverage for residence, authorization, housing,
language and start timing. It caught and fixed a `Deutschland`/`Deutsch` false
match. Focused tests: 87 passed; isolated PostgreSQL: 982 passed.

## 2026-10-15 — preserve explicit non-required Candidate Fit status

Reproduced “no Kubernetes experience required” being classified as a
must-have under Requirements. Added narrow per-clause negation handling;
separate skills retain their own importance. Focused Fit/score tests: 64
passed; isolated PostgreSQL: 984 passed.

## 2026-10-15 — evidence refresh and immutable package regression

Extended repeat-source PostgreSQL coverage to check that source location
evidence updates while the prepared package retains its original evidence.
Targeted integration test: 1 passed; full suite at parent checkpoint: 984.

## 2026-10-15 — disclose missing historical mobility snapshots

Application Package preview and export now clearly say when older records
lack a structured source-evidence snapshot; current data is not backfilled.
Focused package tests: 12 passed; full isolated PostgreSQL: 984 passed.

## 2026-10-15 — respect skill-specific preferred language

Within a broad Requirements heading, supported direct English/Russian plus
phrasing now classifies that skill as preferred, without downgrading distinct
mandatory skills or changing cross-section required priority. Focused tests:
66 passed; isolated PostgreSQL: 986 passed.

## 2026-10-15 — short explicit non-required skill wording

Candidate Fit now also recognizes “No Kubernetes required” as not mandatory
under a Requirements heading. Focused tests: 67 passed; PostgreSQL: 987 passed.

## 2026-10-15 — bound evidence-rich vacancy detail cards

A synthetic long description with all mobility fields reproduced a 6467-unit
Telegram card. Rendering now caps UTF-16 length at 3900 by trimming the
description only; source evidence, score and link remain. Full isolated
PostgreSQL: 988 passed.

## 2026-10-15 — Russian accommodation evidence

Explicit Russian statements that accommodation is or is not provided now
produce attributed evidence; bare mentions stay unknown. Full isolated
PostgreSQL: 988 passed.
