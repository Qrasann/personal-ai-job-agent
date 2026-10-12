# Project roadmap

Latest operational improvement in progress: public HH `ConnectError` is now
skipped immediately so a failing HH request does not consume a retry before
other sources finish. Other transport errors keep their existing bounded
retry; verification and deployment are pending. This changes source resilience,
not the matching/ranking roadmap.

The canonical roadmap is maintained at the repository root:
[ROADMAP.md](../../ROADMAP.md).

Keep one roadmap so planned work, release status, and version milestones do not
drift between duplicate copies.
