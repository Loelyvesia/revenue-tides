# Bold tidal rebuild — performance report

## Production bundle

| Asset group | Before | After | Change |
|---|---:|---:|---:|
| JavaScript, raw | 125.67 KB | 146.01 KB across 9 chunks | +20.34 KB |
| JavaScript, gzip | 46.53 KB | 58.21 KB across 9 chunks | +11.68 KB |
| Initial JavaScript, gzip | 46.53 KB | 37.51 KB | -9.02 KB |
| CSS, raw | 50.01 KB | 62.53 KB across 3 chunks | +12.52 KB |
| CSS, gzip | 10.50 KB | 14.45 KB across 3 chunks | +3.95 KB |

The full payload grows because the new presentation contains multiple purpose-built SVG stages, motion states, responsive compositions, and semantic fills. The opening payload shrinks because Measurement, Prism, Findings, Observatory, Notes, and Appendix are independent async chapters.

## Geometry and motion

- Static source templates: 7 SVG roots, 39 path declarations, 8 gradient declarations, 4 local SVG filters, and 3 semantic patterns.
- Runtime Hero: 9 bands generated from frozen series data; only 3 are shown on mobile.
- Motion families: load/reveal, tide reshape, event pulse, pointer parallax, ruler transition, and active-row sweep.
- Reduced motion removes path drawing, morph transitions, parallax, pulse, gradient movement, and staged reveals.
- Largest emitted asset: initial JavaScript `95.32 KB` raw / `37.51 KB` gzip.

## Dependency decision

No new runtime or development dependency was added. Vue, native SVG, CSS, and a 2 KB local geometry utility were sufficient; neither Three.js, D3, Nivo, nor a motion library was necessary.

## Browser observations

- Chrome 153: 15/15 PASS.
- Edge 149: 15/15 PASS.
- Firefox 156: 13/13 PASS.
- Six required Chromium viewports: 0 px page-level overflow.
- Console errors/warnings/exceptions: 0.
- Required network failures: 0.

