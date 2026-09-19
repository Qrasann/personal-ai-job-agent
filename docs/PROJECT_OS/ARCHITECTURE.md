# SYSTEM ARCHITECTURE

## Общая схема

text
[Telegram Bot (aiogram 3)]
│
▼
[app/main.py] ─── (APScheduler: scan_all every 15m)
│
├──> [app/sources/] ─── HH (API + fallback scraper), RemoteOK, TG Ingestion
│           │
│           ▼
├──> [app/domain/] ──── NormalizedJob -> canonical_fingerprint()
│           │
│           ▼
├──> [app/database/] ── repository.py -> PostgreSQL (asyncpg, models: Job, Match, Profile)
│           │
│           ▼
└──> [app/scoring/] ─── Match Scoring (Tech, Geo, Salary, Relocation, Roles, Blacklist)


## Хранение данных (PostgreSQL)
- `users`: Telegram-пользователи, настройки доступа, soft-delete (`deleted_at`).
- `candidate_profiles` & `candidate_facts`: подтвержденные факты опыта и навыков.
- `search_profiles`: целевые роли, география, зарплатные ожидания, `exclude_terms`.
- `jobs`: нормализованные вакансии с уникальным индексом `fingerprint`.
- `job_source_refs`: связка вакансии с исходной платформой (`source_id`, `source_job_id`).
- `job_matches`: результаты скоринга и статусы рассмотрения (`notified`, `saved`, `excluded`).
