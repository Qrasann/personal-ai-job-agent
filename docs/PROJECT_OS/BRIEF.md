# Codex Brief

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
resume persistence read, so the same resume and proposed facts cannot be inserted twice
by a duplicate Telegram callback. If processing fails after the claim, the user
must resend the document; existing partial-write recovery remains future work.

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
