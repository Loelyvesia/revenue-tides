# Performance regression

Status: `PASS`

| Asset | UI 2.0 | UI 2.1 | Result |
|---|---:|---:|---|
| JavaScript | 113.98 kB / 43.00 kB gzip | 125.10 kB / about 46.3 kB gzip | PASS — gzip growth remains below 10%. |
| CSS | 29.80 kB / 6.94 kB gzip | 50.98 kB / about 10.6 kB gzip | REVIEWED — expected geometry/responsive styling growth; no runtime cost. |
| HTML | 0.91 kB | 0.91 kB | PASS |

- New runtime dependencies: `0`
- Images, game art, font files, video, particles, and chart libraries: `0`
- Largest runtime file: approximately `125.10 kB` uncompressed JavaScript.
- Two consecutive builds: `BYTE-IDENTICAL` across 20 files.
- Measurement chapter Chinese copy reduction: `40.6%` by CJK character count, exceeding the 30% target.

Research screenshots are stored outside the production bundle.
