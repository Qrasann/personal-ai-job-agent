# Known Issues

## Resolved in the current development branch
- Concurrent scheduled/manual scans could both observe a missing JobMatch and then race to insert the same `(job_id, profile_id, search_profile_id)`. `save_match` now uses an atomic PostgreSQL upsert and the fix passed a local scheduled/manual scan smoke test.
- Relocation discovery initially used `relocation_queries` while matching scored only career `queries`, filtering otherwise relevant broad-role results. Matching now uses the active strategy's discovery queries.
- Generic description text could be misread as a salary for non-HH sources. Notifications and details now use only structured salary values or explicit source salary/card text.

- work_permit, relocation_package and immigration_support are not separate Job columns yet; v3.5.2 infers them conservatively from vacancy text.
- Source/country priority affects processing order, not Recommendation Model v2 score yet.
- City priority exists in the preference engine but dedicated Telegram city-priority buttons are pending.
- Country picker is limited to data/countries.yaml.
- Only implemented adapters actually scan; future registered sources still need collectors.
- HH is primarily domestic and RemoteOK is tech-heavy. Arbeitnow adds Germany coverage but its current feed can legitimately contain no low-barrier role matches; additional legal-work/visa-capable country sources are still needed.
- Job Bank Canada adds international TFW coverage, but an LMIA request or
  permission to apply does not establish sponsorship or candidate eligibility.
  Initial coverage is one page, six queries and twelve details per profile;
  the five-second crawl delay adds up to about 90 seconds plus network time.
  Decimal CAD/hour salaries are preserved as source text; structured salary
  normalization and display are pending.
- Full CI is required before merge; live Telegram polling and dual-profile scan smoke tests passed on the local deployment.
