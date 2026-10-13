# Codex Brief

Updated: 2026-10-14 (Europe/Moscow)

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

## Current checkpoint — 2026-10-14

Source 3.5.7; branch feature/v3.5.7-international-market-coverage. Earlier six
stages complete. af1ff56 fixes source salary display and remote-limit precedence;
Telegram evidence stage completed next. Latest unit 646 / 3 skipped,
PostgreSQL 649, compileall/secret/diff passed. Runtime last read up/PG healthy;
no new deployment/publication. See HANDOFF for exact continuation/limitations.
Context Watch has no synchronized delta. Next: malformed numeric source values;
v3.5.7 real Telegram/source acceptance still requires approved runtime update.

## Earlier validated checkpoint

- Shutdown requested by owner, 2026-10-13 08:28 Moscow. Worktree was clean at
  `bacdcc7` before this docs-only checkpoint; no unfinished code edits.
  Runtime status rechecked: app up, PostgreSQL healthy. No deployment or new
  long operation started. On reboot read HANDOFF's shutdown section, recheck
  Git/runtime, and consume the pending owner deployment decision first.
- Source version 3.5.7; branch `feature/v3.5.7-international-market-coverage`.
- Latest verified implementation HEAD: `443aaeb`; any later docs-only
  checkpoint does not change the validated application candidate.
- Resumed from clean `c829a5f`; HH recovery/summary follow-up committed as
  `5c4b959`, source listing-expiry/card stage `c516a77`, remote-query plan
  `e7b56f6`, GE SmartRecruiters feed `5044e90`, exact requirement sections
  `5d02cb2`. Later stages stay local
  until explicit publication approval.
  Read `git status` and `git log -3` before continuing; never reset user work.
- Compose `repo` still runs the previously authorized c829a5f build. App up,
  PostgreSQL healthy. Startup scan completed 2026-10-12 21:53:38 UTC
  (2026-10-13 00:53:38 Moscow), including one isolated HH ConnectError.
- Latest runtime log (2026-10-13 05:08:33 UTC) reproduced `KeyError: 'found'`
  in old HH aggregation after recovery. Scan completed, but that source result
  was discarded. Local 5c4b959/443aaeb fixes this exact transition with a
  regression; deploy remains gated by owner agreement.
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
- New curated SmartRecruiters/Devexperts feed is GE-only, public read-only,
  selected-role scoped and source-toggle aware. One page max 100, max ten
  relevant details, 10s request / 60s total budget, one transport retry and
  six-hour scheduled cache. Verified partial results survive later budget
  expiry; external cancellation propagates. Hybrid/GE-only remote remains
  scoped, with salary/visa/relocation unknown unless explicitly offered.
- Live read-only adapter probe found one customer-support-related posting in
  GE/hybrid; visa/relocation unknown. It is a lead, not a Good/eligibility claim.
- Exact Devexperts headings now identify required (`What we expect from
  candidates`) and preferred (`As a Plus`) sections. Existing skill vocabulary,
  scorer weights and thresholds are preserved; no nontechnical facts invented.
- Explicit Georgian/Armenian query and resume text now tokenize as Unicode
  words in Georgia discovery and matching. Existing punctuation, generic-word
  exclusions, scoring weights/caps/65 threshold are preserved. No translations
  or owner-selected roles are introduced.
- Latest verification: 606 unit passed / 3 skipped, PostgreSQL 609 passed;
  compileall, secret scan and diff check pass. Separate local Docker validation
  image built and Python 3.12 imports/compile passed without networking.
  All new stages remain undeployed.

## Current priority

Complete v3.5.7 practical relevance and source coverage before v3.6.
Current code candidate is ready for the authorized deployment/Telegram/source
relevance gate. Owner approval is required to update the working Compose build
under the latest request. Validate new source counts and scoped relocation
output after that update before closing v3.5.7; do not claim Good/eligibility
from adapter HTTP success. v3.6 follows the mandatory v3.5.7 acceptance. Preserve score
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
- Alternative skill/language groups are not modeled separately yet: requirement
  section mentions are technical evidence, not full employer-condition fit.
  Track that improvement in v3.6; no individual Python requirement inferred
  from a source naming alternative programming languages.
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
