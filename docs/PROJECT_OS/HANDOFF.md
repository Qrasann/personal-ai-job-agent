# HANDOFF PROTOCOL

## Project
Personal AI Job Agent (`personal-ai-job-agent`)

## Date
2026-09-19

## Current Version & Git Target
- **Version:** v3.5.3
- **Branch:** `main`
- **Last Release Tag:** `v3.5.3`
- **Last Commit:** `4f247a0 chore(release): bump version to v3.5.3`

## What Was Just Done
1. Исправлена ошибка параллельного сканирования в `app/database/repository.py`: при одновременном вызове `/scan` и фонового `scan_all` возникал конфликт уникальности по `fingerprint`. Обернуто в транзакционные сейвпоинты `begin_nested()`.
2. Добавлен тест `tests/test_upsert_race.py` (164 теста проходят успешно).
3. Приложение собрано и запущено в контейнере Docker (`repo-app-1`).
4. Настроена структура операционной системы проекта `docs/PROJECT_OS/`.

## Immediate Next Steps for Incoming Model/Developer
1. Убедиться, что `docs/PROJECT_OS/` закомичен и запушен в ветку `main`.
2. Проверить логи контейнера на отсутствие сбоев планировщика:

bash
docker compose logs --tail 50 app

3. Выбрать следующую задачу из `docs/PROJECT_OS/TASKS.md` (развитие источников ATS / расширение профиля кандидата).

## Invariants to Preserve
- Никогда не трогать volumes `jobagent_v3_pg` и `jobagent_v3_files`.
- Сохранять формат асинхронных тестов через `asyncio.run()`.
- Исключения из черного списка фильтруются до этапа нотификации пользователя.
