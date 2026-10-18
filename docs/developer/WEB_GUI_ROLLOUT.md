# Web GUI rollout and rollback gates

This runbook applies to the separate `/mnt/Storage/AI-Job-Bot/repo` runtime. The development checkout is not the runtime. The Web GUI Compose overlay is opt-in and binds `127.0.0.1`; never publish it to a public interface without an explicit access design.

## Verified development evidence

- The development code and read-only runtime check both report PostgreSQL schema version 8 on 2026-10-18. The Web GUI and per-user scan lease add no schema migration.
- The isolated PostgreSQL suite passed after the current v3.5.7 feature merge. A separate HTTP/PostgreSQL regression traversed all nine GUI stages, saved manual statuses, exported a frozen package and denied a foreign package.
- A local validation image built. These results do not establish production source quality or release acceptance.

## Before starting the runtime service

1. Obtain a current owner-private PostgreSQL custom-format backup outside either repository. Keep directory permissions at `0700` and the dump at `0600`; do not print or commit its contents. Verify `pg_restore --list`, then perform a full restore into a separate private PostgreSQL instance and verify schema version 8 and representative row counts. Record backup path, timestamp, checksum and restore result privately.
2. Record the current running app image ID and Compose configuration without printing `.env`. Keep the old image available for rollback. Confirm the target source tree still expects schema version 8 and that no new migration is pending.
3. Run the full isolated PostgreSQL suite, secret scan, Docker build and required GitHub CI on the exact rollout commit. Review the `WEB_GUI_TOKEN` requirement (at least 24 characters), `TELEGRAM_ADMIN_CHAT_ID`, database URL and localhost port binding without exposing values.
4. Confirm owner access to `127.0.0.1:8080` through a local browser or a private tunnel. Do not add a public reverse proxy as part of this rollout.

## Controlled rollout and smoke

Use the runtime Compose project `repo` and both Compose files. Start only the `web` service after the backup and gates pass; preserve the existing named PostgreSQL and storage volumes. Verify an invalid login is denied, the owner login works, and Dashboard → Search → Jobs → Review → Profiles → Sources → Relocation → CV → Applications load owner data without a 500 response. Check one source-specific vacancy detail and one frozen application export against their original posting/package. Use an isolated test database for write-path acceptance; do not create dummy jobs or status events in production.

Confirm the existing Telegram bot still responds to `/scanstatus`, `/jobs career`, `/jobs relocation` and `/review`. For a user-requested real scan, trigger `/scan` or Search, then compare per-source and per-profile counts and partial-error codes. Inspect a small sample of live links and retain unknown visa/work-right evidence as unknown. No real application or recruiter message is part of smoke.

## Rollback

If only the Web GUI fails, stop only the `web` service and preserve the database and volumes. If the bot code was updated with the GUI branch and regresses, redeploy the recorded previous app image/config without resetting Git or dropping volumes. This increment adds no schema migration, so a database restore is not the routine rollback. Restore the verified backup only after separately assessing data loss since backup and obtaining owner approval for that destructive step. Recheck Telegram status and search after rollback.
