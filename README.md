# v3.4.6 — Telegram UX and requirement classification

Telegram supports multiple commands in one message, one command per line:

```text
/version
/facts
/compare 24
```

Commands execute sequentially, so state-changing commands finish before the next command runs.

Vacancy comparison now separates technical signals into required, preferred and other/unknown groups.
Candidate experience remains independently classified as commercial, lab, learning, unknown or missing.

Temporary Telegram API network failures during startup are retried with capped backoff.
Manual Docker runtime control remains unchanged.

The existing Technical score and notification threshold are unchanged in this release.

# v3.4.5 — Candidate Facts vacancy comparison

Vacancies can now be compared with Candidate Facts using `/compare <id>` or the **🧩 Сравнить с профилем** button.

Experience remains truth-aware: `commercial`, `lab`, `learning`, `unknown`, and `missing`. Lab and learning experience is never presented as commercial experience.

```text
/jobs
/job 24
/compare 24
```

Coverage currently represents recognized technical signals; required vs nice-to-have classification will be added separately.

# v3.4.4 — Vacancy details

Telegram now keeps `/jobs` compact but makes each match inspectable with `/job <id>` or the **📋 Подробнее** button. HH details are fetched only when requested from the ordinary public vacancy page; scheduled discovery still uses the lightweight search page and never attempts to bypass CAPTCHA. Source vacancy text and Job Agent scoring are shown as separate sections.

```text
/jobs
/job 25
```

# v3.4.2 — CI foundation

GitHub Actions now validates every push to `main`, `feature/**`, `fix/**` and every pull request to `main`. The pipeline compiles Python sources, runs pytest, performs a lightweight secret scan across Git history, and verifies that the Docker image builds. A `.dockerignore` keeps `.env`, `.venv`, Git metadata and runtime data out of the Docker build context.

Local development checks:

```bash
python -m pip install -r requirements-dev.txt
python -m compileall -q app tests
python -m pytest -q
./scripts/secret-scan.sh
docker build -t personal-ai-job-agent:local .
```

# v3.4.1 — Candidate Fact types

Candidate Facts now distinguish `commercial`, `lab`, `learning`, and `unknown`. Existing commercial flags are preserved; legacy non-commercial facts are intentionally left `unknown` until the user classifies them. Search/scoring behavior is unchanged.

```text
/facts
/fact add <text>
/fact type <id> commercial
/fact type <id> lab
/fact type <id> learning
/fact type <id> unknown
```

# v3.4.0 — Storage foundation

This is a deliberately small release on top of v3.3.3. It adds safe in-place database schema versioning, persistent file storage for future resume imports, soft-delete metadata fields (not yet exposed in the UI), and `/version`. Search/scoring behavior is intentionally unchanged.


## v3.3.3 scoring fixes

- HH `3–6 лет` is treated as a stretch band, not as an explicit 5+ years requirement.
- Stretch roles can cross the default notification threshold; senior/lead and explicit 5+ requirements remain capped.
- `/jobs` hides stale rows below the current `notify_min_score`.
- RemoteOK discovery ignores generic words like `engineer` and requires meaningful role terms in title/tags.

# Personal AI Job Agent v3.3.3

Персональный AI-агент для поиска выбранных вакансий из России: российский рынок + international remote + relocation, с Telegram как главным интерфейсом.

## v3.3.2 — очистка ленты перед подключением LLM

- `/status` показывает реальную версию из файла `VERSION`;
- `/scan` показывает, сколько вакансий дал каждый источник, сколько прошло фильтр и сколько уведомлений отправлено;
- senior/lead/старший/ведущий вакансии в fallback-режиме ограничиваются по score и не попадают в обычную ленту;
- требования 3–4 года считаются stretch, 5+ лет — высоким опытом;
- crypto/blockchain/web3 — мягкий risk penalty для ручной проверки, а не выдуманный hard-ban;
- HH web parser сохраняет весь текст карточки, чтобы видеть seniority/experience, которые HH размещает вне snippet;
- одинаковые `title + company` больше не повторяются в `/jobs`, а повторные repost-уведомления подавляются.


## Что изменилось в v3.3.2

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
/job <id>
/compare <id>
/sources
/facts
/resumes
/chats
/pause
/resume
```

## HH workflow в v3.3.2

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

При сборке v3.3.2: **18 passed**.

## v3.3: HH public-web fallback

If anonymous `api.hh.ru/vacancies` returns HTTP 403, the personal build can fall back to the ordinary public HH search page (`hh.ru/search/vacancy`) and parse the server-rendered vacancy cards. This fallback is discovery-only, rate-limited by the existing HH cache, and never attempts to solve or bypass CAPTCHA. If the web page itself requests verification, HH discovery stops and the bot reports the problem.

Environment controls:

```env
HH_WEB_FALLBACK_ENABLED=true
HH_WEB_MAX_PAGES=1
HH_WEB_USER_AGENT=Mozilla/5.0 (X11; Linux x86_64; rv:154.0) Gecko/20100101 Firefox/154.0
```

## v3.3.2 hotfix

HH web fallback no longer treats a harmless `captcha` string embedded in normal HH JavaScript as an active CAPTCHA page. A real challenge is detected from the final captcha URL or explicit verification text when normal vacancy-serp markers are absent.


## Проверка v3.3.3

`pytest`: **27 passed**. `compileall`: OK.
