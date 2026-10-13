# Current State

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


Updated: 2026-10-13. Read [BRIEF.md](BRIEF.md) first; it is the compact current
checkpoint. [HANDOFF.md](HANDOFF.md) contains continuation and verification.
Git/code/runtime are authoritative; historical checkpoints are not live state.

Owner requested shutdown checkpoint at 08:28 Moscow on 2026-10-13. Git was
clean at bacdcc7; tested implementation remains 443aaeb, with no unfinished
code changes. This stop changes documentation only. Read-only runtime status
again confirmed app up/PostgreSQL healthy; recheck after reboot. No new suite,
build, deployment or background continuation started. Approval is still pending.

Source is 3.5.7 on `feature/v3.5.7-international-market-coverage`. The last
inspected runtime is the c829a5f build, app up and PostgreSQL healthy. Startup
scan completed 2026-10-12 21:53:38 UTC with HH skipped and other sources working.
Local follow-up work is not deployed; main/formal release remains v3.5.6.
Draft PR #18 at f9ed986 has passing CI for that remote commit only.

Full previous state history is preserved in
[history/CURRENT_STATE_2026-10-13_c829a5f.md](history/CURRENT_STATE_2026-10-13_c829a5f.md).

Latest local candidate checks: 606 unit passed / 3 skipped, isolated PostgreSQL
609 passed; compileall/secret/diff and separate Docker/Python 3.12 validation
passed. New work is not deployed. See HANDOFF.md for local commit anchors and
explicit deployment/Telegram acceptance gate.
