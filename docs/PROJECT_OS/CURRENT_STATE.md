# Current State

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
