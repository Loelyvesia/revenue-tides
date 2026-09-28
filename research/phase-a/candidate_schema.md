# Candidate Schema — Draft Only

This schema is intentionally not frozen. Phase C would freeze it only after a controlled pilot.

## `game`

| Field | Type | Notes |
| --- | --- | --- |
| `game_id` | string PK | Stable project ID; never a display-name join key. |
| `canonical_name` | string | Edition-qualified where required. |
| `normalized_english_name` | string | Search/display normalization only. |
| `original_localized_name` | string nullable | Preserve original script. |
| `publisher_org_id` | string nullable | Time-versioned organization reference. |
| `developer_org_id` | string nullable | Time-versioned organization reference. |
| `release_date` | date nullable | Must carry `release_date_basis`. |
| `platform_scope` | enum set | Declared game availability, not observation coverage. |
| `region_scope` | enum set | Edition scope. |
| `official_url` | URL | Canonical official site. |
| `identity_status` | enum | `RESOLVED`, `REGIONAL_EDITION_ISOLATED`, `OPEN`, etc. |

## `app_identity`

Needed because one game family can have several regional/store applications.

| Field | Type | Notes |
| --- | --- | --- |
| `app_identity_id` | string PK | Package/store identity. |
| `game_id` | string FK | May point to an edition-level game. |
| `store` | enum | `APPLE_APP_STORE`, `GOOGLE_PLAY`, `THIRD_PARTY_ANDROID`, etc. |
| `store_id` | string | Apple numeric ID or package name. |
| `region` | string | Storefront or distribution region. |
| `publisher_name_as_listed` | string | Preserve source wording. |
| `valid_from`, `valid_to` | date nullable | Handles publisher changes/renames. |
| `identity_evidence_source_id` | string FK | Source that establishes the mapping. |

## `commercial_observation`

| Field | Type | Notes |
| --- | --- | --- |
| `observation_id` | string PK | Stable row ID. |
| `subject_type` | enum | `GAME`, `APP_IDENTITY`, `PUBLISHER_SEGMENT`, `MARKET`. |
| `game_id` | string FK nullable | Blank for non-game subjects. |
| `period_start`, `period_end` | date/timestamp nullable | Observation period; never publication time. |
| `period_label` | string | Preserve source label such as “Last Month.” |
| `published_at` | date/timestamp nullable | Source publication time. |
| `metric_type` | enum | See below. |
| `value` | decimal nullable | Exact/rounded source value; never imputed. |
| `unit` | string nullable | `CURRENCY`, `DOWNLOADS`, `RANK`, etc. |
| `currency` | ISO 4217 nullable | Required for monetary values. |
| `rank` | integer nullable | Kept separate from value. |
| `market` | string | Explicit geography. |
| `platform_scope_id` | string FK | Exact included/excluded channels. |
| `evidence_class` | enum | Required. |
| `source_id` | string FK | Required. |
| `is_estimate` | boolean | Required even when evidence class is present. |
| `value_precision` | enum | `EXACT_AS_REPORTED`, `ROUNDED`, `APPROXIMATE`, `RANGE`. |
| `missing_state` | enum nullable | Required when the metric is absent. |
| `coverage_notes` | string | Exclusions and identity caveats. |
| `retrieved_at` | timestamp | Retrieval time. |

Preliminary `metric_type` values remain distinct:

- `PUBLISHER_RECOGNIZED_REVENUE`
- `GROSS_CONSUMER_SPENDING`
- `IAP_REVENUE`
- `STORE_REVENUE_ESTIMATE`
- `MOBILE_REVENUE_ESTIMATE`
- `REVENUE_RANK`
- `REVENUE_GROWTH_RANK`
- `DOWNLOAD_ESTIMATE`
- `DOWNLOAD_RANK`
- `DOWNLOAD_GROWTH_RANK`
- `BOOKINGS`
- `GMV`
- `PLAYER_SPENDING`
- `MAU`
- `DAU`
- `MARKET_AGGREGATE_IAP`

No aliasing or implicit conversion is permitted among these values.

## `platform_coverage`

| Field | Type | Notes |
| --- | --- | --- |
| `platform_scope_id` | string PK | Reusable coverage record. |
| `apple_app_store` | coverage enum | Included/excluded/unknown/not applicable. |
| `google_play` | coverage enum | Same. |
| `third_party_android` | coverage enum | Same. |
| `china_ios` | coverage enum | Separate from global iOS. |
| `china_android` | coverage enum | Separate from Google Play. |
| `pc` | coverage enum | Same. |
| `console` | coverage enum | Same. |
| `direct_web_shop` | coverage enum | Same. |
| `alternative_payment` | coverage enum | Same. |
| `coverage_text_as_published` | string | Verbatim-short or paraphrased source caveat. |

Coverage enum: `INCLUDED`, `EXCLUDED`, `PARTIAL`, `UNKNOWN`, `NOT_APPLICABLE`.

## `live_event`

| Field | Type | Notes |
| --- | --- | --- |
| `event_id` | string PK | Stable event record. |
| `game_id` | string FK | Edition-aware. |
| `event_name` | string | Source name. |
| `event_type` | enum | Major version, character, season, anniversary, crossover, expansion, regional launch, monetization event, etc. |
| `announced_at` | timestamp nullable | May be absent on microsites. |
| `started_at`, `ended_at` | timestamp nullable | Include timezone or a precision field. |
| `date_precision` | enum | `TIMESTAMP`, `DAY`, `MONTH`, `LOCAL_TIME`, `UNKNOWN`. |
| `region` | string | Explicit. |
| `platform` | string | Explicit. |
| `source_id` | string FK | Official source preferred. |
| `evidence_class` | enum | Normally `EVENT_OFFICIAL`. |

## `source`

| Field | Type | Notes |
| --- | --- | --- |
| `source_id` | string PK | Stable source record. |
| `publisher_name` | string | Source publisher, not game publisher. |
| `source_type` | enum | Article, official report, official event, documentation, etc. |
| `url` | URL | Required. |
| `published_at`, `retrieved_at` | timestamp nullable/required | Separate fields. |
| `license_or_terms_note` | string | Factual, scoped note. |
| `snapshot_path` | path nullable | Small and justified only. |
| `sha256` | hex nullable | Required when snapshot exists. |
| `access_class` | enum | `PUBLIC_HTML`, `PUBLIC_PDF`, `LOGIN_REQUIRED`, `PAID_ONLY`, etc. |

## `attributed_claim`

| Field | Type | Notes |
| --- | --- | --- |
| `claim_id` | string PK | Stable row ID. |
| `game_id` | string FK nullable | Subject if game-specific. |
| `period` | string/date range | Claim period. |
| `claim_text_summary` | string | Neutral summary, not a long quote. |
| `attributed_to` | string | Analyst/publisher/source. |
| `source_id` | string FK | Required. |
| `claim_type` | enum | `PERFORMANCE_ATTRIBUTION`, `MILESTONE`, etc. |
| `claim_status` | enum | `ATTRIBUTED_CLAIM`, `CORROBORATED`, `DISPUTED`, `UNKNOWN`. |
| `our_causal_conclusion` | boolean | Must be false during the pilot. |

## Evidence class enum

`OFFICIAL_REPORTED`, `INDUSTRY_ESTIMATE`, `RANK_OBSERVED`, `EVENT_OFFICIAL`, `SECONDARY_CONTEXT`, `UNKNOWN`.

## Temporal rules

- `published_at` is never substituted for `period_start`/`period_end`.
- Point-in-time observations use equal start/end timestamps or an explicit observation-kind field.
- “Last Month” stays unresolved until the source exposes bounds; retrieval month is not silently converted into an observation month.
- Month records use closed calendar bounds or a normalized month key plus timezone policy.

