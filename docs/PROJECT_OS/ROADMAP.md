# Roadmap

## v3.5.1 — Search Quality & Telegram UX
Stable baseline on main.

## v3.5.2 — Search Control Center
- source include/exclude and priority;
- city/country scope and priority;
- work-mode controls;
- relocation, visa, work permit, relocation package, immigration support;
- current / desired / minimum salary controls;
- blacklist refinements;
- review testsbuild and port only useful work cleanly.

## v3.5.3 — Fast Scan & Scan Dashboard
- cheap prefilter;
- bounded concurrency;
- cache/reuse;
- source timing and timeouts;
- cancellation;
- persistent scan and control panels;
- applicant/competition signals where available (audited 2026-10-11; current
  public feeds do not expose per-vacancy applicant counts).

## v3.5.4 — Multi-Source Discovery & Source Intelligence
- employer career sites;
- Greenhouse, Lever, Ashby, SmartRecruiters, Workable;
- Telegram as first-class source;
- Habr Career, RemoteOK, HH and international boards;
- source health/quality;
- canonical vacancy and cross-source dedupe.

## v3.5.5 — Candidate Import & Profile Sync
- [x] PDF/DOCX/TXT extraction with bounded size/page/ZIP limits and no raw-file
  persistence.
- [x] Telegram preview and explicit confirmation before resume/fact writes.
- [x] Persist fact confidence/provenance; skip duplicates and flag overlaps.
- [x] Additive PostgreSQL migration and regression coverage.
- [ ] Complete owner-driven real-chat acceptance before tagging.

## v3.5.6 — Recommendation Model v2
- [x] Persist evidence-backed component breakdown per match and show it in
  Telegram vacancy details.
- [x] Keep unsupported values unknown; public competition counts and employer
  security data remain unavailable.
- [x] Preserve existing total score and thresholds until real outcome labels
  support safe calibration.
- [x] Publish and deploy v3.5.6; verify schema 4/4, polling and named volumes.
- [ ] Complete owner-driven real-chat acceptance before tagging.

## v3.5.7 — International / Remote / Relocation Intelligence
Eligibility, visa/relocation intelligence, country-specific sources and salary normalization.

## v3.6 — Resume + Vacancy Intelligence
Truthful vacancy-specific RU/EN CV adaptation and skill-gap analysis.

## v3.7 — Application Package
CV + truthful cover letter + application questions + preparation checklist.

## v3.8 — Application & Recruiter Agent
Application funnel, recruiter replies and follow-up.

## v3.9 — Interview Agent
Vacancy-specific troubleshooting and interview preparation.

## v4.x — Productization
Web UI, multi-user/multi-profession, AI Router, BYOK and monetization.
