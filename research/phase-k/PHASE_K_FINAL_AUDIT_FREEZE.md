# PHASE K — COMPETITION MATERIALS / FINAL AUDIT / FREEZE

## Decision

**Status: PASS**  
**Final status: COMPLETE / FROZEN**  
**Release:** `revenue-tides-release-1.0.0`  
**Freeze date:** `2026-09-24`  
**Deployment:** `NOT_DEPLOYED`

## Frozen versions

- Method: `revenue-tides-method-freeze-1.0.0`
- Findings: `revenue-tides-findings-1.0.0`
- Web Data: `revenue-tides-webdata-1.0.0`
- Data cutoff: `2026-09-22`

## Final data and Findings

The final project contains 4 publishers, 9 analytical series, 75 observations, 26 curated official events, 3 issuer-attributed claims, and 18 derived observations from 2024Q3–2026Q2. All 9 legitimate NCSOFT same-quarter version overlaps remain separate. Six formal Findings reproduce from public web data; F1, F2, and F4 remain the headline set.

F1 retains the KRW 6.797–13.455 billion definition difference. F2 retains KRW 7.012 → 65.719 billion and +837.3% with PC launch as same-quarter context only. F3 retains +32.4% and 4.1% below peak. F4 retains 20.7% initial drawdown, three-quarter recovery/new peak, and 30.8% endpoint drawdown. F5 remains limited to Lineage W royalty-integrated v2 and 35.3%. F6 retains 9/15 sign-sensitive changes and 60.0%.

## Design and frontend

Quarter Prism / 季度棱镜 remains the signature interaction and Tidal Ledger / 潮汐账本 remains the visual system. The static Vue 3 + TypeScript + Vite site consumes the Phase G data layer only. Metric versions, derived bounds, entity types, event separation, claims, caveats, and source routes remain visible. No production source or research data changed during Phase K.

## QA

- TypeScript: PASS
- Vitest: 62/62 PASS
- Production build: PASS; JS 107.29 kB / 40.27 kB gzip, CSS 26.78 kB / 5.71 kB gzip, HTML 0.91 kB
- Phase G isolated-boundary validation: 90/90 PASS
- Phase I validation: 100/100 PASS
- Phase J validation: 102/102 PASS
- Final Chrome 153 release smoke: 40/40 PASS at the complete scripted route, including 1440×900 and 390×844
- Phase K validation: 110/110 PASS
- Manual final review: 12/12 PASS

Chrome 153, Edge 149, and Firefox 156 remain the tested production browsers. WebKit/Safari-equivalent and a real interactive screen-reader session were unavailable and remain explicit limitations.

## Competition package

The package includes bilingual project summaries and abstracts, short/long descriptions, Chinese 30-second/90-second/3-minute scripts, an English pitch, reviewer route, 24-question Judge Q&A, Findings guide, methodology, provenance, architecture, Quarter Prism and Tidal Ledger notes, accessibility/browser/performance/limitations summaries, final QA summary, and nine selected production screenshots. The design description is 119 Chinese characters, below the 300-character limit.

## Integrity, storage, and release

Method, Findings, web-data, and design hashes validate. `release/final_manifest.json`, external critical hashes, and the relevant-file inventory provide a self-reference-safe release record. No full project, `node_modules`, duplicate `dist`, raw evidence copy, or ZIP archive was added to `release/`. The project remains small outside local dependencies; retained raw evidence is 10.35 MiB and public web data is 182,030 bytes.

## Known limitations

Publisher-defined metrics remain heterogeneous and cross-company absolute ranking is forbidden. Values are not a uniform global consumer-spending measure. NCSOFT versions cannot be stitched. Derived Netmarble observations inherit rounded-share uncertainty. Events are curated, non-exhaustive, and non-causal. Observed-window non-recovery is not permanent decline. Remote source availability may change.

`PROJECT 02 COMPLETE / FROZEN`
