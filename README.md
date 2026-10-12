# Personal AI Job Agent

[English](README.md) · [Русский](README.ru.md)

A Telegram job-search assistant with independent **Career-first** and
**Relocation-first** search profiles, PostgreSQL storage, and evidence-based
vacancy matching.

## Project status

- **Stable GitHub `main`:** v3.5.6. The latest formal release and tag are also
  v3.5.6. Changelog entries v3.5.2–v3.5.5 are cumulative milestones included
  in that release; they were not published as separate tags.
- **Active candidate:** v3.5.7 on
  `feature/v3.5.7-international-market-coverage`; PR #18 is an open draft
  against `main`. It has not been merged, tagged, or released.
- The current candidate keeps verified Job Bank vacancies after an isolated
  transport failure, avoids unnecessary idle time while retaining at least
  five seconds between request starts, and gives explicitly remote jobs a
  processing-priority bonus in both profiles. This does not change Match Score
  or prove that an employer permits work from every country. It also adds
  Himalayas' documented remote-jobs API and Remotive's official Devops RSS
  feed, with source attribution and country-scope handling. The Remotive
  response is shared and persisted for 24 hours.
- `/jobs below` opens a separate, score-descending manual-review list for
  nonzero matches below the normal threshold. It does not change scoring,
  notifications, or the threshold and states that legal work/relocation support
  still need confirmation.
- `/jobs career`, `/jobs relocation`, and `/jobs relocation below` show one
  direction with its own threshold and scores. Detail and comparison buttons
  retain that profile. Ordinary hotel/warehouse staff no longer trigger an
  engineering Staff/Senior exclusion; actual seniority restrictions remain.
- Verification for the current worktree: 319 passed and 3 database-dependent
  tests skipped locally; all 3 repository PostgreSQL integration tests passed.
  Compilation and `git diff --check` pass. The earlier full isolated-database
  suite result predates the latest source changes.
- Local Compose `repo` source/runtime are 3.5.7 and PostgreSQL is healthy. It
  was rebuilt at 01:36 Moscow on Oct 12; scoped job lists, details and
  comparisons are available for Telegram verification. Remotive's category RSS returned
  HTTP 200 with no job items, so Remotive's current parsed count is 0. The API
  also returned a general feed despite category filters, so the worktree uses
  the official Devops RSS feed and cache key v3. The owner confirmed `/sources`
  and `/scan`; `/jobs` attribution awaits a matching listing. The Himalayas
  Telegram source and geography-card acceptance is
  complete.
- English and Russian README entry points are provided separately. The
  published release notes for v3.5.6 are bilingual; the technical changelog is
  maintained in English.

## Search profiles

- **Career-first** prioritizes DevOps, Infrastructure, and SRE career fit.
- **Relocation-first** searches configured relocation roles and ranks only
  evidence-backed eligibility and support signals. Explicitly remote jobs get
  earlier processing priority in both independent profiles; geographic work
  eligibility remains a separate check. Missing visa or relocation details
  remain unknown.
- A scan processes active profiles independently and continues when an
  individual source fails.

Configured public sources include HeadHunter, Remote OK, Himalayas, Remotive
(DevOps/Sysadmin), Arbeitnow, Job Bank Canada, EURES, and Telegram ingestion.
Remotive's public feed is refreshed once per day and links back to its original
listing. HR.ge is included when Georgia is selected for a profile; JOBS.GE is
currently paused after returning HTTP 410. The v3.5.7
candidate adds selectable Armenia and a public Greenhouse feed for Lineate
when Armenia or Georgia is selected; it does not imply visa sponsorship or
relocation support. See the [roadmap](ROADMAP.md) and
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
- [Changelog (English)](CHANGELOG.md)
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
