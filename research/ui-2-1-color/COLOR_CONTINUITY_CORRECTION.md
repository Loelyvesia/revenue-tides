# Revenue Tides — UI 2.1 Color Continuity Correction

Status: `PASS`

This post-freeze correction removes the full-page dark/light alternation without changing research data, frozen Findings, information architecture, or analytical behavior.

## Final semantic roles

| Role | Token | Value | Use |
|---|---|---:|---|
| PAGE | `--page-bg` | `#EEECE5` | Continuous warm mineral canvas |
| SURFACE | `--surface-bg` / `--surface-subtle` | `#F5F2EA` / `#E4E1D7` | Raised and softly differentiated editorial areas |
| INK | `--ink` | `#202321` | Near-black graphite text and rules |
| DATA | `--data-teal` | `#1F716D` | Quantitative trajectory and selected values |
| CONTEXT | `--context-copper` | `#955A3B` | Event and context only |
| UNCERTAINTY | `--uncertainty-violet` | `#6D667C` | Derived intervals and unresolved direction |
| INSTRUMENT | `--instrument-bg` | `#1C2423` | Quarter Prism inner analytical panel only |

Instrument variants provide accessible off-white text and restrained accent contrast without introducing a second site theme.

## Section result

- Hero: warm mineral surface; impact comes from typography and the nine real normalized trajectories.
- Measurement: continuous page canvas.
- Quarter Prism: warm chapter and controls surrounding one bordered dark instrument panel.
- F1: subtle mineral surface; legacy and royalty-integrated values remain distinguished by position, labels, rules, and color.
- F2: warm surface; teal spike, copper PC-release context, graphite headline number.
- F4: continuous page canvas; teal tidal sequence and graphite/copper annotation.
- Observatory: subtle mineral surface in the same family.
- Research Appendix and source drawers: warm surfaces.
- Navigation: one translucent warm treatment across every chapter.

No full-bleed dark section remains. Legacy `chapter--dark`, `surface-dark`, `on-dark`, and navigation theme-switch tokens/classes were removed.

## Validation

- Color-continuity validator: `29/29 PASS`.
- Vitest: `62/62 PASS`.
- UI 2.1 validator: `28/28 PASS`.
- Phase I validator: `100/100 PASS`.
- Phase J validator: `102/102 PASS`.
- Chrome 153: `15/15 PASS`.
- Edge 149: `15/15 PASS`.
- Firefox 156: `14/14 PASS`.
- Viewports: 1440×900, 1280×800, 1024×768, 768×1024, 390×844, and 320×700 all have `0 px` page-level horizontal overflow.
- Console errors, warnings, exceptions, and required network failures: `0`.

## Contrast audit

Small-text combinations meet WCAG AA's 4.5:1 threshold:

| Pair | Ratio |
|---|---:|
| muted graphite / page | 4.55:1 |
| tidal teal / page | 4.88:1 |
| oxidized copper / page | 4.67:1 |
| instrument faint / instrument | 4.67:1 |
| uncertainty violet / instrument | 4.93:1 |

Focus treatment, source links, keyboard navigation, reduced motion, and semantic non-color labels remain intact.

## Bundle effect

- Previous UI 2.1 JS: 125.10 kB / about 46.35 kB gzip.
- Corrected JS: 125.02 kB / 46.31 kB gzip.
- Previous UI 2.1 CSS: 50.98 kB / about 10.57 kB gzip.
- Corrected CSS: 50.40 kB / 10.52 kB gzip.
- No dependency was added.

## Review boundary

No deployment, tag, release freeze, research-data edit, or Finding edit was performed.

`STOPPED BEFORE COLOR SYSTEM REVIEW`
