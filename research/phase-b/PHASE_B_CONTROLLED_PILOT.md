# PHASE B — CONTROLLED PILOT

## Decision

**Status: PASS**

The controlled pilot demonstrates that one data model can represent five materially different publisher reporting practices without presenting them as one universal revenue metric. The canonical dataset contains 41 observations: 35 `OFFICIAL_REPORTED` observations and 6 `DERIVED_FROM_OFFICIAL` observations. It remains below the 50-observation ceiling.

The pilot is limited to Goddess of Victory: NIKKE, Stellar Blade, Lineage M, Black Desert IP, and MARVEL Contest of Champions. It contains no quantitative Sensor Tower, AppMagic, Nexon, Lineage 2M, or Lineage W records.

## Pilot series

| Series | Entity | Evidence | Quarters | Metric handling |
| --- | --- | --- | ---: | --- |
| Goddess of Victory: NIKKE | IP | `OFFICIAL_REPORTED` | 8 | Stable SHIFT UP IP-revenue definition |
| Stellar Blade | IP | `OFFICIAL_REPORTED` | 8 | Stable IP metric; PC launch stored as event context |
| Lineage M legacy v1 | Game title | `OFFICIAL_REPORTED` | 6 | Ends at 2025Q4 |
| Lineage M royalty-integrated v2 | Game title in IP-revenue presentation | `OFFICIAL_REPORTED` | 5 | Separate 2025Q2–2026Q2 window; three quarters overlap v1 |
| Black Desert | IP | `OFFICIAL_REPORTED` | 8 | PC, console, and mobile remain aggregated |
| MARVEL Contest of Champions | Game title | `DERIVED_FROM_OFFICIAL` | 6 | Official total revenue × rounded official title share |

Lineage M has two metric versions but remains one pilot game series. The unique key includes metric-definition identity, so overlapping quarters do not collide.

## Model result

- Entity types are explicit: `COMPANY`, `GAME_TITLE`, `GAME_EDITION`, `IP`, `FRANCHISE`, and `PLATFORM`.
- All four companies use verified calendar-aligned fiscal quarters in this window. Exact start and end dates are stored rather than inferred from labels at analysis time.
- Original values and units remain intact. The only normalization is deterministic KRW or KRW billion to KRW million scaling.
- Direct and derived evidence coexist without sharing an evidence class.
- Cross-company amounts are not directly comparable by default. No leaderboard is produced.
- Change features run only inside a compatible metric version. The first Lineage M v2 row has `METRIC_VERSION_BREAK` rather than a cross-version QoQ change.

## Lineage M break

The legacy mobile-title chart reports 2024Q3–2025Q4. The 2Q26 presentation states that royalties are integrated into IP revenue and presents a five-quarter 2025Q2–2026Q2 window. The three overlapping quarters have different values and different metric IDs. They are not averaged, overwritten, or stitched.

## Derived-value test

For MCOC, each quarter retains the official consolidated-revenue denominator, official whole-percent title share, point estimate, formula, and a compatible share interval based on ±0.5 percentage point. Decimal arithmetic and outward two-decimal rounding are deterministic. The derived rows are never labeled `OFFICIAL_REPORTED`.

## Event and claim layers

Six official events cover four pilot entities: NIKKE's 3.5th anniversary, Stellar Blade's PC launch, two Lineage M updates, and two Black Desert updates. Two issuer explanations are stored separately as attributed claims. Events establish temporal context only.

## Provenance and public release

Fifteen necessary official PDFs are retained for deterministic reconstruction. Their combined size is 10,855,955 bytes. Each has a SHA-256 hash. Six event pages are retained only as canonical official URLs. The public-safe table excludes local paths, hashes, copied slides, charts, and raw files.

No OCR, bar-height inference, private APIs, login bypass, paid source, or third-party PDF mirror was used.

## Phase boundary

Phase C is not started. The corpus is not expanded, findings are not produced, and no frontend or visual design is created.

`STOPPED BEFORE PHASE C`
