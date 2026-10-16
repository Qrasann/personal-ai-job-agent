# Personal AI Job Agent — Codex Instructions

## Working repository

- This is the active application repository. Do not use the legacy n8n project in `~/projects/job-agent`.
- The local production-style deployment uses Docker Compose project name `repo` and preserves its existing named PostgreSQL and storage volumes.
- Never print, commit, replace, or delete `.env` or credentials.
- Never reset, clean, or overwrite a dirty worktree. Inspect `git status` first and preserve user changes.

## Development workflow

- Read `docs/PROJECT_OS/BRIEF.md` first. Then read only the detailed PROJECT_OS files relevant to the active task. Old HANDOFF/TASKS entries are historical, not current operational facts.
- Act as the continuing lead developer. Use the actual Git state, the canonical `ROADMAP.md`, and the short current `docs/PROJECT_OS/BRIEF.md` and relevant HANDOFF sections to choose the next useful, safe task. Keep the original v3.5.x–v4.x product direction.
- Work in small completed increments: verify the current behavior, implement a focused change, add meaningful regression coverage, run the relevant gates, update PROJECT_OS, record a local checkpoint when allowed, then choose the next task. Do not stop at an audit or one blocked task while independent useful work remains.
- Treat new owner ideas and bug reports as input to the same roadmap: assess their impact, adjust priority, finish the focused work, and return to the remaining plan. Do not duplicate completed components.
- Explain progress briefly: what is being changed, the evidence and test result, and the next step. Ask the owner only for material architecture choices, data-loss risk, credentials, or authorization for external actions.
- Model routing: The current local Codex default and verified Main session are GPT-6 Sol at medium effort. Use `job_scout` (GPT-6 Luna, low effort, read-only) only for independent research when its startup/context cost is justified; use `job_deep_review` (GPT-6.1 Sol, high effort, read-only) only for complex security, architecture, or difficult debugging. Main should work alone for ordinary and small tasks; normally keep at most one additional agent active. Give a narrowly scoped Scout a self-contained prompt with `fork_turns="none"` when prior conversation context is unnecessary. Verify actual turn model and usage before claiming routing or savings; review Scout findings against code/tests. Do not assume a running Main session can switch models mid-turn.
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

<!-- PERSONAL_AI_JOB_AGENT_CODEX_MODE_V1_BEGIN -->
## Persistent Codex collaboration mode — Personal AI Job Agent

This is an existing long-running product, not a greenfield project. Follow all existing
safety/project instructions. Do not override stricter instructions elsewhere.

1. Before work, check `git status --short --branch`, current HEAD, and any unfinished
   changes. Read the relevant sections of root `ROADMAP.md` and current `BRIEF.md`;
   inspect only task-relevant headings in other PROJECT_OS files, not their full histories.
   Treat the **local code and tests** as evidence of implementation; the canonical
   root `ROADMAP.md` is the product roadmap. Remote GitHub may be behind local work.
2. Develop like an ongoing engineering partnership: pick the next high-value,
   unblocked task; define acceptance criteria; implement a small coherent increment;
   test; inspect the diff; update concise PROJECT_OS status/handoff; continue to the
   next task when the current interactive/exec run can continue safely.
3. New user bugs/features temporarily reprioritize the queue. Fix/test/document,
   integrate genuinely new ideas into the canonical roadmap, then resume the broader
   original + updated product vision. Do not redo completed work or repeatedly audit
   without a reason. Do not stop all work for one externally blocked task.
4. Keep explanations concise and useful: what changed, why, verified test results,
   current blockers, next item. Never claim a test or live acceptance passed unless run.
5. Main performs ordinary work itself. Delegate to Fast/Deep only if these agents are
   actually configured and delegation meaningfully saves cost or improves quality.
   A prompt alone does not switch the main model automatically; inspect the actual
   CLI/model configuration before claiming adaptive routing. Prefer one subagent at a time.
6. No `push`, PR merge, release/tag, deployment, VERSION change, production DB/volume
   modification, automated job applications or external recruiter messages without
   explicit owner authorization. No destructive Git operations. Preserve uncommitted
   changes. Run PostgreSQL tests only with the isolated DB described in
   `docs/developer/TESTING.md`. Local commits only for owned, reviewable, verified
   changes and only when permitted by existing project rules. Never stage proposal
   Markdown files or secrets by accident.
7. Before context/session ends, leave exact state and next steps in
   `docs/PROJECT_OS/HANDOFF.md`. Codex cannot promise indefinite operation after a
   session finishes; an external supervisor is needed for timed/unattended loops.

See `docs/PROJECT_OS/AI_INSTRUCTIONS.md` for the full working protocol.
<!-- PERSONAL_AI_JOB_AGENT_CODEX_MODE_V1_END -->
