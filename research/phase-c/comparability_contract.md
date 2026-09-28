# Comparability contract

Frozen classes:

- `DIRECTLY_COMPARABLE`
- `WITHIN_SERIES_ONLY`
- `VERSION_BREAK`
- `CONTEXT_ONLY`
- `NOT_COMPARABLE`

The conservative default for a stable publisher-defined game/IP series is `WITHIN_SERIES_ONLY`. Observations are directly comparable only under compatible entity identity, metric definition, reporting scope, currency/unit basis, and metric version.

Cross-company absolute revenue levels are `NOT_COMPARABLE` by default. Same currency does not override accounting differences.

Cross-series unitless trajectory-shape comparisons are permitted only after each stable series is independently normalized to its own baseline or previous quarter. They describe relative pattern, not economic level, and must propagate derived uncertainty when relevant.
