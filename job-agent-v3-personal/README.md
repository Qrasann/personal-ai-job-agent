# Personal AI Job Agent v3.2

Персональный AI-агент для поиска выбранных вакансий из России: российский рынок + international remote + relocation, с Telegram как главным интерфейсом.

## Что изменилось в v3.2

Главное изменение — базовая работа больше **не требует HH applicant OAuth / HH_ACCESS_TOKEN**.

HeadHunter в этой сборке работает как discovery-source:

- один лёгкий запрос поиска вместо запроса деталей каждой вакансии;
- `area=113` для поиска по России;
- несколько выбранных ролей объединяются в один поисковый запрос;
- результаты нормализуются, дедуплицируются и проходят scoring;
- в Telegram есть кнопка **«Подготовить отклик»** и ссылка на вакансию;
- приватные HH-действия (автоотклик/чаты) по умолчанию отключены.

Важно: текущая документация HH предупреждает, что анонимный vacancy search может потребовать CAPTCHA. Агент CAPTCHA не обходит. При таком ответе HH источник сообщает об ограничении, а остальные источники продолжают работать.

## Быстрый запуск

```bash
cp .env.example .env
nano .env
docker compose up -d --build
```

Минимально в `.env` нужны:

```env
TELEGRAM_BOT_TOKEN=...
TELEGRAM_ADMIN_CHAT_ID=...
HH_USER_AGENT=PersonalJobAgent/0.2 (your-real-email@example.com)
```

`HH_ACCESS_TOKEN` для обычного запуска **не нужен**.

## Основные Telegram-команды

```text
/start
/status
/settings
/role DevOps Engineer
/roleadd Linux Administrator
/roles
/mode
/mode local on
/mode remote on
/mode relocation on
/scan
/jobs
/sources
/facts
/resumes
/chats
/pause
/resume
```

## HH workflow в v3.2

```text
HH vacancy search
      ↓
NormalizedJob
      ↓
score + dedupe
      ↓
Telegram card
      ↓
[Подготовить отклик]
      ↓
выбранное CV + сопроводительное
      ↓
[Открыть вакансию]
      ↓
ручная отправка на HH
```

Приватный HH applicant-коннектор оставлен в коде только как legacy/optional слой. Чтобы он вообще активировался, одновременно нужны:

```env
HH_PRIVATE_API_ENABLED=true
HH_ACCESS_TOKEN=...
```

Для новых установок это не предполагается и включать его не нужно.

## Международный поиск

В ядре остаются три независимых направления:

- `local_ru` — Россия;
- `remote_international` — зарубежный remote;
- `relocation` — вакансии с relocation/visa/work permit signals.

Remote-фильтр отдельно штрафует вакансии вроде `US only`, `EU only`, `must be authorized to work`, а `Remote Worldwide` получает высокий geography score.

## Проверка

В сборке есть unit-тесты:

```bash
pytest -q
```

При сборке v3.2: **18 passed**.
