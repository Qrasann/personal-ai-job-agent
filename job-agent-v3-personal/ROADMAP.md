# Personal Job Agent roadmap

## P0 — make the personal loop reliable

- [x] Telegram control plane
- [x] Candidate Facts
- [x] multiple CV variants
- [x] HeadHunter discovery
- [x] Russia-scoped HH search
- [x] HeadHunter apply connector
- [x] HeadHunter chat connector
- [x] forwarded Telegram vacancy ingestion
- [x] selectable target role(s)
- [x] Russia / remote / relocation switches
- [x] remote-country restriction heuristics
- [x] relocation / visa-support heuristics
- [ ] run full Docker integration test on the target Arch Linux machine
- [ ] complete HH OAuth setup and first real authorized scan
- [ ] test one manual HH application end-to-end
- [ ] test inbound HH recruiter message -> Telegram draft -> send

## P1 — improve sources

- [ ] configured Telegram channel registry and per-channel enable/disable
- [ ] Lever company career-page adapter
- [ ] Greenhouse company career-page adapter
- [ ] additional permitted international remote source(s)
- [ ] relocation-focused company/ATS discovery

## P2 — improve intelligence

- [ ] structured LLM vacancy extraction when deterministic parsing is uncertain
- [ ] work-authorization classifier with evidence snippets
- [ ] improve automatic RU vs EN CV selection
- [ ] cover-letter review buttons in Telegram
- [ ] recruiter conversation memory per application
- [ ] structured multiple-choice recruiter-bot actions where a provider exposes them

## P3 — autonomy after review

- [ ] safe allow-list for auto-apply
- [ ] safe allow-list for automatic recruiter answers
- [ ] daily digest and funnel statistics
- [ ] stale application follow-up reminders

## Later

Multi-user/SaaS, freelance marketplaces and country-local aggregators outside Russia remain extension points, but are intentionally deferred until the personal agent works reliably.
