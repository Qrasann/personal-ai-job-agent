# ARCHITECTURE DECISION RECORDS (ADR)

## ADR-001: Мультиисточниковая архитектура (Multi-Source Discovery)
- **Status:** ACCEPTED
- **Context:** HeadHunter часто блокирует запросы (HTTP 403) при частом обращении к API.
- **Decision:** HH является лишь одним из источников. Реализован веб-скрейпинг fallback, подключен RemoteOK, архитектура подготовлена к подключению прямых сайтов работодателей и Telegram-каналов.

## ADR-002: Атомарный Ingestion вакансий через Savepoints
- **Status:** ACCEPTED
- **Context:** Ручной `/scan` и плановый APScheduler `scan_all` могут одновременно обрабатывать одну и ту же вакансию, вызывая `UniqueViolationError` по `ix_jobs_fingerprint`.
- **Decision:** Использовать точки сохранения `async with session.begin_nested()` при вставке `Job` и `JobSourceRef`. При `IntegrityError` сессия не падает, а запись извлекается повторно.

## ADR-003: Синхронный запуск асинхронных тестов
- **Status:** ACCEPTED
- **Context:** В репозитории не используется `pytest-asyncio`.
- **Decision:** Все async-тесты оформляются как обычные функции с вызовом `asyncio.run(...)`.

## ADR-004: Черный список в SearchProfile
- **Status:** ACCEPTED
- **Context:** Требовалось исключать нерелевантные сферы (гэмблинг, беттинг) и нецелевые грейды.
- **Decision:** Поле `exclude_terms` хранится в `SearchProfile` (JSON/список), фильтрация применяется на стадии скоринга до отправки пользователю.
