# KNOWN ISSUES & WORKAROUNDS

## 1. HeadHunter API HTTP 403 Forbidden
- **Symptom:** `api.hh.ru/vacancies` периодически возвращает статус 403.
- **Mitigation:** В коде `app/sources/adapters/hh.py` реализован автоматический fallback на открытый веб-поиск по HTML страницам `hh.ru/search/vacancy`.

## 2. Отсутствие pytest-asyncio в локальном окружении
- **Symptom:** Тесты с декоратором `@pytest.mark.asyncio` падают с ошибкой `async def functions are not natively supported`.
- **Rule:** Писать тесты через `def test_...(): asyncio.run(...)`.

## 3. Требование сетевой БД для интеграционных тестов
- **Symptom:** `test_repository_integration.py` пропускается (`skipped`), если не задана переменная `JOB_AGENT_TEST_DATABASE_URL`.
- **Reason:** Интеграционные тесты требуют реального PostgreSQL. В обычных юнит-тестах используются моки сессий.
