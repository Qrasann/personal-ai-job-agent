# Roadmap

Last reviewed: 2026-10-11

## Current release candidate — v3.5.6

The `main` branch contains source version v3.5.6. The last published GitHub
release is v3.5.1. v3.5.6 remains untagged until the owner checks resume import
preview/save and Recommendation v2 vacancy details in Telegram.

The current candidate also includes a focused EURES transport fix and clearer
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

- The owner confirmed the active Relocation-first target `GE`, the paused JOBS.GE
  status, and a completed live scan: EURES returned 16 vacancies and HR.ge 2.
  Continue checking result relevance and access conditions before treating
  Georgia as validated recurring coverage. Georgia details remain capped and
  paced, scheduled results are cached for six hours, and `/scan` forces a fresh
  fetch.
- Treat the Georgian adapters as limited personal discovery sources. JOBS.GE
  robots rules were unavailable (HTTP 410), HR.ge allows crawling in
  robots.txt, and neither board's recurring-reuse terms were confirmed. Keep
  request volume low and don't broaden collection without a clear source
  contract.
- Build an Armenia source only after confirming a public API or obtaining
  permission for automated access and reuse. The Unified Social Service lists
  e-work.am and workforall.am as public vacancy platforms, but both search
  pages timed out in the current check and no documented API/access terms were
  found. Request a permitted feed and clarify foreign-candidate access through
  `info@socservice.am`; Job.am and Staff.am have terms that constrain automated
  collection or redistribution.
- Official e-work registration guidance requires a PSN or national eID online;
  its in-person path for foreign nationals requires a residence card. Do not
  assume either portal serves a foreign jobseeker before relocation.
- Prefer employer career feeds or ATS APIs where available. Require a working
  posting URL, publication/expiry checks, location, language and eligibility
  evidence; do not mirror a whole job board.
- Expand role aliases for English, Russian, Georgian and Armenian searches
  where they improve real result coverage. Keep translations curated and
  deduplicate equivalent vacancies.
- Keep visa sponsorship, work authorization, relocation support, salary and
  language requirements as separate evidence fields. Never assume citizenship
  from the current country or turn missing evidence into a refusal.
- Measure EURES success by parsed search/detail results per profile, not by
  response status alone; retain partial results and keep retries bounded.

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
