# Experiment: verified external feature reuse (2026-10-20)

**Status:** isolated evaluation only; not a production integration, release, or replacement roadmap.

- Our repository: `Qrasann/personal-ai-job-agent`.
- Base: published `feature/v3.5.7-international-market-coverage` at `e4f8eafc615bf9508964820d16c8e3f39b78cd26`. The owner's local worktree may be newer: check it before any future cherry-pick.
- Source: [MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search), **pinned to tag `v1.7.3`**, MIT. Retained copyright/license: `LICENSES/ai-job-search-MIT.txt`.
- Rule: evaluate overlap against current code/tests first; only adopt a better solution if its advantage is demonstrated and no conflict/regression occurs.
- This branch does not alter canonical `ROADMAP.md`, `AGENTS.md`, priorities, active Draft PR #18, the Telegram UX ordering, or the indefinitely frozen Web GUI.
- No production DB migration, Docker deploy, model-provider change, external applications, recruiter actions, or private credentials.

## Isolated first candidate — posting integrity guard

Upstream code and its regression tests are staged **without modification**:

- `tools/posting_guard.py` — standalone deterministic inspection of untrusted vacancy text / HTML: hidden content, invisible controls, spoofing/instruction-like lines. It reports findings without automatically excluding a job.
- `tests/test_posting_guard.py` — upstream's `unittest` regression suite, discoverable by our `pytest` runner.

The application does **not** import or execute this tool. Search, scoring, source collection, LLM prompts and notifications are unchanged. No compatibility claim or runtime improvement is implied by merely copying it.

To evaluate locally or in CI:

```bash
python -m pytest -q tests/test_posting_guard.py
python -m compileall -q app tools tests
python tools/posting_guard.py --help
```

**Promotion gates** before any runtime wiring:
1. Upstream tests pass **in this repository**, and existing Python/DB/secret-scan CI stays green.
2. Add *our own* Russian/English/relocation posting fixtures: ordinary SSH/SRE instructions, mixed HTML, Cyrillic + English skills, nested hidden blocks, source-specific raw evidence and borderline injection-like text.
3. Demonstrate a specific vulnerability or quality improvement over existing safe JSON separation in `app/agents/llm.py`, without silently changing canonical vacancy text, evidence, match scores, eligibility, Good/Stretch thresholds or user settings.
4. Integrate only behind an explicit, default-off rollout switch (or a similarly safe staged path), with a clear comparison and rollback. Keep raw source text for provenance. A warning is not proof of maliciousness.
5. Check the owner's **actual local** worktree and pending changes, then obtain authorization for any merge/deploy. An upstream MIT license is not a source-access permission for job sites.

## Candidate overlap matrix (not automatically approved)

| Scope | Current integration decision | Reason / verification |
| --- | --- | --- |
| Posting integrity gate | **ISOLATED CANDIDATE** | Vendored from upstream tag with upstream tests; **not connected** to runtime |
| PDF text / ATS validator | **EVALUATE LATER** | Compare to any actual CV export implementation; test Cyrillic and extractability |
| PDF layout checks | **EVALUATE LATER** | Upstream thresholds are template-specific; do not port blindly |
| Draft + independent review | **EVALUATE LATER** | Extend existing `/prepare` rather than replacing Candidate Facts or immutable snapshots |
| Application-form answers | **EVALUATE LATER** | Keep answer claims grounded and external form submission approval-only |
| Outcome/follow-up | **EVALUATE LATER** | Extend existing PostgreSQL status/history; never duplicate or auto-contact |
| Company research/cache | **EVALUATE LATER** | Only verified official sources; proper provenance and freshness |
| Interview and skill gaps | **EVALUATE LATER** | Extend existing deterministic practical interviews; no invented proficiency |
| Foreign board scraping / eligibility gates | **NO BULK PORT** | Respect access terms, independently configured Career-first/Relocation-first and unknown legal evidence |
| Claude workflow / spreadsheet tracker | **DO NOT REPLACE** | Our Python/PostgreSQL/Telegram architecture already provides the backbone |

## Non-regression and scope guarantees

- `main` and `feature/v3.5.7-international-market-coverage` remain unmodified by this experiment.
- No direct runtime coupling between the external guard and the application; no new runtime dependency.
- No `git merge`, rebase, production deploy, DB mutation or force push without separate approval and verified test gates.
- Current roadmap priorities remain unchanged. Web GUI is **frozen indefinitely**; Telegram controls are improved only as tasks become due in the established sequence.
