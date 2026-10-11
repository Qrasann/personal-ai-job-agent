# Personal AI Job Agent

[English](README.md) · [Русский](README.ru.md)

A Telegram job-search assistant with independent **Career-first** and
**Relocation-first** search profiles, PostgreSQL storage, and evidence-based
vacancy matching.

## Project status

- `main` contains source version **v3.5.6**.
- The latest published GitHub release is **v3.5.1**. The v3.5.6 release tag is
  intentionally pending end-to-end Telegram acceptance of resume import and
  vacancy recommendation details.
- The production-style local Compose deployment was last verified on v3.5.6,
  with PostgreSQL healthy and schema 4/4.

## Search profiles

- **Career-first** prioritizes DevOps, Infrastructure, and SRE career fit.
- **Relocation-first** searches configured relocation roles and ranks only
  evidence-backed eligibility and support signals. Missing visa or relocation
  details remain unknown.
- A scan processes active profiles independently and continues when an
  individual source fails.

Configured public sources include HeadHunter, Remote OK, Arbeitnow, Job Bank
Canada, and EURES. Georgia adapters (JOBS.GE and HR.ge) are included when
Georgia is selected for a profile. Armenia does not yet have a connected local
source; see the [roadmap](ROADMAP.md) and
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
