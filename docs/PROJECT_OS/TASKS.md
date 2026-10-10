# Tasks

## v3.5.2
- [x] Search preference engine.
- [x] Source enable/disable.
- [x] Source priority.
- [x] Multi-country selection and priorities.
- [x] Multi-city scope.
- [x] Relocation/visa/work-permit/package/immigration policies.
- [x] Button-driven Telegram Control Center.
- [x] Integrate prefilter/order into scan pipeline.
- [x] Unit tests for preference engine.
- [x] Add career-first, relocation-first and balanced search strategies.
- [x] Keep career and relocation discovery queries independent.
- [x] Add Telegram strategy selection and `/relocationroles`.
- [x] Add unauthenticated Arbeitnow Germany discovery with conservative support signals.
- [ ] Add further official or public relocation sources with usable legal-work/visa evidence.
- [x] Add public Job Bank Canada discovery for international candidates; keep
  LMIA, eligibility and explicit support evidence separate.
- [x] Add opt-in independent Career-first and Relocation-first SearchProfiles.
- [x] Make one scan discover and match each active SearchProfile independently.
- [x] Preserve profile settings and matches when parallel search is disabled.
- [x] Full CI green (GitHub Actions run 102 succeeded for the Job Bank commit).
- [x] Add current/desired/minimum salary controls in Telegram; minimum feeds
  the existing per-currency scoring threshold.
- [x] Add Telegram blacklist controls with case-insensitive add/remove/clear,
  persisted across active search directions.
- [x] Compare testsbuild with main and selectively port useful behavior;
  Saved navigation already exists locally, and no broad branch merge was needed.
- [ ] Complete comprehensive Telegram acceptance in a real chat; local polling,
  dual-profile scan, and updated startup acceptance remain to be verified.
- [ ] Tag v3.5.2 after acceptance.

## Next
v3.5.3 Fast Scan & Scan Dashboard.
