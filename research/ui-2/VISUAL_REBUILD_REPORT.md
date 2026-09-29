# Revenue Tides — UI 2.0 Visual Reconstruction Report

Status: `REVIEW REQUIRED`

- Branch: `ui-rebuild-2.0`
- Release candidate: `revenue-tides-release-2.0.0`
- Package version: `2.0.0`
- Date: 2026-09-29

## Outcome

The runtime presentation layer was reconstructed around four acts:

1. **The Number** — a five-step measurement scrollytelling sequence.
2. **The Quarter** — Quarter Prism V2 as a pinned analytical stage.
3. **The Findings** — full-page F1, F2, and F4 evidence chapters.
4. **The Archive** — a nine-series Observatory with one lazy detail pane.

Research Notes retain F3/F5/F6, and the Research Appendix retains versions, comparison policy, caveats, and all public source access.

## Research integrity

- Research data changed: `NO`
- Frozen Findings changed: `NO`
- Web Data changed: `NO`
- New series, quarters, companies, sources, or Findings: `NONE`
- Cross-company absolute comparison: `NOT IMPLEMENTED`
- Metric-version stitching: `NOT IMPLEMENTED`
- Event-causality field: `NOT IMPLEMENTED`

Hero trajectories are computed from public Phase G observations after load. Each metric definition is rendered as its own normalized path, so Lineage version breaks do not become a false continuous trajectory.

## Interaction and motion

- Motion dependency: `NONE`
- Scroll helper: `NONE`
- Orchestration: native `IntersectionObserver` plus one rAF-throttled progress listener.
- Scroll-jacking: `NONE`
- Quarter Prism input paths: scroll steps, native quarter select, timeline points, previous/next buttons, and Left/Right keys.
- Reduced motion: native scrolling and zero-duration transition tokens.

## Visual system

- Surfaces: dark / paper / ink-light.
- Typography: system CJK sans, serif fallback, and system monospace numerics; no packaged font.
- Accents: teal for direct trajectory/state, copper for context and uncertainty, double rules for version seams.
- No images, game art, particle field, WebGL, glassmorphism, stock chart, UI framework, or chart dependency.

## Browser and viewport QA

- Chrome 153: `15/15 PASS`
- Edge 149: `15/15 PASS`
- Firefox 156: production-build render `PASS`
- 1440×900, 1280×800, 1024×768, 768×1024, 390×844, 320×700: `0 px` page-level horizontal overflow.
- Chrome console errors/warnings/exceptions: `0/0/0`
- Edge console errors/warnings/exceptions: `0/0/0`
- Required network failures: `0`

## Automated regression

- Vitest: `62/62 PASS`
- Phase G isolated validator: `90/90 PASS`
- Phase I validator: `100/100 PASS`
- Phase J validator: `102/102 PASS`
- TypeScript: `PASS`
- Production build: `PASS`

## Bundle

- JavaScript: 113.98 kB uncompressed / 43.00 kB gzip.
- CSS: 29.80 kB uncompressed / 6.94 kB gzip.
- New runtime dependencies: `0`.
- Two consecutive production builds: `BYTE-IDENTICAL` across 19 output files.

## Review boundary

No deployment, tag, release freeze, or GitHub Pages update was performed. This candidate stops before UI 2.0 release.
