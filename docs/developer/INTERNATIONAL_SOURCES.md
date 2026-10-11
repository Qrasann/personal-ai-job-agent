# Public international discovery

## EURES — implemented on 2026-10-11

- Public portal: https://eures.europa.eu/portal/jv-se/home?lang=en&pageCode=find_a_job
- The EURES public search endpoint is undocumented; the adapter follows the
  publicly observable portal contract. Search and vacancy details returned
  HTTP 200 during the live contract check.
- Searches the active profile's role queries and requests only vacancies with
  `euresFlagCodes=["WITH"]`. Because the endpoint can return broad/fuzzy
  matches, the adapter also requires a query token in the title.
- EURES describes the flag as an employer expression of interest in recruiting
  internationally across EURES countries. This is evidence of cross-border
  recruitment interest, not visa sponsorship, relocation support, or permission
  for a third-country national to work in the destination country.
- Stores the flag, its evidence, and source details URL; visa and relocation
  fields remain unknown. Uses application links from vacancy details when
  provided and otherwise links to the public EURES portal.
- Bounds each profile to six queries and eight detail requests. No apply or
  messaging capability is enabled. EURES member-country destinations are
  selectable in the country catalog.
- Endpoint contract reference (community-maintained, reverse engineered):
  https://github.com/rorar/EURES-API-Documentation. The European Commission's
  official portal and its vacancy record remain the data source.

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

## Armenia and Georgia — market coverage review (2026-10-11)

### Current implementation

- Georgia (`GE`) is in `data/countries.yaml`. JOBS.GE and HR.ge adapters are
  registered and included only when Georgia is a target of that search profile.
- The owner-provided latest `/scan` listed HH, Remote OK, Arbeitnow, Job Bank
  and EURES, but no Georgian sources. `/targets` previously changed only the
  first active profile, which made it easy to leave Relocation-first without
  Georgia. The updated command now applies target countries to all active
  profiles by default; `/targets relocation GE` and `/targets career GE` set a
  single profile. `/sources` displays each active profile's source plan.
- Armenia (`AM`) is not yet in the country catalog and no Armenian source
  adapter is connected. Do not present Armenia as a working search market until
  both country selection and a usable source are implemented.

### Armenia source candidates

- The Armenian Unified Social Service describes [e-work.am](https://e-work.am/)
  as a state employment platform consolidating vacancies across the country;
  its official [overview](https://social.welfare.gov.am/en/what-is-e-work)
  supports it as a candidate for a future access review. Direct portal access
  timed out during this review, and no public API or automated-access terms
  could be verified. Do not build an adapter until the public contract and
  access rules are confirmed.
- [Staff.am](https://staff.am/jobs/devops-infrastructure) has public listings
  in the requested DevOps/Infrastructure area, but its [Terms of Use](https://staff.am/en/site/terms-of-use)
  prohibit automated agents scraping, stripping or mining data without express
  written permission. No recurring collector without permission or an approved
  feed.
- [Job.am](https://job.am/jobs) publishes current local vacancies, but its
  [Terms of Service](https://job.am/terms) prohibit unauthorized reproduction,
  publication and further distribution of its materials. Do not mirror vacancy
  descriptions into the bot without permission or an approved API.
- For a supported adapter, prefer a documented public feed, a written source
  agreement, or employer career/ATS endpoints that the employer exposes for
  discovery. Preserve canonical links and collect only the fields needed for
  matching.

### Georgia source review

- A live GET of `https://jobs.ge/robots.txt` returned HTTP 410, so no crawl
  rules could be verified. A live GET of `https://www.hr.ge/robots.txt`
  returned HTTP 200 with `User-agent: *`, `Allow: /` and a sitemap URL. The
  sitemap is large (about 5.4 MB); the adapter does not download it. Robots
  guidance does not grant rights to reuse vacancy content, and no explicit
  permission for recurring extraction was verified for either board.
- The adapters now fetch one listing page and at most six matching detail
  pages per source, use a 15-second request timeout, and wait two seconds
  before each detail request. Individual detail failures preserve successful
  results; if all details fail, the scan reports a source error. Keep the
  sources limited to profiles that target Georgia and verify result quality in
  Telegram before treating them as useful.
- Scheduled scans reuse cached Georgia results for six hours. Telegram
  `/scan` explicitly forces fresh discovery for the owner's requested test.
- Role filtering ignores generic tokens such as “engineer” when a query has a
  more specific role term. HR.ge salary enters structured scoring only when a
  single supported currency and an explicit monthly period are present. Bare
  dollar symbols, annual amounts and unperiodized ranges remain source text.
- [findjobs.ge terms](https://findjobs.ge/en/terms/) welcome polite discovery by
  search engines and AI assistants, but also prohibit repeated or systematic
  reuse of substantial parts of the board without written permission. A bot
  scheduled to scan repeatedly must not use it as a recurring source without
  permission or a suitable public API.

### Eligibility and realistic relocation

- Do not infer citizenship or work rights from a candidate's current country.
  Keep location, work authorization, visa sponsorship, relocation support,
  language and salary separate, and leave unsupported fields unknown.
- For current country-specific rules, consult the official
  [Armenian employment-based residence guidance](https://migration.mia.gov.am/en/acquiring-employment-based-residence-status),
  [Georgian residence permit guidance](https://sda.gov.ge/en/products/migration-residence-permits/)
  and [Georgian labour migration law](https://www.matsne.gov.ge/en/document/view/2806732?publication=6).
  These links are references for source evidence, not a substitute for checking
  the candidate's actual status and the rules in force at application time.
