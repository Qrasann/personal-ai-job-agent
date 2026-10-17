# Telegram Channel Watch — Bot API and optional local folder intake

## Optional Telegram folder user client (offline-tested; live acceptance pending)

The private folder intake uses Telegram's official `chatlists.checkChatlistInvite`
preview through optional Telethon 1.x. It does not import the folder, join chats,
send user-account messages, or read private conversations. Install locally with
`.venv/bin/python -m pip install -r requirements-telegram-user.txt`. Obtain an
owner-controlled API ID/hash from my.telegram.org and set `TELEGRAM_API_ID` and
`TELEGRAM_API_HASH` locally; never commit them or the session. From the repo root,
run `.venv/bin/python scripts/telegram-folder-watch inspect`, approve the
interactive account sign-in on the user's computer, and enter the folder link
at the hidden prompt. The private inventory appears under
`~/.local/share/personal-ai-job-agent/telegram-folder/folder.json` (0600). It
contains Telegram-reported numeric IDs, usernames, types and preview status;
all channels start disabled. A preview is not proof of joined/read access.

Review the inventory locally, select only accessible broadcast channels by
setting `enabled: true` and a `career`, `relocation` or `both` scope. Supergroups
and peers no longer joined are excluded. Run `.venv/bin/python
scripts/telegram-folder-watch probe` to check read access to enabled IDs without
printing post text. Then run `watch` only after configuring the existing bot
database and owner ID. The runner rechecks the folder preview and current IDs,
disables account-wide updates, and polls **only** selected broadcast peers every
five minutes (two seconds between requests, up to 20 newer posts per channel
per pass). It hands posts to the existing `telegram_watch.consume_channel_post`
pipeline. The first pass anchors at the latest post without scanning history;
later passes resume from a private, atomic `cursors.json` (0600), including
bounded catch-up after restart. Very large backlogs take multiple passes; edits
are not replayed. Bot notifications still use the normal bot pipeline; the user
client itself does not send. Only known public usernames produce public post
links. No folder invite, API credentials or session belong in GitHub or logs.
A single local runner is expected; do not launch duplicates.

Source identity is `channel:<numeric ID>:<message ID>`, with Telegram's post
date saved in UTC and retained in the bounded retry queue. Explicitly labeled
candidate CV posts and ads are counted separately and skipped. Other posts are
vacancy **candidates**, not verified job offers; Good/Stretch count profile
assessments and can exceed unique posts. Live false-positive/yield measurement
and live restart catch-up validation are still required before broad rollout. Telegram
API terms and rate limits apply; no account login or live channel read was done
in the offline implementation checkpoint.

Official method: https://core.telegram.org/method/chatlists.checkChatlistInvite
and user authorization: https://core.telegram.org/api/auth .

Commands (registered users only):

- `/channels` or `/channels list|stats`: subscriptions and persistent counters.
- `/channels add @channel [career|relocation|both]`: create/update, default both.
- `/channels on|off|remove @channel`: enable, pause or remove subscription.
- Public `https://t.me/channel` or numeric `-100…` channel ID also accepted.

This consumes new Bot API channel_post updates, including photo captions. Bot
must have access to that channel; saving a subscription does not join the bot,
read arbitrary public channels or scan history. Forwarded vacancies remain a
separate manual ingestion path. No Telegram user-account/session credentials,
MTProto history, employer applications or recruiter messages are introduced by
the Bot API path. The optional local client above is a separate process.
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
Pause-state and active-search-profile lookup errors also skip only that
subscriber; later subscribers still receive the live post. A skipped lookup
is not marked seen, so a later Bot API redelivery can try again. It is not
added to the retry queue because the subscription/scope could not be verified.
Retry-state lookup failures likewise skip that subscriber and continue the
bounded queue for others; existing queued entries are preserved.

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
