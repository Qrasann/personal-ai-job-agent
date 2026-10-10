# Known Issues

## Resolved in the current development branch
- Concurrent scheduled/manual scans could both observe a missing JobMatch and then race to insert the same `(job_id, profile_id, search_profile_id)`. `save_match` now uses an atomic PostgreSQL upsert; local deployment still needs this change delivered before the workaround is no longer necessary.

- work_permit, relocation_package and immigration_support are not separate Job columns yet; v3.5.2 infers them conservatively from vacancy text.
- Source/country priority affects processing order, not Recommendation Model v2 score yet.
- City priority exists in the preference engine but dedicated Telegram city-priority buttons are pending.
- Country picker is limited to data/countries.yaml.
- Only implemented adapters actually scan; future registered sources still need collectors.
- Full CI and live Telegram smoke tests are required before merge.
