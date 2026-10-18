## 2026-10-17 — Russian preferred Candidate Fit wording

- [x] Reproduce `Желательно знание Linux` being classified as required; add narrow skill-local preferred patterns before/after the skill name.
- [x] Candidate Fit/interview/resume suites 105 passed; full offline unit suite 1206 passed, 18 skipped; compileall, diff check, secret scan passed. No persistence changes, so no PostgreSQL run for this increment.
- [ ] Continue independent Source Intelligence or Candidate Fit work.

## 2026-10-17 — Remotive relocation evidence semantics

- [x] Reproduce candidate-required remote geography being exposed as physical work country; keep market identity and remote scope while leaving work country unknown.
- [x] Georgia and Armenia/Georgia fixture cases pass; targeted suites 160 passed; isolated PostgreSQL full suite 1205 passed; compileall, diff check and secret scan passed; test DB stopped.
- [x] PostgreSQL rediscovery regression: same canonical Remotive Job, new provider ID, preserved remote scope/evidence and latest provider identity; isolated full suite 1206 passed.
- [x] Reproduce and fix code-only Remotive location parsing (`GE`, `GE Only`, `Remote - GE`, `Georgia (GE)`); country-code parsing is uppercase/context-delimited to avoid lowercase `in`/`am` false matches. Expanded to AM fixtures and cross-market exclusion; focused suites 139 passed; isolated full suite 1218 passed.
- [x] Disambiguate `Georgia, GA` from country GE and ISO Gabon/GA; country-code helper resolves it to US. Focused suites 134 passed; isolated full suite 1213 passed. US is not an enabled Remotive target market.
- [ ] Continue review of exact provider attribution in JobMatch only after confirming a compatible non-schema approach; meanwhile choose another independent source-quality/candidate-fit issue.

## 2026-10-17 — Himalayas remote country restrictions

- [x] Reproduce `locationRestrictions=[Georgia]` being reported as physical work country; keep market filter and remote scope, leave work country unknown absent employer location.
- [x] Verify sponsorship, relocation assistance, and prior work authorization remain unknown; targeted relocation/source suites 169 passed; isolated PostgreSQL suite 1219 passed; compileall, diff check, secret scan passed.
- [ ] Continue an independent Source Intelligence or Candidate Fit fixture-backed issue.

## 2026-10-17 — ELK/non-IT Candidate Fit vocabulary

- [x] Reproduce wildlife `elk` text matching the ELK Stack skill; preserve uppercase acronym and explicit stack matching while eliminating lowercase wildlife false positives.
- [x] Fact-comparison tests 43; unit suite 1180 passed / 17 skipped; isolated PostgreSQL 1197 passed; test DB stopped.
- [ ] Continue fixture-backed Candidate Fit and Relocation-first quality checks.

## 2026-10-17 — Candidate Fit professional-network context

- [x] Reproduce business contact network text as a false technical Networking requirement; suppress only explicit professional/contact phrases.
- [x] Focused fit suites 74; unit suite 1182 passed / 17 skipped; isolated PostgreSQL 1199 passed; test DB stopped.
- [ ] Continue a separate Candidate Fit or Source Intelligence edge case with fixture-backed evidence.

## 2026-10-17 — Candidate Fit compound Docker requirement

- [x] Prevent `Docker Compose` from counting as a second Docker requirement unless Docker appears independently; preserve compound OR alternatives.
- [x] Fit tests 71; unit suite 1178 passed / 17 skipped; isolated PostgreSQL 1195 passed; test DB stopped.
- [ ] Continue Candidate Fit/source quality review with a concrete fixture-backed issue.

## 2026-10-17 — Remotive ambiguous Georgia location

- [x] Reproduce a `Georgia, USA` Remotive posting passing the GE target filter; disambiguate USA/U.S.A./U.S./United States qualifiers while retaining unqualified Georgia as GE.
- [x] Remotive tests 13; unit suite 1175 passed / 17 skipped; isolated PostgreSQL 1192 passed; test DB stopped.
- [ ] Continue independent Candidate Fit / source-quality work; real source yield and US market coverage are not inferred.

## 2026-10-17 — avoid false relocation restrictions from neutral wording

- [x] Reproduce neutral English/German/Russian citizen mentions being classified as hiring restrictions; require explicit restriction wording while retaining tested US and regional native-script phrases.
- [x] Relocation evidence tests 32; unit suite 1170 passed / 17 skipped; isolated PostgreSQL 1187 passed; test DB stopped.
- [ ] Continue an independent Candidate Fit or Source Intelligence regression; do not infer live hiring eligibility.

## 2026-10-17 — Relocation Evidence native citizenship terms

- [x] Reproduce missing Armenian/Georgian native-script citizen conditions and retain observed citizenship scope without making a legal conclusion.
- [x] Relocation evidence tests 29; unit suite 1167 passed / 17 skipped; isolated PostgreSQL 1184 passed; test DB stopped.
- [ ] Continue independent Candidate Fit/source-quality review using fixtures; live regional hiring eligibility remains unverified.

# Tasks

## 2026-10-17 — Telegram Career folder watcher

- [x] Inspect local 21-item manifest; all ID/username/type/access fields are unverified.
- [x] Add optional read-only folder preview and explicit broadcast ID selection in a private local User Client; reuse the existing watcher and preserve publication date/retry identity.
- [x] Separate explicit CV/advertising posts from possible vacancy posts; keep unknown salary unknown; add offline regressions.
- [ ] Owner performs interactive local MTProto login with private API credentials, reviews exact IDs/types/access and enables 2–3 broadcast channels.
- [ ] Measure live posts, true vacancies, Good/Stretch, false positives, duplicates and errors; then incrementally enable remaining verified channels. No live acceptance claimed.
- [x] Implement bounded per-approved-channel cursor catch-up without account-wide updates; offline cursor/order tests pass.
- [ ] Validate restart catch-up in the live 2–3-channel pilot; edited-post handling remains separate and unimplemented.
- [x] Reproduce four explicit candidate-header false positives and keep them out of vacancy ingestion; retain vacancy posts that merely ask applicants to send a résumé.
- [x] Show persisted filtered/duplicate channel counters in `/channels` and describe Bot API plus the optional local client accurately; 1277 offline unit tests passed, 21 PostgreSQL tests skipped.
- [x] Reproduce `Atlanta/Savannah, Georgia` Telegram location being mislabeled GE; leave country unknown while retaining `Tbilisi, Georgia` as GE. Full isolated PostgreSQL suite: 1300 passed.

## 2026-10-17 — Recruiter work-eligibility sensitive topics

- [x] Reproduce visa, work authorization and citizenship questions accepted as non-sensitive when model returned `requires_human=false`.
- [x] Add narrow English/Russian markers that force human review; no automatic replies enabled.
- [x] Recruiter tests: 15 passed; full unit suite 1257 passed/21 skipped; compileall, diff check and secret scan passed.
- [x] Publish PR #44 to feature and merge after CI (GitHub verified 2026-10-17); next tasks follow the unified root ROADMAP priorities.

## 2026-10-17 — Application Package Telegram failure integration

- [x] Verify persisted package → failed Telegram confirmation → `/prepare` retry against isolated PostgreSQL.
- [x] Confirm retry returns the same package without duplicate or content replacement.
- [x] Targeted isolated PostgreSQL file: 2 passed; full unit suite 1252 passed/21 skipped; compileall, diff check and secret scan passed.
- [x] Commit `7b90d5a`, publish PR #43 and merge after CI; feature now `0a50a29`.

## 2026-10-17 — Source Intelligence publication-age telemetry

- [x] Keep only explicit timezone-aware source dates eligible for age calculations; naive, malformed, missing and future timestamps remain unknown.
- [x] Add non-filtering age buckets: ≤7d, 8–30d, >30d, unknown; show them in source diagnostics.
- [x] Targeted availability/diagnostics/scan suites: 104 passed.
- [x] Full unit suite: 1252 passed, 20 skipped; compileall, diff check and secret scan passed.
- [x] Commit `a037d67`, merge PR #42 at feature `f6e354b` after all CI checks passed.
- [ ] Continue the next independent Relocation-first, Candidate Fit or Application Package gap.

## 2026-10-17 — Candidate Fit negated requirement variants

- [x] Reproduce contractions, “not a hard requirement/must-have”, and “no previous experience is necessary” becoming required.
- [x] Add direct negation normalization/patterns; keep these signals unknown without inferring refusal.
- [x] All 11 explicit non-requirement fixtures pass; prior positive clauses after “but”/“and” remain required.
- [x] Full unit suite: 1241 passed, 20 skipped; compileall, diff check, secret scan and CI passed.
- [x] Commit `c5e0f44`, merge PR #41 to feature at `543057f`.
- [ ] Continue an independent Source Intelligence or Relocation-first gap.

## 2026-10-17 — Greenhouse US Georgia postal-code variant

- [x] Reproduce `Atlanta, Georgia, GA`, `Georgia (GA)` and `GA, Georgia` entering GE-targeted results.
- [x] Exclude explicit Georgia+GA state markers while preserving `Tbilisi, Georgia (GE)`.
- [x] Greenhouse + Remotive tests: 52 passed; red reproduction confirmed all three failures before fix.
- [x] Full unit suite: 1234 passed, 20 skipped; compileall, diff check and secret scan passed.
- [x] Commit `f13acf8`, publish PR #40, merge after all three CI checks passed; feature now `d618dc8`.
- [ ] Continue the next independent Source Intelligence or Relocation-first gap.

## 2026-10-17 — Candidate Fit: explicit non-requirements

- [x] Reproduce four phrasings being scored as required despite explicit negation.
- [x] Narrowly classify direct non-requirement wording as unknown; preserve positive requirements after “but” and “and”.
- [x] Fact-comparison/recommendation/technical-score tests: 101 passed.
- [ ] Run remaining unit and static gates; update full current handoff and checkpoint.
- [ ] Continue the next independent Source Intelligence or Relocation-first issue.

## 2026-10-17 — distinguish US Georgia from country GE in Greenhouse

- [x] Reproduce “Atlanta, Georgia, USA” entering a GE-targeted Greenhouse search.
- [x] Disambiguate explicit US qualifiers without changing unqualified Georgia or Tbilisi, Georgia behavior.
- [x] Greenhouse/Remotive/relocation tests: 84 passed; full isolated PostgreSQL suite: 1246 passed; test DB stopped; compileall, diff check and secret scan passed.
- [x] Commit `236b065`, PR #38 passed Python checks, Docker build and secret scan, and merged to feature at `9244aca`.

## 2026-10-17 — recognize human medical networks as non-technical

- [x] Reproduce medical professionals and physician/nurse networks becoming required technical Networking skills.
- [x] Extend the narrow organizational-network exclusion while retaining explicit infrastructure network/firewall requirements.
- [x] Fact-comparison/technical-score tests: 91 passed; full isolated PostgreSQL suite: 1240 passed; DB stopped; compileall, diff check and secret scan passed.
- [x] Save checkpoint `6159bc0` and publish PR #37 to feature.
- [ ] Wait for PR #37 CI, then integrate if all checks pass.
- [ ] Continue a separate roadmap task.

## 2026-10-17 — do not let EURES detail budget truncate search cards

- [x] Reproduce five validated search cards collapsing to two results when `max_details=2`.
- [x] Keep details HTTP calls bounded separately from the already-collected results; un-enriched cards preserve safe search fields and portal link.
- [x] EURES tests: 27 passed; full isolated PostgreSQL suite: 1238 passed; test DB stopped; compileall, diff check and secret scan passed.
- [x] Save checkpoint `771abc8` and merge PR #36 to feature after CI passed.
- [ ] Continue the next independent roadmap issue.

## 2026-10-17 — prevent organizational networks from inflating Candidate Fit

- [x] Reproduce a healthcare organization network being classified as a required technical Networking skill.
- [x] Exclude narrow institutional network phrases while retaining network routing/firewall requirements.
- [x] Fact comparison/technical-score tests: 89 passed; full isolated PostgreSQL suite: 1237 passed; test DB stopped; compileall, diff check and secret scan passed.
- [x] Save checkpoint `be421c8` and publish PR #35 to feature.
- [x] Integrate PR #35 at feature commit `52aeb1c` after all CI checks passed.
- [ ] Continue a distinct Source Intelligence/Candidate Fit regression.

## 2026-10-17 — retain EURES search cards when detail enrichment fails

- [x] Reproduce valid EURES search cards being dropped after detail 404/503, including a total detail outage that failed the entire source.
- [x] Return search-level cards with official EURES fallback links when detail enrichment fails; keep successfully enriched cards, partial counters and per-detail diagnostics.
- [x] EURES tests: 26 passed; full isolated PostgreSQL suite: 1235 passed; test database stopped; compileall, diff check and secret scan passed.
- [x] Save checkpoint `6159bc0`, publish PR #37 and integrate at feature commit `1e66216` after CI passed.
- [ ] Continue another independent Source Intelligence/Candidate Fit improvement.

## 2026-10-17 — keep local work-authorization gates visible in remote eligibility

- [x] Reproduce worldwide boilerplate overriding an explicit existing Canadian work-authorization prerequisite and yielding a false `eligible=yes`.
- [x] Let explicit work-authorization requirements keep remote eligibility `uncertain`; do not infer rejection from unknown candidate authorization.
- [x] Relocation/source suites: 149 passed; full unit suite: 1214 passed, 20 PostgreSQL-dependent tests skipped because the isolated DB was stopped. Compileall, diff check and secret scan passed.
- [ ] Commit this follow-up and confirm CI on PR #33.
- [ ] Continue an independent Source Intelligence/Candidate Fit regression after feature integration.

## 2026-10-17 — serialize duplicate Candidate Facts resume imports

- [x] Reproduce two simultaneous confirmations of one resume fingerprint creating duplicate `ResumeProfile` rows and imported facts.
- [x] Recheck profile/source/fingerprint inside the repository transaction while locking the candidate profile; return the existing resume ID to the losing Telegram confirmation and consume its stale preview.
- [x] Targeted Telegram/repository integration checks: 28 passed; full isolated PostgreSQL suite: 1233 passed; compileall, diff check and secret scan passed. No schema change; isolated test DB stopped.
- [ ] Save the focused local checkpoint, publish PR against the feature branch, and wait for CI.
- [ ] Continue the next distinct Source Intelligence or Relocation-first regression.

## 2026-10-17 — bound HH ConnectTimeout retries

- [x] Reproduce the same HH ConnectTimeout being attempted once per search profile in one scan.
- [x] Apply the existing bounded HH cooldown to ConnectTimeout while preserving its notification and isolating other sources.
- [x] Targeted HH timeout/connection/TLS tests: 3 passed; full isolated PostgreSQL suite: 1231 passed; compileall, diff check, secret scan passed.
- [x] Checkpoint `4be92a6` and handoff `55a259b` pushed to PR #32; latest CI is running.
- [ ] After green CI, continue an independent Source Intelligence/Relocation-first task.

## 2026-10-17 — Russian Candidate Fit aliases

- [x] Reproduce missed `Линукса`, `Докера`, `Кубернетесом` requirements against canonical English Candidate Facts.
- [x] Add narrow Russian transliteration/inflection aliases; retain canonical output and thresholds.
- [x] Full isolated PostgreSQL suite: 1230 passed; targeted fact-comparison/model tests: 63 passed; compileall, diff check, secret scan passed.
- [x] Checkpoint `098497a` published to PR #32; CI rerun queued.
- [ ] After green CI, integrate into the feature branch and continue an independent Source Intelligence gap.

## 2026-10-17 — Application Package retry safety and audit retention

- [x] Review PR #31 and confirm local delivery-failure handling still allowed duplicate `/prepare` drafts.
- [x] Persist an immutable match marker, reuse existing packages regardless of later status, and serialize simultaneous retries with the existing match-row lock.
- [x] Exercise retry-after-status-change and concurrent-request behavior in isolated PostgreSQL; offline `/prepare` UX regressions covered.
- [x] Review PR #27's v7→v8 FK change; implement `ON DELETE RESTRICT` and prove the stored package/status history remains after a blocked job-delete attempt.
- [x] Targeted suite: 58 passed; full isolated PostgreSQL suite: 1226 passed; compileall, diff check, secret scan passed.
- [ ] Review exact work-branch vs feature/origin integration and resolve stale PR #31/#27 state without replaying duplicate code; do not touch `main` or production.
- [ ] Continue fixture-backed Source Intelligence/Candidate Fit improvements.

## 2026-10-17 — classify explicit skill advantage wording as preferred

- [x] Red regression reproduced “Linux experience would be an advantage” being treated as required under a Requirements heading.
- [x] Added narrow skill-local English advantage/beneficial and Russian “будет преимуществом” variants; no thresholds or weights changed.
- [x] Fit/interview/resume suites: 80 passed; full unit suite: 1186 passed, 17 skipped; compileall, diff check and secret scan passed. Checkpoint `74015e4`.
- [ ] Continue an independent Source Intelligence or Relocation-first offline regression.


## 2026-10-17 — classify explicit skill advantage wording as preferred

- [x] Red regression reproduced “Linux experience would be an advantage” being treated as required under a Requirements heading.
- [x] Added narrow skill-local English advantage/beneficial and Russian “будет преимуществом” variants; no thresholds or weights changed.
- [x] Fit/interview/resume suites: 80 passed; full unit suite: 1186 passed, 17 skipped; compileall, diff check and secret scan passed. Checkpoint `74015e4`.
- [ ] Continue an independent Source Intelligence or Relocation-first offline regression.


## 2026-10-17 — preserve positive skill requirement after contrastive negation

- [x] Red test reproduced a required skill classified `unknown` when a positive mention followed a negated mention after “but”.
- [x] Split contrastive clauses for required-skill classification; the skill must be named in the positive clause.
- [x] Fact-comparison tests: 44 passed; full unit suite: 1183 passed, 17 skipped; compileall, diff check, secret scan passed. Checkpoint `82d6ebf`.
- [ ] Continue with the next distinct offline source-quality, Candidate Fit or Relocation-first regression.


## 2026-10-17 — choose freshest same-source posting after canonical dedupe

- [x] Reproduce same-source multiple provider IDs mapping to one canonical Job while source selection returned the oldest ref.
- [x] Select the newest valid source evidence capture for non-exact lookups; preserve exact ID resolution and deterministic legacy fallback.
- [x] Focused tests: 38 passed; full isolated PostgreSQL suite: 1199 passed; DB stopped. Checkpoint `577859a`.
- [ ] Continue with a distinct Candidate Fit or Source Intelligence regression; do not conflate canonical match identity with exact provider-posting attribution.

## 2026-10-17 — rediscovery / partial failure / cross-source consistency review

- [x] Verify existing source snapshot refresh, stable first-seen provenance, independent refs after dedupe, and partial-cache attempt aggregation.
- [x] Focused offline suites: 95 passed, 1 skipped; isolated PostgreSQL rediscovery/dedupe/application-flow checks: 3 passed.
- [ ] Continue with a distinct, reproducible Candidate Fit or Source Intelligence issue. Exact provider posting attribution is not stored on canonical `JobMatch`; investigate only with a user-visible reproducer before proposing data-model work.

## 2026-10-17 — native Armenian/Georgian language requirement cues

- [x] Reproduce Armenian/Georgian required and preferred phrases being left unspecified; include explicit negations to guard against false required status.
- [x] Add narrow required/preferred/negated lexical cues; regional language text without a recognized cue remains unspecified.
- [x] Relocation evidence tests: 27 passed; full isolated PostgreSQL suite: 1182 passed.
- [ ] Continue relocation quality from fixtures; lexical references are not legal eligibility guidance or live acceptance.

## 2026-10-17 — Armenian and Georgian language evidence

- [x] Reproduce required/preferred language evidence silently missing Armenian and Georgian in English, Russian and native-script descriptions.
- [x] Canonicalize the two regional languages while leaving unsupported proficiency/requirement wording unspecified rather than inferred.
- [x] Relocation evidence tests: 21 passed; full isolated PostgreSQL suite: 1176 passed.
- [ ] Continue Relocation-first evidence coverage; no country-specific hiring eligibility was inferred or live-verified.

## 2026-10-17 — validate EURES application destinations before persistence

- [x] Reproduce EURES retaining credential-bearing HTTPS targets and failing detail enrichment on malformed IPv6 authorities.
- [x] Accept bounded HTTPS URLs with a hostname and no userinfo; otherwise retain the official EURES portal fallback, including for URLs exceeding Telegram's link limit.
- [x] EURES/vacancy-link tests: 69 passed; full isolated PostgreSQL suite: 1170 passed.
- [ ] Continue offline Relocation-first evidence review; external links and job eligibility still require human confirmation.

## 2026-10-17 — validate source links before Telegram rendering

- [x] Reproduce vacancy details rendering `javascript:`, credential-bearing and protocol-relative source URLs as clickable HTML.
- [x] Share bounded HTTP(S), host, credential, control-character and authority validation across vacancy details, list attribution and `/prepare` preview.
- [x] Link/rendering suites: 112 passed; full isolated PostgreSQL suite: 1164 passed; post-suite link regressions: 6 passed.
- [ ] Continue Relocation-first evidence review; no live source or employer action was performed.

## 2026-10-17 — reject boolean EURES publication timestamps

- [x] Reproduce booleans being treated as integers and rendered as 1970 publication dates.
- [x] Keep boolean creation dates unknown while preserving numeric epoch-millisecond handling.
- [x] EURES tests: 21 passed; full isolated PostgreSQL suite: 1161 passed.
- [ ] Continue Source Intelligence/Relocation-first offline checks; source freshness remains distinct from publication timestamp presence.

## 2026-10-17 — isolate malformed EURES search metadata

- [x] Reproduce a non-object `locationMap` throwing `TypeError` and aborting the whole parsed page.
- [x] Treat malformed optional location/employer blocks as unknown/empty metadata while retaining the listing and valid siblings.
- [x] EURES tests: 19 passed; full isolated PostgreSQL suite: 1159 passed.
- [ ] Continue offline Source Intelligence/Relocation-first review; live source acceptance remains separate.

## 2026-10-17 — EURES whole-token query relevance

- [x] Reproduce `Java` matching the unrelated `JavaScript Developer` title through substring filtering.
- [x] Require query-token boundaries while preserving meaningful punctuation tokens and existing any-token query semantics.
- [x] EURES tests: 18 passed; full isolated PostgreSQL suite: 1158 passed.
- [ ] Continue offline Source Intelligence/Relocation-first review; fixture checks are not live source acceptance.

## 2026-10-17 — prevent GitLab repository work from inflating CI fit

- [x] Reproduce GitLab-only repository/project wording being extracted as a GitLab CI requirement.
- [x] Require explicit CI/CD, pipeline or runner context for the GitLab CI skill; preserve “CI/CD based on GitLab”.
- [x] Candidate Fit, scoring, resume diff and interview suites: 101 passed; full isolated PostgreSQL suite: 1157 passed.
- [ ] Continue Source Intelligence/Relocation-first offline review; no live source acceptance was performed.

## 2026-10-17 — correct source first-seen provenance in vacancy details

- [x] Reproduce that “Источник обнаружен” was populated from refreshed relocation evidence `captured_at`, making old listings appear newly discovered.
- [x] Use the existing stable `JobSourceRef.first_seen_at` and serialize legacy naive-UTC values explicitly as UTC; keep the evidence capture timestamp intact and separate.
- [x] Targeted vacancy detail/service tests 49 passed; full isolated PostgreSQL suite 1154 passed; compileall and diff check passed.
- [ ] Next: continue offline Source Intelligence/Candidate Fit gaps; live source freshness and yield remain unverified.

## 2026-10-17 — Himalayas application-link ingestion boundary

- [x] Reject credential-bearing, nonstandard-port, malformed-port, HTTP and off-domain Himalayas application links before normalization/persistence; preserve valid official HTTPS links.
- [x] Reject oversized provider GUID/URL fallback values with stable hashes while keeping ordinary IDs and vacancy URL unchanged.
- [x] Himalayas source suite 35 passed; full isolated PostgreSQL suite 1153 passed.
- [ ] Continue source adapter reliability and Candidate Fit work; live feed relevance remains unverified.

## 2026-10-17 — concurrent cross-source canonical dedupe acceptance

- [x] In isolated PostgreSQL, concurrently ingest two provider postings with one canonical fingerprint; verify one Job row and both provider references persist.
- [x] Targeted race test 1 passed; full isolated PostgreSQL suite 1154 passed.
- [ ] Continue review of source identity/provenance and practical relocation fit; no live source scan was performed.

## 2026-10-17 — Application tracking rollback acceptance

- [x] Inject status-history insert failure and verify the current status and append-only timeline roll back together in isolated PostgreSQL.
- [x] Targeted fault-injection test 1 passed; full isolated PostgreSQL suite 1139 passed.
- [ ] Continue Source Intelligence with a concrete, locally reproducible adapter/parsing gap; keep live source relevance and HH root cause gated on authorized runtime evidence.

## 2026-10-17 — preserve canonical identity on incomplete source refresh

- [x] Reproduce blank country/city being treated as complete during same-posting refresh; require nonempty trimmed location fields before updating canonical fingerprint.
- [x] Isolated PostgreSQL regression and full suite: 1140 passed. Existing canonical location/fingerprint preserved; schema and cross-source matching policy unchanged.
- [ ] Continue practical Source Intelligence and Candidate Fit improvements using local evidence; live result yield still needs owner-approved source acceptance.

## 2026-10-17 — Candidate Fit OpenTelemetry vocabulary

- [x] Add explicit `OpenTelemetry` / `Open Telemetry` matching for vacancy requirements and Candidate Facts; avoid ambiguous acronym-only matches.
- [x] Focused fit/score tests 65 passed; full isolated PostgreSQL suite 1144 passed.
- [ ] Continue reviewing the remaining supported-vocabulary gaps and Source Intelligence contracts without broad score-policy changes.

## 2026-10-17 — Application Package delivery retry safety

- [x] Distinguish `/prepare` failures before persistence from Telegram delivery failures after durable save; point to `/applications` and warn that repeating preparation creates a second draft. Test command and callback delivery failures.
- [x] Targeted tests 47; unit suite 1124 passed/14 skipped; isolated PostgreSQL suite 1138 passed; compileall, diff check and secret scan passed.
- [ ] Next: continue offline workflow reliability and practical source/Candidate Fit improvements. Live source usefulness, Telegram channel acceptance and HH root-cause diagnosis remain blocked on owner-approved runtime evidence.

## 2026-10-17 — source relevance follow-up

- [x] Reproduce RemoteOK short-role loss and substring false positives; retain whole QA/HR/Go/C# terms with title/tag matching and all-specific-token semantics. Targeted 71; full isolated PostgreSQL 1070 passed.
- [x] Preserve explicit known-geography `only` labels from RemoteOK/Arbeitnow in remote scope and source evidence; bare office/global labels remain unknown. Two adapter regressions reproduced the loss; targeted 79 and full isolated PostgreSQL 1091 passed.
- [x] Enforce scan diagnostic UTF-16 budgets with emoji/profile names and intact HTML; offline scan/status test preserves complete saved history. Targeted 56; full isolated PostgreSQL 1096 passed.
- [x] Fix fallback matching dropping short role names and substring collisions; eight red regressions, targeted 83 and full isolated PostgreSQL 1104 passed. Structured skill scoring/thresholds unchanged.
- [x] v3.6: fix resume role/content ambiguity for short names and Java/JavaScript; six red regressions, targeted 69 and full isolated PostgreSQL 1110 passed. CV/facts unchanged; no score boost from CV selection.
- [x] Source reliability: RemoteOK/Arbeitnow malformed optional tags and RemoteOK invalid optional salary types no longer fail or discard a valid row; targeted 71, full isolated PostgreSQL 1125 passed.
- [x] Normalize RemoteOK publication dates conservatively and keep invalid dates unknown; RemoteOK tests 30, full isolated PostgreSQL 1130 passed.
- [x] Preserve the common system/systems role variant and exclude generic engineer/administrator terms when choosing among CVs; full isolated PostgreSQL 1134 passed.
- [x] Bound unconfirmed resume previews to 15 minutes, 8 per user and 64 total; evict oldest only in memory. Targeted 17, full isolated PostgreSQL 1136 passed.
- [x] Verify Candidate Facts ADD/UPDATE/KEEP against code/tests: overlap defaults to KEEP, duplicate target UPDATE rejected, stale/foreign replacement blocked in transaction, imported experience remains `unknown`/noncommercial. Existing tests cover these invariants; no duplicate code change.
- [ ] Live source/query usefulness remains pending an explicitly authorized scan environment.

## 2026-10-17 — v3.5.7 rejection diagnostics

- [x] Preserve a deterministic reason for every vacancy excluded by search settings without changing score thresholds or treating unknown evidence as refusal.
- [x] Aggregate reason counts across source attempts and show the three largest causes in `/scan` and `/scanstatus` source diagnostics.
- [x] Cover Career-first/Relocation-first separation, geography, required visa evidence, salary and source aggregation. Targeted 96 passed; full isolated PostgreSQL suite 1058 passed.
- [x] Distinguish below-threshold scoring causes in source and per-profile scan summaries using structured scores rather than parsing human prose.
- [ ] Next: use measured settings/scoring causes to improve source/query relevance without weakening the 65 threshold; live measurements require an explicitly authorized scan environment.

## 2026-10-17 — `/prepare` failure integrity

- [x] Push only `f82c8d3`, `374b375`, `f53256e` to the feature branch after linear-history, secret and prior isolated-suite checks; remote SHA `f53256e` verified. Leave proposal files untracked.
- [x] Remove obsolete `.bashrc` launcher functions after timestamped backup; fresh Bash resolves all four one-word commands through `scripts/job-agent-codex` symlinks and their distinct dry-runs.
- [x] Render `/prepare` preview before saving; atomically save owner-scoped draft, status event and match status. Prove render failure has no write and injected PostgreSQL update failure rolls back the draft. Targeted 7 + 1 passed; full isolated suite 1053 passed.
- [ ] Next: test failure after durable package commit during Telegram delivery and make retry behavior clear without sending any employer application; continue tracking and source/fit roadmap tasks.

## 2026-10-17 — first offline workflow acceptance

- [x] Verify current feature branch on isolated tmpfs PostgreSQL: 1051 passed
  before the new test; 1052 passed after it.
- [x] Cover two postings sharing one canonical Job, selected-source score,
  owner review/saved state, frozen package export and cross-user denial after
  a different source refreshes its posting.
- [ ] Add further distinct offline workflow tests for grounded `/prepare`
  delivery and tracking; atomic-write failure injection is covered.

## 2026-10-17 — command-center consolidation follow-up

- [x] Match eight visible command-center tasks to five indexed primary
  rollouts and three inaccessible untitled IDs; retain all histories.
- [x] Map 17 child reports to current code/docs and remaining validation;
  preserve reusable bug/review prompts and old experiment limits without
  copying private candidate data.
- [x] Add one-word Main/Fast/Deep/agents launchers for Codex CLI v0.163.0;
  verify pinned Main and real ephemeral read-only Luna/low and Sol/high runs.
- [ ] Owner decides archival after manual review of the three missing-rollout
  tasks and private-context preservation. No automatic archive or deletion.

## 2026-10-17 — local Codex history inventory

- [x] Reconcile `dabe9a3` with BRIEF and inventory 22 indexed Codex threads
  plus one metadata-only rollout without archiving or deleting sessions.
- [x] Preserve distinct owner input, historical results and child-agent
  findings in [CODEX_SESSION_INVENTORY.md](CODEX_SESSION_INVENTORY.md), with
  private relocation facts kept outside Git and no duplicated roadmap.
- [ ] Follow current BRIEF priorities; validate historical risks against
  current code/tests before changing implementation or status.

## Active priorities — 2026-10-16

- [x] Independent audit fixes #19–#26 merged; PR #28 at-least-once notifications merged with green PR CI. Latest combined CI needs independent check.
- [ ] Review HH reservation ambiguity/reconciliation and offline acceptance; no live submissions.
- [x] Owner chose at-least-once job alerts; delivery journal, leased PostgreSQL claims, independent minute retries and /delivery implemented in PR #28.
- [x] PR #28 offline PostgreSQL, callback UX, concurrency and failure tests passed CI (1051 passed, 82.94%).
- [ ] Live Telegram acceptance and operational retry monitoring before deployment; do not send to real users without owner approval.
- [ ] Test safe preservation of Application snapshots/history under future Job deletion (no production migrations now).
- [ ] End-to-end isolated PostgreSQL workflow and source provenance/multiuser regressions.
- [ ] Return to canonical ROADMAP's v3.5.7 acceptance, then Source Intelligence, Candidate Fit, Application Package, Recruiter and Interview stages.

Older task logs below are historical. Current priorities and restrictions: [BRIEF.md](BRIEF.md).

## 2026-10-15 — exact source posting at ingestion completed

- [x] Reproduce a cross-source canonical Job causing score inputs from a different posting.
- [x] Resolve source ref by feed and provider posting ID; score and notify from its normalized snapshot.
- [x] Keep HH full-detail prefilter tied to the exact provider ID; verify two same-feed IDs sharing a Job on PostgreSQL.
- [x] Full isolated PostgreSQL 1017 passed.
- [ ] Next: source quality and Candidate Fit explanation, then Application Package, Relocation-first and broader roadmap.

## 2026-10-15 — Interview Agent alternatives completed

- [x] Reproduce “Docker or Kubernetes” creating two required exercises while Candidate Fit counts one choice.
- [x] Select one curated scenario per explicit required/preferred OR group and label the alternatives in the practice plan.
- [x] Full isolated PostgreSQL 1016 passed.
- [ ] Next: interactive practice/feedback with owner-controlled answers, plus Source Intelligence and Candidate Fit work from the full roadmap.

## 2026-10-15 — UTF-16-safe package preview completed

- [x] Reproduce an emoji-heavy `/prepare` preview exceeding Telegram's UTF-16 limit despite its character count.
- [x] Budget the visible preview in UTF-16 units and give a `/job` fallback for excessively escaped links.
- [x] Full isolated PostgreSQL 1014 passed; saved package/export retain full text.
- [ ] Next: independent Candidate Fit and Source Intelligence quality, then remaining roadmap.

## 2026-10-15 — employer clarification prompts completed

- [x] Derive bounded, prioritized employer questions from unknown relocation evidence in the vacancy card.
- [x] Do not present confirmed conditions as unknown or make candidate-specific legal conclusions.
- [x] Synthetic/card regressions and full isolated PostgreSQL 1012 passed.
- [ ] Next: deeper source quality and Candidate Fit; continue Application Package, Recruiter, Interview, AI Router and v4.x.

## 2026-10-15 — model failure fallback for Application Package completed

- [x] Reproduce a model exception aborting cover-letter generation.
- [x] Use local fact-grounded draft on model client/call error or empty output, without echoing error text.
- [x] Focused 34 and full isolated PostgreSQL 1009 passed.
- [ ] Next: continue Source Intelligence, Candidate Fit, Relocation-first and broader roadmap.

## 2026-10-15 — fallback letter fact grounding completed

- [x] Reproduce inactive/deleted facts appearing in fallback draft and unsupported experience wording when facts are absent.
- [x] Filter both fallback and model Candidate Fact payloads to active, nondeleted facts; use neutral wording for empty evidence.
- [x] Focused 32 and full isolated PostgreSQL 1007 passed.
- [ ] Next: continue Application Package claim review, Source Intelligence and Relocation-first; then Recruiter/Interview and remaining roadmap.

## 2026-10-15 — source-bound HH details cache completed

- [x] Reproduce stale full details overlaying a changed source card and stale cache reuse.
- [x] Bind new HH cache writes to normalized source snapshots, retain old cache/provenance, and refetch when the card changes.
- [x] Reject a cache save raced by another source-card update under row lock; synthetic and isolated PostgreSQL regressions passed. Full isolated suite: 1004 passed.
- [ ] Next: broader source quality and Relocation-first evidence utility; revisit legacy unbound caches only with trustworthy historical provenance.

## 2026-10-15 — package preview identity and link completed

- [x] Reproduce a dense review preview that could omit selected-posting context.
- [x] Reserve selected source/posting ID and validated manual link in bounded preview; preserve unsafe-link rejection.
- [x] Focused 58 and full isolated PostgreSQL 1002 passed.
- [ ] Next: Source Intelligence cached-detail freshness/provenance or Relocation-first evidence utility, then broader roadmap.

## 2026-10-15 — selected-source observation display completed

- [x] Show provider posting ID and last ingestion-observation timestamp in the vacancy card, distinct from publication date.
- [x] Hide absent or invalid timestamps; keep unknown availability explicit. Focused 58 and full isolated PostgreSQL 1001 passed.
- [ ] Next: source quality and cross-source consistency, then Relocation-first evidence utility and broader roadmap.

## 2026-10-15 — consistent required-experience gating completed

- [x] Reproduce a three-year minimum plus preferred 5+ years incorrectly marked `skip`.
- [x] Reuse required-year extraction for high-experience gating; preserve the existing 3–4-year stretch boundary.
- [x] Verify required more-than-five remains gated and preferred-only 5+ remains ungated. Full isolated PostgreSQL: 1000 passed.
- [ ] Next: independent Source Intelligence quality or Relocation-first evidence utility, then resume broader roadmap.

## 2026-10-15 — selected provider posting identity in packages completed

Saved packages now retain the selected source ID and provider posting ID, with source-specific HH draft text; focused 67 and full isolated PostgreSQL suite passed. Next: choose an independent Candidate Fit or source quality improvement with realistic fixtures, then continue Application Package and Relocation-first.

## 2026-10-15 — source-specific posting snapshot for review and preparation

Each newly ingested or refreshed `JobSourceRef` now stores its own normalized posting fields beside evidence and verified detail cache. Vacancy details, Candidate Fit review and `/prepare` use the selected source's title, description and structured fields; already cached full HH details take precedence for drafting. A synthetic cross-source regression reproduced a Jobs.ge package using an HR.ge description before the change. PostgreSQL regression confirms same-source refresh updates its own snapshot and a second source keeps separate text. Existing refs without a normalized snapshot retain the canonical fallback until rediscovery. Full isolated PostgreSQL: 996 passed.


## 2026-10-15 — align Application Package with displayed source

`/prepare` and vacancy details now use one source-reference preference order. A synthetic shared Job with `hr_ge` and `jobs_ge` previously displayed one source but prepared the other source's URL and mobility evidence; the regression now keeps the package source aligned with the detail view. This selects a deterministic review source, not a claim about which feed originally created the match. Focused package/detail tests: 38 passed; full isolated PostgreSQL: 994 passed.


## 2026-10-15 — keep Arbeitnow remote location unconfirmed

Arbeitnow no longer assigns Germany as the work country or a city to every remote posting. Its free-form `location` is retained as `source_location`; Relocation Evidence keeps the work country unknown for a synthetic remote “Worldwide” fixture. Onsite source behavior is unchanged. Focused adapter/evidence/preferences tests: 63 passed; full isolated PostgreSQL: 993 passed.


## 2026-10-15 — recognize explicit “provide no housing” refusals

Relocation Evidence now treats “We provide no housing” and “We offer no accommodation” as explicit refusals. A regression showed these phrases were previously marked as provision because the positive verb rule matched across `no`. Focused evidence/detail tests: 50 passed; full isolated PostgreSQL: 992 passed.


## 2026-10-15 — distinguish housing denial from an information offer

Relocation Evidence now recognizes explicit employer verb-first refusals such as “We do not provide housing” and “We cannot offer accommodation”. It no longer reads “housing details are provided” as accommodation provision, and a refusal to provide housing details remains unknown. Synthetic regression reproduced the previous false offer. Focused evidence/detail tests: 50 passed; full isolated PostgreSQL: 992 passed.


## 2026-10-15 — preserve conflicting housing evidence

Relocation Evidence now marks contradictory explicit housing provision/refusal statements as `unknown` with `conflicting_text` confidence and both source excerpts. A single explicit provision or refusal keeps its prior classification. Synthetic regression reproduced the previous false refusal. Focused evidence/detail tests: 49 passed; full isolated PostgreSQL: 991 passed.


## 2026-10-15 — keep RemoteOK free-form location out of country claims

RemoteOK's free-form `location` is no longer persisted as normalized `country`: labels such as “Worldwide” or an office location do not establish the employee's work country or hiring eligibility. The original text is retained as `source_location`, so Relocation Evidence shows it as an excerpt while the country value remains unknown. Remote scope remains unspecified. Focused source/location tests: 54 passed; full isolated PostgreSQL: 990 passed.


## 2026-10-15 — keep preferred experience out of hard fit threshold

Candidate Fit now ignores explicitly preferred/desirable years when deriving the minimum required experience. When a required minimum is also stated, only required/unlabelled bands determine the threshold; a preferred-only band does not create a mandatory years-of-experience gap. Regression reproduced a 3-year minimum plus 5 years preferred being misread as 5. Focused fit/resume tests: 60 passed; full isolated PostgreSQL: 990 passed.


## 2026-10-15 — capture Russian negotiable start timing

Added a regression and source-text pattern for “Выход на работу по договорённости”. Confirmed immediate Russian start wording remains classified independently. Full isolated PostgreSQL: 988 passed.


## 2026-10-15 — Russian accommodation evidence

Added explicit Russian positive and negative accommodation wording with
regression coverage; mentions without an assertion stay unknown. Full isolated
PostgreSQL: 988 passed.

## 2026-10-15 — cap vacancy detail cards with mobility evidence

Large posting plus all eight mobility signals reproduced a Telegram message
overrun. Added a UTF-16-aware ceiling and dynamically shortens only the
description. Evidence, scoring and source link stay visible. Full isolated
PostgreSQL: 988 passed.

## 2026-10-15 — recognize short non-required skill wording

Extended the explicit technical-skill negation parser to cover “No Kubernetes
required”; other independent requirements are preserved. Focused tests: 67;
full isolated PostgreSQL: 987 passed.

## 2026-10-15 — honor skill-specific preferred phrases

Added narrow English/Russian per-skill preference wording under broad
Requirements headings. A plus-marked technology is preferred, while separate
must-haves keep their importance. Focused tests: 66; full isolated PostgreSQL:
986 passed.

## 2026-10-15 — disclose missing historical evidence snapshots

Legacy Application Package previews/exports now identify missing structured
mobility evidence and never backfill mutable current source state into the
historical record. Focused tests: 12 passed; full isolated PostgreSQL: 984.

## 2026-10-15 — verify evidence refresh preserves package snapshot

Extended the repeat-source PostgreSQL regression: current source location
evidence refreshes, while a prepared package keeps its first capture. Targeted
isolated DB test: 1 passed; full suite at parent checkpoint: 984 passed.

## 2026-10-15 — exclude explicit non-required skills from must-haves

Red test reproduced “No Kubernetes experience required” becoming a must-have
under Requirements. Added narrow per-clause negation handling; separate skills
retain their own importance. Focused tests: 64; full isolated PostgreSQL: 984
passed.

## 2026-10-15 — German Relocation Evidence fixtures

Added a synthetic German fixture covering several hiring and relocation
conditions, and fixed a `Deutschland`/`Deutsch` false match. Focused tests: 87;
full isolated PostgreSQL: 982 passed. Continue locale coverage only with
explicit text fixtures; legal meaning remains outside the parser.

## 2026-10-15 — avoid cross-component support inference

Added a source-evidence boundary for ambiguous visa/relocation wording: if a
sentence-level refusal may belong to another component, retain unknown and the
excerpt rather than storing a false refusal. Scoring code is unchanged.
Focused tests: 46; full isolated PostgreSQL: 981 passed.

## 2026-10-15 — classify start-timing evidence

Added a bounded category beside the exact source phrase: immediate, relative
window, stated date, notice period, or negotiable. No candidate-fit judgment
is made. Focused tests: 44; full isolated PostgreSQL: 979 passed. Next: continue
source-aware evidence and independent Candidate Fit/Application Package work.

## 2026-10-15 — retain multiple language conditions

Language evidence no longer stops at the first language mention. It records
multiple supported language conditions independently and retains conflicting
required/preferred statements for review. CEFR stays separate. Focused tests:
47; full isolated PostgreSQL: 978 passed. Next: continue source/location
provenance or Candidate Fit; live legal evidence remains separate.

## 2026-10-15 — distinguish explicit authorization non-requirement

Added tri-state handling for the prior-work-authorization condition: explicit
required, explicit not required, unknown, and conflicting assertions. No legal
eligibility result is inferred. Focused tests: 82; full isolated PostgreSQL:
977 passed. Next: continue source-provenance gaps or return to Candidate Fit.

## 2026-10-15 — freeze Relocation Evidence in Application Package

`prepare_match` carries the selected source evidence into the immutable vacancy
snapshot; HH application snapshots do likewise. Export emits the saved evidence
instead of reading current source state. PostgreSQL regression covers a source
refresh after package capture; the saved original evidence remains intact. No
schema change. Focused: 20 passed; repeat-refresh DB regression: 1 passed;
full isolated PostgreSQL: 976 passed.

## 2026-10-15 — preserve source work-location excerpt

Work-country evidence now includes an adapter-provided structured location
excerpt when available and displays it alongside the normalized code. No
country is inferred from unrelated description text. Focused tests: 41; full
isolated PostgreSQL: 975 passed. Continue with source-specific locale mappings
only where adapters provide explicit structured provenance.

## 2026-10-15 — separate citizenship and residence scope

Added a bounded interpretation for explicit restriction snippets: citizenship
versus residence/location, with the original excerpt shown in the vacancy
detail. This is not a legal conclusion. Focused tests: 41; full isolated
PostgreSQL: 975 passed. Next: broaden country/language mappings only where
source text supports them; then continue independent Fit/Source Intelligence.

## 2026-10-15 — classify housing and language evidence

Extended Relocation Evidence: housing confirmation now requires explicit
provision/refusal language; language retains required/preferred/unspecified
status and explicit English CEFR separately. Vacancy details display this
distinction with source evidence. Ambiguous mentions are not promoted into
benefit/eligibility assertions. Focused tests: 84; full isolated PostgreSQL:
974 passed. Next: improve country and hiring-scope extraction conservatively,
then return to independent Candidate Fit/Source Intelligence work.

## 2026-10-15 — source-scoped Relocation Evidence v1

Added versioned per-source evidence records for work country, hiring scope,
existing authorization, visa sponsorship, relocation assistance, housing,
language and start timing. Observed evidence carries source ID/URL, excerpt,
capture timestamp and categorical confidence; unknown values have no invented
quote. Vacancy detail cards expose the provenance. A synthetic regression
found and fixed `No relocation details` being mistaken for a refusal. No
scoring/Candidate Fact change. Full isolated PostgreSQL suite: 973 passed.
Next: tighten extracted language/country/conditions with synthetic fixtures,
then return to Source Intelligence or Candidate Fit; live legal eligibility
and Telegram acceptance remain separate.

## 2026-10-15 — isolate recruiter instructions from message content

Applies the same data/instruction boundary to recruiter drafting. Sensitive
topics still require human response; automatic replies remain explicitly
opt-in and OFF by default. Focused tests: 16 passed; isolated PostgreSQL:
969 passed.

## 2026-10-15 — isolate cover-letter instructions from vacancy content

Separates cover-letter developer instructions from JSON vacancy/resume/fact
data and treats embedded instructions as untrusted. This is a prompt-injection
mitigation, not a guarantee of factual output; the user still reviews every
draft. Focused LLM tests: 5 passed; isolated PostgreSQL suite: 968 passed.

## 2026-10-15 — add OpenShift to Fit and Interview practice

Added OpenShift (including Red Hat OpenShift) as a distinct requirement and
curated safe rollout practice. Focused fit/interview tests: 87 passed; full
isolated PostgreSQL suite: 967 passed.

## 2026-10-15 — preserve timezone evidence in vacancy dates

Updated vacancy publication-date display to retain explicit UTC or unknown
timezone semantics. No freshness or stale-posting claim is inferred. Focused
detail/source tests: 68 passed; isolated PostgreSQL suite: 964 passed.

## 2026-10-15 — nested Candidate Fit alternatives

Implemented nested flat parenthesized OR chains as one explainable choice when
each option is an unambiguous supported skill. Independent requirements remain
separate; mixed AND/OR and repeated mentions remain conservative. Focused
fit/resume/score tests: 79 passed; full isolated PostgreSQL suite: 960 passed.

## 2026-10-15 — refresh repeated source postings safely

Completed repeat-discovery refresh for existing provider IDs. Nonempty Job
fields/current raw values update; unknown values, verified detail cache,
source provenance and prior Application Package snapshots are retained.
Advisory/row locks protect concurrent source/fingerprint upserts. Existing
identity collisions are not merged. Two new isolated PostgreSQL regressions;
full suite: 957 passed. Next: investigate safe reconciliation of already
diverged cross-source Job rows, or continue Candidate Fit/Relocation-first work.

## 2026-10-15 — do not infer a salary period in match scoring

Removed the implicit monthly fallback in salary ranking. Unknown periods
remain reviewable and receive a neutral score; explicitly monthly/annual values
retain their established normalized comparison. Focused regression suite: 61
passed; full isolated PostgreSQL suite: 955 passed.

## 2026-10-15 — disclose unrecognized requirements in package review

Package review now distinguishes “no recognized technical requirements” from
“no discrepancies among recognized skills,” preserving the manual review
prompt when deterministic extraction finds nothing. Focused tests: 20 passed.

## 2026-10-15 — scoped `/prepare` command

Implemented `/prepare <vacancy_id> [career|relocation]` using the existing
owner-scoped package workflow. Active-profile scoping, missing-match behavior
and sanitized error handling have regression coverage. Focused tests: 31;
isolated PostgreSQL suite: 953 passed. Next: continue practical Candidate Fit
and source-quality work from ROADMAP; preserve Recruiter/Interview and v4.x
directions. Live Telegram acceptance remains separate.

## 2026-10-15 — mobility evidence in package review

Prepared packages now show the existing visa/relocation/work-permit evidence
and prior-authorization requirement, with unknowns and personal-eligibility
limits preserved. Preview HTML is bounded to 3700 characters, keeps the mobility
block, and points to full CV review when details are omitted. Malformed,
credential-bearing and overlong URLs do not break previews or become truncated
links. Focused tests: 116; full isolated PostgreSQL: 948 passed.

## 2026-10-15 — source yield before preference filters

Per-source attempts now retain received-result and preference-exclusion counts.
The dashboard distinguishes an empty source from results removed by settings,
separately from scoring filters and processing errors. Counts cover adapter
results per profile/attempt (including cache reuse), not unique global jobs.
Focused source/preferences tests: 91; isolated PostgreSQL: 943 passed.

## 2026-10-15 — serialize manual application status changes

A deterministic isolated PostgreSQL regression reproduced duplicate status
events from simultaneous identical updates. A row lock now serializes the
status check and append for the owning application. Focused DB/handler tests:
32 passed; full isolated PostgreSQL: 941 passed. No schema migration.

## 2026-10-15 — immutable vacancy snapshot in Application Package

Schema v7 adds an additive vacancy snapshot: title, company, original stored
description and source vacancy URL. Prepared and HH packages capture it beside
the CV/letter; export no longer queries the mutable Job. Provider/application
URLs remain separate. Old rows disclose missing snapshots without backfilling
current data as historical fact. Focused package/migration tests: 64 passed;
full isolated PostgreSQL: 940 passed, including v4-to-v7 upgrade/idempotency
and export after later Job edits. Production schema remains untouched.

## 2026-10-15 — nonoverlapping Candidate Fit alternatives

Pure OR expressions such as `Linux or (Docker or Kubernetes)` now produce
one alternative group. Previously the inner group was counted twice, lowering
Linux-only coverage and showing a spurious missing group in resume review.
Three regressions failed before the fix. Focused fit/score/resume: 70 passed;
full isolated PostgreSQL: 936 passed.

## 2026-10-15 — normalize Arbeitnow epoch publication dates

- [x] Convert numeric `created_at` epoch seconds to UTC ISO timestamps.
- [x] Keep missing, malformed, boolean and out-of-range values unknown.
- [x] Focused Arbeitnow/detail tests: 46; isolated PostgreSQL: 933 passed.
- [ ] Measure freshness only where source semantics and listing lifecycle are
  documented; do not equate publication date with active hiring.

## 2026-10-15 — application status provenance in exports

- [x] Label export status as locally recorded and not independently receipt-
  verified by the employer/provider.
- [x] Verify package and handler tests (40) and isolated PostgreSQL (929).
- [ ] Record provider-side submission evidence only when the provider exposes
  verifiable receipt data; preserve manual statuses as owner-entered data.

## 2026-10-15 — Remotive publication timestamp normalization

- [x] Normalize timezone-aware RSS RFC 2822 and API ISO dates to UTC ISO.
- [x] Keep malformed and timezone-less publication values unknown.
- [x] Focused Remotive tests: 8 passed; isolated PostgreSQL: 929 passed.
- [ ] Extend source freshness indicators only where each feed documents
  publication/expiry semantics and timezone behavior.

## 2026-10-15 — isolated parenthesized skill alternatives

- [x] Recognize explicit parenthesized alternatives next to an independent
  requirement without grouping that independent skill.
- [x] Keep slash, repeated, and responsibilities-section examples ungrouped.
- [x] Verify focused fit/scoring/resume tests (67) and isolated PostgreSQL (928).
- [ ] Extend nested parentheses or multiple compound clauses only with
  separate grammar and scoring regressions.

## 2026-10-15 — keep extra alternative CV claims reviewable

- [x] Preserve a satisfied alternative group while flagging extra CV options
  that have no Candidate Fact support.
- [x] Verify both `/resumediff` and `/prepare` presentation.
- [x] Focused comparison tests: 63; isolated PostgreSQL: 923 passed.

## 2026-10-15 — recruiter sensitive-context fallback

- [x] Require human review for sensitive markers in the supplied conversation
  context as well as the latest recruiter question.
- [x] Recognize English `passport` and parse JSON string booleans explicitly.
- [x] Verify focused recruiter tests (13) and isolated PostgreSQL (921).
- [ ] Keep outbound auto-reply disabled by default and separately verified.

## 2026-10-15 — preserve alternatives in resume comparison

- [x] Carry required/preferred OR groups into resume coverage comparison.
- [x] Require one same option in both Candidate Facts and selected CV for
  confirmation; disclose different or missing evidence without false claims.
- [x] Verify focused comparison/command tests (61) and isolated PostgreSQL (917).
- [ ] Extend to nested/compound alternatives only with conservative extraction
  and fit/application regressions.

## 2026-10-15 — tighten salary-period text boundary

- [x] Require a recognized period unit immediately after the salary amount.
- [x] Add regression for unrelated nearby date text.
- [x] Verify focused salary tests (83) and isolated PostgreSQL (914).

## 2026-10-15 — Interview Agent IaC/cloud/observability exercises

- [x] Add deterministic exercises for Terraform, Ansible, AWS, Grafana and Helm.
- [x] Cover safe/reversible operations, least privilege and evidence checks.
- [x] Verify focused interview/command tests (31) and isolated PostgreSQL (913).
- [ ] Define privacy-safe answer retention and feedback rubric before adding
  interactive answer capture or scoring.

## 2026-10-15 — source publication-date field coverage

- [x] Count nonempty and absent publication-date fields per source attempt.
- [x] Show coverage in source summaries without stale/validity inference.
- [x] Verify focused source tests (55) and isolated PostgreSQL suite (912).
- [ ] Add freshness or expiry assessment only where source semantics and
  timezone/format evidence are defined.

## 2026-10-15 — display explicit salary period evidence

- [x] Show explicit nearby periods in formatted vacancy salary text.
- [x] Preserve structured-period precedence and leave unknown periods alone.
- [x] Verify focused salary/display tests (82) and isolated PostgreSQL (910).
- [ ] Review source-specific gross/net and currency-conversion evidence before
  allowing any cross-basis strict comparison.

## 2026-10-15 — application export audit trail

- [x] Include recorded, owner-scoped status events in explicit package export.
- [x] Cover ordered status text and handler lookup with regressions.
- [x] Focused suites: 35 passed; full isolated PostgreSQL: 905 passed.
- [ ] Continue exact package fidelity where provider-side attachment evidence
  can be recorded without implying a manual status is externally verified.

## 2026-10-15 — recruiter draft failure fallback

- [x] Convert recruiter LLM failure into a safe manual-response notification;
  don't log the raw exception payload.
- [x] Convert authorized auto-send transport failure into owner review with the
  draft retained; auto-reply remains OFF by default.
- [x] Verify both regressions; focused 9 and full isolated PostgreSQL 905 passed.
- [ ] Extend recruiter tracking beyond HH only with source permissions and
  owner-approved interaction boundaries.

## 2026-10-15 — legacy application migration verification

- [x] Add a real isolated PostgreSQL upgrade test from schema v4 through v5/v6
  using a preexisting submitted application.
- [x] Seed one initial event from its known status and original creation time;
  do not infer unrecorded status changes.
- [x] Verify new snapshot fields and history; full isolated suite: 903 passed.

## 2026-10-15 — disclose unknown salary-period behavior

- [x] Explain known-period-only strict comparison in `/salary`, `/settings`
  and the strict toggle confirmation.
- [x] Regression-test command text and strict filter behavior; focused 41,
  full isolated PostgreSQL 902 passed.

## 2026-10-15 — strict salary floor requires a known period

- [x] Stop assuming missing `salary_period` is monthly in the opt-in strict
  salary filter; keep unknown-period salaries reviewable.
- [x] Preserve explicit monthly/yearly behavior and add a regression for an
  adapter record without period evidence.
- [x] Focused salary/scoring suite: 66 passed; isolated PostgreSQL: 902 passed.
- [ ] Review provider-specific tax-basis/period evidence before adding more
  automatic conversions.

## 2026-10-15 — Interview Agent DNS/TLS/security coverage

- [x] Recognize DNS, TLS and explicit Security Operations requirements in
  Candidate/Vacancy fit without broadening to generic security wording.
- [x] Add exercises for DNS cache/TTL, certificate chain/SNI, and safe incident
  containment with evidence preservation.
- [x] Verify focused fit/scoring/interview tests (52) and full isolated suite
  (901 passed).
- [ ] Continue curated failure scenarios for Nginx, Docker, Kubernetes and CI;
  add interactive feedback only when evidence/retention are defined.

## 2026-10-15 — Interview Agent troubleshooting practice

- [x] Add `/interview <vacancy_id> [career|relocation]` based on recognized
  vacancy requirements and the selected profile's Candidate Fact comparison.
- [x] Curate reproducible Linux, Docker, Kubernetes, Nginx, Networking,
  PostgreSQL, CI/CD and Prometheus scenarios; put required topics first and
  display saved fact type without grading or prediction.
- [x] Verify focused suite (29) and full isolated PostgreSQL suite (900).
- [ ] Add interactive answer capture and evidence-grounded feedback only after
  defining private storage/retention and a useful scoring rubric.

## 2026-10-15 — resume snapshot and explicit package export

- [x] Add additive schema v6 fields for a local resume-text snapshot and
  external HH resume ID; populate for prepared and HH application records.
- [x] Add owner-scoped `/application <id> export`, bounded by the resume import
  size limit; include vacancy metadata, exact saved cover letter and snapshot.
- [x] Label pre-v6 records whose resume snapshot is unavailable and verify
  explicit export routing, user isolation and PostgreSQL persistence.
- [x] Focused tests: 44 passed; full isolated PostgreSQL suite: 896 passed.
- [ ] Original-format PDF/DOCX export and exact provider-side attachment
  evidence remain future scope.

## 2026-10-15 — append-only application status history

- [x] Add schema v5 application status events as an additive migration/table.
- [x] Append initial `prepared` status and each actual manual change; skip
  duplicate events for unchanged status.
- [x] Add owner-scoped `/application <id> history` and integration coverage for
  chronology, invalid/wrong-owner changes and hidden wrong-owner history.
- [x] Run focused 40 tests and full isolated PostgreSQL suite (892 passed).
- [x] Local text snapshot and user-triggered text export are implemented;
  original-format/provider-side attachment proof remains open.

## 2026-10-15 — persisted draft versions and manual application status

- [x] Persist each prepared cover-letter text with user, job, selected resume,
  source URL, timestamp and `prepared` status in the existing Application model.
- [x] Add user-scoped `/applications` and allowlisted manual status updates via
  `/application <id> <status>`; verify wrong-user and invalid-status rejection.
- [x] Update the match to `prepared`; preserve preview-only behavior with no
  submit, recruiter contact or schema migration.
- [x] Run PostgreSQL integration checks for record and status persistence;
  full isolated suite: 890 passed.
- [ ] Add exact resume-content snapshot/export and richer application history.

## 2026-10-15 — reviewed application package preview

- [x] Extend `/prepare` with Candidate Fact/CV skill consistency review beside
  the existing grounded cover-letter preview and selected resume.
- [x] Warn on CV-only terms and recognized requirements missing from both
  sources; validate vacancy links as credential-free HTTP(S) and bound message
  size. Keep preview manual; do not submit or create application status.
- [x] Verify focused tests (28) and isolated PostgreSQL suite (888); compileall,
  diff-check and secret scan passed.
- [x] Save the prepared cover-letter version and selected resume reference;
  separately tracked exact resume export/submission evidence remains planned.

## 2026-10-15 — read-only vacancy-to-resume diff

- [x] Add `/resumediff <vacancy_id> [resume_id]` for a selected saved resume;
  use only the authorized profile's active Candidate Facts and resume records.
- [x] Separate confirmed fact/CV overlap, facts missing from CV, CV-only terms,
  and gaps in both. Do not generate or alter resume claims.
- [x] Fix the confirmed unbound `issue` error paths in `/job`, `/compare` and
  compare callback with sanitized diagnostics.
- [x] Verify focused tests (47), full isolated PostgreSQL (884), compileall,
  diff-check and secret scan. Telegram live acceptance remains open.
- [x] Use this checklist in the `/prepare` review preview; live Telegram
  acceptance remains a separately recorded gate.

## 2026-10-15 — Candidate Fact traceability

- [x] Show matched skill references to the strongest Candidate Fact IDs and
  provenance labels in `/compare`; leave missing skills uncited.
- [x] Escape provenance output and point to `/facts` and `/fact` review/edit
  paths; keep scoring unchanged.
- [x] Verify focused comparison tests (23) and the isolated PostgreSQL suite
  (879); compileall, diff-check and secret scan passed.
- [ ] Continue truthful tailored-resume diffs and the first reviewed
  Application Package slice, with every statement grounded in Candidate Facts.

## 2026-10-15 — per-source Stretch yield

- [x] Include the existing `stretch` outcome count in each source's scan
  dashboard line beside Good; profile and overall totals remain unchanged.
- [x] Include existing filtered and duplicate counts, with source-summary
  regression coverage; do not change matching or deduplication behavior.
- [x] Run the full isolated PostgreSQL suite after the display changes.
- [ ] Continue toward broader source quality/freshness metrics only when the
  underlying observations are well-defined.

## 2026-10-15 — recoverable version snapshot

- [x] Verify feature branch HEAD `37633fc`, tracked upstream and dirty status.
- [x] Keep both proposal files untracked and refresh the exact handoff.
- [x] Create local and GitHub backup-branch copies of the verified snapshot;
  never point the backup at release/main or create a release/tag.

## 2026-10-15 — conservative multi-option skill alternatives

- [x] Recognize explicit two-or-more-option `or/или` chains, including
  Oxford-comma lists, in one required or preferred clause as a single choice.
- [x] Keep repeated skills and clauses with non-matching/ambiguous options
  ungrouped; comma-only skill lists and independent requirements remain separate.
- [x] Preserve existing score weights; regressions cover multi-option choices
  and comma-only requirements.
- [ ] Extend beyond isolated connector chains only with conservative grammar
  and scoring regressions.

## 2026-10-15 — salary setting clarity

- [x] State that salary minimum is a scoring reference, not a hard vacancy
  filter; document that only structured salary values are compared.
- [x] Update `/salary` and `/settings` labels and verify both with regression
  coverage; full isolated PostgreSQL suite passed (866 tests).
- [x] Keep strict filtering opt-in and default OFF; the owner requested the
  option while preserving scoring-only behavior for existing users.

## 2026-10-15 — CEFR requirement wording

- [x] Distinguish explicit required, preferred and unspecified language cues;
  contradictory or negated cues remain unspecified, with no scoring effect.
- [x] Add regression checks for English/Russian cues and comparison rendering.
- [x] Verify full isolated PostgreSQL suite (867 passed), compileall,
  diff-check and secret scan.
- [ ] Extend language vocabulary only with reviewed evidence mappings.

## 2026-10-15 — line-wrapped skill alternatives

- [x] Recognize an isolated required/preferred two-skill `or/или` choice when
  its explicit connector wraps to an adjacent line.
- [x] Keep independent skills separate and repeated/ambiguous skills ungrouped;
  focused 43 and full isolated PostgreSQL 869 passed.
- [ ] Extend to nested/multi-line clauses only with conservative grammar and
  score regressions.

## 2026-10-15 — salary evidence and strict floor

- [x] Add an OFF-by-default strict filter that excludes only comparable
  structured values proven below the monthly floor; retain unknown evidence.
- [x] Add /salary strict on|off across active Career-first/Relocation-first
  searches and cover same-currency, annual, ranged, missing and unsupported data.
- [x] Verify full isolated PostgreSQL suite: 873 passed; compileall,
  diff-check and secret scan passed.
- [ ] Review salary tax-basis and provider normalization evidence before
  broadening strict comparisons.

## 2026-10-14 — explicit language and mobility evidence

- [x] Extract only explicit English CEFR levels near English/«английский»;
  leave fluent wording, ranges and unsupported profile formats unknown.
- [x] Compare vacancy CEFR with the selected candidate profile separately from
  technical score; add `/english [A1-C2|unknown]` and persist the value.
- [x] Stop creating generic profiles with an invented B2. Fresh bootstrap uses
  tracked general English B1; existing profiles remain untouched and editable.
- [x] Show foreign-vacancy visa sponsorship, relocation, work-permit assistance
  and pre-existing work-authorization evidence separately; missing stays unknown.
- [ ] Expand language evidence beyond explicit CEFR only after defining
  reviewable mappings; do not infer legal eligibility from vacancy support.


## 2026-10-14 — measured model routing and fit follow-up

- [x] Verify current Main turn from the session log: `gpt-6-sol/medium`, matching
  the user config; align AGENTS without changing any model.
- [x] Invoke one read-only `job_scout`; verify its actual turn was
  `gpt-6-luna/low` and review its conclusion against installed HTTPX behavior.
- [x] Record Scout context cost (83,803 total input/output tokens, including
  56,576 cached input); use self-contained `fork_turns="none"` for future
  narrow tasks when delegation is justified. No measured savings claim.
- [x] Reproduce and fix an explicit required alternative followed by another
  sentence on one line; keep an independently repeated requirement separate.
- [x] Prevent a preferred alternative from spanning a skill promoted to an
  independently required skill; compare each pair against final importance.
- [ ] Measure a comparable narrow Scout task with isolated context before
  claiming reduced total token use. Deep remains reserved for hard cases.


## 2026-10-14 — isolated DB and narrow alternative requirements

- [x] Run full unit and isolated PostgreSQL suites against the `job-agent-tests`
  tmpfs database on port 55432; no production DB or runtime modification.
- [x] Count an explicit, isolated two-skill `or/или` choice in required or
  preferred sections once using strongest confirmed Candidate Fact; retain
  separate skill evidence and explain alternative scoring in the comparison view.
- [ ] Extend to complex/nested alternatives only with a reviewable requirement
  model; keep independent requirements and ambiguous prose conservative.
- [ ] Review and checkpoint the existing large dirty tree when Git metadata is
  writable; exclude both untracked owner proposal files.

## 2026-10-14 — independent follow-up increments

- [x] Bound dense source HTML views without splitting entities; preserve the
  complete ledger in state and send distinct new errors separately.
- [x] Make explicit adapter schema/HTML/RSS contract failures typed response
  diagnostics; preserve existing partial Himalayas/SmartRecruiters outcomes.
- [x] Retain verified Job Bank jobs after HTTP/schema detail errors, continue
  independent queries, stop source requests on 403/429; keep bounded pacing.
- [x] Carry partial metadata through all source-cache hits; separate cached
  collection observations from independent profile processing attempts.
- [x] Count actual HH/EURES/Job Bank/Arbeitnow/SmartRecruiters transport retries.
- [x] Scan staged/worktree/history for high-risk secret patterns, paths only;
  sanitize progress logs and historical failed scan stage display.
- [x] Verify Candidate Fact transaction cases within the full isolated
  PostgreSQL suite (855 passed); local checkpoint remains pending.
- [x] Reproduce flattened adjacent requirement headings misclassifying optional
  skills as required; split only at explicit headings, then verify comparison
  and existing 85/15 technical weighting in English and Russian.
- [x] Keep an explicit `with Python among the language alternatives` example
  as unknown evidence rather than a separate mandatory skill; preserve an
  independently stated Python must-have and verify score impact.
- [ ] Model general alternative requirement groups beyond isolated two-skill
  `or/или` lines, including nested and multi-line clauses, conservatively.


- [x] Separate attempted HH failures from later unattempted cooldown skips;
  preserve recovery history and partial status without repeated outage alerts.

## 2026-10-14 — source failure root cause and diagnostics

- [x] Reproduce legacy `found` failure after error→success; preserve all four
  multi-profile outcome orders plus repeated cache and EURES observation dedupe.
- [x] Add stable source counters, status, history and controlled diagnostic codes.
- [x] Separate source/network/HTTP/response/processing/summary failures; preserve
  valid jobs after individual prefilter/processing errors.
- [x] Safe Russian plain-text alerts, one per distinct issue/profile group/pass;
  safe single-escaped HTML dashboards and incomplete manual scan status.
- [x] Explicit RemoteOK 30-second phase budgets and reject non-list JSON shape.
- [x] Persist latest scheduled source summary under a separate state key; show
  the latest finished scan without replacing active manual work.
- [ ] Owner supplies sanitized production traceback to confirm whether the
  actual HH/RemoteOK `found` alerts came from the reproduced legacy defect.
- [ ] Authorized runtime network diagnosis / Telegram acceptance / isolated DB.


## 2026-10-14 — network diagnostics follow-up

- [x] Classify typed transport causes without parsing/logging URL/error text.
- [x] Sanitize raw SSL/DNS failures in source summaries, logs and alerts.
- [x] Bounded static detail-URL review of EURES, Himalayas and SmartRecruiters;
  no listing-controlled internal/cross-host fetch was established.
- [ ] Observe typed HH categories in separately authorized runtime; IPv4/IPv6,
  proxy routing and HTTP blocking require actual safe runtime evidence.

## 2026-10-14 — Candidate Fact review and verification

- [x] Add explicit ADD/UPDATE/KEEP controls for import overlaps with KEEP default,
  final confirmation, stale-preview guard and preserved prior facts.
- [x] Verify replacement rollback, row locking and cross-profile rejection in
  the full isolated PostgreSQL suite; runtime review remains open.
- [ ] Check real Telegram conflict-review UX after authorized deployment.

## 2026-10-14 — source metrics and checkpoint blockers

- [x] Preserve processing-error counts when another search profile succeeds.
- [x] Count distinct cached EURES failures while deduplicating a reused discovery.
- [ ] Save the reviewed local checkpoint once `.git` is writable; `git add`
  currently fails creating `.git/index.lock` on a read-only filesystem.
- [ ] Re-run isolated PostgreSQL once localhost sockets/Docker access are allowed.

## 2026-10-14 — local checkpoint follow-up

- [x] Preserve import preview after a failed resume lookup, not only a save.
- [x] Restrict manual HH reply setup to the owner and clear non-owner stale state.
- [ ] Re-run isolated PostgreSQL checks when the execution environment permits
  Docker/localhost sockets; current failure is PermissionError before DB access.

## 2026-10-14 — exception log hygiene

- [x] Prevent Telegram startup network errors and HH chat polling errors from
  logging raw exception URLs/parameters; cover both with regressions.

## 2026-10-14 — dependency security

- [x] Raise pypdf/python-multipart lower bounds past checked upstream
  advisories; validate locally with patched pypdf.
- [ ] **P1, build reproducibility:** design a reviewed lock or constraints
  process with hash/upgrade checks for runtime and CI images before deployment.
- [ ] **P1, acceptance:** after authorized image rebuild, verify installed
  package versions in the separate runtime image and run its import smoke test.

## 2026-10-14 — EURES response isolation

- [x] Keep other EURES queries/details after one HTTP or parse failure; keep
  total failure visible and do not retry HTTP 4xx/5xx blindly.
- [x] Carry partial EURES query/detail failure counts through source cache,
  per-profile summaries, aggregation and `/scanstatus` without changing scores.

## 2026-10-14 — Job Bank detail efficiency

- [x] Measure repeated detail work from read-only runtime logs and cache
  recently verified Job Bank details with one-hour TTL, 256-entry cap and
  forced-refresh bypass; keep the five-second request pacing.
- [ ] **P1, acceptance:** after authorized deployment, compare Job Bank
  `/scanstatus` duration and eligible results across adjacent scheduled scans;
  verify a manual `/scan` still fetches current details.

## 2026-10-14 — Georgia source security

- [x] Reproduce and block listing-provided cross-host detail URLs for HR.ge
  and JOBS.GE. Keep relative same-host links working.
- [ ] **P1, source review:** verify remaining adapters' detail URL and redirect
  boundaries when adding any new collector; only fetch permitted source hosts.

## 2026-10-14 — resume import follow-up

- [x] Reproduce concurrent duplicate resume-confirmation writes and make the
  pending preview token one-time before database work.
- [x] Save an imported resume and proposed facts in one transaction; retain the
  preview after a persistence error and verify rollback plus retry on isolated
  PostgreSQL.
- [x] Implement per-conflict ADD/UPDATE/KEEP; preserve old rows and unknown
  replacement classification. Integration/runtime acceptance remains open.

## 2026-10-14 — reliability and security follow-up

- [x] Isolate scheduled scan failures per user, with a regression proving the
  next active user is scanned after an exception.
- [x] Restrict Telegram candidate commands/callbacks to private chats and the
  global HH applicant token to the configured owner profile; cover both gates.
- [x] Remove raw HTTP transport messages and HH API bodies from source alerts.
- [x] Preserve later vacancies from a successful source after one vacancy
  fails processing; record a partial source and error count.
- [ ] **P0, owner/runtime gate:** after explicit deployment authorization,
  verify private-chat commands and selected Bot API channel posts in the real
  runtime. Confirm a group cannot access candidate data or invoke a callback.
- [ ] **P1, security:** review legacy HH manual reply flow and any future
  per-user OAuth before enabling private actions for additional users.
- [ ] **P1, reliability:** measure HH ConnectError frequency in the authorized
  runtime; the current bounded cooldown isolates HH but does not repair an
  upstream DNS/TLS/proxy failure.

## Night development checkpoint — 2026-10-14

- [x] Reconcile canonical roadmap with current v3.5.7 code/tests and original
  v3.5.1–v4.x vision; keep proposed numbering separate from `VERSION`.
- [x] Isolate one subscriber's pause/profile/retry-state lookup failure in
  Channel Watcher so later subscribers still process; add four regressions.
- [ ] **P0, owner access and separate deployment approval:** choose actual
  channels, grant Bot API access, then check `/channels`, new post, replay,
  retry, and both profile results in the authorized runtime. No history or
  edited-post acceptance is implied by local tests.
- [ ] **P0, v3.5.7 exit:** review useful GE/AM and remote results in both scoped
  Telegram lists, verify current source restrictions and role/eligibility
  evidence, run CI/isolated PostgreSQL suite and record owner release decision.
- [ ] **P1, source coverage:** verify a permitted current Armenian employer
  feed or explicit lawful alternative before adding a collector; measure
  relevant vacancies, not HTTP success alone. Preserve lower-barrier
  Relocation-first discovery and the 65-point threshold.
- [ ] **P1, watcher follow-up:** design edited-post behavior and per-profile
  replay/history policy before implementation; Bot API access and source
  permissions are dependencies. No arbitrary history collection.
- [ ] **P2, source intelligence:** canonical cross-source references and source
  yield/health metrics after the v3.5.7 acceptance gate.

Older stage task lists below are retained as historical records; current
priority and dependencies are the list above and root `ROADMAP.md`.

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

## 2026-10-14 — Telegram watcher persistent retries

Failed deliveries persist in RuntimeState queue (max100 per user); retry job
every minute handles max5 posts, /channels retry scoped to invoking user. Off,
paused and source-disabled users stay protected. Existing queued entries never
evicted for overflow; overflow separately counted. Success/seen replay clears
queue; failures rotate; malformed entries preserved/logged. Real PostgreSQL
integration now verifies queue recovery after reload, real dual-profile matching
and replay suppression. Latest716unit/4skipped,720PostgreSQL; safety checks pass.
Stage1 a6d67fa and stage2 3dffc39 complete; current stage local/undeployed.
No schema/score change. Next separate Docker check then owner-approved runtime
and real selected-channel acceptance; edits/history are not claimed.

## Telegram watcher stage 2 — 2026-10-14

Labeled role/company/location/work-mode fields now parse conservatively; generic
headers/hashtags no longer hide the role. Narrative office mentions do not assign
country; ambiguous multi-country and Georgia/USA locations stay unknown.
Forwarded channel posts/captions preserve original public URL and numeric source
identity, sharing a serialized durable replay guard with automatic delivery.
Private/hidden forwards get no invented public link. No schema/score change.
Targeted51/1skipped; full unit710/4skipped, PostgreSQL714; safety checks passed.
Stage1 a6d67fa complete; next bounded persistent failed-post retry queue.
Production unchanged; Bot API access/history limitations still apply.

## Telegram watcher stage 1 — 2026-10-14

Implemented /channels subscriptions (add/on/off/remove, career/relocation/both),
Bot API post/caption routing for selected users only, persistent statistics and
SeenMessage replay suppression. Both profiles use existing scoring/persistence;
pause/source-disable respected. Alias subscriptions union scopes. No migration,
production change, account login/history scraping or external application.
Unit698/4skipped, PostgreSQL702; watcher targeted23 including real PostgreSQL
reload and dual-profile matches. Compileall/secret/diff passed. Help entry added;
see developer/TELEGRAM_WATCH for access/transaction/retry limitations.
Next safe stage: labeled role/company/location parsing and forwarded-channel
provenance; then edited-post/retry handling. Deployment approval remains separate.

## Next priority correction — Telegram vacancy channels

Owner explicitly restored Telegram channel discovery as a priority. Current
implementation accepts channel_post updates and user-forwarded posts only;
there is no configured channel watchlist or arbitrary-channel history/search
collector. A registry label is not proof of automatic coverage. Existing
Telegram evidence-parser fixes are completed; do not repeat them. Next stage:
identify owner-selected remote/DevOps and AM/GE channels, distinguish actual
Bot API access from manual-forward destinations, implement truthful configuration
and visibility with regressions. Requested @names/links or permission to curate
a list; response pending. No user-account login/MTProto collection authorized.
Keep deployment gate separate; Telegram discovery task is independent.

Verified implementation06fe88c; separate Docker imagea80ee8bdf948 built,
Python3.12 compile/import/evidence smoke passed without networking. Latest676
unit/679PostgreSQL and safety checks passed. Owner deployment approval requested
for06fe88c, answer pending. Earlier11c07cc request is superseded; no runtime
update or publication performed. Actual following HEAD is docs-only.

## 2026-10-14 — Direct employer visa predicates

Shared evidence now handles employer sponsor-visa verb phrases, including
plural, can/will and explicit refusal. Conditional/advice/non-employer claims
remain unknown. Refusal wins over offers in either order, also in Telegram.
84 targeted tests; full unit676/3 skipped, PostgreSQL679; compileall/secret/diff
passed. No formulas, thresholds, migration or deployment. Prior stage02635d7
complete. Compact BRIEF/HANDOFF now replaces duplicate current snapshots;
original text remains Git history/DEVELOPMENT_LOG. Next mandatory gate: approved
runtime/Telegram acceptance; independent AM feed discovery stays open.


## Latest stage — 2026-10-14: Greenhouse evidence

Greenhouse uses shared tri-state support classification, so advice, conditional
support and prerequisites no longer become employer sponsorship offers.
Existing source snippets are retained only when consistent with the classified
value. Hybrid wins over mixed hybrid/remote labels; explicit remote locations
are preserved as bounded remote_scope. No new filters, weights or thresholds.
Validated 665 unit / 3 skipped, PostgreSQL 668, compileall/secret/diff passed.
Local implementation follows e4644b3; no deployment/publication. Next safe task:
shared explicit sponsor-visa verb phrases and refusal precedence. Mandatory
v3.5.7 runtime/Telegram acceptance remains pending; see HANDOFF.


Candidate 11c07cc also passed a separate Docker build (image8fc8cddae7d6)
and Python3.12 import/compile/evidence smoke in a network-disabled ephemeral
container. Repo runtime/volumes unchanged. Owner update approval requested for
11c07cc; unanswered at this checkpoint. Any following checkpoint is docs-only.

## Current checkpoint — 2026-10-14

Source 3.5.7, feature/v3.5.7-international-market-coverage. Previous six stages
remain complete. New stages: af1ff56 (source salary display and remote limit
precedence), 76b5661 (Telegram unknown/negative support and explicit salary
units), then malformed numeric salary bounds (obtain final HEAD from Git).
Latest complete candidate: 658 unit passed / 3 skipped, isolated PostgreSQL
661 passed; compileall, secret scan and git diff --check passed.
No scoring formula/weight/65-threshold changes or schema migrations.

See BRIEF/HANDOFF for implementation limits and pending deployment/acceptance.
Next: approved runtime validation; independent Armenian employer-feed research
remains open. Historical counts below belong to their recorded stages.

## v3.5.6 candidate maintenance — EURES and target markets
- [x] Reproduce EURES TLS body-read failure with default compressed encoding
  inside the running container; verify that identity encoding reads the full
  50-result JSON response.
- [x] Add `Accept-Encoding: identity` to EURES and cover it with a regression
  test.
- [x] Make `/targets` apply countries to all active search profiles by default;
  support explicit `career` and `relocation` scopes.
- [x] Make `/sources` list each active profile's configured source plan.
- [x] Replace the mixed-language root README with linked English and Russian
  versions; align changelog headings and refresh the roadmap/source review.
- [x] Full isolated PostgreSQL suite: 224 passed; branch coverage 66.33%.
- [x] Push `6fa3406` to GitHub branch
  `feature/v3.5.6-eures-identity-market-targets` and pass GitHub CI.
- [x] Publish follow-up handoff commit `e43072c`; push and PR CI passed.
- [x] Apply the candidate through `JOB_AGENT_COMPOSE_PROJECT=repo ./job-agent
  update`; verify polling, healthy PostgreSQL, and unchanged
  `repo_jobagent_v3_pg` / `repo_jobagent_v3_files` volumes.
- [x] Verify the first post-update startup scan completed successfully; EURES
  search and detail requests returned HTTP 200 with no SSL retry/error.
- [x] Review Georgia robots endpoints: JOBS.GE returns 410 (no rules); HR.ge
  allows `/` and publishes a sitemap. Do not treat robots guidance as reuse
  permission; no explicit recurring-extraction permission was verified.
- [x] Bound JOBS.GE/HR.ge to six details per source, 15-second request timeout,
  and two-second pacing; preserve partial results and report total detail
  failure. Tighten role matching and require explicit currency plus a monthly
  period before HR.ge salary is structured for scoring. Cache scheduled
  Georgia results for six hours; manual `/scan` remains a force refresh.
- [x] Add Georgia source regressions and run the full isolated PostgreSQL suite:
  230 passed, 67.46% branch coverage; compileall and diff check passed.
- [x] Push commits `2963705` and `0110173` to PR #16; latest push CI
  `38127150025` and PR CI `38127152783` passed. Apply with the safe updater
  and verify the completed startup scan, EURES HTTP 200 responses, healthy
  PostgreSQL, and attached existing volumes.
- [x] Owner ran `/targets relocation GE`, `/sources`, and `/scan`; EURES found
  16 vacancies, HR.ge found 2, JOBS.GE returned HTTP 410, and Arbeitnow had a
  transient `ReadTimeout`.
- [x] Pause JOBS.GE in the source plan after its configured homepage returned
  HTTP 410; keep it visible in `/sources` with the reason.
- [x] Add one retry for Arbeitnow transport failures and cap its request timeout
  at 15 seconds; do not retry HTTP status responses.
- [x] Full isolated PostgreSQL suite after the source changes: 233 passed,
  67.67% branch coverage; `compileall` and `git diff --check` passed.
- [x] Publish `170ed4e` to PR #16; push CI `38129138392` and PR CI
  `38129141546` passed.
- [x] Clarify in the English/Russian README and changelog that `main` source
  version v3.5.6 and cumulative changelog milestones are distinct from formal
  releases; publish one cumulative v3.5.6 release after acceptance.
- [x] Push current branch handoff and README clarification in PR #16; latest
  push CI `38129983586` passed.
- [x] Merge PR #16 into `main` after candidate CI and owner source/scan checks;
  merge commit `874b372`, PR push/PR CI `38135381779` / `38135384930`, and main
  CI `38135649948` passed. `README.md` and `README.ru.md` are now both on main.
- [x] Apply through the safe updater; verify runtime 3.5.6, active app,
  healthy PostgreSQL, completed startup scan, and attached existing named
  PostgreSQL/storage volumes. Logs show Arbeitnow, EURES, and HR.ge HTTP 200s;
  JOBS.GE was not requested and no source error appeared.
- [x] Owner supplied a post-deploy Telegram scan log: Arbeitnow's single retry
  recovered from `ReadTimeout` with HTTP 200; EURES, HR.ge, Job Bank, and HH
  requests in the excerpt succeeded; JOBS.GE was not requested. Telegram
  handled the update in 162.7 seconds.
- [x] Owner confirmed `/sources` visibly marks JOBS.GE paused and shared
  `/scanstatus`: completed GE scan returned HH 209, Remote OK 3, Arbeitnow 2,
  Job Bank 12, EURES 16, and HR.ge 2. Timings: HH 7.6s, Remote OK 1.5s,
  Arbeitnow 17.1s, Job Bank 99.5s, EURES 14.5s, HR.ge 13.0s. Keep Job Bank's
  five-second request interval while evaluating latency.
- [x] Owner completed Telegram acceptance: unsupported ZIP rejected, duplicate
  resumes detected, TXT resume #6 saved after confirmation with zero facts
  proposed, and `/job 580` displayed Recommendation v2 with unsupported
  dimensions unknown.
- [x] Prepare one cumulative v3.5.6 release; keep v3.5.2–v3.5.5 as untagged
  milestones included in it rather than creating retroactive tags.
- [x] Push annotated tag `v3.5.6` on CI-verified commit `50afdab` and publish
  the bilingual GitHub Release after CI run `38138941745` passed.
- [ ] Monitor later scheduled EURES scans; the first clean run does not prove
  the underlying TLS cause is permanently resolved.
- [x] Change Job Bank pacing to enforce at least five seconds between request
  starts, without an extra wait when a slow response already consumes the
  interval. Requests remain serialized. Regression tests verify both fast and
  slow responses and concurrent callers.
- [x] Owner compared a post-update Telegram `/scan` and `/scanstatus` at
  20:42–20:44 Moscow: Job Bank returned 12 results in 71.2s, down from 100.7s
  in the earlier check; EURES returned 16 in 34.1s. The supplied scan log has
  no source failure. The retry/partial-recovery path remains verified by tests,
  since this live scan had no transport failure.

## v3.5.7 International Market Coverage — active candidate
- [x] Save owner-requested shutdown checkpoint (2026-10-13 08:28 Moscow):
  clean Git at bacdcc7 before docs update, tested implementation 443aaeb,
  no unfinished code edits, runtime still c829a5f/app up/PostgreSQL healthy.
  Preserve prior test evidence; no new long operations, deployment or data
  changes. HANDOFF contains exact reboot/continuation and approval gate.
- [x] Make explicit Georgian/Armenian role/resume text tokenization Unicode
  aware in Georgia discovery/matching. Preserve generic exclusions, technical
  punctuation, weights/caps/threshold and supplied preferences; no translation
  aliases invented. Targeted 48 passed; full unit 606 / 3 skipped, PostgreSQL 609;
  compileall/secret/diff pass. Separate Docker/Python 3.12 validation passed.
  Working runtime remains c829a5f pending owner deployment agreement.
- [ ] Owner authorizes working-runtime implementation 443aaeb update (question
  sent, answer pending), then real Telegram/new source/scoped relocation
  acceptance; keep separate from unit tests.
  Latest old-runtime logs reproduced the already-fixed HH aggregate KeyError
  at 05:08:33 UTC on Oct 13. This strengthens the update priority; agreement
  is still required by the owner's explicit deployment instruction.
- [x] Recognize exact public Devexperts `What we expect from candidates`
  required and `As a Plus` preferred section headings. Negative near-match,
  HTML/inline, and optional-coverage regressions pass; vocabulary, weights
  and thresholds unchanged. Targeted 80; unit 585 / 3 skipped, PostgreSQL 588;
  safety checks passed. Alternative-language groups remain a v3.6 limitation.
- [x] Connect curated public SmartRecruiters/Devexperts feed for selected GE
  only, respecting independent role queries/source toggles. Bound page/details,
  transport retry/time budgets/cache; preserve verified partial results, and
  keep hybrid/GE-only remote scope and support unknowns truthful. Read-only
  live adapter probe found one relevant GE/hybrid support lead. Targeted 59,
  full shared unit 585 / 3 skipped, PostgreSQL 588; safety checks pass. Not deployed.
- [x] Plan bounded Himalayas queries so selected support roles no longer
  disappear behind the first four physical-work queries. Keep supplied query
  text, within-group order, max four, market/cache bounds, full parse-time role
  matching and owner preferences/scores. Regression covers customer support
  for both GE/AM. Targeted 73 passed; shared worktree unit 568 / 3 skipped,
  PostgreSQL 571 passed; compileall/secret/diff pass. Not deployed.
- [x] Preserve Himalayas `expiryDate` as source listing-expiry evidence in
  existing source-ref JSON and display UTC expiry/expired/unknown on /job.
  Reassess cached dates at render time; future expiry never confirms employer
  hiring or an application deadline. No migration/score/filter change.
  Targeted suite 76 passed; shared candidate unit 563 passed / 3 skipped,
  PostgreSQL 566 passed; compileall/secret/diff pass. Not deployed.
- [x] Complete the HH cooldown follow-up: accurate quiet skipped/partial
  /scan and persisted /scanstatus, shared serialized probes, HH cache
  invalidation on ConnectError, and aggregate recovery retaining successful
  counts. Targeted tests 49 passed; full shared-candidate suite 486 passed /
  3 skipped; isolated PostgreSQL 489 passed; compileall/secret/diff checks pass.
  Runtime remains c829a5f (healthy; startup completed 21:53:38 UTC), without
  the follow-up. Do not deploy without owner approval.
- [x] On HH public `ConnectError`, skip without Telegram notification and
  continue other sources. Suppress duplicate attempts across search profiles
  for 15 minutes, then probe HH again on a later scan. Non-HH source errors
  retain existing alerts. Regression test covers silent skip, profile cooldown,
  and retry after expiry. Targeted tests: 18 passed; unit suite: 444 passed,
  3 skipped; isolated PostgreSQL suite: 447 passed; compileall, secret scan
  and diff check pass. Compose `repo` rebuilt at 00:52 Moscow; runtime 3.5.7
  was up and PostgreSQL healthy. Commit c829a5f startup scan completed
  at 21:53:38 UTC and reproduced one locally logged HH connection failure;
  other sources continued. Silent failure handling also has regression tests.
- [x] Add jobs.ss.ge as a selected-Georgia manual-search destination after
  confirming that it exposes broad vacancy listings but no verified reusable
  public API or automated-collection permission. Keep it link-only. Targeted
  source tests: 5 passed; full suite: 443 passed, 3 skipped; isolated
  PostgreSQL suite: 446 passed; compileall, secret scan and diff check passed.
  Compose was rebuilt at 00:47 Moscow; owner `/sources`
  rendering confirmation remains pending.
- [x] Skip HH immediately on public-search `httpx.ConnectError`; let source
  isolation finish other feeds. Keep the single retry for other transient
  transport errors. Targeted tests: 15 passed; full suite: 443 passed, 3
  skipped; isolated PostgreSQL suite: 446 passed; compileall, secret scan and
  diff check passed. Commit `5a815b5` rebuilt Compose `repo` at 00:43 Moscow;
  startup scan completed at 21:44:48 UTC with PostgreSQL healthy. Runtime logs
  show HH skipped on `ConnectError` while Himalayas, Remote OK, Arbeitnow,
  Job Bank, EURES, Greenhouse, Lever and HR.ge continued successfully.
- [x] Add one bounded retry for transient transport failures in the public HH
  API and web-search requests. This directly addresses the observed TLS
  `ConnectError`; it does not assume Yandex is the cause. Do not retry HTTP
  errors/CAPTCHA or change private applicant endpoints. Targeted HH tests: 13
  passed; full local suite: 441 passed, 3 skipped; isolated PostgreSQL: 444
  passed; compileall, secret scan and diff check passed.
- [x] Commit as `b427e96` and rebuild Compose `repo` without changing named
  volumes. Source/runtime report 3.5.7 and PostgreSQL is healthy. Startup scan
  completed at 00:25 Moscow; HH API 403 fell back to public search, where a
  TLS `ConnectError` triggered the new single retry. Later public HH requests
  returned HTTP 200 and `scan_all` completed successfully. No causal claim is
  made about Yandex infrastructure.
- [x] Recognize common remote-board requirement headings (`What we are
  looking for`, `What you'll bring`, `Nice-to-have skills`) so existing
  technical requirement coverage is not left unknown; label interview-risk
  as the technical-risk index (`100 − requirement coverage`) and leave
  nontechnical conditions unscored. Targeted suite: 37 passed; full isolated
  PostgreSQL suite: 442 passed; compileall, secret scan and diff check passed.
  Risk formula commit `a3a2494` and curly-apostrophe test commit `e382ddb` are
  applied in Compose 3.5.7; startup scan completed after an isolated source
  error. Telegram `/job 1273` confirmation remains open.
- [x] Keep the candidate's current self-assessed general English at B1 and
  retain B2 only as a technical-reading estimate in the fresh-profile defaults.
  Add regression coverage; do not overwrite facts on existing profiles.
- [x] Check the official Emerging Travel Group Junior DevOps listing and
  Workable's documented public jobs endpoint. The role currently names AM/GE,
  remote, 1.5+ years commercial DevOps, six months Kubernetes, and English
  B1+; endpoint returned 403. Add the employer's official posting as a
  link-only manual source and do not scrape or infer legal eligibility.
- [x] Commit the English distinction and ETG manual lead as `8ca977f` and
  `432d44c`; synchronize PROJECT_OS and private context to current Git state.
- [ ] After rebuild, owner verifies `/sources`, `/jobs relocation`, and
  `/jobs relocation below`; the supplied 21:13 Telegram lists predate the
  21:26 rebuild of the domestic-onsite filter.
- [x] Align the AI job-bot's bootstrap profile with the owner's current
  equal-priority GE/AM plan and add bounded lower-barrier Relocation-first
  role queries. Existing persisted user settings remain unchanged; add a
  configuration regression.
- [x] Audit bounded employer support evidence across preferences,
  recommendations, and source adapters. Preserve unknown values, distinguish
  separate support components, and prevent role requirements or guidance from
  being reported as offers.
- [x] Compare annual salary amounts with monthly profile minimums without
  changing source amount/period; display known annual/monthly/hourly/weekly
  periods. Hourly/weekly comparisons stay unknown without contracted hours.
- [x] Reset stale scan dashboard fields when a new manual scan begins and
  isolate independent source failures while retaining successful discoveries.
- [x] Preserve the original persisted Remotive response age across restarts and
  forced scans; show Himalayas timezone bounds as provider claims in details.
- [x] Resumed full validation: 424 local passed / 3 skipped; isolated
  PostgreSQL suite 427 passed, 73.22% branch coverage; compileall and
  `git diff --check` passed.
- [x] Publish the cumulative candidate as `8da96f8` on PR #18's existing
  feature branch; push CI `38280187127` and PR CI `38280191809` passed. Safely
  update/start Compose `repo`, verify source/runtime 3.5.7, healthy PostgreSQL,
  and the unchanged named PostgreSQL/storage volumes.
- [x] Diagnose the startup scan's EURES database failure: fixed-width source
  whitespace made `cityName` exceed the 256-character city column. Normalize
  whitespace; preserve genuinely overlong source text as raw evidence and
  keep city unknown. Full isolated PostgreSQL suite: 429 passed, 73.24% branch
  coverage; targeted EURES suite: 13 passed; compile and diff checks passed.
- [x] Publish EURES follow-up `159d510` to PR #18; push CI `38281187340` and
  PR CI `38281192380` passed. Safely update Compose `repo`, verify healthy
  runtime 3.5.7 and unchanged named volumes. The fresh startup scan completed
  at 17:04:14 UTC after EURES HTTP 200 responses with no database/source error,
  traceback, or repeated city-width insertion failure in the log window.
- [x] Add profile-specific `/jobs career|relocation [below]` lists using each
  enabled profile's own threshold; retain independent scores through detail
  and comparison buttons and explicit `/job`/`/compare` scope arguments.
- [x] Correct ordinary `hotel staff`/`warehouse staff` being classified as
  engineering Staff/Senior. Keep technical Staff, seniority, high-experience,
  management and user exclusions covered by regressions.
- [x] Verify selected-score isolation, user ownership, legacy callbacks and
  below-threshold scope. Full local suite: 319 passed, 3 skipped; all 3 isolated
  PostgreSQL repository tests passed; compilation and diff checks passed.
- [x] Add an at-a-glance roadmap showing completed, current and later stages;
  maintain the private relocation roadmap separately with current official
  legal references and progress.
- [ ] Verify the new scoped commands/cards in Telegram after local rebuild.
- [x] Evaluate bounded HH search for selected destinations. Verify HH's public
  `/areas` catalog: Russia is area `113`, Georgia is area `28`, and Armenia is
  not present. Search each represented current/target
  market independently, deduplicate results, and attribute country only from
  the scoped area query; do not guess an Armenia area. Local suite: 430 passed,
  3 skipped; isolated PostgreSQL suite: 433 passed; compileall, secret scan,
  and diff checks passed. This source change is committed locally as `552cb72`;
  Telegram/runtime acceptance remains pending.
- [x] Add the Himalayas documented public search API as a bounded remote
  source: up to four active-profile queries, three selected markets and one
  page of 20 jobs per query/market; cache for 24 hours and show source links
  and salary periods in Telegram.
- [x] Preserve provider country restrictions; missing restrictions remain
  unknown and no individual visa/work/payroll eligibility is inferred. Stop
  treating RemoteOK's unspecified hiring geography as worldwide.
- [x] Add regressions for country scope, unknown eligibility, salary periods,
  attribution, bounded requests, partial failures and cache isolation. Targeted
  suite: 41 passed.
- [x] Full local suite: 266 passed, 3 database tests skipped; isolated
  PostgreSQL suite: 269 passed; branch coverage 69.70% against the 55% gate.
  `compileall` and `git diff --check` passed.
- [x] Rebuild Compose project `repo`; app and PostgreSQL healthy, original
  named volumes `repo_jobagent_v3_pg` and `repo_jobagent_v3_files` remain
  attached. Startup scan completed at 17:35:32 UTC. Himalayas requests for GE
  and AM returned HTTP 200; the inspected log window showed no source errors.
  HH API returned 403 and public web fallback succeeded.
- [x] Owner verified `/sources`, `/scan`, `/scanstatus`, and `/jobs`: Himalayas
  returned 20 cached roles and appeared first with source links; Career-first
  processed 191 jobs and Relocation-first 67. Job Bank returned 12 in 71.2s,
  EURES 16 in 34.1s. Supplied log excerpt shows no source exception or SSL
  failure; HH API 403 recovered through the public-web fallback.
- [x] Owner verified Telegram `/job 1273` at 20:56 Moscow time: the card shows
  Himalayas' worldwide scope and explicitly says the employer must confirm
  hiring from the user's country. The listing had no salary. Logs show the
  Telegram update handled in 567ms without an error.
- [x] Add a curated Collectly Lever Postings API source for selected AM/GE
  profiles. Keep the Belgrade/RS source location separate from remote-country
  eligibility; require a remote workplace and a public timezone range covering
  UTC+4; preserve unknown country, visa, and relocation facts. Do not submit
  applications.
- [x] Add Lever regressions for role, remote mode, timezone scope, selected
  markets, salary metadata, attribution URL, malformed payloads, and source
  registration and safe timezone text in vacancy details. Full local suite:
  274 passed, 3 database tests skipped;
  `compileall` and `git diff --check` passed.
- [x] Rebuild local Compose `repo`; verify PostgreSQL healthy and startup
  `scan_all` completed at 18:06:21 UTC. Lever returned HTTP 200 for both
  profiles; inspected scan logs contain no source exception.
- [x] Owner verified `/sources` lists Lever for both profiles and ran
  `/scan`/`/scanstatus`: 1 live Lever vacancy in 9.6s; complete scan in 131s,
  266 processed, 37 Good, 33 Stretch, 196 filtered, 0 new notifications.
  Job Bank returned 12 in 71.4s; EURES 16 in 55.2s; no source error appeared
  in the supplied log excerpt.
- [x] Inspect the saved Collectly Lever match after `/jobs` omitted it. Read-only
  runtime query found job #1333 saved as `filtered`, score 0, because the
  Career-first profile explicitly excludes `senior devops`; this is expected
  filtering, not a source failure. The detail renderer's timezone/country
  caveat has regression coverage. Keep the explicit filter unless the owner
  chooses to change it.
- [x] Add an explicit remote-work processing preference to both independent
  profiles. It orders remote vacancies earlier within each source result batch,
  preserves each profile's role queries, leaves Match Score and notification
  thresholds untouched, and does not treat unknown remote scope as worldwide
  eligibility.
- [x] Add regressions for remote/onsite ordering across strategies, unknown
  scope, and negated remote labels. Full isolated PostgreSQL suite: 257 passed,
  68.59% branch coverage; local suite: 254 passed, 3 database-dependent tests
  skipped; compileall and `git diff --check` passed.
- [x] Verify remote work is surfaced to the owner after the candidate update:
  Telegram `/review` and `/stretch` showed remote CloudCops 88/Good and Sporty
  Group 72/Stretch. Regressions verify source-batch processing priority across
  strategies; source geography remains qualified and unknown eligibility is
  not inferred.
- [x] Keep vacancy priority aligned with match rating: `/review`, `/stretch`,
  and `/saved` already sort highest score first; `/jobs` now does the same and
  uses recency only to break ties. The owner confirmed that higher-rated jobs
  should always have higher priority. Keep the notification threshold at 65;
  do not promote lower-rated results ahead of higher-rated ones.
- [x] Add Remotive's official remote DevOps/Sysadmin feed with a single shared
  daily response cache in existing PostgreSQL runtime state. Link each listing
  to Remotive and show its name; retain explicit location scope, reject clear
  country-only mismatches, and leave free-text salary unstructured. Verify
  profile sharing, restart persistence, source attribution, parser behavior,
  and no application capability.
- [x] Owner confirmed `/sources` lists Remotive and `/scan` completes; record
  the actual count rather than treating HTTP 200 as usable results. The first
  scan returned 0 because category query parameters returned a general feed.
  The worktree now uses Remotive's official Devops RSS feed and bumps the cache
  key to v3. Targeted and full unit tests pass; rebuild returned a valid RSS
  response with zero items. Recheck after the cache expires and confirm `/jobs`
  attribution if the feed returns a match.
- [x] Add `/jobs below` as a manual-review view of nonzero scores below the
  configured threshold. Keep descending order; exclude duplicate and zero-score
  results; state that legal work and relocation eligibility require separate
  confirmation. Do not change Match Score or notification behavior.
- [x] Give the immediate startup `scan_all` job a five-minute scheduler
  misfire grace. A local restart showed the old one-second default could skip
  the first scan after a brief startup delay; regression test covers the job
  registration, and the rebuilt app started the scan immediately.
- [ ] Improve practical Relocation-first results while preserving the 65-point
  threshold, descending score order, independent search direction, and
  evidence-based visa/work eligibility. Current scans can complete with 0
  Good/Stretch; investigate relevance and source coverage without inflating
  scores or changing owner exclusions.
- [x] Review JOBS.GE and HR.ge robots guidance and add conservative request
  bounds. Terms/reuse permission remains unverified; owner must inspect scan
  quality before treating the sources as useful.
- [x] Review the official Armenian jobseeker registration guidance. Its PSN,
  national eID, and residence-card requirements describe registration with the
  state service; they do not establish a general ban on direct employer
  applications.
- [x] Check current official Armenian source candidates: the Unified Social
  Service lists e-work.am and workforall.am; both public search pages timed out,
  and no API/access terms were found. Online e-work registration requires PSN
  or national eID; the in-person foreign-citizen path requires a residence card.
- [x] Review the official `workpermit.am` employer-side foreign-hiring flow and
  EAEU exemption. Its FAQ lists a job-finding question, but the answer is not
  rendered; the official guide documents an employer-created vacancy and
  employer entry of the selected foreign worker. The lawful-residence
  certificate is separate and requires a Public Services Number to print. No
  anonymous job feed is verified.
- [x] Recheck the current Georgian Labour Migration Law: the new right-to-work
  process for covered foreign workers is in force from 2026-03-01.
- [x] Review current Staff.am and Job.am terms. Keep them as manual search
  destinations; do not automate collection or reuse without a permitted feed
  or written permission.
- [x] Defer cold outreach to the Unified Social Service and Migration Service:
  it is not a prerequisite for this release, and no documented public feed or
  API has been identified.
- [x] Add Armenia (`AM`) to the supported country catalog without implying a
  government-board integration or individual eligibility determination.
- [x] Connect Greenhouse's public Job Board GET API for the Lineate board when
  AM or GE is selected. Match active role queries and explicit locations;
  leave visa/relocation support unknown without direct posting evidence.
- [x] Add Greenhouse regressions for selected-country scoping, role matching,
  explicit support evidence and API contract errors. Targeted source/country/
  preference tests: 20 passed.
- [ ] Evaluate permitted employer career/ATS feeds, documented public APIs,
  and owner-selected Telegram channels for Armenia/Georgia. Verify role
  relevance, location, language, expiry, access conditions, and eligibility
  evidence before integration.
- [x] Confirm owner-visible `/sources`, `/jobs`, `/jobs relocation`, and
  `/jobs relocation below` rendering in Telegram. The output exposed Russian
  onsite jobs in the relocation lane; suppress same-current-country onsite
  jobs for Relocation-first unless domestic relocation is explicitly enabled.
  Keep explicit remote and unknown-country jobs; preserve Career-first and
  score semantics. Targeted tests 49 passed; full local suite 437 passed / 3
  skipped; isolated PostgreSQL 440 passed; compileall, secret scan and diff
  check passed. Rebuilt Compose 3.5.7; startup scan completed at 18:26:17 UTC,
  PostgreSQL healthy. One HeadHunter web request logged transient ConnectError.
  Owner confirmation of the filtered output remains open.
- [x] Add verified Armenia/Georgia manual-search links to `/sources` for ITA
  Jobs, Staff.am, Job.am, CareerCenter.am, Findjobs.ge and LeverX Careers.
  Manual entries are clickable, excluded from scanners and source toggles, and
  explicitly do not imply work eligibility. Findjobs.ge terms prohibit
  repeated/systematic extraction of substantial data without written
  permission, so no recurring adapter was added. Full local suite: 432 passed,
  3 skipped; isolated PostgreSQL suite: 435 passed; compileall, secret scan,
  and diff check passed. Rebuilt Compose `repo`; startup `scan_all` completed
  at 18:06:12 UTC, runtime is 3.5.7 and PostgreSQL is healthy. No manual
  portal was requested during the scan.
- [ ] Keep visa sponsorship, work authorization, relocation support, salary
  and language evidence separate; unknown remains unknown.
- [x] Run the full isolated PostgreSQL suite and compile checks for the v3.5.7
  candidate after the encoded-HTML fix: 241 passed, 68.23% branch coverage;
  `git diff --check` passed.
- [x] Preserve Job Bank results when an individual query or detail request
  exhausts its bounded transport retry; continue processing other queries and
  vacancy details. Keep the five-second request pacing and avoid parallel
  calls. Full PostgreSQL suite: 251 passed, 68.44% branch coverage.
- [x] Owner ran Telegram `/scan` and `/scanstatus` at 19:33–19:36 Moscow time.
  The scan completed with Job Bank 12, EURES 16, HR.ge 2, HH 209, Remote OK 3,
  Arbeitnow 2 and Greenhouse 1; Job Bank took 100.7 seconds. Supplied logs show
  Job Bank detail requests and EURES/HR.ge requests returning HTTP 200, with no
  Job Bank warning or source failure in the excerpt. This confirms a healthy
  live run; partial transport-failure recovery remains covered by regression
  tests because no failure occurred during this scan.
- [x] Push candidate commit `4ccae7f`; GitHub push CI run `38143185017` passed
  Python checks, Docker build and secret scan.
- [x] Push HTML-entity fix commit `5d6b00b`; push CI `38147877309` and PR CI
  `38147879757` passed Python checks, Docker build and secret scan.
- [x] Open draft PR #18; GitHub checks `38143909265` and `38143905027` passed.
  Keep it unmerged until the fixed Telegram detail card is confirmed.
- [x] Apply with the safe updater; verify source/runtime 3.5.7, healthy
  PostgreSQL, attached original volumes and completed startup scan.
- [x] Owner checked `/targets relocation GE,AM`, `/sources`, `/scan`, and
  `/scanstatus`. Greenhouse was enabled and its public API returned HTTP 200,
  with zero matching roles. This is expected for the current configuration:
  Career-first has no target markets, and Relocation-first searches broad
  non-technical roles.
- [x] Owner completed `/targets career GE,AM`, `/sources`, `/scan`, and
  `/scanstatus`. Greenhouse returned one Lineate Infrastructure Engineer for
  GE (67/100) and one new notification; EURES returned 16. The separate
  Relocation-first Job Bank request failed with `ConnectTimeout`; all other
  sources completed. The bot showed work mode as unknown.
- [x] Inspect the Lineate notification through `/jobs` and `/job 1091`. Salary,
  work mode and unsupported visa/relocation facts remain unknown. The official
  posting is for a Georgian office and requires 3+ years Linux administration,
  2+ years production AWS, and 24/7 shift participation; see
  https://job-boards.greenhouse.io/lineate/jobs/8018252. The owner found its
  description displayed as escaped HTML entities.
- [x] Safely deploy the HTML-entity decoding fix. Compose source/runtime is
  3.5.7, PostgreSQL remained healthy, and startup `scan_all` completed at
  14:40:12 UTC. EURES search/detail calls returned HTTP 200 without SSL errors.
- [x] Owner reopened `/job 1091`: the Greenhouse description is now readable;
  salary, work mode, visa/work authorization and relocation assistance remain
  unknown without explicit evidence.
- [x] Recognize English `Necessary`, `Required`, `Minimum`, and `Essential
  Qualifications` headings so their technical signals count as required rather
  than falling back to an unqualified role score. Cover the technical score
  and interview-risk breakdown with regressions.
- [x] Full isolated PostgreSQL suite after the scoring fix: 246 passed,
  68.29% branch coverage; compile and diff checks passed. Push CI `38149543660`
  and PR CI `38149546515` passed for commit `7a6901d`.
- [x] Apply `7a6901d` through the safe updater. Source/runtime 3.5.7, app
  polling and PostgreSQL healthy. Startup scan completed at 15:04:57 UTC;
  inspected logs show the expected HH public fallback and HTTP 200 responses
  from the active sources, with no source error.
- [x] Extract `Minimum N years` / `At least N years` and add Windows and
  Databricks to technical evidence matching; regression coverage includes the
  Lineate-style requirements and experience comparison. Full PostgreSQL suite:
  247 passed, 68.36%; compile and diff checks passed.
- [x] Push CI `38150088881` and PR CI `38150092577` passed on code commit
  `678ddfc`; docs commit `664c559` also passed push/PR CI `38150288518` and
  `38150292566`.
- [x] Apply the candidate through the safe updater. Source/runtime 3.5.7 and
  PostgreSQL healthy. Startup scan completed at 15:15:48 UTC; inspected logs
  show no source error, SSL failure, timeout or traceback.
- [x] Owner reopened `/job 1091` and reported Technical 100 and interview risk
  `н/д` despite “Minimum 3 years.” Inspection found the saved posting's singular
  `Necessary Qualification` heading, which the parser did not recognize.
- [x] Recognize singular and plural necessary/required/minimum/essential
  qualification headings. Regressions cover the real singular Greenhouse form,
  Technical Score v2, and Recommendation v2 interview risk. Full isolated
  PostgreSQL suite: 248 passed, 68.36% branch coverage; compile and diff checks
  passed.
- [x] Push code commit `e978d07`; push CI `38151153964` and PR CI `38151157085`
  passed. Deploy through the safe updater; Compose source/runtime 3.5.7 and
  PostgreSQL healthy. Startup scan completed at 15:28:27 UTC with no source
  errors, SSL errors, timeouts, or tracebacks in the inspected logs.
- [x] Owner reopened `/job 1091` after the singular-heading fix and reported
  Technical 42 but interview risk `н/д`. The detail route supplies decoded
  text to Technical Score while Recommendation v2 independently rescored the
  stored HTML; this isolated the remaining mismatch.
- [x] Pass the same normalized vacancy text into Recommendation v2 and add a
  regression for the encoded Lineate HTML. It verifies Technical 42 and an
  interview-risk score of 58 rather than `н/д`.
- [x] Full isolated PostgreSQL suite: 248 passed, 68.36% branch coverage;
  compileall and `git diff --check` passed. Commit `8a583c7` passed push CI
  `38151840822` and PR CI `38151843490`.
- [x] Deploy `8a583c7` with the safe updater. Compose source/runtime 3.5.7 and
  PostgreSQL healthy. Startup scan completed at 15:38:13 UTC; the five-minute
  log check found no source errors, SSL failures, timeouts, or tracebacks.
- [x] Owner reopened `/job 1091` in Telegram at 18:42 Moscow time and confirmed
  Technical 42 plus interview risk 58 with explicit required-skill coverage
  and `fit=good`. This score is a matching-gap indicator, not a calibrated
  probability.
- [x] Add one bounded retry for Job Bank `httpx.TransportError` only, preserve
  the existing five-second delay before each request and shared crawl lock, and
  leave HTTP status errors unretried. Regression tests cover recovery,
  exhaustion, status handling and pacing; full isolated PostgreSQL suite:
  244 passed, 68.26% branch coverage.
- [x] Push commit `36c425b`; push CI `38148615302` and PR CI `38148617896`
  passed Python checks, Docker build and secret scan.
- [x] Safely update Compose project `repo`; source/runtime is 3.5.7,
  PostgreSQL is healthy, and startup `scan_all` completed at 14:51:38 UTC.
  Job Bank search and 12 detail requests and EURES search/detail requests
  returned HTTP 200; no Job Bank, EURES or scan error appeared in the inspected
  logs. No runtime transport failure occurred, so retry recovery is verified by
  regressions, not by injecting a live failure.
- [ ] For the time-sensitive relocation search, verify each useful opening's
  active/closing status, application deadline, expected start timing, and work
  eligibility from public evidence; leave missing details unknown.

## Follow-up — salary floor semantics
- [x] Clarify current assessment-reference behavior: Telegram now says
  `Месячный минимум для оценки` and does not promise a hard salary filter.
  This wording was already implemented before the current resume.
- [ ] A strict salary floor remains a separate owner decision; preserve current
  scoring and unknown structured-salary behavior until then.

## GitHub main synchronization
- [x] Integrate GitHub `main` commit `375af5f` into the release branch without
  rewriting history; full PostgreSQL suite passed (220 tests, 65.66%), commit
  `77379aa` was pushed, and both CI runs passed.
- [x] Owner supplied real-chat smoke results for `/salary`, `/blacklist`,
  `/scanstatus`, `/cancel`, `/import` prompt, `/version` and `/status`.
- [x] Merge PR #15 into `main`; GitHub main is v3.5.6 at `062eb25`.

## v3.5.6 Recommendation Model v2
- [x] Add persisted, explainable component scores for technical fit, growth,
  fast-exit, interview risk, salary, remote, relocation, security,
  infrastructure and competition.
- [x] Leave unsupported signals unknown, including public candidate counts.
- [x] Display component breakdown and evidence in vacancy details.
- [x] Keep existing total score/notification thresholds stable pending labeled
  outcomes; add additive JSONB migration 4.
- [x] Full isolated PostgreSQL suite: 220 passed, 65.66% branch coverage.
- [x] Publish `496c920`, deploy v3.5.6 and verify schema 4/4, polling and
  unchanged named volumes.
- [x] Owner opened `/job 580` and confirmed the Recommendation v2 components
  render; unavailable signals were shown as `н/д`.

## v3.5.5 Candidate Import & Profile Sync
- [x] Extract text from PDF, DOCX and TXT with bounded input/resource limits.
- [x] Add Telegram `/import` with explicit preview, cancel and save choices.
- [x] Persist resume text only after confirmation; never persist raw upload bytes
  or original filename.
- [x] Add confidence/provenance to Candidate Facts through additive migration 3.
- [x] Detect exact duplicates and flag overlaps without replacing existing facts.
- [x] Full isolated PostgreSQL suite: 217 passed, 65.15% branch coverage.
- [x] Publish commit `8131e2e` and deploy with `./job-agent update`; verify
  runtime 3.5.5, schema 3/3, healthy PostgreSQL and unchanged named volumes.
- [x] Owner confirmed `/import` opens the upload prompt and existing command
  smoke tests respond.
- [x] Owner uploaded a TXT test resume; the confirmation flow saved it as #6
  with zero facts added. Unsupported ZIP was rejected and prior imports were
  detected as duplicates; acceptance is recorded in the latest handoff entry.

## v3.5.2
- [x] Search preference engine.
- [x] Source enable/disable.
- [x] Source priority.
- [x] Multi-country selection and priorities.
- [x] Multi-city scope.
- [x] Relocation/visa/work-permit/package/immigration policies.
- [x] Button-driven Telegram Control Center.
- [x] Integrate prefilter/order into scan pipeline.
- [x] Unit tests for preference engine.
- [x] Add career-first, relocation-first and balanced search strategies.
- [x] Keep career and relocation discovery queries independent.
- [x] Add Telegram strategy selection and `/relocationroles`.
- [x] Add unauthenticated Arbeitnow Germany discovery with conservative support signals.
- [x] Add further public international sources with explicit candidate-eligibility evidence.
- [x] Add public Job Bank Canada discovery for international candidates; keep
  LMIA, eligibility and explicit support evidence separate.
- [x] Add public EURES vacancies explicitly flagged for cross-border
  recruitment; keep this separate from visa and relocation support.
- [x] Add opt-in independent Career-first and Relocation-first SearchProfiles.
- [x] Make one scan discover and match each active SearchProfile independently.
- [x] Preserve profile settings and matches when parallel search is disabled.
- [x] Full CI green (GitHub Actions run 110 succeeded for v3.5.4; Fast Scan
  code run 105 also passed).
- [x] Add current/desired/minimum salary controls in Telegram; minimum feeds
  the existing per-currency scoring threshold.
- [x] Add Telegram blacklist controls with case-insensitive add/remove/clear,
  persisted across active search directions.
- [x] Compare testsbuild with main and selectively port useful behavior;
  Saved navigation already exists locally, and no broad branch merge was needed.
- [x] Consolidate v3.5.2 source milestones into cumulative release v3.5.6;
  do not publish a retroactive v3.5.2 tag.

## Next
## Source alert resilience
- [x] Retry transient EURES transport failures with a bounded retry budget;
  do not retry HTTP status errors.
- [x] Ensure source failure notifications contain normalized error details;
  add regression coverage for transport retry and HTTP status formatting.
- [x] Full PostgreSQL suite: 206 passed, 64.46% branch coverage.
- [x] Publish as `f397f58`, run the safe tracked-branch update, verify runtime
  3.5.4 / healthy PostgreSQL / EURES HTTP 200, and confirm named volumes remain
  attached.
- [x] Extend EURES retries to raw `ssl.SSLError`; add a regression test and
  rerun the full suite (207 passed, 64.49% branch coverage).
- [x] Publish/deploy raw SSL retry as `d5d78d3`; runtime showed retry recovery
  on successful requests and one profile exhausting its retry budget.
- [x] Preserve successful EURES query/detail results if another exhausts
  retries; validate with a regression and the full suite (208 passed, 64.51%).
- [x] Publish/deploy partial-result handling as `8a87604`; verify retry-to-200
  behavior and confirm other sources continue when one profile exhausts all
  EURES search requests.

## v3.5.4 Multi-Source International Discovery
- [x] Add bounded EURES discovery for the employer's cross-border recruitment
  flag and support EURES destination-country selection.
- [x] Full PostgreSQL suite (203 passed) and coverage gate (64.39%) pass;
  GitHub Actions run 110 passes; Compose runtime updated to 3.5.4.
- [x] Complete real-chat acceptance for the latest Telegram controls and
  source dashboard; include the untagged v3.5.2–v3.5.5 milestones in cumulative
  release v3.5.6 without retroactive tags.

## v3.5.3 Fast Scan & Scan Dashboard
- [x] Run independent source discovery with a bounded concurrency of three;
  preserve source priority for sequential matching/ingestion.
- [x] Add source duration and isolated timeout/error reporting.
- [x] Reuse existing discovery cache; persist latest manual scan status and
  source summary in `runtime_state`.
- [x] Add `/scanstatus` and `/cancel` for in-flight manual scans.
- [x] Validate rebuilt Telegram bot polling and startup scan; real-chat command
  controls remain part of v3.5.2 acceptance above.
- [x] Audit competition/applicant signals in connected public sources. Per-vacancy
  applicant counts are employer-only (HH and Job Bank); EURES exposes positions,
  not applicant volume. Keep candidate counts unknown instead of estimating them.

## v3.6 follow-up — explicit requirement alternatives
- [ ] Represent alternative requirements (e.g. knowledge of one programming
  language from a list) separately from individually mandatory skills.
  Current required/preferred extraction labels section mentions only; avoid
  treating a Python mention among language alternatives as an employer's
  individual Python requirement. Preserve truth and review scoring semantics
  before changing approved weights or thresholds.
## 2026-10-18 — private Web GUI MVP, active

- Implement local owner-only Dashboard → Search → Jobs → Review → Profiles → Sources → Relocation → CV → Applications against existing PostgreSQL and scan service; retain human approval before sending. Initial route/action implementation is in `app/web.py`.
- Isolated PostgreSQL suite passed 1306 before the below-threshold UI addition; targeted Web GUI/search-preference tests passed 52/52 afterward. Finish diff check, then browser/manual acceptance with real owner data. Follow with reviewed browser CV import, bot/web scan coordination, source yield measurement and gated release. Keep Telegram two-track `/scan` available in parallel. No production mutation yet.
## 2026-10-18 — browser profile facts and package review

- Add owner-scoped manual Candidate Fact entry with explicit evidence and unknown experience default; show frozen application package/history with manual status/export. Targeted Web/application tests passed 14/14. Finish diff check and local checkpoint. PDF/DOCX import with reviewed facts remains the next CV step.
## 2026-10-18 — reviewed browser CV upload

- Reuse the existing safe PDF/DOCX/TXT parser, fact proposal/overlap review and atomic CV+facts persistence in Web GUI. Explicit preview and owner-scoped confirmation are implemented at local checkpoint `03094e5`; full isolated PostgreSQL suite passed 1314/1314 and the updated Docker image built. Follow with cross-process scan coordination, isolated browser/PostgreSQL acceptance and live source value measurement.
## 2026-10-18 — opt-in local Web GUI service

- Add a separate Compose overlay for the Web GUI, bound to localhost with an explicit long token and existing PostgreSQL dependency. Config validation passed with a dummy token. Complete static gates/checkpoint; runtime rollout still waits for backup/compatibility/rollback/smoke gates.
## 2026-10-18 — coordinated bot/Web scans

- Add a per-user PostgreSQL transaction lease for scheduled, Telegram and Web scans, with explicit busy state and preserving the active scan's dashboard. Full isolated suite passed 1318 before the final skipped-dashboard selection test, which passed in targeted tests; static gates and Docker build passed. Complete local checkpoint. GitHub push/PR is pending network availability; runtime was not changed.
## 2026-10-18 — Web GUI PostgreSQL acceptance and rollout prep

- Isolated HTTP/PostgreSQL test passed for all nine routes, owner-scoped status writes, export and cross-owner denial. Runtime/development schema versions read-only matched at 8. Added a concrete backup/restore, private smoke and rollback runbook; actual backup and release gates remain pending. Commit the verified test/docs, then retry Draft PR/CI when GitHub connectivity returns.

## 2026-10-18 — daily Web dashboard clarity

- Completed: concise persistent scan status and totals on Dashboard, per-profile Career-first/Relocation-first links, daily workflow shortcuts, and a separate sanitized Diagnostics page. Web unit tests passed 15; combined Web HTTP/PostgreSQL tests passed 16. Next: improve Jobs/Review cards and filters for fast save/skip/manual-application work, then perform integrated MVP stabilization.
