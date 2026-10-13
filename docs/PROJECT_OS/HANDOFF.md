# Handoff

Updated: 2026-10-13 (Europe/Moscow)

## Shutdown checkpoint — 08:28 Moscow

Owner requested a safe stop for powering off the PC. No new implementation,
test suite, build or deployment started. Before this documentation checkpoint,
Git HEAD was `bacdcc794862125f7c6404e119b767547bf11eb0`, with a clean worktree;
application/data/build inputs still match tested implementation `443aaeb`.
The checkpoint commit itself is docs-only; obtain its exact HEAD from Git.
There are no unfinished code edits or uncommitted implementation stages.

Read-only status: `repo` app up, PostgreSQL healthy; isolated `postgres-test`
also healthy. No services were stopped/rebuilt and no data or volumes touched.
These are pre-shutdown observations: recheck after the next boot. Test DB is
disposable tmpfs and may be empty after restart; it is not the user's DB.

Latest completed candidate checks remain 606 unit passed / 3 skipped,
609 PostgreSQL passed, compileall, secret scan, diff check and separate
Python 3.12/Docker validation passed. Suites were not rerun for this docs-only
stop. Publication/CI remains as last recorded below, not rechecked now.
For this docs-only checkpoint, secret scan and `git diff --check` passed.

On resume: read BRIEF/AGENTS, Git status/log, private CONTEXT_INDEX and
CURRENT_CONTEXT, then this handoff. Preserve new user edits. Recheck runtime
status before any action; do not repeat the six completed stages. Deployment
approval for `443aaeb` is still unanswered; powering off is not approval.
Continue at the explicit deployment and real v3.5.7 acceptance gate below.
Development is stopped at the owner's request; no background Codex continuation
or post-reboot automation has been configured.

## Current source and runtime

- Source 3.5.7 on `feature/v3.5.7-international-market-coverage`.
- Verified implementation HEAD is `443aaeb` (six local completed stages).
  A following docs-only checkpoint may change Git HEAD; read the actual ref.
- Latest completed local stages `5c4b959` (HH recovery), `c516a77` (expiry),
  `e7b56f6` (remote queries), `5044e90` (GE public feed),
  `5d02cb2` (exact required/preferred sections), `443aaeb` (Unicode tokens);
  obtain current HEAD with `git rev-parse --short HEAD`
  and inspect `git status --short`. Resumed clean; preserve in-flight stages.
- Runtime remains the c829a5f Compose `repo` build from 00:52 Moscow. App up,
  PostgreSQL healthy; startup scan completed at 21:53:38 UTC / 00:53:38 Moscow.
  One HH connection error was isolated and other sources completed.
- A fresh log read reproduced old HH `aggregate["found"]` KeyError at
  2026-10-13 05:08:33 UTC for profile 2. Scheduled scan completed at 05:08:34,
  losing that recovered source's batch. This is the precise already-tested
  aggregate-recovery regression fixed in 5c4b959, part of candidate 443aaeb.
  Runtime approval remains pending; do not bypass the deployment gate.
- Draft PR #18 remains open at remote `f9ed986`, with successful Python,
  Docker build and secret-scan checks. CI does not cover local later commits.
  Formal release/main is v3.5.6. No new production deployment is authorized.

## Completed capabilities and current work

Dual search profiles, scoped review/card paths, descending rankings, truthful
candidate facts, resume import and manual application workflow remain intact.
AM/GE manual links, Lineate Greenhouse, Collectly Lever, Himalayas/Remotive and
source resilience are preserved. Threshold stays 65; legal eligibility and
unsupported candidate/work/relocation facts remain unknown.

The HH follow-up implements quiet `пропущен` display in /scan and /scanstatus,
`частично` for mixed-profile results, serialized HH probes, invalidation of HH
caches on ConnectError, and safe aggregate recovery instead of KeyError.
Regression tests verify no extra alert, bounded concurrent probes, real retry
after cooldown, and retained successful counts. Targeted suite 49 passed;
full shared-candidate unit suite 486 passed / 3 skipped; isolated PostgreSQL
489 passed; compileall, secret scan and git diff --check passed.

Himalayas expiry evidence is now carried through the existing source-ref raw
JSON to /job cards. `expiryDate` is source listing expiry, separately labeled
from employer hiring/application deadline; missing/malformed/timezone-ambiguous
values stay unknown. Epoch seconds/ms and timezone-aware ISO are normalized to
UTC. Old source refs without metadata show unknown until provider refresh.
No database migration, score change, new filter or extra provider requests.
Targeted expiry/service/card suite 76 passed; full shared candidate unit 563
passed / 3 skipped, PostgreSQL 566 passed; compileall/secret/diff checks passed.
Prepared independent remote-query/source modules are included in those totals.

Remote query planning is now implemented for Himalayas only. It chooses up to
four supplied queries with support/IT roles ahead of physical-work roles, stable
inside each group. Original preferences and all parse-time role matching stay
intact; no EURES or scoring changes. Both AM and GE are covered by the request
regression. Targeted 73 passed; full shared worktree unit 568 passed / 3 skipped,
PostgreSQL 571 passed; compileall/secret/diff pass. These are historical
stage-specific results; SmartRecruiters integration is completed below.

SmartRecruiters/Devexperts is now wired in GE catalog/registry/service/cache.
One public page (max 100), max 10 matching details; request 10s / total 60s, one
transport retry, six-hour scheduled cache. Partial usable details survive the
source's total budget expiry; external cancellation propagates. Source toggles
are respected. Read-only live adapter probe found one Application Support
Engineer Level1 (GE/hybrid); salary/visa/relocation remain unknown. AM is not
attributed to this GE-only feed. No private API, apply or messaging capability.
Targeted source/catalog/service/cache 59 passed; shared candidate unit 585
passed / 3 skipped, PostgreSQL 588 passed; compileall/secret/diff passed.
Exact Devexperts required/preferred heading classification now passes 80
targeted tests, with existing 85/15 technical weights intact. Nontechnical
conditions stay unscored. Alternative-language groups remain a known v3.6 gap;
do not turn a required-section Python mention into an individually mandatory
Python hiring claim. Full unit 585 / 3 skipped, PostgreSQL 588 and safety checks
passed. Unicode query-token support is now implemented as the next completed local
stage: explicit Georgian/Armenian words tokenize in Georgia discovery, role
matching and resume selection. English/Russian punctuation/generic exclusions,
weights/caps and threshold remain unchanged; no translation or preference
injection. Targeted multilingual/Georgia/resume/Staff suite 48 passed. Latest
full unit 606 / 3 skipped, PostgreSQL 609, compileall/secret/diff passed. Separate
local validation image built; Python 3.12 import/compile passed with no network.

## Next concrete work

1. Obtain owner agreement for updating the working Compose repo to this
   tested candidate (latest user request makes production deployment a gate).
   Do not rebuild/update runtime until agreement is explicit.
   Approval was requested for implementation `443aaeb` and is pending.
   Once approved, ensure Git is clean and application/data files still match
   that tested candidate, then `JOB_AGENT_COMPOSE_PROJECT=repo ./job-agent rebuild`,
   inspect status/startup logs, and record actual acceptance.
2. After update, verify startup scan and source counts; owner checks /sources,
   /jobs relocation, /jobs relocation below and updated /job cards.
3. Evaluate real source relevance without inflating ratings; complete required
   v3.5.7 acceptance before moving to v3.6. Curated cross-language translation
   aliases remain unverified; Unicode support handles supplied same-language
   text, not automatic translations.

After v3.5.7 obligations: v3.6 candidate/vacancy fit, v3.7 application workspace,
v3.8 recruiter/interview support, then v4 agent/multi-user/product work per
canonical ROADMAP. If a task needs an owner decision, record the blocker and
continue independent safe work.

## Verification and transfer

Read AGENTS.md and BRIEF.md first, then relevant code/TASKS. Run
`.venv/bin/pytest -q`; isolated PostgreSQL URL and safety rules are in
`docs/developer/TESTING.md`. Never point integration tests at the user's DB.
Use `./scripts/secret-scan.sh`, compileall and git diff --check before commit.
Local commits authorized; publication and production deployment require owner
approval. Never delete volumes or include .env/private context in Git.

Original full handoff is preserved in
[history/HANDOFF_2026-10-13_c829a5f.md](history/HANDOFF_2026-10-13_c829a5f.md).
Detailed new chronology stays in DEVELOPMENT_LOG.md. Private context index is
outside the repository and must be handed over separately when authorized.
