# Personal AI Job Agent — active brief (2026-10-16)

## Verified Git state
- Source tree: `feature/v3.5.7-international-market-coverage`, `VERSION=3.5.7`. At this checkpoint: `b6d41d4`. The final formal release and untouched `main` remain v3.5.6.
- Independent audit fixes #19–#25 are merged into the feature branch. The feature is **not deployed**. CI for PR #25 was green (1043 pytest cases, 82.73% coverage, Docker build, secret scan); verify latest merged CI before stating a newer result.
- Full previous `BRIEF.md` is preserved in `history/BRIEF_PRE_AUDIT_2026-10-16.md`. Root `ROADMAP.md` is the sole canonical product roadmap; this file records the current working checkpoint.
- User-owned untracked files `AI-JOB-AGENT-MERGED-ROADMAP-PROPOSAL.md` and `CODEX-MAIN-ROADMAP-SYNC-PROMPT.md` must stay untouched and uncommitted.

## Product scope
The personal flow is: discover → normalize/dedupe → fit/score → user review → grounded resume/cover letter package → explicit owner approval → application tracking → interview practice. Maintain independent **Career-first** (DevOps/Linux/Infrastructure/SRE) and **Relocation-first** (lawful international employment, including non-IT roles) search profiles. Never invent candidate experience, remote hiring eligibility, visa sponsorship, housing, salary period or employer promises. Unknown evidence remains unknown. Preserve selected provider/source-posting identity and snapshots in review and application packages.

## What is implemented (source + CI, not live acceptance)
- Core bot, per-user profiles, PostgreSQL, source adapters, scan controls, Telegram /jobs, /review, /prepare and manual application status/history/export.
- Source-specific posting snapshots and HH cache digest/race guards. The current source observation is used for scoring, review and preparation; stale HH network/cache responses are not treated as verified.
- HH owner-only submission now persists a `sending` reservation **before** the external API call. A concurrent, previously attempted or ambiguous submission blocks automatic repeat. Confirmed `sent`, external handoff and unknown states are distinguished in database/history/UI. A prepared or reviewed-but-never-sent draft is not considered a submission. No live HH sending was done.
- Recruiter auto-reply defaults OFF; invalid/nonfinite confidence requires human review. HH callback errors redact unexpected provider/DB payloads and validate IDs.
- Auto-apply has **no implementation** despite legacy `AUTO_APPLY` config: /status now explicitly discloses that it never submits automatically. Do not enable it.
- Telegram alerts use a durable per-match retry journal in the PR #28 feature branch. Lost Telegram confirmation can yield duplicate alerts; this is the approved policy, not a zero-duplicate promise. /delivery shows delivery metadata, not vacancy text.
- Initial deterministic interview exercises, conservative relocation evidence classification, Candidate Facts/CV comparisons and LLM drafting with safe factual fallback exist, but broader fit, eligibility, workflow and runtime quality remain partial.

## Next practical work (ordered)
1. Preserve correctness and user trust: review HH reservation/ambiguous response behavior, status/history/export; no provider-side exactly-once guarantees without HH idempotency or reconciliation. Run isolated PostgreSQL fault-injection and manual UX acceptance, never live apply without explicit user approval.
2. Telegram delivery: owner chose at-least-once semantics (duplicates acceptable, missed opportunities not). PR #28 introduces a durable per-match RuntimeState journal, PostgreSQL-fenced claims, immutable alert payload, retry worker and /delivery. Review isolated PostgreSQL tests and latest CI before merging; live Telegram behavior is not yet accepted. Follow [delivery protocol](../developer/NOTIFICATION_DELIVERY.md).
3. Protect application audit history from future job deletion: `Application.job_id` currently uses FK `ON DELETE CASCADE`. Any migration/FK change needs isolated PostgreSQL upgrade tests, back-up/rollback planning and explicit owner authorization before touching production.
4. Add 3–5 meaningful offline end-to-end PostgreSQL tests: discovery → scoring → selected posting → review → grounded /prepare → tracking/export, cross-source identity, multiuser access and failure injection. Do not optimize the number of passing tests.
5. Continue canonical ROADMAP milestones, particularly verified Source Intelligence + practical Relocation-first utility, v3.6 Candidate Fit, v3.7 Application Package, v3.8 Recruiter, v3.9 Interview; later AI Router/Web UI. Measure useful real vacancies and maintain source permission/legal uncertainty.
6. Live Telegram/channel/HH-source acceptance requires owner-approved test environment and source permissions. Do not infer live readiness from unit tests or CI.

## Engineering boundaries
- Before work inspect `git status -sb`, branch/HEAD, GitHub PRs and `ROADMAP.md`. Prefer the short current brief and only relevant sections of the historical HANDOFF/TASKS files.
- Isolated test DB only: `docker compose -f docker-compose.test.yml up -d postgres-test`; `JOB_AGENT_TEST_DATABASE_URL=postgresql+asyncpg://jobagent_test:jobagent_test@127.0.0.1:55432/jobagent_test .venv/bin/pytest -q`.
- Other gates: `git diff --check`, `bash scripts/secret-scan.sh`, Python compilation, GitHub CI + Docker build.
- Never mutate production DB/volumes, `main`, VERSION, releases/tags, external HH/recruiter actions or secrets without explicit separate authorization. Avoid destructive git cleanup.
- Historical checkpoint logs are evidence of past work, not proof of current production behavior. Keep a short current handoff rather than adding dozens of repeating checkpoint headings.
