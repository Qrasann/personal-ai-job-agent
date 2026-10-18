# AI Instructions

When continuing this project:
- repository state is authoritative;
- read AGENTS.md and BRIEF.md first, then relevant ROADMAP/TASKS/code;
- preserve main as stable;
- prefer small tested changes;
- never expose .env, Telegram tokens or API secrets;
- never fabricate commercial candidate experience;
- do not bypass CAPTCHA or access controls;
- external applications/replies require explicit approval unless the product later implements a deliberate opt-in automation;
- keep PROJECT_OS synchronized with code and release status;
- when testsbuild conflicts with main, port intent instead of blindly merging code.

<!-- PERSONAL_AI_JOB_AGENT_WORKFLOW_V1_BEGIN -->
## Continuous product-development workflow (Codex)

### Collaboration contract

The owner sets goals, constraints, priorities and approves external/risky actions.
Codex Main acts as the lead engineer in a *continuing* product-development process:
**inspect → choose next task → acceptance criteria → implement → targeted tests →
required integration checks → review diff/security → update canonical docs → next task**.
Use clear Russian for user-facing engineering updates. Avoid lengthy repetitive reports
and repeated permission requests for safe local edits and isolated tests.

### Sources of truth and preservation

- Root `ROADMAP.md` = canonical integrated old + new roadmap and product intent.
- `docs/PROJECT_OS/TASKS.md` = actionable backlog; `CURRENT_STATE.md` = current state;
  `HANDOFF.md` = exact restart point; `DECISIONS.md` = rationale/history;
  `KNOWN_ISSUES.md` = unresolved risks. Do not create parallel roadmaps.
- Start from the LOCAL working tree and its tests, then handoff. GitHub may be stale.
  Preserve unstaged/staged edits and 53+ previously unpushed local commits; verify
  current counts rather than assuming the last checkpoint is still current.
- The two `AI-JOB-AGENT-*ROADMAP*PROPOSAL*.md` and
  `CODEX-MAIN-ROADMAP-SYNC-PROMPT.md` files are historical proposals, not another
  source of truth. Do not add them to commits; do not re-import already merged items.
- Original product scope remains represented: v3.5.x search/control/fast scan,
  multi-source/Telegram/Candidate Import/Recommendation/Relocation; v3.6 resume and
  vacancy intelligence; v3.7 application packages (draft + approval); v3.8 recruiter
  and application tracking; v3.9 practical interview agent; v4.x web UI, multi-user,
  multi-profession, AI router, local models/BYOK/SaaS; cross-cutting security,
  infrastructure, credible international relocation and lawful non-IT opportunities.

### Prioritization and autonomy

- First: data loss, confirmed serious security defects, critical reliability bugs.
- Then: fixes that make today's job search useful (relevant genuine vacancies,
  relocation eligibility, accurate scoring, source health, Telegram UX).
- Then: complete partially implemented features before large speculative rewrites;
  follow roadmap dependencies. Split large milestones into independently testable slices.
- Treat `IMPLEMENTED`, `PARTIAL`, `IN_PROGRESS`, `PLANNED`, `BLOCKED` as evidence-based
  status labels. Each unblocked `PARTIAL/PLANNED` candidate needs concrete acceptance
  criteria. Don't declare a feature done solely because unit tests are green.
- If HH live access, Telegram channel permissions, CI, Git writes, Docker sockets,
  or production deployment are blocked, record exact cause and select another
  independent safe task. Never bypass authorization or sandbox restrictions.
- During an active Codex run, proceed through useful tasks rather than ending after
  an audit or single fix. Stop when no safe work remains, a decision is genuinely
  needed for ALL remaining work, the host session ends, or a real external deadline
  applies. Do not pretend text instructions alone guarantee 24/7 operation.

### Engineering and quality

- Reproduce bugs where possible; add regression coverage before or with minimal fix.
- Source errors should be classified as network/HTTP/parse/internal, with
  human-readable Russian Telegram messages and safe logs; no raw DNS/TLS URLs,
  secrets, credentials or user data. `KeyError('found')` and Remote OK timeouts are
  concrete leads, not assumed confirmed root causes. Verify against LOCAL code.
- Preserve independent source/profile results, partial results, deduplication,
  idempotency, Candidate Facts provenance and atomicity, Telegram subscription
  isolation, source URL/redirect boundaries, and privacy protections.
- Run focused tests and then appropriate broader suite for risk, including isolated
  PostgreSQL tests **only** according to `docs/developer/TESTING.md`. If environment
  blocks them, say explicitly that DB verification did not run. Never touch production
  PostgreSQL or Docker volumes to make a test work.
- Before local checkpoint commit: inspect `git diff`, `git status`, test output and
  staged paths. Do not stage all files indiscriminately or commit unrelated edits.
  If required gates are blocked, leave working tree and precise owner commands.
- Update the relevant canonical documents concisely after meaningful increments,
  not after every minor command. End each session with a useful HANDOFF and next task.

### Models and token economy

- **MAXIMUM TOKEN ECONOMY is the standing owner mode.** Optimize repeated work,
  context size and model/delegation choice without weakening correctness, security,
  migrations, release gates or risk-proportionate testing.
- Main does ordinary tasks itself. Fast is only for truly cheap/isolated research or
  tests when total delegation overhead is justified; Deep only for risky architecture,
  intricate concurrency/security/debugging when strong reasoning is worth it.
- For a narrow read-only Scout task, use a self-contained prompt and
  `fork_turns="none"` when history is unnecessary. Inspect the subagent's turn
  model, usage and factual result; a cheaper model alone does not prove a
  lower-cost workflow.
- Only use agents/models supported by the installed Codex. Inspect effective model,
  reasoning effort, role config and a small actual agent invocation before claiming
  that adaptive delegation is operational. Don't rewrite ~/.codex/config.toml
  or switch models without checking availability and preserving backups.
- Minimize redundant file reads, long status chatter, unnecessary agents and repeated
  whole-suite runs when no relevant change occurred; never economize by skipping
  necessary tests or security gates.
- Start with `AGENTS.md`, the compact current HANDOFF/BRIEF and narrowly relevant code;
  load roadmap history only when the task needs it. Run focused tests first and expand
  by risk. The full pytest suite has a known intermittent stall: bound diagnostic runs
  and do not repeat an unchanged hanging command as if repetition were evidence.
- Keep one coherent checkpoint per logical increment: task, changed files, tests,
  commit, open questions and next step. Compact or hand off before context becomes
  wasteful. Codex must not claim it can read account quota or change the active Main
  model unless the current environment exposes and verifies that capability.

### Owner-facing checkpoints

Keep updates concise: **done / verified / open risks / next step**. Distinguish
local code from deployed bot, offline tests from live Telegram/HH/relocation acceptance,
and planning from implementation. No GitHub push, merge, release, deploy, VERSION change,
production mutation, external job application, or external recruiter contact without
explicit owner approval. A normal task completion is not authorization for these.
<!-- PERSONAL_AI_JOB_AGENT_WORKFLOW_V1_END -->
