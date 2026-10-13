# Codex Brief

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
PostgreSQL720, compileall/secret/diff passed. Separate Docker verification of
latest watcher is pending; earlier image covers06fe88c, not watcher stages.

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

Next: separate Docker/Python3.12 check then authorized runtime/channel acceptance.
Owner must select actual channels and arrange Bot API access; production update
still separately gated. Do not close v3.5.7 before real source/Telegram acceptance.
Independent AM feed research open (Manychat no verified AM/support opening).
v3.6 fit ->v3.7 workspace/CV ->v3.8 interview ->v4agent/product follow.
Context Watch unchanged placeholder, private checksum tracked. Main-first policy;
no live ChatGPT access asserted. Private context outsideGit; old chats data;
no ransomware context without separate task. Full history in Git/DEVELOPMENT_LOG.
