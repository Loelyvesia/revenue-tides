# Metric contract

Every observation references a versioned metric definition containing:

- metric name and reporting company;
- entity scope and economic/accounting meaning;
- platform and geographic scope;
- royalty, licensing, and platform-receipt treatment;
- unit basis;
- `valid_from` and `valid_to`;
- metric version and `comparable_group_id`.

Unknown semantics remain the literal state `UNKNOWN`.

Each observation stores fiscal-year label, fiscal-quarter label, exact period start and end, reporting company, and publication date separately. Original `reported_value_raw`, `reported_unit_raw`, and `original_currency` are mandatory.

Deterministic same-currency scale normalization is allowed, such as KRW billion to KRW million. FX conversion is not part of the canonical analytical layer. Half-year and annual metrics remain context-only unless a formal amendment approves a different primary reporting frequency.
