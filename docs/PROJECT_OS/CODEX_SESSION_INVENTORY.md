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

## Primary sessions

| ID | Created | Historical scope and result |
| --- | --- | --- |
| `01a1277e` | Oct 10 | Initial shell/navigation discussion, including a legacy path; no project requirement or verified code result to import. |
| `01a12783` | Oct 10 | Early v3.5.7 development, source/relocation and Telegram feedback, private ChatGPT export/context work, Channel Watcher. Its code/results are reflected in Git, canonical roadmap and dated PROJECT_OS history; personal relocation details stay in private context. |
| `01a1375a` | Oct 13 | Independent overnight Watcher subscriber-isolation fix and roadmap reconciliation; historical checkpoint `99ea166`, reported 724 isolated-PostgreSQL tests. Already integrated. |
| `01a13763` | Oct 13 | Continuing source diagnostics, Candidate Fact review, workflow instructions and current inventory request. Use actual HEAD rather than old turn checkpoints. |
| `01a13b75` | Oct 14 | Later v3.6 fit alternatives, Relocation Evidence, `/prepare`, source snapshots, application/interview work and Main/Scout routing review. Its last reported local checkpoint was `c6eddbf` with 1017 isolated-PostgreSQL tests; newer branch changes supersede that checkpoint. |
| `01a145bd` | Oct 16 | Unindexed metadata-only rollout: no user/agent messages or result found. |

## Child sessions

All child reports were research or scoped work for a parent. A child report is
not independent proof that its recommendation was merged or deployed.

| Parent | Child ID / name | Historical finding or contribution |
| --- | --- | --- |
| `01a12783` | `01a12d10` Laplace | Scoped `/compare` chain/profile ownership. |
| `01a12783` | `01a12d11` Mendel | Dated Armenia/Georgia legal-source research; reverify current rules before personal advice. |
| `01a12783` | `01a130df` Leibniz | `/scanstatus` reset regression for a new manual run. |
| `01a12783` | `01a130e0` Locke | Himalayas time-zone restrictions in the vacancy card. |
| `01a12783` | `01a130e2` Sartre | Explicit relocation-assistance phrasing and negative/conditional boundaries. |
| `01a12783` | `01a13222` Chandrasekhar | Unicode Georgian/Armenian role tokenization. |
| `01a12783` | `01a13222` Hume | Devexperts required/preferred heading regressions. |
| `01a12783` | `01a13223` Gibbs | Preserve verified partial jobs after later source-detail timeout. |
| `01a12783` | `01a133bb` Fermat | Historical shutdown handoff; also recorded old runtime `KeyError('found')`. |
| `01a12783` | `01a1361b` Franklin | Historical checkpoint handoff; no separate product requirement. |
| `01a12783` | `01a1361b` Noether | Remote scope/residence conflict finding; current code and tests must decide status. |
| `01a12783` | `01a1361c` Feynman | Historical checkpoint handoff; no separate product requirement. |
| `01a12783` | `01a1372e` Erdos | Context Watch lacked a synchronized chat delta; no live-chat access. |
| `01a12783` | `01a13739` Helmholtz | Manychat official employer research; no confirmed suitable current opening, so no new source claim. |
| `01a13763` | `01a138e5` Volta | Historical missing-`found` error→success path, later reproduced and handled in source diagnostics. |
| `01a13b75` | `01a13b7c` Schrodinger | Raised a Greenhouse redirect concern. Current adapter creates `httpx.AsyncClient` without enabling redirect following; treat the old concern as a review lead, not a confirmed SSRF. Broader adapter URL/redirect review remains open. |
| `01a13b75` | `01a13df3` Chandrasekhar | Application snapshot/audit-history research. Package snapshots now exist; `Application.job_id ON DELETE CASCADE` remains an explicit migration risk. |

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
  PR #29 and #30 after the BRIEF's `9b938ed` checkpoint. This inventory ran no
  pytest or PostgreSQL suite and does not infer deployment or release status.

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
