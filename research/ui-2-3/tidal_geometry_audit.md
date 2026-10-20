# Tidal Geometry Audit

`src/utils/tidalGeometry.ts` now exposes a surface system:

- `tidalAreaPath`: exact quarterly anchors form the upper waterline; the lower body is presentation geometry.
- `tidalEnvelopePath`: creates a softer deep mass without encoding another variable.
- `tidalSplitPaths`: supports non-stacked reporting-definition currents.
- `tidalFadeMask`: provides deterministic edge dissolution.

`TidalBand.vue` no longer imports or uses `ribbonPath`. It renders deep mass → filled body → light surface, hides default axes/ticks/nodes, and retains only peak, derived-uncertainty, version-disturbance and event-critical marks.

All overview geometry remains within-series normalized. Quarter anchors remain exact. Interpolation is presentational only; no intermediate observations are exposed or selectable.
