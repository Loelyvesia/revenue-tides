# Missingness policy

Frozen states:

- `AVAILABLE`
- `NOT_REPORTED`
- `NOT_APPLICABLE`
- `METRIC_VERSION_BREAK`
- `DERIVATION_UNAVAILABLE`
- `SOURCE_UNAVAILABLE`
- `UNRESOLVED`
- `OUTSIDE_SERIES_WINDOW`

No missingness state may become numeric zero. No forward fill, interpolation, neighboring-quarter averaging, or synthetic chart value is allowed.

Numeric zero is valid only when an official source explicitly reports zero. It is not equivalent to missing, not reported, not applicable, no longer disclosed, below threshold, or unknown.
