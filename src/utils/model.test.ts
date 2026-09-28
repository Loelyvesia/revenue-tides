import { mount } from '@vue/test-utils'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import QuarterPrism from '../components/prism/QuarterPrism.vue'
import type { Caveat, Finding, ProjectMetadata, SeriesDetail, SeriesIndexRecord, SourceRecord, WebManifest } from '../types/webData'
import {
  assertNormalizedComparison,
  formatKrwMillion,
  groupByQuarter,
  observationMetric,
  prefersReducedMotion,
  resolveSources,
  sourceIdsForQuarter,
} from './model'

function json<T>(relative: string): T {
  return JSON.parse(readFileSync(resolve(process.cwd(), 'data/web', relative), 'utf8')) as T
}

const manifest = json<WebManifest>('manifest.json')
const project = json<ProjectMetadata>('project.json')
const series = json<SeriesIndexRecord[]>('series_index.json')
const findings = json<Finding[]>('findings.json')
const sources = json<SourceRecord[]>('sources.json')
const caveats = json<Caveat[]>('caveats.json')
const detail = (id: string): SeriesDetail => json<SeriesDetail>(`series/${id}.json`)
const allDetails = series.map((record) => detail(record.series_id))
const allObservations = allDetails.flatMap((record) => record.observations)

describe('frozen public data', () => {
  it('loads the public manifest', () => expect(manifest.webdata_version).toBe('revenue-tides-webdata-1.0.0'))
  it('contains exactly nine series', () => expect(series).toHaveLength(9))
  it('contains exactly six Findings', () => expect(findings).toHaveLength(6))
  it('keeps headline IDs F1/F2/F4', () => expect(findings.filter((item) => item.headline).map((item) => item.finding_id)).toEqual(['F1', 'F2', 'F4']))
  it('keeps 75 observations reachable', () => expect(allObservations).toHaveLength(75))
  it('keeps 26 events reachable', () => expect(allDetails.flatMap((item) => item.events)).toHaveLength(26))
  it('keeps entity types visible', () => expect(new Set(series.map((item) => item.entity_type))).toEqual(new Set(['GAME_TITLE', 'IP'])))
  it('loads all project caveats', () => expect(caveats).toHaveLength(6))
  it('retains the curated-event caveat', () => expect(caveats.some((item) => item.caveat_id === 'CAVEAT_CURATED_EVENTS')).toBe(true))
  it('forbids absolute cross-company comparison', () => expect(project.comparison_policy.absolute_cross_company).toBe('NOT_COMPARABLE'))
})

describe('series rendering models', () => {
  it('groups direct observations by quarter', () => expect(groupByQuarter(detail('series_nikke'))).toHaveLength(8))
  it('groups Lineage overlap into two observations', () => expect(groupByQuarter(detail('series_lineage_m')).find((group) => group.quarter === '2025Q2')?.observations).toHaveLength(2))
  it('keeps all three Lineage overlaps representable', () => expect(groupByQuarter(detail('series_lineage_m')).filter((group) => group.observations.length === 2)).toHaveLength(3))
  it('preserves version identity on every observation', () => expect(allObservations.every((item) => item.metric_version && item.metric_definition_id)).toBe(true))
  it('disables cross-version change', () => expect(detail('series_lineage_w').metric_versions.every((item) => item.version_break?.cross_version_change_allowed === false)).toBe(true))
  it('restarts the baseline for each version', () => {
    const lineage = detail('series_lineage_w')
    for (const version of lineage.metric_versions) {
      const first = lineage.observations.filter((item) => item.metric_version === version.version).sort((a, b) => a.period_index - b.period_index)[0]
      expect(first?.baseline_index).toBe(100)
    }
  })
  it('does not provide a first-period QoQ after baseline restart', () => {
    const v2 = detail('series_lineage_w').observations.find((item) => item.observation_id === 'obs_lw_v2_2025q2')
    expect(v2?.qoq.eligible).toBe(false)
  })
  it('retains derived uncertainty bounds', () => expect(allObservations.filter((item) => item.evidence_class === 'DERIVED_FROM_OFFICIAL').every((item) => item.lower_bound !== null && item.upper_bound !== null)).toBe(true))
  it('retains sign-sensitive derived states', () => expect(allObservations.filter((item) => item.derived?.direction_sign_stable === false)).toHaveLength(9))
  it('keeps direct observations without fabricated bounds', () => expect(allObservations.filter((item) => item.evidence_class === 'OFFICIAL_REPORTED').every((item) => item.lower_bound === null && item.upper_bound === null)).toBe(true))
  it('never turns missing values into zero', () => expect(allObservations.some((item) => item.value === null && item.value === 0)).toBe(false))
  it('resolves observation metric definitions', () => {
    const nikke = detail('series_nikke')
    expect(observationMetric(nikke.observations[0]!, nikke.metric_versions)?.metric_definition_id).toBe('md_su_ip_revenue_v1')
  })
  it('resolves evidence sources', () => expect(resolveSources(['src_su_2q26_fs'], sources)[0]?.company).toBe('SHIFT UP'))
  it('collects event source IDs separately', () => {
    const stellar = detail('series_stellar_blade')
    const quarter = groupByQuarter(stellar).find((group) => group.quarter === '2025Q2')!
    expect(sourceIdsForQuarter(quarter, stellar)).toContain('src_ps_stellar_pc_html')
  })
  it('event records contain no causal field', () => expect(allDetails.flatMap((item) => item.events).every((event) => !('caused_revenue_change' in event))).toBe(true))
  it('issuer claims remain attributed', () => expect(allDetails.flatMap((item) => item.attributed_claims).every((claim) => claim.attributed)).toBe(true))
})

describe('Finding reproduction', () => {
  const finding = (id: string) => findings.find((item) => item.finding_id === id)!
  const obs = (id: string) => allObservations.find((item) => item.observation_id === id)!
  it('F1 references the three Lineage series', () => expect(finding('F1').series_ids).toEqual(['series_lineage_m', 'series_lineage_2m', 'series_lineage_w']))
  it('F1 preserves same-quarter Lineage M differences', () => {
    const differences = ['2025q2', '2025q3', '2025q4'].map((quarter) => obs(`obs_lm_v2_${quarter}`).value! - obs(`obs_lm_v1_${quarter}`).value!)
    expect(Math.min(...differences)).toBe(6797)
    expect(Math.max(...differences)).toBe(13455)
  })
  it('F2 reproduces 7.012 billion KRW', () => expect(Number((obs('obs_stellar_2025q1').value! / 1000).toFixed(3))).toBe(7.012))
  it('F2 reproduces 65.719 billion KRW', () => expect(Number((obs('obs_stellar_2025q2').value! / 1000).toFixed(3))).toBe(65.719))
  it('F2 reproduces +837.3%', () => expect(Number(obs('obs_stellar_2025q2').qoq.percent_change!.toFixed(1))).toBe(837.3))
  it('F2 preserves the non-causal limitation', () => expect(finding('F2').forbidden_interpretation).toContain('does not prove'))
  it('F3 reproduces +32.4%', () => expect(Number(obs('obs_nikke_2026q2').qoq.percent_change!.toFixed(1))).toBe(32.4))
  it('F3 reproduces 4.1% below peak', () => expect(Number(Math.abs(obs('obs_nikke_2026q2').drawdown_percent!).toFixed(1))).toBe(4.1))
  it('F3 remains unrecovered inside the window', () => expect(obs('obs_nikke_2026q2').recovery.status).toBe('NOT_RECOVERED_WITHIN_OBSERVED_WINDOW'))
  it('F4 reproduces the initial 20.7% drawdown', () => expect(Number(Math.abs(obs('obs_bd_2025q2').drawdown_percent!).toFixed(1))).toBe(20.7))
  it('F4 preserves three-quarter recovery', () => expect(obs('obs_bd_2025q3').recovery.quarters).toBe(3))
  it('F4 reproduces the ending 30.8% drawdown', () => expect(Number(Math.abs(obs('obs_bd_2026q2').drawdown_percent!).toFixed(1))).toBe(30.8))
  it('F5 is restricted to royalty-integrated v2', () => expect(finding('F5').metric_definition_ids).toEqual(['md_nc_lineage_w_royalty_v2']))
  it('F5 reproduces -35.3%', () => expect(finding('F5').quantitative_summary).toContain('-35.3%'))
  it('F6 reproduces 9 of 15', () => {
    const eligible = allObservations.filter((item) => finding('F6').observation_ids.includes(item.observation_id) && item.qoq.eligible)
    expect(eligible).toHaveLength(15)
    expect(eligible.filter((item) => item.derived?.direction_sign_stable === false)).toHaveLength(9)
  })
  it('F6 reproduces 60.0%', () => expect(finding('F6').quantitative_summary).toContain('60.0%'))
})

describe('formatting and policy', () => {
  it('formats canonical million values without fake precision', () => expect(formatKrwMillion(7011.668848)).toBe('KRW 7.012 bn'))
  it('does not format unavailable values as zero', () => expect(formatKrwMillion(null)).toBe('Unavailable'))
  it('allows only baseline-index comparison', () => expect(assertNormalizedComparison('BASELINE_INDEX')).toBe('BASELINE_INDEX'))
  it('rejects an absolute comparison request', () => expect(() => assertNormalizedComparison('ABSOLUTE_REVENUE')).toThrow('unavailable'))
  it('can detect reduced-motion preference', () => expect(typeof prefersReducedMotion()).toBe('boolean'))
})

describe('Quarter Prism interaction', () => {
  const lineage = detail('series_lineage_m')
  const wrapperFactory = () => mount(QuarterPrism, { props: { detail: lineage, sources, caveats, initialQuarter: '2025Q2' }, attachTo: document.body })
  it('provides an accessible named analytical SVG', () => {
    const wrapper = wrapperFactory()
    expect(wrapper.get('svg[role="img"]').attributes('aria-labelledby')).toContain('prism-title')
    wrapper.unmount()
  })
  it('announces selection in a polite live region', () => {
    const wrapper = wrapperFactory()
    expect(wrapper.get('[aria-live="polite"]').text()).toContain('Lineage M')
    wrapper.unmount()
  })
  it('renders both metric lanes in an overlap quarter', () => {
    const wrapper = wrapperFactory()
    expect(wrapper.findAll('.metric-lane')).toHaveLength(2)
    wrapper.unmount()
  })
  it('navigates with the next-quarter button', async () => {
    const wrapper = wrapperFactory()
    await wrapper.findAll('.prism-controls button')[1]!.trigger('click')
    expect((wrapper.get('select').element as HTMLSelectElement).value).toBe('2025Q3')
    wrapper.unmount()
  })
  it('respects previous-quarter bounds', () => {
    const wrapper = mount(QuarterPrism, { props: { detail: lineage, sources, caveats, initialQuarter: '2024Q3' } })
    expect(wrapper.findAll('.prism-controls button')[0]!.attributes('disabled')).toBeDefined()
  })
  it('supports direct quarter selection', async () => {
    const wrapper = wrapperFactory()
    await wrapper.get('select').setValue('2026Q2')
    expect(wrapper.get('.reading-pane h3').text()).toContain('2026Q2')
    wrapper.unmount()
  })
  it('supports keyboard left and right navigation', async () => {
    const wrapper = wrapperFactory()
    await wrapper.get('.quarter-prism').trigger('keydown', { key: 'ArrowRight' })
    expect((wrapper.get('select').element as HTMLSelectElement).value).toBe('2025Q3')
    await wrapper.get('.quarter-prism').trigger('keydown', { key: 'ArrowLeft' })
    expect((wrapper.get('select').element as HTMLSelectElement).value).toBe('2025Q2')
    wrapper.unmount()
  })
  it('exposes a mobile stacked reading model in the same DOM', () => {
    const wrapper = wrapperFactory()
    expect(wrapper.get('.reading-pane').exists()).toBe(true)
    expect(wrapper.get('.quarter-list').exists()).toBe(true)
    wrapper.unmount()
  })
})
