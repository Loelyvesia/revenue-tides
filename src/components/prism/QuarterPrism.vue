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
      <button class="native-control" :disabled="selectedIndex === 0" @click="step(-1)">← 上一季度</button>
      <label>
        <span class="visually-hidden">直接选择季度</span>
        <select v-model="selectedQuarter" class="native-control" aria-label="直接选择季度">
          <option v-for="group in quarterGroups" :key="group.quarter" :value="group.quarter">{{ group.quarter }}</option>
        </select>
      </label>
      <button class="native-control" :disabled="selectedIndex === quarterGroups.length - 1" @click="step(1)">下一季度 →</button>
    </div>

    <div class="desktop-prism">
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
        <rect class="reading-window" :x="xFor(selectedIndex) - 42" y="40" width="84" height="270" rx="2" />
        <g v-if="hasVersionBreak" class="version-seam" aria-label="指标版本断点">
          <line :x1="xFor(Math.max(0, quarterGroups.findIndex((group) => group.observations.some((observation) => observation.metric_version.includes('royalty'))))) - 6" y1="42" :x2="xFor(Math.max(0, quarterGroups.findIndex((group) => group.observations.some((observation) => observation.metric_version.includes('royalty'))))) - 6" y2="310" />
          <line :x1="xFor(Math.max(0, quarterGroups.findIndex((group) => group.observations.some((observation) => observation.metric_version.includes('royalty'))))) + 2" y1="42" :x2="xFor(Math.max(0, quarterGroups.findIndex((group) => group.observations.some((observation) => observation.metric_version.includes('royalty'))))) + 2" y2="310" />
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
          <p class="eyebrow">SELECTED QUARTER / ANALYTICAL READING WINDOW</p>
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
      <button class="native-control" :aria-expanded="evidenceOpen" @click="evidenceOpen = !evidenceOpen">{{ evidenceOpen ? '收起证据' : '查看证据与来源' }}</button>
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
.quarter-prism { padding: clamp(1rem, 3vw, 2rem); border: 1px solid var(--rule-border); background: rgba(251, 249, 242, 0.82); }
.prism-controls { display: flex; justify-content: center; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 1.25rem; }
.trajectory { display: block; width: 100%; min-height: 300px; color: var(--uncertainty); }
.grid line { stroke: var(--rule-grid); stroke-width: 1; }
.reading-window { fill: rgba(31, 103, 99, 0.07); stroke: var(--accent-primary); stroke-width: 2; transition: x var(--motion-signature) ease; }
.trajectory-line { fill: none; stroke: var(--accent-primary); stroke-width: 2; vector-effect: non-scaling-stroke; }
.lane-1 { stroke: var(--text-primary); stroke-dasharray: 8 5; }
.direct-mark { fill: var(--accent-primary); stroke: var(--surface-primary); stroke-width: 2; }
.derived-mark { fill: var(--surface-primary); stroke: var(--evidence-derived); stroke-width: 2; }
.direct-mark.selected, .derived-mark.selected { stroke: var(--text-primary); stroke-width: 4; }
.whisker line { stroke: var(--uncertainty); stroke-width: 2; }
.version-seam line { stroke: var(--text-primary); stroke-width: 2; stroke-dasharray: 3 3; }
.quarter-label { fill: var(--text-secondary); font: 12px var(--font-numeric); }
.visual-summary { margin: 0 auto 1rem; max-width: 55rem; color: var(--text-secondary); font-size: 0.875rem; }
.reading-pane { padding-top: 1.5rem; border-top: 1px solid var(--rule-border); }
.reading-pane header { display: flex; justify-content: space-between; gap: 1rem; align-items: start; }
.scope { color: var(--text-secondary); }
.overlap-note { padding: 0.75rem 1rem; border-block: 1px solid var(--text-primary); font-weight: 650; }
.metric-lanes { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 22rem), 1fr)); gap: 1rem; }
.metric-lane { display: grid; grid-template-columns: 1rem 1fr; gap: 0.8rem; padding: 1rem; border-top: 2px solid var(--text-primary); background: var(--surface-primary); }
.lane-mark { width: 0.8rem; height: 0.8rem; margin-top: 0.35rem; border-radius: 50%; background: var(--evidence-direct); }
.metric-lane.derived .lane-mark { border-radius: 0; border: 2px solid var(--evidence-derived); background: transparent; transform: rotate(45deg); }
.metric-value { display: block; margin: 0.2rem 0; font-size: clamp(1.25rem, 3vw, 1.75rem); }
.metric-lane p { margin: 0.25rem 0 0.75rem; }
.metric-lane dl { margin: 0; }
.metric-lane dl div { display: grid; grid-template-columns: 6rem 1fr; gap: 0.5rem; padding-block: 0.35rem; border-top: 1px solid var(--rule-grid); }
dt { color: var(--text-secondary); font-size: 0.75rem; } dd { margin: 0; }
.uncertainty-block { margin-top: 0.8rem; padding: 0.8rem; border: 1px solid var(--evidence-derived); background-image: repeating-linear-gradient(135deg, transparent 0 7px, rgba(89, 97, 94, 0.12) 7px 9px); }
.interval-geometry { position: relative; height: 1.25rem; margin-bottom: 0.35rem; border-inline: 2px solid var(--uncertainty); }
.interval-geometry::before { content: ''; position: absolute; top: 50%; inset-inline: 0; border-top: 2px solid var(--uncertainty); }
.interval-geometry span { position: absolute; left: 50%; top: 0.25rem; width: 0.75rem; height: 0.75rem; border: 2px solid var(--evidence-derived); background: var(--surface-primary); transform: translateX(-50%) rotate(45deg); }
.version-note { display: grid; grid-template-columns: 1rem 1fr; gap: 0.8rem; margin-top: 1rem; padding: 1rem; border-block: 1px solid var(--rule-border); }
.version-note p { margin: 0.15rem 0; }
.double-seam { border-inline: 2px solid var(--text-primary); }
.source-action { display: grid; gap: 0.75rem; margin-top: 1rem; }
.source-action > button { justify-self: start; }
.quarter-list { display: flex; gap: 0.5rem; overflow-x: auto; padding: 1rem 0 0.25rem; }
.quarter-button { min-width: 6rem; min-height: 52px; border: 1px solid var(--rule-border); background: transparent; color: inherit; cursor: pointer; }
.quarter-button span, .quarter-button small { display: block; }
.quarter-button[aria-current="true"] { border: 2px solid var(--accent-primary); background: var(--surface-secondary); }

@media (max-width: 390px) {
  .quarter-prism { padding: 1rem; }
  .desktop-prism { display: none; }
  .prism-controls { display: grid; grid-template-columns: 1fr; }
  .prism-controls .native-control { width: 100%; }
  .reading-pane { border-top: 2px solid var(--accent-primary); }
  .reading-pane header { display: block; }
  .reading-pane .tag { margin-top: 0.5rem; }
  .metric-lanes { display: block; }
  .metric-lane + .metric-lane { margin-top: 0.75rem; }
  .metric-lane dl div { grid-template-columns: 1fr; gap: 0.1rem; }
  .quarter-list { display: grid; grid-template-columns: repeat(2, 1fr); overflow: visible; }
  .quarter-button { min-width: 0; }
}
</style>
