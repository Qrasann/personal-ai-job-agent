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

## Himalayas — implemented in the v3.5.7 candidate

- Bounded remote query planning prioritizes supplied support/IT roles before
  physical-work queries. This includes the default selected customer-support
  role previously omitted by first-four truncation. It keeps original text and
  stable order within groups, never adds roles, and retains the four-query,
  three-market, daily-cache bounds. Country eligibility remains separate.

- Source `expiryDate` is now preserved in bounded `raw.availability` metadata
  and displayed as UTC listing expiry on /job. Primary references describe
  epoch seconds/milliseconds and timezone-aware ISO; invalid/ambiguous values
  stay unknown. Cached cards re-evaluate expiry at display time. This is not an
  employer deadline, hiring-status confirmation, or work-eligibility claim.
  Existing persisted source refs gain metadata only on their normal refresh;
  no schema or request-frequency change.

- Official API reference: https://himalayas.app/docs/remote-jobs-api and
  https://himalayas.app/api. The provider documents a public JSON search API
  with role, ISO country and worldwide filters; no authentication is required.
- The provider limits each request to 20 jobs, applies an unspecified rate
  limit, and refreshes its data once per day. The adapter uses at most four
  active-profile role queries and three selected markets, requests one recent
  page per query/market, serializes calls with a short delay, and keeps a
  24-hour discovery cache. It does not paginate or mirror the whole board.
- The API says an empty locationRestrictions array means worldwide. Explicit
  country limits are retained only when they match the selected target market;
  an absent restrictions field stays unknown. A worldwide label does not
  establish candidate work authorization, employer payroll, or tax handling.
- Salary values retain their stated currency and pay period; Telegram labels
  hourly, weekly, fortnightly, monthly and annual amounts explicitly. The
  adapter links to the Himalayas listing and displays Himalayas attribution, as
  required by the provider. It does not submit applications.
- API responses have been inspected through the official live browse endpoint.
  The rebuilt startup scan made filtered GE and AM requests and both returned
  HTTP 200; Telegram confirmation of parsed result counts and card rendering is
  still pending. The candidate has parser, request-bound, daily-cache,
  market-scope, source-attribution and unknown-eligibility regressions.

## Remotive — implemented in the v3.5.7 candidate

- Official public category RSS feed: https://remotive.com/remote-jobs/devops/feed.
  The [RSS feed documentation](https://github.com/remotive-com/remote-jobs-feed)
  lists category-specific feeds and shows the expected RSS/XML fields. The
  [public API documentation](https://github.com/remotive-com/remote-jobs-api)
  and terms say developers may share listings, must link to Remotive and show
  attribution, must not submit listings to third-party job websites, and may
  not display jobs to collect signups or email addresses.
- The API's documented filters returned the same 18-job general feed for
  `category=devops`, `category=Devops`, and `category=software-development` in
  the Oct 12 runtime check. The adapter now uses the official Devops category
  RSS feed and parses at most 250 entries, with one shared refresh every 24
  hours. A single response is shared between Career-first,
  Relocation-first, and active users; the existing `runtime_state` table keeps
  the response across app restarts. `/scan` does not force a Remotive refresh.
  The 2026-10-12 runtime check returned a valid RSS document with channel
  metadata but no job entries; both profiles correctly parsed zero. This is
  currently an empty-provider response, not evidence that the source has jobs.
- Every vacancy uses the Remotive-hosted source URL and the `/jobs` list displays
  Remotive by name, including when the same canonical posting also appears on
  Himalayas. The source performs discovery only; it does not apply or message.
- `candidate_required_location` stays visible as remote scope. Explicit country
  lists that exclude the selected market and clear `Only` restrictions without
  a selected-country match are filtered. Region labels are not converted into
  country eligibility, and missing location stays `unknown`. Remote scope does
  not establish work authorization, employer hiring eligibility, visa
  sponsorship, payroll/tax availability, or relocation support.
- Salary is preserved as source text and is not parsed into a numeric salary.
  Response parsing is limited to the documented Devops category and
  the profile's role queries. The adapter is covered for malformed payloads,
  source URLs, country scope, daily caching across profiles and restarts,
  attribution, and disabled application capabilities.

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
- A single transport retry remains bounded. Request starts are separated by
  at least five seconds, including retries; a slow response consumes the
  interval so it does not incur an extra full delay. If one search
  query or vacancy detail exhausts its retries, discovery continues with the
  remaining work and keeps successfully verified vacancies. The source reports
  an error when every search fails or every requested detail fails; HTTP status
  errors are not treated as transport retries and remain visible failures.
- Initial bounded coverage: first page, at most six queries and twelve details
  per profile. Broad first queries can consume the detail budget. For 18 fast
  requests, the minimum start interval can account for about 85 seconds before
  network time; slow responses consume part or all of that interval.
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
- Armenia (`AM`) is selectable in the v3.5.7 candidate. That candidate also
  connects the public Lineate Greenhouse board for profiles targeting `AM` or
  `GE`; only roles whose title and explicit location match are returned. The
  live match confirmed so far is one Infrastructure Engineer role for a
  Georgian office. This is narrow employer coverage, not general Armenian job
  board coverage; no Armenian-targeted vacancy has yet matched the current
  DevOps/Infrastructure queries.

### Armenia source candidates

- The Armenian Unified Social Service lists both [e-work.am](https://e-work.am/)
  and [workforall.am](https://workforall.am/) as its vacancy information
  platforms on its current [labor-market page](https://social.welfare.gov.am/labor-market-situation-in-armenia).
  The official [e-work overview](https://social.welfare.gov.am/en/what-is-e-work)
  says it consolidates vacancies and enables employer/jobseeker matching.
- Direct browser checks of the public e-work search and workforall vacancy
  pages timed out. No documented public API, feed, or automated-collection
  terms were found in the official material reviewed. The government
  [jobseeker registration guidance](https://social.welfare.gov.am/en/registration-of-job-seekers-1)
  requires a Public Services Number or national eID for online registration;
  foreign nationals using the in-person service need a residence card. This
  does not establish whether anonymous vacancy browsing is possible, but it
  means neither portal is yet verified as a pre-move foreign-candidate service.
  These are registration requirements for the state service; they do not
  establish a general prohibition on applying directly to employers.
- The Migration and Citizenship Service's [workpermit.am FAQ](https://workpermit.am/en/faq)
  displays “How to find a job using this Platform?”, but the answer is not
  present in the public page response. Its [official user guide](https://workpermit.am/files/Platform_User_Guide.pdf)
  documents an employer-led flow: the employer registers and submits a vacancy,
  then enters the selected foreign worker's information; the platform creates
  that worker's account afterward. This confirms the foreign-hire workflow, not
  anonymous vacancy discovery or an authorized feed.
- Defer automated integration of the government portals. A cold email to the
  Unified Social Service (`info@socservice.am`) is not a prerequisite for the
  current release; revisit only if direct access becomes necessary and a
  relevant feed or authorized route is plausible. No country adapter should
  imply that an unverified portal is searchable by the bot.
- [Staff.am](https://staff.am/jobs/devops-infrastructure) has public listings
  in the requested DevOps/Infrastructure area, but its [Terms of Use](https://staff.am/en/site/terms-of-use)
  prohibit automated agents scraping, stripping or mining data without express
  written permission. Treat it as a manual search destination; no recurring
  collector without permission or an approved feed.
- [Job.am](https://job.am/jobs) publishes current local vacancies, but its
  [Terms of Service](https://job.am/terms) prohibit unauthorized reproduction,
  publication and further distribution of its materials. Treat it as a manual
  search destination; do not mirror vacancy descriptions into the bot without
  permission or an approved API.
- [CareerCenter.am](https://careercenter.am/en/jobs) has current Armenia
  listings, including infrastructure and technical-support roles. Its
  [posting rules](https://careercenter.am/en/posting-rules) expressly prohibit
  copying or further disseminating vacancy information to other public sources
  without prior written consent. Keep it as a manual-search destination; do
  not connect a recurring adapter without written permission or an approved
  feed.
- [Worknet.am](https://worknet.am/en) is another live Armenia job board listed
  by Relokatz. Its automated-access and reuse terms have not been verified;
  treat it as a manual-search candidate until those terms and a permitted feed
  are checked.
- [ITA Jobs](https://jobs.ita.am/) is a free IT Association of Armenia
  directory that says it collects openings from employer and academy pages and
  links users to the original application page. Its public terms/privacy page
  does not document a reusable API. Keep it as a direct, manual-search link;
  validate each opening on the employer's page.
- In the 2026-10-12 review, the [Findjobs.ge home page](https://findjobs.ge/en/)
  advertised local, remote, and no-experience categories and linked its current
  [Terms of Use](https://findjobs.ge/en/terms/), updated 2026-09-27. The terms
  welcome search engines and AI assistants but prohibit repeated/systematic
  extraction or reuse of substantial parts of the board without written
  permission. It is therefore a manual link in the bot, not a recurring
  collector. Its listing summaries and labels are leads only; verify the
  original posting, employer, salary period, expiry, language and legal
  eligibility before applying.
- [LeverX Careers](https://career.leverx.com/vacancies) currently lists DevOps
  roles for Georgia, including [Middle DevOps Engineer](https://career.leverx.com/vacancies/middle-devops-engineer)
  (hybrid/remote) and [Senior DevOps Engineer](https://career.leverx.com/vacancies/devops-engineer)
  (Georgia/Albania, hybrid/remote). The postings request English B2+; they do
  not state salary, visa sponsorship, or relocation support. The portal says
  candidate CVs should be submitted through its own career site and warns that
  legitimate HR contacts use `@leverx.com`. No documented public feed/API or
  automated-reuse permission was found in this review, so keep it a manual
  search destination. Remote/work-mode labels do not prove hiring eligibility
  for a Russian citizen from a selected country.
- For a supported adapter, prefer a documented public feed, a written source
  agreement, or employer career/ATS endpoints that the employer exposes for
  discovery. Preserve canonical links and collect only the fields needed for
  matching.

### Lineate Greenhouse board — candidate integration, checked 2026-10-11

- Greenhouse documents `GET https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs`
  as its public Job Board API and says GET requests do not require
  authentication. The candidate uses the documented `content=true` GET for the
  Lineate board only; it does not submit applications or call private ATS APIs.
- The [current Lineate board](https://job-boards.greenhouse.io/lineate) lists
  an [Infrastructure Engineer opening for its Georgian office](https://job-boards.greenhouse.io/lineate/jobs/8018252).
  Its description includes SRE/DevOps, Linux and cloud-infrastructure duties.
  The country is mapped to GE from the explicit “Georgian office” location;
  city is left unknown because the listing does not name one.
- The same board lists data-engineering roles in Yerevan. They do not match the
  current DevOps/Infrastructure title queries and are excluded by the adapter's
  title filter. The feed is scoped to a profile's selected AM/GE market; it
  does not make unmatched locations eligible.
- The Infrastructure Engineer posting does not state visa sponsorship or
  relocation assistance. Those fields remain unknown. No salary is inferred
  from description text, and Greenhouse's `updated_at` value is not presented
  as a publication date.
- This is a candidate source, not proof of an individual right to work in
  Georgia. Keep current local work-right requirements separate from source
  discovery and match scoring.

### Collectly Lever Postings API — candidate integration, checked 2026-10-11

- Lever's official [Postings API support page](https://hire.lever.co/developer/support)
  describes the API as publicly accessible for published job postings. Lever's
  [official API documentation](https://github.com/lever/postings-api) documents
  JSON GET requests, `skip`/`limit` pagination, and hosted application links;
  the authenticated Lever Data API and application-submission endpoints are
  not used.
- The employer-hosted [Collectly Engineering board](https://jobs.lever.co/CollectlyInc/?team=Engineering)
  currently publishes [Senior DevOps/DevSecOps Engineer](https://jobs.lever.co/CollectlyInc/3240d98f-b916-46d4-a89e-3ae4aa988338).
  A read-only GET to `https://api.lever.co/v0/postings/CollectlyInc?mode=json`
  returned the public board and the same current posting. It states remote
  work from GMT-7 to GMT+4, infrastructure-as-code, CI/CD, cloud, monitoring,
  security, and fluency in English. It asks for a Bachelor's degree or
  equivalent experience and does not specify a minimum number of years.
- The Lever record labels its posting location Belgrade and country RS. Since
  the role is remote with an explicit timezone band that includes UTC+4, the
  adapter can surface it for selected AM/GE searches. It deliberately leaves
  normalized country/city and country-of-hire eligibility unknown; the source
  office is not treated as the only possible hiring country, and timezone fit
  does not establish payroll, tax, immigration, or work-right eligibility.
- The employer's hosted application form states that new hires must attend
  one or two weeks of onboarding in Yerevan and that the employer covers travel
  and accommodation. This is a useful potential relocation lead, but it does
  not prove that a Russian citizen can be hired or settle in Armenia. Salary
  is not stated, and no expiry/deadline is provided in the inspected public
  board record. The source API's `createdAt` is retained as metadata, not shown
  as a publication date.
- The candidate collector is limited to Collectly's public board, one page of
  at most 100 records, explicitly remote DevOps matches, and a timezone range
  covering UTC+4. It runs only when AM or GE is selected and uses a six-hour
  application cache. No general Lever-site crawling, applicant-form scraping,
  or automated application is enabled. The API documentation does not state a
  public-feed request limit; the bounded request and cache are conservative
  local policy, not a claimed vendor quota.

### Armenia employer-side foreign-hiring route — checked 2026-10-11

- The Migration and Citizenship Service's [workpermit.am portal](https://workpermit.am/en/home)
  is an official electronic system for employers to register vacancies and
  process foreign hires through the employment-based residence procedure. Its
  described flow starts with employer registration, vacancy submission and
  government review; it is not yet verified as an anonymous public vacancy
  catalogue or a documented API/feed. Do not automate its authenticated
  workflow or treat registration as a jobseeker search interface.
- The portal's FAQ includes “How to find a job using this Platform?”, but the
  publicly rendered answer was not available in the checked page. No public
  search feed or API was identified. Defer integration; contacting the
  Migration Service (`workpermit@gov.am`) is not a prerequisite for the
  current release.
- The official [employer/foreigner user guide](https://workpermit.am/files/Platform_User_Guide.pdf)
  explains that the employer creates the vacancy case and later enters the
  selected foreign worker's information, after which the worker receives an
  account. The guide does not establish a public jobseeker search or vacancy
  feed.
- The Unified Social Service says employers may post vacancies on e-work.am or
  send them in a prescribed format to `info@socservice.am`. This makes an
  authorized feed/referral request concrete, but does not itself grant the
  bot access or permission to reuse vacancy data.
- The official workpermit.am page says citizens of EAEU member states working
  in Armenia are exempt from work-permit documentation for the employment
  contract period. Candidate nationality is not established by the bot's
  current country; do not infer this status from `RU` profile location.
- The same page distinguishes the exemption from residence documentation:
  EAEU citizens may register to receive a certificate confirming lawful
  residence, but the portal says it cannot be printed without a Public Services
  Number. Do not present the work-permit exemption as automatic completion of
  residence registration.
- Add an Armenia adapter only after finding a role-relevant public discovery
  route with permitted recurring access, canonical job links, and candidate
  access before relocation. Government registration prerequisites alone do not
  prove direct employer applications are unavailable to foreign candidates.
- The Migration and Citizenship Service announced that residence-status
  applications move to a new electronic system on 2026-11-01, and the existing
  migration.e-gov.am and Early One channels stop accepting those applications.
  Recheck the new official workflow before giving the owner a post-arrival
  checklist or relying on an old guide.

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
- Georgia's consolidated [Labour Migration Law](https://matsne.gov.ge/en/document/view/2806732)
  now includes changes effective 2026-03-01: paid work for a local employer by
  an alien without permanent residence requires a right to work obtained via
  the local employer after an employment agreement. The subsequent visa or
  work-residence steps depend on whether the worker is outside Georgia or
  already there. The law has a separate exception from those follow-up
  immigration-document steps for work performed completely remotely when the
  worker need not enter Georgia; do not interpret that as a general right to
  take local Georgian employment without checking the worker's case.
- Georgia's [official work-residence guidance](https://sda.gov.ge/en/products/migration-residence-permits/)
  also lists employer-turnover and minimum-income documentation. This is a
  practical feasibility signal for local employment, not a bot-side legal
  determination.
- For current country-specific rules, consult the official
  [Armenian employment-based residence guidance](https://migration.mia.gov.am/en/acquiring-employment-based-residence-status),
  [Georgian residence permit guidance](https://sda.gov.ge/en/products/migration-residence-permits/)
  and [Georgian labour migration law](https://www.matsne.gov.ge/en/document/view/2806732?publication=6).
  These links are references for source evidence, not a substitute for checking
  the candidate's actual status and the rules in force at application time.

## SmartRecruiters / Devexperts — curated GE feed, 2026-10-13

- Official public API: https://developers.smartrecruiters.com/reference/v1listpostings
  and authentication docs https://developers.smartrecruiters.com/docs/authentication.
  Public Posting API GETs need no credentials; apply endpoints are not used.
- Curated Devexperts company only, country=ge, destination=PUBLIC; one page max 100
  and ten role-matching unique details. GE must be current/selected; no AM scope
  or role injection. Source preferences/disable controls and six-hour cache apply.
- Request 10s / total 60s; one transport retry, no status-response retries; strict
  numeric IDs and trusted posting URLs. Keep partial verified usable results on
  later detail failure or own timeout; propagate external cancellation.
- Live adapter check found one Application Support Engineer Level1 in GE/hybrid.
  Publication releasedDate is preserved; no closing/application deadline inferred.
  Structured hybrid/GE-only remote stays scoped. General perks/foreign-language
  classes do not imply sponsorship, relocation or individual hiring eligibility.
- Listing/details evidence is stored in existing source-ref JSON; salary and
  legal/support signals remain unknown without explicit direct source evidence.
  Read-only discovery capabilities; no applications, messaging or employer contact.
