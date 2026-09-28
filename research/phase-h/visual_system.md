# Visual system

## Tidal Ledger / 潮汐账本

The interface combines fiscal ledger rules, hydrographic measurement ticks, calibration seams, and restrained archival annotations. “Tide” appears through repeated quarterly movement, peaks, drawdowns, recovery, and measurement marks—not ocean imagery. The composition is an analytical report sheet, not a trading terminal or SaaS dashboard.

## Palette

The exact tokens live in `design/phase-h/design_tokens.json`. Warm mineral paper is the primary surface; deep graphite carries text; muted tidal teal marks selected quantitative evidence; oxidized copper marks event context; graphite hatch and whiskers carry uncertainty. Direct/derived, versions, and events always add shape, stroke, label, and placement distinctions.

## Typography hierarchy

| Role | Treatment |
| --- | --- |
| Display title | 52 px at wide desktop, 36 px tablet, 30 px mobile; 650 weight; short line length |
| Section title | 32 / 28 / 24 px; 650 weight |
| Finding title | 24 / 22 / 20 px; 650 weight; canonical bilingual title available |
| Body | 16 px; 1.55–1.7 line-height; clean system sans |
| Annotation | 12–14 px; never below 12 px in design target |
| Source note | 12–14 px; secondary graphite, still AA contrast |
| Quarter label | 12–14 px; tabular numerals; uppercase Q retained |
| Numeric label | 16–24 px by context; tabular numerals; original currency adjacent |

System stack: `system-ui`, platform UI fonts, Segoe UI, Microsoft YaHei, sans-serif. Numerical labels may use a safe system monospace stack. No proprietary font or packaged font file is required.

## Grid and composition

- 12 editorial columns at 1280–1440, 8 columns at 768–1024, 4 columns below 768.
- Thin ledger rules organize content; whitespace separates chapters. Most sections have no enclosing card.
- The analytical canvas aligns quarter ticks, quantitative track, context rail, and evidence footer to one coordinate system.
- The reading column is capped near 720 px. The Prism may use up to 1280 px.
- Radius is 0–4 px. Shadows, glass surfaces, glossy cards, and decorative gradients are absent.

## Data-mark grammar

| Meaning | Shape | Stroke / pattern | Label | Placement |
| --- | --- | --- | --- | --- |
| Direct observation | Filled circle | Solid 2 px teal edge | `Official reported` plus metric label | Quantitative trajectory |
| Derived observation | Outlined diamond | 2 px violet/graphite outline | `Derived from official` | Centered on compatible interval |
| Uncertainty interval | Capped whisker or hatched band | Solid boundary plus diagonal hatch; no opacity-only encoding | Lower–upper bounds and rounded-share note | Same quantitative track |
| Rolling peak | Small horizontal calibration cap | Graphite 2 px | `Rolling peak` only when selected/relevant | Above the observation |
| Drawdown | Vertical bracket from peak reference to observation | Thin graphite rule | Percent and window status | Beside selected quarter |
| Recovery | Return-to-peak notch | Solid notch plus `Recovered` label | Duration in quarters | On the recovery observation |
| Version boundary | Double vertical calibration seam with center gap | 4 px total structural rule | Before/after versions and reason | Across trajectory and tick axis |
| Event | Short neutral tick | Copper stroke, no up/down arrow | Event name and `Same quarter context` | Separate context rail |
| Issuer attribution | Square note marker | Copper outline with `Issuer explanation` label | Issuer and summary | Below context rail |
| Headline Finding | Margin rule and Finding ID | Teal rule plus full title | Frozen statement | Editorial chapter margin |
| Source reference | Superscript-like source index and `Evidence` link | Underline on focus/hover | Company, document, page | Evidence footer/drawer |

## Version-break grammar

The double calibration seam is the strongest structural primitive. It changes line continuity, lane label, and baseline origin. It is never red, never called an error, and never bridged by a quantitative path. Overlap quarters are shown in parallel lanes sharing one quarter coordinate. `cross_version_change_allowed=false` is expressed by absence of a connecting segment and by the note “Definitions are not a continuous change series.”

## Uncertainty grammar

Interval geometry is mandatory for derived observations. The point estimate is subordinate to the compatible range. When a change interval crosses zero, the zero reference is visible and the label reads “Direction not robust to rounding.” Stable directions may show a neutral plus/minus sign, but never winner/loser color semantics.

## Event and source grammar

Events live on a physically separate context rail with a shared quarter coordinate. Event symbols never encode good/bad direction. The rail carries the permanent note “Curated, non-exhaustive context; timing does not establish causality.” Source access opens a quiet drawer or evidence footer rather than covering the plot with citations. Absolute cross-company levels are not comparable.

## Numeric display

- Canonical values remain available in `KRW_million`; display conversion to billion KRW or 亿元 is deterministic and reversible.
- Respect frozen presentation precision: e.g. KRW 7.012 bn and 65.719 bn for F2, +837.3%.
- Always pair number with metric label, entity type, platform/reporting scope, and metric version where relevant.
- Never show USD, a revenue rank, or a cross-company common absolute scale.

## Evidence legend

The compact key shows five items: filled circle `Official reported`; outlined diamond plus whisker `Derived from official`; copper rail tick `Event context`; outlined square `Issuer explanation`; double seam `Metric version change`. The legend is introduced in S1 and becomes a small expandable key thereafter.

## Motion

Motion communicates calibration and decomposition: the Prism snaps; lanes separate; an interval extends; the context rail enters; a peak cap locks. Nothing loops. Timing and reduced-motion behavior are frozen in `motion_spec.md`.

## Accessibility

All meaning is duplicated by text and structure. Focus uses a 2–3 px high-contrast outline with offset. Charts have concise summaries and a structured data alternative. Touch targets are at least 44 px. No interaction or evidence is hover-only.
