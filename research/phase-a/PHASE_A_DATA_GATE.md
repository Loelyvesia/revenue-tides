# PHASE A — DATA GATE

## Decision

- **Status:** `CONDITIONAL PASS`
- **Recommended scope:** `Hybrid Evidence`, with monthly revenue rank as the longitudinal spine.
- **Phase boundary:** Phase B is **not authorized** by this result. The conditions below must be resolved and explicitly approved first.

The viable research object is:

`Game identity × observation month × store/market coverage × metric type × evidence class × source`

It is not “true global game revenue.”

## Gate answers

1. **Can we obtain a reproducible monthly historical signal?** Yes, conditionally. Sensor Tower has a public monthly article for every month from `2024-11` through `2026-08` (22/22 expected months). Top-five revenue ranks are usually textual; the remaining top-ten order is commonly chart-image-only. Acquisition must be manual and citation-led because current Sensor Tower Terms prohibit automated scraping/indexing.
2. **Strongest signal?** A hybrid led by `revenue rank` and `revenue-growth rank`, with sparse public amount estimates, official segment disclosures, and official event dates kept as different metric/evidence types.
3. **Primary source?** Sensor Tower public monthly worldwide mobile-game ranking articles, only as cited public articles and only after redistribution/terms risk is resolved.
4. **Supplementary sources?** Sensor Tower public app-page snapshots (forward snapshots only), AppMagic public reports/current charts, Tencent and NetEase investor materials, Apple/Google identity pages, and official game event pages.
5. **Historical coverage?** Continuous public article inventory for `2024-11`–`2026-08`; no public title-level exact-amount series was reconstructed.
6. **Missing platform/market coverage?** Third-party Android stores, China Android, PC, console, direct web shops, and alternative payment channels are generally excluded or unknown. China coverage in store estimates is commonly iOS only.
7. **Can official live-ops events be linked by date?** Yes for the three schema tests (Whiteout Survival, Pokémon GO, Genshin Impact), though some official microsites omit `announced_at` and local-time events need timezone-aware representation.
8. **Fully public/free?** Access cost can remain zero, but public redistribution of Sensor Tower/AppMagic service data is not yet cleared. A public project is conditional on a defensible citation/permission policy and must not mirror charts or expose a substitute commercial database.
9. **Can provenance stay small?** Yes. Even Scenario L is comfortably below roughly 200 MB without image/video archives; derived structured data is much smaller.
10. **What claims are forbidden?** Total-game-revenue claims from mobile-store estimates; publisher-segment allocation to titles; estimate-as-official wording; rank-to-dollar conversion; missing-as-zero; causal claims from temporal coincidence; and Steam revenue from owners multiplied by price.
11. **Steam/PC revenue?** Out of scope for the primary quantitative dataset. Steamworks financial reports and financial APIs require partner/financial permissions and are not public title-level sources.
12. **Proceed to Controlled Pilot?** Not yet. This gate is conditional rather than PASS.

## Source-family findings

### Sensor Tower monthly articles

- 22/22 expected months found from November 2024 through August 2026.
- Observation month and publication month differ by about one month and are stored separately.
- Top-five revenue ranks are normally available in prose.
- Ranks 6–10 are often only in images. Phase A did not bulk OCR or manually transcribe dozens of charts.
- Exact title-level monthly estimates appear only for selected titles/months; market aggregates are much more consistently textual.
- Articles explicitly exclude third-party Android markets. China is represented as iOS in market shares.
- Download estimates represent first-time downloads under Sensor Tower's stated methodology, not installs on every device or repeat downloads.
- Public articles include analyst attributions linking events to performance; those are stored only as `ATTRIBUTED_CLAIM`.

### Sensor Tower public app pages

Eight pilot pages returned public rounded “Last Month” estimates without login on 2026-09-22. The tested URLs were store/country scoped (US iOS for seven games and China iOS for the Honor of Kings China edition), not verified worldwide aggregates. Detailed historical series was not public.

Capability A — reproducible forward snapshots: **technically possible but legally unsuitable for automated collection under current Terms**.

Capability B — reconstruct past monthly observations: **not supported publicly**.

### AppMagic

- A public 2026 landscape report exposes methodology, annual title values, and 2023–2025 context.
- The report says estimates derive from Top Free/Top Grossing chart positions across countries; it covers App Store and Google Play, with China App Store only, and excludes other distribution sources.
- Public top charts expose current/selected-period ranks and several granularities, but a stable unauthenticated historical per-title quantitative series was not established.
- Detailed history/export should be treated as login/paid or ambiguous until explicitly verified.
- AppMagic is supplementary, not the reproducible primary layer.

### Official publisher / investor relations

- Tencent reported FY2025 Domestic Games revenue of RMB164.2 billion and named Honor of Kings among contributors, but did not disclose Honor of Kings revenue.
- NetEase reported FY2025 games and related value-added services revenue of RMB92.1 billion and named titles explaining change, but did not disclose title amounts.
- Official reports validate company/segment direction and terminology. They cannot be allocated to pilot games.

### Official events

The event schema worked for six sample records across three games. Exact start/end timestamps were available for some events; others exposed day-level or local-time ranges and lacked a visible announcement date. Official event pages are usable with explicit missingness and timezone fields.

### Steam / PC boundary

Steamworks documentation states that the Sales & Activations Reports portal and monthly reports are partner-facing. `IPartnerFinancialsService` requires a dedicated Financial API Group and publisher key with financial permissions. No authentication was attempted. Public Steam price and owner proxies are not revenue data.

## Temporal granularity

| Granularity | Public support | Phase A conclusion |
| --- | --- | --- |
| DAY | Official event dates; Steam financial API is private | Events only |
| WEEK | AppMagic UI can present weekly rankings | Public historical reproducibility not established |
| MONTH | Sensor Tower monthly article series; rounded current app-page snapshots | Strongest feasible longitudinal unit |
| QUARTER | Official publisher segment reports; AppMagic controls/reports | Context/validation only |
| YEAR | Annual reports and AppMagic research reports | Context/validation only |

Monthly remains the preferred commercial comparison unit, but a monthly rank observation is not interchangeable with a monthly amount.

## Scope variants

| Scope | Result | Reason |
| --- | --- | --- |
| Amount-first | FAIL | No free, reproducible, continuous title-level monthly amount series for the pilot. Current page values are rounded snapshots and detailed history is gated. |
| Rank-first | CONDITIONAL PASS | Continuous monthly public articles exist, but the reliable text layer is mostly top five and chart reuse/transcription has legal/manual limits. |
| Hybrid Evidence | CONDITIONAL PASS — recommended | Preserves monthly rank continuity while allowing sparse estimates, official segment context, and official events without pretending they are equivalent. |

## Evidence taxonomy tested

- `OFFICIAL_REPORTED`: issuer/company financial or official announcement with the issuer's metric definition.
- `INDUSTRY_ESTIMATE`: third-party modeled revenue, consumer spend, downloads, or similar estimates.
- `RANK_OBSERVED`: published rank without an exact amount.
- `EVENT_OFFICIAL`: official game/publisher event or update evidence.
- `SECONDARY_CONTEXT`: contextual reporting unsuitable as the primary quantitative source.
- `UNKNOWN`: unresolved classification.

`ATTRIBUTED_CLAIM` is stored in a separate claim table; it is not promoted to our causal conclusion.

## Conditions required before Phase B

1. Obtain a documented redistribution position for Sensor Tower/AppMagic facts, or constrain outputs to short cited summaries that do not reproduce charts, service tables, or a substitute database.
2. Confirm a manual, citation-led acquisition protocol. No scraping, private API access, login bypass, or automated chart OCR.
3. Freeze a small corpus (preferably the same eight games; never more than ten in the controlled pilot) whose textual rank coverage is sufficient for the intended comparisons.
4. Define rank missingness precisely: outside published top N must remain `NOT_PUBLISHED`, never a synthetic rank.
5. Treat public app-page estimates only as forward, timestamped, country/store snapshots unless a source explicitly supplies period bounds.
6. Curate event records manually from official sources and keep attribution separate from temporal coincidence.
7. Receive explicit user approval after these conditions are accepted. Conditional PASS does not start Phase B.

## Stop boundary

`STOPPED BEFORE PHASE B`

