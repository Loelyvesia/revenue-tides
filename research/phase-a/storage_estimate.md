# Storage Estimate

Assumptions: up to six structured commercial metrics per game-month; compact UTF-8 text; official-event metadata only; no image/video archive; no mirrored commercial sites.

| Component | Scenario S — 10 games × 24–36 months | Scenario M — 30 games × 36–60 months | Scenario L — 100 games × 60 months |
| --- | ---: | ---: | ---: |
| Structured CSV | 1–2 MB | 5–10 MB | 18–30 MB |
| Structured JSON | 2–4 MB | 10–20 MB | 35–60 MB |
| Structured Parquet | 0.3–0.8 MB | 1.5–4 MB | 5–12 MB |
| Provenance metadata | 0.5–1 MB | 2–5 MB | 8–15 MB |
| Small permitted official HTML/text snapshots | 3–8 MB | 15–35 MB | 60–120 MB |
| Event metadata | <0.2 MB | <1 MB | 2–4 MB |
| Frontend processed data | 0.5–2 MB | 2–6 MB | 6–18 MB |

Even the largest scenario should remain below roughly 200 MB with disciplined snapshots. The preferred deployable layer would normally be compact JSON/Parquet-derived aggregates, while raw provenance remains outside the frontend.

