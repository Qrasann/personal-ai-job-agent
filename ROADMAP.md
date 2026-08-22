# Roadmap

## v3.3.3 — сейчас

## v3.3.3 scoring hotfix
- Исправить HH band `3–6 лет`: это stretch, а не 5+ лет.
- Stretch вакансии снова могут попасть в уведомления при пороге 65.
- `/jobs` скрывает старые low-score строки.
- RemoteOK требует meaningful role term в title/tags.

- [x] Telegram control plane
- [x] Россия + remote + relocation modes
- [x] Candidate Facts
- [x] несколько CV
- [x] HH discovery без обязательного applicant OAuth
- [x] один HH search request вместо N+1 detail requests
- [x] обработка CAPTCHA как ограничения, без обхода
- [x] «Подготовить отклик» + CV + cover letter + ссылка
- [x] RemoteOK
- [x] Telegram forwarded/channel ingestion
- [x] scoring / deduplication

## v3.3 — ближайшее

- [ ] улучшить HH scoring по данным search result без private detail API
- [ ] добавить выбранные российские источники помимо HH
- [ ] добавить curated Telegram channel collector
- [ ] international ATS: Lever/Greenhouse
- [ ] relocation parser: visa/work permit/allowed countries
- [ ] удобное редактирование search filters через Telegram buttons

## v3.4

- [ ] browser-assisted apply: только пользовательская сессия и подтверждённые действия
- [ ] остановка при CAPTCHA/anti-bot вместо обхода
- [ ] отслеживание статусов откликов там, где источник это позволяет
- [ ] recruiter/recruiter-AI conversation adapters для доступных каналов

## Later

- [ ] multi-user productization
- [ ] country-aware local markets
- [ ] freelance mode
- [ ] web dashboard

## Small-release track after v3.4.0
- v3.4.1: Candidate Fact experience types (commercial / lab / learning) + edit/delete-safe commands.
- v3.4.2: persisted RU/EN UI language and localized command aliases.
- v3.4.3: /help, /commands and /test diagnostics.
- v3.5.x: onboarding and resume import in small increments.
