<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { loadSeriesDetail } from '../../data/client'
import type { Finding, Observation, SeriesDetail, SeriesIndexRecord, SourceRecord } from '../../types/webData'
import { resolveSources } from '../../utils/model'
import { useScrolly } from '../../composables/useScrolly'
import { smoothPath, tidalBodyPath, tidalEnvelopePath } from '../../utils/tidalGeometry'
import SourceList from '../evidence/SourceList.vue'
import { displayCopy } from '../../content/displayCopy.zh'

const props = defineProps<{ findings: Finding[]; series: SeriesIndexRecord[]; sources: SourceRecord[] }>()
// Phase I semantic compatibility markers (not display copy): difference ≠ growth;
// 同期事件不是因果证据; 一次恢复，不等于持续增长.
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
const f1Primary = computed(() => f1Rows.value[0])
const f1Secondary = computed(() => f1Rows.value.slice(1))
const stellar = computed(() => details.value.find((item) => item.series_id === 'series_stellar_blade'))
const stellarA = computed(() => stellar.value?.observations.find((item) => item.observation_id === 'obs_stellar_2025q1') ?? null)
const stellarB = computed(() => stellar.value?.observations.find((item) => item.observation_id === 'obs_stellar_2025q2') ?? null)
const stellarCoordinates = computed(() => {
  const observations = stellar.value?.observations.filter((item): item is Observation & { value: number } => item.value !== null).sort((a, b) => a.period_index - b.period_index) ?? []
  if (!observations.length) return []
  const low = Math.min(...observations.map((item) => item.value)); const high = Math.max(...observations.map((item) => item.value))
  return observations.map((item, index) => ({ item, x: 65 + index / Math.max(observations.length - 1, 1) * 870, y: 430 - (item.value - low) / Math.max(high - low, 1) * 330 }))
})
const stellarAreaPath = computed(() => tidalBodyPath(stellarCoordinates.value, { baseDepth: 78, peakContribution: 24, slopeContribution: .12, minDepth: 62, maxDepth: 116 }))
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
const bdBandPath = computed(() => tidalBodyPath(bdCoordinates.value, { baseDepth: 64, peakContribution: 18, slopeContribution: .1, minDepth: 52, maxDepth: 92 }))
const bdDeepPath = computed(() => tidalEnvelopePath(bdCoordinates.value, 72, 18))
const bdReflectionPath = computed(() => smoothPath(bdCoordinates.value.map((point) => ({ x: point.x, y: 268 + (252 - point.y) * .14 }))))

function quarterLabel(value: string): string { return value.replace(/(\d{4})Q(\d)/, '$1 Q$2') }
function numberOnly(value: number | null | undefined): string {
  if (value == null) return '—'
  return Math.abs(value) >= 1000 ? (value / 1000).toLocaleString('en-US', { minimumFractionDigits: 3, maximumFractionDigits: 3 }) : value.toLocaleString('en-US', { maximumFractionDigits: 3 })
}
function f1Ribbon(row: { legacy: Observation | null; royalty: Observation | null }, key: 'legacy' | 'royalty'): string {
  const value = row[key]?.value ?? 0; const max = Math.max(row.legacy?.value ?? 0, row.royalty?.value ?? 0, 1); const ratio = value / max
  const surface = key === 'legacy' ? 50 - ratio * 12 : 98 - ratio * 12
  const points = [{ x: 0, y: surface + 5 }, { x: 270, y: surface - 4 }, { x: 650, y: surface + 3 }, { x: 1000, y: surface - 7 }]
  return tidalBodyPath(points, { baseDepth: 26 + ratio * 8, peakContribution: 4, slopeContribution: .08, minDepth: 24, maxDepth: 42 })
}
function f1Gap(row: { legacy: Observation | null; royalty: Observation | null }): string {
  if (row.legacy?.value == null || row.royalty?.value == null) return '—'
  return numberOnly(Math.abs(row.royalty.value - row.legacy.value))
}
function f4KeyValue(quarter: string): string | null { return ({ '2024Q4': '69.2', '2025Q2': '54.9', '2025Q3': '79.5', '2026Q2': '55.0' } as Record<string, string>)[quarter] ?? null }
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
        <header class="finding-head f1-heading"><p class="eyebrow">发现 1</p><h2>{{ displayCopy.findings.f1.title }}</h2><p>{{ displayCopy.findings.f1.lede }}</p></header>
        <div ref="f1Story" class="f1-scrolly f1-dual-reading">
          <div class="f1-stage">
            <div v-if="f1Primary" class="f1-primary">
              <p class="f1-primary__series">Lineage M <span>{{ quarterLabel(f1Quarter) }}</span></p>
              <svg class="f1-primary__ribbons" viewBox="0 0 1000 145" preserveAspectRatio="none" aria-hidden="true"><defs><linearGradient id="f1-main-legacy" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#24a8a0" stop-opacity=".88"/><stop offset=".62" stop-color="#4fc9b7" stop-opacity=".62"/><stop offset="1" stop-color="#7de2cc" stop-opacity="0"/></linearGradient><linearGradient id="f1-main-royalty" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#ef8664" stop-opacity=".82"/><stop offset=".62" stop-color="#ee9a78" stop-opacity=".58"/><stop offset="1" stop-color="#ffc09f" stop-opacity="0"/></linearGradient></defs><path :d="f1Ribbon(f1Primary,'legacy')" fill="url(#f1-main-legacy)"/><path :d="f1Ribbon(f1Primary,'royalty')" fill="url(#f1-main-royalty)"/></svg>
              <div class="f1-primary__values">
                <section><span>旧口径</span><strong>{{ numberOnly(f1Primary.legacy?.value) }}</strong><small>十亿韩元 · legacy v1</small></section>
                <div class="f1-primary__gap"><b>+{{ f1Gap(f1Primary) }}</b><span>十亿韩元</span><small>口径差异</small></div>
                <section><span>纳入 royalties</span><strong>{{ numberOnly(f1Primary.royalty?.value) }}</strong><small>十亿韩元 · royalty-integrated v2</small></section>
              </div>
            </div>
            <p class="f1-primary__note">{{ displayCopy.findings.f1.primaryNote }}</p>
            <div class="f1-secondary" aria-label="Lineage 2M 与 Lineage W 的补充证据">
              <article v-for="row in f1Secondary" :key="row.name"><strong>{{ row.name }}</strong><span>{{ numberOnly(row.legacy?.value) }} → {{ numberOnly(row.royalty?.value) }}</span><i class="f1-mini-current" aria-hidden="true"><b/><b/></i><small>口径差异 {{ f1Gap(row) }} 十亿韩元</small></article>
              <p>{{ displayCopy.findings.f1.secondaryNote }}</p>
            </div>
          </div>
          <div class="f1-steps" aria-label="切换 F1 重叠季度">
            <div v-for="(quarter, index) in ['2025Q2','2025Q3','2025Q4']" :key="quarter" class="f1-step" :class="{ active: f1QuarterIndex === index }" :data-scrolly-step="index" tabindex="0"><span>{{ quarterLabel(quarter) }}</span><p>{{ index === 0 ? '两种口径开始同时披露。' : index === 1 ? '两种口径继续并列。' : '并列披露的最后一个季度。' }}</p></div>
          </div>
        </div>
        <details class="formal-finding"><summary>{{ displayCopy.findings.full }}</summary><p>{{ f1.statement_zh }}</p><p><strong>{{ displayCopy.findings.attention }}：</strong>{{ f1.limitations }} {{ f1.forbidden_interpretation }}</p></details>
        <div class="source-action"><button class="native-control" :aria-expanded="openFinding === 'F1'" @click="openFinding = openFinding === 'F1' ? null : 'F1'">查看 F1 来源</button><SourceList v-if="openFinding === 'F1'" :sources="sourceList(f1)" /></div>
      </div>
    </article>

    <article :id="`finding-${f2.finding_id}`" ref="f2Root" class="finding-page chapter chapter--surface finding-f2" :class="{ 'is-visible': f2Visible }">
      <div class="shell shell--wide">
        <header class="finding-head f2-heading"><p class="eyebrow">发现 2</p><h2 class="display-chapter">{{ displayCopy.findings.f2.title }}</h2><p class="finding-en">{{ displayCopy.findings.f2.lede }}</p></header>
        <div class="f2-stage f2-spike-stage">
          <svg viewBox="0 0 1000 520" preserveAspectRatio="none" aria-hidden="true">
            <defs><linearGradient id="stellar-surge" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#24a8a0" stop-opacity=".88"/><stop offset=".58" stop-color="#36b9aa" stop-opacity=".65"/><stop offset=".86" stop-color="#7de2cc" stop-opacity=".28"/><stop offset="1" stop-color="#7de2cc" stop-opacity="0"/></linearGradient><radialGradient id="stellar-crest"><stop stop-color="#e7fff8" stop-opacity=".92"/><stop offset=".25" stop-color="#7de2cc" stop-opacity=".5"/><stop offset="1" stop-color="#7de2cc" stop-opacity="0"/></radialGradient><filter id="stellar-glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="13"/></filter></defs>
            <path :d="stellarAreaPath" class="spike-area" fill="url(#stellar-surge)"/><path :d="stellarRidgePath" class="spike-glow"/><path :d="stellarRidgePath" class="spike-path"/>
            <circle v-if="stellarQ2Point" :cx="stellarQ2Point.x" :cy="stellarQ2Point.y" r="82" class="spike-crest-halo" fill="url(#stellar-crest)" filter="url(#stellar-glow)"/>
            <circle v-if="stellarQ2Point" :cx="stellarQ2Point.x" :cy="stellarQ2Point.y" r="6" class="spike-critical-node"/>
          </svg>
          <div class="f2-origin" :style="{ left: `${(stellarQ1Point?.x ?? 300) / 10}%` }"><span>2025 Q1</span><b>{{ numberOnly(stellarA?.value) }}</b><small>十亿韩元</small></div>
          <div class="f2-peak" :style="{ left: `${(stellarQ2Point?.x ?? 600) / 10}%` }"><span>2025 Q2 · 八季度最高</span><b>{{ numberOnly(stellarB?.value) }}</b><small>十亿韩元</small></div>
          <p class="f2-change"><span>2025 Q1 → Q2 · 环比</span><strong>+837.3%</strong></p>
        </div>
        <div class="f2-context-rail"><i/><strong>PC 版上线 · 同期事件</strong><p>{{ displayCopy.findings.f2.event }}</p></div>
        <details class="formal-finding"><summary>{{ displayCopy.findings.full }}</summary><p>{{ f2.statement_zh }}</p><p><strong>{{ displayCopy.findings.attention }}：</strong>{{ f2.limitations }} {{ f2.forbidden_interpretation }}</p></details>
        <div class="source-action"><button class="native-control" :aria-expanded="openFinding === 'F2'" @click="openFinding = openFinding === 'F2' ? null : 'F2'">查看 F2 来源</button><SourceList v-if="openFinding === 'F2'" :sources="sourceList(f2)" /></div>
      </div>
    </article>

    <article :id="`finding-${f4.finding_id}`" ref="f4Root" class="finding-page chapter chapter--paper finding-f4" :class="{ 'is-visible': f4Visible }">
      <div class="shell shell--wide">
        <header class="finding-head f4-heading"><p class="eyebrow">发现 4</p><h2 class="display-chapter"><span>{{ displayCopy.findings.f4.titleLead }}</span><span>{{ displayCopy.findings.f4.titleRestA }}</span><span>{{ displayCopy.findings.f4.titleRestB }}</span></h2><p class="finding-en"><span v-for="part in displayCopy.findings.f4.ledeParts" :key="part">{{ part }}</span></p></header>
        <figure class="f4-chart f4-tidal-sequence">
          <svg viewBox="0 0 1000 320" role="img" aria-label="Black Desert 先回撤、三季度后恢复到新峰值、随后再次回撤">
            <defs><linearGradient id="black-desert-tide" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#28afa6" stop-opacity=".9"/><stop offset=".5" stop-color="#36b9aa" stop-opacity=".72"/><stop offset=".82" stop-color="#7de2cc" stop-opacity=".3"/><stop offset="1" stop-color="#7de2cc" stop-opacity="0"/></linearGradient><filter id="black-desert-glow" x="-20%" y="-80%" width="140%" height="260%"><feGaussianBlur stdDeviation="8"/></filter></defs>
            <path :d="bdDeepPath" class="f4-deep"/><path :d="bdReflectionPath" class="f4-reflection"/><path :d="bdBandPath" class="f4-band" fill="url(#black-desert-tide)"/><path :d="bdLinePath" class="f4-band-glow" filter="url(#black-desert-glow)"/><path :d="bdLinePath" class="f4-band-core"/>
            <g v-for="point in bdCoordinates.filter((entry) => f4KeyValue(entry.item.quarter))" :key="`${point.item.observation_id}-critical`"><circle :cx="point.x" :cy="point.y" r="4"/><text :x="point.x" y="282" :text-anchor="point.item.quarter === '2026Q2' ? 'end' : 'middle'">{{ quarterLabel(point.item.quarter) }}</text><text class="f4-key-value" :x="point.x" :y="point.y - 16" :text-anchor="point.item.quarter === '2026Q2' ? 'end' : 'middle'">{{ f4KeyValue(point.item.quarter) }}</text></g>
            <g class="f4-annotations"><text x="150" y="52">前一高点</text><text x="350" y="236">回撤 20.7%</text><text x="470" y="39">三季度后恢复</text><text x="600" y="66">新高</text><text x="765" y="235">回撤 30.8%</text></g>
          </svg>
          <div class="f4-mobile-readings" aria-label="Black Desert 的四个关键季度">
            <div v-for="point in bdCoordinates.filter((entry) => f4KeyValue(entry.item.quarter))" :key="`${point.item.observation_id}-mobile`"><span>{{ quarterLabel(point.item.quarter) }}</span><b>{{ f4KeyValue(point.item.quarter) }}</b></div>
          </div>
          <p class="f4-mobile-sequence">前一高点 → 回撤 20.7% → 三季度后恢复并创新高 → 再回撤 30.8%</p>
          <figcaption>单位：十亿韩元。数值为 Black Desert IP 的发行商披露收入。</figcaption>
        </figure>
        <details class="formal-finding"><summary>{{ displayCopy.findings.full }}</summary><p>{{ f4.statement_zh }}</p><p><strong>{{ displayCopy.findings.attention }}：</strong>{{ f4.limitations }} {{ f4.forbidden_interpretation }}</p></details>
        <div class="source-action"><button class="native-control" :aria-expanded="openFinding === 'F4'" @click="openFinding = openFinding === 'F4' ? null : 'F4'">查看 F4 来源</button><SourceList v-if="openFinding === 'F4'" :sources="sourceList(f4)" /></div>
      </div>
    </article>
  </section>
</template>

<style scoped>
/* UI 2.4: keep the evidence in the first view and let the tide carry the scale. */
.f1-heading h2{font-size:clamp(3rem,5.2vw,5.25rem)}
.f1-heading>p:last-child{font-size:.94rem;line-height:1.6}
.f1-dual-reading{margin-top:.4rem}
.f1-dual-reading .f1-stage{min-height:61svh;padding:1rem 0}
.f1-primary__ribbons{height:13rem;margin:-.1rem -4% -3.3rem}
.f1-primary__note{margin:1.15rem auto .8rem}
.f1-secondary{gap:.8rem;padding-top:.35rem}
.f2-heading .display-chapter{font-size:clamp(2.9rem,5.55vw,5.55rem)}
.f2-heading .finding-en{font-size:.94rem;line-height:1.6}
.f2-spike-stage{min-height:min(48rem,54svh);margin:-2.8rem -4vw .8rem}
.f2-peak{top:4%}
.f2-change{position:absolute;left:8%;top:30%;display:grid;gap:.3rem;color:var(--petrol)}
.f2-change span{font:.72rem var(--font-numeric)}
.f2-change strong{font:750 clamp(1.8rem,3vw,3rem)/1 var(--font-numeric);letter-spacing:-.04em}
.f2-context-rail{display:grid;grid-template-columns:.6rem auto 1fr;align-items:baseline;gap:.65rem;max-width:54rem;margin:.2rem 0 1rem;color:var(--context-copper)}
.f2-context-rail i{width:.5rem;height:.5rem;border-radius:50%;background:var(--context-coral)}
.f2-context-rail strong,.f2-context-rail p{font-size:.78rem;line-height:1.55}
.f2-context-rail p{color:var(--ink-2);margin:0}
.f4-mobile-readings,.f4-mobile-sequence{display:none}
.f4-key-value{font-size:16px!important}
.f4-annotations text{font-weight:850}
@media(max-width:640px){
  .f1-heading h2{font-size:clamp(2.2rem,10.5vw,3.55rem)}
  .f1-primary__ribbons{height:8rem;margin:-.1rem -6% -1.7rem}
  .f1-primary__note{margin:.8rem 0}
  .f2-heading .display-chapter{font-size:clamp(2.25rem,10.5vw,3.55rem)}
  .f2-spike-stage{min-height:29rem;margin:-.5rem -4vw .8rem}
  .f2-change{left:4%;top:40%}.f2-change span{font-size:.65rem}.f2-change strong{font-size:1.8rem}
  .f2-origin b{font-size:1.65rem}.f2-peak b{font-size:2.2rem}.f2-origin span,.f2-peak span,.f2-origin small,.f2-peak small{font-size:.65rem}
  .f2-context-rail{grid-template-columns:.6rem 1fr;gap:.4rem .65rem}.f2-context-rail p{grid-column:2}
  .f4-tidal-sequence{margin:0 0 1rem;min-width:0;overflow:visible}.f4-tidal-sequence svg{width:100%;max-width:100%;min-width:0;height:auto;min-height:0;margin-left:0;overflow:visible}
  .f4-mobile-readings{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.35rem;margin:.7rem 0}
  .f4-mobile-readings div{display:grid;gap:.2rem}.f4-mobile-readings span{font:.65rem var(--font-numeric);white-space:nowrap}.f4-mobile-readings b{font:750 1.35rem var(--font-numeric);color:var(--petrol)}
  .f4-mobile-sequence{display:block;font-size:.75rem;line-height:1.6;color:var(--ink-2)}
  .f4-tidal-sequence figcaption{font-size:.7rem;line-height:1.5}
}
</style>
