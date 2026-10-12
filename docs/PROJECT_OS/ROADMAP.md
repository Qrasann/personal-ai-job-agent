# Project roadmap

Latest incremental source-coverage step: `/sources` now includes a manual
Georgia link to jobs.ss.ge, which exposes a broader local vacancy catalog.
Automated extraction remains off because a reusable API/permission was not
verified. Targeted source tests pass; full validation and deployed Telegram
confirmation remain open.

Latest operational improvement in progress: public HH `ConnectError` is now
skipped immediately so a failing HH request does not consume a retry before
other sources finish. Other transport errors keep their existing bounded
retry; verification and deployment are pending. This changes source resilience,
not the matching/ranking roadmap.

The canonical roadmap is maintained at the repository root:
[ROADMAP.md](../../ROADMAP.md).

Keep one roadmap so planned work, release status, and version milestones do not
drift between duplicate copies.
