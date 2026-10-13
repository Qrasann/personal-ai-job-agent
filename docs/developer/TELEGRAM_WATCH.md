# Telegram Channel Watch — Bot API stage

Commands (registered users only):

- `/channels` or `/channels list|stats`: subscriptions and persistent counters.
- `/channels add @channel [career|relocation|both]`: create/update, default both.
- `/channels on|off|remove @channel`: enable, pause or remove subscription.
- Public `https://t.me/channel` or numeric `-100…` channel ID also accepted.

This consumes new Bot API channel_post updates, including photo captions. Bot
must have access to that channel; saving a subscription does not join the bot,
read arbitrary public channels or scan history. Forwarded vacancies remain a
separate manual ingestion path. No Telegram user-account/session credentials,
MTProto history, employer applications or recruiter messages are introduced.
Official Bot API visibility: https://core.telegram.org/bots/faq#what-messages-will-my-bot-get

Subscriptions/counters live per user in existing RuntimeState JSON. Seen events
use existing SeenMessage with `(user_id, source, message_id)` uniqueness; no DB
migration. Username and numeric aliases union scopes; each search profile runs
once. Pause, disabled Telegram source and inactive search profiles are honored.
Original score formulas/thresholds, persisted vacancies, matches and notification
deduplication remain in ingest_and_match. Good/Stretch counters count profile
assessments (one post may produce two), not unique vacancies or hiring promises.

A per-user async lock serializes update/configuration operations in the existing
single polling process. Seen records survive restart and subscription removal;
no seen record is written if processing fails, so a redelivered post can retry.
Existing match/notification deduplication protects partial-profile retries.
Errors are local warnings/counters, never raw post/credential logs. Corrupt
configuration is preserved and that subscriber skipped, others continue.

Limitations: single polling process; no distributed/exactly-once guarantee.
Scoring, seen records and statistics are separate transactions; crash windows
can replay processing or undercount counters, existing notifications still have
their usual deduplication contract. Bot API does not promise a failed update
will be redelivered; the persistent queue below handles recorded failures. Edited-post
processing and rich post metadata are next; no historical backfill is claimed.

## Structured posts and forwarded provenance

Explicit Role/Position/Вакансия, Company/Компания, Location/Локация and
Work mode/Формат labels are used; free-text offices are not location evidence.
Country/city scope remains source evidence, not work permission. Generic
headers and hashtag-only lines are skipped for title extraction.
Channel forwards preserve original numeric channel/message identity and public
URL if provided. Photo captions also route through manual ingestion. Manual
and automatic delivery share a per-user lock/SeenMessage replay guard; paused
manual processing with zero assessments does not consume a seen record.
The seen marker is per-user/post (no historical rescore/backfill when changing
subscription scope); per-profile historical rescore is a separate future task.

## Bounded persistent retry

Failed selected deliveries store source identity/body in RuntimeState JSON, max
100 per user. Scheduler retries five posts total per minute; /channels retry
retries up to five for the requesting user. Failed entries rotate; disabled
subscriptions and paused users retain their queue, no hidden scope expansion.
Overflow does not evict earlier entries: failures outside the full queue are
counted visibly and need redelivery/manual forward. Bodies bounded16384 chars
(Bot API messages/captions are smaller); no raw content in warning logs.
Retry is recovery of accepted live updates, not reading channel history.
Existing single-process/transaction caveats remain; edits are not implemented.
