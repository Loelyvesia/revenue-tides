# Component architecture

The application is one narrative page rather than a router-driven dashboard.

| Layer | Main modules | Responsibility |
| --- | --- | --- |
| Bootstrap | `App.vue`, `data/client.ts` | Validate and load shared public JSON; coordinate section data. |
| Narrative | `OpeningSection`, `MeasurementPrimer`, `FindingChapter`, `MethodSources` | Implement S0, S1, S3, S5, and S6 in frozen order. |
| Signature | `QuarterPrismShell`, `QuarterPrism`, `EventRail` | Lazy-load a selected series; render all Prism states and input paths. |
| Exploration | `SeriesObservatory`, `SeriesDetailView`, `TideStrip` | Browse nine series and reveal one lazy detail without a page reload. |
| Evidence | `SourceList`, `CaveatKey` | Resolve deduplicated source IDs and structured caveats. |
| Domain | `types/webData.ts`, `utils/model.ts` | Strict public-contract types, grouping, formatting, resolution, and comparison guardrails. |

State remains local and composable: selected series, quarter, evidence disclosure, and lazy-load state. No global store, chart library, router, or component framework is present. Finding visuals reuse the same circle/diamond, parallel-lane, seam, interval, and separate-context grammar as Quarter Prism.
