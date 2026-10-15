# Codex Brief

## 2026-10-15 — test source evidence refresh against immutable package

Isolated PostgreSQL regression proves a repeated source ID updates its
location excerpt while an already prepared package retains the earlier
evidence. Targeted DB test: 1 passed; prior full suite: 984 passed.

## 2026-10-15 — keep explicit non-required skills out of must-have scoring

Candidate Fit now recognizes narrow “no Kubernetes experience required” and
“Kubernetes is not required” phrases under a Requirements heading. That skill
stays unknown while separate positive requirements retain their status.
Focused Fit/score tests: 64 passed; full isolated PostgreSQL: 984 passed.

## 2026-10-15 — add synthetic German relocation evidence

Added German source-text fixture coverage for residence restrictions,
authorization, accommodation, language preference and start timing. It exposed
and fixed `Deutschland` being misread as `Deutsch`. Focused tests: 87 passed;
full isolated PostgreSQL: 982 passed.

## 2026-10-15 — keep support-component ambiguity unknown

Relocation Evidence now refuses to copy an ambiguous legacy parser result when
a denial for one support component may have contaminated another in the same
sentence. Conflicting or component-mismatched support wording stays unknown
with an excerpt for review; the scoring parser itself is unchanged. Focused
evidence/detail tests: 46 passed; full isolated PostgreSQL: 981 passed.

## 2026-10-15 — classify explicit start timing

Start timing observations now distinguish immediate availability, relative
windows, stated dates, notice periods and negotiable timing while retaining the
original excerpt. This describes vacancy wording and does not assess candidate
availability. Focused evidence/detail tests: 44 passed; full isolated
PostgreSQL: 979 passed.

## 2026-10-15 — retain multiple language conditions

Relocation Evidence now extracts multiple supported languages independently
within one posting, each with its requirement classification and excerpt.
Conflicting explicit statuses for the same language stay marked conflicting;
English CEFR remains attached to its own observation. Detail cards can show
multiple conditions. Synthetic evidence/detail tests: 47 passed; full isolated
PostgreSQL: 978 passed.

## 2026-10-15 — distinguish explicit work-authorization non-requirement

Relocation Evidence records an explicit “work permit not required” statement
as confirmed false; absent text remains unknown, and contradictory positive /
negative wording is kept unknown with `conflicting_text` confidence. Focused
evidence/support/detail tests: 82 passed; full isolated PostgreSQL: 977 passed.

## 2026-10-15 — freeze mobility evidence in Application Package

Prepared vacancy snapshots now deep-copy the source-scoped Relocation Evidence
from the selected `JobSourceRef`. Repeated source refreshes cannot rewrite
evidence already saved with an Application Package; `/application … export`
includes the saved evidence object. Preparation preview notes the evidence
capture time. No schema change. Focused package/service tests: 20 passed;
repeat-refresh PostgreSQL regression: 1 passed; full isolated PostgreSQL: 976.

## 2026-10-15 — retain the source location excerpt

Work-country evidence now preserves the source adapter's structured
`source_location`/`source_country` text when present, beside the normalized
country code. Detail cards show both, making the raw supporting location
reviewable. Synthetic fixture/detail tests: 41 passed; full isolated
PostgreSQL: 975 passed.

## 2026-10-15 — distinguish citizenship and residence restrictions

Hiring restriction evidence now labels explicit citizenship scope separately
from current-residence/location scope and displays the matching source excerpt.
This records what the posting says without inferring the applicant's legal
eligibility. Focused restriction/detail tests: 41 passed; full isolated
PostgreSQL: 975 passed.

## 2026-10-15 — classify explicit housing and language conditions

Relocation Evidence now distinguishes housing explicitly provided/refused from
mere mentions. Language excerpts distinguish required, preferred and
unspecified; an explicit English CEFR level is retained independently. Vacancy
cards display these classifications with their source excerpt/provenance.
Ambiguous phrases remain unknown or observed, not a promise or hiring mandate.
Focused relocation/language/detail tests: 84 passed; full isolated PostgreSQL:
974 passed.

## 2026-10-15 — source-scoped Relocation Evidence v1

Each ingested source posting now stores a versioned mobility evidence packet
in its own `JobSourceRef.raw`: source-reported work country, explicit
citizenship/residence restriction excerpts, prior work authorization, visa
sponsorship, relocation support, and observed housing/language/start-timing
text. Every field records source ID/URL, capture time and bounded confidence;
unobserved values remain `unknown` with no fabricated excerpt. Vacancy detail
cards disclose the per-field provenance. This does not change scoring or
Candidate Facts and makes no legal eligibility conclusion. Synthetic-only
regressions cover evidence and unknown behavior; full isolated PostgreSQL:
973 passed. The parser also keeps “no relocation details” unknown, not a
confirmed employer refusal.

## 2026-10-15 — isolate recruiter instructions from message content

Recruiter drafting now supplies fixed developer instructions separately from
JSON-encoded Candidate Facts, conversation context and question. The model is
told these fields are untrusted data and cannot override factual/sensitive-topic
rules. Auto-reply remains OFF by default; focused recruiter/private-HH tests:
16 passed; full isolated PostgreSQL suite: 969 passed.

## 2026-10-15 — isolate cover-letter instructions from vacancy content

Cover-letter generation now sends fixed developer instructions separately
from JSON-encoded Candidate Facts, résumé metadata and vacancy content. The
instructions treat those fields as data, reject embedded instructions and
restrict candidate claims to facts. Manual review remains required. Focused
LLM tests: 5 passed; full isolated PostgreSQL suite: 968 passed.

## 2026-10-15 — add OpenShift to Fit and Interview practice

Candidate Fit recognizes OpenShift and “Red Hat OpenShift” as a distinct
technical requirement. `/interview` has a curated rollout exercise covering
image digest, readiness, service/Route and safe rollback without broadening
SCC or RBAC. Focused fit/interview tests: 87 passed; full isolated PostgreSQL:
967 passed.

## 2026-10-15 — preserve timezone evidence in vacancy dates

Vacancy detail cards now render timezone-aware publication timestamps in UTC,
keep date-only values as dates, and label timezone-naive date-times as lacking
source timezone evidence. They no longer make an aware timestamp look like
local time. Focused source/detail tests: 68 passed; full isolated PostgreSQL:
964 passed.

## 2026-10-15 — nested Candidate Fit alternatives

Candidate Fit now groups a nested flat choice such as `Linux and (Docker or
(Kubernetes or ArgoCD))` into one Docker/Kubernetes/ArgoCD alternative while
keeping Linux independent. Resume coverage uses that same group. Mixed nested
`and/и` expressions and repeated skill mentions remain ungrouped. Focused
fit/resume/score tests: 79 passed.

## 2026-10-15 — refresh repeated source postings safely

Repeated source IDs now refresh nonempty Job fields and current source raw
data, preserving unknown-but-previously-known Job fields, verified
`details_cache_v1`, source ID/first-seen provenance, and already saved
Application Package snapshots. Transaction advisory locks serialize natural
source/fingerprint keys; row locks serialize existing records. Complete new
fingerprints are adopted only if no other Job owns them. Focused PostgreSQL
regressions cover refresh, cache/provenance preservation, immutable snapshots,
cross-source deduplication and concurrent inserts. Full isolated suite: 957
passed.

## 2026-10-15 — do not infer a salary period in match scoring

Salary ranking no longer treats a missing period as monthly when comparing
structured vacancy pay with a user's monthly reference. Unknown or unsupported
periods remain reviewable and receive a neutral salary score; explicit monthly
and annual periods keep their existing comparison. Focused salary/score tests:
61 passed.

## 2026-10-15 — disclose unrecognized requirements in package review

Application Package preview now says when the supported technical vocabulary
found no requirements and asks the user to inspect the full vacancy. It no
longer presents an empty comparison as evidence that no fit discrepancies
exist. Focused package tests: 20 passed.

## 2026-10-15 — scoped `/prepare` command

Added `/prepare <vacancy_id> [career|relocation]` to create the existing
reviewable Application Package from an owner-scoped match. Explicit scopes
must resolve to an active search profile; missing matches and internal errors
do not expose details. Draft storage and the match's `prepared` status reuse
the callback flow, and users are directed to `/applications` before retrying
after an error. Focused handler tests: 31 passed; isolated PostgreSQL suite:
953 passed.

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

Arbeitnow's numeric `created_at` epoch-seconds values now normalize to UTC ISO
timestamps; malformed values remain unknown. Focused Arbeitnow/detail tests:
46 passed; isolated PostgreSQL suite: 933 passed.

## 2026-10-15 — clarify application status provenance in exports

Application Package exports state that the locally recorded status does not
independently verify receipt by an employer or provider. Focused package and
handler tests: 40 passed; isolated PostgreSQL suite: 929 passed.

## 2026-10-15 — normalize Remotive publication timestamps

Remotive's RSS `pubDate` values are RFC 2822 while its API uses ISO values.
Both are now normalized to UTC ISO timestamps when timezone-aware; malformed
and timezone-less values remain unknown. Focused Remotive tests: 8 passed;
isolated PostgreSQL suite: 929 passed.

## 2026-10-15 — isolated parenthesized skill alternatives

Candidate Fit recognizes an explicit parenthesized choice beside another
requirement, such as `Linux and (Docker or Kubernetes)`: Linux remains
independent and Docker/Kubernetes form one alternative. Repeated skills outside
the group, ambiguous forms, and slash syntax remain ungrouped. Focused tests:
67 passed; isolated PostgreSQL: 928 passed.

## 2026-10-15 — keep extra alternative CV claims reviewable

An OR requirement can be satisfied by one confirmed option, while an additional
CV option in the same group may still be unsupported. `/resumediff` and
`/prepare` now surface those extra CV claims for review. Focused tests: 63;
isolated PostgreSQL: 923 passed.

## 2026-10-15 — recruiter sensitive-context fallback

Recruiter replies now force human review when sensitive topics appear anywhere
in the supplied conversation context, not only the latest message. Added the
missing English `passport` marker and parse JSON boolean strings explicitly.
Focused tests: 13 passed; full isolated PostgreSQL: 921 passed.

## 2026-10-15 — preserve alternatives in resume comparison

`/resumediff` and `/prepare` now treat recognized `or/или` alternatives as one
group. A group is confirmed only when the same option appears in the selected
CV and Candidate Facts; different options are shown as an evidence mismatch
instead of a false gap/confirmation. Focused tests: 61 passed; isolated
PostgreSQL suite: 917 passed.

## 2026-10-15 — tighten salary-period text boundary

Salary-period display now requires the explicit unit immediately after the
currency amount, avoiding unrelated nearby dates such as a review in one
month. Focused salary tests: 83 passed; full isolated PostgreSQL: 914 passed.

## 2026-10-15 — Interview Agent IaC/cloud/observability exercises

Added curated vacancy-specific exercises for Terraform, Ansible, AWS, Grafana
and Helm, including safe plan/state review, idempotency, least privilege,
missing metric samples and rendered-manifest review. No candidate answers are
collected or scored. Focused tests: 31 passed; full isolated PostgreSQL: 913.

## 2026-10-15 — source publication-date field coverage

Per-source scan summaries now show how many discovered vacancies have a
nonempty source publication-date field. This measures field coverage only; it
does not validate dates or label vacancies stale. Focused source tests: 55
passed; full isolated PostgreSQL suite: 912 passed.

## 2026-10-15 — display explicit salary period evidence

Salary text with a nearby explicit period now displays that period beside the
amount. Unknown units remain unnormalized; this is presentation only and does
not change strict filtering. Focused tests: 82 passed; full isolated PostgreSQL
suite: 910 passed.

## 2026-10-15 — include status timeline in application export

`/application <id> export` now includes the saved owner-scoped status history
alongside the exact CV-text snapshot and cover-letter text. Focused tests: 35
passed; full isolated PostgreSQL suite: 905 passed. No migration was needed.

## 2026-10-15 — recruiter draft failure fallback

HH recruiter-message handling now catches model-generation and authorized
auto-send errors, keeps raw exception payloads out of logs, and notifies the
owner to answer manually. Auto-reply remains OFF by default. Focused private-HH
tests: 9 passed; full isolated PostgreSQL suite: 905 passed.

## 2026-10-15 — legacy application migration verification

Added a PostgreSQL regression that simulates an existing v4 schema, runs
migrations v5/v6, and verifies new snapshot fields plus initial status history.
Existing applications receive only their recorded current status at their
original creation time; no past transition history is inferred. Full isolated
suite: 903 passed.

## 2026-10-15 — disclose unknown salary-period behavior

`/salary`, strict-toggle response and `/settings` now explain that the strict
filter compares only structured salary with a known period; unknown periods
stay visible. Focused command/filter tests: 41 passed; full isolated PostgreSQL
suite: 902 passed.

## 2026-10-15 — strict salary filter requires a known period

Fixed a confirmed comparison risk: strict monthly floors no longer assume a
missing `salary_period` means monthly. Structured values without a period remain
eligible for review; explicit monthly/yearly values retain existing behavior.
Focused salary/scoring tests: 66 passed; full isolated PostgreSQL suite: 902.

## 2026-10-15 — Interview Agent DNS/TLS/security coverage

Expanded Candidate Fact vocabulary and practice templates with DNS, TLS and
Security Operations. Scenarios include cache/TTL tracing, certificate chain/SNI
verification, and proportionate incident containment with evidence retention.
Security mentions remain scoped to explicit operations terms. Focused fit,
scoring and interview tests: 52 passed; full isolated PostgreSQL: 901 passed.

## 2026-10-15 — Interview Agent troubleshooting practice

Added `/interview <vacancy_id> [career|relocation]` with up to five curated
Linux, Docker, Kubernetes, Nginx, Networking, PostgreSQL, CI/CD and Prometheus
exercises selected from recognized requirements. Required topics come first;
each displays Candidate Fact type. No LLM call, interview prediction or score.
Focused tests: 29 passed; full isolated PostgreSQL suite: 900 passed.

## 2026-10-15 — resume-content snapshot and explicit package export

Schema v6 stores a local resume-text snapshot and optional external HH resume
ID with each application record. `/application <id> export` returns the saved
cover letter, resume snapshot and vacancy metadata as UTF-8 text after
user-scoped lookup; old rows disclose missing snapshots. The user's request is
required to send the file to Telegram. Focused tests: 44 passed; full isolated
PostgreSQL suite: 896 passed.

## 2026-10-15 — append-only application status history

Schema v5 adds `application_status_events`; prepared drafts and actual manual
status changes append owner-scoped events. `/application <id> history` shows the
timeline, and repeated status values do not create duplicate events. Isolated
PostgreSQL full suite: 892 passed; focused migration/status tests: 40 passed.

## 2026-10-15 — saved draft versions and manual application tracking

The existing applications table now records each user-confirmed prepared
preview's cover-letter text, resume ID, source URL and timestamp. `/applications`
lists records; `/application <id> <status>` applies an allowlisted user-scoped
manual status. It does not send, submit or contact anyone. PostgreSQL integration
covers snapshots, status changes and ownership; full isolated suite: 890 passed.

## 2026-10-15 — reviewed application package preview

Extended existing `/prepare` with a vacancy-to-CV/Candidate Facts checklist,
selected resume, bounded cover-letter draft and safe HTTP(S) source link. The
preview warns about CV-only assertions and missing evidence, and states that it
was not sent. No application state or external action is created. Focused tests:
28 passed; full isolated PostgreSQL suite: 888 passed.

## 2026-10-15 — read-only vacancy-to-resume diff

Added `/resumediff <vacancy_id> [resume_id]` to compare recognized vacancy
skills with the chosen saved CV and active Candidate Facts. It distinguishes
overlap, supported facts missing from the CV, CV mentions absent from Candidate
Facts, and gaps in both. It creates no resume text or claims. Fixed undefined
error diagnostics in `/job`, `/compare`, and the comparison callback. Focused
tests: 47 passed; isolated PostgreSQL suite: 884 passed.

## 2026-10-15 — Candidate Fact traceability

`/compare` links each matched skill to the strongest Candidate Fact ID and its
escaped provenance label, with `/facts` and `/fact` review/edit commands. Missing
skills receive no fact citation and scoring is unchanged. Focused tests: 23
passed; full isolated PostgreSQL suite: 879 passed.

## 2026-10-15 — per-source Relocation-first yield

Per-source scan details show processed, Good, Stretch, filtered and duplicate
counts from the existing per-source ledger, making source yield easier to
compare. No matching/deduplication behavior changed. Source diagnostics tests:
30 passed; full isolated PostgreSQL suite: 878 passed. The personal runtime
database and volumes were not used.

The verified code checkpoint is `9001040`; current feature HEAD at this
handoff refresh is `eb56824`. Local and GitHub backup branch
`backup/v3.5.7-20261015` preserves this snapshot; the two owner
proposal files remain excluded. VERSION remains 3.5.7, and v3.5.6 remains the
latest formal release.

# 2026-10-15 — Candidate/Vacancy multi-option fit

Candidate/Vacancy fit now treats explicit `or/или` chains and Oxford-comma
lists as one scoring choice in a required or preferred section. Comma-only
lists stay independent requirements; ambiguous and repeated options do not
group. Weights and thresholds are unchanged. Focused matching, scoring and
Recommendation v2 tests: 52 passed; the current full local suite: 874 passed,
4 PostgreSQL tests skipped before the final isolated run. The full isolated
PostgreSQL suite passed with 878 tests. Compileall, staged/worktree diff checks
and staged/worktree/history secret scan passed. Local commits now record the
feature and reliability increments; docs checkpoint is next.

## 2026-10-15 — salary reference wording and final verification

Clarified `/salary` and `/settings`: the monthly minimum is a scoring reference,
not a vacancy filter; only structured salary values are compared, while salary
amounts found only in description text remain display evidence. A regression
checks both user-facing views. Full isolated PostgreSQL suite: 866 passed;
compileall and secret scan passed. `git diff --check` passed after removing an
extra trailing blank line in DEVELOPMENT_LOG. No scoring behavior changed.

## 2026-10-15 — line-wrapped skill alternatives

An explicit two-skill `or/или` choice can now span a line break around the
connector. Independent following skills stay separate; repeated skills keep
the clause ungrouped as ambiguous. Focused matching/comparison tests passed
43/43; the full isolated PostgreSQL suite passed 869 tests. No score weights or
thresholds changed. Nested and more complex clauses remain planned.

## 2026-10-15 — opt-in strict salary floor

/salary strict on|off configures both active search tracks; it is OFF by
default. When enabled it excludes only structured salary evidence in the same
currency and a supported monthly/yearly period whose upper bound is below the
configured minimum. Unknown or incomplete values remain eligible. Focused
salary/preferences tests passed 52/52; the full isolated PostgreSQL gate passed
with 873 tests. Compileall, diff-check and secret scan passed. No score weights
changed.

## 2026-10-15 — CEFR requirement wording

Vacancy CEFR comparison now labels a level as required or preferred only when
the posting has an explicit cue; otherwise it reports unspecified. Contradictory
cues and negated requirements remain unspecified. This is display evidence only
and does not affect score. Focused language/comparison tests passed 22/22; full
isolated PostgreSQL passed with 867 tests.

## 2026-10-14 — language fit and mobility evidence

Vacancy comparison now extracts explicit English CEFR evidence and compares it
with the selected profile without changing technical/total scores. Ambiguous
ranges, “fluent” wording and unmapped profile text remain unknown. `/english`
shows, sets or clears A1–C2 (+) values. Fresh personalized bootstrap now uses
tracked general English B1; generic profiles default unknown instead of the old
invented B2, and existing profiles are never rewritten. Foreign vacancy cards
show visa sponsorship, relocation, work-permit help and explicit pre-existing
authorization separately, including honest unknowns and a legal-eligibility
caveat. Focused language/comparison 32 and mobility 87 passed; intermediate
isolated PostgreSQL gates 863 and 865 passed. The final documented full gate
also passed with 865 tests. No score, threshold, production or external action
change.


## 2026-10-14 — verified model routing and sentence alternative

Current Main session log confirms `gpt-6-sol/medium`; local config agrees.
AGENTS now states that fact rather than an unconfigured 6.1 Sol target.
One read-only Scout turn ran on `gpt-6-luna/low`, but its proposed Greenhouse
redirect bug was false: installed HTTPX defaults to no redirect following.
Scout consumed 83,803 total tokens, including 56,576 cached input, after
inheriting full history; total quota savings are unproven. Future narrow Scout
tasks use a self-contained isolated context when justified. Deep was not run.
An explicit `Linux or Windows. Docker.` required line now scores the first
pair as one choice while preserving Docker as separate and repeated Windows
as mandatory. A preferred pair also stops grouping when one skill is separately
required. Focused 56 and isolated PostgreSQL 857 passed; compileall and secret
scan passed. No production/runtime/publication change.


## 2026-10-14 — isolated PostgreSQL and explicit alternatives

Baseline 847 unit/4 skipped and 851 isolated PostgreSQL tests passed against
the separate `job-agent-tests` tmpfs database. An explicit two-skill `or/или`
choice in required or preferred sections contributes one scoring unit with the
stronger confirmed Candidate Fact; repeated or ambiguous skills remain separate.
The comparison view states the detected pair and keeps per-skill evidence.
After the changes, 855 isolated PostgreSQL tests, compileall, diff and secret
scan passed. No production DB, runtime, publication or external action.
Main's local default is `gpt-6-sol/medium`; Fast/Deep role files specify
Luna/low and 6.1 Sol/high. The newer entry above records actual Scout usage.


## 2026-10-14 — required/preferred fit increment

Permanent `AGENTS.md` workflow now directs Main to continue from Git, ROADMAP
and HANDOFF through small verified increments. Flattened vacancy text with
`Requirements: Linux. Nice to have: Docker.` previously marked Docker required
and scored Linux-only commercial evidence 50. Explicit punctuated section
headings now split before classification; Docker remains preferred, and the
existing 85/15 weighting scores that example 85. English/Russian and neutral
section regressions added. A real Devexperts example mentioning Python among
language alternatives is now `unknown`, not an individual must-have: commercial
Linux/Bash/networking evidence scores 100 instead of 75; an independent Python
requirement still wins. This is narrow, not general alternative-group scoring.
No global threshold or eligibility change. PostgreSQL and runtime acceptance
remain separate gates.

## 2026-10-14 — source diagnostics and follow-up completed locally

Legacy error→success `KeyError('found')` reproduced; exact production trace
remains unavailable. Uniform counters/status and per-profile attempt history
now retain failures, partial collection and processing outcomes. Russian typed
notifications are safe, deduplicated per pass, and distinguish response,
network, HTTP and application telemetry. RemoteOK connection budget 30 seconds does not
establish DNS/TLS/proxy/IP-family/blocking cause; no live requests performed.
Scheduled history is persisted separately and `/scanstatus` prefers active
manual work, otherwise the latest scan. Source HTML section is bounded before
escaping (5940-character fixture reproduced overflow). Job Bank preserves
verified jobs after HTTP/schema errors and stops further calls on 403/429.
Eight adapter contract failures are typed response errors; existing partial
Himalayas/SmartRecruiters/Job Bank outcomes and actual bounded retries now
reach the summary/cache. EURES collection observation dedupe is preserved;
cached discovery does not merge independent profile processing failures.
Secret guard now checks staged/worktree/history content without printing
matching values; progress logs and legacy failed stages are sanitized.
Final full unit 844 passed/4skipped; targeted 125 passed. compileall/diff/secret
gates passed. Isolated PostgreSQL blocked by Docker API permissions; no commit
(.git read-only), runtime change or publication. Next: isolated DB gate, then
Candidate/Vacancy required-versus-preferred comparison from the existing code.

HH connection failures count as failed attempts; later cooldown skips count
separately. Recovery retains failed history and marks the source partial.

## 2026-10-14 — safe transport-cause diagnostics

HH connection warnings and persisted skip state now classify typed exception
causes (DNS, TLS/certificate, proxy, timeout, reset/refusal/unreachable). Unknown
causes remain unclassified; IP family and source blocking are not inferred.
Raw TLS/DNS errors now share transport-message sanitization in logs/alerts.
Full local suite: 785 passed / 4 skipped; live HH root cause remains unresolved.

## 2026-10-14 — explicit Candidate Fact conflict choices

Resume import now offers per-overlap ADD/UPDATE/KEEP, defaulting to KEEP.
Selection remains a preview until final confirmation. UPDATE locks/rechecks the
reviewed active fact in the same profile, retains it as inactive history, and
creates an unknown replacement. It never inherits commercial classification.
Unit/behavior tests pass; PostgreSQL replacement/rollback/isolation regressions
are written but remain environment-blocked. Full unit suite: 769 passed / 4 skipped.

## 2026-10-14 — source counter preservation

Source aggregation now preserves vacancy-processing errors from an earlier
profile after a later profile succeeds. EURES failure observations identify
individual discovery attempts: one reused cache is counted once, while distinct
cached discoveries retain their combined failures. Full unit suite: 750 passed /
4 skipped. Current sandbox blocks isolated DB access and Git index writes.

## 2026-10-14 — resume retry and manual HH authorization

Import preview now survives a failed duplicate-check read as well as a failed
atomic save. Manual HH reply setup requires the configured Telegram owner;
stale pending replies belonging to other users are cleared without sending.
Regressions cover denied setup, stale-state cleanup and the owner flow.
Full local suite: 748 passed / 4 skipped. Current sandbox blocks Docker and
localhost sockets, so isolated PostgreSQL could not be rerun in this turn.

## 2026-10-14 — network exception logging

Telegram startup retry and HH chat polling now log exception classes without
raw messages that could contain URLs or parameters. Regression tests reproduced
the leak before the change. Retry/backoff and private-action settings remain.

## 2026-10-14 — dependency floor review

Raised `pypdf` minimum to 6.20.1 after checking its Oct 12 upstream advisory;
the local test venv was upgraded from 6.20.0. Raised `python-multipart` minimum
to 0.0.31, while local 0.0.32 already satisfied it. These are dependency
floors, not a lockfile or proof of the runtime image's installed versions.

## 2026-10-14 — EURES partial response isolation

EURES now continues independent search queries and detail IDs after a single
HTTP status or malformed response, while raising an error when every search
or every detail fails. Transport retries remain bounded; HTTP errors are not
retried. Regression tests cover HTTP, malformed contracts and total failure.

## 2026-10-14 — Job Bank repeat detail work

Read-only runtime logs showed 12 repeated Job Bank detail URLs at five-second
pacing in adjacent scheduled scans. Local code now caches verified detail HTML
for one hour (max 256 entries), while a forced `/scan` refetches it. Targeted
tests cover reuse, forced refresh and expiry. Runtime speed after deployment
is unmeasured; the current runtime was not updated.

## 2026-10-14 — Georgia detail URL boundary

HR.ge and paused JOBS.GE now accept listing-provided detail links only on their
own HTTPS host. A malicious absolute link previously sent the detail client to
another host; both adapters have regressions. No live source query was made.

## 2026-10-14 — resume import callback replay

Concurrent confirmation callbacks now claim one preview token before the first
resume persistence read, so the same resume and proposed facts cannot be
inserted twice by a duplicate Telegram callback. Resume content and selected
proposed facts now persist in one transaction. Failed saves roll back and
restore the preview for retry without re-uploading the document.

## 2026-10-14 — EURES partial-failure visibility

Individual search/detail HTTP, transport and parse failures are counted while
successful vacancies are preserved. Counts survive cache and profile-summary
aggregation and appear in `/scan` and `/scanstatus`; a cache hit does not count
the same request failure twice across search profiles.

## 2026-10-14 — local reliability and security checkpoint

Scheduled scans now continue after one user's scan raises. Telegram candidate
commands and callbacks route only in private chats; selected channel posts remain
available. HH applicant actions require the configured owner profile before any
outbound request. Source transport errors and HH API response bodies no longer
appear in user-facing error text. A failed vacancy no longer prevents later
vacancies from the same successful source from being processed; the source is
marked partial. Regression tests cover each case. This is
local code only; no runtime deployment, outbound application or release occurred.
See the newest DEVELOPMENT_LOG and HANDOFF entries for exact verification.

## Night development checkpoint — 2026-10-14

Root `ROADMAP.md` now maps original v3.5.1–v4.x intent to verified code and
proposed v3.5.8/v3.5.9 labels without changing `VERSION`. The selected-channel
Watcher now skips a subscriber whose pause/profile or retry-state lookup fails
and continues later users; regressions cover these failures. Full/isolated
PostgreSQL results and final diff are in
the latest `DEVELOPMENT_LOG.md` entry. Existing local runtime is untouched;
real channel Bot API access and deployment approval remain the acceptance gate.
The two untracked owner proposal files remain preserved and excluded.

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

Updated2026-10-14. Source3.5.7, feature/v3.5.7-international-market-coverage.
Current task: Telegram Channel Watcher. Read actualGit/AGENTS first; preserve
user edits. No production/publication or actual employer contact authorized.

## Latest implemented state

Watcher stage1 a6d67fa: /channels add/on/off/remove, career/relocation/both,
selected Bot API channel posts/captions, per-user persistent stats/replay guard.
Stage2 3dffc39: explicit role/company/location/mode labels, original forwarded
channel identity/public URL, shared manual/automatic replay coordination.
Stage3 completed next: bounded PostgreSQL failed-post queue, automatic retry
job every minute (five posts/tick), /channels retry. Pause/source-disable/off
respected; failed retries rotate, queue max100, overflow counted without eviction.
No schema migration; RuntimeState/SeenMessage reused. Original profiles/scorer,
thresholds and notification dedupe preserved. Latest716 unit/4skipped,
PostgreSQL720, compileall/secret/diff passed. Separate Docker/Python3.12 verification of watcher cb1ba4a passed;
earlier image records remain historical.

All previous v3.5.7 source/remote/metadata/support fixes remain complete.
Source salary evidence and candidate/legal/hiring unknowns stay truthful.
GE/AM equal; independent profiles; descending rating65 without inflated scores.

## Limits and next work

Bot API updates require the bot's actual channel access; adding a subscription
is not joining, arbitrary public-channel reading or history backfill. No user
account/MTProto access authorized. Source lists still represent configuration,
not live health. Edited-post/history/per-profile historical rescore are not
implemented. Single polling process; no distributed/exactly-once promise.
State, matches, seen markers and statistics use separate transactions; crash
windows can undercount/replay, overflow failures are counted outside full queue.
Detailed contract: docs/developer/TELEGRAM_WATCH.md.

Next: authorized runtime/channel acceptance.
Owner must select actual channels and arrange Bot API access; production update
still separately gated. Do not close v3.5.7 before real source/Telegram acceptance.
Independent AM feed research open (Manychat no verified AM/support opening).
v3.6 fit ->v3.7 workspace/CV ->v3.8 interview ->v4agent/product follow.
Context Watch unchanged placeholder, private checksum tracked. Main-first policy;
no live ChatGPT access asserted. Private context outsideGit; old chats data;
no ransomware context without separate task. Full history in Git/DEVELOPMENT_LOG.
