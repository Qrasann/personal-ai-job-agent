# Project roadmap

Latest incremental source-coverage step: `/sources` now includes a manual
Georgia link to jobs.ss.ge, which exposes a broader local vacancy catalog.
Automated extraction remains off because a reusable API/permission was not
verified. Targeted source tests pass; full validation and deployed Telegram
confirmation remain open.

Latest operational improvement in progress: public HH `ConnectError` is
silently skipped in Telegram, other sources continue, and a 15-minute
cooldown ensures HH is periodically probed without duplicate profile attempts.
Other provider errors remain visible; HH's other transport errors retain their
bounded retry. Tests pass; Compose rebuild/runtime verification and commit are
pending. This changes source resilience, not the matching/ranking roadmap.

The canonical roadmap is maintained at the repository root:
[ROADMAP.md](../../ROADMAP.md).

Keep one roadmap so planned work, release status, and version milestones do not
drift between duplicate copies.
