# Known Issues

- work_permit, relocation_package and immigration_support are not separate Job columns yet; v3.5.2 infers them conservatively from vacancy text.
- Source/country priority affects processing order, not Recommendation Model v2 score yet.
- City priority exists in the preference engine but dedicated Telegram city-priority buttons are pending.
- Country picker is limited to data/countries.yaml.
- Only implemented adapters actually scan; future registered sources still need collectors.
- Full CI and live Telegram smoke tests are required before merge.
