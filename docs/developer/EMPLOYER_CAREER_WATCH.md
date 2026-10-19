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

Common-search integration: `EmployerCareerWatchSource` exposes the 14 entries
in the owner-reviewed catalog to the existing scan pipeline. Each normalized
job retains employer/provider identity, official URL, source location, and the
catalog verification date. Country/city and hiring eligibility remain unknown
unless supported by posting evidence. The adapter does not claim freshness
beyond the catalog's `verified_at` date and does not alter existing single-
company adapters. Canonical job deduplication remains the repository's existing
cross-source behavior.
