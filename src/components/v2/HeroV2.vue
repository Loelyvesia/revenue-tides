<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { loadSeriesDetail } from '../../data/client'
import type { Observation, SeriesDetail, SeriesIndexRecord } from '../../types/webData'
import { prefersReducedMotion } from '../../composables/useScrolly'
import { ribbonPath, smoothPath } from '../../utils/tidalGeometry'
import TidalBand from './TidalBand.vue'

const props = defineProps<{ series: SeriesIndexRecord[] }>()
const details = ref<SeriesDetail[]>([])
const leaving = ref(false)
const root = ref<HTMLElement | null>(null)
const field = ref<HTMLElement | null>(null)
let scrollRaf = 0
let loadTimer = 0

const rows = computed(() => props.series.map((record) => ({ record, detail: details.value.find((item) => item.series_id === record.series_id) ?? null })))
const fieldBands = computed(() => rows.value.flatMap(({ record, detail }, seriesIndex) => {
  if (!detail) return []
  const candidates = detail.metric_versions.map((metric) => detail.observations
    .filter((item): item is Observation & { value: number } => item.metric_definition_id === metric.metric_definition_id && item.value !== null)
    .sort((a, b) => a.period_index - b.period_index))
  const observations = candidates.sort((a, b) => b.length - a.length)[0] ?? []
  if (!observations.length) return []
  const indices = observations.map((item) => item.period_index)
  const minIndex = Math.min(...indices); const maxIndex = Math.max(...indices)
  const values = observations.map((item) => item.baseline_index ?? item.value)
  const low = Math.min(...values); const high = Math.max(...values)
  const center = 380 + (seriesIndex - 4) * 47
  const points = observations.map((item) => {
    const value = item.baseline_index ?? item.value
    const ratio = high === low ? .5 : (value - low) / (high - low)
    return { x: 70 + (item.period_index - minIndex) / Math.max(maxIndex - minIndex, 1) * 1060, y: center - (ratio - .5) * 74, ratio, observation: item }
  })
  const geometry = points.map(({ x, y }) => ({ x, y }))
  return [{ id: record.series_id, name: record.name, index: seriesIndex, points, ridge: smoothPath(geometry), area: ribbonPath(geometry, (_point, pointIndex) => 12 + points[pointIndex].ratio * 11) }]
}))

async function loadBands(): Promise<void> { details.value = await Promise.all(props.series.map((record) => loadSeriesDetail(record))) }
function onScroll(): void {
  if (scrollRaf) return
  scrollRaf = requestAnimationFrame(() => { scrollRaf = 0; if (root.value) leaving.value = root.value.getBoundingClientRect().bottom < window.innerHeight * .6 })
}
function onPointerMove(event: PointerEvent): void {
  if (!field.value || prefersReducedMotion() || window.matchMedia('(max-width: 640px)').matches) return
  const bounds = field.value.getBoundingClientRect(); const dx = ((event.clientX - bounds.left) / bounds.width - .5) * 2; const dy = ((event.clientY - bounds.top) / bounds.height - .5) * 2
  field.value.style.setProperty('--field-x', `${(dx * 7).toFixed(2)}px`); field.value.style.setProperty('--field-y', `${(dy * 5).toFixed(2)}px`)
}
function resetPointer(): void { field.value?.style.setProperty('--field-x', '0px'); field.value?.style.setProperty('--field-y', '0px') }

onMounted(() => { loadTimer = window.setTimeout(() => { void loadBands() }, 80); if (!prefersReducedMotion()) window.addEventListener('scroll', onScroll, { passive: true }) })
onBeforeUnmount(() => { window.clearTimeout(loadTimer); window.removeEventListener('scroll', onScroll); if (scrollRaf) cancelAnimationFrame(scrollRaf) })
</script>

<template>
  <section id="opening" ref="root" class="hero hero-signature chapter--surface" :class="{ 'hero--leaving': leaving }" aria-label="封面">
    <div ref="field" class="hero__field hero-tidal-field" aria-label="九条研究序列的标准化季度潮汐场" @pointermove="onPointerMove" @pointerleave="resetPointer">
      <svg viewBox="0 0 1200 760" preserveAspectRatio="none" role="img" aria-labelledby="hero-field-title hero-field-desc">
        <title id="hero-field-title">九条序列的归一化季度潮汐场</title><desc id="hero-field-desc">所有形状只表达序列内部变化，不比较不同公司的绝对收入。</desc>
        <defs>
          <linearGradient v-for="band in fieldBands" :id="`hero-gradient-${band.index}`" :key="`gradient-${band.id}`" x1="0" y1="0" x2="1" y2=".22"><stop offset="0" :stop-color="band.index % 3 === 0 ? '#0b5662' : '#128f91'" stop-opacity=".08"/><stop offset=".42" :stop-color="band.index % 4 === 0 ? '#51d4bd' : '#24a8a0'" :stop-opacity="band.index === 4 ? .76 : .43"/><stop offset="1" :stop-color="band.index % 3 === 1 ? '#9af2d8' : '#64d6c5'" stop-opacity=".1"/></linearGradient>
          <filter id="hero-tide-glow" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="8"/></filter>
          <filter id="hero-grain"><feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="2" seed="9"/><feColorMatrix values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 .06 0"/></filter>
        </defs>
        <g class="hero-tides">
          <g v-for="band in fieldBands" :key="band.id" class="hero-tide" :class="`hero-tide--${band.index + 1}`" :style="{ '--stagger': `${band.index * 110}ms` }">
            <path class="hero-tide__glow" :d="band.ridge" filter="url(#hero-tide-glow)"/><path class="hero-tide__area" :d="band.area" :fill="`url(#hero-gradient-${band.index})`"/><path class="hero-tide__ridge" :d="band.ridge"/><g class="hero-tide__nodes"><circle v-for="point in band.points" :key="point.observation.observation_id" :cx="point.x" :cy="point.y" r="2.8"/></g>
          </g>
        </g>
        <rect class="hero-field__grain" width="1200" height="760" filter="url(#hero-grain)"/>
      </svg>
      <div class="hero__quarter-scale" aria-hidden="true"><span>2024 Q3</span><span>2025 Q1</span><span>2025 Q3</span><span>2026 Q1</span><span>2026 Q2</span></div>
      <div class="hero-band__semantic visually-hidden" aria-hidden="true"><TidalBand v-if="details[0]" :detail="details[0]" decorative/></div>
    </div>
    <div class="hero__content">
      <p class="hero__kicker">REVENUE TIDES / COMMERCIAL TIDE FIELD</p><h1 class="hero__title"><span>付费潮汐</span><small>游戏商业生命线</small></h1><p class="hero__en">Revenue Tides</p>
      <div class="hero__thesis"><p>流水不是一个统一数字。</p><span>报告口径、实体范围与证据方式，会改变我们看到的商业轨迹。</span></div>
      <p class="hero__comparability">Normalized within each series · absolute revenue is not compared · 不同公司绝对收入不可比较</p>
      <ul class="hero__stats" aria-label="项目规模"><li><b>09</b><span>/ SERIES</span></li><li><b>75</b><span>/ OBSERVATIONS</span></li><li><b>04</b><span>/ PUBLISHERS</span></li></ul><a class="hero__enter" href="#measurement">进入潮汐场 ↓</a>
      <p class="visually-hidden">9 条序列 · 75 个观察 · 4 家发行商 · 2024Q3—2026Q2</p>
    </div>
    <div class="hero__transition-band" aria-hidden="true"><i/><i/><i/><i/><i/></div>
  </section>
</template>

<style scoped>
.hero{position:relative;min-height:100svh;overflow:clip;padding:clamp(6rem,11vh,8.5rem) max(1.25rem,calc((100vw - 96rem)/2)) clamp(2.5rem,6vh,4rem);isolation:isolate;background:radial-gradient(circle at 78% 28%,rgba(125,226,204,.26),transparent 31%),radial-gradient(circle at 18% 72%,rgba(36,168,160,.13),transparent 30%),linear-gradient(135deg,#f8f5ee 0%,#ebece6 54%,#e5eee9 100%)}
.hero::before{content:'';position:absolute;inset:0;z-index:-1;background:linear-gradient(100deg,rgba(248,245,238,.98) 0 22%,rgba(248,245,238,.76) 43%,rgba(248,245,238,.08) 72%)}
.hero__content{position:relative;z-index:3;width:min(55rem,66vw);padding-top:1vh}.hero__kicker{font:650 .7rem var(--font-numeric);letter-spacing:.23em;color:var(--ink-3);margin-bottom:clamp(1.8rem,4vh,3rem)}
.hero__title{margin:0;color:var(--ink);line-height:.78;letter-spacing:-.075em;text-shadow:0 2px 24px rgba(248,245,238,.65)}.hero__title span{display:block;font:790 clamp(6rem,11.8vw,11.5rem)/.76 var(--font-serif)}.hero__title small{display:block;margin-top:1.6rem;font:680 clamp(1.25rem,2vw,2rem)/1.1 var(--font-sans);letter-spacing:.08em;color:var(--ink-2)}
.hero__en{margin-top:.9rem;font:700 clamp(.78rem,1vw,1rem) var(--font-numeric);letter-spacing:.26em;text-transform:uppercase;color:var(--data-teal)}.hero__thesis{margin-top:clamp(1.7rem,4vh,2.8rem);max-width:36rem}.hero__thesis p{font:680 clamp(1.2rem,2vw,1.75rem) var(--font-serif);color:var(--ink)}.hero__thesis span{display:block;margin-top:.45rem;color:var(--ink-2);font-size:.92rem}.hero__comparability{margin-top:1.15rem;max-width:39rem;font:.6rem var(--font-numeric);letter-spacing:.08em;color:var(--ink-3)}
.hero__stats{display:flex;gap:clamp(1.1rem,3vw,3rem);margin:clamp(1.5rem,3vh,2.2rem) 0 0;padding:0;list-style:none}.hero__stats li{display:flex;align-items:baseline;gap:.35rem;color:var(--ink-3);font:.6rem var(--font-numeric);letter-spacing:.12em}.hero__stats b{color:var(--ink);font-size:1.1rem}.hero__enter{display:inline-block;margin-top:clamp(1.4rem,3vh,2.2rem);color:var(--ink);font:650 .68rem var(--font-numeric);letter-spacing:.18em;text-decoration:none;border-bottom:2px solid var(--aqua);padding-bottom:.35rem}
.hero__field{--field-x:0px;--field-y:0px;position:absolute;z-index:1;inset:4.5rem 0 0 24%;overflow:hidden;transform:translate3d(var(--field-x),var(--field-y),0);transition:transform .45s var(--ease-out);pointer-events:auto}.hero__field svg{width:100%;height:calc(100% - 2.5rem);overflow:visible}.hero-tides{transform-origin:58% 50%;transition:transform 1s var(--ease-out),opacity .8s ease}.hero--leaving .hero-tides{transform:translateY(20%) scaleY(.13);opacity:.44}
.hero-tide{opacity:0;animation:hero-tide-arrive 1.7s var(--ease-out) forwards;animation-delay:var(--stagger)}.hero-tide__area{stroke:none}.hero-tide__ridge{fill:none;stroke:#d9fff4;stroke-width:1.25;stroke-opacity:.72;vector-effect:non-scaling-stroke}.hero-tide__glow{fill:none;stroke:#45cfb7;stroke-width:9;stroke-opacity:.22}.hero-tide__nodes circle{fill:#f7fffb;stroke:#138c89;stroke-width:1.15;vector-effect:non-scaling-stroke}.hero-tide:nth-child(even) .hero-tide__ridge{stroke:#8be5d1;stroke-opacity:.54}.hero-tide:nth-child(3n) .hero-tide__nodes{opacity:.55}.hero-field__grain{opacity:.17;mix-blend-mode:multiply;pointer-events:none}
.hero__quarter-scale{position:absolute;left:7%;right:5%;bottom:.3rem;display:flex;justify-content:space-between;border-top:1px solid rgba(13,86,98,.3);padding-top:.5rem;font:.55rem var(--font-numeric);letter-spacing:.08em;color:var(--ink-3)}.hero__transition-band{position:absolute;left:0;right:0;bottom:0;height:20px;display:grid;grid-template-columns:repeat(5,1fr);align-items:end;opacity:.75}.hero__transition-band i{display:block;border-top:2px solid rgba(36,168,160,.36);transform:translateY(calc(var(--n,0)*-3px))}.hero__transition-band i:nth-child(2){--n:1}.hero__transition-band i:nth-child(3){--n:2}.hero__transition-band i:nth-child(4){--n:1}
@keyframes hero-tide-arrive{from{opacity:0;transform:translateX(-7%);clip-path:inset(0 100% 0 0)}55%{opacity:1}to{opacity:1;transform:none;clip-path:inset(0)}}
@media(max-width:900px){.hero__content{width:76vw}.hero__field{left:18%;opacity:.82}.hero__title span{font-size:clamp(5.2rem,15vw,8rem)}}
@media(max-width:640px){.hero{min-height:100svh;padding:5.5rem 1rem 2rem;display:flex;align-items:flex-end;background:radial-gradient(circle at 60% 20%,rgba(125,226,204,.38),transparent 38%),linear-gradient(160deg,#f7f4ec,#e4eee8)}.hero::before{background:linear-gradient(180deg,rgba(247,244,236,.1),rgba(247,244,236,.48) 52%,rgba(247,244,236,.97) 78%)}.hero__content{width:100%;padding-bottom:.9rem}.hero__kicker{margin-bottom:1.2rem}.hero__title span{font-size:clamp(4.2rem,23vw,6.6rem);line-height:.78}.hero__title small{font-size:1.05rem;margin-top:1.05rem}.hero__thesis{margin-top:1.15rem}.hero__thesis p{font-size:1.06rem}.hero__thesis span{font-size:.78rem;max-width:23rem}.hero__comparability{font-size:.52rem;max-width:22rem}.hero__stats{margin-top:1rem}.hero__enter{margin-top:1rem}.hero__field{inset:3.8rem -28% 43% -22%;opacity:.88;transform:none}.hero__field svg{height:100%}.hero-tide{display:none}.hero-tide:nth-child(2),.hero-tide:nth-child(5),.hero-tide:nth-child(8){display:block}.hero__quarter-scale{left:18%;right:18%;font-size:.42rem}.hero__quarter-scale span:nth-child(even){display:none}}
@media(prefers-reduced-motion:reduce){.hero,.hero__field,.hero-tides{transition:none}.hero-tide{opacity:1;animation:none;clip-path:none}.hero--leaving .hero-tides{transform:none;opacity:1}}
</style>
