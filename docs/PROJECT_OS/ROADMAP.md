# Project roadmap

## Current checkpoint — 2026-10-14

Resumed from b228ea5 and preserved interrupted local edits. Source 3.5.7,
branch feature/v3.5.7-international-market-coverage. Completed source-evidence
quality stage: explicit residence/country limits outrank worldwide boilerplate
in signals and cards, including old cached rows; Himalayas keeps the stated
residence clause without mapping regions to countries. Existing weights,
threshold 65 and explicit US/EU rules remain unchanged. Unsupported country
hiring/work authorization remains uncertain.

Source salary text now reaches /job as bounded, escaped display-only evidence.
Decimal/hourly or ambiguous amounts do not enter the legacy numeric salary
parser or monthly scoring; structured salary wins when present. Regression
coverage includes Job Bank decimal hourly text, unchanged match score, malformed
metadata, HTML escaping, structured precedence and remote restriction examples.
46 targeted passed; full unit 631 passed / 3 skipped, PostgreSQL 634 passed;
compileall, secret scan and diff check passed. No migrations or provider calls
added. This stage is local and undeployed; read actual commit HEAD from Git.

Read-only runtime check: existing repo app up ~2h/PostgreSQL healthy. No runtime
update performed here; previous c829a5f build remains the last identified build.
The earlier startup/CI records below are historical, not new acceptance.
Deployment agreement remains pending. Context Watch is an unsynchronized
placeholder (no meaningful delta); no live ChatGPT access was claimed.

Next independent v3.5.7 task: fix Telegram ingestion's unknown/negative support
and ambiguous decimal salary parsing, then tests/security/docs/local commit.
After approved runtime update, validate startup/source/Telegram acceptance
before closing v3.5.7 and beginning v3.6. Keep old six stages complete.


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
