export type EvidenceClass = 'OFFICIAL_REPORTED' | 'DERIVED_FROM_OFFICIAL'
export type EntityType = 'GAME_TITLE' | 'IP'
export type MissingnessState =
  | 'AVAILABLE'
  | 'NOT_REPORTED'
  | 'NOT_APPLICABLE'
  | 'METRIC_VERSION_BREAK'
  | 'DERIVATION_UNAVAILABLE'
  | 'SOURCE_UNAVAILABLE'
  | 'UNRESOLVED'
  | 'OUTSIDE_SERIES_WINDOW'

export interface ManifestFile {
  path: string
  bytes: number
  sha256: string
  record_count: number | null
}

export interface WebManifest {
  webdata_version: string
  method_version: string
  findings_version: string
  data_cutoff: string
  build_version: string
  build_date: string
  series_count: number
  observation_count: number
  event_count: number
  finding_count: number
  headline_finding_ids: string[]
  company_count: number
  source_count: number
  global_caveat_ids: string[]
  files: ManifestFile[]
}

export interface CompanyRecord {
  company_id: string
  name: string
  reporting_currency: string
  fiscal_calendar_status: string
  IR_url: string
}

export interface ProjectMetadata {
  project_id: string
  title_zh: string
  title_en: string
  subtitle_zh: string
  subtitle_en: string
  method_version: string
  findings_version: string
  webdata_version: string
  data_cutoff: string
  primary_temporal_unit: 'FISCAL_QUARTER'
  corpus_series_count: number
  observation_count: number
  event_count: number
  claim_count: number
  headline_finding_ids: string[]
  global_caveats: string[]
  comparison_policy: {
    absolute_cross_company: 'NOT_COMPARABLE'
    normalized_unitless_shape: string
    within_stable_series: 'WITHIN_SERIES_ONLY'
  }
  causality_policy: string
  companies: CompanyRecord[]
}

export interface SeriesIndexRecord {
  series_id: string
  name: string
  publisher_defined_name: string
  entity_type: EntityType
  company_id: string
  company_name: string
  platform_scope: string
  evidence_mode: EvidenceClass
  first_period: string
  last_period: string
  quarter_count: number
  metric_version_count: number
  event_count: number
  claim_count: number
  finding_ids: string[]
  headline_finding_ids: string[]
  detail_path: string
  status: 'VALIDATED'
}

export interface VersionBreak {
  break_before: string | null
  break_after: string | null
  break_reason: string
  cross_version_change_allowed: false
  baseline_restart: true
  same_quarter_overlap: boolean
}

export interface MetricVersion {
  metric_definition_id: string
  label: string
  version: string
  valid_period: { first: string; last: string }
  comparable_group_id: string
  economic_meaning: string
  accounting_scope: string
  platform_scope: string
  geographic_scope: string
  unit_basis: string
  evidence_class: EvidenceClass
  comparison_scope: 'WITHIN_SERIES_ONLY'
  version_break: VersionBreak | null
  caveat_ids: string[]
}

export interface DerivedObservationFields {
  derivation_ref: string
  share_percent: number
  share_rounding_note: string
  direction_sign_stable: boolean | null
  point_change_sign: string
  lower_case_sign: string
  upper_case_sign: string
}

export interface Observation {
  observation_id: string
  quarter: string
  period_key: string
  period_index: number
  period_start: string
  period_end: string
  metric_definition_id: string
  metric_version: string
  value: number | null
  unit: 'KRW_million'
  currency: 'KRW'
  evidence_class: EvidenceClass
  lower_bound: number | null
  upper_bound: number | null
  missingness_state: MissingnessState
  qoq: {
    absolute_change: number | null
    percent_change: number | null
    eligible: boolean
    previous_observation_id: string | null
  }
  baseline_index: number | null
  rolling_peak: number | null
  drawdown_percent: number | null
  recovery: { status: string; quarters: number | null }
  eligibility: {
    qoq: boolean
    baseline: boolean
    drawdown: boolean
    volatility: boolean
  }
  derived: DerivedObservationFields | null
  source_id: string
  source_page: string | null
}

export interface EventRecord {
  event_id: string
  series_id: string
  name: string
  event_type: string
  start_date: string
  end_date: string | null
  date_precision: string
  fiscal_period: string
  platform_scope: string
  region_scope: string
  source_id: string
  curated: true
}

export interface AttributedClaim {
  claim_id: string
  series_id: string
  period: string
  issuer: string
  summary: string
  claim_type: string
  source_id: string
  attributed: true
}

export interface SeriesIdentity {
  series_id: string
  entity: string
  publisher_defined_name: string
  entity_type: EntityType
  company_id: string
  company: string
  platform_scope: string
  reporting_scope: string[]
  caveat_ids: string[]
}

export interface SeriesDetail {
  series_id: string
  identity: SeriesIdentity
  metric_versions: MetricVersion[]
  observations: Observation[]
  events: EventRecord[]
  attributed_claims: AttributedClaim[]
  findings: string[]
  sources: string[]
}

export interface Finding {
  finding_id: string
  title_zh: string
  title_en: string
  statement_zh: string
  statement_en: string
  finding_class: string
  strength: string
  series_ids: string[]
  period_start: string
  period_end: string
  metric_definition_ids: string[]
  evidence_class: string
  quantitative_summary: string
  uncertainty_note: string
  limitations: string
  forbidden_interpretation: string
  headline: boolean
  observation_ids: string[]
  event_ids: string[]
  claim_ids: string[]
  source_ids: string[]
  caveat_ids: string[]
}

export interface SourceRecord {
  source_id: string
  company: string
  document_title: string | null
  document_type: string
  published_at: string | null
  reporting_period: string | null
  canonical_url: string
  specific_document_url: string
  source_pages: string[]
  access_note: string
}

export interface Caveat {
  caveat_id: string
  text_zh: string
  text_en: string
}

export interface BootstrapData {
  manifest: WebManifest
  project: ProjectMetadata
  series: SeriesIndexRecord[]
  findings: Finding[]
  caveats: Caveat[]
}

export type LoadState = 'idle' | 'loading' | 'ready' | 'error'
