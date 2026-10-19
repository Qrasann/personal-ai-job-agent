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

Common-search integration: `EmployerCareerWatchSource` reads public Greenhouse,
Lever, and SmartRecruiters feeds from the owner-reviewed employer catalog,
bounded to four concurrent requests, one page per board (provider limit 100
for Lever and SmartRecruiters; local parser cap 500), and per-board timeouts.
The custom career page uses its reviewed opening until a
stable public feed is available. Existing Collectly and Devexperts adapters
remain the sole providers for their boards to avoid a second source identity.
Each normalized ATS job retains employer/provider identity, an allowlisted
official posting URL, source location text, and a feed observation timestamp.
Country/city and hiring eligibility remain unknown; market tags and free-form
locations are not converted into legal or normalized location evidence.
Provider failures are isolated and reported as partial results. Common
repository canonical deduplication continues to apply.
