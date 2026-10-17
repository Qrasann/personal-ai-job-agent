# Job notification delivery (v3.5.7 development)

## Approved behavior

The owner chose **at least once**: prioritize delivery of matching vacancies even when an uncertain Telegram result can create a duplicate. This is an alerting policy, not permission for automatic HH job applications or recruiter messages.

Job alerts have no Telegram-side idempotency key. A client timeout after server acceptance, process crash after send, or failed PostgreSQL commit after send may cause a second Telegram message. **Do not promise exactly once.**

## Durable protocol

- Each initial qualified JobMatch writes one RuntimeState row with key jobnotify:<match-id> and JSON value (status, attempt count, frozen alert payload, next_attempt_at, claim token, latest Telegram message ID and a bounded event journal).
- The claim holds a PostgreSQL row lock on the owner and JobMatch, ensuring only one in-flight claim per match across overlapping scans or independent workers. The claim is committed **before** Telegram I/O. No new database migration/table is required.
- Delivered confirmation commits both journal sent and JobMatch notified in one DB transaction. Failed sends record retry and exponential backoff 60s, 120s, 240s, capped at 3600s.
- After an ambiguous result the original sending lease expires after 120s; the scheduler reclaims and retries. Late success from an older claimant is fenced by a token and cannot overwrite a newer claim. A duplicate external message is still possible and intentional under the chosen policy.
- The scheduled retry worker runs every minute, including at startup, independently of source discovery. It reads only due non-final journal entries. Paused users receive no retries until unpaused.
- Retry sends the original frozen alert text, URL and buttons, *not* re-fetched text that could have changed or disappeared.
- The /delivery command shows the current user's latest outcomes and attempt counts, without displaying stored vacancy payload or credentials.
- Existing notified JobMatches from before this change are unaffected; they have no new journal row and should not be resent.

## Failure modes and privacy

- First reservation failure: do not send. The scan may retry on rediscovery.
- Telegram send failure: record retry and exponential backoff. If DB also fails, keep the lease until its expiry.
- Telegram succeeds but DB update fails: keep sending until lease expiry, then retry; duplicates possible.
- Invalid/malformed journal data is not overwritten automatically. Investigate it, do not echo raw provider errors.
- Row claims are per user and match. Journal growth/retention and multi-instance performance are not yet accepted.
- The journal is **only for scored job alerts**. Source diagnostics, recruiter chat alerts and channel watcher notifications retain separate existing mechanisms.

## Checks and limits

Run isolated PostgreSQL tests, especially tests/test_notification_delivery.py: claim concurrency, lease fencing, retry timing, user isolation, uncertain acknowledgments, and ingestion-to-alert flow. CI also builds Docker and scans secrets.

A green CI does not prove live Telegram delivery. Deploy only after explicit production approval and backup. No schema bump from this change. PR #27 (separate Application/job FK migration) remains unmerged and needs independent review.
