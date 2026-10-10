# Architecture

Pipeline:

Source adapters
→ normalized vacancy
→ Search Control prefilter/order
→ persistence/dedupe
→ matching
→ Telegram queues
→ application workflow

## v3.5.2 settings
New controls stay in SearchProfile.settings JSON while UX is still evolving:
- disabled_sources
- source_priorities
- target_countries
- country_priorities
- local_city
- selected_cities
- city_priorities
- geography
- relocation_preferences

Hard filtering only happens for explicit require/exclude choices. prefer is a soft ordering signal.

## Branches
- main: stable/releasable
- feature/*: focused development
- testsbuild: experimental legacy branch; port intentionally, never blind-merge.
