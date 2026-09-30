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
        <div class="measurement-instrument" :class="`measurement-instrument--${activeIndex + 1}`">
          <p class="measurement-instrument__label">MEASUREMENT STATE / SCHEMATIC TIDAL GEOMETRY</p>
          <svg class="measurement-tide" viewBox="0 0 760 380" preserveAspectRatio="none" aria-hidden="true">
            <defs>
              <linearGradient id="measurement-solid" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#0b5662" stop-opacity=".45"/><stop offset=".55" stop-color="#24a8a0" stop-opacity=".85"/><stop offset="1" stop-color="#7de2cc" stop-opacity=".25"/></linearGradient>
              <linearGradient id="measurement-alt" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#ee805f" stop-opacity=".2"/><stop offset=".52" stop-color="#ee8d64" stop-opacity=".8"/><stop offset="1" stop-color="#ffc0a2" stop-opacity=".2"/></linearGradient>
              <pattern id="measurement-uncertainty" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><line x1="0" y1="0" x2="0" y2="9" stroke="#8f75c9" stroke-width="2" opacity=".42"/></pattern>
              <filter id="measurement-glow" x="-20%" y="-80%" width="140%" height="260%"><feGaussianBlur stdDeviation="8"/></filter>
            </defs>
            <line x1="34" y1="245" x2="726" y2="245" class="measurement-axis"/>
            <g class="measurement-state measurement-state--direct"><path d="M42 228 C170 214 250 146 360 168 C468 190 536 112 716 154 L716 194 C536 152 468 230 360 208 C250 186 170 254 42 268 Z" fill="url(#measurement-solid)"/><path d="M42 248 C170 234 250 166 360 188 C468 210 536 132 716 174"/></g>
            <g class="measurement-state measurement-state--scope"><path d="M42 220 C170 200 250 130 360 158 C468 186 560 94 716 144 L716 206 C560 156 468 248 360 220 C250 192 170 262 42 282 Z" fill="url(#measurement-solid)"/><path d="M42 251 C170 231 250 161 360 189 C468 217 560 125 716 175"/></g>
            <g class="measurement-state measurement-state--version"><path d="M42 232 C170 206 250 153 362 179 L362 213 C250 187 170 240 42 266 Z" fill="url(#measurement-solid)"/><path d="M362 179 C470 205 572 118 716 150 L716 182 C572 150 470 237 362 213 Z" fill="url(#measurement-solid)"/><path d="M362 217 C470 243 572 160 716 192 L716 220 C572 188 470 271 362 245 Z" fill="url(#measurement-alt)"/><line x1="362" y1="88" x2="362" y2="296" class="measurement-seam"/></g>
            <g class="measurement-state measurement-state--derived"><path d="M42 280 C166 260 248 104 360 140 C482 180 574 90 716 132 L716 230 C574 188 482 278 360 238 C248 202 166 328 42 348 Z" fill="url(#measurement-uncertainty)"/><path d="M42 314 C166 294 248 148 360 184 C482 224 574 134 716 176" class="measurement-derived-ridge"/></g>
            <g class="measurement-state measurement-state--event"><path d="M42 236 C170 224 250 154 360 177 C468 199 536 120 716 160 L716 198 C536 158 468 237 360 215 C250 192 170 262 42 274 Z" fill="url(#measurement-solid)"/><path d="M42 255 C170 243 250 173 360 196 C468 218 536 139 716 179"/><line x1="525" y1="258" x2="525" y2="294" class="measurement-event-tick"/><circle cx="525" cy="294" r="8" class="measurement-event-pulse"/></g>
          </svg>
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
    </div>
  </section>
</template>

<style scoped>
.measurement-instrument{position:relative;width:100%;height:min(66svh,42rem);display:flex;align-items:flex-end;padding:clamp(1.2rem,3vw,2.5rem);overflow:hidden;border-radius:0 8rem 0 0;background:radial-gradient(circle at 72% 32%,rgba(125,226,204,.38),transparent 28%),linear-gradient(145deg,rgba(255,255,255,.62),rgba(216,235,228,.74));box-shadow:0 34px 80px rgba(16,74,75,.12)}
.measurement-instrument::after{content:'';position:absolute;inset:0;pointer-events:none;background:linear-gradient(180deg,transparent 55%,rgba(248,245,238,.92) 86%)}
.measurement-instrument__label{position:absolute;z-index:3;top:1.1rem;left:1.25rem;font:600 .54rem var(--font-numeric);letter-spacing:.13em;color:var(--ink-3)}
.measurement-tide{position:absolute;inset:1.8rem 0 0;width:100%;height:72%;overflow:visible}.measurement-axis{stroke:rgba(11,86,98,.28);stroke-width:1}.measurement-state{opacity:0;transition:opacity .5s ease,transform .65s var(--ease-out);transform:translateY(10px)}.measurement-state path:not([fill]){fill:none;stroke:var(--aqua-luminous);stroke-width:2.2;filter:url(#measurement-glow)}.measurement-instrument--1 .measurement-state--direct,.measurement-instrument--2 .measurement-state--scope,.measurement-instrument--3 .measurement-state--version,.measurement-instrument--4 .measurement-state--derived,.measurement-instrument--5 .measurement-state--event{opacity:1;transform:none}.measurement-seam{stroke:var(--context-coral);stroke-width:3;stroke-dasharray:4 7}.measurement-derived-ridge{stroke:var(--uncertainty-violet)!important;stroke-width:4!important;filter:none!important}.measurement-event-tick{stroke:var(--context-coral);stroke-width:3}.measurement-event-pulse{fill:var(--context-coral);filter:drop-shadow(0 0 10px rgba(238,128,95,.75));animation:measurement-pulse 1.8s ease-in-out infinite}
.reading{position:relative;z-index:4;width:min(100%,38rem);padding:1.2rem 1.4rem;background:rgba(248,245,238,.78);backdrop-filter:blur(14px);border-left:3px solid var(--aqua);box-shadow:0 18px 48px rgba(20,70,70,.08)}
.reading__q {
  font-family: var(--font-numeric);
  font-size: 0.78rem;
  letter-spacing: 0.14em;
  color: var(--ink-3);
  margin-bottom: 0.9rem;
}
.reading__v { font-size: clamp(4rem, 8vw, 7.5rem); color: var(--petrol); line-height: .86; margin-bottom: 0.9rem; text-shadow:0 0 24px rgba(125,226,204,.25) }
.reading__meta {
  font-family: var(--font-numeric);
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  color: var(--ink-3);
}
.reading__events { list-style: none; padding: 0; margin: 0.8rem 0 0.9rem; }
.reading__events li { font-size: 0.9rem; color: var(--ink-2); margin-bottom: 0.4rem; }
.reading__events .dot { display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: var(--copper); margin-right: 0.6rem; }

.scope-box {border-left:4px solid var(--aqua);padding:.65rem 1.1rem;width:fit-content;background:rgba(125,226,204,.14)}
.scope-box--wide {border-left-width:10px;background:rgba(36,168,160,.18)}
.scope-box__title { font-family: var(--font-numeric); font-weight: 650; font-size: 0.95rem; letter-spacing: 0.1em; }
.scope-box__desc { font-size: 0.8rem; color: var(--ink-3); margin-top: 0.2rem; }
.scope-arrow { font-size: 1.4rem; color: var(--ink-3); margin: 0.4rem 0 0.4rem 1.4rem; }

.split-row { display: flex; gap: 2.4rem; align-items: flex-start; }
.split-col { border-top: 4px solid var(--aqua); padding-top: 0.7rem; min-width: 11rem; }.split-col+ .split-col{border-top-color:var(--context-coral)}
.split-col__label { font-family: var(--font-numeric); font-size: 0.7rem; letter-spacing: 0.1em; color: var(--ink-3); }
.split-col__v { font-size: clamp(2rem, 4vw, 3.2rem); color: var(--ink); margin: 0.3rem 0; }
.split-col--alt .split-col__v { color: var(--copper); }

.interval-row { display: flex; align-items: center; gap: 1rem; margin: 1.1rem 0; }
.interval-row__bar { display: flex; align-items: center; gap: 0.35rem; }
.interval-row__bar i { display: block; width: 26px; height: 4px; background: var(--uncertainty-lavender); }
.interval-row__lo, .interval-row__hi { font-size: 0.95rem; color: var(--ink-2); }

@media (max-width: 640px) {
  .measurement-instrument{height:36svh;min-height:19rem;padding:.8rem;border-radius:0 3rem 0 0}.measurement-instrument__label{font-size:.42rem}.measurement-tide{height:68%;top:2rem}.reading{padding:.8rem;background:rgba(248,245,238,.84)}.reading__v{font-size:clamp(3rem,15vw,4.5rem)}
  .split-row { flex-direction: column; gap: 1.2rem; }
}
@keyframes measurement-pulse{50%{r:12px;opacity:.38}}
@media(prefers-reduced-motion:reduce){.measurement-state{transition:none}.measurement-event-pulse{animation:none}}
</style>
