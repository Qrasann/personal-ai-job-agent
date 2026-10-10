# Public international discovery

## Job Bank Canada — implemented on 2026-10-10

- Official entrypoint: https://www.jobbank.gc.ca/findajob/foreign-candidates
- TFW context: https://www.jobbank.gc.ca/landing-tfw-international.xhtml
- Public search uses `fsrc=32` (TFW), `fglo=1` (international candidates),
  `searchstring` (active profile query), and `sort=M` (recent first).
- Search/detail HTML contracts were verified directly without authentication.
  A live `warehouse worker` query returned one vacancy open to international
  candidates with `LMIA requested`; sponsorship remained unknown.
- Canonical URLs remove session identifiers. Eligibility text, source URL,
  LMIA status and explicit offer snippets persist in JobSourceRef.raw.
- LMIA requested/approved and permission to apply are separate from employer
  visa/relocation offers. Neither implies a granted visa, a work permit,
  sponsorship, or this candidate's eligibility.
- Explicit existing-work-authorization restrictions exclude a posting from
  this international discovery adapter. Missing evidence stays unknown.
- Search Control uses adapter support signals instead of generic positive
  keyword inference for Job Bank postings. Explicit refusals override offers.
- Decimal CAD/hour salary text is preserved as `source_salary_text` and in
  posting details. It does not enter the existing integer/USD fallback;
  structured salary remains unknown until decimal/period-aware normalization.
- Public robots.txt specifies a five-second crawl delay. Requests are serialized
  across scheduled/manual scans in one process. Existing discovery cache applies.
- Initial bounded coverage: first page, at most six queries and twelve details
  per profile. Broad first queries can consume the detail budget. Healthy
  requests add up to about 90 seconds per uncached profile, plus network time.
- No automatic apply or messages. The source respects profile source controls,
  relocation mode and existing country/geography filters. Canada is now in the
  country catalog. No database migration is needed.

## Other candidates

- DWP Find a job: https://findajob.dwp.gov.uk/ — direct public search returned
  the service-error page on 2026-10-10. Do not connect until healthy search and
  details can be validated; search-engine visibility alone is insufficient.
- Workforce Australia: https://www.workforceaustralia.gov.au/individuals/jobs/search
  — candidate for a later contract/access review; no adapter implemented.
- Employer ATS feeds remain a later option; employer sponsor status must never
  be treated as a sponsorship offer for every vacancy.
