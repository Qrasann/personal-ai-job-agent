# Handoff

For v3.5.2 review:
1. read CURRENT_STATE.md and TASKS.md;
2. inspect app/search/preferences.py;
3. inspect app/telegram/settings_handlers.py and settings_ui.py;
4. inspect the small integrations in app/services.py and app/main.py;
5. run pytest;
6. launch the bot in a test Telegram chat;
7. verify /settings, source toggles, country toggles, /cities and relocation policies;
8. verify /scan behaves like v3.5.1 if new geography controls were never configured.

Do not merge testsbuild wholesale. Compare it with main and port selected functionality with tests.
