# TASKS & BACKLOG

## Current Active Task
**ID:** V3.5.3-TASK-001
**Title:** Внедрение переносимого контекста (Project OS)
**Status:** IN_PROGRESS
**Goal:** Создать и зафиксировать в репозитории полный набор протоколов `docs/PROJECT_OS/` для бесшовной передачи контекста между ChatGPT, Claude, Gemini и разработчиками.
**Acceptance Criteria:**
- Директория `docs/PROJECT_OS/` содержит все базовые протоколы.
- Контекст синхронизирован с версией v3.5.3 и коммитом `4f247a0`.
- Все тесты проходят: 164 passed.

---

## Next Tasks (Backlog v3.6.0)

### TASK-002: Валидация и расширение фильтрации ATS / внешних ссылок
- **Goal:** Добавить разбор вакансий из прямых карьерных страниц и популярных ATS (Greenhouse, Lever) при пересылке ссылок.
- **Complexity:** Medium.

### TASK-003: Rate-limiting и Circuit Breaker для fallback-парсера HeadHunter
- **Goal:** При получении серии капч или 302/403 перенаправлений временно усыплять парсер HH с уведомлением пользователя через `/status`.
- **Complexity:** Low.

### TASK-004: Экспорт сохраненных вакансий
- **Goal:** Реализовать команду `/export` для выгрузки сохраненных вакансий (`/saved`) в Markdown/JSON.
- **Complexity:** Low.
