# Missingness audit

All targeted observations in the bounded pilot are available. This does not justify using zero for absent future data.

Allowed states are `AVAILABLE`, `NOT_REPORTED`, `NOT_APPLICABLE`, `METRIC_VERSION_BREAK`, `DERIVATION_UNAVAILABLE`, `SOURCE_UNAVAILABLE`, and `UNRESOLVED`.

The observation table contains only actual available quantitative records. It does not manufacture placeholder observations for absent quarters. Structural unknowns in metric definitions remain the literal value `UNKNOWN`. Change features use blank numeric fields plus a reason when no compatible predecessor exists. Zero is reserved for an explicitly reported numerical zero; none occurs in this pilot.
