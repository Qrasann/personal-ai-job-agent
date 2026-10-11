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
- After the bot update, verify both profiles and inspect live scan logs. A
  source returning HTTP 200 headers is not healthy until its response body is
  read and vacancies are parsed.

## Next — v3.5.7 International Market Coverage

Focus on useful, legally reachable vacancies in Georgia and Armenia, while
preserving the separate Career-first and Relocation-first goals.

- Confirm the active profile targets and source enablement through `/targets`
  and `/sources`; test the Georgian adapters through a live scan, starting
  with Relocation-first, and assess latency and result quality. Georgia detail
  requests are capped and paced, scheduled results are cached for six hours,
  and `/scan` forces a fresh fetch.
- Treat the Georgian adapters as limited personal discovery sources. JOBS.GE
  robots rules were unavailable (HTTP 410), HR.ge allows crawling in
  robots.txt, and neither board's recurring-reuse terms were confirmed. Keep
  request volume low and don't broaden collection without a clear source
  contract.
- Build an Armenia source only after confirming a public API or obtaining
  permission for automated access and reuse. The official e-work portal is a
  candidate for access review; Job.am and Staff.am have terms that constrain
  automated collection or redistribution.
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
- Never enable auto-apply, private HeadHunter actions or destructive database
  operations as part of a release.
