# Decisions

1. main stays on v3.5.1 until v3.5.2 passes CI and smoke tests.
2. testsbuild is reference/experimental work, not an automatic merge source.
3. v3.5.2 Search Control lives in SearchProfile.settings to avoid premature DB migration.
4. Disabled sources are never collected.
5. Country/source priority changes processing order; it does not fake technical fit.
6. prefer never removes a vacancy; require/exclude are explicit hard gates.
7. Unknown geography is not silently discarded.
8. Structured relocation flags are preferred; conservative text heuristics fill missing work-permit/package/support signals.
9. Repository + tests + PROJECT_OS must be sufficient for another developer or AI to continue.
10. Never fabricate candidate experience or silently auto-apply externally.
