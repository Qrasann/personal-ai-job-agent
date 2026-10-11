# Personal AI Job Agent — Codex Instructions

## Working repository

- This is the active application repository. Do not use the legacy n8n project in `~/projects/job-agent`.
- The local production-style deployment uses Docker Compose project name `repo` and preserves its existing named PostgreSQL and storage volumes.
- Never print, commit, replace, or delete `.env` or credentials.
- Never reset, clean, or overwrite a dirty worktree. Inspect `git status` first and preserve user changes.

## Development workflow

- Read `docs/PROJECT_OS/BRIEF.md` first. Then read only the detailed PROJECT_OS files relevant to the active task.
- Continue the existing architecture; do not recreate the project or rewrite working components without evidence.
- Maintain both independent search directions: Career-first for DevOps/Infrastructure/SRE and Relocation-first for legal international work with evidence-based visa/relocation handling.
- Do not treat missing relocation evidence as a confirmed refusal, and do not fabricate salary, visa, or relocation claims.
- Add regression tests for behavior changes and update `BRIEF.md`, `DEVELOPMENT_LOG.md`, `TASKS.md`, and `HANDOFF.md` after each completed stage.

## Verification

- Unit suite: `.venv/bin/pytest -q` when the virtual environment is available.
- PostgreSQL suite: start `docker compose -f docker-compose.test.yml up -d postgres-test`, then run tests with the documented `JOB_AGENT_TEST_DATABASE_URL` from `docs/developer/TESTING.md`.
- Before committing, run `git diff --check` and inspect `git status --short`.
- For the local running bot, use `JOB_AGENT_COMPOSE_PROJECT=repo ./job-agent status` and `JOB_AGENT_COMPOSE_PROJECT=repo ./job-agent logs`.
- Update the tracked release branch with `JOB_AGENT_COMPOSE_PROJECT=repo ./job-agent update`; it intentionally refuses dirty, detached, or untracked branches.

## Safety

- Do not delete Docker volumes, run `docker compose down -v`, or recreate the database unless the user explicitly requests data removal and a verified backup exists.
- Do not push, merge, or open a pull request unless the user explicitly authorizes publication.
- Do not enable automated job applications or private HH actions without explicit user approval.
