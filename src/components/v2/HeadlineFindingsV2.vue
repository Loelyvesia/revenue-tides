<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { loadSeriesDetail } from '../../data/client'
import type { Finding, Observation, SeriesDetail, SeriesIndexRecord, SourceRecord } from '../../types/webData'
import { formatKrwMillion, resolveSources } from '../../utils/model'
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
const allObservations = computed(() => details.value.flatMap((detail) => detail.observations))
const f1Quarter = computed(() => ['2025Q2', '2025Q3', '2025Q4'][f1QuarterIndex.value])
const f1Rows = computed(() => ['series_lineage_m', 'series_lineage_2m', 'series_lineage_w'].map((seriesId) => {
  const detail = details.value.find((item) => item.series_id === seriesId)
  const values = detail?.observations.filter((item) => item.quarter === f1Quarter.value) ?? []
  return { name: detail?.identity.entity ?? seriesId, legacy: values.find((item) => item.metric_version.includes('legacy')) ?? null, royalty: values.find((item) => item.metric_version.includes('royalty')) ?? null }
}))
const stellar = computed(() => details.value.find((item) => item.series_id === 'series_stellar_blade'))
const stellarA = computed(() => stellar.value?.observations.find((item) => item.observation_id === 'obs_stellar_2025q1') ?? null)
const stellarB = computed(() => stellar.value?.observations.find((item) => item.observation_id === 'obs_stellar_2025q2') ?? null)
const blackDesert = computed(() => details.value.find((item) => item.series_id === 'series_black_desert'))
const bdPoints = computed(() => {
  const obs = blackDesert.value?.observations.filter((item): item is Observation & { value: number } => item.value !== null).sort((a, b) => a.period_index - b.period_index) ?? []
  if (!obs.length) return ''
  const min = Math.min(...obs.map((item) => item.value)); const max = Math.max(...obs.map((item) => item.value))
  return obs.map((item, i) => `${50 + i / Math.max(obs.length - 1, 1) * 700},${230 - (item.value - min) / Math.max(max - min, 1) * 155}`).join(' ')
})

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
      <div class="shell">
        <header class="finding-head"><p class="eyebrow">ACT III · F1 · {{ f1.strength }}</p><h2 class="display-chapter">{{ f1.title_zh }}</h2><p class="finding-en">{{ f1.title_en }}</p><p class="body-lg">{{ f1.statement_zh }}</p></header>
        <div ref="f1Story" class="f1-scrolly">
          <div class="f1-steps">
            <div v-for="(quarter, index) in ['2025Q2','2025Q3','2025Q4']" :key="quarter" class="f1-step" :class="{ active: f1QuarterIndex === index }" :data-scrolly-step="index" tabindex="0"><span>{{ quarter }}</span><p>{{ index === 0 ? '重叠窗口开始。' : index === 1 ? '定义差异继续存在。' : '重叠窗口结束；版本仍不可拼接。' }}</p></div>
          </div>
          <div class="f1-stage">
            <p class="eyebrow">SAME QUARTER · TWO DEFINITIONS</p>
            <h3 class="display-figure">{{ f1Quarter }}</h3>
            <div v-for="row in f1Rows" :key="row.name" class="definition-pair">
              <strong>{{ row.name }}</strong><span>legacy<br><b>{{ formatKrwMillion(row.legacy?.value ?? null) }}</b></span><i aria-hidden="true"/><span>royalty-integrated<br><b>{{ formatKrwMillion(row.royalty?.value ?? null) }}</b></span>
            </div>
            <p class="definition-warning">REPORTING DEFINITION SEAM · difference ≠ growth</p>
          </div>
        </div>
        <div class="finding-boundary"><p><strong>限制</strong> {{ f1.limitations }}</p><p><strong>禁止解读</strong> {{ f1.forbidden_interpretation }}</p></div>
        <div class="source-action"><button class="native-control" :aria-expanded="openFinding === 'F1'" @click="openFinding = openFinding === 'F1' ? null : 'F1'">F1 证据来源</button><SourceList v-if="openFinding === 'F1'" :sources="sourceList(f1)" /></div>
      </div>
    </article>

    <article :id="`finding-${f2.finding_id}`" class="finding-page chapter chapter--dark finding-f2">
      <div class="shell">
        <header class="finding-head"><p class="eyebrow">F2 · {{ f2.strength }}</p><h2 class="display-chapter">{{ f2.title_zh }}</h2><p class="finding-en">{{ f2.title_en }}</p></header>
        <div class="f2-stage">
          <div class="f2-values"><span><small>2025 Q1</small>{{ formatKrwMillion(stellarA?.value ?? null) }}</span><b aria-hidden="true">→</b><span class="peak"><small>2025 Q2 · WINDOW PEAK</small>{{ formatKrwMillion(stellarB?.value ?? null) }}</span></div>
          <strong class="f2-number display-figure">+837.3%</strong>
          <div class="f2-event"><i/><span>PC LAUNCH · SAME QUARTER</span><p>同期事件不是因果证据；PC 单独收入不可得。</p></div>
        </div>
        <p class="body-lg finding-statement">{{ f2.statement_zh }}</p>
        <div class="finding-boundary"><p><strong>限制</strong> {{ f2.limitations }}</p><p><strong>禁止解读</strong> {{ f2.forbidden_interpretation }}</p></div>
        <div class="source-action"><button class="native-control" :aria-expanded="openFinding === 'F2'" @click="openFinding = openFinding === 'F2' ? null : 'F2'">F2 证据来源</button><SourceList v-if="openFinding === 'F2'" :sources="sourceList(f2)" /></div>
      </div>
    </article>

    <article :id="`finding-${f4.finding_id}`" class="finding-page chapter chapter--paper finding-f4">
      <div class="shell">
        <header class="finding-head"><p class="eyebrow">F4 · {{ f4.strength }}</p><h2 class="display-chapter">{{ f4.title_zh }}</h2><p class="finding-en">{{ f4.title_en }}</p><p class="body-lg">{{ f4.statement_zh }}</p></header>
        <figure class="f4-chart">
          <svg viewBox="0 0 800 300" role="img" aria-label="Black Desert 先回撤、三季度后恢复到新峰值、随后再次回撤">
            <line x1="45" y1="235" x2="755" y2="235"/><polyline :points="bdPoints"/>
            <circle cx="150" cy="110" r="6"/><circle cx="350" cy="180" r="6"/><circle cx="450" cy="75" r="6"/><circle cx="750" cy="180" r="6"/>
            <text x="135" y="90">PEAK</text><text x="325" y="205">−20.7%</text><text x="425" y="55">RECOVERED · 3Q</text><text x="665" y="205">−30.8%</text>
          </svg>
          <figcaption>一次恢复，不等于持续增长；窗口末未恢复，也不等于永久下降。</figcaption>
        </figure>
        <div class="finding-boundary"><p><strong>限制</strong> {{ f4.limitations }}</p><p><strong>禁止解读</strong> {{ f4.forbidden_interpretation }}</p></div>
        <div class="source-action"><button class="native-control" :aria-expanded="openFinding === 'F4'" @click="openFinding = openFinding === 'F4' ? null : 'F4'">F4 证据来源</button><SourceList v-if="openFinding === 'F4'" :sources="sourceList(f4)" /></div>
      </div>
    </article>
  </section>
</template>
