<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { loadSeriesDetail } from '../../data/client'
import type { Observation, SeriesDetail, SeriesIndexRecord } from '../../types/webData'
import { prefersReducedMotion } from '../../composables/useScrolly'
import { displayCopy } from '../../content/displayCopy.zh'
import { smoothPath, tidalBodyPath, tidalEnvelopePath } from '../../utils/tidalGeometry'
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
  return [{
    id: record.series_id,
    name: record.name,
    index: seriesIndex,
    points,
    surface: smoothPath(geometry),
    body: tidalBodyPath(geometry, { baseDepth: 42, peakContribution: 14, slopeContribution: .1, minDepth: 34, maxDepth: 64 }),
    deep: tidalEnvelopePath(geometry, 48, 18),
  }]
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
          <filter id="hero-tide-glow" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="5"/></filter>
          <filter id="hero-grain"><feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="2" seed="9"/><feColorMatrix values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 .06 0"/></filter>
          <linearGradient id="hero-body-fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="white"/><stop offset=".62" stop-color="white" stop-opacity=".88"/><stop offset=".87" stop-color="white" stop-opacity=".34"/><stop offset="1" stop-color="white" stop-opacity="0"/></linearGradient><mask id="hero-body-mask"><rect width="1200" height="760" fill="url(#hero-body-fade)"/></mask>
        </defs>
        <g class="hero-tides">
          <g v-for="band in fieldBands" :key="band.id" class="hero-tide" :class="[`hero-tide--${band.index + 1}`, { 'is-foreground': [1,4,6,8].includes(band.index) }]" :style="{ '--stagger': `${band.index * 110}ms` }">
            <g mask="url(#hero-body-mask)"><path class="hero-tide__deep" :d="band.deep"/><path class="hero-tide__area" :d="band.body" :fill="`url(#hero-gradient-${band.index})`"/></g><path class="hero-tide__glow" :d="band.surface" filter="url(#hero-tide-glow)"/><path class="hero-tide__surface" :d="band.surface"/>
          </g>
        </g>
        <rect class="hero-field__grain" width="1200" height="760" filter="url(#hero-grain)"/>
      </svg>
      <div class="hero__quarter-scale" aria-hidden="true"><span>2024 Q3</span><span>2025 Q1</span><span>2025 Q3</span><span>2026 Q1</span><span>2026 Q2</span></div>
      <div class="hero-band__semantic visually-hidden" aria-hidden="true"><TidalBand v-if="details[0]" :detail="details[0]" decorative/></div>
    </div>
    <div class="hero__content">
      <p class="hero__kicker">REVENUE TIDES</p><h1 class="hero__title"><span>{{ displayCopy.hero.title }}</span><small>{{ displayCopy.hero.subtitle }}</small></h1>
      <div class="hero__thesis"><p>{{ displayCopy.hero.lede }}</p><span>{{ displayCopy.hero.dek }}</span></div>
      <p class="hero__comparability">{{ displayCopy.hero.comparison }}</p>
      <ul class="hero__stats" aria-label="项目规模"><li><b>09</b><span>条序列</span></li><li><b>75</b><span>个季度观察</span></li><li><b>04</b><span>家公司</span></li></ul><a class="hero__enter" href="#measurement">{{ displayCopy.hero.enter }} ↓</a>
      <p class="visually-hidden">9 条序列 · 75 个观察 · 4 家发行商 · 2024Q3—2026Q2</p>
    </div>
    <div class="hero__transition-band" aria-hidden="true"><i/><i/><i/><i/><i/></div>
  </section>
</template>

<style scoped>
.hero{position:relative;min-height:100svh;overflow:clip;padding:clamp(6rem,11vh,8.5rem) max(1.25rem,calc((100vw - 96rem)/2)) clamp(2.5rem,6vh,4rem);isolation:isolate;background:radial-gradient(circle at 78% 28%,rgba(125,226,204,.18),transparent 34%),radial-gradient(circle at 18% 72%,rgba(36,168,160,.08),transparent 32%),linear-gradient(135deg,#f8f5ee 0%,#ebece6 54%,#e5eee9 100%)}
.hero::before{content:'';position:absolute;inset:0;z-index:2;pointer-events:none;background:radial-gradient(ellipse at 19% 44%,rgba(248,245,238,.94) 0 16%,rgba(248,245,238,.72) 33%,rgba(248,245,238,.24) 51%,transparent 68%)}
.hero__content{position:relative;z-index:3;width:min(55rem,66vw);padding-top:1vh}.hero__kicker{font:650 .7rem var(--font-numeric);letter-spacing:.23em;color:var(--ink-3);margin-bottom:clamp(1.8rem,4vh,3rem)}
.hero__title{margin:0;color:var(--ink);line-height:.78;letter-spacing:-.075em;text-shadow:0 2px 24px rgba(248,245,238,.65)}.hero__title span{display:block;font:790 clamp(6rem,11.8vw,11.5rem)/.76 var(--font-serif)}.hero__title small{display:block;margin-top:1.6rem;font:680 clamp(1.25rem,2vw,2rem)/1.1 var(--font-sans);letter-spacing:.08em;color:var(--ink-2)}
.hero__en{margin-top:.9rem;font:700 clamp(.78rem,1vw,1rem) var(--font-numeric);letter-spacing:.26em;text-transform:uppercase;color:var(--data-teal)}.hero__thesis{margin-top:clamp(1.7rem,4vh,2.8rem);max-width:36rem}.hero__thesis p{font:680 clamp(1.2rem,2vw,1.75rem) var(--font-serif);color:var(--ink)}.hero__thesis span{display:block;margin-top:.45rem;color:var(--ink-2);font-size:.92rem}.hero__comparability{margin-top:1.15rem;max-width:39rem;font:.6rem var(--font-numeric);letter-spacing:.08em;color:var(--ink-3)}
.hero__stats{display:flex;gap:clamp(1.1rem,3vw,3rem);margin:clamp(1.5rem,3vh,2.2rem) 0 0;padding:0;list-style:none}.hero__stats li{display:flex;align-items:baseline;gap:.35rem;color:var(--ink-3);font:.6rem var(--font-numeric);letter-spacing:.12em}.hero__stats b{color:var(--ink);font-size:1.1rem}.hero__enter{display:inline-block;margin-top:clamp(1.4rem,3vh,2.2rem);color:var(--ink);font:650 .68rem var(--font-numeric);letter-spacing:.18em;text-decoration:none;border-bottom:2px solid var(--aqua);padding-bottom:.35rem}
.hero__field{--field-x:0px;--field-y:0px;position:absolute;z-index:1;inset:2.5rem -4% -1rem -6%;overflow:hidden;transform:translate3d(var(--field-x),var(--field-y),0);transition:transform .45s var(--ease-out);pointer-events:auto;mask-image:linear-gradient(90deg,rgba(0,0,0,.32),rgba(0,0,0,.7) 26%,#000 48%)}.hero__field::before{content:'';position:absolute;inset:8% 3% 15% 10%;border-radius:50%;background:radial-gradient(ellipse,rgba(78,208,184,.11),rgba(125,226,204,.035) 44%,transparent 74%);filter:blur(34px)}.hero__field svg{position:relative;width:100%;height:calc(100% - 1.2rem);overflow:visible}.hero-tides{transform-origin:58% 50%;transition:transform 1s var(--ease-out),opacity .8s ease}.hero--leaving .hero-tides{transform:translateY(22%) scaleY(.18);opacity:.42}
.hero-tide{opacity:0;mix-blend-mode:multiply;animation:hero-tide-arrive 1.7s var(--ease-out) forwards;animation-delay:var(--stagger)}.hero-tide__area{stroke:none;opacity:.47}.hero-tide__deep{fill:rgba(11,86,98,.07)}.hero-tide__surface{fill:none;stroke:#cafff1;stroke-width:.75;stroke-opacity:.38;vector-effect:non-scaling-stroke}.hero-tide__glow{fill:none;stroke:#45cfb7;stroke-width:13;stroke-opacity:.07}.hero-tide.is-foreground{mix-blend-mode:normal}.hero-tide.is-foreground .hero-tide__area{opacity:1}.hero-tide.is-foreground .hero-tide__surface{stroke-width:1.25;stroke-opacity:.78}.hero-tide.is-foreground .hero-tide__glow{stroke-width:16;stroke-opacity:.13}.hero-field__grain{opacity:.045;mix-blend-mode:multiply;pointer-events:none}
.hero__quarter-scale{position:absolute;left:8%;right:5%;bottom:.3rem;display:flex;justify-content:space-between;padding-top:.5rem;font:.52rem var(--font-numeric);letter-spacing:.08em;color:rgba(27,68,68,.58)}.hero__transition-band{position:absolute;left:23%;right:-5%;bottom:-2rem;height:5rem;border-radius:50%;background:radial-gradient(ellipse,rgba(36,168,160,.16),transparent 68%);filter:blur(16px)}.hero__transition-band i{display:none}
@keyframes hero-tide-arrive{from{opacity:0;transform:translate3d(-6%,10px,0) scaleY(.9)}55%{opacity:.8}to{opacity:1;transform:none}}
@media(max-width:900px){.hero__content{width:76vw}.hero__field{left:18%;opacity:.82}.hero__title span{font-size:clamp(5.2rem,15vw,8rem)}}
@media(max-width:640px){.hero{min-height:100svh;padding:7.2rem 1rem 2rem;display:block;background:radial-gradient(circle at 60% 24%,rgba(125,226,204,.22),transparent 40%),linear-gradient(160deg,#f7f4ec,#e4eee8)}.hero::before{z-index:2;background:radial-gradient(ellipse at 35% 42%,rgba(247,244,236,.88),rgba(247,244,236,.55) 38%,transparent 68%)}.hero__content{width:100%;padding-bottom:.9rem}.hero__kicker{margin-bottom:1.2rem}.hero__title span{font-size:clamp(4.2rem,23vw,6.6rem);line-height:.78}.hero__title small{font-size:1.05rem;margin-top:1.05rem}.hero__thesis{margin-top:1.15rem}.hero__thesis p{font-size:1.06rem}.hero__thesis span{font-size:.78rem;max-width:23rem}.hero__comparability{font-size:.52rem;max-width:22rem}.hero__stats{margin-top:1rem}.hero__enter{margin-top:1rem}.hero__field{inset:2.8rem -36% 12% -35%;opacity:.84;transform:none;mask-image:linear-gradient(180deg,#000,rgba(0,0,0,.72) 68%,transparent)}.hero__field svg{height:100%}.hero-tide{display:none}.hero-tide:nth-child(2),.hero-tide:nth-child(5),.hero-tide:nth-child(8){display:block}.hero__quarter-scale{left:18%;right:18%;bottom:28%;font-size:.42rem}.hero__quarter-scale span:nth-child(even){display:none}}
@media(max-width:640px){.hero__kicker{display:none}}
@media(prefers-reduced-motion:reduce){.hero,.hero__field,.hero-tides{transition:none}.hero-tide{opacity:1;animation:none;clip-path:none}.hero--leaving .hero-tides{transform:none;opacity:1}}
</style>
