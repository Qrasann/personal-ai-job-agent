# Employer Career Watcher

The curated catalog in `data/employer_watchlist.yaml` is the reviewed input for
official employer career monitoring. It is not a claim that every opening is a
candidate fit or legally accessible. Each opening keeps an exact provider ID,
official link, coarse suitability band and explicit unknown values for work
authorization, visa sponsorship and relocation unless the posting provides
separate evidence.

Run the offline schema and safety validation from the repository root:

```bash
.venv/bin/python scripts/employer-career-watch validate
```

Run the opt-in read-only freshness probe:

```bash
.venv/bin/python scripts/employer-career-watch probe
```

The probe performs GET requests only. Greenhouse, Lever and SmartRecruiters API
URLs are derived exactly from the reviewed company identifier; arbitrary API
hosts are rejected. Custom career pages are checked only at the stored official
opening URL. Redirects are not followed, credentials and nonstandard ports are
rejected, requests have per-operation and per-employer time limits, and the
probe does not write PostgreSQL, subscribe to Telegram, apply, or contact an
employer.

`advertised_count` describes the returned board page and is never a fit metric.
`current_openings` means only that the reviewed provider ID still appears in
the official public response. A changed or unavailable result requires manual
review before the catalog is refreshed; it must not silently become a confirmed
closure or eligibility refusal.

Freshness observation: the bounded read-only probe on 2026-10-19 found all
14 reviewed provider IDs current across the 12 enabled employers. This does not
change the catalog's own `verified_at` date (2026-10-18); it is a separate
dated observation and makes no claim about applicant fit or hiring eligibility.

### Betsson Group addition, 2026-10-19

The official Betsson careers page links to its public Greenhouse board. A
read-only public board/detail check found provider ID `8200701`, “Platform Core
DevOps Engineer - Infra”, location Malta, still present on 2026-10-19. The
watchlist now has 13 enabled employers and 15 reviewed openings. This role is
recorded as medium suitability; work authorization, sponsorship and relocation
remain unknown because the vacancy does not establish them. Its public ATS feed
is included in the existing bounded common-search adapter; it is not a claim
that the role is open to a particular candidate.

Common-search integration: `EmployerCareerWatchSource` reads public Greenhouse,
Lever, and SmartRecruiters feeds from the owner-reviewed employer catalog,
bounded to four concurrent requests, one page per board (provider limit 100
for Lever and SmartRecruiters; local parser cap 500), and per-board timeouts.
The custom career page uses its reviewed opening until a
stable public feed is available. Existing Collectly and Devexperts adapters
remain the sole providers for their boards to avoid a second source identity.
Each normalized ATS job retains employer/provider identity, an allowlisted
official posting URL, source location text, and a feed observation timestamp.
Only an exact, simple `City, Country` office/location label using a supported
country name can populate city/country. Remote or regional labels, multi-location
text, and ambiguous US state abbreviations remain unknown. Search-market tags
and remote eligibility are never converted into a physical work location.
An exact country-name-only ATS office label may populate country while leaving
city empty; bare country codes and the ambiguous standalone `Georgia` remain
unknown.
Hiring eligibility, sponsorship and relocation remain unknown unless separate
posting evidence supports them.

The curated Betsson record includes reviewed `betting` and `gambling` industry
tags because its posting text may omit the employer's sector. These tags remain
separate from the displayed vacancy text and flow through source-ref metadata
to the structured employer policy. Betting and casino/iGaming default to
`ALLOW`; legacy sector entries in `exclude_terms` are inert and do not suppress
Betsson. A user may still set an explicit category or exact-employer
`ALLOW`/`WARN`/`BLOCK` override through `/employerpolicy`; an exact-employer
choice has highest priority. This is source classification, not inferred
vacancy eligibility. Matching semantics are at assessment version 3; ordinary
rescans refresh rediscovered matches without bulk mutation.
Provider failures are isolated and reported as partial results. Common
repository canonical deduplication continues to apply.
