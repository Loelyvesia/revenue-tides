<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { loadSeriesDetail } from '../../data/client'
import type { Finding, Observation, SeriesDetail, SeriesIndexRecord, SourceRecord } from '../../types/webData'
import { formatKrwMillion, resolveSources } from '../../utils/model'
import SourceList from '../evidence/SourceList.vue'

const props = defineProps<{
  finding: Finding
  series: SeriesIndexRecord[]
  sources: SourceRecord[]
  compact?: boolean
}>()

const root = ref<HTMLElement | null>(null)
const details = ref<SeriesDetail[]>([])
const state = ref<'idle' | 'loading' | 'ready' | 'error'>('idle')
const error = ref<string | null>(null)
const evidenceOpen = ref(false)
let observer: IntersectionObserver | null = null

const observations = computed(() => details.value.flatMap((detail) => detail.observations).filter((observation) => props.finding.observation_ids.includes(observation.observation_id)))
const derivedChanges = computed(() => observations.value.filter((observation) => observation.qoq.eligible && observation.derived?.direction_sign_stable !== null))
const signSensitiveCount = computed(() => derivedChanges.value.filter((observation) => observation.derived?.direction_sign_stable === false).length)

async function activate(force = false): Promise<void> {
  if (state.value === 'loading' || (state.value === 'ready' && !force)) return
  state.value = 'loading'
  error.value = null
  try {
    const records = props.finding.series_ids.map((id) => props.series.find((record) => record.series_id === id)).filter((record): record is SeriesIndexRecord => Boolean(record))
    details.value = await Promise.all(records.map((record) => loadSeriesDetail(record, force)))
    state.value = 'ready'
  } catch (reason) {
    error.value = reason instanceof Error ? reason.message : 'Finding evidence load failed'
    state.value = 'error'
  }
}

function value(id: string): number | null {
  return observations.value.find((observation) => observation.observation_id === id)?.value ?? null
}

function f4Path(): string {
  const ordered = [...observations.value].filter((item): item is Observation & { value: number } => item.value !== null).sort((a, b) => a.period_index - b.period_index)
  if (!ordered.length) return ''
  const min = Math.min(...ordered.map((item) => item.value))
  const max = Math.max(...ordered.map((item) => item.value))
  return ordered.map((item, index) => {
    const x = 70 + (index / Math.max(ordered.length - 1, 1)) * 680
    const y = 210 - ((item.value - min) / Math.max(max - min, 1)) * 145
    return `${x},${y}`
  }).join(' ')
}

onMounted(() => {
  if (!('IntersectionObserver' in window)) { void activate(); return }
  observer = new IntersectionObserver((entries) => {
    if (entries.some((entry) => entry.isIntersecting)) { void activate(); observer?.disconnect() }
  }, { rootMargin: '250px' })
  if (root.value) observer.observe(root.value)
})
onBeforeUnmount(() => observer?.disconnect())
</script>

<template>
  <article ref="root" :id="`finding-${finding.finding_id}`" :class="['finding-chapter', { compact }]">
    <div class="finding-margin">
      <span class="finding-id">{{ finding.finding_id }}</span>
      <span class="strength">{{ finding.strength }}</span>
    </div>
    <div class="finding-body">
      <p class="eyebrow">{{ finding.headline ? 'HEADLINE FINDING' : 'FORMAL FINDING' }} · {{ finding.period_start }}—{{ finding.period_end }}</p>
      <h3>{{ finding.title_zh }}</h3>
      <p class="title-en" lang="en">{{ finding.title_en }}</p>
      <p class="finding-statement">{{ finding.statement_zh }}</p>
      <p class="statement-en" lang="en">{{ finding.statement_en }}</p>

      <div v-if="state === 'idle' || state === 'loading'" class="finding-loading">证据视觉正在按需加载…</div>
      <div v-else-if="state === 'error'" class="finding-error" role="alert">
        <strong>Finding 证据暂时无法加载</strong>
        <button class="native-control" @click="activate(true)">重试</button>
      </div>
      <div v-else class="finding-visual">
        <template v-if="finding.finding_id === 'F1'">
          <div class="overlap-visual" role="img" aria-label="Lineage M 2025Q2 同季度两个报告口径并列显示，不表示增长">
            <span class="quarter-axis numeric">2025Q2 · 同一季度</span>
            <div class="definition-lane">
              <span>legacy_v1</span><strong class="numeric">{{ formatKrwMillion(value('obs_lm_v1_2025q2')) }}</strong>
            </div>
            <div class="definition-seam" aria-hidden="true"><span>REPORTING DEFINITION SEAM</span></div>
            <div class="definition-lane v2">
              <span>royalty_integrated_v2</span><strong class="numeric">{{ formatKrwMillion(value('obs_lm_v2_2025q2')) }}</strong>
            </div>
            <p>定义差异 ≠ 增长。No cross-version QoQ.</p>
          </div>
        </template>
        <template v-else-if="finding.finding_id === 'F2'">
          <div class="event-finding" role="img" aria-label="Stellar Blade 2025Q1 至 2025Q2 观察值上升 837.3%，PC 上线仅作为同季度背景">
            <div class="trajectory-stage">
              <span class="point low"><i></i><b class="numeric">2025Q1 · {{ formatKrwMillion(value('obs_stellar_2025q1')) }}</b></span>
              <span class="rise-line" aria-hidden="true"></span>
              <span class="point high"><i></i><b class="numeric">2025Q2 · {{ formatKrwMillion(value('obs_stellar_2025q2')) }}</b></span>
              <strong class="change-label numeric"><b>+837.3%</b><small>八季度窗口峰值</small></strong>
            </div>
            <div class="context-rail"><span></span><strong>PC launch · same quarter</strong><small>PC-only amount unavailable · timing does not establish causality</small></div>
          </div>
        </template>
        <template v-else-if="finding.finding_id === 'F4'">
          <svg class="sequence-visual" viewBox="0 0 820 280" role="img" aria-label="Black Desert 从峰值回撤，三季度后恢复到新峰值，再次回撤并在窗口内未恢复">
            <title>Black Desert 完整回撤与恢复序列</title>
            <desc>2024Q4 峰值，2025Q2 回撤 20.7%，2025Q3 恢复至新峰值，2026Q2 再回撤 30.8%。</desc>
            <line x1="60" y1="220" x2="770" y2="220" class="axis" />
            <polyline :points="f4Path()" class="sequence-line" />
            <g v-for="(observation, index) in observations" :key="observation.observation_id">
              <circle :cx="70 + (index / Math.max(observations.length - 1, 1)) * 680" :cy="210 - (((observation.value ?? 0) - Math.min(...observations.map(item => item.value ?? 0))) / Math.max(Math.max(...observations.map(item => item.value ?? 0)) - Math.min(...observations.map(item => item.value ?? 0)), 1)) * 145" r="6" />
              <text :x="70 + (index / Math.max(observations.length - 1, 1)) * 680" y="246" text-anchor="middle">{{ observation.quarter }}</text>
            </g>
            <text x="205" y="40">峰值 → -20.7%</text><text x="405" y="38">三季度后恢复 / 新峰值</text><text x="615" y="65">第二次回撤 -30.8%</text>
          </svg>
          <p class="visual-summary">窗口末仍未恢复；不表示永久下降。</p>
        </template>
        <template v-else-if="finding.finding_id === 'F3'">
          <div class="recovery-visual">
            <strong class="numeric">2026Q2 · +32.4% QoQ</strong><span class="gap">仍比 2025Q2 峰值低 4.1%</span><b>NOT_RECOVERED_WITHIN_OBSERVED_WINDOW</b>
          </div>
        </template>
        <template v-else-if="finding.finding_id === 'F5'">
          <div class="boundary-visual">
            <span class="seam" aria-hidden="true"></span><div><strong>royalty_integrated_v2 only</strong><p class="numeric">2025Q2—2026Q2 · four consecutive decreases · -35.3%</p><small>legacy 轨迹在校准缝另一侧，不参与本 Finding。</small></div>
          </div>
        </template>
        <template v-else-if="finding.finding_id === 'F6'">
          <div class="uncertainty-grid" role="img" :aria-label="`${derivedChanges.length} 个可比较派生变化，${signSensitiveCount} 个方向受取整区间影响，${derivedChanges.length - signSensitiveCount} 个方向稳定`">
            <div v-for="observation in derivedChanges" :key="observation.observation_id" :class="['change-interval', { sensitive: observation.derived?.direction_sign_stable === false }]">
              <span class="zero">0</span><i></i><b>{{ observation.derived?.direction_sign_stable === false ? '方向敏感' : '方向稳定' }}</b>
            </div>
          </div>
          <p class="visual-summary numeric">{{ signSensitiveCount }}/{{ derivedChanges.length }} sign-sensitive · 60.0% · {{ derivedChanges.length - signSensitiveCount }}/{{ derivedChanges.length }} sign-stable</p>
        </template>
      </div>

      <div class="finding-notes">
        <p><strong>限制</strong> {{ finding.limitations }}</p>
        <p><strong>禁止解读</strong> {{ finding.forbidden_interpretation }}</p>
      </div>
      <button class="native-control evidence-button" :aria-expanded="evidenceOpen" @click="evidenceOpen = !evidenceOpen">{{ evidenceOpen ? '收起 Finding 证据' : '查看 Finding 证据' }}</button>
      <SourceList v-if="evidenceOpen" :sources="resolveSources(finding.source_ids, sources)" :title="`${finding.finding_id} 证据来源`" />
    </div>
  </article>
</template>

<style scoped>
.finding-chapter { display: grid; grid-template-columns: 6rem minmax(0, 1fr); gap: clamp(1.5rem, 5vw, 4rem); padding-block: clamp(5rem, 9vw, 8rem); border-top: 1px solid var(--rule-border); }
.finding-margin { border-top: 3px solid var(--accent-primary); padding-top: 0.75rem; }
.finding-id, .strength { display: block; font-family: var(--font-numeric); }
.finding-id { font-size: 2rem; font-weight: 580; letter-spacing: -.05em; }.strength { margin-top: .2rem; color: var(--text-secondary); font-size: 0.7rem; }
.finding-body { max-width: 64rem; }
.finding-body > h3 { max-width: 20ch; font-size: clamp(2rem, 4vw, 2.75rem); line-height: 1.08; letter-spacing: -.045em; }
.title-en { margin: 0.35rem 0 1.5rem; color: var(--text-secondary); }
.finding-statement { max-width: 50rem; margin-top: 2rem; font-size: clamp(1.05rem, 1.8vw, 1.25rem); line-height: 1.85; font-weight: 500; }
.statement-en { max-width: 50rem; color: var(--text-secondary); font-size: 0.875rem; }
.finding-loading, .finding-error { margin-block: 1.5rem; padding: 2rem; border-block: 1px solid var(--rule-border); }
.finding-visual { margin-block: 3rem 2rem; }
.overlap-visual { display: grid; grid-template-columns: 1fr 3rem 1fr; gap: 1.5rem; padding-block: 2rem; border-block: 1px solid var(--rule-border); }
.quarter-axis, .overlap-visual > p { grid-column: 1 / -1; }.quarter-axis { color: var(--text-secondary); letter-spacing: .08em; }.definition-lane { display: grid; gap: 0.75rem; border-top: 3px solid var(--accent-primary); padding-top: 1.25rem; }.definition-lane.v2 { border-top: 3px double var(--text-primary); }.definition-lane span { color: var(--text-secondary); font: .75rem var(--font-numeric); letter-spacing: .04em; }.definition-lane strong { font-size: clamp(1.6rem, 3vw, 2.35rem); letter-spacing: -.04em; }.definition-seam { position: relative; border-inline: 3px double var(--text-primary); }.definition-seam span { position: absolute; bottom: .25rem; left: 50%; width: 12rem; color: var(--text-secondary); font: 9px var(--font-numeric); letter-spacing: .08em; transform: rotate(-90deg) translateY(-50%); transform-origin: left bottom; }
.event-finding { padding-top: .5rem; }.trajectory-stage { position: relative; height: 20rem; border-block: 1px solid var(--rule-border); background: linear-gradient(180deg, transparent 74%, var(--rule-faint) 74% calc(74% + 1px), transparent calc(74% + 1px)); }.point { position: absolute; display: grid; gap: 0.6rem; }.point i { width: .9rem; height: .9rem; border-radius: 50%; background: var(--accent-primary); box-shadow: 0 0 0 5px var(--accent-wash); }.point b { font-size: .78rem; }.point.low { left: 5%; bottom: 2.5rem; }.point.high { right: 5%; top: 2rem; }.rise-line { position: absolute; left: 8%; right: 8%; top: 49%; border-top: 2px solid var(--accent-primary); transform: rotate(-15deg); transform-origin: center; }.change-label { position: absolute; top: 39%; left: 35%; display: grid; color: var(--accent-strong); }.change-label b { font-size: clamp(3rem, 7vw, 5.5rem); line-height: .9; letter-spacing: -.08em; }.change-label small { margin-top: .75rem; color: var(--text-secondary); font: 650 .72rem var(--font-sans); letter-spacing: .04em; }.context-rail { display: grid; grid-template-columns: 1rem auto 1fr; gap: 0.75rem; align-items: center; padding-top: 1rem; border-top: 2px solid var(--event); }.context-rail span { height: 1.5rem; border-left: 3px solid var(--event); }.context-rail small { color: var(--text-secondary); }
.sequence-visual { display: block; width: 100%; min-height: 21rem; border-block: 1px solid var(--rule-border); }.sequence-visual .axis { stroke: var(--rule-border); }.sequence-line { fill: none; stroke: var(--accent-primary); stroke-width: 2.5; }.sequence-visual circle { fill: var(--accent-primary); stroke: var(--surface-primary); stroke-width: 2; }.sequence-visual text { fill: var(--text-primary); font: 13px var(--font-sans); }.visual-summary { color: var(--text-secondary); }
.recovery-visual { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; padding: 1.5rem; border-top: 2px solid var(--accent-primary); }.recovery-visual strong { font-size: 1.35rem; }.recovery-visual b { grid-column: 1 / -1; padding-top: 0.75rem; border-top: 1px solid var(--rule-border); font-family: var(--font-numeric); }
.boundary-visual { display: grid; grid-template-columns: 1rem 1fr; gap: 1rem; padding: 1.5rem; border-block: 1px solid var(--rule-border); }.boundary-visual .seam { border-inline: 2px solid var(--text-primary); }.boundary-visual p { margin: 0.35rem 0; }
.uncertainty-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 0.75rem; }.change-interval { position: relative; min-height: 5rem; border: 1px solid var(--rule-border); background: var(--surface-primary); }.change-interval .zero { position: absolute; left: 50%; top: 0.3rem; color: var(--text-secondary); font: 11px var(--font-numeric); }.change-interval i { position: absolute; left: 55%; right: 10%; top: 2.1rem; border-top: 3px solid var(--accent-primary); }.change-interval i::before, .change-interval i::after { content: ''; position: absolute; top: -0.35rem; height: 0.7rem; border-left: 2px solid currentColor; }.change-interval i::before { left: 0; }.change-interval i::after { right: 0; }.change-interval.sensitive { background-image: repeating-linear-gradient(135deg, transparent 0 6px, rgba(89,97,94,.12) 6px 8px); }.change-interval.sensitive i { left: 18%; right: 18%; border-color: var(--uncertainty); }.change-interval b { position: absolute; inset: auto 0 0.35rem; text-align: center; font-size: 0.7rem; }
.finding-notes { margin-block: 2rem; padding-left: 1.25rem; border-left: 2px solid var(--warning); }.finding-notes::before { content: 'METHOD NOTE'; display: block; margin-bottom: .4rem; color: var(--warning); font: 650 .68rem var(--font-numeric); letter-spacing: .1em; }.finding-notes p { margin: 0.35rem 0; }.evidence-button { margin-bottom: 0.75rem; }
.compact { padding-block: 3rem; }.compact .finding-statement { font-size: 1rem; }
@media (max-width: 767px) {
  .finding-chapter { grid-template-columns: 1fr; padding-block: 4.5rem; }.finding-margin { display: flex; justify-content: space-between; max-width: 7rem; }.finding-body > h3 { font-size: clamp(2rem, 9vw, 2.65rem); }.overlap-visual { grid-template-columns: 1fr; }.definition-seam { height: 1.25rem; border-inline: 0; border-block: 3px double var(--text-primary); }.definition-seam span { display: none; }.event-finding .change-label { left: 20%; }.change-label b { font-size: clamp(3rem, 17vw, 4.5rem); }.context-rail { grid-template-columns: .75rem 1fr; }.context-rail small { grid-column: 2; }.uncertainty-grid { grid-template-columns: repeat(3, 1fr); }.recovery-visual { grid-template-columns: 1fr; }.recovery-visual b { grid-column: 1; }
}
@media (max-width: 390px) { .trajectory-stage { height: 17rem; }.point.low { left: 0; }.point.high { right: 0; }.point b { max-width: 8rem; }.event-finding .change-label { left: 11%; top: 41%; }.sequence-visual { min-width: 39rem; }.finding-visual:has(.sequence-visual) { overflow-x: auto; }.uncertainty-grid { grid-template-columns: repeat(2, 1fr); } }
</style>
