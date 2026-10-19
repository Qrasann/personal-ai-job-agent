# Handoff

Standing owner mode: **MAXIMUM TOKEN ECONOMY**. Continue with Main alone for ordinary work, read only the compact current handoff plus task-relevant files, run targeted tests before risk-driven expansion, and do not repeat the known unchanged full-pytest stall. Fast/Deep are exceptions justified by total cost/risk, not defaults. Do not claim visibility into Codex quotas unless the environment exposes it.

## Current checkpoint — Telegram pilot guard and Employer common search (2026-10-19)

Branch `wip/telegram-pilot-20261019`, latest local checkpoint `a13a508` (after WIP `86536a7`). Added a fail-closed guard requiring an existing authorized MTProto session for probe/sample/watch; it disconnects and exits before Telethon can offer an interactive login. Private inventory and existing MTProto session are available, but this shell has no API ID/hash and no sample file. No channel read was made. When the owner runs locally with API credentials present, the single bounded read-only command is `TELEGRAM_PILOT_POST_LIMIT=20 .venv/bin/python scripts/telegram-folder-watch sample && .venv/bin/python scripts/telegram-channel-pilot`; it samples at most 20 posts for the selected three public channels and analyzes the private file, without notifications or database writes.

Employer Career Watch reads reviewed Greenhouse, Lever and SmartRecruiters feeds into common search with bounded requests and allowlisted URLs; custom-page and overlapping direct-adapter behavior stays explicit. A local Job Location Intelligence slice now resolves only exact supported `City, Country` labels and structured non-remote SmartRecruiters locations; remote, regional, multi-location and ambiguous US-state values remain unknown. Source text and resolution provenance are retained. Focused geo/employer tests: 18 passed; compileall, diff check and secret scan passed. The earlier 2026-10-19 read-only probe found all 14 watched provider IDs current across 12 employers. `jobbot status` confirms the running app and healthy PostgreSQL; manual command remains intact. Autostart is still enabled: `ai-job-bot.service` enabled, Docker enabled, both `repo` containers `unless-stopped`, while system/user timers have no AI Job Agent task; earlier read-only inspection found no relevant cron/KDE autostart entry. Current owner instruction forbids system-service changes without separate authorization. No production DB settings or data changed.

WIP code checkpoint `3cedf1b` is pushed; subsequent local eligibility wording change is uncommitted pending its target gates. Draft PR [#56](https://github.com/Qrasann/personal-ai-job-agent/pull/56) targets `feature/v3.5.7-international-market-coverage`. Latest CI run [39288215789](https://github.com/Qrasann/personal-ai-job-agent/actions/runs/39288215789) is in progress; `a13a508` CI passed, and `29a14dc` all 3 checks passed. Job Location Intelligence passed 18 focused tests; eligibility requirements (generic authorization/permit, legally-authorized/eligible-to-work wording) passed 98 related tests. Match writes now store assessment version 1; unversioned legacy Good cards suppress their old score and direct the owner to `/scan`, whose regular matcher refreshes only rediscovered rows. Non-actionable titles retain a stronger repeat-review warning. Targeted review/scoring/refresh tests: 94 passed; isolated PostgreSQL repository round-trip test passed. No production DB/runtime access, bulk rescore or status mutation. Manual-start remains out of scope absent separate authorization. Applicant Count remains blocked until a permitted public source provides dated application counts; preserve unknown legal status without authoritative vacancy evidence.

## Current restart point — compact Telegram vacancy workflow (2026-10-19)

Working branch `work/telegram-notification-reliability-20261018` starts at merged feature commit `a1debc9`. The current uncommitted slice replaces the default `/scanstatus` diagnostic wall with a short health/Good/Stretch/new summary and an inline details toggle. `/review` is a single decision card and retains owner-checked back/next/save/skip while adding Main menu. `/job` now starts compact and exposes Requirements, Description, Hiring terms, Competition and Source tabs; callbacks strictly parse IDs, call the existing owner-scoped detail service, and edit the same message. Full legacy detail rendering remains available internally, so no evidence or provenance was deleted. Persisted `applicant_count_v1` is displayed only for non-negative integer `kind=applications` evidence with source/date; views and invalid values stay `Нет открытых данных`. Structured eligibility continues to separate remote scope, residence/citizenship, authorization, sponsorship and relocation; source provenance now links a safe official URL when present.

Targeted Telegram/scoped-detail/scoring suites pass 196 tests; compileall, secret scan and diff check pass. The DevOps Volunteer rule is present in dev and fit-skips/caps the role at 58, while the card explicitly labels volunteer/unpaid text. A read-only SELECT in the isolated Web acceptance database found two older stored `DevOps Volunteer` assessments at 69 and 60 (`new`), confirming that persisted pre-fix rows are not retroactively rescored merely by changing code. The owner's production screenshot showed Makerble at Good 88/100; production PostgreSQL was not queried or changed. Runtime reports v3.5.7 but its version string alone cannot prove this later scoring checkpoint is deployed. Remaining UX work: verified adapter applicant-count capture, optional secondary sort, ReplyKeyboardMarkup, richer match/missing-skill summary and isolated visual before/after Telegram acceptance.

The authorized MTProto pilot remains limited to `@devops_jobs_feed`, `@itjobsgeorgia` and `@vgrecruitingit`, without joining. This shell still has neither `TELEGRAM_API_ID`/`TELEGRAM_API_HASH` nor a private session/inventory, so no interactive authorization or channel read was possible. Continue the pilot when the owner supplies those values locally; never commit the session. Employer Career Watcher remains P0. Web GUI, production bot/database/volumes and external applications/messages remain untouched.

## Current restart point — Search Quality & Worldwide Relocation (2026-10-18)

The owner froze further Web GUI redesign and feature work. Preserve the existing MVP, its tests and its Firefox acceptance evidence; only critical security/data-correctness fixes may touch it. DEC-001–015 remain approved, while the current order is Search Quality & Coverage, Worldwide Relocation, Telegram source pilot and button-first Telegram UX (P0), Candidate-to-Offer (P1), then Skill Check/Interview/AI Router/Stack Watch (P2). Telegram Mini App is deferred.

Branch `work/web-acceptance-quality-20261018` started this stage clean at `8434014`; roadmap/worldwide/TLS checkpoint `e9e0f08` is committed. Himalayas previously made no global request when target countries existed and considered only the first three countries while parsing restrictions. Code now keeps at most three country probes, adds one worldwide probe per bounded query, and matches returned restrictions against all configured countries. A read-only public probe returned 8 unique relevant DevOps cards: 7 through the global discovery request (including one with a regional residence limit) and 1 Germany-limited result; one country request failed. Visa, relocation support and right-to-work remain unknown. HH probing resolved IPv4 DNS but repeatedly exposed `ssl.SSLEOFError` below `ConnectError`, while another attempt reached HTTP 403. The safe typed-cause classifier now reports this as `TLS_CONNECTION_FAILED`; cooldown behavior is unchanged. Relevant suites passed 201 and the combined source/HH isolation suite passed 142. A complete 1331-test PostgreSQL run again stopped returning output around the first HH private-scope test, so it is not claimed as passed; the separate tmpfs test DB was stopped without deleting any volume.

Read-only acceptance aggregates give the first source usefulness baseline. Himalayas dominates current candidate yield; Job Bank contributes one qualifying non-IT warehouse role from 12; EURES has volume but no Good after role filtering; RemoteOK/Arbeitnow are low-volume with no Good; HH and multiple ATS/Georgia endpoints remain network/access-limited. Sampling the qualifying titles exposed `Site Reliability Engineer Expression of Interest Form` as a second non-actionable false Good beside the already-fixed volunteer role. Working scoring code retains this exact title class for manual review but fit-skips and caps it at 58; targeted scoring suites pass 79. Finish static gates and checkpoint, then inspect the remaining Himalayas Good set and suitable exclusions before expanding sources. Do not change production, the running Telegram bot, production PostgreSQL or any existing volume; do not send applications or messages.

## Current restart point — isolated Web acceptance and source quality (2026-10-18)

Dev was clean and fast-forwarded to merged feature commit `5331294` (PR #52). A standalone `jobagent-web-accept-20261018` Compose project is running on localhost port 18080 with its own PostgreSQL on 55433 and its own named database/file volumes; it does not load `.env` or reuse project `repo`. Firefox 158 WebDriver BiDi completed owner login, all ten pages (Dashboard, Search, Jobs, Review, Profiles, Sources, Relocation, CV, Applications, Diagnostics), a Candidate Fact write, manual application-status write, detail and export-link checks. This is real browser evidence against fixture data, not production acceptance. The owner still needs to complete visual/user acceptance. Keep the stack available until the owner responds; do not remove its volumes.

The owner also launched a permitted source-backed scan in this isolated stack. After normalizing the acceptance profile role from compound `DevOps / SRE` to `DevOps Engineer`, the control pass processed 84: Career-first 15, all scoring-filtered; Relocation-first 69, with 9 Good and 60 filtered. Source totals were Himalayas 34 (partial, 8 Good), EURES 30, Job Bank 12 (1 Good), RemoteOK 6 and Arbeitnow 2; several ATS/HR.ge requests had controlled network failures. The minimal acceptance profile has no real owner commercial-history facts, so Career score yield is not a valid measure of owner fit. Manual sampling found EURES generic `Engineer` leakage and a Himalayas `DevOps Volunteer` Good false positive. Working code now removes generic EURES query tokens when a specific token exists and keeps explicit volunteer/unpaid titles visible but fit-skipped/capped at 58. It does not change thresholds or infer relocation support.

Verification: focused regressions 65 passed; broader EURES/RemoteOK/Himalayas/discovery/diagnostics/scoring suites 183 passed; compileall, secret scan and diff check passed. Exact acceptance `init`/`web` images built, the idempotent one-shot schema/owner initializer passed, and only the isolated Web container was recreated with database/file volumes preserved. Firefox then repeated authenticated traversal of all ten pages successfully; existing browser sessions need to log in again after that restart. A full PostgreSQL run started on separate tmpfs project `jobagent-dev-tests-20261018` but its runner ended without a final pytest summary after 16%, so it must not be claimed as passed; the test DB was stopped without volume deletion. External public vacancy pages also failed to render through the automation browser, so stored source cards were sampled but external link validity remains open. Next: finish owner visual acceptance, rerun the complete isolated PostgreSQL gate, then publish the quality fixes and continue link sampling/zero-yield diagnosis. Production runtime, Telegram bot, PostgreSQL and volumes were untouched; no application or message was sent.

## Historical handoffs

## Current handoff — 2026-10-18 HH real-yield stabilization

PR #51 already contains the connected Web MVP; working code now also fixes the concrete real-source sample where HH returned teacher/sales titles for `cleaner`. Both HH API and web fallback require a meaningful query token in title, excluding generic role words. Targeted HH suite passed 19; full isolated PostgreSQL suite passed 1327; test DB is stopped. Commit/push code/tests/docs and wait for exact-head CI, then merge to the feature branch. Existing runtime data and services remain unchanged; refreshed yield requires gated deployment and rediscovery.

## Current handoff — 2026-10-18 real search active, Web PR #51

Draft PR #51 targets the feature branch at code/docs checkpoint `c83ded2`; CI is running. Read-only runtime logs and aggregate state confirm the existing Telegram scheduler completed a real 09:12:07–09:15:56 UTC pass with 11 successful source aggregates and 271 processed vacancies. Career-first: 52 Good, 26 Stretch, 144 scoring-filtered. Relocation-first: 0 Good/Stretch, 49 scoring-filtered and 50 preference exclusions. No new notification was emitted. This confirms active real search but not useful Relocation-first yield. Commit/push this evidence, require exact-head CI, then sample a few current links and continue gated localhost Web rollout. Runtime and production DB were not changed by development actions.

## Current handoff — 2026-10-18 integrated Web MVP stabilization

The connected daily Web MVP is committed through `e856813`. Full isolated PostgreSQL suite passed 1325 tests; `job-agent-web-mvp-validation:local` built successfully; the test database is stopped without volume deletion. Finish final static checks and checkpoint this documentation, then push the three post-PR-50 MVP commits, open a feature-targeted PR and require exact-commit CI. After publication, use read-only runtime evidence to confirm fresh Telegram Career-first/Relocation-first search activity before gated localhost Web deployment. Runtime remains unchanged.

## Current handoff — 2026-10-18 connected daily Web MVP

Dashboard/Diagnostics is committed at `23bcc7b`; Jobs/Review is committed at `88b4feb`. The working tree completes Search readiness/persisted status and Applications status/text filters, frozen-package cards and safe external links. Career-first and IT/non-IT Relocation-first configuration is visible without mixing in technical telemetry. Web unit suite passed 18; combined owner-authenticated HTTP/PostgreSQL Web suites passed 19. The isolated test database is stopped. Finish static gates and checkpoint, then run the full PostgreSQL suite and Docker build as the integrated MVP stabilization stage. Runtime remains unchanged and live browser/source acceptance is still pending.

## Current handoff — 2026-10-18 Jobs/Review daily workflow

On top of committed Dashboard/Diagnostics checkpoint `23bcc7b`, the working tree adds Career/Relocation, status and title/company filters to Jobs/Review and compact vacancy cards with known metadata, collapsed scoring reasons and explicit manual package preparation. Save/skip/prepare retain existing owner checks; no external submission path was added. Web unit suite passed 16 tests; combined owner-authenticated HTTP/PostgreSQL Web suites passed 17. The isolated database is stopped. Finish static gates and checkpoint, then continue Search/Application clarity before integrated MVP stabilization. Runtime remains unchanged.

## Current handoff — 2026-10-18 concise Web scan results

Working tree adds a compact persistent Dashboard summary and separate Diagnostics page on top of checkpoint `9b7356d`. Dashboard shows scan status, processed/Good/Stretch/new totals, Career-first/Relocation-first results and daily workflow links instead of the raw JSON journal. Diagnostics shows sanitized source status, controlled codes and filter reasons without stored raw exception messages. Web unit suite passed 15 tests; combined owner-authenticated HTTP/PostgreSQL Web suites passed 16. The isolated test database is stopped. Finish static gates and checkpoint this increment, then continue Jobs/Review filtering and cards. Runtime remains unchanged.

## Safe restart checkpoint — 2026-10-18 Web GUI MVP merged

- GUI code on local branch `work/codex-main-20261018` is at `c7ce239`; this restart note is the following documentation-only checkpoint. PR #50 merged into `feature/v3.5.7-international-market-coverage` as `1131bc4`; both pull-request and push CI runs passed Python checks, Docker build and secret scan.
- The private owner-only GUI implements Dashboard → Search → Jobs → Review → Profiles → Sources → Relocation → CV → Applications on the existing PostgreSQL/backend. It includes real Career-first/Relocation-first scans, source evidence, below-threshold relocation leads, Candidate Facts, reviewed PDF/DOCX/TXT CV import, frozen application packages/history, CSRF/owner isolation and a PostgreSQL lease shared with Telegram/scheduled scans. The localhost-only Compose overlay is opt-in.
- Verification passed: full isolated PostgreSQL suite through 1318 tests before the last selector assertion; subsequent targeted scan/Web tests, the selector regression and the nine-page HTTP/PostgreSQL owner flow passed. GitHub CI is green on the exact merged commit. A private production dump was created outside both repositories with mode `0600`, `pg_restore --list` succeeded, and a full restore into a disposable tmpfs PostgreSQL verified schema 8 plus representative row counts. The disposable verifier and isolated test PostgreSQL are stopped; no Docker volume was deleted.
- Not finished: the Web GUI is not deployed or browser-smoke-tested against runtime; no `WEB_GUI_TOKEN` has been configured here. Runtime `/mnt/Storage/AI-Job-Bot/repo` and its production database were not changed. Live source usefulness still needs a small owner-requested Career-first/Relocation-first scan and link sample; no application or recruiter message has been sent.
- After restart: inspect Git/runtime status first, fetch the merged feature commit, confirm the private backup still exists, then prepare the exact runtime update and localhost Web service smoke using `docs/developer/WEB_GUI_ROLLOUT.md`. Do not start rollout until token/config compatibility is confirmed; preserve Telegram as the immediate search interface. Resume Telegram Folder Watcher, interactive Interview Agent, AI Router and international-source roadmap work after the GUI release gate.

## Current handoff — 2026-10-18 Web GUI PostgreSQL acceptance and rollout plan

Local code checkpoint `7c4215e` includes per-user scan coordination. New isolated HTTP/PostgreSQL acceptance passes: all nine GUI stages, real owner-scoped match/application status writes, frozen export and denial of another user's package. A read-only runtime check found schema 8, matching development's expected version 8. `docs/developer/WEB_GUI_ROLLOUT.md` now gives backup/restore, compatibility, private smoke and non-destructive rollback gates; none has been performed against runtime yet. GitHub push/PR remains unavailable after DNS and unsandboxed connection timeout, so CI is pending. Finish static checks/local checkpoint for this test/runbook, then retry publication when network returns. No runtime mutation or employer contact.

## Current handoff — 2026-10-18 cross-process scan coordination

The branch merged the latest remote v3.5.7 feature baseline at `b75d8f1`; full isolated PostgreSQL suite passed 1314 afterward. GitHub publication of `work/codex-main-20261018` failed on DNS inside sandbox and timed out outside sandbox; no Draft PR exists yet. Current working change adds a PostgreSQL transaction lease around scheduled, Telegram and Web GUI scans, with clear busy states and no overwrite of an active scan dashboard. PostgreSQL lock, cancellation, bot/dashboard and Web regressions passed 68 targeted tests; full isolated suite passed 1318 before the final skipped-dashboard selection assertion, which passed in a 9-test targeted run. The updated Docker image built; compileall, secret-scan and diff check passed. Test DB stopped without volume deletion. Local checkpoint remains; retry publication only when network is available. Runtime remains untouched. Then continue real-link sampling and backup/rollback/smoke gates for GUI deployment.

## Current handoff — 2026-10-18 local Web GUI launch path

Code checkpoints through `980e5c6` cover the private Web GUI, reviewed CV import and opt-in localhost-only Compose overlay. The base bot Compose service is unchanged. Both README files point to `docs/developer/WEB_GUI.md`; Compose configuration parsed with a dummy token and showed `127.0.0.1:8080` binding. The latest remote v3.5.7 feature baseline is being merged into this branch before Draft PR/CI; repeat the isolated PostgreSQL suite after that merge. No runtime release or production database mutation occurred. Next: coordinate bot/web scans, run browser/PostgreSQL acceptance, inspect real vacancy links and complete backup/rollback/smoke gates before starting this overlay against runtime.

## Current handoff — 2026-10-18 reviewed browser CV import

Branch `work/codex-main-20261018` has code checkpoint `03094e5`. Earlier checkpoints `56a71d7`, `ba76c4f` and `fe2259d` cover the nine-stage private Web GUI, below-threshold Relocation-first inspection, manual Candidate Facts and frozen application review. The latest code checkpoint adds PDF/DOCX/TXT upload, a 15-minute owner-scoped bounded preview, per-fact ADD/KEEP/UPDATE selection and explicit CV-only or CV+facts commit through the existing atomic repository path. Uploaded bytes are not retained; proposed facts remain unknown experience. Full isolated PostgreSQL suite passed 1314/1314; updated Docker image built; compileall, secret-scan and diff check passed. The test PostgreSQL container was stopped without volume deletion. Runtime was not modified. Next: cross-process scan coordination, real vacancy sampling, isolated browser/PostgreSQL acceptance, then backup/compatibility/rollback/smoke release gates.

## Current handoff — 2026-10-18 profile facts and application review

Previous local checkpoints `56a71d7` and `ba76c4f` built a private nine-stage Web GUI and below-threshold Relocation-first inspection. This working increment adds owner-entered Candidate Facts with required evidence and unknown experience as the form default, plus an owner-scoped Applications detail page showing the frozen package and status history before manual updates/export. Targeted application/Web tests passed 14/14; compileall and secret-scan passed. Final diff check and checkpoint remain. No external application or runtime change. Browser CV PDF/DOCX import, scan coordination, real vacancy sampling and release acceptance remain next.

## Current handoff — 2026-10-18 below-threshold relocation inspection

Local Web GUI checkpoint `56a71d7` passed 1306 isolated PostgreSQL tests, 6 targeted Web GUI tests, static gates and an isolated Docker build. A read-only aggregate runtime check found the current Relocation-first scan yielded no Good/Stretch, with technical/geography gaps; it did not justify inflating scores. Current working change adds owner-scoped `Jobs → Relocation ниже порога`, including filtered manual leads with reasons and preserving the domestic-onsite exclusion. Targeted Web GUI/search-preference tests passed 52/52; compileall and secret-scan passed. Final diff check and local checkpoint remain. Runtime was not modified. Follow with real link sampling, browser CV fact review, scan coordination and release gates; do not publish private profile or vacancy details.

## Current handoff — 2026-10-18 Web GUI MVP

Branch `work/codex-main-20261018` started clean at `34bd4d6c`. Owner moved a usable private Web GUI and real two-track search to P0. `app/web.py` now has owner-only local routes for Dashboard, Search, Jobs, source-specific detail/evidence, Review, Profiles, Sources, Relocation, CV and Applications, real repository actions, CSRF and owner checks, plus the existing `scan_for_user` and package preparation. `requirements.txt` adds explicit aiohttp. Full isolated PostgreSQL suite passed 1306 before the final source-detail route; targeted Web GUI tests passed 6/6 after it. `git diff --check`, compileall and secret-scan passed after the route. Runtime `/mnt/Storage/AI-Job-Bot/repo` was not changed; read-only Docker status showed `repo-app-1` up, but no real source acceptance or application send was performed. Next: browser/PostgreSQL acceptance, browser CV import with reviewed facts and bot/web scan coordination; prepare backup/rollback/smoke gates before runtime change. Existing Telegram `/parallelsearch on`, `/relocationroles`, `/scan` remains the immediate live-search route. Do not confuse offline tests with live yield.

## Current handoff — 2026-10-17 Telegram Georgia location

Feature includes merged PRs #46–#48 at `a2df2dc`; current branch is `work/telegram-georgia-location`. Red offline fixtures showed `Atlanta, Georgia` and `Savannah, Georgia` parsed as country GE. The narrow parser guard leaves their country unknown while `Tbilisi, Georgia` remains GE. Targeted Telegram suites: 57 passed, 1 skipped; full isolated PostgreSQL suite: 1300 passed. Static gates, local commit, PR/CI and feature merge are next. No live Telegram account access or production change. The two owner proposal files remain untracked. All 21 folder IDs/access remain unverified; owner-controlled local login and 2–3-channel live acceptance are still required.

## Earlier handoff — 2026-10-17 Telegram channel quality dashboard

Feature includes merged PRs #46 and #47 at `a11c176`; current branch is `work/telegram-channel-quality-stats`. A red regression showed `/channels` hid persisted filtered and duplicate counts and still implied Bot API was the sole automatic intake path. The view now displays received/processed, possible vacancies, non-vacancies, Good/Stretch, filtering, duplicate assessments, replays and errors; its header explains the optional local client. Offline unit suite: 1277 passed, 21 PostgreSQL tests skipped; this UI-only change did not start the isolated DB. Final static gates, local commit, PR/CI and feature merge are next. The two owner proposal files remain untracked/untouched. All 21 folder IDs/access remain unverified; private interactive login and 2–3-channel live acceptance are still required. No production or user-account action.

## Earlier handoff — 2026-10-17 candidate-header quality follow-up

Feature has merged PR #46 at `486819d` after Python/Docker/secret CI passed. Current branch `work/telegram-folder-post-quality` adds a narrow filter for four explicit candidate headers (`#OpenToWork`, `#ищуработу`, `Резюме:`, `Resume:`); regressions were red before the fix and the full isolated PostgreSQL suite passed 1298 afterward. Final static gates, commit, PR/CI and feature merge remain next. The two owner proposal files remain untracked and untouched. No local Telegram API credentials/session exist; the 21 supplied chat labels have no verified IDs/access. Owner must perform private interactive folder inspection and 2–3-channel live acceptance before wider activation. No production change or account login occurred.

## Earlier handoff — 2026-10-17 Telegram Career folder

Branch `work/telegram-folder-watcher` has PR #46 to feature; latest pushed merge checkpoint `c5bd6b6` incorporated a concurrent feature documentation commit `b74fa06` without discarding either set of docs. The two owner proposal files remain untracked/untouched. Owner's local 21-item folder manifest has no verified IDs/usernames/types/access, so no live channel claim. Optional local Telethon preview writes a private all-disabled inventory; selected broadcast IDs use bounded five-minute polling with account-wide updates disabled and private restart cursors. Telegram post date survives retry; explicit CV/advertising headers are skipped; channel counters label possible vacancy posts, Good/Stretch assessments, replays and errors. No user login or production change; API credentials/session are absent here. Final isolated PostgreSQL suite passed 1294 after scoped polling; the added publication-date persistence regression passed separately (1). Push the latest received-count fix to PR #46 and wait for green CI. See `docs/developer/TELEGRAM_WATCH.md` for private local setup and `TASKS.md` for acceptance. Next: 2–3-channel owner-controlled identity/access/yield acceptance, then gradual expansion. Do not publish invite/session or treat preview as read access.

## Current restart point (GitHub verified after PR #44, 2026-10-17)
- Feature baseline 8b33ee5, main v3.5.6, PR #18 Draft/open; PR #38–#44 merged. Verify the ACTUAL local HEAD/worktree and active Codex sessions on every restart.
- Last user-reported offline suite: 1257 passed, 21 skipped; compileall, secret scan and CI passed. No evidence of current production release or authorized real-channel/source acceptance.
- Follow root ROADMAP.md Unified execution priorities. Start with useful Career-first/Relocation-first source yield and a small authorized Telegram channel pilot, independently prepare v3.5.7 release gates. If blocked on permissions/runtime, work on P1 CV diff or interactive interview feedback.
- Do not mistake Telegram folder display names for IDs or accessible feeds. Do not commit invitation links, CVs, finances, credentials or MTProto sessions. Preserve the two user-owned untracked proposal files.
- PR #27/#31 were closed without direct merges: preserve behavior through regression and check patch equivalence before deleting unique branches.
- New requests extend the same plan. Main-first; no force push/destructive cleanup. Employer outreach needs user approval of exact vacancy/message. Production requires backup/migration/rollback/smoke acceptance.

## Historical handoff entries

### Older checkpoint — 2026-10-17

Feature/origin is synced at `0a50a29`; PRs #38–#43 passed CI and merged. PR #43 added isolated PostgreSQL `/prepare` failure→retry coverage (2 passed; full unit 1252 passed/21 skipped). Current branch `work/recruiter-eligibility-human-review` has a local Recruiter Agent fix: five English/Russian visa, work authorization and citizenship questions were incorrectly marked non-sensitive when model requested no review; explicit signals now force human review. Recruiter suite 15 passed; full unit 1257 passed/21 skipped; compileall/diff/secret scan passed. No messages sent and auto-reply remains disabled. Commit owned code/tests/docs only, never stage proposals; publish a PR to feature, wait for green CI and merge. Then continue with the next independent roadmap task. PR #18 still targets `main`; do not merge; production/runtime untouched.

### Older checkpoint — 2026-10-17

Branch `work/v357-rejection-diagnostics`; HEAD `55a259b`, 67 commits ahead of `origin/feature/v3.5.7-international-market-coverage`, none behind at last fetch. PR #32 targets feature and CI is running on this exact head (prior head `4a15adb` passed Python, Docker build and secret scan). The branch includes atomic/idempotent `/prepare`, v8 application-history protection, Russian Linux/Docker/Kubernetes Candidate Fit aliases, and HH ConnectTimeout cooldown. Full isolated PostgreSQL suite: 1231 passed; targeted package tests 58, Candidate Fit/model tests 63, HH timeout/ConnectError/TLS tests 3; compileall, diff check and secret scan passed. Isolated PostgreSQL container is stopped. PR #31 and #27 remain open; their equivalent behavior is in #32 and should be marked superseded only after #32 merges. PR #18 still targets `main`; do not merge it or alter `main`. Only untracked files are the untouched user proposals. Production runtime/DB/volumes unchanged. Next: await #32 CI; if green, merge to feature, then close #31/#27 as superseded and continue Source Intelligence/Relocation-first.




Older entries below are dated checkpoints and must not be treated as current Git/runtime facts.

## 2026-10-17 — Remotive remote-location evidence (historical)

The preceding handoff checkpoint was `d6917d3`, 61 commits ahead of feature origin. Subsequent entries below are historical evidence only.

## Current entry point — 2026-10-17 Candidate Fit contrastive negation

Branch `work/v357-rejection-diagnostics`; HEAD `74015e4`, 49 commits ahead of `origin/feature/v3.5.7-international-market-coverage`; no behind commits. Worktree is clean except the two untouched user proposal files. Reproduced `Requirements: Linux experience would be an advantage` being classified as required. Narrow English advantage/beneficial and Russian “будет преимуществом” skill-local phrasings now classify as preferred; no thresholds or weights changed. Fact-comparison/interview/resume suites: 80 passed; full unit suite: 1186 passed, 17 skipped; compileall, diff check and secret scan passed. No persistence changes. Source-ref latest-observation fix at `577859a` passed the full isolated PostgreSQL suite (1199); test DB stopped. No live acceptance or external action. Next: continue with another independent offline Relocation-first or Source Intelligence regression, preferably one affecting actual country eligibility evidence without inferring law.

## Current entry point — 2026-10-17 Candidate Fit contrastive negation

Branch `work/v357-rejection-diagnostics`; HEAD `82d6ebf`, 47 commits ahead of `origin/feature/v3.5.7-international-market-coverage`; no behind commits. Worktree is clean except the two untouched user proposal files. Candidate Fit regression: `Linux is not required, but Linux knowledge is mandatory` was classified as unknown because a negative occurrence masked the separate positive requirement in the same sentence. `_required_skill_in_section` now evaluates contrastive clauses separately; the positive clause must explicitly mention the skill. Fact-comparison tests: 44 passed; full unit suite: 1183 passed, 17 skipped. `compileall`, `git diff --check` and secret scan passed. No threshold, schema or database change. The preceding Source Intelligence fix at `577859a` selects the latest same-source posting after canonical dedupe; its full isolated PostgreSQL suite passed (1199). No live source/Telegram acceptance or external action. Next: continue a distinct offline Candidate Fit or Relocation-first quality issue; use isolated PostgreSQL only for persistence changes.

## Current entry point — 2026-10-17 latest source posting after dedupe

Branch `work/v357-rejection-diagnostics`; HEAD `577859a`, 45 commits ahead of `origin/feature/v3.5.7-international-market-coverage`; no behind commits. Worktree is clean except the two untracked user proposal files, untouched. Offline Source Intelligence regression reproduced that multiple provider IDs from one source can dedupe to one canonical Job while `source_ref(job, source)` always selected the oldest posting. Review/`/prepare` could therefore show stale URL, description and source evidence after a newer same-source observation. Non-exact source-ref lookup now selects the newest valid relocation evidence capture timestamp; exact provider-ID lookup is unchanged, and legacy refs without timestamps retain deterministic first-ref behavior. Focused tests: 38 passed; full isolated PostgreSQL suite: 1199 passed; compileall, diff check and secret scan passed; test DB stopped. Local code checkpoint `577859a`. `JobMatch` still does not store the exact provider posting ID, so source preference can differ from the provider that first produced a canonical match; this distinct limitation remains. No live source, Telegram, employer, production, push or merge actions. Next: investigate a reproducible Candidate Fit requirement-classification edge case; keep schema changes and live acceptance separate.

## Current entry point — 2026-10-17 regional relocation language evidence

Starting HEAD `f90e87d`. Armenia/Georgia review found relocation language evidence did not recognize Armenian or Georgian language mentions. Added canonical forms for English labels, Russian adjectives and native scripts; requirement status is inferred only from existing supported cues, otherwise stays unspecified. Targeted relocation evidence tests 21 passed; full isolated PostgreSQL suite 1176 passed. Current code/docs require final gates and local checkpoint; stop test DB before handoff. No law, eligibility, source or live claim changed. Next: continue a separate offline Relocation-first fit/evidence regression.

## Current entry point — 2026-10-17 EURES application links

Starting checkpoint `5af3361` (shared Telegram link rendering validation). EURES could persist credential-bearing application links and malformed IPv6 values could raise during detail parsing. EURES now accepts bounded HTTPS links without userinfo and falls back to the official portal otherwise; the limit matches Telegram clickability. Targeted EURES/vacancy-link tests 69 passed; latest full isolated PostgreSQL suite 1170 passed. Current code/docs require final gates and a local checkpoint; stop test DB before handoff. No URL was fetched/opened and no employer action occurred. Next: continue a distinct offline Relocation-first evidence bug review.

## Current entry point — 2026-10-17 safe Telegram source links

Starting checkpoint `8fd949c`. Reproduced that vacancy details made `javascript:`, credential-bearing and protocol-relative source URLs clickable. A shared bounded HTTP(S) validator now checks vacancy details, job-list source attribution and `/prepare` preview, rejecting unsafe schemes, userinfo, malformed authorities and oversized/control-character URLs. Link/rendering suites: 112 passed; full isolated PostgreSQL suite: 1164 passed; added unsafe-link cases: 6 passed. Full suite ran on isolated DB; it has been stopped. No outbound requests, source scraping, applications, schema or production changes. Final gates and local checkpoint remain. Next: continue a separate offline Relocation-first evidence case; no live eligibility claims.

## Current entry point — 2026-10-17 EURES timestamp validation

Starting HEAD `c77c087`. EURES freshness review found booleans accepted as numeric epoch milliseconds, producing false 1970 publication dates. They now remain unknown; valid numeric timestamps retain UTC normalization. EURES tests 21 passed; full isolated PostgreSQL suite 1161 passed. Code/docs need final gates and local checkpoint; test DB must be stopped before handoff. No live calls or schema changes. Next: continue Relocation-first quality with an offline evidence/eligibility regression that does not infer legal eligibility.

## Current entry point — 2026-10-17 EURES partial parsing

Branch `work/v357-rejection-diagnostics`; latest checkpoint `23b5418`. The follow-up reproduced integer `locationMap` raising `TypeError` and aborting the page. Malformed optional `locationMap`/`employer` values now become unknown/empty metadata; valid listing rows and siblings are preserved. EURES tests 19 passed; full isolated PostgreSQL 1159 passed. The isolated test DB is stopped. No live EURES/network, schema or production action. Next: continue a distinct offline Source Intelligence or Relocation-first regression check.

## Current entry point — 2026-10-17 EURES query relevance

Branch `work/v357-rejection-diagnostics`. Candidate Fit checkpoint `1cb278c` prevents generic GitLab repository/project mentions from becoming GitLab CI fit; explicit CI/CD/pipeline/runner terms remain recognized. Next increment reproduced and fixed EURES substring leakage (`Java` matched `JavaScript Developer`) using whole-token matching. EURES tests 18 passed; full isolated PostgreSQL suite 1158 passed. EURES change/docs are ready for local checkpoint after compileall, diff check and secret scan. Test DB must be stopped before handoff. No live source calls, schema changes or production actions. Next: continue Source Intelligence/Relocation-first offline investigation after checkpoint.

## Current entry point — 2026-10-17 GitLab CI Candidate Fit

Starting HEAD `3614f2a`; worktree had only the two user-owned untracked proposal files. Candidate Fit previously treated any GitLab mention as GitLab CI. A red test reproduced the false requirement/score. Matching now requires explicit CI/CD, pipeline or runner context with GitLab; repository/project-only text is not scored as GitLab CI. Existing explicit formulations still pass. Focused suites: 101 passed; full isolated PostgreSQL suite: 1157 passed. No weights, thresholds, schema, live sources or production changed. The isolated test DB is stopped. Next: continue Source Intelligence with a concrete offline adapter/provenance defect; retain uncertainty for live source quality and relocation eligibility.

## Current entry point — 2026-10-17 source first-seen provenance

Branch `work/v357-rejection-diagnostics`; latest local code checkpoint `b9e280f`. Vacancy details now show stable `JobSourceRef.first_seen_at` for “Источник обнаружен”; they no longer reuse the refreshed `relocation_evidence_v1.captured_at`. Legacy naive UTC timestamps are serialized with `+00:00`. Evidence capture remains independently available. Targeted detail/service tests 49 passed, full isolated PostgreSQL suite 1154 passed, compileall, diff check and secret scan passed. The isolated test DB is stopped. No schema, live source, production, Telegram send or external change. Next: identify a distinct offline Source Intelligence or Candidate Fit regression; preserve uncertain relocation eligibility and keep live yield blocked pending authorized runtime evidence.

## Current entry point — 2026-10-17 source relevance

Branch `work/v357-rejection-diagnostics`; read exact HEAD from Git. Latest offline increments: Application tracking rollback acceptance; preservation of canonical identity on blank-location refresh; OpenTelemetry Candidate Fit support; safe/bounded Himalayas application links and provider IDs; and concurrent cross-source canonical dedupe. The concurrency test yields one canonical Job and two provider refs. Full isolated PostgreSQL suite: **1154 passed**. No schema, scoring threshold, live source, or production changes. `/prepare` distinguishes post-save Telegram delivery failure and warns retry creates another draft. Test container stopped; no volumes removed. Two user proposal files remain untracked/untouched. No push, merge, deployment, live network, Telegram sends, production changes or schema changes. Candidate Facts ADD/UPDATE/KEEP was checked against implementation/tests; no duplicate work added. Next: inspect remaining Source Intelligence and Candidate Fit gaps; live relevance/HH root cause require authorized runtime evidence. Run compileall, `git diff --check`, and secret scan before committing the new concurrency acceptance. PRs #31/#27/#18 remain unmerged as last checked 2026-10-17. Exact remaining model quota percentage cannot be inspected here.

## Current entry point — 2026-10-17 v3.5.7 rejection diagnostics

Work branch `work/v357-rejection-diagnostics` starts from feature commit `2652416`; Draft PR #31 remains separate and unmerged. Search filtering now records deterministic settings-exclusion reasons and structured scoring-filter factors, aggregates them per source and per Career-first/Relocation-first profile, and renders a bounded list of leading causes in `/scan` and `/scanstatus`. Settings coverage includes domestic onsite, geography, required visa signal, strict salary floor and unknown-evidence preservation. Scoring coverage distinguishes hard fit, cap/risk and the largest weighted component deficit without parsing prose. Final targeted 66 passed; full isolated PostgreSQL **1061 passed**. No source query, threshold, production data or external request changed. Compileall, diff and secret gates passed before checkpoint. Next: use these measurements for source/query relevance; live measurement needs explicit authorization.

## Current entry point — 2026-10-17 `/prepare` integrity

Feature branch remote and local synchronized at `f53256e` after owner-authorized push of exactly three consolidation commits. The two proposal files remain untracked. Fresh login Bash now resolves `main`, `fast`, `deep`, `agents` to `~/.local/bin` symlinks into `scripts/job-agent-codex`; a `.bashrc` backup exists at `/home/roma/.bashrc.bak-job-agent-20261017-002714`. No archive/delete done. Archive candidates remain navigation-only `01a1277e`, completed Watcher primary `01a1375a`, and child rows marked candidate in `CODEX_SESSION_INVENTORY.md`; keep Main, three inaccessible Untitled tasks and large primaries pending owner review.

New local `/prepare` increment renders before persistence and commits prepared application, status event and match state atomically after owner/match validation. Render failure unit regression and isolated PostgreSQL transaction-failure injection passed; full isolated suite **1053 passed**. This remains offline acceptance only; no live Telegram or employer action. Next: test post-commit Telegram delivery failure/retry UX, then application tracking or source/fit roadmap work. Check current Git before continuing; this new increment has not been pushed.

## Current entry point — 2026-10-17 offline workflow follow-up

One new isolated-PostgreSQL end-to-end test in
`tests/test_offline_application_flow.py` covers source-scoped score/review/
saved/package export and another user's denial, including refresh of the
other source after package preparation. Baseline full 1051 passed; targeted
1 passed; final full **1052 passed**. Only `job-agent-tests` tmpfs PostgreSQL
was started on localhost 55432; production Compose/volumes untouched. This is
one of the requested 3–5 offline paths, not a live `/prepare` or HH acceptance.
The next independent roadmap increment should test the grounded `/prepare`
handler or a failure-injection path, avoiding a duplicate of this happy path.
The docs/launcher/test changes passed final local gates and were saved as
local checkpoints; check actual Git HEAD before further work.

## Current entry point — 2026-10-17 consolidation follow-up

Starting HEAD `374b375`, feature branch two docs commits ahead of origin; two
owner proposal files remain untouched/untracked. `codex agents` showed eight
tasks. Five correspond to indexed primary sessions. Three `Untitled task`
IDs (`01a1467c-5690`, `01a1467c-7836`, `01a14682-4913`) failed with
`no rollout found` and have no local SQLite history; manual review required.
All 17 child findings now have transfer destinations and remaining unknowns in
`CODEX_SESSION_INVENTORY.md`. No history archived/deleted.
`scripts/job-agent-codex` plus `~/.local/bin/{main,fast,deep,agents}` provide
one-word launchers. Main resumes exact existing thread `01a13763-4d60-7461-
bdcb-5d6f2076d0bb`; Fast/Deep use ephemeral read-only role TOMLs and were
actually seen on Luna/low and 6.1 Sol/high. `agents` opens the native browser.
These checks used model tokens; no cost saving is claimed. The startup/CLI
smoke changed no application code. Next: safely verify current test branch and
implement one focused offline roadmap increment. No main, production, release,
external employer action or proposal-file change.

## Current entry point — 2026-10-17

Audited code baseline `dabe9a3` on
`feature/v3.5.7-international-market-coverage`, then saved this documentation
inventory in a local checkpoint. The two user-owned proposal files are the only pre-existing
untracked paths; do not stage or modify them. This documentation-only pass
indexed local Codex history in [CODEX_SESSION_INVENTORY.md](CODEX_SESSION_INVENTORY.md)
and updated BRIEF from the stale `9b938ed` checkpoint. The index contains 5
primary and 17 child threads; one additional rollout has metadata only.
No session was archived/deleted, no test suite was rerun, and no main,
production, release or external action occurred. Session reports are dated
evidence, not current runtime/test claims. Resume with BRIEF's existing
priorities: HH submission reservation/ambiguous outcome and isolated DB
acceptance, notification journal/live Telegram acceptance, Application
history deletion safety, then offline end-to-end and roadmap quality work.
External/live or production steps still require separate owner authorization.
Keep candidate/relocation personal details in private context, not tracked
session summaries.

## Current entry point — 2026-10-16

Read [BRIEF.md](BRIEF.md) for the short active checkpoint, merged audit fixes #19–#26, and owner-approved Telegram at-least-once notification delivery merged via PR #28 (HEAD `9b938ed`). The independent schema migration PR #27 remains unmerged; no production changes. Read [delivery protocol](../developer/NOTIFICATION_DELIVERY.md) for retry semantics. The sections below are **historical** and their HEAD/test counts are not current. Feature tree at this entry: `9b938ed`, formal release/main v3.5.6. No deployment, release, production DB or main change.

## Current development checkpoint — 2026-10-15

Starting HEAD `06e7584`. Ingestion now selects a source ref by both feed and provider posting ID, then scores and notifies from that exact posting snapshot rather than a cross-source canonical Job. HH detail prefilter uses the exact provider ID. Red synthetic scoring regression and real PostgreSQL same-feed multi-ID test; full isolated PostgreSQL 1017 passed. Next: source quality and Candidate Fit explanation, then broader roadmap. No production, VERSION, deployment, push or external action. Owner proposal files untouched.

## Current development checkpoint — 2026-10-15

Starting HEAD `eceb80f`. Interview Agent now uses one labelled exercise for each explicit required/preferred skill OR group; it chooses the option best supported by Candidate Facts, without treating both alternatives as mandatory. Red regression and preferred-group fixture; full isolated PostgreSQL 1016 passed. Next: interactive answer/feedback design, plus Source Intelligence and Candidate Fit from the full roadmap. No production, VERSION, deployment, push or external action. Owner proposal files untouched.

## Current development checkpoint — 2026-10-15

Starting HEAD `9b36423`. `/prepare` preview now counts Telegram UTF-16 units instead of Python characters, bounds displayed cover text, and points to `/job` when HTML escaping makes a URL too long. Red emoji fixture reached 4991 units before; full isolated PostgreSQL 1014 passed after. Saved package/export retain full text and URL. Next: independent Candidate Fit/Source Intelligence quality, then Recruiter/Interview/AI Router/v4.x. No production, VERSION, deployment, push or external action. Owner proposal files untouched.

## Current development checkpoint — 2026-10-15

Starting HEAD `68c7e55`. Vacancy cards now show a bounded employer-question prompt for unknown relocation conditions and omit confirmed topics. It is source-evidence review guidance, not a candidate-specific legal conclusion. Synthetic/card regressions and full isolated PostgreSQL 1012 passed. Next: deeper Source Intelligence quality and Candidate Fit; then Application Package, Recruiter, Interview, AI Router and v4.x. No production, VERSION, deployment, push or external action. Owner proposal files untouched.

## Current development checkpoint — 2026-10-15

Starting HEAD `00a405c`. Model client/call failures and empty model output now use the local fact-grounded letter instead of aborting `/prepare`. A red synthetic provider-failure regression and empty-output fixture passed; focused 34 and full isolated PostgreSQL 1009 passed. Next: independent Source Intelligence, Candidate Fit or Relocation-first increment; continue Recruiter/Interview/AI Router/v4.x. No production, VERSION, deployment, push or external action. Owner proposal files untouched.

## Current development checkpoint — 2026-10-15

Starting HEAD `f344083`. Fixed fallback cover letter using inactive/deleted facts and claiming relevant experience with no active facts. Model Candidate Fact payloads now exclude deleted records too; drafts remain subject to owner review. Red synthetic regressions; focused 32 and full isolated PostgreSQL 1007 passed. Next: Application Package claim review, Source Intelligence quality and Relocation-first evidence utility; continue Recruiter/Interview/AI Router/v4.x afterward. No production, VERSION, deployment, push or external action. Owner proposal files untouched.

## Current development checkpoint — 2026-10-15

Starting HEAD `cf1111c`. Newly fetched HH detail caches are bound to the exact normalized source posting digest. When a source card changes, older verified cache stays in raw provenance but no longer overrides review/`/prepare`; the next HH detail read refetches. Row-locked save rejects a fetch raced by a newer card. Legacy unbound caches retain old behavior until refreshed. Synthetic and real PostgreSQL upsert/race regressions passed; full isolated PostgreSQL: 1004 passed. Next: broader source-quality utility or Relocation-first practical evidence, then full roadmap. No production, VERSION, deployment, push or external action. Owner proposal files untouched.

## Current development checkpoint — 2026-10-15

Starting HEAD `f226b9b`. `/prepare` preview now reserves space for selected provider identity and validated manual vacancy link, even when a dense CV checklist is shortened; unsafe links still yield a manual-search warning. Red synthetic fixture; focused 58 and full isolated PostgreSQL 1002 passed. Next: Source Intelligence cache provenance/freshness or Relocation-first evidence utility, then wider roadmap. No production, VERSION, deployment, push or external action. Owner proposal files untouched.

## Current development checkpoint — 2026-10-15

Starting HEAD `6fbab48`. Vacancy cards now show the selected provider posting ID and evidence-capture timestamp separately from publication time; this is ingestion provenance, not confirmation of availability. Red synthetic display regression; focused 58 and full isolated PostgreSQL 1001 passed. Next: Source Intelligence cross-source consistency/quality or Relocation-first evidence utility, then wider roadmap. No production, VERSION, deployment, push or external action. Owner proposal files untouched.

## Current development checkpoint — 2026-10-15

Starting HEAD `b289afe`. Candidate Fit high-experience gating now reuses required-year extraction, preventing a preferred 5+ band from marking a three-year job `skip`. Senior title policy and the existing stretch boundary remain. Red regression and additional preferred-only/required-five fixtures; full isolated PostgreSQL: 1000 passed. Next: independent Source Intelligence quality or Relocation-first evidence utility, then wider roadmap. No production, VERSION, deployment, push or external action. Owner proposal files untouched.

## Current development checkpoint — 2026-10-15

Starting HEAD `ccae426`. New Application Package snapshots and exports retain the selected source ID and provider posting ID. The mocked HH private path uses its selected source posting text; no live application occurred. Focused 67 passed; full isolated PostgreSQL suite exited 0. Legacy packages disclose unrecorded IDs without backfill. Next: independent Candidate Fit/source quality increment, then full roadmap. No production, VERSION, deployment, push or external action. Owner proposal files untouched.

## Current development checkpoint — 2026-10-15

Starting HEAD `0f87785`. Added per-source normalized posting snapshots at `upsert_job` and use the selected source's fields in vacancy details, Candidate Fit review and `/prepare`; verified HH detail cache takes precedence for draft text. A red synthetic regression showed the selected Jobs.ge evidence paired with an HR.ge description. Isolated PostgreSQL regression confirms snapshots refresh per source without mixing cross-source text or losing the details cache. Full isolated PostgreSQL: 996 passed. Older refs without snapshots retain canonical fallback until rediscovery; no historical source content is invented. Next: verify package snapshot/export and source-selection edge cases, then Candidate Fit and broader roadmap. No production, VERSION, deployment, push or external actions. Owner proposal files untouched.

## Current development checkpoint — 2026-10-15

Starting HEAD `bd297f3`. Fixed `/prepare` selecting a different source reference from vacancy details when a deduplicated Job has both `hr_ge` and `jobs_ge` records. Both paths now use the same deterministic order, so the package URL and mobility evidence match the reviewed source. Synthetic regression was red before the fix. Focused package/detail tests: 38 passed; full isolated PostgreSQL: 994 passed. This does not identify the original discovery source of a JobMatch. Next: continue Candidate Fit, Source Intelligence, Application Package or the remaining full roadmap. No production, external action or VERSION change. Proposal files untouched.

## Current development checkpoint — 2026-10-15

Starting HEAD `68d1096`. Fixed Arbeitnow assigning `DE` and a city to remote jobs whose free-form location can be “Worldwide” or office metadata. Remote records now retain the location as source text while work-country evidence remains unknown. Synthetic regression was red before the fix; focused adapter/evidence/preferences tests: 63 passed; full isolated PostgreSQL: 993 passed. Next: continue the full roadmap with an independent Candidate Fit, Application Package or source-quality task. Onsite Arbeitnow behavior remains as before. No production, VERSION or external action; proposal files untouched.

## Current development checkpoint — 2026-10-15

Starting HEAD `8e698f2`. Fixed “We provide no housing” / “We offer no accommodation” being interpreted as housing provision. The negative verb-object form now wins over overlapping positive text. Focused evidence/detail tests: 50 passed; full isolated PostgreSQL: 992 passed. Next: return to independent Source Intelligence, Candidate Fit, Application Package or recruiter/interview slices from the full roadmap. No production/external action or VERSION change. The two owner proposal files remain untracked and untouched.

## Current development checkpoint — 2026-10-15

Starting HEAD `aca6b36`. Fixed the explicit “We do not provide housing” form being interpreted as provision. Direct employer refusals are now false; “housing details” wording stays unknown. Synthetic regression was red before the fix. Focused evidence/detail tests: 50 passed; full isolated PostgreSQL: 992 passed. Next: continue another independent task from the full roadmap, especially source quality, Candidate Fit or Application Package. No production, VERSION, scoring or Candidate Fact change; owner proposals remain untracked and untouched.

## Current development checkpoint — 2026-10-15

Starting HEAD `409b9a0`. Fixed Relocation Evidence treating contradictory housing assertions as a confirmed refusal. Separate explicit provision/refusal statements now produce `unknown` and `conflicting_text`, retaining both excerpts; a single refusal remains false. Focused evidence/detail tests: 49 passed; full isolated PostgreSQL: 991 passed. Next: continue Source Intelligence, Candidate Fit, Application Package or other safe roadmap work. No legal conclusion, scoring, Candidate Fact, production or external change. The two owner proposal files remain untracked and untouched.

## Current development checkpoint — 2026-10-15

Starting HEAD `290d6bd`. Fixed RemoteOK's free-form `location` being treated as a normalized work country. The original string is retained as `source_location`; country/work-country are unknown and remote hiring scope stays unspecified. Regression reproduces “Worldwide” before the fix. Focused RemoteOK/location/relocation tests: 54 passed; full isolated PostgreSQL: 990 passed. Next: continue an independent roadmap task in Application Package, Source Intelligence or Relocation Evidence. Candidate Fit threshold fix remains in prior checkpoint `290d6bd`; Candidate Facts and scores outside country normalization are unchanged. No production/external actions. Proposals untouched.

## Current development checkpoint — 2026-10-15

Starting HEAD `e538e0f`. Fixed a reproduced Candidate Fit defect where “Minimum 3 years … required. 5 years of experience preferred” imposed a hard 5-year threshold. Explicitly preferred years are excluded from the required minimum; preferred-only years do not produce an experience requirement. Focused fit/resume tests: 60 passed; full isolated PostgreSQL suite: 990 passed. Next: continue the canonical roadmap with a focused Source Intelligence, Relocation-first evidence or Application Package task. Candidate Facts and Career-first/Relocation-first independence are unchanged. No production or external actions. Proposal files remain untouched.

## Current development checkpoint — 2026-10-15

Starting HEAD `4f79583`. Added synthetic Relocation Evidence regressions for Russian start timing: “Начать можно сразу” is immediate and “Выход на работу по договорённости” is negotiable. The latter was previously missed because the excerpt rule matched only infinitive `выйти`. Focused timing test: 1 passed; full isolated PostgreSQL suite: 988 passed. Next: continue the full roadmap with a practical, independent Candidate Fit or source intelligence increment; preserve Career-first/Relocation-first and unknown evidence. No scoring, Candidate Facts, legal conclusions or production state changed. Proposal files remain untracked and untouched.

## Current development checkpoint — 2026-10-15

Starting HEAD `629564c`. Added synthetic regression coverage for explicit
Russian “housing provided/not provided” wording. Bare mentions remain unknown.
Full isolated PostgreSQL: 988 passed; compileall, diff check and secret scan
passed. Continue Relocation Evidence locale/source work or Candidate Fit.
No production changes. Proposals untouched.

## Current development checkpoint — 2026-10-15

Starting HEAD `a632d80`. Vacancy detail cards now stay under 3900 UTF-16 units
even with all eight relocation fields and a large source description. A red
synthetic regression measured 6467 before the fix; the renderer now trims only
description content and retains evidence, scores and original link. Full
isolated PostgreSQL: 988 passed; compileall, diff check and secret scan passed.
Next: continue Source Intelligence/Relocation Evidence or Candidate Fit.
Production untouched; proposals remain untracked.

## Current development checkpoint — 2026-10-15

Starting from HEAD `a91d8c2`, extended Candidate Fit negation recognition to
include “No Kubernetes required”. Separate explicit requirements remain
unchanged. Focused Fit/score tests: 67 passed; full isolated PostgreSQL: 987
passed. Compileall, diff check and secret scan are pending before checkpoint.
Next: continue Candidate Fit/Source Intelligence. No Candidate Facts or
production data changed; proposal files untouched.

## Current development checkpoint — 2026-10-15

Started from HEAD `d8cfee1`. Candidate Fit now classifies direct skill-local
“is a plus” / “будет плюсом” wording under Requirements as preferred; separate
positive requirements remain required, and the established cross-section
priority is unchanged. Focused Fit/score tests: 66 passed; full isolated
PostgreSQL: 986 passed; compileall, diff check and secret scan passed. Next:
continue practical Candidate Fit or Source Intelligence. No Candidate Facts or
production changes. Test DB localhost:55432; proposals untouched.

## Current development checkpoint — 2026-10-15

Started from HEAD `0fff52e`. Legacy Application Package previews and exports
now explicitly disclose when no structured mobility evidence was saved and do
not backfill current source evidence into past records. Focused package/export
tests: 12 passed; full isolated PostgreSQL: 984 passed; compileall, diff check
and secret scan passed. Next: continue useful Candidate Fit, Source Intelligence
or Relocation Evidence work. No schema/production change; proposal files
untouched.

## Current development checkpoint — 2026-10-15

Started at Candidate Fit checkpoint `42a61f5`. Extended isolated repeat-source
PostgreSQL regression: source location evidence refreshes for the same provider
ID, but a previously prepared package keeps its earlier quote. Targeted DB
test: 1 passed. The prior full isolated suite passed 984 tests; this increment
changed tests/docs only. `git diff --check` passes. Next: continue safe Source
Intelligence or Candidate Fit work. No production change; proposal files remain
untracked and untouched.

## Current development checkpoint — 2026-10-15

Started from HEAD `ed0b991`. Candidate Fit no longer treats a supported
“no <skill> experience required” / “<skill> is not required” phrase as a
must-have solely because it appears beneath Requirements. The skill remains
unknown; separate positive requirements keep their status. Regression was red
before the fix. Focused Fit/score tests: 64 passed; full isolated PostgreSQL:
984 passed; compileall, diff check and secret scan passed. Next: continue
Candidate Fit or Source Intelligence/Relocation Evidence. No Candidate Facts,
production or external changes. Test DB localhost:55432; proposals untouched.

## Current development checkpoint — 2026-10-15

Started from HEAD `1d38344`. Added synthetic German Relocation Evidence for
residence scope, work authorization, housing, language and start timing. Fixed
a reproduced `Deutschland`/`Deutsch` false language match. Focused tests: 47
passed; full isolated PostgreSQL: 982 passed; compileall, diff check and secret
scan passed. Next: continue supported locale evidence or Candidate Fit. Test
DB localhost:55432/jobagent_test. No legal, score, production or external
changes; proposals untouched.

## Current development checkpoint — 2026-10-15

Started from HEAD `1ab8482`. Relocation Evidence now conservatively leaves
visa/relocation wording unknown when its per-component parse disagrees with a
sentence-level result, avoiding a refusal being attributed to the wrong
component. The existing scoring parser was not changed. Focused tests: 46;
full isolated PostgreSQL: 981 passed; compileall, diff check and secret scan
passed. Next: continue source evidence handling or Candidate Fit. No
Candidate-Fact/scoring/legal/production changes. Test DB localhost:55432;
proposal files untouched.

Started from HEAD `d0f2960`. Start-timing evidence now preserves exact source
text and classifies immediate, relative window, stated date, notice period and
negotiable wording; it does not assess candidate availability. Focused tests:
44 passed; full isolated PostgreSQL: 979 passed; compileall, diff check and
secret scan passed. Next: continue source-aware country/hiring evidence and
return to Candidate Fit/Application Package. No legal, scoring or production
change. Test DB localhost:55432/jobagent_test; proposals untouched.

Started from HEAD `54fac96`. Relocation Evidence now captures multiple
language observations in one posting independently; each stores required,
preferred, unspecified or conflicting status with its own excerpt. Explicit
English CEFR remains separate. Detail cards render the distinct conditions.
Focused tests: 87 passed; full isolated PostgreSQL: 978 passed; compileall,
diff check and secret scan passed. Next: continue source-aware country/hiring
scope or Candidate Fit work. No score/Candidate Facts/legal conclusion or
production change. Isolated test DB localhost:55432/jobagent_test; proposal
files untouched.

Started from HEAD `b3f99f2`. Prior work-authorization evidence now preserves
explicit negative statements as confirmed `false`, leaves missing statements
unknown and marks contradictory positive/negative source text as a conflict.
Focused tests: 82 passed; full isolated PostgreSQL: 977 passed; compileall,
diff check and secret scan passed. Next: continue conservative
Relocation-first/source-provenance work or resume Candidate Fit. Application
Package now snapshots this evidence at preparation time. No legal judgment,
scoring change, or production action. Isolated DB localhost:55432/jobagent_test.
Proposals untouched.

Started from HEAD `f5c1d21`. Application Package vacancy snapshots now deep-copy
the chosen source's `relocation_evidence_v1`; package exports serialize that
saved snapshot and do not query mutable JobSourceRef evidence. `/prepare`
preview includes the evidence capture time. HH application snapshots use the
same code path. Focused package/service/HH tests: 20 passed; repeat source
refresh PostgreSQL regression: 1 passed; full isolated PostgreSQL suite: 976
passed. Compileall, diff check and secret scan are pending before checkpoint.
No migration or production change. Next: finish those gates, then continue
Relocation-first country/source work or Candidate Fit. Proposals untouched;
isolated DB localhost:55432/jobagent_test.

Starting HEAD: `9702299`. Work-country evidence now preserves and displays a
source adapter's structured location/country excerpt beside its normalized
country value (for example, fixture-only `DE` plus `Berlin, Germany`). It does
not infer country from free text. Focused relocation/detail tests: 41 passed;
full isolated PostgreSQL: 975 passed. Next: review supported adapters for
structured locale provenance, then resume independent Fit/Source Intelligence
tasks. No scoring, Candidate Facts, legal conclusions or production changes.
Test DB: localhost:55432/jobagent_test. Owner proposals untouched.

Starting HEAD: `86e4c83`. Added distinct labels for explicit citizenship and
residence/location hiring restrictions, retaining the source excerpt and
provenance on vacancy details. This is only a description of source wording,
not a legal conclusion. Focused tests: 41 passed; full isolated PostgreSQL:
975 passed; compileall, diff check and secret scan passed. Next: improve
country/language mappings only from explicit source evidence, then resume
independent Candidate Fit/Source Intelligence work. No scoring or Candidate
Facts change; no live/legal/production action. Test database:
localhost:55432/jobagent_test. Proposals untouched.

Starting HEAD: `17dbeb7` (first Relocation Evidence checkpoint). Follow-up
classifies housing only when explicit provided/refused wording exists and
separates language required/preferred/unspecified plus explicit English CEFR.
Vacancy cards show these values with excerpts and provenance. Focused tests:
84 passed; full isolated PostgreSQL: 974 passed; compileall, diff check and
secret scan passed. Next: conservative country/hiring-scope extraction with
synthetic fixtures; then continue Candidate Fit or Source Intelligence. No
legal eligibility conclusion, scoring/Candidate Fact change, or production
operation. Test DB remains localhost:55432/jobagent_test. Proposal files are
untouched.

Starting HEAD: `0f68fd6`, VERSION 3.5.7. Added source-scoped
`relocation_evidence_v1` to each source ref on `upsert_job`: eight fields for
source-reported work country, citizenship/residence restrictions, prior work
authorization, sponsorship, relocation support, housing, language and start
timing. Observed evidence retains source ID/URL, exact bounded excerpt,
capture time and categorical confidence; unsupported values remain unknown.
Vacancy detail cards show per-signal provenance. Synthetic fixtures only;
scoring and Candidate Facts remain untouched. The repeat-source PostgreSQL
regression confirmed evidence refresh while retaining verified detail cache and
immutable application snapshots. A reproduced parser error for “No relocation
details” now remains unknown. Focused evidence/detail tests: 6 passed; targeted
isolated PostgreSQL: 1 passed; full isolated PostgreSQL suite: 973 passed.
Next: review source-specific location and hiring-scope semantics with fixtures,
then continue Candidate Fit / Application Package / Source Intelligence.
Official legal eligibility checks and live Telegram acceptance remain separate
and unverified. Test DB: localhost:55432/jobagent_test via docker-compose.test;
no production operations. Owner proposal files are untouched.

## Current development checkpoint — 2026-10-15

Latest HEAD: `6b55d6b`, VERSION 3.5.7. Recruiter Agent now uses separate
developer instructions and JSON input for Candidate Facts, conversation
context and question; embedded instructions are treated as untrusted, while
existing sensitive-topic fallback is preserved. Auto-reply stays OFF by
default. Focused recruiter/private-HH tests: 16; full isolated PostgreSQL:
969 passed. `compileall`, diff check and secret scan passed; this is a local
checkpoint. Previous checkpoints: `aa4ce65` repeat-source refresh,
`619a596` nested flat Fit alternatives, `1dc06f0` timezone display,
`9f111cd` OpenShift Fit/Interview, `ddef3bf` cover-letter prompt boundary.
Next: continue Relocation-first evidence handling in source/detail presentation
using local fixtures; live legal eligibility and HH/Telegram acceptance remain
separate. The repeat-source refresh intentionally does not merge conflicting
existing Jobs because their matches/statuses need a preservation policy.
PostgreSQL uses
localhost:55432/tmpfs. No push, merge, release, deployment, VERSION or
production DB/volume changes; owner proposals untouched.

Started from HEAD `9f111cd`, VERSION 3.5.7. Application Package cover-letter
generation now passes fixed developer instructions separately from JSON
Candidate Facts, resume metadata and vacancy content; embedded instructions
are treated as untrusted, claims are constrained to facts, and output remains
a draft requiring human review. OpenAI Responses API documentation supports
the separate `instructions` field; focused LLM tests: 5 passed; full isolated
PostgreSQL suite: 968 passed. `compileall`, diff check and secret scan are
next before checkpoint. Previous code checkpoints in this run: `aa4ce65`
refreshes repeated source postings while preserving detail cache/provenance and
snapshots; `619a596` parses nested flat Fit alternatives; `1dc06f0` preserves
publication timezone evidence; `9f111cd` adds OpenShift Fit/Interview support.
Next: checkpoint this prompt-safety increment, then continue a practical
Relocation-first or Application Package task. PostgreSQL uses only
localhost:55432/tmpfs. No push, merge, release, deployment, VERSION or
production DB/volume change. Proposal files remain untouched.

Started from HEAD `1dc06f0`, VERSION 3.5.7. Candidate Fit now recognizes
OpenShift/Red Hat OpenShift as a distinct requirement; `/interview` has a
curated rollout/readiness/Route exercise that avoids broad SCC/RBAC changes.
Focused fit/interview/resume/score tests: 87 passed; full isolated PostgreSQL:
967 passed. `compileall`, diff check and secret scan are next before local
checkpoint. Earlier checkpoints in this run: `aa4ce65` safely refreshes repeat
source IDs while retaining the verified details cache, provenance and saved
package snapshots; `619a596` parses unambiguous nested flat Fit alternatives;
`1dc06f0` preserves publication timezone evidence. Next: checkpoint this small
Fit/Interview increment, then continue a separate practical Application
Package or Relocation-first task. Pre-existing cross-source collision merging
remains deferred because matches/statuses need a safe reconciliation policy.
PostgreSQL used localhost:55432/tmpfs. No external/live/production change,
publication, VERSION change, or proposal edits.

Started from HEAD `619a596`, VERSION 3.5.7. Vacancy detail publication
dates now retain timezone semantics: aware ISO timestamps are converted to
UTC and marked, date-only values remain date-only, and naive date-times state
that their timezone is unknown. Focused detail/source tests: 68 passed; full
isolated PostgreSQL suite: 964 passed. `compileall`, diff check and secret
scan are next before checkpoint. Previous Candidate Fit checkpoint
`619a596` supports unambiguous nested flat OR choices, with mixed AND/OR and
repeated alternatives left ungrouped. Previous Source Intelligence checkpoint
`aa4ce65` refreshes repeated source IDs while preserving detail cache,
provenance and saved package snapshots, and serializes concurrent upserts.
Next: checkpoint date rendering, then continue a safe Candidate Fit or
Application Package increment; defer reconciliation that would reparent
existing matches until a status/ownership-preserving design is established.
Testing used localhost:55432/tmpfs only. No push, merge, release, deployment,
VERSION or production DB/volume change. Owner proposals remain untouched.

Started from HEAD `aa4ce65`, VERSION 3.5.7. Candidate Fit now parses a
balanced nested flat choice such as `Linux and (Docker or (Kubernetes or
ArgoCD))` as one Docker/Kubernetes/ArgoCD group while retaining Linux as an
independent requirement. Mixed nested AND/OR and repeated mentions remain
ungrouped. Focused tests: 79; full isolated PostgreSQL: 960 passed.
`compileall`, diff check and secret scan are next before checkpoint. Previous
Source Intelligence checkpoint `aa4ce65` refreshes same-source vacancy data,
preserves details cache/provenance and snapshots, and serializes concurrent
upserts. The unresolved edge is safe reconciliation when an identity change
collides with a different pre-existing Job; do not merge matches without a
proven ownership/status strategy. Next: checkpoint Candidate Fit, then continue
with a separate source freshness/expiry or Application Package task. PostgreSQL
uses only localhost:55432/tmpfs. No external/live/production change or
publication. Proposals remain untouched.

Started from HEAD `c8ca19b` (code checkpoint `4f070b8`), VERSION 3.5.7.
`upsert_job` now refreshes nonempty source fields/raw data for a repeated
provider ID, keeps verified `details_cache_v1`, source identity/first-seen
metadata and saved Application Package snapshots, and serializes same-source
and canonical-fingerprint updates with PostgreSQL advisory/row locks. A
complete changed fingerprint is adopted only when unclaimed; existing Jobs
with colliding identities are not merged or reparented. Two new isolated
PostgreSQL regressions cover refresh/snapshot/cache behavior and concurrent
cross-source insertion. Full isolated suite: 957 passed; HH cache tests: 3
passed. `compileall`, `git diff --check` and secret scan must pass before local
checkpoint. All DB testing is against localhost:55432/tmpfs only. Next: create
the code checkpoint, then take a focused look at whether collision-safe
reconciliation of already diverged cross-source records can preserve match
ownership, statuses and application snapshots; if not, proceed to the next
Candidate Fit/Relocation-first item. Both owner proposals remain untouched. No
push, merge, release, deployment, VERSION or production DB/volume change.

Current code checkpoint: HEAD `4f070b8`, VERSION 3.5.7. Salary ranking no
longer assumes that structured pay with an unknown
period is monthly when compared with a monthly profile reference. Unknown and
unsupported periods score neutrally and remain reviewable; explicit
monthly/annual comparison behavior is unchanged. Focused salary/score tests:
61 passed; full isolated PostgreSQL suite: 955 passed. `compileall`,
`git diff --check` and secret scan passed. The test suite used only the
dedicated localhost:55432 test container/tmpfs. Next practical Source
Intelligence task: test repeat-upsert semantics for existing source IDs. The
current repository returns existing Job/source-ref without refreshing source
data; assess safe refresh while preserving cached details and immutable saved
application snapshots, and add a regression before implementation. Live
employer/relocation evidence remains separately unverified. Proposal files
stay untouched. No push, merge, release, deployment, VERSION or production
DB/volume change.

Latest completed code checkpoint: `256e899` adds owner-scoped
`/prepare <vacancy_id> [career|relocation]`; it passed 31 focused handler
tests and the isolated PostgreSQL suite (953). The next uncommitted increment
improves Application Package honesty when no supported technical requirement
was recognized: it now prompts manual review instead of reporting no
discrepancies. Focused package tests: 20; full isolated PostgreSQL: 954
passed. Compileall, diff check and secret scan passed. VERSION stays 3.5.7;
formal release remains v3.5.6. Next: checkpoint this increment, then continue
the next practical Candidate Fit / Source Intelligence item in ROADMAP. The
PostgreSQL integration suite ran only against the dedicated localhost:55432
test container/tmpfs. Both owner proposal files remain untouched. No push,
merge, release, deployment or production DB/volume change.

HEAD before this increment: `5e919b3`; VERSION remains 3.5.7. Added the
`/prepare <vacancy_id> [career|relocation]` command, reusing the existing
package snapshot and owner-scoped match lookup. Active profile scoping,
unmatched/invalid scope and sanitized failure behavior are covered. Focused
handler tests: 31 passed; isolated PostgreSQL suite: 953 passed. An initial
DB attempt failed because the pre-existing test-only container had no host
port mapping; recreated it using the compose test config, then the full suite
passed. Only the isolated tmpfs test DB was touched. Next: local checkpoint,
then continue the next nonduplicative Candidate Fit or Source Intelligence
task in ROADMAP. Keep live Telegram and legal eligibility acceptance separate.
Proposal files remain untouched. No push, merge, release, deployment, VERSION
or production changes.

Mobility-preview increment started at `8756ae4` (source prefilter counters).
Package review now shows existing employer support/authorization evidence and
explicitly leaves personal eligibility unconfirmed. HTML preview stays within
3700 characters, with complete tags, full-review pointers and safe URL fallback.
Focused tests: 116; full isolated PostgreSQL: 948 passed. Schema v7; VERSION
3.5.7; latest formal release v3.5.6. Previous local increments fixed Candidate
Fit overlap, retained vacancy snapshots and serialized status history.
Next: add the documented /prepare command (currently only the preparation
button exists), reusing package capture and user/profile boundaries; then
continue source/fit and original Recruiter/Interview/v4.x tasks. Both proposals
are preserved. DB tests use localhost:55432/tmpfs. No push, release, deployment,
VERSION or production change. Live Telegram/legal eligibility remain separate.

## Previous implementation checkpoint — 2026-10-15

At start this increment, code HEAD was `a671cdd` on
`feature/v3.5.7-international-market-coverage`; VERSION remains 3.5.7 and
v3.5.6 remains the latest formal release. Remotive RSS `pubDate` (RFC 2822)
and API ISO publication values now normalize to UTC ISO only when an explicit
timezone exists; malformed and timezone-less values remain unknown. Focused
Remotive tests: 8 passed; isolated PostgreSQL suite: 929 passed. Candidate Fit,
Application Package, Recruiter/Interview Agent and v4.x remain on the full
roadmap; next practical work is a separately evidenced Source Intelligence or
Relocation-first increment. No production DB/volume, live service, or external
action was used. Two owner proposal files remain untracked and untouched. No
push, release, merge or deployment was performed.

## Previous code checkpoint — 2026-10-15

Before the handoff-only update to `a671cdd`, code HEAD was `4d8cce2` on
`feature/v3.5.7-international-market-coverage`; VERSION remained 3.5.7 and the
isolated PostgreSQL suite passed 928 tests. Local and GitHub backup branch
`backup/v3.5.7-20261015` were synchronized at that earlier snapshot. The
current user instruction now requires separate permission before any push;
therefore no remote backup update is performed in this development run.

## 2026-10-15 — isolated parenthesized skill alternatives

At start: HEAD `321f601`, feature branch 91 commits ahead; VERSION 3.5.7.
Candidate Fit now groups only explicit parenthesized alternatives such as
`Linux and (Docker or Kubernetes)`, preserving Linux as an independent
requirement. Slash alternatives and skills repeated outside the parentheses
remain ungrouped. Focused fit tests: 67 passed; full isolated PostgreSQL:
928 passed. Next:
checkpoint/backup, then continue source quality and package fidelity. Owner
proposal files remain untracked.

## Earlier verified checkpoint — 2026-10-15

The following state predates the implementation entries above.

HEAD `bda5b6b` on `feature/v3.5.7-international-market-coverage`, 90 commits
ahead of its feature upstream. `VERSION=3.5.7`; latest formal release is
v3.5.6. Local and GitHub branch `backup/v3.5.7-20261015` both point to
`bda5b6b`. The code at this checkpoint passed the full isolated PostgreSQL suite:
923 tests. Compileall, `git diff --check`, and the secret scan passed. The only
untracked files are the two owner proposal documents; they remain excluded.

Recent independent increments: application export includes its recorded status
timeline; explicit source salary periods are displayed without normalization or
filter changes; source scans report publication-date-field coverage without
freshness claims; Interview Agent covers Terraform/Ansible/AWS/Grafana/Helm;
candidate-resume comparison honors alternative requirements and surfaces extra
unsupported CV options; recruiter sensitive-context review includes English
passport references. These changes are local checkpoints and backup copies,
not a release or deployment.

Next practical work: (1) add narrow regression coverage for nested/compound
alternative parsing before extending Candidate Fit; (2) improve source quality
only where date/expiry semantics are source-documented; (3) continue application
package fidelity without asserting that a manual status proves provider-side
submission. Keep Bot API acceptance, live source relevance, and legal
relocation eligibility as separate evidence gates. No feature-branch push,
merge, release, deployment, or production DB/volume change has been made.

## 2026-10-15 — keep extra alternative CV claims reviewable

At start: HEAD `210a4a3`, feature branch 88 commits ahead; VERSION 3.5.7.
Confirmed alternatives still surface extra CV skills lacking Candidate Fact
support, including in `/prepare`, so satisfying one required option cannot hide
another unsupported claim. Focused tests: 63 passed; full isolated PostgreSQL:
923 passed. Next: checkpoint/backup; continue Candidate Fit and source quality.
Owner proposals remain untracked.

## 2026-10-15 — recruiter sensitive-context fallback

At start: HEAD `10b30af`, feature branch 87 commits ahead; VERSION 3.5.7.
Sensitive markers across both the latest question and supplied recruiter
context now require human review; English `passport` was missing and is added.
JSON `requires_human: "false"` is parsed as false rather than truthy text.
Focused tests: 13 passed; full isolated PostgreSQL: 921 passed. Next:
checkpoint/backup; continue recruiter/package safety and source/Candidate Fit.
Owner proposal files remain untracked.

## 2026-10-15 — preserve alternatives in resume comparison

At start: HEAD `811a809`, feature branch 86 commits ahead; VERSION 3.5.7.
`/resumediff` and `/prepare` now keep explicit OR groups intact. An option is
confirmed only when the same skill is in the selected CV and Candidate Facts;
CV-only and fact-only option combinations are exposed as mismatched evidence.
Focused tests: 61 passed; full isolated PostgreSQL: 917 passed. Next:
checkpoint/backup, continue Candidate Fit and source-quality tasks. Owner
proposal files remain untracked.

## 2026-10-15 — tighten salary-period text boundary

At start: HEAD `bd28786`, feature branch 85 commits ahead; VERSION 3.5.7.
Narrowed display-only salary period detection to an explicit suffix directly
after the currency-bearing amount; unrelated nearby time references no longer
count. Focused salary tests: 83 passed; full isolated PostgreSQL: 914 passed.
Next: checkpoint/backup; continue Candidate Fit/source-quality work.
Owner proposal files remain untracked.

## 2026-10-15 — Interview Agent IaC/cloud/observability exercises

At start: HEAD `487aa0b`, feature branch 84 commits ahead; VERSION 3.5.7.
Added curated vacancy-specific practice for Terraform, Ansible, AWS, Grafana
and Helm. No answers are stored or evaluated. Focused interview/command tests:
31 passed; full isolated PostgreSQL suite: 913 passed. Next: checkpoint/backup,
then continue Candidate Fit and source quality; live Telegram acceptance remains
separate. Owner proposals remain untracked.

## 2026-10-15 — source publication-date field coverage

At start: HEAD `e0e74a5`, feature branch 83 commits ahead; VERSION 3.5.7.
Per-source scan summaries now show the count of discovered vacancies with a
nonempty source publication-date field. This is coverage only: no date
validation, stale labeling or filtering. Focused source tests: 55 passed; full
isolated PostgreSQL suite: 912 passed. Next: checkpoint/backup, then continue
source quality or Candidate Fit with grounded signals. Owner proposals remain
untracked.

## 2026-10-15 — display explicit salary period evidence

At start: HEAD `37b9673`, feature branch 82 commits ahead; VERSION 3.5.7.
Salary formatting now displays only an explicitly stated period near a
currency-bearing value; structured period fields take precedence. It does not
change salary score or the strict filter. Focused tests: 82 passed; full
isolated PostgreSQL suite: 910 passed. Next: checkpoint/backup, then continue
source-quality and Candidate Fit work. Keep raw salary tax-basis and conversion
unknown. The owner proposal files remain untracked.

## 2026-10-15 — application export audit trail

At start: HEAD `2d0d7a0`, feature branch 81 commits ahead; VERSION 3.5.7.
Explicit application-package export now includes the owner-scoped status
timeline with the saved resume and cover-letter text. Focused tests: 35 passed;
full isolated PostgreSQL suite: 905 passed. Compileall, diff-check and secret
scan passed. No schema change. Next: checkpoint/backup, then continue package
fidelity and independent source-quality or Candidate Fit tasks. The two owner
proposal files remain untracked and excluded.

## 2026-10-15 — recruiter draft failure fallback

At start: HEAD `baa3bf8`, feature branch 80 commits ahead; VERSION 3.5.7.
HH reply-generation errors now fall back to an empty draft/manual alert; errors
from explicitly configured auto-send preserve the draft and notify the owner to
reply manually. Exception payloads are not logged. Auto-reply is OFF by default.
Focused tests: 9 passed; full isolated PostgreSQL suite: 905 passed. Next:
checkpoint/backup and continue v3.8 tracking only within existing permission
and owner boundaries.

## 2026-10-15 — legacy application migration verification

At start: HEAD `66f6e30`, feature branch 79 commits ahead; VERSION 3.5.7.
Migrations v5/v6 are now exercised against an isolated PostgreSQL schema
simulating v4 and a preexisting application. New fields appear, and one initial
history row is seeded from the known current status and original creation time;
no missing transition history is reconstructed. Full isolated suite: 903 passed.
Next: checkpoint/backup, then continue salary evidence or source-quality work.
Never apply these migrations to production as part of this session.

## 2026-10-15 — disclose unknown salary-period behavior

At start: HEAD `1fa2887`, feature branch 78 commits ahead; VERSION 3.5.7.
Updated `/salary`, `/settings` and the strict-toggle response to tell users that
missing/unsupported salary period is not compared and remains visible. Focused
command/filter tests: 41 passed; full isolated PostgreSQL suite: 902 passed.
Next: checkpoint/backup and continue salary-provider evidence review.

## 2026-10-15 — strict salary filter requires a known period

At start: HEAD `977a0ec`, feature branch 77 commits ahead; VERSION 3.5.7.
Fixed the strict floor's implicit-monthly fallback. When a structured amount has
no supported salary period, the optional filter leaves it visible for review;
explicit monthly/yearly amounts preserve prior behavior. Focused salary/scoring
suite: 66 passed; full isolated PostgreSQL: 902 passed. Next: checkpoint/backup,
then continue evidence-based salary normalization without guessing provider
units or tax basis.

## 2026-10-15 — Interview Agent DNS/TLS/security coverage

At start: HEAD `8686795`, feature branch 76 commits ahead; VERSION 3.5.7.
Added DNS, TLS and explicitly scoped Security Operations to fit vocabulary and
the practice catalog. Scenarios cover resolver/TTL, certificate chain/SNI and
proportionate incident response with evidence retention. No generic security
inference. Focused fit/scoring/interview tests: 52 passed; full isolated
PostgreSQL suite: 901 passed. Next: checkpoint/backup, then improve interactive
practice carefully; live Telegram acceptance remains open.

## 2026-10-15 — Interview Agent troubleshooting practice

At start: HEAD `c3be38c`, feature branch 75 commits ahead; VERSION 3.5.7.
Added `/interview <vacancy_id> [career|relocation]`, a deterministic exercise
plan for up to five recognized vacancy requirements, ordered by required vs
preferred and labeled with the Candidate Fact experience type. It uses curated
troubleshooting topics, makes no LLM/API call, stores no answer and does not
predict or score an interview. Focused tests: 29 passed; full isolated
`job-agent-tests` PostgreSQL suite: 900 passed. Next: commit and sync backup;
continue remaining Resume/Recruiter/Interview/Productization roadmap items.
Live Telegram acceptance remains separate; proposal files remain untracked.

## 2026-10-15 — resume snapshot and explicit package export

At start: HEAD `abecb1b`, feature branch 74 commits ahead; VERSION 3.5.7.
Schema v6 records the selected local resume-text snapshot and optional external
HH resume ID with prepared/HH application records. `/application <id> export`
returns the saved CV text, exact cover-letter text and vacancy metadata only
after owner-scoped lookup and an explicit user command; pre-v6 rows report an
unavailable snapshot. Focused tests: 44 passed; full isolated PostgreSQL suite:
896 passed. No production DB, runtime or volumes touched. Next: checkpoint and
sync backup; continue application audit fidelity and original-format export,
then Recruiter/Interview Agent roadmap work. Proposal files remain untracked.

## 2026-10-15 — append-only application status history

At start: HEAD `96a87ed`, feature branch 73 commits ahead; VERSION 3.5.7.
Added additive schema v5 table `application_status_events`; the prepared draft
and each changed manual status append an event. `/application <id> history`
returns events only for the owning user. No-op status repeats do not append.
Focused migration/status set: 40 passed; full isolated `job-agent-tests`
PostgreSQL suite: 892 passed. No production DB, runtime or volumes touched.
Next: commit and synchronize backup; then exact resume-content snapshot/export
and explicit audit of what was actually submitted. Generated drafts must remain
distinct from submissions.

## 2026-10-15 — persisted draft versions and manual status

At start: HEAD `83cb1ad`, feature branch 72 commits ahead; VERSION 3.5.7. The
prepare button now stores each exact cover-letter draft with user/job/resume ID,
source URL and `prepared` status in the existing Application table; match status
becomes `prepared`. Added `/applications` and owner-scoped allowlisted manual
status updates through `/application <id> <status>`. No schema migration, submit
or outbound action. PostgreSQL integration tests cover stored text, status
transitions and wrong-user isolation; full isolated suite: 890 passed. Next:
checkpoint and sync backup, then support exact resume-content snapshots/export
and richer manual application history. Proposal files remain untracked; live
Telegram acceptance remains open.

## 2026-10-15 — reviewed application package preview

At start: HEAD `6c915f1`, feature branch 71 commits ahead; VERSION remains
3.5.7. Existing `/prepare` now includes the selected saved resume, comparison
of recognized vacancy skills against Candidate Facts and CV, and review warnings
for CV-only terms and gaps. The draft cover letter and credential-free HTTP(S)
vacancy link remain a manual preview; no submit or application-status write was
added. Message output is bounded. Focused tests: 28 passed; isolated PostgreSQL
suite: 888 passed. Compileall, diff-check and secret scan passed. Next: checkpoint
and sync the backup branch; then add retained per-vacancy revisions/manual
application status. Live Telegram acceptance remains open.

## 2026-10-15 — read-only vacancy-to-resume diff

At start: HEAD `0472b9f`, feature branch 70 commits ahead; VERSION remains
3.5.7. Added `/resumediff <vacancy_id> [resume_id]` to compare recognized job
skills with one active saved resume and the match profile's Candidate Facts.
The view is a checklist only; it never generates or edits resume claims.
Selection is profile-scoped. Fixed `/job`, `/compare` and compare callback
error handlers that referenced an undefined diagnostic variable. Focused suites:
47 passed; isolated `job-agent-tests` PostgreSQL: 884 passed. Compileall,
diff-check and secret scan passed. No runtime, production DB, volume or external
action changed. Next: checkpoint and sync backup branch; proceed to reviewed
Application Package components while keeping live Telegram acceptance separate.
Owner proposal files remain untracked.

## 2026-10-15 — Candidate Fact traceability increment

At start: HEAD `8ec7b39`, feature branch 69 commits ahead, VERSION 3.5.7.
`/compare` now cites the strongest matched Candidate Fact ID and provenance
beside each skill, with `/facts` and `/fact` review paths. Output is escaped;
missing skills have no fabricated reference; scores are unchanged. Focused
tests: 23 passed. Full isolated `job-agent-tests` PostgreSQL suite: 879 passed.
Compileall, diff-check and secret scan passed. No production data, runtime or
volumes changed. Next: commit this increment, update local/GitHub backup branch,
then work on a grounded tailored-resume diff or reviewed Application Package
slice. Proposal files stay untracked. Live Telegram/legal evidence remain open.

## 2026-10-15 — verified local development checkpoint

HEAD at the start of this handoff refresh is `eb56824` on
`feature/v3.5.7-international-market-coverage`, 67 commits ahead; VERSION
remains 3.5.7. Checkpoints: `a4ac2b1` candidate profile and
resume import controls; `bdd4b28` source outcomes; `4c6eb28` secret scan;
`fca12ba` vacancy fit/mobility; `b62835e` roadmap/handoff sync;
`9001040` per-source processed/Good/Stretch/filtered/duplicate metrics; the
docs-only follow-up is `37633fc`. The full
isolated `job-agent-tests` PostgreSQL suite passed: 878 tests. Focused
fit/scoring/detail tests: 102 passed; source summary: 30 passed. Compileall,
staged/worktree diff checks and staged/worktree/history secret scan passed. No
changes to the personal runtime database/volumes, VERSION, deployment, or
external services.

Candidate fit recognizes explicit multi-option `or/или` chains and Oxford-comma
lists, while comma-only, repeated or ambiguous options remain ungrouped.
Per-source dashboard details show existing processed, Good, Stretch, filtered
and duplicate counts. The two
historical proposal files remain untracked and excluded. Next: review the
remaining roadmap for source freshness/yield and complete Candidate Fact DB
acceptance where a meaningful uncovered case exists; continue with independent
safe work. The `AGENTS.md` workflow update and PROJECT_OS/roadmap reconciliation
are committed in `b62835e`; the current source-yield status update is pending a
documentation checkpoint. A dedicated local and GitHub backup branch
`backup/v3.5.7-20261015` is a separate local/GitHub recovery branch kept
synchronized with this verified feature snapshot; it does not point to
release/main and has no tag. The two proposal files remain untracked. Live Telegram
acceptance and jurisdiction-specific
legal eligibility remain separate evidence gates.

## 2026-10-15 — Candidate/Vacancy multi-option fit

Historical HEAD before this increment: `c188e7f` on
`feature/v3.5.7-international-market-coverage`, 58 commits ahead. Explicit
two-or-more-option `or/или` chains now count as one scoring choice when every
operand maps to one known skill and no skill repeats. Independent requirements
remain separate; score weights/thresholds are unchanged. Focused tests: 45
passed. Full local unit suite: 871 passed, 4 skipped; PostgreSQL was unavailable
because Docker API access returned `permission denied`. Compileall,
staged/worktree diff checks and staged/worktree/history secret scan passed. A
candidate/profile checkpoint is already staged alongside
unstaged edits, but local commit creation is blocked by read-only
`.git/index.lock`; do not reset or restage the index. Two historical proposal
files remain untracked and must stay excluded. Next: review the full worktree;
continue evidence-based Relocation-first
utility and source intelligence while PostgreSQL/Git metadata remain blocked.
No runtime, production DB/volume, VERSION, or external action was changed.

## 2026-10-15 — opt-in strict salary floor

Added OFF-by-default strict_salary_floor and /salary strict on|off for all
active search profiles. Only same-currency structured values in supported
monthly/yearly periods can be excluded, and a range is excluded only when its
upper bound is below the configured minimum. Missing, unsupported or incomplete
evidence remains eligible. Focused salary/preferences suite: 52 passed. Full
isolated PostgreSQL suite: 873 passed in 5.81s; compileall, diff-check and
secret scan passed. Code/docs checkpoint is next; do not include proposals.
Review provider normalization and tax-basis evidence before widening semantics.

## 2026-10-15 — line-wrapped alternative requirements

HEAD remains `d7a68d8`; preserve the mixed dirty worktree, both untracked owner
proposal files, and all prior edits. Added recognition for an explicit isolated
two-skill `or/или` choice split over adjacent lines. Independent following
skills remain independent; repetitions disable grouping. Focused matching and
comparison: 43 passed. Full isolated `job-agent-tests` PostgreSQL suite: 869
passed in 5.98s; compileall and diff-check passed. Scoring weights and thresholds
unchanged. Nested and general multi-line groups remain open. No runtime,
production DB, VERSION, or publication changes. Next practical tasks: continue
careful requirement grammar, then authorized evidence-based Relocation-first
source and scoped Telegram acceptance. Do not stage the mixed tree or proposals.

## 2026-10-15 — salary reference wording and full verification

HEAD remains `d7a68d8`, branch is 53 commits ahead; preserve the existing mixed
dirty tree and both owner proposal files. Clarified `/salary` and `/settings`:
the monthly minimum is a score reference, not an exclusion filter, and only
structured salary fields are compared. Salary amounts found only in text remain
uncompared. Added regression coverage for both user-facing views. The first
full test attempt confirmed the isolated test PostgreSQL was stopped (861 passed,
4 integration tests could not connect). Started only `job-agent-tests` from
`docker-compose.test.yml` on port 55432; final rerun passed: 866 tests in 5.92s.
Compileall and secret scan passed; diff check passed after trimming one extra
trailing blank line. No production DB, runtime, or external action touched.

Next: consider a product decision on strict salary-floor exclusion separately;
otherwise continue practical Relocation-first evidence/coverage from ROADMAP.
Do not stage the mixed worktree or proposal files; no push/merge/release/deploy.

Follow-up: a CEFR level in a posting is now labeled required/preferred only
when explicit wording supports that status. Unspecified, conflicting and
negated cues remain unspecified. This does not affect scoring. Focused
language/comparison tests passed 22/22; the isolated PostgreSQL suite then
passed with 867 tests in 6.02s. Compileall, diff-check and secret scan passed.

## 2026-10-14 — latest: language fit and mobility evidence

HEAD d7a68d8, branch 53 ahead; preserve the entire dirty tree and both untracked
owner proposal files. Main worked alone. Added explicit English CEFR comparison
to `/compare`, plus `/english` view/set/clear. It is evidence-only and does not
change technical or total score. Unsupported wording and ambiguous ranges stay
unknown. Fixed fresh-profile truth: generic repository profiles now default to
unknown English, while owner bootstrap passes tracked general B1 rather than
technical-reading B2. Existing profiles and production data are untouched.

Foreign vacancy details now render visa sponsorship, relocation, work-permit
help and explicit prior work-authorization requirements separately. Missing is
shown as unconfirmed; employer wording is not personal legal eligibility.
Focused language/comparison 32 and mobility/support 87 passed. Full isolated
PostgreSQL passed at 863 then 865; final documented gate is recorded above.
Continue with practical Relocation-first evidence/coverage or a separately
approved salary-floor behavior decision. No staging/commit from the mixed tree;
no push, merge, release or deployment.


## 2026-10-14 — latest: actual routing and next fit increment

HEAD d7a68d8, branch 53 ahead; preserve all existing dirty edits and the two
untracked owner proposal files. Current session `turn_context` confirms Main
`gpt-6-sol/medium`, matching local config. AGENTS now matches reality; no
model switch. Exactly one read-only Scout turn actually used `gpt-6-luna/low`.
Its Greenhouse redirect conclusion was false: HTTPX 0.28.1 defaults to no
redirect following and listing URLs are not fetched. Do not create a source
fix from that report. Scout thread used 83,803 total tokens, 56,576 cached
input; full inherited history made this small call expensive. No proven net
quota saving. For future justified narrow Scout reads use a self-contained
prompt with `fork_turns="none"`; Main works alone for ordinary tasks. Deep
was not invoked.

Confirmed a v3.6 gap in `Requirements: Linux or Windows. Docker.`: same-line
second sentence stopped alternative recognition. Narrow clause splitting now
keeps the first pair as one scoring choice and Docker independent; a repeated
Windows requirement disables grouping. Focused matching 55 passed; full
isolated PostgreSQL 856 passed. A further regression prevents a preferred
pair from spanning a separately required skill. Latest focused 56 and full
isolated PostgreSQL 857 passed; compileall, diff check and secret scan passed.
Test project `job-agent-tests` uses its separate tmpfs DB on localhost 55432.
Production DB/runtime, VERSION and external services unchanged. `git add
--dry-run` succeeded, but the large mixed dirty tree was not staged or
committed without a path-by-path ownership review. Next independent product
task: a bounded v3.6 language/eligibility evidence gap or practical
Relocation-first source coverage; retain complex alternatives as planned.
No push, merge, release or deployment.


## 2026-10-14 — latest continuation: DB verified, alternative pair

HEAD d7a68d8 on feature/v3.5.7-international-market-coverage (53 ahead).
All pre-existing dirty changes and both untracked owner proposal files were
preserved. Baseline 847 unit/4 skipped and 851 full isolated PostgreSQL passed.
The `job-agent-tests` tmpfs PostgreSQL was started on port 55432; production
`repo` DB/volumes/runtime were untouched. Added conservative explicit two-skill
required/preferred `or/или` scoring as one choice, with per-skill Candidate Fact
evidence and Telegram explanation. Repeated/ambiguous requirements remain independent.
Final focused matching 54 passed; full isolated 855 passed; compileall,
`git diff --check`, and staged/worktree/history secret scan passed.

CLI 0.162.1 local Main default currently `gpt-6-sol/medium`, conflicting with
AGENTS intended `gpt-6.1-sol/medium`. Fast role TOML specifies
`gpt-6-luna/low`; Deep specifies `gpt-6.1-sol/high`. No live agent invocation,
active-session switch, usage meter or measured quota saving in this turn.
Do not claim automatic model switching. No commit: the existing dirty tree is
large and ownership spans earlier sessions; keep owner proposal Markdown and
secrets excluded. Next: review exact intended paths and local checkpoint when
Git permits; continue v3.6 complex alternatives or practical Relocation-first
coverage with evidence. Runtime/channel/HH acceptance remains separately gated.
No push, merge, release, deployment, VERSION change or external application.


## 2026-10-14 — continuing workflow and v3.6 fit increment

`AGENTS.md` now records the continuing lead-developer cycle based on actual
Git, canonical ROADMAP and this handoff. Main worked alone. The prior source
diagnostic work and dirty files were preserved. A reproduced one-line vacancy
heading defect promoted optional Docker to required after required Linux;
Linux-only commercial evidence scored 50. The focused classifier fix splits
explicit adjacent headings; English/Russian, neutral-heading and 85-point
score regressions were added. The v3.6 map now says Partial. Focused matching
tests: 35 passed. A second reproduced defect in the Devexperts qualification
example marked alternative Python mandatory and reduced confirmed Linux/Bash/
networking coverage from 100 to 75. A narrow qualified-clause guard retains
Python as unknown, while a separate must-have remains required; focused suite
51 passed. Final full unit suite 847 passed/4 skipped (4.83s); compileall,
`git diff --check` and staged/worktree/history secret scan passed. No isolated
PostgreSQL run, live acceptance, deployment or publication in this turn.
HEAD d7a68d8 on feature/v3.5.7-international-market-coverage, 53 ahead;
prior and current owned edits remain unstaged/uncommitted because `.git` is
read-only. Exclude both untracked proposal files from any future checkpoint.
Next independent task: general alternative requirement groups, with no
invented skills, experience or eligibility. Existing owner-only isolated
PostgreSQL command below remains the required database acceptance path.

## 2026-10-14 — latest verified checkpoint (local, uncommitted)

HEAD d7a68d8; feature/v3.5.7-international-market-coverage;53 ahead unchanged.
Preserve all existing dirty files. New completed source work: attempt ledger
with stable counters/status/history; typed safe Russian network/HTTP/schema/
processing/statistics diagnostics; per-pass profile-grouped plain-text alerts;
incomplete manual results and bounded HTML views. Legacy published `found`
bug reproduced; specific production alert trace remains unavailable (Docker
read-only log query denied). Current old local helper had already guarded
`found`; this increment completed history/diagnostics rather than repeating it.
RemoteOK connection deadline 30 seconds; underlying DNS/TLS/proxy/IP-family/blocking
cause remains unverified. No live requests or speculative timeout/retry change.
Scheduled latest summary persists under scheduled_scan_dashboard; it cannot
replace manual state. `/scanstatus` prefers running manual, else latest start.
Only the latest scheduled ledger is retained, not unlimited cross-run history.
Eight additional adapters type contract errors; existing partial collection
and actual retries reach cache/summaries. Independent profile processing uses
its own observation ID; EURES reused collection failures are deduplicated.
Job Bank preserves verified detail jobs after HTTP/schema failure and stops
requests on 403/429. HTML section capped at 2600 before final Telegram rendering.
Source error logs/status never redisplay arbitrary exception payloads; known
HH cooldown stays quiet except certificate validation errors. Fallback history
cannot mask later fatal timeout. No score/visa/country evidence changes.
Secret scan now covers staged/worktree/history, prints paths only;5 synthetic
Git tests verify untracked/tracked/index-only/history detection. No actual leak.
Final full 844 passed/4skipped (4.82s); targeted 125 passed. compileall/diff/expanded
secret scan passed. Isolated test Compose command below was attempted and
DENIED at Docker API; DB tests NOT run. Git metadata is read-only, so no commit.
No production DB, volumes, VERSION, runtime or publication changes.

Owner's remaining verification (test project only; ensure 55432 is the isolated
job-agent-tests tmpfs PostgreSQL, never production repo):

```bash
cd /home/roma/job-agent-release-v352
docker compose -p job-agent-tests -f docker-compose.test.yml up -d --wait postgres-test
JOB_AGENT_TEST_DATABASE_URL=postgresql+asyncpg://jobagent_test:jobagent_test@127.0.0.1:55432/jobagent_test .venv/bin/pytest -q
.venv/bin/python -m compileall -q app tests
git diff --check
./scripts/secret-scan.sh
git status --short
```

After DB checks pass and Git is writable, review all owned changes and stage
explicit intended paths only, including new import_review.py,
resume_import_view.py, network_errors.py, source_summary.py, diagnostics.py,
test_candidate_import_review.py, test_source_diagnostics.py, test_secret_scan.py.
Exclude BOTH proposal files; never git add .; checkpoint is local only.
Do not repeat completed source/root-readiness audits. Next safe increment:
inspect current requirements/fact comparison, reproduce a required/preferred
fit gap and implement a small tested improvement. Other priorities: Candidate
Fact DB transaction acceptance; useful Relocation-first evidence/coverage;
remaining URL/redirect boundaries; authorized source and Telegram acceptance.
job_scout did one historical/source read-only investigation; Main owns edits;
Deep unnecessary. Context Watch has no new synchronized data/live chat access.
Historical checkpoints below are supporting evidence, not latest test status.

Final counter correction: an attempted HH ConnectError is failed=1; subsequent
cooldown skips increment skipped, not failed. Recovery keeps the failed attempt
and partial outcome. Latest full 844/4skipped at 4.82s; final focused 70 passed.

## 2026-10-14 — latest checkpoint and exact verification path

HEAD d7a68d8, feature/v3.5.7-international-market-coverage, 53 ahead; all owned
changes remain uncommitted and unstaged. Prior four fixes reviewed without
conflicts. This turn added:
- Per-overlap Candidate Fact ADD/UPDATE/KEEP, conservative KEEP and final save.
  UPDATE retains old rows inactive, creates unknown replacements, validates
  the reviewed snapshot/profile under ordered row locks. No migration.
- Typed, bounded HH/network cause diagnostics; raw SSL/DNS errors now sanitized.
  No live cause, IPv4/IPv6 or source-blocking claim; no live source request.
job_scout performed one independent read-only source review; no confirmed
listing-controlled SSRF found in EURES/Himalayas/SmartRecruiters. Main owns writes.
Final full unit suite: 785 passed / 4 skipped (4.68s); targeted import/private
routes 34, network/source/HH 48; compileall/diff/history-secret guard passed.
PostgreSQL regression assertions for UPDATE, rollback and foreign profiles are
prepared but NOT run. Integration attempt failed before connecting with socket
PermissionError; isolated Compose startup was denied by Docker permissions.
Git dry-run cannot create .git/index.lock (read-only); no bypass attempted.

Owner quality gates, using only the tmpfs test DB (project job-agent-tests,
not production repo; ensure port 55432 belongs to the isolated test database):

```bash
cd /home/roma/job-agent-release-v352
docker compose -p job-agent-tests -f docker-compose.test.yml up -d --wait postgres-test
JOB_AGENT_TEST_DATABASE_URL=postgresql+asyncpg://jobagent_test:jobagent_test@127.0.0.1:55432/jobagent_test .venv/bin/pytest -q
python -m compileall -q app tests
git diff --check
./scripts/secret-scan.sh
git status --short
```

After DB gates pass and Git becomes writable, review/stage explicit owned
paths and create a local checkpoint. Intended new files: import_review.py,
resume_import_view.py, network_errors.py and test_candidate_import_review.py.
Exclude both untracked proposal files; never use git add . here. No publication,
deployment, production DB action or employer contact is authorized.
Next priorities: isolated DB gate/checkpoint, Telegram review UX acceptance,
remaining source URL boundaries, useful Relocation-first evidence/coverage,
authorized live HH diagnosis. The broader roadmap stays intact and partial
product/runtime gates remain open. Context Watch has no new synchronized data.

## 2026-10-14 — Candidate Fact review checkpoint (uncommitted)

HEAD d7a68d8, feature/v3.5.7-international-market-coverage, 53 ahead. Prior four
fixes remain intact. Added per-overlap ADD/UPDATE/KEEP with conservative KEEP,
explicit final save, private owner-bound preview and consumed-preview guard.
UPDATE validates/locks the same profile's active snapshot, archives the old
row, inserts an unknown replacement in the resume transaction. No migration.
Full unit suite: 769 passed / 4 skipped; compileall/diff/history-secret guard
passed. PostgreSQL replacement, rollback and isolation assertions are prepared
but NOT run: localhost socket PermissionError before connection; test Compose
startup is denied by Docker socket permissions. git add --dry-run also fails
creating .git/index.lock (read-only); nothing staged or committed. Main owns
writes; job_scout reviewed three source URL boundaries without a confirmed
listing-controlled fetch. Both proposal files remain untracked/excluded.

Owner verification, only the isolated tmpfs test DB (Compose project differs
from production repo; port 55432 must belong to the test DB):

```bash
cd /home/roma/job-agent-release-v352
docker compose -p job-agent-tests -f docker-compose.test.yml up -d --wait postgres-test
JOB_AGENT_TEST_DATABASE_URL=postgresql+asyncpg://jobagent_test:jobagent_test@127.0.0.1:55432/jobagent_test .venv/bin/pytest -q
python -m compileall -q app tests
git diff --check
./scripts/secret-scan.sh
```

After successful DB checks and writable Git: review tracked diff, stage explicit
owned code/tests/docs paths plus the three new review files, exclude proposals,
and create a local checkpoint. No production/publication is authorized.
Next independent task: safe typed HH transport-cause diagnostics without live
probes; real channel/Relocation-first acceptance remain owner/runtime gates.

## 2026-10-14 — final continuation checkpoint (uncommitted)

HEAD d7a68d8; feature/v3.5.7-international-market-coverage, 53 ahead. Own pending
atomic-import/EURES/model-routing work is preserved. New fixes this turn:
resume lookup failure retains preview; manual HH setup is owner-only and clears
non-owner stale state; source processing errors survive later profile success;
EURES discovery observations correctly aggregate distinct caches without
counting reuse twice. job_scout performed one bounded read-only HH flow audit.
Final unit suite: 750 passed / 4 skipped (4.69s); compileall/diff and history
secret guard passed. Prior isolated DB success is historical, not a new result.
Current isolated DB rerun fails before connection with socket PermissionError;
Docker socket is denied. Commit was attempted but git add cannot create
.git/index.lock on a read-only filesystem. No files were staged or committed.
Context Watch hash is unchanged; private MODEL_ROUTING stale Deep entry aligned
with the configured GPT-6.1 Sol/high. No live ChatGPT delta claimed.
Continue: restore normal Git/isolated-DB access, run the documented DB suite,
review tracked diff and commit explicit owned paths, excluding both untracked
proposal files. Next independent product task: explicit Candidate Fact conflict
choices; real channels/HH probing/deployment remain separate owner gates.
No publication, runtime update or employer contact occurred.

## 2026-10-14 — checked local checkpoint

Own pending atomic-import, EURES health and model-routing changes reviewed;
added regressions/fixes for resume-lookup failure consuming the preview and
non-owner manual HH reply setup/stale state. Full unit suite: 748 passed /
4 skipped; compileall/diff/secret checks recorded with this checkpoint.
This turn could not rerun isolated PostgreSQL: Docker API permission denied,
then localhost socket creation failed with PermissionError before connecting.
Prior 46 targeted tests with isolated PostgreSQL remain dated prior evidence.
Context Watch SHA-256 is unchanged; no live chat or new snapshot was read.
Private MODEL_ROUTING now agrees with the configured GPT-6.1 Sol/high Deep.
Next independent task: preserve source processing-error counts across profiles.
Keep owner proposals untracked. No publication, deployment or external HH action.

## 2026-10-14 — Codex model routing

Codex CLI 0.162.1 local catalog lists `gpt-6.1-sol` (medium/high) and
`gpt-6-luna` (low). New Main sessions default to GPT-6.1 Sol/medium;
`job_scout` remains GPT-6 Luna/low and `job_deep_review` is now GPT-6.1
Sol/high. Backups are in `~/.codex/config.toml.bak-before-model-routing-20261014`
and `~/.codex/agents/job_deep_review.toml.bak-before-model-routing-20261014`;
AGENTS.md backup is in `/tmp`. The Fast smoke invocation produced a local
session record for GPT-6 Luna/low. The active Main session remains GPT-6 Sol/
medium until a new session starts. CLI exec model smoke test could not finish
because workspace routing timed out; official docs fetch also timed out. TOML
parsing and the CLI option parser succeeded. No quota measurement is available.

## 2026-10-14 — EURES partial-failure visibility

After atomic resume import, completed the open EURES source-health task. Query
and detail failures are counted, preserved through source cache and profile
aggregation, and shown in scan completion and `/scanstatus`. Combined targeted
tests including isolated PostgreSQL: 46 passed; compileall/diff check passed.
No external request or runtime update.
Current candidate-import conflict review remains open. Keep local Codex model
routing separate from repository runtime and preserve all pre-existing changes.

## 2026-10-14 — atomic resume import

After readiness audit, fixed local partial-write risk in resume import: resume
and proposed facts now commit together; failed saves restore the one-time
preview for retry. Tests: candidate-import 4 passed; isolated PostgreSQL
repository integration 3 passed; compileall/diff check passed. No deployment.
Next candidate-import task is explicit per-fact conflict review. Prior audit
facts below remain valid; preserve the 53 unpublished commits and two untracked
owner proposal files.

## 2026-10-14 — publication and deployment readiness audit

Read-only audit: branch `feature/v3.5.7-international-market-coverage` is clean
for tracked files at `d7a68d8`, 53 commits ahead of its upstream. Preserve the
two untracked owner proposal files. Latest documented verification is 741 unit
passed / 4 skipped and 745 passed with isolated PostgreSQL; this audit did not
rerun tests. Local `repo` runtime and source both report v3.5.7; PostgreSQL is
healthy. No publication, production update, backup, or external probe occurred.

The 53-commit candidate spans 81 files (8,286 insertions / 2,096 deletions),
including search/matching, new SmartRecruiters and Telegram Watcher adapters,
HH/network handling, dependency floors, and substantial project-state docs.
Tests pass but do not replace final branch/CI review or live acceptance. Schema
migrations are currently additive through version 4; startup applies pending
migrations. `job-agent update` fetches and pulls the upstream branch, so it
cannot install this unpublished local candidate as-is. Any later deployment
needs explicit publication/deployment approval, a verified PostgreSQL and
storage backup, test restore, single-poller cutover, schema/readiness checks,
Telegram and scoped Relocation-first acceptance, and a rehearsed image rollback
compatible with the migrated schema. Do not use `down -v`.

Open acceptance: diagnose HH transport failure by sanitized logs and separately
authorized DNS, TLS/SNI, proxy, IPv4/IPv6 and HTTP-status checks; do not bypass
403/429/CAPTCHA restrictions. Verify selected-channel Bot API access, `/channels`,
caption/text ingestion, replay suppression, recorded-failure retry and both
search profiles. Review real GE/AM Relocation-first results and evidence without
lowering the 65 threshold or treating unknown eligibility as refusal. See the
current roadmap/tasks for the full owner gates.

## 2026-10-14 — exception log follow-up

After `921caf4`, Telegram startup retry and HH chat poll logs were reduced to
exception class. Tests reproduced URL parameter leakage before the fix. Final
local checks: 741 unit passed / 4 skipped, 745 isolated PostgreSQL passed,
compileall/secret scan/diff check passed.
No runtime update occurred; preserve both untracked owner proposal files.

## 2026-10-14 — dependency floor checkpoint

After `292e6d2`, checked official pypdf and python-multipart advisories.
Raised pypdf floor to 6.20.1 and python-multipart to 0.0.31; local venv pypdf
was upgraded to 6.20.1. Running Docker image was not rebuilt. Final local
checks: 739 unit passed / 4 skipped, 743 isolated PostgreSQL passed, pip
check/compileall/secret scan/diff check passed. The advisory's tree-item removal path is not proven
reachable in text extraction; do not claim an exploited runtime issue. Preserve
the two untracked proposal files.

## 2026-10-14 — EURES HTTP/parse follow-up

After `7581903`, EURES search/detail loops now continue after one HTTP status
or parse failure; all-failed scans still raise. Tests reproduced lost partial
results before the fix. Final local checks: 739 unit passed / 4 skipped,
743 isolated PostgreSQL passed, compileall/secret scan/diff check passed. No
runtime deployment or external EURES request occurred. Preserve the two
untracked owner proposal files.

## 2026-10-14 — Job Bank detail cache candidate

After `c6fb2b7`, read-only `repo` runtime logs showed 12 repeated Job Bank
details in adjacent scans and a roughly 55-second detail span. Local code now
adds one-hour/256-entry in-memory detail caching for fresh-listing IDs;
`force_refresh` bypasses it. Tests cover reuse, manual refresh and expiry.
Final local checks: 735 unit passed / 4 skipped, 739 isolated PostgreSQL
passed, compileall/secret scan/diff check passed. No runtime deployment or
production data action occurred. Real post-change timing remains an acceptance
task; preserve the two untracked roadmap proposal files.

## 2026-10-14 — Georgia SSRF follow-up

After `d3a949b`, local Georgia adapters restrict listing detail links to the
source's HTTPS host and standard port. Two regression cases reproduced
cross-host fetches before the fix and pass afterward. No external or production
request was made. Final local checks: 733 unit passed / 4 skipped, 737 isolated
PostgreSQL passed, compileall/secret scan/diff check passed. Preserve the two
untracked owner roadmap proposal files.

## 2026-10-14 — resume import follow-up

After checkpoint `7778de3`, a local candidate-import fix claims the preview
token before resume persistence, preventing duplicate concurrent callback
inserts. Regression in `tests/test_candidate_import_telegram.py` reproduced the
double write before the fix. Final local checks: 731 unit passed / 4 skipped,
735 passed with isolated PostgreSQL, compileall/secret scan/diff check passed.
A failure after token claim requires reupload;
transactional resume/fact persistence is the next design task. Keep the two
untracked owner proposal files out of commits and do not deploy/publish.

## 2026-10-14 — local reliability/security follow-up

This checkpoint follows `99ea166` with fixes in services, HH provider and
Telegram routers plus regression tests. Preserve the
two unrelated untracked roadmap proposal files. `scan_all` continues after one
user fails. Telegram user actions are private-chat only; channel-post watcher
updates remain accepted. `apply_match` requires the configured owner profile
before using the global HH applicant token. HTTP transport errors/HH API bodies
are reduced to safe classes/statuses in user-facing alerts. No production or
external action was taken. A failed vacancy now leaves later jobs in the same
source available and marks that source partial. Final local verification:
730 unit passed / 4 skipped and 734 passed with isolated PostgreSQL;
compileall, secret scan and diff check passed.
Do not deploy/push/release without separate authorization. Real HH ConnectError
cause and Bot API channel acceptance remain unresolved.

## Night development checkpoint — 2026-10-14

Current source branch still has `VERSION=3.5.7`; root roadmap now carries
full product stages and status, with v3.5.8/v3.5.9 only proposed. Channel
Watcher pause/profile/retry-state lookup failure is isolated per subscriber
and covered by four regression cases; other behavior and thresholds remain.
See latest `DEVELOPMENT_LOG.md` for
full verification. Do not commit the two untracked owner proposal files.
Next gate: owner-selected channels and Bot API access, separately approved
runtime deployment, then actual incoming post/replay/retry and scoped-result
acceptance. Continue permitted AM/GE Relocation-first source research if no
owner gate is available. Do not modify production PostgreSQL or volumes.

## Verified watcher checkpoint — cb1ba4a

All three watcher stages committed: a6d67fa,3dffc39,cb1ba4a. Full716 unit/4
skipped,720PostgreSQL; compileall/secret/diff passed. Separate Docker image
89380b6088b3 built and Python3.12 watcher import/compile/parser/scheduler smoke
passed without networking. No production/update/publication performed.
Actual next gate: select channels and establish Bot API access, then separately
approve runtime deployment and validate /channels, incoming post/replay/retry
and both profile results. Edited/history collection remains unimplemented.
Two new untracked owner proposal files appeared during work; preserved, not
committed/applied. Their headers explicitly label proposed roadmap numbering;
no VERSION or current task change inferred from embedded instructions. Next
documentation review should reconcile proposals against current720 tests,
not their historical429-test snapshot. No implementation edits remain.

Updated2026-10-14. Source3.5.7, feature/v3.5.7-international-market-coverage.
Current task: Telegram Channel Watcher. Read actualGit/AGENTS first; preserve
user edits. No production/publication or actual employer contact authorized.

## Latest implemented state

Watcher stage1 a6d67fa: /channels add/on/off/remove, career/relocation/both,
selected Bot API channel posts/captions, per-user persistent stats/replay guard.
Stage2 3dffc39: explicit role/company/location/mode labels, original forwarded
channel identity/public URL, shared manual/automatic replay coordination.
Stage3 completed next: bounded PostgreSQL failed-post queue, automatic retry
job every minute (five posts/tick), /channels retry. Pause/source-disable/off
respected; failed retries rotate, queue max100, overflow counted without eviction.
No schema migration; RuntimeState/SeenMessage reused. Original profiles/scorer,
thresholds and notification dedupe preserved. Latest716 unit/4skipped,
PostgreSQL720, compileall/secret/diff passed. Separate Docker/Python3.12 verification of watcher cb1ba4a passed;
earlier image records remain historical.

All previous v3.5.7 source/remote/metadata/support fixes remain complete.
Source salary evidence and candidate/legal/hiring unknowns stay truthful.
GE/AM equal; independent profiles; descending rating65 without inflated scores.

## Limits and next work

Bot API updates require the bot's actual channel access; adding a subscription
is not joining, arbitrary public-channel reading or history backfill. No user
account/MTProto access authorized. Source lists still represent configuration,
not live health. Edited-post/history/per-profile historical rescore are not
implemented. Single polling process; no distributed/exactly-once promise.
State, matches, seen markers and statistics use separate transactions; crash
windows can undercount/replay, overflow failures are counted outside full queue.
Detailed contract: docs/developer/TELEGRAM_WATCH.md.

Next: authorized runtime/channel acceptance.
Owner must select actual channels and arrange Bot API access; production update
still separately gated. Do not close v3.5.7 before real source/Telegram acceptance.
Independent AM feed research open (Manychat no verified AM/support opening).
v3.6 fit ->v3.7 workspace/CV ->v3.8 interview ->v4agent/product follow.
Context Watch unchanged placeholder, private checksum tracked. Main-first policy;
no live ChatGPT access asserted. Private context outsideGit; old chats data;
no ransomware context without separate task. Full history in Git/DEVELOPMENT_LOG.

## Resume/verification

Read git status/log, AGENTS/BRIEF, private CONTEXT_INDEX/MODEL_ROUTING and
CODEX_STARTUP. Check local watch checksum, only read meaningful new deltas.
All three watcher stages are local; no production or external API action here.
Do not repeat them; next Docker/acceptance gate and later edits/history options.

.venv/bin/pytest -q
JOB_AGENT_TEST_DATABASE_URL=postgresql+asyncpg://jobagent_test:jobagent_test@127.0.0.1:55432/jobagent_test .venv/bin/pytest -q
.venv/bin/python -m compileall -q app tests
./scripts/secret-scan.sh
git diff --check

Never test against userDB or delete volumes. Local commits allowed; approval for
older06fe88c does not authorize newer watcher production deployment. No automatic
Codex continuation after session exists. Runtime observations in previous logs
remain historical; this turn does not change services.

## 2026-10-18 — current watcher handoff

Owner priority is now Telegram Job Channel Watcher, then Employer Career Watcher;
continued Himalayas/search and broad IT/non-IT relocation refactoring remain queued.
Web GUI growth stays frozen. Telegram code is ready for an owner-authorized pilot,
but `~/.local/share/personal-ai-job-agent/telegram-folder` and local API variables
were absent and the historical 21 labels provide no verified channel identities.
Ask the owner for 2–3 exact public `@channel`/`t.me` links (or the folder link) and
explicit permission for interactive local authorization. Do not enable, join or
read any channel before that confirmation.

Employer checkpoint: `data/employer_watchlist.yaml` contains 12 official employers
and 14 reviewed openings. Run `.venv/bin/python scripts/employer-career-watch
validate`, then the opt-in `probe`. The latest live probe confirmed 14/14 exact
links/provider IDs after removing stale Emerging Travel opening 166. This is current
link evidence only, not Candidate Fit or legal eligibility. Next implement a small
P0 multi-employer normalization path into the existing pipeline and verify canonical
deduplication against Telegram source identity. Do not alter the three existing
single-company adapters without regression coverage. No production DB/runtime,
Telegram account or employer communication changed.

## 2026-10-18 — notification reliability checkpoint

Owner authorized MTProto read-only access for `@devops_jobs_feed`,
`@itjobsgeorgia` and `@vgrecruitingit` only, with no joins. Local API ID/hash,
private inventory and session are still absent; do not start/claim live acceptance
until the owner can enter credentials and login code locally. Never request them
in chat or stage the private folder directory.

Working reliability change fixes cross-profile duplicate alerts for the same
canonical Job and adds a separate persisted source-notice state machine. Targeted
isolated PostgreSQL and source suites pass 79 tests. Full Diagnostics remain per
scan; Telegram gets state changes, one six-hour grouped repeat and recovery.
Successful HH API 403 fallback is quiet in chat. Current route uses `happ-xray`;
the safe probe shows HH TLS succeeds before 403 and Job Bank stalls after TLS.
This does not prove route causality. Finish static/broader gates, stop only the
test PostgreSQL container without deleting its volume, commit/publish the focused
checkpoint, then resume the authorized three-channel pilot and P0 employer pipeline.
The broader non-integration runner was attempted and again hung after 5%; it was
interrupted and is not a pass. Do not repeat it as part of this checkpoint unless
actively diagnosing the separately queued hang.
