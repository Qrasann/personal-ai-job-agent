# Codex Brief

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
