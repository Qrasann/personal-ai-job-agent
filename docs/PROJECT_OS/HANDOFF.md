# Handoff

## 2026-10-14 — Georgia SSRF follow-up

After `d3a949b`, local Georgia adapters restrict listing detail links to the
source's HTTPS host and standard port. Two regression cases reproduced
cross-host fetches before the fix and pass afterward. No external or production
request was made. Final local checks: 733 unit passed / 4 skipped, 737 isolated
PostgreSQL passed, compileall/secret scan/diff check passed. Preserve the two
untracked owner roadmap proposal files.

## 2026-10-14 — resume import follow-up

After checkpoint `7778de3`, a local candidate-import fix claims the preview
token before resume persistence, preventing duplicate concurrent callback
inserts. Regression in `tests/test_candidate_import_telegram.py` reproduced the
double write before the fix. Final local checks: 731 unit passed / 4 skipped,
735 passed with isolated PostgreSQL, compileall/secret scan/diff check passed.
A failure after token claim requires reupload;
transactional resume/fact persistence is the next design task. Keep the two
untracked owner proposal files out of commits and do not deploy/publish.

## 2026-10-14 — local reliability/security follow-up

This checkpoint follows `99ea166` with fixes in services, HH provider and
Telegram routers plus regression tests. Preserve the
two unrelated untracked roadmap proposal files. `scan_all` continues after one
user fails. Telegram user actions are private-chat only; channel-post watcher
updates remain accepted. `apply_match` requires the configured owner profile
before using the global HH applicant token. HTTP transport errors/HH API bodies
are reduced to safe classes/statuses in user-facing alerts. No production or
external action was taken. A failed vacancy now leaves later jobs in the same
source available and marks that source partial. Final local verification:
730 unit passed / 4 skipped and 734 passed with isolated PostgreSQL;
compileall, secret scan and diff check passed.
Do not deploy/push/release without separate authorization. Real HH ConnectError
cause and Bot API channel acceptance remain unresolved.

## Night development checkpoint — 2026-10-14

Current source branch still has `VERSION=3.5.7`; root roadmap now carries
full product stages and status, with v3.5.8/v3.5.9 only proposed. Channel
Watcher pause/profile/retry-state lookup failure is isolated per subscriber
and covered by four regression cases; other behavior and thresholds remain.
See latest `DEVELOPMENT_LOG.md` for
full verification. Do not commit the two untracked owner proposal files.
Next gate: owner-selected channels and Bot API access, separately approved
runtime deployment, then actual incoming post/replay/retry and scoped-result
acceptance. Continue permitted AM/GE Relocation-first source research if no
owner gate is available. Do not modify production PostgreSQL or volumes.

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

## Resume/verification

Read git status/log, AGENTS/BRIEF, private CONTEXT_INDEX/MODEL_ROUTING and
CODEX_STARTUP. Check local watch checksum, only read meaningful new deltas.
All three watcher stages are local; no production or external API action here.
Do not repeat them; next Docker/acceptance gate and later edits/history options.

.venv/bin/pytest -q
JOB_AGENT_TEST_DATABASE_URL=postgresql+asyncpg://jobagent_test:jobagent_test@127.0.0.1:55432/jobagent_test .venv/bin/pytest -q
.venv/bin/python -m compileall -q app tests
./scripts/secret-scan.sh
git diff --check

Never test against userDB or delete volumes. Local commits allowed; approval for
older06fe88c does not authorize newer watcher production deployment. No automatic
Codex continuation after session exists. Runtime observations in previous logs
remain historical; this turn does not change services.
