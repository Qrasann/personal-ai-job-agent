# v3.5.1 — Search Quality & Telegram UX

This release improves vacancy discovery, realistic candidate fit classification and Telegram vacancy browsing.

- Manual `/scan` performs fresh discovery; HH search covers separate role queries and multiple pages.
- Vacancies are routed into Good, Stretch and Skip lanes using seniority, experience and hard production requirements.
- Candidate commercial experience and resume-content fit are now considered without inventing experience or inflating Match Score.
- Local city, remote work and optional domestic relocation policies are configurable.
- Review, Stretch and saved queues have richer cards and Back/Next navigation.
- `/jobs` includes inline details buttons; `/start` and `/help` expose the shared command menu.
- RUB/RUR salary aliases are normalized.
- Full local baseline: 157 passed, 3 skipped.
- No database schema migration is required.

# v3.5.0 — Review & Saved workflow

Telegram review workflow now operates on the complete vacancy backlog and saved vacancies have their own browsing flow.

- `/review` shows the full notified backlog with real `N из M` position.
- Save and skip automatically continue through the full review queue.
- `/saved` shows saved vacancies ordered by match score and recency.
- Saved cards support vacancy details and next navigation.
- Equivalent title/company rows are deduplicated.
- PostgreSQL integration tests verify backlogs larger than 10 vacancies.
- No database migration is required.

# v3.4.9 — Quality foundation

This release strengthens the test and database quality foundation without changing the user-facing vacancy workflow.

- Added isolated PostgreSQL integration tests and CI PostgreSQL 16 service.
- CI now enforces branch coverage of at least 55%.
- Full suite baseline: 117 passed, total application coverage 58%.
- Repository coverage increased to 65%; Candidate bootstrap is 100% covered.
- Added mutation testing for Technical Score v2 and Candidate Facts comparison.
- Mutation baseline: 249 mutants, 240 killed, 9 equivalent/redundant, 0 meaningful survivors.
- Removed unused geo runtime code.
- Replaced deprecated datetime.utcnow usage with UTC-compatible naive timestamps.
- Simplified Candidate Fact comparison according to its CandidateFact contract.
- Added developer testing documentation.

No database schema migration is required.

# v3.4.8 — Vacancy Review Queue

Telegram gained a review queue for notified vacancies with save, skip, details and next actions.

- Added /review for notified matches.
- Added saved status and reused skipped status.
- Saved and skipped vacancies suppress duplicate repost notifications.
- Saving or skipping automatically advances the current review batch.
- Review ordering prefers higher scores and newer vacancies.
- Duplicate title/company rows are suppressed in the review queue.
- Existing vacancy details remain available from the review flow.

No database schema migration is required.

# v3.4.7 — Technical Score v2 and live scan progress

Technical scoring now uses structured required and preferred vacancy requirements together with Candidate Facts. HeadHunter vacancies can be selectively enriched with full public vacancy details and cached for reuse.

Legacy Technical scoring remains the fallback when required technical requirements cannot be recognized. Geography, salary, relocation and existing score caps remain unchanged.

Telegram `/scan` now shows live source progress, vacancy-analysis progress, a spinner and elapsed time.

No database migration is required.

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
Detailed testing, PostgreSQL integration, coverage and mutation-testing documentation: [`docs/developer/TESTING.md`](docs/developer/TESTING.md).

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
