# Responsive visual QA

Status: `PASS`

| Viewport | Result | Notes |
|---|---|---|
| 1440×900 | PASS | Full editorial grid and analytical canvases visible. |
| 1280×800 | PASS | No overflow; section rhythm and Prism controls remain stable. |
| 1024×768 | PASS | Two-column sections retain readable measures. |
| 768×1024 | PASS | Ledger and Finding layouts reflow without page overflow. |
| 390×844 | PASS | Mobile hero, Prism stepper, Lineage lanes, and ledger rows are purpose-built. |
| 320×700 | PASS | No page-level horizontal scroll; controls remain usable and long labels wrap. |

Automated browser measurements report `overflow_px = 0` for all six viewports. Visible mobile controls remain at least 44 px high. The F4 sequence and quarter tick list use local horizontal scrolling where needed without widening the page.

At 200% zoom equivalent (720×450 CSS viewport), the core Prism reading and event context remain present, controls remain at least 44 px high, and page-level overflow remains zero.
