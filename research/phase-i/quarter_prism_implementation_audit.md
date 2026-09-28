# Quarter Prism implementation audit

| State / requirement | Implementation | Result |
| --- | --- | --- |
| Direct observation | Solid circle, original KRW unit, metric/evidence/scope/source fields | PASS |
| Same-quarter overlap | Shared quarter coordinate and two simultaneous labeled lanes | PASS |
| Version boundary | Double calibration seam, disconnected polylines, baseline restart and no cross-version QoQ copy | PASS |
| Derived uncertainty | Outlined diamond, capped whisker, point/bounds/share/rounding/sign-stability block | PASS |
| Event context | Separate copper rail and permanent curated/non-causal notice | PASS |
| Issuer explanation | Separate labeled block; never called a Finding | PASS |
| Empty event | Explicit neutral “No curated event” text | PASS |
| Mobile | Desktop SVG hidden at 390; stacked controls, lanes, uncertainty, context, evidence, and direct quarter list | PASS |
| Inputs | Previous, Next, native select, direct quarter buttons, Left/Right keys | PASS |
| Assistive output | Accessible SVG title/description plus settled `aria-live="polite"` summary | PASS |

The graph scale is local to the selected series. Each metric version has its own SVG polyline; no path bridges versions. The current quarter reading always lists canonical values and evidence fields, so no critical information depends on hover. Browser keyboard verification moved Lineage M from 2025Q2 to 2025Q3 while focus remained on the Prism.
