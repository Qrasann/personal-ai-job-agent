# DEVELOPMENT LOG

## 2026-09-19 — v3.5.3 Release & Project OS Setup
- **Changes:**
  - Устранена гонка `UniqueViolationError` при одновременной вставке вакансий (коммит `4797db8`).
  - Добавлен тест `tests/test_upsert_race.py`.
  - Выпущен релиз `v3.5.3` (коммит `4f247a0`, тег `v3.5.3`).
  - Создана система переносимого контекста `docs/PROJECT_OS/`.
- **Tests:** 164 passed, 3 skipped.

## 2026-09-19 — v3.5.2 Release: Blacklist Controls
- **Changes:**
  - Реализованы команды управления черным списком: `/blacklist`, `/blacklist <term>`, `/blacklist remove <term>`, `/blacklist clear`.
  - В карточки вакансий встроена кнопка «🚫 В чёрный список».
- **Release:** `v3.5.2` (PR #12).
