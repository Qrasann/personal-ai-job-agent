# Codex session inventory — 2026-10-17

Read-only inventory of local Codex history for this repository. Source:
`~/.codex/state_5.sqlite` thread index and `~/.codex/sessions/**/rollout-*.jsonl`
metadata, owner messages and final agent reports. These are historical reports,
not fresh test or runtime evidence. Current code, Git, `ROADMAP.md` and `BRIEF.md`
remain authoritative. No session was archived, deleted or resumed for this review.

The index contains **22 threads: 5 primary and 17 child**. There are **23
rollout files**: the extra `01a145bd` file has metadata only and is absent from
the thread index. Dates below are rollout creation dates (UTC); IDs are unique
prefixes sufficient to locate the local file. `01a13763` is this continuing
primary thread, shown to make the inventory complete.

## Agent command center: all eight visible tasks

Codex CLI v0.163.0 `codex agents` displayed eight project tasks on Oct 17.
Five titled tasks correspond to the five indexed primary rollouts below by
title/content/time; the three additional `Untitled task` rows could not be
opened. Each failed with `no rollout found`; no matching record exists in
`state_5.sqlite` or `thread_history_1.sqlite`. Their original instructions
and outcomes are **unavailable**, so no completion or safe archival claim is
possible. The separate `01a145bd` metadata-only rollout is not one of these
three IDs.

| Command-center task | Local thread | Transferred to | Unchecked / recommendation |
| --- | --- | --- | --- |
| `Продолжить разработку Job Agent` (Working) | `01a13763` | `AGENTS.md`, `ROADMAP.md`, `BRIEF.md`, this inventory | **Keep:** sole Main continuation. |
| `Продолжи разработку Job Agent` (Ready) | `01a13b75` | Current code, roadmap v3.6–v3.9, dated PROJECT_OS checkpoints | **Manual review:** large later dialog; historical runtime claims need fresh acceptance. |
| `Start Codex in job-agent` (Inactive) | `01a1277e` | No distinct project requirement | **Archive candidate:** initial navigation only. |
| `Продолжай разработку Personal AI Job Agent v3.…` (Inactive) | `01a1375a` | Watcher code/tests, roadmap and HANDOFF | **Archive candidate:** local historical test result only. |
| `Проверь состояние проекта` (Inactive) | `01a12783` | Roadmap, Git history, PROJECT_OS, private context for personal facts | **Manual review:** sensitive early owner context stays private; verify preservation before archive. |
| `Untitled task` (Ready) | `01a1467c-5690-7a20-9261-6b9ddd4a0ee4` | Nothing retrievable | **Manual review:** missing rollout and indexed history. |
| `Untitled task` (Ready) | `01a1467c-7836-7713-9030-067a169570a7` | Nothing retrievable | **Manual review:** missing rollout and indexed history. |
| `Untitled task` (Ready) | `01a14682-4913-7903-b345-84721f5fd135` | Nothing retrievable | **Manual review:** missing rollout and indexed history. |

## Primary sessions

| ID | Created | Historical scope and result |
| --- | --- | --- |
| `01a1277e` | Oct 10 | Initial shell/navigation discussion, including a legacy path; no project requirement or verified code result to import. |
| `01a12783` | Oct 10 | Early v3.5.7 development, source/relocation and Telegram feedback, private ChatGPT export/context work, Channel Watcher. Its code/results are reflected in Git, canonical roadmap and dated PROJECT_OS history; personal relocation details stay in private context. |
| `01a1375a` | Oct 13 | Independent overnight Watcher subscriber-isolation fix and roadmap reconciliation; historical checkpoint `99ea166`, reported 724 isolated-PostgreSQL tests. Already integrated. |
| `01a13763` | Oct 13 | Continuing source diagnostics, Candidate Fact review, workflow instructions and current inventory request. Use actual HEAD rather than old turn checkpoints. |
| `01a13b75` | Oct 14 | Later v3.6 fit alternatives, Relocation Evidence, `/prepare`, source snapshots, application/interview work and Main/Scout routing review. Its last reported local checkpoint was `c6eddbf` with 1017 isolated-PostgreSQL tests; newer branch changes supersede that checkpoint. |
| `01a145bd` | Oct 16 | Unindexed metadata-only rollout: no user/agent messages or result found. |

Primary-session transfer checks: `01a1277e` adds nothing beyond correct repo
selection; `01a12783` supplies the original owner relocation/channel/search
intent and historical experiments, now held by roadmap, Git and private
context; `01a1375a` supplies an already merged Watcher isolation regression;
`01a13763` is Main; `01a13b75` supplies implemented candidate/source/package
increments plus open live acceptance. Old permissions to push or deploy are
superseded by the current explicit authorization boundary. No transcript or
private candidate fact was copied here.

## Child sessions

All child reports were research or scoped work for a parent. A child report is
not independent proof that its recommendation was merged or deployed.

| Parent | Child ID / name | Transferred result and destination | Still unverified / disposition |
| --- | --- | --- | --- |
| `01a12783` | `01a12d10` Laplace | Scoped `/compare` flow: matching/Telegram code and tests. | Runtime UX; archive candidate. |
| `01a12783` | `01a12d11` Mendel | Dated Armenia/Georgia source references: international-source docs. | Current legal rules and personal eligibility; manual review. |
| `01a12783` | `01a130df` Leibniz | `/scanstatus` reset: handler and regression test. | Live manual-scan UX; archive candidate. |
| `01a12783` | `01a130e0` Locke | Himalayas time-zone restriction display: adapter/view tests. | Current listing relevance; archive candidate. |
| `01a12783` | `01a130e2` Sartre | Relocation-assistance phrase boundaries: signal parser/tests. | New languages/phrases; archive candidate. |
| `01a12783` | `01a13222` Chandrasekhar | Georgian/Armenian role tokenization: matching code/tests. | Real source yield; archive candidate. |
| `01a12783` | `01a13222` Hume | Devexperts heading distinction: fact-comparison code/tests. | Other ATS formats; archive candidate. |
| `01a12783` | `01a13223` Gibbs | Partial jobs after timeout: source-loop code/tests. | Live source behavior; archive candidate. |
| `01a12783` | `01a133bb` Fermat | Historical checkpoint; old `found` traceback lead in source diagnostics. | Current HH runtime cause; archive candidate. |
| `01a12783` | `01a1361b` Franklin | Historical checkpoint: dated HANDOFF/DEVELOPMENT_LOG. | No distinct open finding; archive candidate. |
| `01a12783` | `01a1361b` Noether | Remote residence/scope conflict: remote-evidence code/tests and roadmap. | Broader free-text scopes; manual review. |
| `01a12783` | `01a1361c` Feynman | Historical checkpoint: dated HANDOFF/DEVELOPMENT_LOG. | No distinct open finding; archive candidate. |
| `01a12783` | `01a1372e` Erdos | Unsynchronized Context Watch boundary: AGENTS/BRIEF and private index. | No live chat delta; archive candidate. |
| `01a12783` | `01a13739` Helmholtz | Manychat research: international-source docs, no suitable role claimed. | Current openings/source permission; manual review. |
| `01a13763` | `01a138e5` Volta | Missing-`found` historical path: source ledger/tests and dated log. | Actual old alert attribution; archive candidate. |
| `01a13b75` | `01a13b7c` Schrodinger | Greenhouse redirect concern: source-security task/inventory. Current client does not enable following redirects. | Remaining adapter boundaries; manual review, no confirmed SSRF. |
| `01a13b75` | `01a13df3` Chandrasekhar | Application snapshots: schema/repository and roadmap; cascade risk in BRIEF. | Upgrade/rollback of future FK change; manual review. |

## Unique owner input, decisions and evidence

- **Product use:** Owner prioritizes a practical, lawful near-term relocation
  path and potentially useful remote roles, while keeping Career-first and
  Relocation-first independent. A remote listing does not prove legal hiring or
  work authorization. Personal finances, passport, citizenship and other
  sensitive route details remain in `~/codex-private-context/`; this tracked
  inventory deliberately does not duplicate them. Use current owner facts,
  not old chat excerpts, for any personal recommendation.
- **Telegram and search:** Owner requested actual channel vacancy discovery,
  descending match-score ordering, preservation of partial source results and
  intelligible errors. Channel Watcher and source diagnostics are in the
  roadmap/code; real channel access and live acceptance remain separate gates.
- **Continuity and context:** Owner requested ongoing Main-led roadmap work,
  backed-up checkpoints and use of selected ChatGPT export. Private Context
  Watch was only a local unsynchronized placeholder in these reports; it never
  established access to a live ChatGPT conversation. `AGENTS.md` and
  `AI_INSTRUCTIONS.md` hold the working protocol.
- **Publication:** Older messages discussed GitHub version copies and updating
  the bot. The current explicit safety rules require separate authorization
  for push/merge/release/deployment and production changes. Historical broad
  permissions are not treated as current authorization. Formal `main` and
  runtime status must be checked independently of feature-branch commits.
- **Delivery policy:** Later owner decision favors at-least-once Telegram job
  alerts: a duplicate after lost confirmation is acceptable; silent loss is
  worse. Durable journal and `/delivery` were merged in PR #28. PR #30 adds
  malformed-journal isolation; live acceptance is still pending.
- **Historical results:** Session-specific test counts (724, 1017 and others)
  are records of earlier checkpoints only. The current `dabe9a3` HEAD includes
  PR #29 and #30 after the BRIEF's `9b938ed` checkpoint. The initial inventory
  pass ran no tests; the later isolated PostgreSQL follow-up is recorded in
  HANDOFF. Neither pass infers deployment or release status.

Reusable, short task prompts extracted from repeated owner requests:

1. **Continue Main:** “Read BRIEF, actual Git and the relevant roadmap row;
   choose one unblocked high-value task; reproduce, fix, test, document and
   checkpoint. Preserve other work and continue.” This is codified in
   `AGENTS.md`/`AI_INSTRUCTIONS.md`; do not paste old full master prompts.
2. **Investigate a bug:** “Separate a confirmed root cause from an external
   hypothesis; add a failing regression, preserve partial results, and report
   tests actually run.” This drove the historical `found` and source-error
   work and remains a useful review template.
3. **Specialist review:** “Read only the named files and answer the concrete
   question with code/test references, uncertainty and no edits.” This is the
   on-demand Scout/Deep boundary; Main verifies any finding.

Experiments already accounted for: the old HH `found` path was reproduced in
tests, but current production error attribution still needs sanitized runtime
evidence; Manychat had no verified suitable opening at its dated check; a
Greenhouse redirect concern is not confirmed by the current non-following
client; alternative-skill scoring and source-posting snapshots are in code
and roadmap, while live quality remains unverified. Historical test counts
are deliberately not carried forward as a claim about current HEAD.

## On-demand role launch (Codex CLI v0.163.0)

The tracked launcher is `scripts/job-agent-codex`. The four one-word names in
`~/.local/bin` point to it; that directory is on the current shell PATH.

| Command | Actual behavior | Model / effort | Session policy |
| --- | --- | --- | --- |
| `main` | `codex resume` with exact thread `01a13763-4d60-7461-bdcb-5d6f2076d0bb` | Existing Main: GPT-6 Sol / medium | Reuse the sole Main session; no `--last` ambiguity. |
| `fast 'question'` | `codex exec --ephemeral` using `job_scout.toml`, read-only | GPT-6 Luna / low | One bounded research job, no persisted rollout. |
| `deep 'question'` | `codex exec --ephemeral` using `job_deep_review.toml`, read-only | GPT-6.1 Sol / high | One difficult review, no persisted rollout. |
| `agents` | `codex agents` | No model call merely to browse | View the native command center. |

Main decides whether a specialist is worth its startup/context cost; Fast and
Deep report findings and cannot modify the repository. They are CLI specialist
executions using the same model/effort/sandbox values as the configured Codex
subagent roles, not persistent replacement Main sessions. Main may also call
the native `job_scout`/`job_deep_review` subagents when justified. No agent is
kept running in the background. `main` should be called only when the thread
is idle; this inventory's exact ID must be updated if Main is deliberately
moved to another saved thread.

If the external `~/.local/bin` symlinks are missing on another machine, inspect
for name conflicts first, then create only missing links to the tracked
`scripts/job-agent-codex`. Do not replace an existing command silently. The
launcher reads Fast/Deep models from the existing role TOMLs; it does not
rewrite the user's Codex config or change Main's active model.

Checks: CLI reports v0.163.0; `main/fast/deep/agents --dry-run` and `bash -n`
passed. Real ephemeral smoke runs reported `gpt-6-luna/low/read-only` and
`gpt-6.1-sol/high/read-only` with `READY`. Each used roughly 16k total tokens
including startup context; no cost saving is inferred. The original failed
fast probe used the symlink directory as workdir, and a first corrected probe
used a CLI option unsupported by `codex exec`; both errors were fixed before
the successful role checks. No model smoke modified repository files.

## Consolidation recommendation

1. Keep root `ROADMAP.md` as the only product roadmap and current `BRIEF.md` as
   the short operational entry point. Link this inventory for provenance;
   do not paste full session transcripts or maintain a second task plan.
2. Keep private candidate/relocation facts and ChatGPT-export notes outside
   Git. Only record non-sensitive product requirements in tracked docs.
3. Use Git/CI and fresh tests to validate old child findings. Keep unresolved
   risk entries for Application deletion, URL/redirect boundaries and live
   Telegram/relocation acceptance; close them only with current evidence.
4. Retain all session files for now. Review any future archival or deletion
   separately, with a verified backup and an owner decision.

**Archive candidates after owner review:** the navigation-only primary
`01a1277e`, completed Watcher primary `01a1375a`, and child rows explicitly
marked “archive candidate”. **Keep:** Main `01a13763`. **Manual review before
archive:** large primaries `01a12783` and `01a13b75`, time-sensitive/open-risk
child rows, three inaccessible `Untitled task` IDs, and metadata-only
`01a145bd`. Archiving changes task visibility; deletion is a separate action
and is not recommended from this inventory. No archive or deletion was done.
