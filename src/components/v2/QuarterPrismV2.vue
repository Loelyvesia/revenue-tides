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
const events = computed(() => detail.value?.events.filter((item) => item.fiscal_period === current.value?.quarter) ?? [])
const claims = computed(() => detail.value?.attributed_claims.filter((item) => item.period === current.value?.quarter) ?? [])
const currentSources = computed(() => detail.value && current.value ? resolveSources(sourceIdsForQuarter(current.value, detail.value), props.sources) : [])
const position = computed(() => {
  const index = groups.value.findIndex((group) => group.quarter === current.value?.quarter)
  return groups.value.length > 1 ? 4 + index / (groups.value.length - 1) * 92 : 50
})

async function load(force = false): Promise<void> {
  const record = props.series.find((item) => item.series_id === selectedId.value)
  if (!record) return
  state.value = 'loading'
  try {
    detail.value = await loadSeriesDetail(record, force)
    const wanted = groups.value.some((group) => group.quarter === selectedQuarter.value)
    if (!wanted) selectedQuarter.value = groups.value[Math.floor(groups.value.length / 2)]?.quarter ?? ''
    state.value = 'ready'
    await nextTick()
    connectQuarterSteps()
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
  const index = groups.value.findIndex((group) => group.quarter === current.value?.quarter)
  const next = groups.value[Math.max(0, Math.min(groups.value.length - 1, index + delta))]
  if (next) selectedQuarter.value = next.quarter
}

function metric(observation: Observation): string {
  return detail.value ? observationMetric(observation, detail.value.metric_versions)?.label ?? observation.metric_version : observation.metric_version
}

watch(selectedId, () => { void load() })
watch(selectedQuarter, (quarter) => {
  const url = new URL(location.href)
  url.searchParams.set('series', selectedId.value)
  url.searchParams.set('quarter', quarter)
  url.hash = 'prism'
  history.replaceState(null, '', url)
})

onMounted(() => {
  if (!('IntersectionObserver' in window)) { void load(); return }
  observer = new IntersectionObserver((entries) => {
    if (entries.some((entry) => entry.isIntersecting)) { void load(); observer?.disconnect() }
  }, { rootMargin: '500px' })
  if (root.value) observer.observe(root.value)
})
onBeforeUnmount(() => { observer?.disconnect(); quarterObserver?.disconnect() })
</script>

<template>
  <section id="prism" ref="root" class="chapter chapter--dark prism-chapter" aria-labelledby="prism-title">
    <div class="shell shell--wide">
      <header class="chapter-head prism-intro">
        <span class="eyebrow">ACT II — THE QUARTER</span>
        <h2 id="prism-title" class="display-chapter">Quarter Prism / 季度棱镜</h2>
        <p class="lede">一次只读一个季度：实体、指标版本、证据、区间、事件与来源并列出现。</p>
      </header>
      <div class="prism-controls">
        <label for="prism-series">SERIES</label>
        <select id="prism-series" v-model="selectedId" class="native-control">
          <option v-for="record in series" :key="record.series_id" :value="record.series_id">{{ record.name }} · {{ record.entity_type }}</option>
        </select>
        <label for="prism-quarter">QUARTER</label>
        <select id="prism-quarter" v-model="selectedQuarter" class="native-control" aria-label="直接选择季度">
          <option v-for="group in groups" :key="group.quarter" :value="group.quarter">{{ group.quarter }}</option>
        </select>
      </div>
      <div v-if="state === 'loading' || state === 'idle'" class="prism-loading">Loading validated series…</div>
      <div v-else-if="state === 'error'" class="prism-loading" role="alert">数据加载失败。<button class="native-control" @click="load(true)">重试</button></div>
      <div v-else-if="detail && current" ref="scrollStory" class="prism-scroll-story">
      <div class="quarter-prism desktop-prism" tabindex="0" aria-label="季度棱镜；可使用左右方向键切换季度" @keydown.left.prevent="choose(-1)" @keydown.right.prevent="choose(1)">
        <div class="prism-main">
          <aside class="prism-identity">
            <p class="eyebrow">ENTITY</p>
            <h3>{{ detail.identity.entity }}</h3>
            <p>{{ detail.identity.company }} · {{ detail.identity.entity_type }}</p>
            <p class="caption">{{ detail.identity.platform_scope }}</p>
          </aside>
          <div class="prism-reading reading-pane" aria-live="polite">
            <p class="eyebrow">SELECTED QUARTER</p>
            <h3 class="display-figure">{{ current.quarter }}</h3>
            <div class="observation-stack">
              <article v-for="observation in current.observations" :key="observation.observation_id" class="metric-lane" :class="{ 'metric-lane--derived': observation.derived }">
                <p class="metric-version">{{ observation.metric_version }}</p>
                <strong class="display-figure">{{ formatKrwMillion(observation.value) }}</strong>
                <p>{{ metric(observation) }}</p>
                <div v-if="observation.lower_bound !== null" class="metric-interval"><span>{{ formatKrwMillion(observation.lower_bound) }}</span><i /><span>{{ formatKrwMillion(observation.upper_bound) }}</span></div>
                <p class="caption">{{ observation.evidence_class }} · QoQ {{ observation.qoq.eligible ? formatPercent(observation.qoq.percent_change) : 'not eligible' }}</p>
              </article>
            </div>
            <p v-if="current.observations.length > 1" class="version-seam">同一季度口径重叠 · 不拼接 · 跨版本 QoQ 不可用</p>
          </div>
          <aside class="prism-context">
            <p class="eyebrow">CONTEXT, NOT CAUSALITY</p>
            <div class="event-rail">
              <p v-if="!events.length && !claims.length" class="caption">No curated event or issuer claim for this quarter.</p>
              <div v-for="event in events" :key="event.event_id" class="event-rail__item is-on"><span class="dot" />{{ event.name }}<small>{{ event.event_type }}</small></div>
              <div v-for="claim in claims" :key="claim.claim_id" class="event-rail__item is-on">ISSUER · {{ claim.summary }}</div>
            </div>
          </aside>
        </div>
        <div class="prism-stage">
          <div class="prism-track">
            <div class="prism-line" />
            <div class="prism-window" :style="{ left: `${position}%` }"><div class="prism-window__wash"/><div class="prism-window__frame"/><span class="prism-window__top">{{ current.quarter }}</span></div>
            <button v-for="group in groups" :key="group.quarter" class="quarter-dot" :class="{ active: group.quarter === current.quarter }" :style="{ left: `${4 + groups.indexOf(group) / Math.max(groups.length - 1, 1) * 92}%` }" :aria-label="`选择 ${group.quarter}`" @click="selectedQuarter = group.quarter" />
          </div>
          <div class="prism-nav"><button class="native-control" :disabled="groups[0]?.quarter === current.quarter" @click="choose(-1)">← PREV</button><button class="native-control" :disabled="groups.at(-1)?.quarter === current.quarter" @click="choose(1)">NEXT →</button></div>
        </div>
        <div class="source-action">
          <button class="native-control" :aria-expanded="evidenceOpen" @click="evidenceOpen = !evidenceOpen">{{ evidenceOpen ? '收起来源' : `查看本季度来源 (${currentSources.length})` }}</button>
          <SourceList v-if="evidenceOpen" :sources="currentSources" title="本季度证据来源" />
        </div>
      </div>
      <ol class="prism-scroll-steps" aria-label="滚动选择季度">
        <li v-for="group in groups" :key="group.quarter" :data-quarter="group.quarter" :class="{ active: group.quarter === current.quarter }"><button @click="selectedQuarter = group.quarter">{{ group.quarter }}</button></li>
      </ol>
      </div>
    </div>
  </section>
</template>
