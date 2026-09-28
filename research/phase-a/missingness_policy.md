# Missingness Policy

Missingness is categorical evidence, never numeric zero.

Allowed states:

- `AVAILABLE`: the metric is publicly present at the recorded scope.
- `NOT_PUBLISHED`: the source did not publish the metric or the title is outside the published list.
- `LOGIN_REQUIRED`: public navigation reaches an authentication boundary.
- `PAID_ONLY`: access requires a paid product or report tier.
- `NOT_APPLICABLE`: the metric/source combination is conceptually inapplicable.
- `NOT_FOUND`: a bounded search did not locate the item.
- `AMBIGUOUS`: a value, period, identity, or definition cannot be resolved safely.
- `ACCESS_ERROR`: the public resource failed independently of a known login/paywall condition.

Rules:

1. Blank numeric values require a missing state.
2. A game outside a published top ten is `NOT_PUBLISHED`, not rank 11 and not zero.
3. Image-only ranks that were not manually verified remain `NOT_PUBLISHED` or `AMBIGUOUS`.
4. “Last Month” without explicit period bounds keeps `period_start` and `period_end` blank and uses `AMBIGUOUS`.
5. A login gate is not `NOT_FOUND`.
6. Publisher-segment amounts are not missing title amounts; they are separate publisher-subject observations.
7. Missing platform/channel coverage is recorded in coverage fields, not folded into the value.
8. No interpolation, rank-to-dollar conversion, or cross-source filling is allowed.

