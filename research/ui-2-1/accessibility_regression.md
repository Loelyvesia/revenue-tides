# Accessibility regression

Status: `PASS`

- Keyboard: native selects, source disclosures, archive rows, quarter ruler, and Prism arrow keys are operable.
- Focus: global visible two-pixel focus outline retained.
- Skip link: retained and functional.
- Reduced motion: F4 reveal and transition effects are disabled; scrolling is not forced smooth.
- ARIA live: Prism reading pane retained.
- Non-color semantics: evidence labels, metric-version text, double seams, derived diamonds/intervals, and written event caveats accompany color.
- Touch targets: base 44 px policy retained; narrow audit reports no undersized critical controls.
- Reflow: 390 px and 320 px browser audits report zero page overflow; long labels wrap or truncate without losing the canonical data value.
- Deep links: asynchronous section growth is followed by bounded hash re-alignment, preventing `#finding-F1` drift.

Chrome and Edge reported zero console errors, warnings, or exceptions. Firefox completed the direct, overlap, derived, event, responsive, hash-navigation, network, and console suite 14/14.
