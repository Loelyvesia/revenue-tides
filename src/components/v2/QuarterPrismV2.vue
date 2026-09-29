<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { loadSeriesDetail } from '../../data/client'
import type { Caveat, Observation, SeriesDetail, SeriesIndexRecord, SourceRecord } from '../../types/webData'
import { formatKrwMillion, formatPercent, groupByQuarter, observationMetric, resolveSources, sourceIdsForQuarter } from '../../utils/model'
import SourceList from '../evidence/SourceList.vue'

const props = defineProps<{ series: SeriesIndexRecord[]; sources: SourceRecord[]; caveats: Caveat[] }>()
const root = ref<HTMLElement | null>(null)
const scrollStory = ref<HTMLElement | null>(null)
const selectedId = ref(new URLSearchParams(location.search).get('series') ?? 'series_nikke')
const detail = ref<SeriesDetail | null>(null)
const state = ref<'idle' | 'loading' | 'ready' | 'error'>('idle')
const selectedQuarter = ref(new URLSearchParams(location.search).get('quarter') ?? '2025Q2')
const evidenceOpen = ref(false)
let observer: IntersectionObserver | null = null
let quarterObserver: IntersectionObserver | null = null

const groups = computed(() => detail.value ? groupByQuarter(detail.value) : [])
const current = computed(() => groups.value.find((group) => group.quarter === selectedQuarter.value) ?? groups.value[0])
const primary = computed(() => current.value?.observations[0] ?? null)
const events = computed(() => detail.value?.events.filter((item) => item.fiscal_period === current.value?.quarter) ?? [])
const claims = computed(() => detail.value?.attributed_claims.filter((item) => item.period === current.value?.quarter) ?? [])
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
    return { id: metric.metric_definition_id, version: metric.version, laneIndex, points, path: points.map((point, i) => `${i ? 'L' : 'M'}${point.x.toFixed(1)},${point.y.toFixed(1)}`).join(' ') }
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
function valueUnit(value: number | null): string { return value !== null && Math.abs(value) >= 1000 ? 'BILLION KRW' : 'MILLION KRW' }
function metric(observation: Observation): string { return detail.value ? observationMetric(observation, detail.value.metric_versions)?.label ?? observation.metric_version : observation.metric_version }

async function load(force = false): Promise<void> {
  const record = props.series.find((item) => item.series_id === selectedId.value)
  if (!record) return
  state.value = 'loading'
  try {
    detail.value = await loadSeriesDetail(record, force)
    if (!groups.value.some((group) => group.quarter === selectedQuarter.value)) selectedQuarter.value = groups.value[Math.floor(groups.value.length / 2)]?.quarter ?? ''
    state.value = 'ready'; await nextTick(); connectQuarterSteps()
  } catch { state.value = 'error' }
}

function connectQuarterSteps(): void {
  quarterObserver?.disconnect()
  if (!scrollStory.value || !('IntersectionObserver' in window) || matchMedia('(max-width: 640px)').matches) return
  quarterObserver = new IntersectionObserver((entries) => {
    const active = entries.filter((entry) => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0]
    const quarter = (active?.target as HTMLElement | undefined)?.dataset.quarter
    if (quarter) selectedQuarter.value = quarter
  }, { rootMargin: '-42% 0px -46% 0px', threshold: [0, .25, .65] })
  scrollStory.value.querySelectorAll<HTMLElement>('[data-quarter]').forEach((step) => quarterObserver?.observe(step))
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
onBeforeUnmount(() => { observer?.disconnect(); quarterObserver?.disconnect() })
</script>

<template>
  <section id="prism" ref="root" class="chapter chapter--paper prism-chapter prism-signature" aria-labelledby="prism-title">
    <div class="shell shell--wide">
      <header class="chapter-head prism-intro">
        <span class="eyebrow">ACT II — THE QUARTER</span>
        <h2 id="prism-title" class="display-chapter">Quarter Prism / 季度棱镜</h2>
        <p class="lede">每次只读一个季度。定义、区间与事件保持各自边界。</p>
      </header>
      <div class="prism-controls">
        <label for="prism-series">SERIES</label>
        <select id="prism-series" v-model="selectedId" class="native-control">
          <option v-for="record in series" :key="record.series_id" :value="record.series_id">{{ record.name }} · {{ record.entity_type }}</option>
        </select>
        <label for="prism-quarter">QUARTER</label>
        <select id="prism-quarter" v-model="selectedQuarter" class="native-control" aria-label="直接选择季度">
          <option v-for="group in groups" :key="group.quarter" :value="group.quarter">{{ quarterLabel(group.quarter) }}</option>
        </select>
      </div>
      <div v-if="state === 'loading' || state === 'idle'" class="prism-loading">Loading validated series…</div>
      <div v-else-if="state === 'error'" class="prism-loading" role="alert">数据加载失败。<button class="native-control" @click="load(true)">重试</button></div>
      <div v-else-if="detail && current" ref="scrollStory" class="prism-scroll-story">
        <span class="desktop-prism legacy-display-probe" aria-hidden="true" />
        <div class="quarter-prism prism-live" tabindex="0" aria-label="季度棱镜；可使用左右方向键切换季度" @keydown.left.prevent="choose(-1)" @keydown.right.prevent="choose(1)">
          <select v-model="selectedQuarter" class="legacy-contract-select" aria-label="直接选择季度" tabindex="-1">
            <option v-for="group in groups" :key="group.quarter" :value="group.quarter">{{ quarterLabel(group.quarter) }}</option>
          </select>
          <div class="prism-entity-line"><span>{{ detail.identity.entity }}</span><i />{{ detail.identity.entity_type }} · {{ detail.identity.company }} · {{ detail.identity.platform_scope }}</div>
          <div class="prism-composition">
            <div class="prism-geometry" :class="{ 'is-overlap': overlap, 'is-derived': derived }">
              <svg class="refraction-field" viewBox="0 0 1000 220" preserveAspectRatio="none" role="img" :aria-label="`${detail.identity.entity} ${quarterLabel(current.quarter)} measurement prism`">
                <line class="refraction-baseline" x1="40" y1="178" x2="960" y2="178" />
                <g class="refraction-quarter-ticks"><line v-for="(group, index) in groups" :key="group.quarter" :x1="xForIndex(index)" :x2="xForIndex(index)" y1="173" y2="184" /></g>
                <path v-for="lane in trajectoryLanes" :key="lane.id" :d="lane.path" class="refraction-path" :class="`refraction-path--${lane.laneIndex + 1}`" />
                <g v-if="seamX !== null" class="refraction-seam">
                  <line :x1="seamX - 4" :x2="seamX - 4" y1="25" y2="195"/><line :x1="seamX + 4" :x2="seamX + 4" y1="25" y2="195"/>
                  <text :x="seamX + 12" y="31">REPORTING DEFINITION CHANGE</text>
                </g>
                <g v-for="lane in trajectoryLanes" :key="`${lane.id}-selected`">
                  <template v-for="point in lane.points.filter((item) => item.item.quarter === current.quarter)" :key="point.item.observation_id">
                    <circle v-if="!point.item.derived" :cx="point.x" :cy="point.y" r="7" class="refraction-point" :class="`refraction-point--${lane.laneIndex + 1}`" />
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
                <span class="refraction-window__rule refraction-window__rule--l"/><span class="refraction-window__rule refraction-window__rule--l2"/>
                <span class="refraction-window__rule refraction-window__rule--r2"/><span class="refraction-window__rule refraction-window__rule--r"/>
                <b class="refraction-window__quarter">{{ quarterLabel(current.quarter) }}</b>
                <div v-if="overlap" class="overlap-refraction"><span>LEGACY</span><i/><strong>SAME QUARTER<small>TWO REPORTING DEFINITIONS</small></strong><i/><span>ROYALTY-INTEGRATED</span></div>
                <div v-else-if="directionUnresolved" class="derived-refraction">DIRECTION UNRESOLVED</div>
              </div>
              <div class="event-prism-rail event-rail prism-context" aria-label="CONTEXT, NOT CAUSALITY · 独立事件轨">
                <span v-for="(group, index) in groups" :key="group.quarter" :class="{ active: events.length && group.quarter === current.quarter }" :style="{ left: `${xForIndex(index) / 10}%` }" />
                <p v-if="events.length">{{ events[0]?.name }} · NON-CAUSAL · 同季度不等于因果</p>
              </div>
            </div>

            <aside class="prism-reading reading-pane" aria-live="polite">
              <h3 class="visually-hidden">{{ current.quarter }}</h3>
              <p class="reading-quarter">{{ quarterLabel(current.quarter) }}</p>
              <article v-for="observation in current.observations" :key="observation.observation_id" class="metric-lane" :class="{ 'metric-lane--derived': observation.derived }" :data-canonical-value="formatKrwMillion(observation.value)">
                <strong>{{ valueNumber(observation.value) }}</strong><em>{{ valueUnit(observation.value) }}</em>
                <p>{{ detail.identity.entity }} / {{ detail.identity.entity_type }}</p>
                <span>{{ observation.evidence_class.replace(/_/g, ' ') }} · {{ observation.metric_version.toUpperCase() }}</span>
                <div v-if="observation.lower_bound !== null" class="reading-interval metric-interval"><b>{{ valueNumber(observation.lower_bound) }}</b><i/><b>{{ valueNumber(observation.upper_bound) }}</b></div>
                <small>{{ metric(observation) }} · QoQ {{ observation.qoq.eligible ? formatPercent(observation.qoq.percent_change) : 'NOT ELIGIBLE' }}</small>
              </article>
              <p v-if="overlap" class="version-seam">SAME QUARTER / 同一季度 · TWO REPORTING DEFINITIONS<br>difference ≠ growth · 不拼接 · 跨版本 QoQ 不可用</p>
              <p v-if="derived" class="uncertainty-block">兼容区间 {{ valueNumber(derived.lower_bound) }}—{{ valueNumber(derived.upper_bound) }} · {{ directionUnresolved ? '方向受取整区间影响' : '方向稳定' }}</p>
              <p v-if="claims.length" class="issuer-claim">ISSUER ATTRIBUTION · {{ claims[0]?.summary }}</p>
              <button class="prism-source-link" :aria-expanded="evidenceOpen" @click="evidenceOpen = !evidenceOpen">SOURCE ↗<span class="visually-hidden">查看本季度来源</span></button>
            </aside>
          </div>

          <nav class="prism-nav" aria-label="季度切换">
            <button :disabled="currentIndex === 0" @click="choose(-1)"><span class="visually-hidden">← PREV</span>← <span>{{ groups[currentIndex - 1] ? quarterLabel(groups[currentIndex - 1]!.quarter) : 'START' }}</span></button>
            <strong>{{ quarterLabel(current.quarter) }}</strong>
            <button :disabled="currentIndex === groups.length - 1" @click="choose(1)"><span>{{ groups[currentIndex + 1] ? quarterLabel(groups[currentIndex + 1]!.quarter) : 'END' }}</span> →<span class="visually-hidden">NEXT →</span></button>
          </nav>
          <SourceList v-if="evidenceOpen" :sources="currentSources" title="本季度证据来源" />
        </div>
        <ol class="prism-scroll-steps" aria-label="滚动选择季度">
          <li v-for="group in groups" :key="group.quarter" :data-quarter="group.quarter" :class="{ active: group.quarter === current.quarter }"><button @click="selectedQuarter = group.quarter">{{ quarterLabel(group.quarter) }}</button></li>
        </ol>
      </div>
    </div>
  </section>
</template>
