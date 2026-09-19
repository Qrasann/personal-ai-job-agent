# CURRENT STATE

Updated: 2026-09-19

## Version
v3.5.3 (Tagged: `v3.5.3`, Commit: `4f247a0`)

## Status
STABLE

## Current Phase
v3.5.3 — Ingestion Resilience & In-Memory Duplicate Mitigation

## Completed in Current Phase
- [x] Реализовано управление черным списком: `/blacklist`, `/blacklist <term>`, `/blacklist remove <term>`, `/blacklist clear`.
- [x] Добавлена инлайн-кнопка «🚫 В чёрный список» в карточки вакансий.
- [x] Реализована команда экспорта сохранённых вакансий `/export` (Markdown / JSON).
- [x] Устранена гонка параллельной вставки (`UniqueViolationError` на `ix_jobs_fingerprint` и `uq_source_job`) через `session.begin_nested()` сейвпоинты в `upsert_job`.
- [x] Покрыто юнит-тестом `tests/test_upsert_race.py`.
- [x] Бот развернут в Docker, Telegram long polling активен, фоновый планировщик APScheduler (`scan_all`, 15м) функционирует.

## Active Task
Мониторинг завершен успешно. Готовность к бэклогу v3.6.0.

## In Progress
- [ ] Оформление документации `docs/PROJECT_OS/`.
- [ ] Формирование бэклога v3.6.0.

## Blocked
None.

## Tests
164 passed, 3 skipped (в среде Python 3.12 / venv).

## Active Branch
`main` (synchronized with `origin/main`).

## Important Constraints
- Не выполнять `docker compose down -v`.
- Не выдумывать опыт кандидата.
- Тесты БД, требующие сетевого PostgreSQL, требуют `JOB_AGENT_TEST_DATABASE_URL`; остальные тесты изолированы моками.
