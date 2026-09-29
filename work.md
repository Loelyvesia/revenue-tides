# Revenue Tides — Work Log

## 2026-09-22 — Phase A started

- Scope: public/free reproducibility audit only.
- Project 01 is frozen and was not modified.
- Stop boundary: no Phase B, frontend, full corpus, or findings work.

## 2026-09-22 — Phase A completed

- Gate result: `CONDITIONAL PASS`.
- Recommended design: hybrid evidence with monthly revenue rank as the longitudinal spine.
- Verified Sensor Tower public monthly article continuity: 22/22 months from 2024-11 through 2026-08.
- Exact title-level monthly amounts are sparse; public app pages are rounded current country/store snapshots and not historical series.
- Current Sensor Tower Terms make automated scraping/indexing inappropriate and leave redistribution conditions unresolved.
- Steam/PC title financials are partner-only and out of scope.
- Automated artifact validation: 15/15 PASS.
- Phase B was not started. Explicit approval and resolution of the report's conditions are required.

## 2026-09-22 — Phase A.1 completed

- Gate result: `CONDITIONAL PASS`.
- Tested five official reporting companies; four are usable for the quantitative backbone.
- Verified six exact series and one official-input-derived series; three exact series span eight consecutive quarters.
- Recommended pivot: all-games, official-disclosure-led, fiscal-quarter analysis with original currency and metric-version breaks preserved.
- Mobile-only is feasible only as a narrower Korean-publisher case study and is not the strongest evidence-led scope.
- No Sensor Tower/AppMagic values were added to the distributable candidate dataset; no raw IR PDFs or charts were retained.
- Automated artifact validation: 18/18 PASS.
- Phase B was not started. Explicit approval of the Phase A.1 scope conditions is required.

## 2026-09-22 — Phase B controlled pilot completed

- Gate result: `PASS` for the bounded five-series controlled pilot.
- Built 41 canonical observations across four reporting companies: 35 exact official and 6 derived from official inputs.
- Preserved two separate Lineage M metric versions with three overlapping quarters; no stitching or cross-version QoQ calculation.
- Retained 15 necessary official PDFs with SHA-256 provenance, totaling 10,855,955 bytes.
- Added six official event records, two attributed claims, explicit comparability rules, a public-safe release table, and deterministic rebuild scripts.
- Automated validation: 52/52 PASS; manual QA: 11/11 PASS.
- Phase C, full-corpus expansion, findings, frontend, and visual design were not started.

## 2026-09-22 — Phase C method/scope freeze completed

- Gate result: `PASS` for method version `revenue-tides-method-freeze-1.0.0`.
- Frozen the fiscal-quarter project definition, seven research questions, entity and evidence lanes, metric-version behavior, comparability, derived-value limits, missingness, event/causality language, permitted transformations, Findings admissibility, provenance, and public-release boundaries.
- Frozen corpus target at 10 analytical series, allowed range 8–12, hard maximum 12; core minimum 6 consecutive quarters and Launch Cohort minimum 4 with at most 2 launch series.
- Confirmed the five-series Phase B pilot remains compatible without changing its 41 observations or source files.
- Hashed all 18 normative Phase C Markdown documents in the machine-readable manifest.
- Automated validation: 56/56 PASS.
- Phase D, corpus expansion, Findings, visualization, and frontend work were not started.

## 2026-09-22 — Phase D curated corpus completed

- Gate result: `PASS` under frozen method version `revenue-tides-method-freeze-1.0.0`.
- Selected 9 core analytical series from 4 reporting companies: 6 direct official and 3 derived official; no Launch Cohort exception was used.
- Built 75 primary observations spanning 2024Q3–2026Q2, with 12 series-version audit rows, 26 curated official events, and 3 issuer-attributed claims.
- Evaluated 16 bounded candidates and documented 7 rejections; the target of 10 was not forced because an additional candidate would weaken evidence or breach the derived-series cap.
- Reused and hash-validated the 15 Phase B PDFs (10,855,955 bytes); no new raw binary source was downloaded.
- Automated validation: 121/121 PASS after two byte-identical canonical rebuilds; manual QA: 27/27 PASS with representative PDF pages rendered and visually inspected.
- Phase E, Findings, web-data shaping, information architecture, visualization, and frontend work were not started.

## 2026-09-22 — Phase E data quality and structural validation completed

- Gate result: `PASS` under unchanged method version `revenue-tides-method-freeze-1.0.0`.
- Reconciled 75 observations as 66 unique series-period rows plus 9 legitimate same-quarter NCSOFT metric-version overlap rows.
- Found and corrected three upstream generated-data defects without changing source observations or the frozen method: cross-series NIKKE/Stellar Blade transformations, drawdown/recovery semantics, and the conservative same-window comparability label.
- Logged 183 field-level before/after corrections; all three root errors are resolved. Zero unresolved `ERROR` or `BLOCKER` items remain. Four limitations remain as documented warnings.
- Revalidated all 18 derived observations with zero Decimal discrepancy; 9 of 15 derived period-to-period changes are sign-sensitive to rounded-share uncertainty.
- Created a 75-row findings-ready analytical layer with explicit transformation eligibility flags and no narrative Findings.
- Automated validation: 240/240 PASS, including two canonical rebuilds and a temporary clean-root rebuild. Manual QA: 34/34 PASS with official PDF pages and event sources checked.
- Phase F, Findings, web-data shaping, visualization, information architecture, and frontend work were not started.

## 2026-09-22 — Phase F evidence-bounded findings completed

- Gate result: `PASS` under unchanged method version `revenue-tides-method-freeze-1.0.0`; Findings frozen as `revenue-tides-findings-1.0.0`.
- Systematically evaluated 12 stable metric windows, 66 normalized comparison proposals, 26 event associations, 3 issuer-attributed claims, 9 reporting-version overlaps, and 15 eligible derived changes.
- Generated 19 candidate Findings, documented 13 rejections, and promoted 6 formal Findings; 3 were selected as headline Findings.
- Formal Findings cover reporting-definition effects, Stellar Blade's PC-launch quarter, NIKKE and Black Desert recovery states, Lineage W persistence under the separate v2 definition, and rounded-share uncertainty.
- Five of six Findings rely on direct official inputs; one is a derived measurement/uncertainty Finding. No sign-sensitive derived direction was promoted.
- Automated validation: 70/70 PASS after a byte-identical second analysis run. Manual Finding QA: 6/6 PASS.
- Phase G, web-data productization, IA, Signature Interaction, visual design, charts, and frontend work were not started.

## 2026-09-22 — Phase G web data productization completed

- Gate result: `PASS` under unchanged method version `revenue-tides-method-freeze-1.0.0` and Findings version `revenue-tides-findings-1.0.0`; public web-data version is `revenue-tides-webdata-1.0.0`.
- Built a 16-file, 182,030-byte public JSON/notice layer with a 7,143-byte bootstrap manifest, lightweight project and series indexes, six frozen Findings, 42 deduplicated sources, structured caveats, and nine lazy-loadable series details.
- Preserved all 9 series, 75 observations, 26 curated events, 3 attributed claims, and 6 frozen Findings without adding a company, quarter, quantitative source, Finding, normalization, or narrative trend label.
- Kept legacy and royalty-integrated Lineage observations separate, including all nine same-quarter overlap rows; cross-version QoQ remains unavailable and each metric version restarts its baseline.
- Retained point values, bounds, rounded shares, derivation references, and direction-sign stability for all 18 `DERIVED_FROM_OFFICIAL` observations.
- Reproduced every frozen Finding number from public web data and validated the public Finding → observation → metric version → source and Finding → event/claim → source chains.
- Canonical, second, and temporary clean builds were byte-identical. Automated validation: 90/90 PASS; manual QA: 31/31 PASS.
- Phase H, information architecture, Signature Interaction, visual design, charts, frontend code, and dependency installation were not started.

## 2026-09-23 — Phase H IA, visual system, and Signature Interaction completed

- Gate result: `PASS` under unchanged method version `revenue-tides-method-freeze-1.0.0`, Findings version `revenue-tides-findings-1.0.0`, and web-data version `revenue-tides-webdata-1.0.0`.
- Defined the Tidal Ledger / 潮汐账本 visual concept and the Quarter Prism / 季度棱镜 Signature Interaction.
- Specified the S0–S6 narrative architecture, Finding encounter order, nine-series Observatory, evidence/source access, loading and failure states, and cross-company comparison guardrails.
- Designed Quarter Prism states for direct observations, same-quarter version overlap, derived uncertainty, event context, metric-version boundary, and mobile stacked decomposition.
- Defined accessible color/type/grid/data-mark tokens, responsive behavior at 1440/1280/1024/768/390/320, keyboard and non-drag paths, reduced motion, and 44 px touch targets.
- Created 14 static experience wireframes and 6 Signature state SVG prototypes. All 20 SVGs parsed and rendered successfully for local visual QA.
- Mapped all six frozen Findings to required data structures and visual treatments; F1/F2/F4 remain the headline set.
- Visual independence audit classified generic dashboards, trading interfaces, Project 01, Earthquake Pulse, Cyclone Eye, and Temperature Earth as `DISTINCT`; no unresolved design `RISK` remains.
- Automated validation: 78/78 PASS. Manual design review: 40/40 PASS across 1440, 1024, 768, and 390 concepts.
- No method, Finding, web data, series, quarter, or source changed. No `package.json`, `src/`, Vue/Vite, frontend dependency, production component, production chart, or Phase I work was created.

## 2026-09-23 — Phase I frontend implementation completed

- Gate result: `PASS` under unchanged method, Findings, and web-data versions.
- Built a static Vue 3 + TypeScript + Vite narrative application with all S0–S6 sections, nine-series Observatory, six frozen Finding chapters, and the Tidal Ledger visual system.
- Implemented Quarter Prism with direct, same-quarter version overlap, version-boundary, derived uncertainty, event-context, issuer-attribution, empty-event, and mobile stacked states.
- Added previous/next, native select, direct quarter buttons, Left/Right keyboard navigation, `aria-live` summaries, reduced motion, accessible SVG descriptions, visible focus, and 44 px controls.
- Kept Phase G as the only frontend research source through a deterministic, hash-validated `data/web/` → `public/data/` sync; shared bootstrap, source registry, and per-series files load in separate stages with retry and in-memory caching.
- Reproduced all frozen Finding numbers and preserved entity type, evidence class, metric versions, derived bounds/sign stability, event non-causality, issuer attribution, and source traceability.
- Browser implementation checks passed at 1440, 1024, 768, and exact 390 × 844 after correcting one detected mobile select overflow; final checks reported no horizontal overflow and no console errors.
- TypeScript: PASS. Vitest: 62/62 PASS. Production build: PASS; main JS 107.29 KB and CSS 26.78 KB uncompressed.
- Automated Phase I validation: 100/100 PASS. Manual implementation QA: PASS across workflows A–H.
- No deployment or Phase J work was performed. Stop boundary: `STOPPED BEFORE PHASE J`.

## 2026-09-24 — Phase J final browser QA completed

- Gate result: `PASS` under unchanged method, Findings, web-data, and Tidal Ledger design freezes.
- Tested the production `dist` over HTTP in system Chrome 153, Edge 149, and Firefox 156; Chrome/Edge passed 40/40 smoke checks each and Firefox passed 14/14 WebDriver BiDi checks.
- Audited 1440×900, 1280×800, 1024×768, 768×1024, exact 390×844, and 320×700; every required viewport reported 0 px page-level horizontal overflow.
- Quarter Prism direct, overlap, version-boundary, derived uncertainty, event/no-event, mobile, keyboard, reduced-motion, hash, source, failure/retry, and cache paths passed without semantic regression.
- Console errors, warnings, uncaught exceptions, unexpected required 4xx/5xx, and required JSON failures were zero. The one blocked request was deliberate and recovered by retry.
- Root static hosting and a temporary `/revenue-tides/` subdirectory build passed; no deployment occurred.
- Final production bundle remains JS 107.29 kB / 40.27 kB gzip, CSS 26.78 kB / 5.71 kB gzip, and HTML 0.91 kB.
- Vitest: 62/62 PASS. Browser smoke: 94/94 PASS plus 40/40 subdirectory checks. Phase J automated validation: 102/102 PASS. Manual browser QA: 10/10 PASS.
- No production/frontend or frozen-data fix was required. No Phase K work was started. Stop boundary: `STOPPED BEFORE PHASE K`.

## 2026-09-24 — Phase K competition materials, final audit, and freeze completed

- Gate result: `PASS`; Project 02 status is `COMPLETE / FROZEN` at release `revenue-tides-release-1.0.0`.
- Preserved method `revenue-tides-method-freeze-1.0.0`, Findings `revenue-tides-findings-1.0.0`, Web Data `revenue-tides-webdata-1.0.0`, and data cutoff `2026-09-22` without changing research or frontend semantics.
- Completed bilingual competition summaries and abstracts, three Chinese pitch lengths plus an English pitch, 24-question Judge Q&A, reviewer and Findings guides, methodology/provenance/architecture/design notes, QA summaries, limitations, and nine selected production screenshots.
- Reproduced all six Finding number sets; retained 9 series, 75 observations, 26 events, 3 attributed claims, 18 derived observations, nine NCSOFT overlap observations, and headline set F1/F2/F4.
- TypeScript: PASS. Vitest: 62/62 PASS. Production build: PASS. Phase G isolated validation: 90/90 PASS. Phase I: 100/100 PASS. Phase J: 102/102 PASS. Final Chrome smoke: 40/40 PASS. Phase K: 110/110 PASS.
- Created final manifest, SHA-256 critical hashes, relevant-file inventory, reproducibility and structure documents, storage/language/semantic/material audits, and final freeze declaration. Deployment status remains `NOT_DEPLOYED`.
- Future changes require a new branch/version or documented amendment. Stop boundary: `PROJECT 02 COMPLETE / FROZEN`.

## 2026-09-28 — Post-freeze visual refresh 1.1 completed

- Created a local frozen baseline branch `release-1.0.0-frozen` and independent working branch `visual-refresh-1.1`; the candidate release is `revenue-tides-release-1.1.0`.
- Preserved the method, Findings, Web Data, source provenance, 9 series, 75 observations, 26 events, metric-version seams, derived uncertainty, event non-causality, and all frozen Finding wording/numbers without change.
- Rebuilt the opening as an editorial cover, converted the primer to one Measurement Grammar, made Quarter Prism the calibrated visual center, differentiated F1/F2/F4, recast the Observatory as a Research Ledger, and rebuilt mobile layouts for 390 px and 320 px.
- Added lightweight active navigation, reduced-motion-safe section reveals, more precise Prism motion, minimal source disclosure, and a Research Appendix footer while adding no framework, chart library, game art, font, or large runtime asset.
- Production screenshots: 14 after captures plus 13 frozen before captures; required desktop and 390 px visual gates were manually reviewed 12/12 PASS.
- Browser QA: Chrome 40/40 PASS, Edge 40/40 PASS, Firefox 14/14 PASS; all six required viewports have 0 px page-level overflow and console errors/warnings/exceptions remain zero.
- TypeScript: PASS. Vitest: 62/62 PASS. Production build: PASS. Phase G isolated: 90/90 PASS. Phase I: 100/100 PASS. Phase J: 102/102 PASS. Frozen Phase K isolated: 110/110 PASS.
- Candidate bundle: JS 112.07 kB / 41.66 kB gzip, CSS 40.46 kB / 8.22 kB gzip, HTML 0.91 kB. Total JS+CSS gzip increased 8.5%; CSS-only growth is documented as a non-blocking size note.
- GitHub Pages was not redeployed and no 1.1.0 tag was created. Stop boundary: `STOPPED BEFORE RELEASE 1.1 FREEZE`.

## 2026-09-29 — UI 2.0 presentation reconstruction completed

- Created the `ui-rebuild-2.0` branch and `revenue-tides-release-2.0.0` review candidate; no deployment, tag, or release freeze was created.
- Replaced the runtime presentation with a four-act narrative: The Number, The Quarter, The Findings, and The Archive, followed by Research Notes and a Research Appendix.
- Built a real-data normalized Hero field with metric versions kept as separate paths; rebuilt Measurement as five-step scrollytelling and Quarter Prism as a pinned scroll/click/select/keyboard stage.
- Rebuilt F1/F2/F4 as full-page evidence chapters, retained F3/F5/F6 as bounded research notes, and converted the Observatory to a nine-series archive with a single lazy detail pane.
- Added no UI framework, animation library, scroll dependency, chart library, image, game art, font, backend, or analytics dependency.
- Preserved frozen method, Findings, Web Data, 9 series, 75 observations, 26 events, entity types, evidence classes, version breaks, derived uncertainty, non-causal events, and all Finding wording/numbers.
- Browser QA: Chrome 15/15 PASS, Edge 15/15 PASS, Firefox production render PASS. All six required viewports reported 0 px page overflow; Chrome/Edge console errors, warnings, and exceptions were zero.
- TypeScript/build: PASS. Vitest: 62/62 PASS. Phase G isolated: 90/90 PASS. Phase I: 100/100 PASS. Phase J: 102/102 PASS. Manual UI 2.0 QA: 31/31 PASS.
- Candidate bundle: JS 113.98 kB / 43.00 kB gzip; CSS 29.80 kB / 6.94 kB gzip. Two consecutive production builds were byte-identical. Stop boundary: `STOPPED BEFORE UI 2.0 RELEASE`.

## 2026-09-29 — UI 2.0 deployed to GitHub Pages

- Published the reviewed UI 2.0 static build to `https://loelyvesia.github.io/revenue-tides/` from GitHub repository `Loelyvesia/revenue-tides` branch `main`.
- GitHub deployment commit: `78cfa0a896f10eb0fd04d109b11fed11ca0c8931`; Pages run `36513179278` completed successfully.
- Fresh production build and Vitest validation passed (62/62). Public HTTP checks passed for the page shell, hashed JavaScript, hashed CSS, and Web Data manifest.
- Online manifest verification retained Web Data `revenue-tides-webdata-1.0.0`, 9 series, 75 observations, and 6 Findings.
- Added `.nojekyll` as deployment infrastructure only. No method, Finding, research value, public data record, corpus scope, frontend dependency, release tag, or freeze version changed.
