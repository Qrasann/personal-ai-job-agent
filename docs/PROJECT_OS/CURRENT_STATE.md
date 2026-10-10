# Current State

## Stable baseline
- main: v3.5.1
- baseline commit: 6f73110324fdf657f6695c25a5af540d2a94e72f
- testsbuild: experimental branch; at restart it was 11 commits ahead and 0 behind main.

## Active development
- branch: feature/v3.5.2-search-control
- target: v3.5.2 Search Control Center

## Implemented on active branch
- enable/disable implemented job sources;
- per-source priority;
- multi-country selection and country priority;
- current city + selected cities + other cities + other countries + worldwide scope;
- relocation / visa / work permit / relocation package / immigration support policies;
- policies: any, prefer, require, exclude;
- generic pre-filter and processing priority before matching;
- button-driven Telegram Search Control Center;
- backward-compatible storage in SearchProfile.settings;
- unit tests for the preference engine.

## Merge rule
main remains the stable source until full CI and manual Telegram smoke tests pass.
