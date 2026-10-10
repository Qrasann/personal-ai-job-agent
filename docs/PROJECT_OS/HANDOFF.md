# Handoff

For v3.5.2 dual-mode review:
1. read CURRENT_STATE.md and TASKS.md;
2. inspect app/search/preferences.py;
3. inspect app/telegram/settings_handlers.py and settings_ui.py;
4. inspect the small integrations in app/services.py and app/main.py;
5. inspect `discovery_queries` and `search_strategy` in app/search/preferences.py;
6. run the full PostgreSQL-backed pytest suite;
7. launch the bot in a test Telegram chat;
8. verify `/settings`, all three strategies, `/relocationroles`, source/country/city controls and relocation policies;
9. verify `/scan` uses career queries in career-first, relocation queries in relocation-first, and both in balanced;
10. verify `/scan` behaves like v3.5.1 when no relocation roles or new geography controls are configured.
11. run `/parallelsearch on`, confirm two active profiles, then verify one `/scan` reports both profile names in progress;
12. run `/parallelsearch off`, confirm only Career-first remains active, then enable it again and confirm relocation settings survived.

Current branch: `feature/v3.5.2-dual-search-modes`, based on `origin/feature/v3.5.2-search-control`.
No database migration is required; new keys are stored in the existing JSON settings field.
Rollback is limited to the dual-mode commit/files because legacy `queries` remain unchanged.

Verified on 2026-10-10: 175 pytest tests passed against isolated PostgreSQL 16;
branch coverage 63.22% (gate 55%); compile, diff check and secret scan passed.
Manual Telegram smoke testing remains unverified.

Parallel search is opt-in. The existing profile becomes `Career-first`; one
`Relocation-first` profile is created and reused. Disabling parallel search
sets that profile inactive and does not delete its settings or JobMatch rows.

Do not merge testsbuild wholesale. Compare it with main and port selected functionality with tests.
