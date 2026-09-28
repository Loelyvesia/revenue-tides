# Frontend data integrity audit

- Phase C: 18/18 frozen method hashes match.
- Phase F: frozen Finding hashes and all six evidence packs match.
- Phase G: 15/15 manifest file hashes match; `public/data/` is byte-identical.
- Phase H: all 34 recorded research/design artifact hashes match `input_manifest.json`.
- Public corpus: 9 series, 75 observations, 26 events, 3 attributed claims, 6 Findings, 42 sources.
- Headline set: exactly F1 / F2 / F4.

Guardrails in types, utilities, rendering, and tests preserve entity type, evidence class, metric version, missingness, transformation eligibility, derived uncertainty, attribution, and source IDs. There is no UI or domain field for global revenue, PC launch effect, winner, health, success, ranking, USD normalization, or causal event effect.

Numeric tests reproduce F1’s 6,797–13,455 million KRW definition differences; F2’s 7.012 / 65.719 billion and 837.3%; F3’s 32.4% and 4.1%; F4’s 20.7%, three-quarter recovery, and 30.8%; F5’s 35.3%; and F6’s 9/15 and 60.0%.
