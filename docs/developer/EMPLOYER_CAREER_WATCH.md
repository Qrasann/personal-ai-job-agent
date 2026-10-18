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

Current integration boundary: this checkpoint establishes a validated catalog
and reproducible official-source freshness check. New multi-employer jobs are
not yet ingested. The next gate is to normalize selected current entries through
the existing source pipeline, retaining employer/provider identity and using
the existing canonical fingerprint so an equivalent Telegram post deduplicates
against the official posting. Existing single-company adapters remain unchanged
until that path has regression coverage.
