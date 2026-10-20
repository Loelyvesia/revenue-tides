<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { loadSeriesDetail } from '../../data/client'
import type { EventRecord, Observation, SeriesDetail, SeriesIndexRecord } from '../../types/webData'
import { useScrolly } from '../../composables/useScrolly'
import { displayCopy } from '../../content/displayCopy.zh'

const props = defineProps<{ series: SeriesIndexRecord[] }>()

const container = ref<HTMLElement | null>(null)
const { activeIndex } = useScrolly({ container, stepCount: 4 })

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
  step3A.value = pick(lmD, '2025Q2', 'legacy')
  step3B.value = pick(lmD, '2025Q2', 'royalty')
  step4Obs.value = jwD?.observations.find((o) => o.quarter === '2024Q3' && o.derived) ?? null
  step5Events.value = sbD?.events.filter((e) => e.fiscal_period === '2025Q2') ?? []
})

function fmt(v: number | null): string {
  if (v === null) return '—'
  return Math.abs(v) >= 1000 ? `${(v / 1000).toFixed(1)}B` : `${Math.round(v).toLocaleString()}M`
}

const scopeFrom = computed(() => (lm.value?.identity.entity_type === 'GAME_TITLE' ? '单款游戏' : '—'))
</script>

<template>
  <section id="measurement" class="chapter chapter--paper measurement-signature" aria-labelledby="measurement-title">
    <div class="shell">
      <header class="chapter-head">
        <span class="eyebrow">读数字之前</span>
        <h2 id="measurement-title" class="display-chapter">{{ displayCopy.measurement.title }}</h2>
        <p class="lede">{{ displayCopy.measurement.lede }}</p>
      </header>
    </div>
    <div ref="container" class="shell scrolly">
      <div class="scrolly__steps" aria-label="测量问题叙述">
        <div v-for="(step, index) in displayCopy.measurement.steps" :key="step.label" class="scrolly__step" :class="{ 'is-active': activeIndex === index }" :data-scrolly-step="index" tabindex="0">
          <div class="step-rule" />
          <p class="step-label">{{ step.label }}</p>
          <h3>{{ step.title }}</h3>
          <p>{{ step.body }}</p>
        </div>
      </div>
      <div class="scrolly__visual" aria-live="polite">
        <div class="measurement-instrument" :class="`measurement-instrument--${activeIndex + 2}`">
          <p class="measurement-instrument__label">财报数字的四种读法</p>
          <svg class="measurement-tide" viewBox="0 0 760 380" preserveAspectRatio="none" aria-hidden="true">
            <defs>
              <linearGradient id="measurement-solid" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#0b5662" stop-opacity=".45"/><stop offset=".55" stop-color="#24a8a0" stop-opacity=".85"/><stop offset="1" stop-color="#7de2cc" stop-opacity=".25"/></linearGradient>
              <linearGradient id="measurement-alt" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#ee805f" stop-opacity=".2"/><stop offset=".52" stop-color="#ee8d64" stop-opacity=".8"/><stop offset="1" stop-color="#ffc0a2" stop-opacity=".2"/></linearGradient>
              <pattern id="measurement-uncertainty" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><line x1="0" y1="0" x2="0" y2="9" stroke="#8f75c9" stroke-width="2" opacity=".42"/></pattern>
              <filter id="measurement-glow" x="-20%" y="-80%" width="140%" height="260%"><feGaussianBlur stdDeviation="8"/></filter>
            </defs>
            <g class="measurement-state measurement-state--direct"><path d="M42 228 C170 214 250 146 360 168 C468 190 536 112 716 154 L716 194 C536 152 468 230 360 208 C250 186 170 254 42 268 Z" fill="url(#measurement-solid)"/><path d="M42 248 C170 234 250 166 360 188 C468 210 536 132 716 174"/></g>
            <g class="measurement-state measurement-state--scope"><path d="M42 220 C170 200 250 130 360 158 C468 186 560 94 716 144 L716 206 C560 156 468 248 360 220 C250 192 170 262 42 282 Z" fill="url(#measurement-solid)"/><path d="M42 251 C170 231 250 161 360 189 C468 217 560 125 716 175"/></g>
            <g class="measurement-state measurement-state--version"><path d="M42 232 C170 206 250 153 362 179 L362 213 C250 187 170 240 42 266 Z" fill="url(#measurement-solid)"/><path d="M362 179 C470 205 572 118 716 150 L716 182 C572 150 470 237 362 213 Z" fill="url(#measurement-solid)"/><path d="M362 217 C470 243 572 160 716 192 L716 220 C572 188 470 271 362 245 Z" fill="url(#measurement-alt)"/><rect x="340" y="104" width="44" height="170" rx="22" class="measurement-seam"/></g>
            <g class="measurement-state measurement-state--derived"><path d="M42 280 C166 260 248 104 360 140 C482 180 574 90 716 132 L716 230 C574 188 482 278 360 238 C248 202 166 328 42 348 Z" fill="url(#measurement-uncertainty)"/><path d="M42 314 C166 294 248 148 360 184 C482 224 574 134 716 176" class="measurement-derived-ridge"/></g>
            <g class="measurement-state measurement-state--event"><path d="M42 236 C170 224 250 154 360 177 C468 199 536 120 716 160 L716 198 C536 158 468 237 360 215 C250 192 170 262 42 274 Z" fill="url(#measurement-solid)"/><path d="M42 255 C170 243 250 173 360 196 C468 218 536 139 716 179"/><circle cx="525" cy="286" r="26" class="measurement-event-halo"/><circle cx="525" cy="286" r="7" class="measurement-event-pulse"/></g>
          </svg>
          <Transition name="fade-switch" mode="out-in">
          <div v-if="activeIndex === 0" key="s1" class="reading">
            <p class="reading__q">统计范围</p>
            <div class="scope-box">
              <div class="scope-box__title">单款游戏</div>
              <div class="scope-box__desc">例如 Lineage M</div>
            </div>
            <div class="scope-arrow" aria-hidden="true">↓</div>
            <div class="scope-box scope-box--wide">
              <div class="scope-box__title">整个 IP</div>
              <div class="scope-box__desc">例如 Black Desert 的跨平台收入</div>
            </div>
            <p class="reading__meta">统计对象不同，数字不能直接放在一起比较。</p>
          </div>
          <div v-else-if="activeIndex === 1" key="s2" class="reading reading--split">
            <p class="reading__q">2025 Q2，同一季度</p>
            <div class="split-row">
              <div class="split-col">
                <p class="split-col__label">旧口径</p>
                <p class="split-col__v display-figure">{{ step3A ? fmt(step3A.value) : '…' }}</p>
                <p class="split-col__meta">legacy v1</p>
              </div>
              <div class="split-col">
                <p class="split-col__label">纳入 royalties</p>
                <p class="split-col__v display-figure">{{ step3B ? fmt(step3B.value) : '…' }}</p>
                <p class="split-col__meta">royalty-integrated v2</p>
              </div>
            </div>
            <p class="reading__meta">两个数字属于不同定义，不能前后拼接。</p>
          </div>
          <div v-else-if="activeIndex === 2" key="s3" class="reading">
            <p class="reading__q">2024 Q3，推导值</p>
            <p class="reading__v display-figure">{{ step4Obs ? fmt(step4Obs.value) : '…' }}</p>
            <div class="interval-row" aria-hidden="true">
              <span class="interval-row__lo numeric">{{ step4Obs ? fmt(step4Obs.lower_bound) : '…' }}</span>
              <span class="interval-row__bar"><i /><i /><i /></span>
              <span class="interval-row__hi numeric">{{ step4Obs ? fmt(step4Obs.upper_bound) : '…' }}</span>
            </div>
            <p class="reading__meta">根据官方占比推算；横线两端是取整后仍可能成立的范围。</p>
          </div>
          <div v-else key="s4" class="reading">
            <p class="reading__q">Stellar Blade，2025 Q2</p>
            <p class="reading__v display-figure">{{ fmt(65718.814) }}</p>
            <ul class="reading__events">
              <li v-for="event in step5Events" :key="event.event_id">
                <span class="dot" />{{ event.name }}
              </li>
            </ul>
            <p class="reading__meta">PC 版在同季度上线；财报没有拆出 PC 端收入。</p>
          </div>
          </Transition>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.measurement-signature{padding-block:clamp(4rem,7vw,6.2rem)}
.measurement-signature :deep(.chapter-head){margin-bottom:clamp(1.4rem,3vw,2.4rem)}
.measurement-signature :deep(.scrolly){gap:clamp(2rem,4vw,4rem)}
.measurement-signature :deep(.scrolly__steps){padding-block:5vh 14vh}
.measurement-signature :deep(.scrolly__step){min-height:54vh;padding-block:9vh;opacity:.28}
.measurement-signature :deep(.scrolly__step.is-active){opacity:1}
@media(min-width:641px){.measurement-signature :deep(.scrolly__steps){padding-top:0}.measurement-signature :deep(.scrolly__step){padding-top:4vh}.measurement-signature :deep(.scrolly__visual){align-items:flex-start;padding-top:2vh}.measurement-signature :deep(.chapter-head){margin-bottom:1.2rem}}
.measurement-instrument{position:relative;width:114%;height:min(47svh,31rem);margin-left:-7%;display:flex;align-items:flex-end;padding:clamp(1rem,2.3vw,1.9rem) 7%;overflow:visible;background:radial-gradient(ellipse at 61% 42%,rgba(68,190,169,.14),transparent 43%)}
.measurement-instrument::after{content:'';position:absolute;inset:10% -2% 7%;pointer-events:none;background:radial-gradient(ellipse,rgba(125,226,204,.07),transparent 65%);filter:blur(18px)}
.measurement-instrument__label{position:absolute;z-index:3;top:1.1rem;left:1.25rem;font:600 .54rem var(--font-numeric);letter-spacing:.13em;color:var(--ink-3)}
.measurement-tide{position:absolute;inset:-.8rem -5% 0;width:110%;height:94%;overflow:visible}.measurement-state{opacity:0;transition:opacity .55s ease,transform .7s var(--ease-out);transform:translateY(10px) scaleY(.94);transform-origin:center}.measurement-state path:not([fill]){fill:none;stroke:#f4fffb;stroke-width:1.35;opacity:.8}.measurement-instrument--1 .measurement-state--direct,.measurement-instrument--2 .measurement-state--scope,.measurement-instrument--3 .measurement-state--version,.measurement-instrument--4 .measurement-state--derived,.measurement-instrument--5 .measurement-state--event{opacity:1;transform:none}.measurement-seam{fill:rgba(238,128,95,.14);stroke:none;filter:blur(4px)}.measurement-derived-ridge{stroke:var(--uncertainty-violet)!important;stroke-width:2!important;filter:none!important}.measurement-event-halo{fill:rgba(238,128,95,.15)}.measurement-event-pulse{fill:var(--context-coral);filter:drop-shadow(0 0 8px rgba(238,128,95,.55));animation:measurement-pulse 1.8s ease-in-out 1}
.reading{position:relative;z-index:4;width:min(100%,38rem);padding:1.2rem 1.4rem 1.2rem 0;background:linear-gradient(90deg,rgba(247,244,236,.9),rgba(247,244,236,.52) 72%,transparent);box-shadow:none}
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

.scope-box {padding:.65rem 1.1rem;width:fit-content;border-radius:999px;background:rgba(125,226,204,.14)}
.scope-box--wide {padding-inline:1.7rem;background:rgba(36,168,160,.18)}
.scope-box__title { font-family: var(--font-numeric); font-weight: 650; font-size: 0.95rem; letter-spacing: 0.1em; }
.scope-box__desc { font-size: 0.8rem; color: var(--ink-3); margin-top: 0.2rem; }
.scope-arrow { font-size: 1.4rem; color: var(--ink-3); margin: 0.4rem 0 0.4rem 1.4rem; }

.split-row { display: flex; gap: 2.4rem; align-items: flex-start; }
.split-col { padding:.7rem 1rem;min-width:11rem;border-radius:50%;background:radial-gradient(ellipse,rgba(125,226,204,.2),transparent 72%) }.split-col+ .split-col{background:radial-gradient(ellipse,rgba(238,128,95,.18),transparent 72%)}
.split-col__label { font-family: var(--font-numeric); font-size: 0.7rem; letter-spacing: 0.1em; color: var(--ink-3); }
.split-col__v { font-size: clamp(2rem, 4vw, 3.2rem); color: var(--ink); margin: 0.3rem 0; }
.split-col--alt .split-col__v { color: var(--copper); }

.interval-row { display: flex; align-items: center; gap: 1rem; margin: 1.1rem 0; }
.interval-row__bar { display: flex; align-items: center; gap: 0.35rem; }
.interval-row__bar i { display: block; width: 26px; height: 4px; background: var(--uncertainty-lavender); }
.interval-row__lo, .interval-row__hi { font-size: 0.95rem; color: var(--ink-2); }

@media (max-width: 640px) {
  .measurement-signature{padding-block:3.4rem}.measurement-signature :deep(.scrolly__steps){padding-block:2vh 8vh}.measurement-signature :deep(.scrolly__step){min-height:42vh;padding-block:6vh}
  .measurement-instrument{width:110%;height:34svh;min-height:18rem;margin-left:-5%;padding:.8rem 4%}.measurement-instrument__label{font-size:.42rem}.measurement-tide{height:82%;top:.4rem}.reading{padding:.8rem 0;background:linear-gradient(90deg,rgba(248,245,238,.72),transparent)}.reading__v{font-size:clamp(3rem,15vw,4.5rem)}
  .split-row { flex-direction: column; gap: 1.2rem; }
}
@keyframes measurement-pulse{50%{r:12px;opacity:.38}}
@media(prefers-reduced-motion:reduce){.measurement-state{transition:none}.measurement-event-pulse{animation:none}}
</style>
