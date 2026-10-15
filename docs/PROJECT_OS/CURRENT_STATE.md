# Current State

## 2026-10-15 — align experience fit and seniority gating

Senior-level title policy is unchanged. Numerical high-experience gating now uses required years from the Candidate Fit parser, so a preferred 5+ band cannot cause a skip. The prior 3–4-year stretch boundary remains. Synthetic regression was red before; full isolated PostgreSQL: 1000 passed.

## 2026-10-15 — freeze selected provider posting identity in packages

New Application Package vacancy snapshots retain the selected source ID and provider posting ID alongside the already frozen text, URL and relocation evidence. Exports disclose missing identity for older packages. The HH private path now drafts from its source-specific posting text. Focused tests: 67 passed; full isolated PostgreSQL suite passed. No live applications were sent.

## 2026-10-15 — source-specific posting snapshot for review and preparation

Each newly ingested or refreshed `JobSourceRef` now stores its own normalized posting fields beside evidence and verified detail cache. Vacancy details, Candidate Fit review and `/prepare` use the selected source's title, description and structured fields; already cached full HH details take precedence for drafting. A synthetic cross-source regression reproduced a Jobs.ge package using an HR.ge description before the change. PostgreSQL regression confirms same-source refresh updates its own snapshot and a second source keeps separate text. Existing refs without a normalized snapshot retain the canonical fallback until rediscovery. Full isolated PostgreSQL: 996 passed.


## 2026-10-15 — align Application Package with displayed source

`/prepare` and vacancy details now use one source-reference preference order. A synthetic shared Job with `hr_ge` and `jobs_ge` previously displayed one source but prepared the other source's URL and mobility evidence; the regression now keeps the package source aligned with the detail view. This selects a deterministic review source, not a claim about which feed originally created the match. Focused package/detail tests: 38 passed; full isolated PostgreSQL: 994 passed.


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


## 2026-10-15 — Russian start timing

Explicit “Выход на работу по договорённости” is retained as negotiable timing; “Начать можно сразу” is immediate. This is source description only. Full isolated PostgreSQL: 988 passed.


## 2026-10-15 — Russian housing evidence

Explicit Russian accommodation provision/refusal is now recognized and
excerpted; an unsupported mention remains unknown. Full isolated PostgreSQL:
988 passed.

## 2026-10-15 — bound evidence-rich Telegram vacancy details

Detail cards enforce a 3900 UTF-16-unit budget; only the long description is
trimmed so evidence, score and source link remain visible. Full isolated
PostgreSQL: 988 passed.

## 2026-10-15 — short non-required skill statement

Candidate Fit now keeps “No Kubernetes required” as unknown rather than
required under a Requirements heading. Focused tests: 67; isolated PostgreSQL:
987 passed.

## 2026-10-15 — skill-local preferred markers

Candidate Fit recognizes a narrow per-skill plus/preferred phrase inside a
Requirements heading and does not promote that skill to required. Unrelated
mandatory skills remain required. Focused tests: 66; isolated PostgreSQL: 986.

## 2026-10-15 — disclose missing evidence in legacy packages

Package previews and exports identify when a historical record lacks a
structured mobility evidence snapshot. They do not imply that current evidence
was captured at preparation time. Focused tests: 12; full isolated PostgreSQL:
984 passed.

## 2026-10-15 — source evidence refresh and package snapshot regression

PostgreSQL regression checks that repeat discovery refreshes source-specific
location evidence without rewriting the evidence already stored in an
Application Package. Targeted isolated DB test: 1 passed; prior full suite:
984 passed.

## 2026-10-15 — explicit non-required skills

Candidate Fit does not promote supported “no experience with this skill
required” / “skill is not required” wording to mandatory status only because it
appears under Requirements. Other skills keep their own classification.
Focused tests: 64; isolated PostgreSQL: 984 passed.

## 2026-10-15 — German relocation evidence fixture

Synthetic German wording now exercises residence, prior work authorization,
housing, language preference and start timing. A word-boundary regression
prevents `Deutschland` from being interpreted as `Deutsch`. Focused tests: 87;
isolated PostgreSQL: 982 passed.

## 2026-10-15 — conservative support-component ambiguity

Visa and relocation evidence now stays unknown if per-component parsing
conflicts with a sentence-level result, preventing a refusal for one benefit
from being applied to another. The legacy scoring parser remains unchanged.
Focused tests: 46; isolated PostgreSQL: 981 passed.

## 2026-10-15 — start-timing evidence kinds

The exact start-timing text remains stored; a conservative classification now
labels immediate, relative, stated date, notice period or negotiable phrases.
It does not compare against candidate availability. Focused tests: 44; isolated
PostgreSQL: 979 passed.

## 2026-10-15 — multiple per-language observations

One source posting can now preserve separate English, German, French, Russian,
Spanish, Dutch, Italian, Polish, Portuguese and Arabic observations, with
required/preferred/unspecified state, excerpt and separate English CEFR where
explicit. Conflicting explicit states remain marked as conflicting. Focused
tests: 47; isolated PostgreSQL: 978 passed.

## 2026-10-15 — explicit prior-authorization negative evidence

The evidence packet now distinguishes an explicit statement that existing
work authorization is not required from a missing condition; contradictory
source statements remain unknown and carry a conflict label. Focused tests:
82; isolated PostgreSQL: 977 passed.

## 2026-10-15 — immutable mobility evidence in prepared packages

Application Package vacancy snapshots now include a deep copy of the selected
source's Relocation Evidence. Package export reads that immutable JSON snapshot
after later source refreshes; the preview identifies its capture time. HH
application snapshots use the same path. No migration. Focused tests: 20; repeat
refresh PostgreSQL regression: 1 passed; full isolated PostgreSQL: 976 passed.

## 2026-10-15 — preserve source work-location excerpt

When the source adapter provides `source_location` or `source_country`, the
work-country evidence retains and displays that exact bounded field alongside
the normalized country value. Otherwise it falls back to the source country
code. Focused tests: 41; isolated PostgreSQL: 975 passed.

## 2026-10-15 — separate citizenship from residence scope

Restriction evidence now classifies explicit source text as citizenship,
residence/location, both, or unspecified. The detail card preserves the quote
and source provenance and labels it as posting text, not a legal determination.
Focused tests: 41; isolated PostgreSQL suite: 975 passed.

## 2026-10-15 — classify housing and language evidence

Housing is `true`/`false` only when a source explicitly says it is provided or
not provided; other mentions remain unknown. Language conditions now retain
required/preferred/unspecified interpretation, with English CEFR level stored
separately. Detail cards render the interpretation and excerpt. Ambiguous
language text remains observed, not a requirement. Focused suite: 84; isolated
PostgreSQL: 974 passed.

## 2026-10-15 — source-scoped Relocation Evidence v1

`upsert_job` now saves `relocation_evidence_v1` beside each source reference,
including source provenance, capture time, excerpt and bounded confidence for
the eight relocation/hiring signals. Structured source country is labeled as
reported by the source; support/prerequisite statements remain separate from
personal eligibility. Housing/language/start text is marked observed rather
than treated as a promise/requirement. Unknowns remain unknown. Details display
the evidence alongside existing mobility summary; scoring and Candidate Facts
are unchanged. Synthetic fixtures only; full isolated PostgreSQL: 973 passed.

## 2026-10-15 — isolate recruiter instructions from message content

Recruiter replies now separate developer instructions from untrusted JSON
context, question and Candidate Facts. Existing sensitive-topic human review
and default-OFF auto-reply policy remain. Focused tests: 16 passed; full
isolated PostgreSQL: 969 passed.

## 2026-10-15 — isolate cover-letter instructions from vacancy content

Cover-letter model calls now use separate developer instructions and
JSON-encoded data fields. Embedded vacancy/resume/fact instructions are
explicitly untrusted, and candidate claims must be grounded in Candidate Facts.
This does not replace human review. Focused LLM tests: 5 passed; full isolated
PostgreSQL: 968 passed.

## 2026-10-15 — add OpenShift to Fit and Interview practice

OpenShift is now separately recognized by Candidate Fit, including its Red Hat
name. Interview practice includes a rollout scenario with safe SCC/RBAC
guidance. Focused fit/interview tests: 87 passed; full isolated PostgreSQL:
967 passed.

## 2026-10-15 — preserve timezone evidence in vacancy dates

Detail cards convert aware publication timestamps to UTC and mark them `UTC`;
date-only values stay date-only, and naive timestamps disclose that their
timezone is unknown. Focused tests: 68 passed; full isolated PostgreSQL: 964
passed.

## 2026-10-15 — nested Candidate Fit alternatives

Explicit nested flat `or/или` chains inside a parenthesized choice now form
one alternative group alongside independent requirements; scoring and resume
coverage share it. Ambiguous mixed `and/и` chains and repeated mentions remain
ungrouped. Focused tests: 79 passed.

## 2026-10-15 — refresh repeated source postings safely

An existing `(source_id, source_job_id)` now refreshes nonempty vacancy fields
and source raw values. Missing values do not erase earlier evidence, verified
HH detail cache survives, and source identity/first-seen metadata is retained.
Saved application snapshots remain immutable. PostgreSQL advisory and row
locks serialize concurrent upserts; cross-source canonical dedup remains in
place, and identity changes do not overwrite another Job's fingerprint. Two
new PostgreSQL regressions added; full isolated suite: 957 passed.

## 2026-10-15 — do not infer a salary period in match scoring

Salary score comparison now requires an explicit supported period when a
monthly profile minimum is configured. Missing or unrecognized periods remain
visible for review and score neutrally instead of being treated as monthly.
Focused salary/score tests: 61 passed.

## 2026-10-15 — disclose unrecognized requirements in package review

When no technical skills or alternatives are recognized, the Application
Package now explicitly says so and prompts a manual review of the full vacancy.
The existing no-discrepancy statement remains limited to recognized skills.
Focused package tests: 20 passed.

## 2026-10-15 — scoped `/prepare` command

`/prepare <vacancy_id> [career|relocation]` now saves the same reviewable
Application Package as the existing preparation button. A scoped lookup is
limited to the user's active search profile; invalid scope, unavailable
profile or unmatched vacancy does not create a package. Errors are sanitized
and point to `/applications` because a saved draft may exist after a partial
failure. Focused handler tests: 31 passed; full isolated PostgreSQL: 953 passed.

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

Arbeitnow numeric `created_at` values now use the shared timestamp parser and
render as UTC ISO dates. Invalid values stay unknown. This does not infer
freshness or change match behavior. Focused tests: 46; isolated PostgreSQL:
933 passed.

## 2026-10-15 — clarify application status provenance in exports

Application text exports now identify status as locally recorded and say that
employer/provider receipt is not independently verified. The existing manual
status and history workflow is unchanged. Focused package/handler tests: 40;
isolated PostgreSQL suite: 929 passed.

## 2026-10-15 — normalize Remotive publication timestamps

Timezone-aware Remotive RSS RFC 2822 and API ISO dates are normalized to UTC
ISO before persistence/display. Malformed or timezone-less dates remain
unknown. Focused Remotive tests: 8; isolated PostgreSQL: 929 passed. This is
date normalization only and makes no vacancy freshness or hiring-status claim.

## 2026-10-15 — isolated parenthesized skill alternatives

Explicit parenthesized `or/или` choices can now coexist with an independent
skill in the same requirement clause. Slash alternatives, repeated skills
outside the parentheses, and responsibility-only mentions remain ungrouped.
Focused tests: 67; full isolated PostgreSQL: 928.

## 2026-10-15 — keep extra alternative CV claims reviewable

Alternative-group comparison now shows unsupported extra CV options even when
another option correctly satisfies the group in both sources. Focused tests:
63 passed; isolated PostgreSQL suite: 923 passed.

## 2026-10-15 — recruiter sensitive-context fallback

Sensitive salary, identity-document, availability and similar topics in any
provided recruiter context now force a human response; English `passport` is
recognized. String `"false"` from valid JSON no longer relies on Python
truthiness. Focused tests: 13; isolated PostgreSQL: 921 passed.

## 2026-10-15 — preserve alternatives in resume comparison

Resume/Application Package checks now retain explicit OR groups: they only
count as confirmed if the same option is present in the selected CV and
Candidate Facts. Mismatched CV/fact options remain reviewable. Focused suite:
61 passed; isolated PostgreSQL: 917 passed.

## 2026-10-15 — tighten salary-period text boundary

The display-only salary-period parser accepts an explicit unit immediately
after the currency-bearing value. It ignores unrelated time references in
surrounding description text. Focused tests: 83; isolated PostgreSQL: 914.

## 2026-10-15 — Interview Agent IaC/cloud/observability exercises

Interview practice now has curated templates for Terraform, Ansible, AWS,
Grafana and Helm. They favor safe, reversible troubleshooting and make no
candidate evaluation. Focused tests: 31 passed; isolated PostgreSQL: 913.

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
