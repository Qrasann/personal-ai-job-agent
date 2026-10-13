# Decisions

## 2026-10-14 — fixed source host for Georgia details

Listing HTML is untrusted input. HR.ge/JOBS.GE detail requests accept only
HTTPS URLs on the source host and standard port. Any new HTML detail adapter
must enforce its own source boundary before network fetches.

## 2026-10-14 — one-time resume import confirmation

The pending import preview is claimed before its first persistence operation to
prevent two Telegram callbacks from writing it concurrently. A failed claimed
preview is re-created by resending the file; atomic resume/fact persistence
requires a separate repository transaction design.

## 2026-10-14 — scoped reliability and security boundaries

Candidate Telegram commands and callbacks are private-chat actions; selected
Bot API channel posts retain their separate watcher route. The one configured
HH applicant credential belongs to the owner profile until per-user OAuth is
designed and approved. A failed vacancy is isolated within its source, with
partial status retained; transport errors are reported by type and HTTP status
without untrusted URLs or response bodies.

## 2026-10-14 — roadmap reconciliation

The complete original v3.5.1–v4.x product vision remains in canonical root
`ROADMAP.md`; already released versions and historical milestone meanings are
immutable. Proposed v3.5.8 Telegram Watcher and v3.5.9 Source Intelligence are
planning labels, not a `VERSION` change or a claim of release. Capability status
is tied to code, tests and runtime evidence. Career-first and Relocation-first
remain independent, and missing hiring/visa/relocation evidence remains unknown.
The two owner proposal Markdown files are reference input and remain untracked.

1. main stays on v3.5.1 until v3.5.2 passes CI and smoke tests.
2. testsbuild is reference/experimental work, not an automatic merge source.
3. v3.5.2 Search Control lives in SearchProfile.settings to avoid premature DB migration.
4. Disabled sources are never collected.
5. Country/source priority changes processing order; it does not fake technical fit.
6. prefer never removes a vacancy; require/exclude are explicit hard gates.
7. Unknown geography is not silently discarded.
8. Structured relocation flags are preferred; conservative text heuristics fill missing work-permit/package/support signals.
9. Repository + tests + PROJECT_OS must be sufficient for another developer or AI to continue.
10. Never fabricate candidate experience or silently auto-apply externally.
11. Supersedes decision 1 (2026-10-11): `main` now contains source version
    v3.5.6. `VERSION` identifies source metadata; only a Git tag/Release marks
    a formal publication. Treat v3.5.2–v3.5.6 as cumulative untagged source
    milestones and publish one tested cumulative v3.5.6 release after the
    remaining Telegram acceptance. Do not backfill intermediate tags.
