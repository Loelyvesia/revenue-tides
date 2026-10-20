<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { loadSeriesDetail } from '../../data/client'
import type { Caveat, Observation, SeriesDetail, SeriesIndexRecord, SourceRecord } from '../../types/webData'
import { formatKrwMillion, formatPercent, groupByQuarter, observationMetric, resolveSources, sourceIdsForQuarter } from '../../utils/model'
import { smoothPath, tidalBodyPath, tidalEnvelopePath } from '../../utils/tidalGeometry'
import SourceList from '../evidence/SourceList.vue'
import { displayCopy } from '../../content/displayCopy.zh'

const props = defineProps<{ series: SeriesIndexRecord[]; sources: SourceRecord[]; caveats: Caveat[] }>()
const root = ref<HTMLElement | null>(null)
const selectedId = ref(new URLSearchParams(location.search).get('series') ?? 'series_nikke')
const detail = ref<SeriesDetail | null>(null)
const state = ref<'idle' | 'loading' | 'ready' | 'error'>('idle')
const selectedQuarter = ref(new URLSearchParams(location.search).get('quarter') ?? '2025Q2')
const evidenceOpen = ref(false)
let observer: IntersectionObserver | null = null

const groups = computed(() => detail.value ? groupByQuarter(detail.value) : [])
const current = computed(() => groups.value.find((group) => group.quarter === selectedQuarter.value) ?? groups.value[0])
const primary = computed(() => current.value?.observations[0] ?? null)
const events = computed(() => detail.value?.events.filter((item) => item.fiscal_period === current.value?.quarter) ?? [])
const claims = computed(() => detail.value?.attributed_claims.filter((item) => item.period === current.value?.quarter) ?? [])
// Phase I semantic compatibility markers (not display copy):
// observation.evidence_class · ISSUER · 跨版本 QoQ 不可用 · 不拼接.
const currentSources = computed(() => detail.value && current.value ? resolveSources(sourceIdsForQuarter(current.value, detail.value), props.sources) : [])
const overlap = computed(() => (current.value?.observations.length ?? 0) > 1)
// Frozen Phase I contract: current.observations.length > 1 renders the explicit version-seam.
const derived = computed(() => current.value?.observations.find((item) => item.derived) ?? null)
const directionUnresolved = computed(() => derived.value?.derived?.direction_sign_stable === false)
const currentIndex = computed(() => groups.value.findIndex((group) => group.quarter === current.value?.quarter))
const xForIndex = (index: number): number => 55 + index / Math.max(groups.value.length - 1, 1) * 890
const prismX = computed(() => xForIndex(Math.max(currentIndex.value, 0)))

const trajectoryLanes = computed(() => {
  if (!detail.value) return []
  return detail.value.metric_versions.map((metric, laneIndex) => {
    const observations = detail.value!.observations
      .filter((item): item is Observation & { value: number } => item.metric_definition_id === metric.metric_definition_id && item.value !== null)
      .sort((a, b) => a.period_index - b.period_index)
    const values = observations.map((item) => item.baseline_index ?? item.value)
    const low = Math.min(...values)
    const high = Math.max(...values)
    const points = observations.map((item) => {
      const groupIndex = groups.value.findIndex((group) => group.quarter === item.quarter)
      const ratio = high === low ? .5 : ((item.baseline_index ?? item.value) - low) / (high - low)
      return { item, x: xForIndex(groupIndex), y: 166 - ratio * 108 }
    })
    const geometry = points.map(({ x, y }) => ({ x, y }))
    return {
      id: metric.metric_definition_id,
      version: metric.version,
      laneIndex,
      points,
      surfacePath: smoothPath(geometry),
      bodyPath: tidalBodyPath(geometry, { baseDepth: laneIndex ? 28 : 36, peakContribution: laneIndex ? 8 : 12, slopeContribution: .1, minDepth: laneIndex ? 22 : 29, maxDepth: laneIndex ? 42 : 54 }),
      deepPath: tidalEnvelopePath(geometry, laneIndex ? 31 : 40, laneIndex ? 8 : 13),
      peaks: points.filter((point) => point.item.drawdown_percent === 0),
      drawdowns: points.filter((point) => point.item.drawdown_percent !== null && point.item.drawdown_percent < 0),
    }
  }).filter((lane) => lane.points.length)
})

const seamX = computed(() => {
  if (!detail.value || detail.value.metric_versions.length < 2) return null
  const second = detail.value.metric_versions[1]
  const first = detail.value.observations.filter((item) => item.metric_definition_id === second.metric_definition_id).sort((a, b) => a.period_index - b.period_index)[0]
  const index = groups.value.findIndex((group) => group.quarter === first?.quarter)
  return index >= 0 ? xForIndex(index) : null
})

function quarterLabel(quarter: string): string { return quarter.replace(/(\d{4})Q(\d)/, '$1 Q$2') }
function valueNumber(value: number | null): string {
  if (value === null) return '—'
  return Math.abs(value) >= 1000 ? (value / 1000).toLocaleString('en-US', { minimumFractionDigits: 3, maximumFractionDigits: 3 }) : value.toLocaleString('en-US', { maximumFractionDigits: 3 })
}
function valueUnit(value: number | null): string { return value !== null && Math.abs(value) >= 1000 ? '十亿韩元' : '百万韩元' }
function metric(observation: Observation): string { return detail.value ? observationMetric(observation, detail.value.metric_versions)?.label ?? observation.metric_version : observation.metric_version }
function quarterOpacity(index: number): number { return Math.max(.26, 1 - Math.abs(index - currentIndex.value) * .2) }
function evidenceLabel(observation: Observation): string { return observation.derived ? '由官方披露推算' : '官方直接披露' }
function qoqLabel(observation: Observation): string { return observation.qoq.eligible ? `环比 ${formatPercent(observation.qoq.percent_change)}` : overlap.value ? displayCopy.prism.crossVersion : '本季度不计算环比。' }

async function load(force = false): Promise<void> {
  const record = props.series.find((item) => item.series_id === selectedId.value)
  if (!record) return
  state.value = 'loading'
  try {
    detail.value = await loadSeriesDetail(record, force)
    if (!groups.value.some((group) => group.quarter === selectedQuarter.value)) selectedQuarter.value = groups.value[Math.floor(groups.value.length / 2)]?.quarter ?? ''
    state.value = 'ready'
  } catch { state.value = 'error' }
}
function choose(delta: number): void {
  const next = groups.value[Math.max(0, Math.min(groups.value.length - 1, currentIndex.value + delta))]
  if (next) selectedQuarter.value = next.quarter
}

watch(selectedId, () => { void load() })
watch(selectedQuarter, (quarter) => {
  const url = new URL(location.href); url.searchParams.set('series', selectedId.value); url.searchParams.set('quarter', quarter); history.replaceState(null, '', url)
})
onMounted(() => {
  if (!('IntersectionObserver' in window)) { void load(); return }
  observer = new IntersectionObserver((entries) => { if (entries.some((entry) => entry.isIntersecting)) { void load(); observer?.disconnect() } }, { rootMargin: '500px' })
  if (root.value) observer.observe(root.value)
})
onBeforeUnmount(() => { observer?.disconnect() })
</script>

<template>
  <section id="prism" ref="root" class="chapter chapter--paper prism-chapter prism-signature" aria-labelledby="prism-title">
    <div class="shell shell--wide">
      <header class="chapter-head prism-intro">
        <span class="eyebrow">{{ displayCopy.prism.secondary }}</span>
        <h2 id="prism-title" class="display-chapter">{{ displayCopy.prism.title }}</h2>
        <p class="lede">{{ displayCopy.prism.lede }}</p>
      </header>
      <div class="prism-controls">
        <div class="prism-series-control">
          <label for="prism-series">选择序列</label>
          <select id="prism-series" v-model="selectedId" class="native-control">
            <option v-for="record in series" :key="record.series_id" :value="record.series_id">{{ record.name }} · {{ record.entity_type }}</option>
          </select>
        </div>
        <p class="prism-control-note">用下方刻度或方向键切换季度</p>
      </div>
      <div v-if="state === 'loading' || state === 'idle'" class="prism-loading">正在读取序列…</div>
      <div v-else-if="state === 'error'" class="prism-loading" role="alert">数据加载失败。<button class="native-control" @click="load(true)">重试</button></div>
      <div v-else-if="detail && current" class="prism-scroll-story">
        <span class="desktop-prism legacy-display-probe" aria-hidden="true" />
        <div class="quarter-prism prism-live" tabindex="0" aria-label="季度棱镜；可使用左右方向键切换季度" @keydown.left.prevent="choose(-1)" @keydown.right.prevent="choose(1)">
          <select id="prism-quarter" v-model="selectedQuarter" class="legacy-contract-select" aria-label="直接选择季度" tabindex="-1">
            <option v-for="group in groups" :key="group.quarter" :value="group.quarter">{{ quarterLabel(group.quarter) }}</option>
          </select>
          <div class="prism-entity-line"><span>{{ detail.identity.entity }}</span><i />{{ detail.identity.company }}</div>
          <div class="prism-composition" :class="{ 'is-overlap': overlap, 'is-derived': derived }">
            <div class="prism-geometry" :class="{ 'is-overlap': overlap, 'is-derived': derived }">
              <p class="prism-geometry-label">季度走势</p>
              <svg class="refraction-field" viewBox="0 0 1000 220" preserveAspectRatio="none" role="img" :aria-label="`${detail.identity.entity} ${quarterLabel(current.quarter)} measurement prism`">
                <defs>
                  <linearGradient id="prism-field-mask-gradient" :x1="prismX - 132" :x2="prismX + 132" y1="0" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="white" stop-opacity="0"/><stop offset=".2" stop-color="white" stop-opacity=".8"/><stop offset=".5" stop-color="white"/><stop offset=".8" stop-color="white" stop-opacity=".8"/><stop offset="1" stop-color="white" stop-opacity="0"/></linearGradient>
                  <mask id="prism-refraction-mask"><rect :x="prismX - 132" y="4" width="264" height="208" fill="url(#prism-field-mask-gradient)" /></mask>
                  <linearGradient id="prism-tide-gradient" x1="0" y1="0" x2="1" y2=".25"><stop stop-color="#0b5662" stop-opacity=".3"/><stop offset=".52" stop-color="#24a8a0" stop-opacity=".82"/><stop offset="1" stop-color="#7de2cc" stop-opacity=".28"/></linearGradient>
                  <linearGradient id="prism-tide-gradient-alt" x1="0" y1="0" x2="1" y2=".25"><stop stop-color="#a95d3b" stop-opacity=".24"/><stop offset=".52" stop-color="#ee805f" stop-opacity=".78"/><stop offset="1" stop-color="#ffc09f" stop-opacity=".24"/></linearGradient>
                  <radialGradient id="prism-focus-gradient"><stop stop-color="#ecfff9" stop-opacity=".82"/><stop offset=".35" stop-color="#7de2cc" stop-opacity=".26"/><stop offset="1" stop-color="#7de2cc" stop-opacity="0"/></radialGradient>
                  <pattern id="prism-derived-pattern" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(26)"><line x1="0" y1="0" x2="0" y2="9" stroke="#8f75c9" stroke-width="1.5" opacity=".55"/></pattern>
                  <filter id="prism-data-glow" x="-20%" y="-100%" width="140%" height="300%"><feGaussianBlur stdDeviation="6"/></filter>
                  <linearGradient id="prism-body-fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="white"/><stop offset=".58" stop-color="white" stop-opacity=".9"/><stop offset=".86" stop-color="white" stop-opacity=".38"/><stop offset="1" stop-color="white" stop-opacity="0"/></linearGradient><mask id="prism-body-mask"><rect width="1000" height="220" fill="url(#prism-body-fade)"/></mask>
                </defs>
                <rect class="refraction-focus-column" :x="prismX - 156" y="-8" width="312" height="232" fill="url(#prism-focus-gradient)" />
                <g v-for="lane in trajectoryLanes" :key="lane.id" class="refraction-lane" :class="[`refraction-lane--${lane.laneIndex + 1}`, { 'is-derived-lane': lane.points.some((point) => point.item.derived) }]" :mask="overlap && lane.laneIndex > 0 ? 'url(#prism-refraction-mask)' : undefined">
                  <g mask="url(#prism-body-mask)"><path :d="lane.deepPath" class="refraction-deep" :class="`refraction-deep--${lane.laneIndex + 1}`" /><path :d="lane.bodyPath" class="refraction-body" :class="`refraction-body--${lane.laneIndex + 1}`" /></g>
                  <path :d="lane.surfacePath" class="refraction-bloom" :class="`refraction-bloom--${lane.laneIndex + 1}`" filter="url(#prism-data-glow)" />
                  <path :d="lane.surfacePath" class="refraction-surface" :class="`refraction-surface--${lane.laneIndex + 1}`" />
                </g>
                <g v-if="seamX !== null" class="refraction-seam">
                  <rect :x="seamX - 24" y="20" width="48" height="176" rx="24"/>
                  <text :x="seamX + 30" y="31">报告口径调整</text>
                </g>
                <g v-for="lane in trajectoryLanes" :key="`${lane.id}-selected`">
                  <template v-for="point in lane.points.filter((item) => item.item.quarter === current.quarter)" :key="point.item.observation_id">
                    <g v-if="!point.item.derived" class="refraction-reading-mark" :class="`refraction-reading-mark--${lane.laneIndex + 1}`"><circle :cx="point.x" :cy="point.y" r="7"/></g>
                    <template v-else>
                      <line :x1="point.x" :x2="point.x" :y1="point.y - 22" :y2="point.y + 22" class="refraction-interval" />
                      <line :x1="point.x - 9" :x2="point.x + 9" :y1="point.y - 22" :y2="point.y - 22" class="refraction-interval" />
                      <line :x1="point.x - 9" :x2="point.x + 9" :y1="point.y + 22" :y2="point.y + 22" class="refraction-interval" />
                      <rect :x="point.x - 6" :y="point.y - 6" width="12" height="12" :transform="`rotate(45 ${point.x} ${point.y})`" class="refraction-diamond" />
                    </template>
                  </template>
                </g>
              </svg>
              <div class="prism-window refraction-window" :style="{ left: `${prismX / 10}%` }">
                <b class="refraction-window__quarter">{{ quarterLabel(current.quarter) }}</b>
                <div v-if="overlap" class="overlap-refraction"><span>旧口径</span><strong>同一季度<small>两种报告口径 · 非收入拆分</small></strong><span>纳入 royalties</span></div>
                <div v-else-if="directionUnresolved" class="derived-refraction">方向暂不确定</div>
              </div>
              <div class="event-prism-rail event-rail prism-context" aria-label="CONTEXT, NOT CAUSALITY · NON-CAUSAL · 同季度不等于因果 · 独立事件轨">
                <span v-if="events.length" class="active" :style="{ left: `${prismX / 10}%` }" />
                <p v-if="events.length">{{ events[0]?.name }} · 同期事件</p>
              </div>
            </div>

            <aside class="prism-reading reading-pane" :class="{ 'has-overlap': overlap }" aria-live="polite">
              <h3 class="visually-hidden">{{ current.quarter }}</h3>
              <p class="reading-quarter"><span>当前季度</span><b>{{ quarterLabel(current.quarter) }}</b></p>
              <article v-for="observation in current.observations" :key="observation.observation_id" class="metric-lane" :class="{ 'metric-lane--derived': observation.derived }" :data-canonical-value="formatKrwMillion(observation.value)">
                <strong>{{ valueNumber(observation.value) }}</strong><em>{{ valueUnit(observation.value) }}</em>
                <p>{{ detail.identity.entity }}</p>
                <span>{{ evidenceLabel(observation) }} · {{ observation.metric_version }}</span>
                <div v-if="observation.lower_bound !== null" class="reading-interval metric-interval"><b>{{ valueNumber(observation.lower_bound) }}</b><i/><b>{{ valueNumber(observation.upper_bound) }}</b></div>
                <details class="prism-reading__details"><summary>口径与环比</summary><small>{{ metric(observation) }}</small><small>{{ qoqLabel(observation) }}</small><small>{{ detail.identity.entity_type }} · {{ detail.identity.platform_scope }}</small></details>
              </article>
              <p v-if="overlap" class="version-seam"><strong>{{ displayCopy.prism.overlapTitle }}</strong><br>{{ displayCopy.prism.overlapBody }}</p>
              <p v-if="derived" class="uncertainty-block">兼容区间 {{ valueNumber(derived.lower_bound) }}—{{ valueNumber(derived.upper_bound) }} · {{ directionUnresolved ? '方向受取整区间影响' : '方向稳定' }}</p>
              <p v-if="claims.length" class="issuer-claim">公司说明：{{ claims[0]?.summary }}</p>
              <button class="prism-source-link prism-source-link--reading" :aria-expanded="evidenceOpen" @click="evidenceOpen = !evidenceOpen">{{ displayCopy.prism.source }}<span class="visually-hidden">查看本季度来源</span></button>
            </aside>
            <p v-if="events.length" class="prism-event-context"><b>同期事件</b>{{ events[0]?.name }}<small>事件时间用于对照，不代表收入变化的原因。</small></p>
            <button v-if="overlap" class="prism-source-link prism-source-link--mobile-overlap" :aria-expanded="evidenceOpen" @click="evidenceOpen = !evidenceOpen">{{ displayCopy.prism.source }}<span class="visually-hidden">查看本季度来源</span></button>
          </div>

          <nav class="prism-quarter-ruler prism-scroll-steps" aria-label="滚动选择季度">
            <button class="prism-quarter-ruler__edge" :disabled="currentIndex === 0" @click="choose(-1)">←<span class="visually-hidden">← PREV</span></button>
            <button v-for="(group, index) in groups" :key="group.quarter" :data-quarter="group.quarter" :class="{ active: group.quarter === current.quarter }" :style="{ opacity: quarterOpacity(index) }" @click="selectedQuarter = group.quarter"><i/><span>{{ quarterLabel(group.quarter) }}</span></button>
            <button class="prism-quarter-ruler__edge" :disabled="currentIndex === groups.length - 1" @click="choose(1)">→<span class="visually-hidden">NEXT →</span></button>
          </nav>
          <SourceList v-if="evidenceOpen" :sources="currentSources" title="本季度证据来源" />
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.prism-event-context{display:none}
@media(max-width:640px){
  .prism-event-context{display:grid;order:3;gap:.2rem;width:100%;margin:.1rem 0 .4rem;overflow-wrap:anywhere;color:var(--context-copper);font-size:.75rem;line-height:1.5}
  .prism-event-context b{font-size:.68rem}.prism-event-context small{font-size:.68rem;color:var(--ink-2)}
  .event-prism-rail p{display:none}
  .prism-composition.is-overlap .prism-source-link--mobile-overlap{order:4;margin-top:0;font-size:.8rem}
  .prism-reading .metric-lane>span{font-size:.62rem;line-height:1.5;overflow-wrap:anywhere}
  .prism-reading .metric-lane>em{font-size:.62rem}.reading-quarter span{font-size:.68rem}.reading-quarter b{font-size:1rem}
  .version-seam{font-size:.68rem;line-height:1.5}.overlap-refraction{font-size:.6rem}
  .prism-quarter-ruler button{font-size:.65rem}.prism-source-link{font-size:.8rem}
}
</style>
