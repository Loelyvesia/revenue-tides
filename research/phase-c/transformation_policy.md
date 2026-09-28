# Transformation policy

Permitted transformations within a stable comparable group are:

- `qoq_absolute_change`
- `qoq_percent_change`
- `baseline_index`
- `rolling_peak`
- `drawdown_from_prior_peak`
- `recovery_to_prior_peak`
- `within_series_range`
- `coefficient_of_variation`

Candidate volatility measures also include standard deviation of QoQ percentage change and median absolute QoQ change, subject to Phase F robustness and minimum-count checks.

For `baseline_index`, select a valid starting observation inside one metric version and calculate `value_t / baseline_value × 100`. Never cross a version break or start from missing data. Propagate derived uncertainty when meaningful.

A drawdown begins below a prior within-version peak. Recovery occurs when a later observation returns to or exceeds that same-version peak. Store peak, trough, recovery quarter, magnitude, and duration. An unrecovered ending is `NOT_RECOVERED_WITHIN_OBSERVED_WINDOW`, not permanent decline.

No proprietary success score, composite game ranking, interpolation, forward fill, or cross-company absolute leaderboard is allowed.
