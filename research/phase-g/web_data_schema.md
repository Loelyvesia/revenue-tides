# Web data schema

Version: `revenue-tides-webdata-1.0.0`  
Encoding: UTF-8  
Canonical serialization: JSON with two-space indentation, lexicographically sorted object keys, deterministic array ordering, and a final newline.

All monetary `value`, `lower_bound`, `upper_bound`, `rolling_peak`, and QoQ absolute-change fields use `KRW_million`. JSON `null` means unavailable or not applicable; it is never converted to numeric zero.

## `manifest.json`

| Field | Type | Nullable | Meaning / source |
| --- | --- | --- | --- |
| webdata_version | string | no | Frozen Phase G data-product version. |
| method_version | string | no | Phase C frozen method version. |
| findings_version | string | no | Phase F frozen Findings version. |
| data_cutoff | date string | no | Latest authorized corpus cutoff. |
| build_version / build_date | string / date string | no | Deterministic build identity and fixed build date. |
| series_count / observation_count / event_count / finding_count | integer | no | Canonical record counts. |
| headline_finding_ids | string[] | no | Frozen set `F1`, `F2`, `F4`. |
| company_count / source_count | integer | no | Public company/source counts. |
| source_count_summary | object | no | Counts by official source document type. |
| series_index | object[] | no | Minimal bootstrap series IDs, names, and lazy detail paths. |
| finding_index | object[] | no | Minimal Finding IDs, frozen titles, headline flag, and series IDs. |
| feature_flags | object<boolean> | no | Data capabilities only; no UI design metadata. |
| global_caveat_ids | string[] | no | References into `caveats.json`. |
| files | object[] | no | Path, byte size, SHA-256, and record count for every public file except the self-referential manifest. |
| manifest_self_hash_policy | string | no | Documents the manifest self-hash exclusion. |

## `project.json`

| Field | Type | Nullable | Meaning / source |
| --- | --- | --- | --- |
| project_id | string | no | Stable project identifier. |
| title_zh / title_en | string | no | Project titles. |
| subtitle_zh / subtitle_en | string | no | Factual dataset description. |
| method_version / findings_version / webdata_version | string | no | Frozen contract versions. |
| data_cutoff | date string | no | Corpus cutoff. |
| primary_temporal_unit | enum | no | `FISCAL_QUARTER`. |
| corpus_series_count / observation_count / event_count / claim_count | integer | no | Canonical counts. |
| headline_finding_ids | string[] | no | Frozen headline Finding IDs. |
| global_caveats | string[] | no | Caveat references. |
| comparison_policy | object | no | Frozen comparability restrictions; cross-company absolute levels are `NOT_COMPARABLE`. |
| causality_policy | string | no | Events remain temporal context; issuer explanations remain attributed. |
| companies | object[] | no | `company_id`, name, reporting currency, fiscal-calendar status, and public IR URL. |

## `series_index.json`

Array of exactly nine lightweight records. Every field is non-null unless stated.

| Field | Type | Meaning |
| --- | --- | --- |
| series_id | string | Canonical analytical-series ID. |
| name / publisher_defined_name | string | Canonical and issuer-defined entity names. |
| entity_type | enum | `GAME_TITLE` or `IP`; never collapsed. |
| company_id / company_name | string | Reporting company identity. |
| platform_scope | string | Publisher-defined platform scope. |
| evidence_mode | enum | `OFFICIAL_REPORTED` or `DERIVED_FROM_OFFICIAL`. |
| first_period / last_period | quarter string | Authorized series window. |
| quarter_count / metric_version_count / event_count / claim_count | integer | Browse-level counts. Quarter count is unique authorized quarters, not overlapping observation rows. |
| finding_ids / headline_finding_ids | string[] | Frozen Finding references. |
| detail_path | string | Relative lazy-load path under `data/web/`. |
| status | enum | `VALIDATED`. |

## `series/{series_id}.json`

Top-level fields are `series_id`, `identity`, `metric_versions`, `observations`, `events`, `attributed_claims`, `findings`, and `sources`.

### identity

`series_id`, `entity`, `publisher_defined_name`, `entity_type`, `company_id`, `company`, `platform_scope`, `reporting_scope[]`, and `caveat_ids[]`. All are non-null.

### metric_versions[]

| Field | Type | Nullable | Meaning |
| --- | --- | --- | --- |
| metric_definition_id | string | no | Canonical Phase D metric ID. |
| label / economic_meaning / accounting_scope | string | no | Frozen issuer-metric semantics. |
| version | string | no | `v1`, `legacy_v1`, `royalty_v2`, or `derived_v1`. |
| valid_period | object | no | First/last represented fiscal quarter. |
| comparable_group_id | string | no | Stable within-version transformation group. |
| platform_scope / geographic_scope / unit_basis | string | no | Metric coverage and source unit semantics. |
| evidence_class | enum | no | `OFFICIAL_REPORTED` or `DERIVED_FROM_OFFICIAL`. |
| comparison_scope | enum | no | `WITHIN_SERIES_ONLY`. |
| version_break | object | yes | For Lineage metrics: `break_before`, `break_after`, reason, `cross_version_change_allowed=false`, `baseline_restart=true`, and same-quarter-overlap flag. |
| caveat_ids | string[] | no | Structured caveat references. |

### observations[]

Each observation preserves the canonical `observation_id`. Multiple objects may share a quarter when metric versions overlap.

| Field | Type | Nullable | Meaning |
| --- | --- | --- | --- |
| observation_id | string | no | Canonical Phase D observation ID. |
| quarter / period_key | quarter string | no | Fiscal-quarter label. |
| period_index | integer | no | Sort key: `year × 4 + quarter - 1`. |
| period_start / period_end | date string | no | Exact fiscal-period bounds. |
| metric_definition_id / metric_version | string | no | Mandatory metric-version identity. |
| value | number | yes | Canonical value in `KRW_million`; null follows missingness. |
| unit / currency | string | no | `KRW_million` / `KRW`. |
| evidence_class | enum | no | `OFFICIAL_REPORTED` or `DERIVED_FROM_OFFICIAL`. |
| lower_bound / upper_bound | number | yes | Derived uncertainty bounds in `KRW_million`; null for direct observations. |
| missingness_state | enum | no | Frozen missingness state (`AVAILABLE`, `NOT_REPORTED`, `NOT_APPLICABLE`, `METRIC_VERSION_BREAK`, `DERIVATION_UNAVAILABLE`, `SOURCE_UNAVAILABLE`, `UNRESOLVED`, `OUTSIDE_SERIES_WINDOW`). |
| qoq | object | no | Absolute/percent change (nullable), eligibility, and previous compatible observation ID. |
| baseline_index / rolling_peak / drawdown_percent | number | yes | Frozen Phase E transformations. |
| recovery | object | no | Frozen status and nullable duration in quarters. |
| eligibility | object<boolean> | no | Authoritative QoQ, baseline, drawdown, and volatility flags. |
| derived | object | yes | For derived observations only: derivation ref, share percent, rounding note, and nullable sign-stability evidence. |
| source_id | string | no | Reference into `sources.json`. |
| source_page | string | yes | Page locator when applicable. |

### events[]

Fields: `event_id`, `series_id`, `name`, `event_type`, `start_date`, nullable `end_date`, `date_precision`, `fiscal_period`, `platform_scope`, `region_scope`, `source_id`, and `curated=true`. No causal-effect field exists.

### attributed_claims[]

Fields: `claim_id`, `series_id`, `period`, `issuer`, `summary`, `claim_type`, `source_id`, and `attributed=true`. These are issuer explanations, not project Findings.

### references

`findings[]` and `sources[]` contain IDs only. Full Finding/source metadata is deduplicated in the corresponding top-level files.

## `findings.json`

Exactly six frozen Findings. Fields are `finding_id`, bilingual frozen titles/statements, `finding_class`, `strength`, `series_ids`, period bounds, `metric_definition_ids`, `evidence_class`, `quantitative_summary`, `uncertainty_note`, `limitations`, `forbidden_interpretation`, `headline`, observation/event/claim/source ID arrays, and caveat IDs. Wording comes verbatim from Phase F; only the key name `limitations` maps the frozen singular `limitation` value.

## `sources.json`

Deduplicated public-safe source records: `source_id`, `company`, nullable `document_title`, `document_type`, nullable publication/reporting period, canonical/specific public URLs, page list, and access classification. Local paths, raw-file hashes, extractor identity, and QA notes are excluded.

## `caveats.json`

Structured records with `caveat_id`, `text_zh`, and `text_en`. IDs are stable and referenced rather than duplicating long warnings.

## `NOTICE.md`

Human-readable notice covering official public-source compilation, publisher-defined metric scope, derived labeling, non-causal event context, source copyright ownership, and non-republication of report artwork.
