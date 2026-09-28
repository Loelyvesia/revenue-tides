# Data-to-UI contract

The web-data layer remains authoritative. Presentation may format values and choose layouts, but it must not recompute research eligibility or reinterpret evidence.

| Web-data field | Conceptual visual role | Guardrail |
| --- | --- | --- |
| `series_id` | Stable selection and deep-link key | Never infer identity from display name |
| `name`, `publisher_defined_name` | Primary/canonical and issuer labels | Preserve issuer wording where definitions depend on it |
| `entity_type` | `GAME_TITLE` or `IP` identity label | Never collapse the types |
| `company_name` | Reporting-company context | Not a ranking dimension |
| `platform_scope`, `reporting_scope` | Scope line adjacent to value | Never shorten to “total revenue” |
| `evidence_mode`, `evidence_class` | Direct circle or derived diamond/interval and text label | Direct and derived remain separate evidence structures |
| `detail_path` | Lazy-load route | Initial bootstrap does not require all detail files |
| `quarter`, `period_index` | Visible quarter and deterministic sort position | Do not parse arbitrary labels for ordering |
| `metric_definition_id` | Metric identity and Finding evidence route | Required on every observation |
| `metric_version` | Reporting lane label | Required; never silently choose one overlapping value |
| `version_break` | Double calibration seam and explanatory note | No cross-version connector, QoQ, or continued baseline |
| `value`, `unit`, `currency` | Canonical numeric mark and formatted label | Preserve raw numeric value; no USD conversion |
| `lower_bound`, `upper_bound` | Whisker/hatched compatible range | Mandatory for derived evidence; never opacity alone |
| `derived.share_percent` | Official rounded-share note | Never imply exact allocation |
| `derived.share_rounding_note` | Contextual uncertainty explanation | Expose on demand and in F6 |
| `derived.derivation_ref` | Evidence-route link | Does not become a source itself |
| `derived.direction_sign_stable` | Stable/sensitive change wording | Sensitive direction cannot receive confident up/down treatment |
| `missingness_state` | Explicit no-value state | Never encode missing as zero or remove the record |
| `qoq` | Precomputed compatible-period change | Render only when `eligible=true`; never recompute across versions |
| `baseline_index` | Optional normalized trajectory | Label `Normalized trajectory — absolute revenue not comparable` |
| `rolling_peak` | Peak calibration cap | Within-series only |
| `drawdown_percent` | Peak-to-current bracket | Never label permanent decline |
| `recovery.status`, `recovery.quarters` | Recovery notch and status | Preserve observed-window qualification |
| `eligibility.*` | Authoritative transformation gates | Browser must not infer eligibility |
| `events[].fiscal_period` | Separate context rail alignment | No causal connector or effect field |
| `events[].curated` | Persistent event-coverage caveat | `curated=true` must remain visible as curated/non-exhaustive |
| `attributed_claims[]` | `Issuer explanation` note track | Never call a project Finding or fact |
| `finding_ids`, `headline` | Finding navigation and editorial priority | Headline set remains F1/F2/F4 |
| `source_id`, `source_page` | Evidence drawer/footer route | Resolve through `sources.json`; no duplicated source payload |
| `caveat_ids` | Compact evidence key and contextual expansions | Do not replace structured caveats with generic warning banners |

## Content hierarchy

1. Project thesis.
2. Frozen Finding statement.
3. Series label and entity type.
4. Metric label, version, platform/reporting scope.
5. Quarter and period context.
6. Value, unit, and evidence class.
7. Uncertainty and sign stability where applicable.
8. Event context and issuer attribution on separate tracks.
9. Limitation, caveat, and source trail.

No number may appear as a principal visual label without series/entity, metric scope, period, unit, and evidence context available in the same state.
