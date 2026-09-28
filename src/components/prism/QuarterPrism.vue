<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { Caveat, Observation, SeriesDetail, SourceRecord } from '../../types/webData'
import { formatKrwMillion, formatPercent, groupByQuarter, observationMetric, resolveSources, sourceIdsForQuarter } from '../../utils/model'
import EventRail from './EventRail.vue'
import SourceList from '../evidence/SourceList.vue'

const props = defineProps<{
  detail: SeriesDetail
  sources: SourceRecord[]
  caveats: Caveat[]
  initialQuarter?: string
}>()

const quarterGroups = computed(() => groupByQuarter(props.detail))
const selectedQuarter = ref(props.initialQuarter ?? quarterGroups.value[0]?.quarter ?? '')
const evidenceOpen = ref(false)

watch(() => props.detail.series_id, () => {
  const preferred = props.initialQuarter && quarterGroups.value.some((group) => group.quarter === props.initialQuarter)
    ? props.initialQuarter
    : quarterGroups.value[0]?.quarter
  selectedQuarter.value = preferred ?? ''
  evidenceOpen.value = false
})

const selectedIndex = computed(() => Math.max(0, quarterGroups.value.findIndex((group) => group.quarter === selectedQuarter.value)))
const selected = computed(() => quarterGroups.value[selectedIndex.value] ?? quarterGroups.value[0])
const selectedEvents = computed(() => props.detail.events.filter((event) => event.fiscal_period === selected.value?.quarter))
const selectedClaims = computed(() => props.detail.attributed_claims.filter((claim) => claim.period === selected.value?.quarter))
const selectedSources = computed(() => selected.value ? resolveSources(sourceIdsForQuarter(selected.value, props.detail), props.sources) : [])
const hasVersionBreak = computed(() => props.detail.metric_versions.some((metric) => metric.version_break !== null))
const versionStartIndex = computed(() => Math.max(0, quarterGroups.value.findIndex((group) => group.observations.some((observation) => observation.metric_version.includes('royalty')))))
const previousQuarter = computed(() => quarterGroups.value[selectedIndex.value - 1]?.quarter ?? '')
const nextQuarter = computed(() => quarterGroups.value[selectedIndex.value + 1]?.quarter ?? '')

const allValues = computed(() => props.detail.observations.flatMap((observation) => [observation.lower_bound, observation.value, observation.upper_bound]).filter((value): value is number => value !== null))
const minValue = computed(() => Math.min(...allValues.value))
const maxValue = computed(() => Math.max(...allValues.value))

function xFor(index: number): number {
  if (quarterGroups.value.length <= 1) return 500
  return 75 + (index / (quarterGroups.value.length - 1)) * 850
}

function yFor(value: number | null): number {
  if (value === null || maxValue.value === minValue.value) return 180
  return 285 - ((value - minValue.value) / (maxValue.value - minValue.value)) * 205
}

function pointsFor(metricVersion: string): string {
  return props.detail.observations
    .filter((observation) => observation.metric_version === metricVersion && observation.value !== null)
    .sort((a, b) => a.period_index - b.period_index)
    .map((observation) => {
      const index = quarterGroups.value.findIndex((group) => group.quarter === observation.quarter)
      return `${xFor(index)},${yFor(observation.value)}`
    })
    .join(' ')
}

function step(delta: number): void {
  const next = Math.min(Math.max(selectedIndex.value + delta, 0), quarterGroups.value.length - 1)
  selectedQuarter.value = quarterGroups.value[next]?.quarter ?? selectedQuarter.value
}

function onKeydown(event: KeyboardEvent): void {
  if (event.target instanceof HTMLSelectElement || event.target instanceof HTMLButtonElement || event.target instanceof HTMLAnchorElement) return
  if (event.key === 'ArrowLeft') { event.preventDefault(); step(-1) }
  if (event.key === 'ArrowRight') { event.preventDefault(); step(1) }
}

function accessibleObservation(observation: Observation): string {
  const bounds = observation.lower_bound !== null && observation.upper_bound !== null
    ? `，兼容区间 ${formatKrwMillion(observation.lower_bound)} 至 ${formatKrwMillion(observation.upper_bound)}`
    : ''
  return `${observation.metric_version}，${formatKrwMillion(observation.value)}，${observation.evidence_class}${bounds}`
}

const liveSummary = computed(() => {
  if (!selected.value) return ''
  const lanePhrase = selected.value.observations.length > 1 ? `同季度 ${selected.value.observations.length} 个报告口径` : '单一报告口径'
  return `${props.detail.identity.entity}，${selected.value.quarter}，${lanePhrase}。${selected.value.observations.map(accessibleObservation).join('；')}。事件 ${selectedEvents.value.length} 个。${selectedClaims.value.length ? '有发行方说明。' : '无发行方说明。'}`
})
</script>

<template>
  <div class="quarter-prism" tabindex="0" aria-label="季度棱镜交互区；使用左右方向键切换季度" @keydown="onKeydown">
    <div class="prism-controls" aria-label="季度导航">
      <button class="native-control step-control" :disabled="selectedIndex === 0" :aria-label="`上一季度 ${previousQuarter}`" @click="step(-1)"><span class="visually-hidden">上一季度</span><span aria-hidden="true">←</span><small>{{ previousQuarter || 'START' }}</small></button>
      <label>
        <span class="visually-hidden">直接选择季度</span>
        <select v-model="selectedQuarter" class="native-control" aria-label="直接选择季度">
          <option v-for="group in quarterGroups" :key="group.quarter" :value="group.quarter">{{ group.quarter }}</option>
        </select>
      </label>
      <button class="native-control step-control next" :disabled="selectedIndex === quarterGroups.length - 1" :aria-label="`下一季度 ${nextQuarter}`" @click="step(1)"><span class="visually-hidden">下一季度</span><small>{{ nextQuarter || 'END' }}</small><span aria-hidden="true">→</span></button>
    </div>

    <div class="desktop-prism">
      <div class="instrument-header"><span class="numeric">READING WINDOW / {{ selected?.quarter }}</span><span>{{ detail.identity.entity }}</span><span class="numeric">{{ selectedIndex + 1 }} / {{ quarterGroups.length }}</span></div>
      <svg class="trajectory" viewBox="0 0 1000 360" role="img" :aria-labelledby="`prism-title-${detail.series_id} prism-desc-${detail.series_id}`">
        <title :id="`prism-title-${detail.series_id}`">{{ detail.identity.entity }} 季度轨迹</title>
        <desc :id="`prism-desc-${detail.series_id}`">{{ liveSummary }} 不同指标版本的轨迹保持断开，事件位于图外的独立轨道。</desc>
        <defs>
          <pattern id="uncertainty-hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <line x1="0" y1="0" x2="0" y2="8" stroke="currentColor" stroke-width="2" />
          </pattern>
        </defs>
        <g class="grid" aria-hidden="true">
          <line v-for="y in [80, 145, 210, 285]" :key="y" x1="60" :y1="y" x2="940" :y2="y" />
        </g>
        <g class="reading-focus" aria-hidden="true">
          <rect class="reading-window" :x="xFor(selectedIndex) - 42" y="40" width="84" height="270" />
          <path :d="`M ${xFor(selectedIndex)-52} 40 h20 M ${xFor(selectedIndex)+32} 40 h20 M ${xFor(selectedIndex)-52} 310 h20 M ${xFor(selectedIndex)+32} 310 h20`" />
          <text :x="xFor(selectedIndex)" y="25" text-anchor="middle">{{ selected?.quarter }}</text>
        </g>
        <g v-if="hasVersionBreak" class="version-seam" aria-label="指标版本断点">
          <line :x1="xFor(versionStartIndex) - 6" y1="42" :x2="xFor(versionStartIndex) - 6" y2="310" />
          <line :x1="xFor(versionStartIndex) + 2" y1="42" :x2="xFor(versionStartIndex) + 2" y2="310" />
          <path :d="`M ${xFor(versionStartIndex)-13} 42 l11 -8 l11 8`" />
          <text :x="xFor(versionStartIndex) + 12" y="58">METRIC DEFINITION CHANGE</text>
        </g>
        <polyline v-for="(metric, metricIndex) in detail.metric_versions" :key="metric.metric_definition_id" :class="['trajectory-line', `lane-${metricIndex}`]" :points="pointsFor(metric.version)" />
        <g v-for="(group, index) in quarterGroups" :key="group.quarter">
          <text :x="xFor(index)" y="334" text-anchor="middle" class="quarter-label">{{ group.quarter }}</text>
          <g v-for="observation in group.observations" :key="observation.observation_id">
            <circle v-if="observation.evidence_class === 'OFFICIAL_REPORTED'" :cx="xFor(index)" :cy="yFor(observation.value)" r="6" :class="['direct-mark', { selected: group.quarter === selected?.quarter }]" />
            <path v-else :d="`M ${xFor(index)} ${yFor(observation.value) - 7} L ${xFor(index) + 7} ${yFor(observation.value)} L ${xFor(index)} ${yFor(observation.value) + 7} L ${xFor(index) - 7} ${yFor(observation.value)} Z`" :class="['derived-mark', { selected: group.quarter === selected?.quarter }]" />
            <g v-if="observation.lower_bound !== null && observation.upper_bound !== null" class="whisker">
              <line :x1="xFor(index)" :x2="xFor(index)" :y1="yFor(observation.upper_bound)" :y2="yFor(observation.lower_bound)" />
              <line :x1="xFor(index) - 5" :x2="xFor(index) + 5" :y1="yFor(observation.upper_bound)" :y2="yFor(observation.upper_bound)" />
              <line :x1="xFor(index) - 5" :x2="xFor(index) + 5" :y1="yFor(observation.lower_bound)" :y2="yFor(observation.lower_bound)" />
            </g>
          </g>
        </g>
      </svg>
      <p class="visual-summary">{{ liveSummary }}</p>
    </div>

    <section v-if="selected" class="reading-pane" aria-label="所选季度分解">
      <header>
        <div>
          <p class="eyebrow">SELECTED QUARTER / INSTRUMENT READING</p>
          <h3>{{ detail.identity.entity }} · <span class="numeric">{{ selected.quarter }}</span></h3>
        </div>
        <span class="tag">{{ detail.identity.entity_type }}</span>
      </header>
      <p class="scope">{{ detail.identity.company }} · {{ detail.identity.platform_scope }}</p>
      <p v-if="selected.observations.length > 1" class="overlap-note">同一季度 · 不同报告口径。两个数值同时保留，不表示增长或先后变化。</p>
      <div class="metric-lanes">
        <article v-for="observation in selected.observations" :key="observation.observation_id" :class="['metric-lane', observation.evidence_class === 'DERIVED_FROM_OFFICIAL' ? 'derived' : 'direct']">
          <div class="lane-mark" aria-hidden="true"></div>
          <div>
            <span class="eyebrow">{{ observation.metric_version }}</span>
            <strong class="metric-value numeric">{{ observation.value === null ? observation.missingness_state : formatKrwMillion(observation.value) }}</strong>
            <p>{{ observationMetric(observation, detail.metric_versions)?.label ?? 'Metric definition unavailable' }}</p>
            <dl>
              <div><dt>证据</dt><dd>{{ observation.evidence_class === 'OFFICIAL_REPORTED' ? 'Official reported' : 'Derived from official' }}</dd></div>
              <div><dt>范围</dt><dd>{{ observationMetric(observation, detail.metric_versions)?.platform_scope ?? detail.identity.platform_scope }}</dd></div>
              <div><dt>环比</dt><dd class="numeric">{{ observation.qoq.eligible ? formatPercent(observation.qoq.percent_change) : '不可用 / 不跨口径计算' }}</dd></div>
              <div><dt>恢复状态</dt><dd>{{ observation.recovery.status }}</dd></div>
            </dl>
            <div v-if="observation.derived" class="uncertainty-block">
              <div class="interval-geometry" aria-hidden="true"><span></span><i></i></div>
              <p class="numeric">兼容区间 {{ formatKrwMillion(observation.lower_bound) }} — {{ formatKrwMillion(observation.upper_bound) }}</p>
              <p>官方取整占比 {{ observation.derived.share_percent }}% · {{ observation.derived.share_rounding_note }}</p>
              <strong>{{ observation.derived.direction_sign_stable === false ? '方向受取整区间影响' : observation.derived.direction_sign_stable === true ? '方向在兼容区间内稳定' : '首期：无可比较方向' }}</strong>
            </div>
          </div>
        </article>
      </div>
      <div v-if="hasVersionBreak" class="version-note">
        <span class="double-seam" aria-hidden="true"></span>
        <div><strong>报告定义校准缝</strong><p>旧口径与 royalty-integrated 口径不拼接；跨版本 QoQ 不可用，基线在新版本重启。</p></div>
      </div>
    </section>

    <EventRail v-if="selected" :events="selectedEvents" :claims="selectedClaims" :quarter="selected.quarter" />

    <div class="source-action">
      <button class="source-trigger" :aria-expanded="evidenceOpen" @click="evidenceOpen = !evidenceOpen"><span class="visually-hidden">查看证据与来源</span>{{ evidenceOpen ? 'CLOSE SOURCE ×' : 'SOURCE ↗' }}</button>
      <SourceList v-if="evidenceOpen" :sources="selectedSources" />
    </div>

    <nav class="quarter-list" aria-label="直接季度列表">
      <button v-for="group in quarterGroups" :key="group.quarter" class="quarter-button" :aria-current="group.quarter === selected?.quarter ? 'true' : undefined" @click="selectedQuarter = group.quarter">
        <span class="numeric">{{ group.quarter }}</span>
        <small>{{ group.observations.length > 1 ? `${group.observations.length} 个口径` : group.observations[0]?.evidence_class === 'DERIVED_FROM_OFFICIAL' ? '派生区间' : '官方披露' }}</small>
      </button>
    </nav>
    <p class="visually-hidden" aria-live="polite">{{ liveSummary }}</p>
  </div>
</template>

<style scoped>
.quarter-prism { position: relative; padding: clamp(1.25rem, 3vw, 2.5rem) 0 0; border-block: 2px solid var(--text-primary); outline: none; }
.quarter-prism:focus-visible { outline: 3px solid var(--focus); outline-offset: 5px; }
.prism-controls { display: grid; grid-template-columns: minmax(7.5rem, auto) minmax(8rem, 11rem) minmax(7.5rem, auto); justify-content: center; gap: .35rem; margin-bottom: 1.5rem; }
.prism-controls label { display: block; }.prism-controls select { width: 100%; border-color: var(--text-primary); text-align: center; font-family: var(--font-numeric); font-weight: 650; }.step-control { display: flex; justify-content: space-between; align-items: center; gap: .75rem; border-color: transparent; background: transparent; }.step-control small { color: var(--text-secondary); font: .68rem var(--font-numeric); }.step-control.next { text-align: right; }
.desktop-prism { border-top: 1px solid var(--rule-border); }.instrument-header { display: grid; grid-template-columns: 1fr auto 1fr; gap: 1rem; align-items: center; padding: .8rem 0; border-bottom: 1px solid var(--rule-grid); color: var(--text-secondary); font-size: .72rem; letter-spacing: .06em; }.instrument-header span:last-child { text-align: right; }
.trajectory { display: block; width: 100%; min-height: 300px; color: var(--uncertainty); }
.grid line { stroke: var(--rule-grid); stroke-width: .75; }
.reading-window { fill: var(--accent-wash); stroke: var(--accent-primary); stroke-width: 1.5; transition: x var(--motion-signature) cubic-bezier(.2,.7,.2,1); }
.reading-focus path { fill: none; stroke: var(--accent-primary); stroke-width: 2; }.reading-focus text { fill: var(--accent-strong); font: 650 12px var(--font-numeric); letter-spacing: .06em; }
.trajectory-line { fill: none; stroke: var(--accent-primary); stroke-width: 1.75; vector-effect: non-scaling-stroke; }
.lane-1 { stroke: var(--text-primary); stroke-dasharray: 7 5; }
.direct-mark { fill: var(--accent-primary); stroke: var(--surface-primary); stroke-width: 1.5; }
.derived-mark { fill: var(--surface-primary); stroke: var(--evidence-derived); stroke-width: 2; }
.direct-mark.selected, .derived-mark.selected { stroke: var(--text-primary); stroke-width: 3; transform-box: fill-box; transform-origin: center; transform: scale(1.25); }
.whisker line { stroke: var(--uncertainty); stroke-width: 2; }
.version-seam line, .version-seam path { fill: none; stroke: var(--text-primary); stroke-width: 1.5; }.version-seam text { fill: var(--text-primary); font: 600 10px var(--font-numeric); letter-spacing: .06em; }
.quarter-label { fill: var(--text-secondary); font: 12px var(--font-numeric); }
.visual-summary { margin: 0 auto 1rem; max-width: 55rem; color: var(--text-secondary); font-size: 0.875rem; }
.reading-pane { display: grid; grid-template-columns: minmax(16rem, .34fr) minmax(0, 1fr); gap: 1rem 3rem; padding-block: 2rem; border-block: 1px solid var(--rule-border); }
.reading-pane header { display: flex; justify-content: space-between; gap: 1rem; align-items: start; }
.reading-pane header, .scope, .overlap-note, .version-note { grid-column: 1; }.scope { color: var(--text-secondary); }
.overlap-note { padding: .75rem 0; border-block: 1px solid var(--text-primary); font-weight: 650; }
.metric-lanes { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 22rem), 1fr)); gap: 1rem; }
.metric-lanes { grid-column: 2; grid-row: 1 / span 5; }.metric-lane { display: grid; grid-template-columns: .8rem 1fr; gap: 1rem; padding: .1rem 0 1rem; border-top: 2px solid var(--text-primary); }
.lane-mark { width: 0.8rem; height: 0.8rem; margin-top: 0.35rem; border-radius: 50%; background: var(--evidence-direct); }
.metric-lane.derived .lane-mark { border-radius: 0; border: 2px solid var(--evidence-derived); background: transparent; transform: rotate(45deg); }
.metric-value { display: block; margin: 0.35rem 0; font-size: clamp(1.65rem, 3vw, 2.4rem); line-height: 1.1; letter-spacing: -.04em; }
.metric-lane p { margin: 0.25rem 0 0.75rem; }
.metric-lane dl { margin: 0; }
.metric-lane dl div { display: grid; grid-template-columns: 6rem 1fr; gap: 0.5rem; padding-block: 0.35rem; border-top: 1px solid var(--rule-grid); }
dt { color: var(--text-secondary); font-size: 0.75rem; } dd { margin: 0; }
.uncertainty-block { margin-top: 1rem; padding: 1rem 0 0; border-top: 1px solid var(--evidence-derived); background-image: repeating-linear-gradient(135deg, transparent 0 7px, rgba(89, 97, 94, 0.08) 7px 9px); }
.interval-geometry { position: relative; height: 1.25rem; margin-bottom: 0.35rem; border-inline: 2px solid var(--uncertainty); }
.interval-geometry::before { content: ''; position: absolute; top: 50%; inset-inline: 0; border-top: 2px solid var(--uncertainty); }
.interval-geometry span { position: absolute; left: 50%; top: 0.25rem; width: 0.75rem; height: 0.75rem; border: 2px solid var(--evidence-derived); background: var(--surface-primary); transform: translateX(-50%) rotate(45deg); }
.version-note { display: grid; grid-template-columns: 1rem 1fr; gap: 0.8rem; margin-top: 1rem; padding: 1rem 0; border-block: 1px solid var(--rule-border); }
.version-note p { margin: 0.15rem 0; }
.double-seam { border-inline: 2px solid var(--text-primary); }
.source-action { display: grid; gap: 0.75rem; margin-top: 1rem; }.source-trigger { justify-self: start; min-height: 44px; padding: 0; border: 0; border-bottom: 1px solid currentColor; color: var(--text-primary); background: transparent; font: 650 .72rem var(--font-numeric); letter-spacing: .08em; cursor: pointer; }
.quarter-list { display: flex; max-width: 100%; min-width: 0; gap: 0; overflow-x: auto; padding: 2rem 0 .25rem; border-top: 1px solid var(--rule-grid); overscroll-behavior-inline: contain; }
.quarter-button { position: relative; min-width: 6.5rem; min-height: 56px; border: 0; border-top: 1px solid var(--rule-border); background: transparent; color: inherit; cursor: pointer; }
.quarter-button::before { content: ''; position: absolute; top: -5px; left: 50%; height: 9px; border-left: 1px solid var(--rule-border); }
.quarter-button span, .quarter-button small { display: block; }
.quarter-button[aria-current="true"] { border-top: 3px solid var(--accent-primary); color: var(--accent-strong); background: var(--accent-wash); }

@media (max-width: 390px) {
  .quarter-prism { padding-top: 1rem; }
  .desktop-prism { display: none; }
  .prism-controls { grid-template-columns: 3rem minmax(0, 1fr) 3rem; gap: .25rem; position: sticky; z-index: 2; top: 58px; padding-block: .5rem; background: var(--surface-background); }
  .step-control { justify-content: center; padding-inline: .25rem; }.step-control small { display: none; }
  .prism-controls .native-control { width: 100%; }
  .reading-pane { display: block; border-top: 2px solid var(--accent-primary); padding-block: 1.25rem; }
  .reading-pane header { display: block; }
  .reading-pane .tag { margin-top: 0.5rem; }
  .metric-lanes { display: block; }
  .metric-lane { padding-top: 1rem; }.metric-lane + .metric-lane { margin-top: 1.25rem; }
  .metric-lane dl div { grid-template-columns: 1fr; gap: 0.1rem; }
  .quarter-list { display: flex; width: 100%; padding-inline: 0; overflow-x: auto; }
  .quarter-button { min-width: 6.25rem; }
}
</style>
