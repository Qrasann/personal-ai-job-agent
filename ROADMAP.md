# Roadmap

Last reviewed: 2026-10-11

## Latest release — v3.5.6

The `main` branch and latest formal GitHub tag/release are v3.5.6. Changelog
entries v3.5.2–v3.5.5 are cumulative milestones included in this release, not
separate releases or tags. The owner completed Telegram acceptance on
2026-10-11: TXT resume import saved after confirmation, unsupported ZIP rejected,
duplicates detected, and Recommendation v2 details displayed with unsupported
signals left unknown.

The v3.5.6 release also includes a focused EURES transport fix and clearer
per-profile market controls:

- EURES sends `Accept-Encoding: identity`; in the live container, a compressed
  response failed during TLS body reading while identity encoding returned the
  full 50-result JSON response.
- `/targets GE` applies the market to all active profiles. Use
  `/targets relocation GE` or `/targets career GE` to set one profile.
- `/sources` shows the source plan for each active profile.
- The owner verified the updated `/sources`, `/scanstatus`, and live scan in
  Telegram. EURES returned 16 parsed vacancies; the supplied later log tail
  shows a successful scheduled scan and responsive command handling. Continue
  monitoring scheduled EURES runs; one success does not establish permanent
  transport stability.
- The owner completed a Relocation-first GE scan: EURES returned 16 jobs,
  HR.ge returned 2, JOBS.GE returned HTTP 410, and Arbeitnow reported a
  transient read timeout. The candidate pauses JOBS.GE and retries one
  transient Arbeitnow transport failure. The owner confirmed the paused state
  in `/sources`; the fresh `/scan` and `/scanstatus` completed. Job Bank took
  99.5 seconds of the 162-second scan. Keep its five-second request pacing
  while evaluating latency improvements.

## Next — v3.5.7 International Market Coverage

Focus on useful, legally reachable vacancies in Georgia and Armenia, while
preserving the separate Career-first and Relocation-first goals.

The active candidate now adds selectable `AM` and a bounded Greenhouse Job
Board API connector for Lineate. It runs only for profiles targeting AM or GE,
filters by the profile's role queries and explicit posting location, and leaves
work mode, salary, visa and relocation unknown without direct evidence. The
current Lineate board shows an Infrastructure Engineer for its Georgian office
and a Data Engineer in Yerevan; only the former matches the current
DevOps/Infrastructure search. The full isolated PostgreSQL suite passes with
240 tests and 68.22% branch coverage; GitHub push CI run `38143185017` passed.
The candidate is running on the local Compose bot for owner Telegram acceptance;
it is not a main-branch release or formal release.

The owner has a near-term relocation objective. Prefer live vacancies with
clear application deadlines and start timing, and record candidate eligibility
only from vacancy or official-source evidence. Missing dates, visa support and
relocation benefits remain unknown. The specific personal timing estimate is
kept out of this public roadmap.

- The owner confirmed the active Relocation-first target `GE`, the paused JOBS.GE
  status, and a completed live scan: EURES returned 16 vacancies and HR.ge 2.
  Continue checking result relevance and access conditions before treating
  Georgia as validated recurring coverage. Georgia details remain capped and
  paced, scheduled results are cached for six hours, and `/scan` forces a fresh
  fetch.
- Georgia's Labour Migration Law now has 2026-03-01 changes in effect: for
  local paid work, an eligible foreign worker needs a right to work through a
  local employer and then the applicable immigration status. Recheck the
  candidate's case and current rules; selecting `GE` alone does not make a
  local vacancy legally actionable.
- Treat the Georgian adapters as limited personal discovery sources. JOBS.GE
  robots rules were unavailable (HTTP 410), HR.ge allows crawling in
  robots.txt, and neither board's recurring-reuse terms were confirmed. Keep
  request volume low and don't broaden collection without a clear source
  contract.
- Defer bot integration of Armenia's government-listed e-work.am and
  workforall.am: both search pages timed out in the current checks, and no
  public API/feed or automated-reuse terms were found. Manual accessibility
  also remains unverified. Do not
  make cold outreach to government agencies a release prerequisite. The
  official e-work registration requirements apply to registration with that
  service; they do not establish a general ban on applying directly to
  employers.
- The Lineate feed uses Greenhouse's documented unauthenticated public GET API.
  The selected-country scope prevents its other office listings from being
  labeled as Armenia/Georgia jobs. Keep expanding the employer list only when
  the employer's public ATS board and a relevant current role are verified.
- Staff.am has listings in the candidate's DevOps/Infrastructure area and may
  be useful for manual search. Its current terms prohibit automated scraping
  without written permission. Job.am terms restrict unauthorized reuse and
  redistribution. Do not add either as a bot collector unless the owner grants
  access through a documented feed or permission.
- The official Armenian `workpermit.am` portal provides an employer-side
  foreign-hiring/work-residence workflow and says EAEU citizens are exempt
  from work-permit documentation for the employment-contract period. It is
  not yet verified as anonymous job discovery or a public feed. Its FAQ
  question “How to find a job” is visible but the answer is not rendered; the
  official user guide describes an employer-led vacancy and foreign-worker
  account flow. Defer integration unless a relevant public feed or documented
  authorized access route is identified; no agency email is needed to continue
  the release.
- Keep Armenia's EAEU work-permit exemption separate from residence paperwork:
  the official portal says its lawful-residence certificate cannot be printed
  without a Public Services Number.
- Official e-work registration guidance requires a PSN or national eID online;
  its in-person path for foreign nationals requires a residence card. These
  are prerequisites for registering with that state employment service, not
  proof that a foreign candidate cannot apply directly to an employer. Keep
  portal access and individual legal eligibility as separate questions.
- Prefer permitted employer career feeds, documented public APIs, and
  owner-selected Telegram channels where available. Require a working
  posting URL, publication/expiry checks, location, language and eligibility
  evidence; do not mirror a whole job board.
- Expand role aliases for English, Russian, Georgian and Armenian searches
  where they improve real result coverage. Keep translations curated and
  deduplicate equivalent vacancies.
- Keep visa sponsorship, work authorization, relocation support, salary and
  language requirements as separate evidence fields. Never assume citizenship
  from the current country or turn missing evidence into a refusal.
- For Georgia, current law requires covered foreign workers in local paid work
  to hold the right to work, employment agreement and applicable immigration
  status; the employer submits the right-to-work application. Selecting `GE`
  must not be presented as proof that a candidate is eligible.
- `/salary minimum` currently contributes to scoring when salary is structured;
  it is not a hard exclusion rule. The bot's “minimum for filter” wording is
  misleading, and `/job 580` showed a 90,000 RUB amount only inside the
  description while the structured salary remained unknown. Clarify this
  behavior or implement a separately tested strict floor before relying on it
  to remove below-minimum vacancies.
- Measure EURES success by parsed search/detail results per profile, not by
  response status alone; retain partial results and keep retries bounded.
- After candidate deployment, verify `/targets relocation GE,AM`, `/sources`,
  and `/scan` in Telegram. Confirm that the Lineate Infrastructure Engineer
  appears only in the GE profile and carries no unsupported visa/relocation
  claim; record `/scanstatus` and source warnings.
- For near-term relocation decisions, keep opening status, application
  deadline, expected start date and work-eligibility evidence separate. Add
  these fields only when a source provides them; do not infer processing time.

## Later stages

- **v3.6 — Candidate and vacancy fit:** validate technical fit, relocation
  viability, salary normalization and affordability with explicit evidence.
- **v3.7 — Application workspace:** improve resume-to-vacancy tailoring and
  track manually confirmed application stages; no automatic application.
- **v3.8 — Recruiter and interview support:** prepare grounded recruiter replies
  and interview practice from the vacancy and confirmed candidate facts.
- **v4.x — Productization:** consider a dashboard or multi-user operation only
  after the personal workflow is stable and the owner wants that scope.

## Release rules

- Keep one release title format: `vX.Y.Z — Feature Name`.
- Publish a GitHub Release only for the tested version tag and include its test
  results, migration status and any owner acceptance still required.
- Keep `VERSION`, `CHANGELOG.md`, README status and the release tag aligned.
- Treat `VERSION` as the source-tree version and a Git tag/Release as the formal
  publication marker. When several cumulative milestones were never tagged,
  publish one tested cumulative release; do not create retroactive tags that
  imply separate releases were accepted.
- Never enable auto-apply, private HeadHunter actions or destructive database
  operations as part of a release.
