# Project roadmap

The canonical roadmap is [ROADMAP.md](../../ROADMAP.md). Current stage remains
v3.5.7 international coverage/relevance; v3.6 candidate fit, v3.7 application
workspace, v3.8 recruiter/interview support and v4 agent/product development
follow its mandatory obligations.

Latest checkpoint: HH skipped/partial summaries and cooldown cache/concurrency
recovery are validated locally. Prior runtime c829a5f is healthy and its startup
scan completed 21:53:38 UTC. No new production deployment/publication authorized.
Source-expiry cards and bounded remote support query planning are implemented
locally. The curated GE SmartRecruiters/Devexperts feed is now wired and
verified read-only, with exact requirement section parsing. Unicode
local-query support is implemented. Next gate is explicit working-runtime
update approval and real source/Telegram acceptance; then v3.6. Owner-only Telegram acceptance stays separately pending.
See BRIEF.md for concise verification and HANDOFF.md for transfer details.

Verified implementation candidate 443aaeb is committed; owner deployment
approval is pending. See HANDOFF.md for precise continuation and runtime gate.
Old runtime reproduced the HH aggregate-recovery KeyError at 05:08:33 UTC;
the candidate already fixes it. Record real source/Telegram acceptance after
the approved update, then continue v3.6.

Owner-requested shutdown checkpoint saved 2026-10-13 08:28 Moscow. No roadmap
stage advanced during the stop. On resume recheck Git/runtime and the pending
deployment decision; do not repeat the six completed local implementation stages.
