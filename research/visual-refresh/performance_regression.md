# Performance regression

Status: `PASS WITH CSS SIZE NOTE`

| Artifact | 1.0.0 baseline | 1.1.0 candidate | Change |
|---|---:|---:|---:|
| JavaScript raw | 107.29 kB | 112.07 kB | +4.78 kB / +4.5% |
| JavaScript gzip | 40.27 kB | 41.66 kB | +1.39 kB / +3.5% |
| CSS raw | 26.78 kB | 40.46 kB | +13.68 kB / +51.1% |
| CSS gzip | 5.71 kB | 8.22 kB | +2.51 kB / +44.0% |
| HTML raw | 0.91 kB | 0.91 kB | unchanged |
| JS + CSS gzip | 45.98 kB | 49.88 kB | +3.90 kB / +8.5% |

The CSS-only preferred target of less than 20% gzip growth was not met. This is recorded as a non-blocking warning because the absolute increase is 2.51 kB, total JS+CSS gzip growth is 8.5%, and the refresh adds no dependency, font, chart library, generated image, game art, or other runtime asset.

Initial data loading remains lazy. Browser smoke confirms the page serves successfully, series payloads remain cached, and no new network errors occur.
