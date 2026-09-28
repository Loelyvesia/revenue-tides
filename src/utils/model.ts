import type { Finding, MetricVersion, Observation, SeriesDetail, SourceRecord } from '../types/webData'

export interface QuarterModel {
  quarter: string
  periodIndex: number
  observations: Observation[]
}

export function groupByQuarter(detail: SeriesDetail): QuarterModel[] {
  const groups = new Map<string, QuarterModel>()
  for (const observation of detail.observations) {
    const current = groups.get(observation.quarter)
    if (current) current.observations.push(observation)
    else groups.set(observation.quarter, { quarter: observation.quarter, periodIndex: observation.period_index, observations: [observation] })
  }
  return [...groups.values()]
    .sort((a, b) => a.periodIndex - b.periodIndex)
    .map((group) => ({ ...group, observations: [...group.observations].sort((a, b) => a.metric_version.localeCompare(b.metric_version)) }))
}

export function observationMetric(observation: Observation, versions: MetricVersion[]): MetricVersion | null {
  return versions.find((version) => version.metric_definition_id === observation.metric_definition_id) ?? null
}

export function resolveSources(ids: string[], sources: SourceRecord[]): SourceRecord[] {
  const wanted = new Set(ids)
  return sources.filter((source) => wanted.has(source.source_id))
}

export function formatKrwMillion(value: number | null): string {
  if (value === null) return 'Unavailable'
  if (Math.abs(value) >= 1000) return `KRW ${(value / 1000).toLocaleString('en-US', { maximumFractionDigits: 3 })} bn`
  return `KRW ${value.toLocaleString('en-US', { maximumFractionDigits: 3 })}m`
}

export function formatPercent(value: number | null, digits = 1): string {
  if (value === null) return 'Unavailable'
  const sign = value > 0 ? '+' : ''
  return `${sign}${value.toFixed(digits)}%`
}

export function sourceIdsForQuarter(quarter: QuarterModel, detail: SeriesDetail): string[] {
  const ids = new Set(quarter.observations.map((observation) => observation.source_id))
  detail.events.filter((event) => event.fiscal_period === quarter.quarter).forEach((event) => ids.add(event.source_id))
  detail.attributed_claims.filter((claim) => claim.period === quarter.quarter).forEach((claim) => ids.add(claim.source_id))
  return [...ids]
}

export function findingById(findings: Finding[], id: string): Finding | null {
  return findings.find((finding) => finding.finding_id === id) ?? null
}

export function assertNormalizedComparison(mode: 'BASELINE_INDEX' | 'ABSOLUTE_REVENUE'): 'BASELINE_INDEX' {
  if (mode !== 'BASELINE_INDEX') throw new Error('Absolute cross-company comparison is unavailable')
  return mode
}

export function prefersReducedMotion(): boolean {
  return typeof window !== 'undefined'
    && typeof window.matchMedia === 'function'
    && window.matchMedia('(prefers-reduced-motion: reduce)').matches
}
