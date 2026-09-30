<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { loadSeriesDetail } from '../../data/client'
import type { Finding, Observation, SeriesDetail, SeriesIndexRecord, SourceRecord } from '../../types/webData'
import { resolveSources } from '../../utils/model'
import { useScrolly } from '../../composables/useScrolly'
import { areaToBaselinePath, ribbonPath, smoothPath } from '../../utils/tidalGeometry'
import SourceList from '../evidence/SourceList.vue'

const props = defineProps<{ findings: Finding[]; series: SeriesIndexRecord[]; sources: SourceRecord[] }>()
const root = ref<HTMLElement | null>(null)
const f1Story = ref<HTMLElement | null>(null)
const f2Root = ref<HTMLElement | null>(null)
const f4Root = ref<HTMLElement | null>(null)
const f2Visible = ref(false)
const f4Visible = ref(false)
const { activeIndex: f1QuarterIndex } = useScrolly({ container: f1Story, stepCount: 3, rootMargin: '-20% 0px -55% 0px' })
const details = ref<SeriesDetail[]>([])
const loaded = ref(false)
const openFinding = ref<string | null>(null)
let observer: IntersectionObserver | null = null
let revealObserver: IntersectionObserver | null = null

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
const stellarCoordinates = computed(() => {
  const observations = stellar.value?.observations.filter((item): item is Observation & { value: number } => item.value !== null).sort((a, b) => a.period_index - b.period_index) ?? []
  if (!observations.length) return []
  const low = Math.min(...observations.map((item) => item.value)); const high = Math.max(...observations.map((item) => item.value))
  return observations.map((item, index) => ({ item, x: 65 + index / Math.max(observations.length - 1, 1) * 870, y: 430 - (item.value - low) / Math.max(high - low, 1) * 330 }))
})
const stellarAreaPath = computed(() => areaToBaselinePath(stellarCoordinates.value, 440))
const stellarRidgePath = computed(() => smoothPath(stellarCoordinates.value))
const stellarQ1Point = computed(() => stellarCoordinates.value.find((point) => point.item.observation_id === 'obs_stellar_2025q1'))
const stellarQ2Point = computed(() => stellarCoordinates.value.find((point) => point.item.observation_id === 'obs_stellar_2025q2'))
const blackDesert = computed(() => details.value.find((item) => item.series_id === 'series_black_desert'))
const bdObservations = computed(() => blackDesert.value?.observations.filter((item): item is Observation & { value: number } => item.value !== null).sort((a, b) => a.period_index - b.period_index) ?? [])
const bdCoordinates = computed(() => {
  const observations = bdObservations.value
  if (!observations.length) return []
  const min = Math.min(...observations.map((item) => item.value)); const max = Math.max(...observations.map((item) => item.value))
  return observations.map((item, i) => ({ item, x: 60 + i / Math.max(observations.length - 1, 1) * 880, y: 228 - (item.value - min) / Math.max(max - min, 1) * 154 }))
})
const bdLinePath = computed(() => smoothPath(bdCoordinates.value))
const bdBandPath = computed(() => ribbonPath(bdCoordinates.value, 24))
const bdReflectionPath = computed(() => smoothPath(bdCoordinates.value.map((point) => ({ x: point.x, y: 268 + (252 - point.y) * .14 }))))

function quarterLabel(value: string): string { return value.replace(/(\d{4})Q(\d)/, '$1 Q$2') }
function numberOnly(value: number | null | undefined): string {
  if (value == null) return '—'
  return Math.abs(value) >= 1000 ? (value / 1000).toLocaleString('en-US', { minimumFractionDigits: 3, maximumFractionDigits: 3 }) : value.toLocaleString('en-US', { maximumFractionDigits: 3 })
}
function f1Ribbon(row: { legacy: Observation | null; royalty: Observation | null }, key: 'legacy' | 'royalty'): string {
  const value = row[key]?.value ?? 0; const max = Math.max(row.legacy?.value ?? 0, row.royalty?.value ?? 0, 1); const ratio = value / max
  const center = 112 - ratio * 58 + (key === 'royalty' ? 3 : 0)
  return ribbonPath([{ x: 5, y: center + 5 }, { x: 320, y: center }, { x: 680, y: center - 5 }, { x: 995, y: center + 1 }], 9 + ratio * 14)
}
function f1Gap(row: { legacy: Observation | null; royalty: Observation | null }): string {
  if (row.legacy?.value == null || row.royalty?.value == null) return '—'
  return numberOnly(Math.abs(row.royalty.value - row.legacy.value))
}
function f1Slug(value: string): string { return value.toLowerCase().replace(/[^a-z0-9]+/g, '-') }
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
  revealObserver = new IntersectionObserver((entries) => entries.forEach((entry) => {
    if (!entry.isIntersecting) return
    if (entry.target === f2Root.value) f2Visible.value = true
    if (entry.target === f4Root.value) f4Visible.value = true
  }), { threshold: .28 })
  if (f2Root.value) revealObserver.observe(f2Root.value)
  if (f4Root.value) revealObserver.observe(f4Root.value)
})
onBeforeUnmount(() => { observer?.disconnect(); revealObserver?.disconnect() })
</script>

<template>
  <section id="headline-findings" ref="root" class="findings-v2" aria-label="核心发现">
    <article :id="`finding-${f1.finding_id}`" class="finding-page chapter chapter--inklight finding-f1">
      <div class="shell shell--wide">
        <header class="finding-head f1-heading"><p class="eyebrow">FINDING / 01 · {{ f1.strength }}</p><h2>同一季度<br><span>两个合法读数</span></h2><p>改变的不是时间，而是报告定义。</p></header>
        <div ref="f1Story" class="f1-scrolly f1-dual-reading">
          <div class="f1-stage">
            <div class="f1-flow-field" aria-hidden="true">
              <div v-for="row in f1Rows" :key="`${row.name}-flow`" class="f1-flow-row">
                <svg viewBox="0 0 1000 145" preserveAspectRatio="none"><defs><linearGradient :id="`f1-legacy-${f1Slug(row.name)}`"><stop stop-color="#0b5662" stop-opacity=".18"/><stop offset=".5" stop-color="#24a8a0" stop-opacity=".82"/><stop offset="1" stop-color="#7de2cc" stop-opacity=".18"/></linearGradient><linearGradient :id="`f1-royalty-${f1Slug(row.name)}`"><stop stop-color="#a95d3b" stop-opacity=".16"/><stop offset=".5" stop-color="#ee805f" stop-opacity=".78"/><stop offset="1" stop-color="#ffc09f" stop-opacity=".16"/></linearGradient></defs><path :d="f1Ribbon(row,'legacy')" :fill="`url(#f1-legacy-${f1Slug(row.name)})`"/><path :d="f1Ribbon(row,'royalty')" :fill="`url(#f1-royalty-${f1Slug(row.name)})`"/><line x1="505" y1="34" x2="505" y2="112"/><path d="M492 35H518 M492 111H518"/><text x="528" y="75">Δ {{ f1Gap(row) }} BN</text></svg>
              </div>
            </div>
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

    <article :id="`finding-${f2.finding_id}`" ref="f2Root" class="finding-page chapter chapter--surface finding-f2" :class="{ 'is-visible': f2Visible }">
      <div class="shell shell--wide">
        <header class="finding-head f2-heading"><p class="eyebrow">FINDING / 02 · {{ f2.strength }}</p><h2 class="display-chapter">The Spike / 同期尖峰</h2><p class="finding-en">{{ f2.title_zh }}</p></header>
        <div class="f2-stage f2-spike-stage">
          <svg viewBox="0 0 1000 520" preserveAspectRatio="none" aria-hidden="true">
            <defs><linearGradient id="stellar-surge" x1="0" y1="1" x2=".8" y2="0"><stop stop-color="#0b5662" stop-opacity=".18"/><stop offset=".58" stop-color="#24a8a0" stop-opacity=".72"/><stop offset="1" stop-color="#7de2cc" stop-opacity=".34"/></linearGradient><radialGradient id="stellar-crest"><stop stop-color="#e7fff8" stop-opacity=".92"/><stop offset=".25" stop-color="#7de2cc" stop-opacity=".5"/><stop offset="1" stop-color="#7de2cc" stop-opacity="0"/></radialGradient><filter id="stellar-glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="13"/></filter></defs>
            <line x1="40" y1="440" x2="960" y2="440" class="spike-baseline"/><path :d="stellarAreaPath" class="spike-area" fill="url(#stellar-surge)"/><path :d="stellarRidgePath" class="spike-glow"/><path :d="stellarRidgePath" class="spike-path"/>
            <circle v-if="stellarQ2Point" :cx="stellarQ2Point.x" :cy="stellarQ2Point.y" r="82" class="spike-crest-halo" fill="url(#stellar-crest)" filter="url(#stellar-glow)"/>
            <line v-if="stellarQ2Point" :x1="stellarQ2Point.x" :x2="stellarQ2Point.x" y1="34" y2="470" class="spike-event-tick"/>
            <g class="spike-nodes"><circle v-for="point in stellarCoordinates" :key="point.item.observation_id" :cx="point.x" :cy="point.y" :r="point.item.observation_id === 'obs_stellar_2025q2' ? 10 : 5"/></g>
          </svg>
          <div class="f2-origin" :style="{ left: `${(stellarQ1Point?.x ?? 300) / 10}%` }"><span>2025 Q1</span><b>{{ numberOnly(stellarA?.value) }}</b><small>BILLION KRW</small></div>
          <div class="f2-peak" :style="{ left: `${(stellarQ2Point?.x ?? 600) / 10}%` }"><span>2025 Q2 / WINDOW PEAK</span><b>{{ numberOnly(stellarB?.value) }}</b><small>BILLION KRW</small></div>
          <strong class="f2-number">+837.3%</strong>
          <div class="f2-event" :style="{ left: `${(stellarQ2Point?.x ?? 600) / 10}%` }"><i/><span>PC RELEASE</span><p>same quarter · not causal proof · 同期事件不是因果证据</p></div>
        </div>
        <p class="body-lg finding-statement">{{ f2.statement_zh }}</p>
        <div class="finding-boundary"><p><strong>限制</strong> {{ f2.limitations }}</p><p><strong>禁止解读</strong> {{ f2.forbidden_interpretation }}</p></div>
        <div class="source-action"><button class="native-control" :aria-expanded="openFinding === 'F2'" @click="openFinding = openFinding === 'F2' ? null : 'F2'">F2 证据来源</button><SourceList v-if="openFinding === 'F2'" :sources="sourceList(f2)" /></div>
      </div>
    </article>

    <article :id="`finding-${f4.finding_id}`" ref="f4Root" class="finding-page chapter chapter--paper finding-f4" :class="{ 'is-visible': f4Visible }">
      <div class="shell shell--wide">
        <header class="finding-head f4-heading"><p class="eyebrow">FINDING / 04 · {{ f4.strength }}</p><h2 class="display-chapter">一轮恢复之后，<br>潮位再次退去</h2><p class="finding-en">{{ f4.title_en }}</p></header>
        <figure class="f4-chart f4-tidal-sequence">
          <svg viewBox="0 0 1000 320" role="img" aria-label="Black Desert 先回撤、三季度后恢复到新峰值、随后再次回撤">
            <defs><linearGradient id="black-desert-tide" x1="0" y1=".8" x2="1" y2=".2"><stop stop-color="#0b5662" stop-opacity=".2"/><stop offset=".44" stop-color="#24a8a0" stop-opacity=".76"/><stop offset=".72" stop-color="#7de2cc" stop-opacity=".5"/><stop offset="1" stop-color="#1a7780" stop-opacity=".18"/></linearGradient><filter id="black-desert-glow" x="-20%" y="-80%" width="140%" height="260%"><feGaussianBlur stdDeviation="8"/></filter></defs>
            <line x1="40" y1="252" x2="960" y2="252" class="f4-baseline"/>
            <g class="f4-quarter-ticks"><line v-for="point in bdCoordinates" :key="point.item.observation_id" :x1="point.x" :x2="point.x" y1="246" y2="258"/></g>
            <path :d="bdReflectionPath" class="f4-reflection"/><path :d="bdLinePath" class="f4-band-glow" filter="url(#black-desert-glow)"/><path :d="bdBandPath" class="f4-band" fill="url(#black-desert-tide)"/><path :d="bdLinePath" class="f4-band-core"/>
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
