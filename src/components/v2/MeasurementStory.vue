<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { loadSeriesDetail } from '../../data/client'
import type { EventRecord, Observation, SeriesDetail, SeriesIndexRecord } from '../../types/webData'
import { useScrolly } from '../../composables/useScrolly'

const props = defineProps<{ series: SeriesIndexRecord[] }>()

const container = ref<HTMLElement | null>(null)
const { activeIndex } = useScrolly({ container, stepCount: 5 })

const lm = ref<SeriesDetail | null>(null)
const jw = ref<SeriesDetail | null>(null)
const sb = ref<SeriesDetail | null>(null)

function byId(list: SeriesIndexRecord[], id: string): SeriesIndexRecord | undefined {
  return list.find((s) => s.series_id === id)
}

function pick(detail: SeriesDetail | null, quarter: string, versionPart: string): Observation | null {
  if (!detail) return null
  return detail.observations.find((o) => o.quarter === quarter && o.metric_version.includes(versionPart)) ?? null
}

const step1Obs = ref<Observation | null>(null)
const step3A = ref<Observation | null>(null)
const step3B = ref<Observation | null>(null)
const step4Obs = ref<Observation | null>(null)
const step5Events = ref<EventRecord[]>([])

onMounted(async () => {
  const lmRec = byId(props.series, 'series_lineage_m')
  const jwRec = byId(props.series, 'series_jackpot_world')
  const sbRec = byId(props.series, 'series_stellar_blade')
  const [lmD, jwD, sbD] = await Promise.all([
    lmRec ? loadSeriesDetail(lmRec) : null,
    jwRec ? loadSeriesDetail(jwRec) : null,
    sbRec ? loadSeriesDetail(sbRec) : null,
  ])
  lm.value = lmD
  jw.value = jwD
  sb.value = sbD
  step1Obs.value = pick(lmD, '2025Q2', 'legacy')
  step3A.value = pick(lmD, '2025Q2', 'legacy')
  step3B.value = pick(lmD, '2025Q2', 'royalty')
  step4Obs.value = jwD?.observations.find((o) => o.quarter === '2024Q3' && o.derived) ?? null
  step5Events.value = sbD?.events.filter((e) => e.fiscal_period === '2025Q2') ?? []
})

function fmt(v: number | null): string {
  if (v === null) return '—'
  return Math.abs(v) >= 1000 ? `${(v / 1000).toFixed(1)}B` : `${Math.round(v).toLocaleString()}M`
}

const scopeFrom = computed(() => (lm.value?.identity.entity_type === 'GAME_TITLE' ? 'GAME_TITLE' : '—'))
</script>

<template>
  <section id="measurement" class="chapter chapter--paper" aria-labelledby="measurement-title">
    <div class="shell">
      <header class="chapter-head">
        <span class="eyebrow">ACT I — THE NUMBER</span>
        <h2 id="measurement-title" class="display-chapter">为什么“游戏收入”不是统一指标</h2>
        <p class="lede">同一季度可以有多个合法数字。差异来自测量口径。</p>
      </header>
    </div>
    <div ref="container" class="shell scrolly">
      <div class="scrolly__steps" aria-label="测量问题叙述">
        <div v-for="i in 5" :key="i" class="scrolly__step" :class="{ 'is-active': activeIndex === i - 1 }" :data-scrolly-step="i - 1" tabindex="0">
          <div class="step-rule" />
          <template v-if="i === 1">
            <p class="step-label">STEP 01 · 单一数值</p>
            <h3>一个游戏，不止一个收入数字</h3>
            <p>先确认季度、数值与实体。</p>
          </template>
          <template v-else-if="i === 2">
            <p class="step-label">STEP 02 · 实体范围</p>
            <h3>实体范围可能不同</h3>
            <p>GAME_TITLE 与 IP 的边界不同。</p>
          </template>
          <template v-else-if="i === 3">
            <p class="step-label">STEP 03 · 口径分裂</p>
            <h3>同一季度，两个合法口径</h3>
            <p>旧定义与新定义可以重叠。</p>
          </template>
          <template v-else-if="i === 4">
            <p class="step-label">STEP 04 · 推导区间</p>
            <h3>推导值必须带着区间</h3>
            <p>官方占比的取整会展开成范围。</p>
          </template>
          <template v-else>
            <p class="step-label">STEP 05 · 事件语境</p>
            <h3>同期事件不是因果证明</h3>
            <p>事件只提供时间语境。</p>
          </template>
        </div>
      </div>
      <div class="scrolly__visual" aria-live="polite">
        <Transition name="fade-switch" mode="out-in">
          <div v-if="activeIndex === 0" key="s1" class="reading">
            <p class="reading__q">2025 Q2</p>
            <p class="reading__v display-figure">{{ step1Obs ? fmt(step1Obs.value) : '…' }}</p>
            <p class="reading__meta">LINEAGE M · GAME_TITLE · OFFICIAL REPORTED · V1</p>
          </div>
          <div v-else-if="activeIndex === 1" key="s2" class="reading">
            <p class="reading__q">实体边界</p>
            <div class="scope-box">
              <div class="scope-box__title">GAME_TITLE</div>
              <div class="scope-box__desc">单款游戏标题</div>
            </div>
            <div class="scope-arrow" aria-hidden="true">↓</div>
            <div class="scope-box scope-box--wide">
              <div class="scope-box__title">IP</div>
              <div class="scope-box__desc">跨平台合并的 IP 收入</div>
            </div>
            <p class="reading__meta">范围括号变化 → 数值语义变化</p>
          </div>
          <div v-else-if="activeIndex === 2" key="s3" class="reading reading--split">
            <p class="reading__q">2025 Q2 · 同一季度</p>
            <div class="split-row">
              <div class="split-col">
                <p class="split-col__label">LEGACY</p>
                <p class="split-col__v display-figure">{{ step3A ? fmt(step3A.value) : '…' }}</p>
                <p class="split-col__meta">V1 · 旧口径</p>
              </div>
              <div class="split-col">
                <p class="split-col__label">ROYALTY-INTEGRATED</p>
                <p class="split-col__v display-figure">{{ step3B ? fmt(step3B.value) : '…' }}</p>
                <p class="split-col__meta">V2 · 新口径</p>
              </div>
            </div>
            <p class="reading__meta">两个合法数字 · 定义差异 ≠ 增长</p>
          </div>
          <div v-else-if="activeIndex === 3" key="s4" class="reading">
            <p class="reading__q">2024 Q3 · DERIVED</p>
            <p class="reading__v display-figure">{{ step4Obs ? fmt(step4Obs.value) : '…' }}</p>
            <div class="interval-row" aria-hidden="true">
              <span class="interval-row__lo numeric">{{ step4Obs ? fmt(step4Obs.lower_bound) : '…' }}</span>
              <span class="interval-row__bar"><i /><i /><i /></span>
              <span class="interval-row__hi numeric">{{ step4Obs ? fmt(step4Obs.upper_bound) : '…' }}</span>
            </div>
            <p class="reading__meta">由官方占比推导 · 兼容取整区间</p>
          </div>
          <div v-else key="s5" class="reading">
            <p class="reading__q">2025 Q2 · STELLAR BLADE</p>
            <p class="reading__v display-figure">{{ fmt(65718.814) }}</p>
            <ul class="reading__events">
              <li v-for="event in step5Events" :key="event.event_id">
                <span class="dot" />{{ event.name }} · {{ event.event_type.replace(/_/g, ' ') }}
              </li>
            </ul>
            <p class="reading__meta">事件 = 语境 · 同期 ≠ 因果</p>
          </div>
        </Transition>
      </div>
    </div>
  </section>
</template>

<style scoped>
.reading { width: min(100%, 36rem); }
.reading__q {
  font-family: var(--font-numeric);
  font-size: 0.78rem;
  letter-spacing: 0.14em;
  color: var(--ink-3);
  margin-bottom: 0.9rem;
}
.reading__v { font-size: clamp(3rem, 6vw, 5rem); color: var(--teal); line-height: 1; margin-bottom: 0.9rem; }
.reading__meta {
  font-family: var(--font-numeric);
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  color: var(--ink-3);
}
.reading__events { list-style: none; padding: 0; margin: 0.8rem 0 0.9rem; }
.reading__events li { font-size: 0.9rem; color: var(--ink-2); margin-bottom: 0.4rem; }
.reading__events .dot { display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: var(--copper); margin-right: 0.6rem; }

.scope-box {
  border: 2px solid var(--ink-2);
  padding: 0.8rem 1.1rem;
  width: fit-content;
}
.scope-box--wide { border-style: dashed; }
.scope-box__title { font-family: var(--font-numeric); font-weight: 650; font-size: 0.95rem; letter-spacing: 0.1em; }
.scope-box__desc { font-size: 0.8rem; color: var(--ink-3); margin-top: 0.2rem; }
.scope-arrow { font-size: 1.4rem; color: var(--ink-3); margin: 0.4rem 0 0.4rem 1.4rem; }

.split-row { display: flex; gap: 2.4rem; align-items: flex-start; }
.split-col { border-top: 2px solid var(--ink); padding-top: 0.7rem; min-width: 11rem; }
.split-col__label { font-family: var(--font-numeric); font-size: 0.7rem; letter-spacing: 0.1em; color: var(--ink-3); }
.split-col__v { font-size: clamp(2rem, 4vw, 3.2rem); color: var(--ink); margin: 0.3rem 0; }
.split-col--alt .split-col__v { color: var(--copper); }

.interval-row { display: flex; align-items: center; gap: 1rem; margin: 1.1rem 0; }
.interval-row__bar { display: flex; align-items: center; gap: 0.35rem; }
.interval-row__bar i { display: block; width: 26px; height: 2px; background: var(--copper); }
.interval-row__lo, .interval-row__hi { font-size: 0.95rem; color: var(--ink-2); }

@media (max-width: 640px) {
  .split-row { flex-direction: column; gap: 1.2rem; }
}
</style>
