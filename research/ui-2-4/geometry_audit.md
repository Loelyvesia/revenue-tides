# UI 2.4 Geometry Audit

## Floating tidal body

`tidalBodyPath()` is now the shared geometry contract for Hero, Quarter Prism, F1, F2, F4, archive fingerprints, and the reusable `TidalBand`.

- The upper edge is the presentation-smoothed path through every real quarterly anchor.
- The lower edge is calculated independently at each anchor from `baseDepth + normalized amplitude + local slope` and then returned right-to-left.
- No component reads values from the interpolated segment between anchors.
- The body is closed against its own moving lower contour, not against a chart floor.
- A vertical alpha mask dissolves the lower mass before its contour can become a dominant baseline.

## Semantic safeguards

Quarter nodes, metric versions, direct/derived evidence, uncertainty intervals and overlap observations are unchanged. `tidalAreaPath()` remains available as a compatibility utility but is no longer used by the presentation components audited here.

## Component result

| Surface | UI 2.3 | UI 2.4 |
|---|---|---|
| Hero | broad field with residual floor-like bodies | nine floating normalized bodies behind the title |
| Prism | area fill visually accumulated toward a lower edge | floating measurement body with a dissolving underside |
| F1 | thin paired currents | thicker paired definition bodies |
| F2 | surge area | floating surge body plus exact ridge |
| F4 | landscape area | floating recovery/drawdown body with stronger key readings |
| Archive | compact area fingerprints | floating fingerprints; selected detail enlarged |

Result: PASS.
