# Codex Brief

Last updated: 2026-10-11 (Europe/Moscow)

## Mission

Continue the existing Personal AI Job Agent. Maintain two independent tracks:

1. **Career-first** — DevOps / Infrastructure / SRE growth.
2. **Relocation-first** — any legal, verifiable work that can enable a realistic move; career fit is secondary.

Never restart the project from scratch. Unknown visa, salary, citizenship, housing, or relocation facts remain unknown; never convert missing evidence into `false` or a positive claim.

## Current runtime

- Source/runtime: `v3.5.6`, database schema `4/4`.
- Active branch: `feature/v3.5.2-dual-search-modes`.
- Local release directory: `~/job-agent-release-v352`.
- Docker Compose project: `repo`.
- Career-first and Relocation-first SearchProfiles are enabled independently.
- Working sources include HH public fallback, RemoteOK, Arbeitnow, Job Bank Canada, EURES, jobs.ge, hr.ge, and configured Telegram ingestion.
- Auto-apply and HH private actions remain off.

## Recently completed

- Added bounded retries for EURES transport failures, including raw
  `ssl.SSLError`, and made source alerts report HTTP status / exception type.
- Added `/parallelsearch on|off|status` and `/relocationroles`.
- Each profile now discovers, scores, stores, and reports results independently.
- Fixed concurrent `JobMatch` inserts with an atomic PostgreSQL upsert.
- Fixed Relocation-first scoring to use `relocation_queries`.
- Added public Arbeitnow Germany discovery with conservative evidence handling.
- Stopped inferring salary from arbitrary description numbers.
- Added safe tracked-branch updates through `./job-agent update`.
- Added Job Bank Canada discovery with separate international eligibility, LMIA, and support evidence.
- Added bounded EURES discovery using the employer cross-border recruitment flag without treating it as visa sponsorship.
- Added explicit Telegram resume import for PDF/DOCX/TXT, plus fact confidence/provenance and overlap review.
- Added persisted Recommendation v2 component breakdown with unknown values
  left unset and displayed in vacancy details.
- Added `/salary`, `/blacklist`, `/scanstatus`, `/cancel`, bounded concurrent discovery, source timings, and persistent manual-scan state.
- Audited public applicant-count signals; connected feeds do not expose reliable candidate-side competition counts.

## Verified

- Latest full PostgreSQL-backed suite: `220 passed`, 65.66% branch coverage
  (rerun on 2026-10-11).
- Targeted EURES, Job Bank and source-error regressions: `25 passed`.
- GitHub Actions run 110 passed.
- Commit `496c920` is published and deployed; Compose reports source/runtime
  3.5.6, PostgreSQL healthy, schema 4/4, and the bot polling. Mount inspection
  confirms the existing `repo_jobagent_v3_pg` and `repo_jobagent_v3_files`
  volumes remain attached. Startup scan began on HH public fallback, Arbeitnow
  and RemoteOK; no startup errors were present in the inspected log tail.
- EURES now preserves partial results when only some requests fail. Existing PostgreSQL and storage volumes remain attached.
- Polling, schema check, scheduled/manual dual-profile scans, and concurrent scan protection passed locally.
- GitHub `main` is still v3.5.1 at `375af5f`; PR #15 contains v3.5.6 but
  diverged from the merged search-control commit. A merge-only synchronization
  is prepared locally; publish it to the PR branch after the checks below.
- Latest supplied/runtime logs show intermittent EURES `SSLError` retries,
  some EURES HTTP 200 responses, and a scheduled scan that still completed.
  Job Bank and other sources continue independently; EURES can still be
  unavailable for an individual profile when every bounded attempt fails.

## Current priority

Complete owner-driven real-chat acceptance for `/salary`, `/blacklist`, `/scanstatus`, `/cancel`, `/import`, and Recommendation v2 vacancy details; record results before merging PR #15 into `main` or tagging releases.

## Open limitations

- Source coverage remains the main Relocation-first bottleneck, especially Armenia and low-barrier legal work.
- Arbeitnow currently improves Germany/Career coverage but may contain no low-barrier roles.
- HH is mostly domestic and can return `403`; public fallback is expected, CAPTCHA must not be bypassed.
- EURES may still return partial results or fail for one profile if repeated
  TLS transport attempts fail; retries are bounded, HTTP status responses are
  not retried, and other sources continue.
- The EURES cross-border flag is not proof of visa sponsorship, relocation support, or third-country work authorization.
- Public applicant counts are unavailable in the connected candidate-facing feeds and remain unknown.
- Dedicated Career Score and Relocation Score, affordability calculation, migration knowledge base, and application tracker are later phases—not completed features.
- Full remote control of the user's Arch machine exists only in a Codex CLI session started on that machine; cloud Codex cannot access `/home/roma`.

## Update protocol

After every completed stage, update this file—not the entire original long prompt:

1. change `Last updated`;
2. move delivered work into **Recently completed**;
3. replace verification counts/results with evidence from the latest run;
4. keep only unresolved items in **Open limitations**;
5. set exactly one practical **Current priority**;
6. add detailed chronology to `DEVELOPMENT_LOG.md` and durable follow-up items to `TASKS.md`.

Do not put secrets, exact passport data, private employment details, or other sensitive candidate information in this public repository.

## Compact startup request

```text
Read AGENTS.md and docs/PROJECT_OS/BRIEF.md first. Then inspect git status,
the latest commits, and only the detailed PROJECT_OS documents relevant to the
current priority. Verify claims against the code; do not restart or broadly
rewrite the project. Preserve .env, Docker volumes, the database, and dirty
user work. Continue the Current priority with tests. After a completed stage,
update BRIEF.md, DEVELOPMENT_LOG.md, TASKS.md, and HANDOFF.md with verified
facts. Report what changed, checks run, remaining limitations, and the exact
safe local deployment command.
```
