# Personal AI Job Agent

[English](README.md) · [Русский](README.ru.md)

A Telegram job-search assistant with independent **Career-first** and
**Relocation-first** search profiles, PostgreSQL storage, and evidence-based
vacancy matching.

## Project status

- **Source on `main`:** v3.5.6.
- **Latest published GitHub Release/tag:** v3.5.6.
- **Active candidate:** v3.5.7 on `feature/v3.5.7-international-market-coverage`;
  it remains an unmerged, unreleased draft PR #18.
- The latest full isolated PostgreSQL suite passes: 247 tests, 68.36% branch
  coverage. Required-section commit `7a6901d` passed push CI
  `38149543660` and PR CI `38149546515`; follow-up `678ddfc` passed push CI
  `38150088881` and PR CI `38150092577`. Documentation commit `664c559` passed
  push CI `38150288518` and PR CI `38150292566`. The owner previously confirmed
  `/job 1091` renders readable text, but Technical 100 came from fallback
  matching because `Necessary Qualifications` was not recognized. The candidate
  now extracts `Minimum N years` and includes Windows and Databricks in
  technical evidence matching.
- The candidate retries one Job Bank transport failure under its shared
  five-second request pacing; HTTP status errors are not retried. That retry
  update's startup scan completed at 14:51:38 UTC with Job Bank and EURES
  search/detail requests returning HTTP 200; no transport failure occurred to
  exercise the retry. The earlier required-section update's startup scan ran
  from 15:02:28 to 15:04:57 UTC. The latest candidate startup scan ran from
  15:13:24 to 15:15:48 UTC and completed successfully. The HH API returned 403
  before its public web fallback succeeded; all active sources returned
  successful responses in the inspected scan logs, with no source failure,
  SSL error, timeout, or traceback. **Review the recalculated Lineate card in
  Telegram is still pending.**
- Changelog entries v3.5.2–v3.5.5 are cumulative source milestones included in
  v3.5.6; they were not published as separate releases or tags.
- Owner acceptance for resume import and Recommendation v2 vacancy details
  completed in Telegram on 2026-10-11.
- The checked-out candidate and local Compose runtime report v3.5.7, with
  PostgreSQL healthy and schema 4/4. GitHub `main` and the latest formal
  release/tag stay at v3.5.6. No v3.5.7 tag or release exists yet.

## Search profiles

- **Career-first** prioritizes DevOps, Infrastructure, and SRE career fit.
- **Relocation-first** searches configured relocation roles and ranks only
  evidence-backed eligibility and support signals. Missing visa or relocation
  details remain unknown.
- A scan processes active profiles independently and continues when an
  individual source fails.

Configured public sources include HeadHunter, Remote OK, Arbeitnow, Job Bank
Canada, EURES, and Telegram ingestion. Georgia adapters (JOBS.GE and HR.ge) are
included when Georgia is selected for a profile. The v3.5.7 candidate adds
selectable Armenia and a public Greenhouse feed for Lineate when Armenia or
Georgia is selected; it does not imply visa sponsorship or relocation support.
See the [roadmap](ROADMAP.md) and
[international source review](docs/developer/INTERNATIONAL_SOURCES.md).

## Safety and data handling

- Automated applications and private HeadHunter actions are off.
- The bot does not bypass CAPTCHA or infer work authorization, visa sponsorship,
  relocation benefits, or salary from missing evidence.
- Resume files are processed with bounded in-memory extraction; the bot shows a
  preview and saves extracted information only after confirmation.
- The safe local updater preserves the PostgreSQL and storage volumes:

  ```bash
  JOB_AGENT_COMPOSE_PROJECT=repo ./job-agent update
  ```

## Documentation

- [Roadmap](ROADMAP.md)
- [Changelog](CHANGELOG.md)
- [Project brief and current priority](docs/PROJECT_OS/BRIEF.md)
- [Developer testing guide](docs/developer/TESTING.md)
- [Public international source review](docs/developer/INTERNATIONAL_SOURCES.md)

## Local checks

```bash
.venv/bin/pytest -q
python -m compileall -q app tests
git diff --check
```

PostgreSQL-backed tests and coverage instructions are in the
[testing guide](docs/developer/TESTING.md).
