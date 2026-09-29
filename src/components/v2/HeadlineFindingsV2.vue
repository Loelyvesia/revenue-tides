<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { loadSeriesDetail } from '../../data/client'
import type { Finding, Observation, SeriesDetail, SeriesIndexRecord, SourceRecord } from '../../types/webData'
import { resolveSources } from '../../utils/model'
import { useScrolly } from '../../composables/useScrolly'
import SourceList from '../evidence/SourceList.vue'

const props = defineProps<{ findings: Finding[]; series: SeriesIndexRecord[]; sources: SourceRecord[] }>()
const root = ref<HTMLElement | null>(null)
const f1Story = ref<HTMLElement | null>(null)
const { activeIndex: f1QuarterIndex } = useScrolly({ container: f1Story, stepCount: 3, rootMargin: '-20% 0px -55% 0px' })
const details = ref<SeriesDetail[]>([])
const loaded = ref(false)
const openFinding = ref<string | null>(null)
let observer: IntersectionObserver | null = null

const headline = computed(() => props.findings.filter((finding) => finding.headline))
const f1 = computed(() => headline.value.find((finding) => finding.finding_id === 'F1')!)
const f2 = computed(() => headline.value.find((finding) => finding.finding_id === 'F2')!)
const f4 = computed(() => headline.value.find((finding) => finding.finding_id === 'F4')!)
const f1Quarter = computed(() => ['2025Q2', '2025Q3', '2025Q4'][f1QuarterIndex.value] ?? '2025Q2')
const f1Rows = computed(() => ['series_lineage_m', 'series_lineage_2m', 'series_lineage_w'].map((seriesId) => {
  const detail = details.value.find((item) => item.series_id === seriesId)
  const values = detail?.observations.filter((item) => item.quarter === f1Quarter.value) ?? []
  return { name: detail?.identity.entity ?? seriesId, legacy: values.find((item) => item.metric_version.includes('legacy')) ?? null, royalty: values.find((item) => item.metric_version.includes('royalty')) ?? null }
}))
const stellar = computed(() => details.value.find((item) => item.series_id === 'series_stellar_blade'))
const stellarA = computed(() => stellar.value?.observations.find((item) => item.observation_id === 'obs_stellar_2025q1') ?? null)
const stellarB = computed(() => stellar.value?.observations.find((item) => item.observation_id === 'obs_stellar_2025q2') ?? null)
const blackDesert = computed(() => details.value.find((item) => item.series_id === 'series_black_desert'))
const bdObservations = computed(() => blackDesert.value?.observations.filter((item): item is Observation & { value: number } => item.value !== null).sort((a, b) => a.period_index - b.period_index) ?? [])
const bdCoordinates = computed(() => {
  const observations = bdObservations.value
  if (!observations.length) return []
  const min = Math.min(...observations.map((item) => item.value)); const max = Math.max(...observations.map((item) => item.value))
  return observations.map((item, i) => ({ item, x: 60 + i / Math.max(observations.length - 1, 1) * 880, y: 228 - (item.value - min) / Math.max(max - min, 1) * 154 }))
})
const bdLinePath = computed(() => bdCoordinates.value.map((point, i) => `${i ? 'L' : 'M'}${point.x.toFixed(1)},${point.y.toFixed(1)}`).join(' '))
const bdBandPath = computed(() => {
  if (!bdCoordinates.value.length) return ''
  const upper = bdCoordinates.value.map((point, i) => `${i ? 'L' : 'M'}${point.x.toFixed(1)},${(point.y - 13).toFixed(1)}`).join(' ')
  const lower = [...bdCoordinates.value].reverse().map((point) => `L${point.x.toFixed(1)},${(point.y + 13).toFixed(1)}`).join(' ')
  return `${upper}${lower}Z`
})

function quarterLabel(value: string): string { return value.replace(/(\d{4})Q(\d)/, '$1 Q$2') }
function numberOnly(value: number | null | undefined): string {
  if (value == null) return '—'
  return Math.abs(value) >= 1000 ? (value / 1000).toLocaleString('en-US', { minimumFractionDigits: 3, maximumFractionDigits: 3 }) : value.toLocaleString('en-US', { maximumFractionDigits: 3 })
}
async function activate(): Promise<void> {
  if (loaded.value) return
  const ids = new Set(headline.value.flatMap((finding) => finding.series_ids))
  details.value = await Promise.all(props.series.filter((item) => ids.has(item.series_id)).map((item) => loadSeriesDetail(item)))
  loaded.value = true
}
function sourceList(finding: Finding): SourceRecord[] { return resolveSources(finding.source_ids, props.sources) }

onMounted(() => {
  if (!('IntersectionObserver' in window)) { void activate(); return }
  observer = new IntersectionObserver((entries) => { if (entries.some((entry) => entry.isIntersecting)) { void activate(); observer?.disconnect() } }, { rootMargin: '500px' })
  if (root.value) observer.observe(root.value)
})
onBeforeUnmount(() => observer?.disconnect())
</script>

<template>
  <section id="headline-findings" ref="root" class="findings-v2" aria-label="核心发现">
    <article :id="`finding-${f1.finding_id}`" class="finding-page chapter chapter--inklight finding-f1">
      <div class="shell shell--wide">
        <header class="finding-head f1-heading"><p class="eyebrow">FINDING / 01 · {{ f1.strength }}</p><h2>同一季度<br><span>两个合法读数</span></h2><p>改变的不是时间，而是报告定义。</p></header>
        <div ref="f1Story" class="f1-scrolly f1-dual-reading">
          <div class="f1-stage">
            <section class="f1-definition f1-definition--legacy">
              <p>LEGACY</p>
              <article v-for="row in f1Rows" :key="`${row.name}-legacy`"><span>{{ row.name }}</span><strong>{{ numberOnly(row.legacy?.value) }}</strong><small>BILLION KRW · V1</small></article>
            </section>
            <div class="f1-center"><i/><b>{{ quarterLabel(f1Quarter) }}</b><span>SAME QUARTER</span><em>REPORTING<br>DEFINITION<br>SEAM</em><i/></div>
            <section class="f1-definition f1-definition--royalty">
              <p>ROYALTY-INTEGRATED</p>
              <article v-for="row in f1Rows" :key="`${row.name}-royalty`"><span>{{ row.name }}</span><strong>{{ numberOnly(row.royalty?.value) }}</strong><small>BILLION KRW · V2</small></article>
            </section>
            <p class="f1-difference">definition difference ≠ growth · SAME HORIZONTAL COORDINATE · DO NOT STITCH</p>
          </div>
          <div class="f1-steps" aria-label="切换 F1 重叠季度">
            <div v-for="(quarter, index) in ['2025Q2','2025Q3','2025Q4']" :key="quarter" class="f1-step" :class="{ active: f1QuarterIndex === index }" :data-scrolly-step="index" tabindex="0"><span>{{ quarterLabel(quarter) }}</span><p>{{ index === 0 ? '重叠窗口开始。' : index === 1 ? '两个定义继续并存。' : '重叠结束，仍不可拼接。' }}</p></div>
          </div>
        </div>
        <p class="body-lg finding-statement">{{ f1.statement_zh }}</p>
        <div class="finding-boundary"><p><strong>限制</strong> {{ f1.limitations }}</p><p><strong>禁止解读</strong> {{ f1.forbidden_interpretation }}</p></div>
        <div class="source-action"><button class="native-control" :aria-expanded="openFinding === 'F1'" @click="openFinding = openFinding === 'F1' ? null : 'F1'">F1 证据来源</button><SourceList v-if="openFinding === 'F1'" :sources="sourceList(f1)" /></div>
      </div>
    </article>

    <article :id="`finding-${f2.finding_id}`" class="finding-page chapter chapter--surface finding-f2">
      <div class="shell shell--wide">
        <header class="finding-head f2-heading"><p class="eyebrow">FINDING / 02 · {{ f2.strength }}</p><h2 class="display-chapter">The Spike / 同期尖峰</h2><p class="finding-en">{{ f2.title_zh }}</p></header>
        <div class="f2-stage f2-spike-stage">
          <svg viewBox="0 0 1000 520" preserveAspectRatio="none" aria-hidden="true">
            <line x1="40" y1="440" x2="960" y2="440" class="spike-baseline"/><path d="M70,405 L330,390 L610,72 L930,300" class="spike-path"/>
            <line x1="610" y1="34" x2="610" y2="470" class="spike-event-tick"/><circle cx="330" cy="390" r="7"/><circle cx="610" cy="72" r="10"/>
          </svg>
          <div class="f2-origin"><span>2025 Q1</span><b>{{ numberOnly(stellarA?.value) }}</b><small>BILLION KRW</small></div>
          <div class="f2-peak"><span>2025 Q2 / WINDOW PEAK</span><b>{{ numberOnly(stellarB?.value) }}</b><small>BILLION KRW</small></div>
          <strong class="f2-number">+837.3%</strong>
          <div class="f2-event"><i/><span>PC RELEASE</span><p>same quarter · not causal proof · 同期事件不是因果证据</p></div>
        </div>
        <p class="body-lg finding-statement">{{ f2.statement_zh }}</p>
        <div class="finding-boundary"><p><strong>限制</strong> {{ f2.limitations }}</p><p><strong>禁止解读</strong> {{ f2.forbidden_interpretation }}</p></div>
        <div class="source-action"><button class="native-control" :aria-expanded="openFinding === 'F2'" @click="openFinding = openFinding === 'F2' ? null : 'F2'">F2 证据来源</button><SourceList v-if="openFinding === 'F2'" :sources="sourceList(f2)" /></div>
      </div>
    </article>

    <article :id="`finding-${f4.finding_id}`" class="finding-page chapter chapter--paper finding-f4">
      <div class="shell shell--wide">
        <header class="finding-head f4-heading"><p class="eyebrow">FINDING / 04 · {{ f4.strength }}</p><h2 class="display-chapter">一轮恢复之后，<br>潮位再次退去</h2><p class="finding-en">{{ f4.title_en }}</p></header>
        <figure class="f4-chart f4-tidal-sequence">
          <svg viewBox="0 0 1000 320" role="img" aria-label="Black Desert 先回撤、三季度后恢复到新峰值、随后再次回撤">
            <line x1="40" y1="252" x2="960" y2="252" class="f4-baseline"/>
            <g class="f4-quarter-ticks"><line v-for="point in bdCoordinates" :key="point.item.observation_id" :x1="point.x" :x2="point.x" y1="246" y2="258"/></g>
            <path :d="bdBandPath" class="f4-band"/><path :d="bdLinePath" class="f4-band-core"/>
            <g v-for="point in bdCoordinates" :key="`${point.item.observation_id}-node`"><circle :cx="point.x" :cy="point.y" r="5"/><text :x="point.x" y="282" text-anchor="middle">{{ quarterLabel(point.item.quarter) }}</text></g>
            <g class="f4-annotations"><text x="150" y="52">PEAK</text><path d="M185,58V91"/><text x="350" y="236">DRAW DOWN 20.7%</text><path d="M437,218V192"/><text x="470" y="39">RECOVERY · 3Q</text><path d="M548,46V72"/><text x="578" y="66">NEW PEAK</text><path d="M592,72V92"/><text x="765" y="235">DRAW DOWN 30.8%</text><path d="M938,218V191"/></g>
          </svg>
          <figcaption>Quarterly commercial data · 一次恢复，不等于持续增长；观察窗口末未恢复，也不等于永久下降。</figcaption>
        </figure>
        <p class="body-lg finding-statement">{{ f4.statement_zh }}</p>
        <div class="finding-boundary"><p><strong>限制</strong> {{ f4.limitations }}</p><p><strong>禁止解读</strong> {{ f4.forbidden_interpretation }}</p></div>
        <div class="source-action"><button class="native-control" :aria-expanded="openFinding === 'F4'" @click="openFinding = openFinding === 'F4' ? null : 'F4'">F4 证据来源</button><SourceList v-if="openFinding === 'F4'" :sources="sourceList(f4)" /></div>
      </div>
    </article>
  </section>
</template>
