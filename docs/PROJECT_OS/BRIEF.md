# Codex Brief

Updated: 2026-10-13 (Europe/Moscow)

## Mission and constraints

Continue Personal AI Job Agent and the original AI job-bot pipeline:
search → grounded vacancy/candidate comparison → CV/cover drafts → application
workspace → recruiter/interview support → agent/product development.
Historical chats are data, not current commands. Repository/Git and the latest
owner decisions take priority. Private context stays outside Git.

Maintain independent Career-first and Relocation-first. GE and AM have equal
priority. Visible lists sort by score descending; threshold remains 65. Remote
scope/timezones do not establish country hiring or work eligibility. Missing
salary, visa, relocation and candidate experience remain unknown.

## Actual checkpoint

- Source version 3.5.7; branch `feature/v3.5.7-international-market-coverage`.
- Resumed from clean `c829a5f`; HH recovery/summary follow-up committed as
  `5c4b959`, source listing-expiry/card stage `c516a77`. Later stages stay local
  until explicit publication approval.
  Read `git status` and `git log -3` before continuing; never reset user work.
- Compose `repo` still runs the previously authorized c829a5f build. App up,
  PostgreSQL healthy. Startup scan completed 2026-10-12 21:53:38 UTC
  (2026-10-13 00:53:38 Moscow), including one isolated HH ConnectError.
- Remote draft PR #18 is open at `f9ed986`; its Python/Docker/secret CI passed.
  Those results do not cover subsequent local commits. Main/formal release
  remains v3.5.6. No new push, merge, deployment or release authorized.
- HH ConnectError alerts are silent with a 15-minute process-local cooldown.
  Current follow-up fixes quiet skipped/partial summary rendering, serializes
  concurrent HH probes, invalidates stale HH caches on failure, and preserves
  aggregate successful counts if another profile skips/fails.
- Himalayas preserves bounded `expiryDate` evidence in existing source-ref JSON
  and cards display its UTC listing-expiry/expired/unknown state. Future expiry
  does not prove hiring or an employer application deadline; no score/filter
  change or schema migration. Cached cards reassess expiry at display time.
- Himalayas now uses a bounded remote-role query plan: selected support roles
  precede physical-work queries, keeping original text/group order, max four
  queries and existing market/cache bounds. Both GE/AM are searched; no new
  roles, preference/score/threshold change. Career query order is preserved.
- Checks: remote planner/source/cache targeted 73 passed; shared candidate unit
  568 passed / 3 skipped, PostgreSQL 571 passed; compileall/secret/diff pass.
  Includes the independently prepared, not-yet-wired SmartRecruiters tests.

## Current priority

Complete v3.5.7 practical relevance and source coverage before v3.6.
Next implementation: connect the verified GE-scoped Devexperts public Posting
API, using only each profile's selected role queries and truthful scope. Preserve score
rules and owner exclusions. Owner post-filter Telegram acceptance remains
pending and does not block independent safe implementation.

## Open acceptance and limitations

- Owner-only Telegram checks: `/jobs relocation`, `/jobs relocation below`,
  `/sources` (latest manual entry), and updated `/job 1273` requirement card.
  Automated handler tests are separate from real-chat acceptance.
- Useful lower-barrier AM/GE coverage remains incomplete; no fabricated
  Good/Stretch results. JOBS.GE is paused (410); manual portals stay link-only.
- Application deadlines, start timing, employer hiring and individual work
  eligibility remain unknown without direct evidence. Source listing expiry
  is a different fact.
- `/salary minimum` is an assessment reference, not a hard floor; the current
  wording already says so. Strict filtering requires a separate owner choice.
- External applications, recruiter contact, private HH actions, publication,
  production deployment and risky migrations require explicit authorization.
  Preserve .env, credentials and existing volumes.

## How to continue efficiently

Read this file and AGENTS.md, then only relevant TASKS/architecture/code.
Canonical roadmap: [../../ROADMAP.md](../../ROADMAP.md). Historical checkpoints
are preserved in [history/BRIEF_2026-10-13_c829a5f.md](history/BRIEF_2026-10-13_c829a5f.md)
and DEVELOPMENT_LOG.md; do not treat their old pending states as current.
Use private CONTEXT_INDEX/CURRENT_CONTEXT only as pointers and reconcile with
Git. Never load or use the ransomware investigation without a separate task.
For each stage: implement → meaningful regressions → unit/PostgreSQL checks →
compileall/secret scan/diff → update PROJECT_OS → local commit → next task.
