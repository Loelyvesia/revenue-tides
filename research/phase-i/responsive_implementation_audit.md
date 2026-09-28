# Responsive implementation audit

| Viewport | Inspection | Result |
| --- | --- | --- |
| 1440 × 900 | Editorial opening, direct Prism, full trajectory and reading pane | PASS |
| 1024 × 900 | Lineage overlap, source/context below the main plot, no overflow | PASS |
| 768 × 900 | Derived MCOC interval and Finding reflow, no overflow | PASS |
| 390 × 844 | Exact device metrics: stacked quarter stepper, hidden desktop SVG, event/uncertainty blocks, 390 px document width | PASS |

The first 390 px browser pass detected a long-select min-content overflow. `.series-picker > * { min-width: 0 }` plus a constrained select fixed it. The repeat measurement reported `innerWidth=390`, `clientWidth=390`, `scrollWidth=390`, no overflow elements, and no console errors.

At mobile widths the Observatory becomes stacked disclosure rows; entity type, evidence, and window remain visible. Touch-oriented controls are at least 44 px. At 320 px the same single-column rules apply and values wrap instead of creating page-level scrolling.
