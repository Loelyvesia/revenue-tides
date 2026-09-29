<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { loadSeriesDetail } from '../../data/client'
import type { SeriesDetail, SeriesIndexRecord } from '../../types/webData'
import { prefersReducedMotion } from '../../composables/useScrolly'
import TidalBand from './TidalBand.vue'

const props = defineProps<{ series: SeriesIndexRecord[] }>()
const details = ref<SeriesDetail[]>([])
const leaving = ref(false)
const root = ref<HTMLElement | null>(null)
let scrollRaf = 0
let loadTimer = 0

const rows = computed(() => props.series.map((record) => ({
  record,
  detail: details.value.find((item) => item.series_id === record.series_id) ?? null,
})))

async function loadBands(): Promise<void> {
  details.value = await Promise.all(props.series.map((record) => loadSeriesDetail(record)))
}

function onScroll(): void {
  if (scrollRaf) return
  scrollRaf = requestAnimationFrame(() => {
    scrollRaf = 0
    if (!root.value) return
    leaving.value = root.value.getBoundingClientRect().bottom < window.innerHeight * .52
  })
}

onMounted(() => {
  loadTimer = window.setTimeout(() => { void loadBands() }, 120)
  if (!prefersReducedMotion()) window.addEventListener('scroll', onScroll, { passive: true })
})
onBeforeUnmount(() => {
  window.clearTimeout(loadTimer)
  window.removeEventListener('scroll', onScroll)
  if (scrollRaf) cancelAnimationFrame(scrollRaf)
})
</script>

<template>
  <section id="opening" ref="root" class="hero hero-signature chapter--surface" :class="{ 'hero--leaving': leaving }" aria-label="封面">
    <div class="hero__field hero-tidal-field" aria-label="九条研究序列的标准化季度轨迹">
      <div v-for="({ record, detail }, index) in rows" :key="record.series_id" class="hero-band" :class="{ 'hero-band--lead': [1, 5, 7].includes(index) }">
        <span class="hero-band__index">{{ String(index + 1).padStart(2, '0') }}</span>
        <span class="hero-band__name">{{ record.name }}</span>
        <TidalBand v-if="detail" :detail="detail" decorative />
        <span v-else class="hero-band__loading" />
      </div>
      <div class="hero__quarter-scale" aria-hidden="true">
        <span>2024 Q3</span><span>2025 Q1</span><span>2025 Q3</span><span>2026 Q1</span><span>2026 Q2</span>
      </div>
    </div>

    <div class="hero__content">
      <p class="hero__kicker">REVENUE TIDES / COMMERCIAL MEASUREMENT</p>
      <h1 class="hero__title"><span>付费潮汐</span><small>游戏商业生命线</small></h1>
      <p class="hero__en">Revenue Tides</p>
      <div class="hero__thesis">
        <p>流水不是一个统一数字。</p>
        <span>报告口径、实体范围与证据方式，会改变我们看到的商业轨迹。</span>
      </div>
      <p class="hero__comparability">Normalized shape · absolute revenue is not compared · 不同公司绝对收入不可比较</p>
      <ul class="hero__stats" aria-label="项目规模">
        <li><b>09</b><span>/ SERIES</span></li>
        <li><b>75</b><span>/ OBSERVATIONS</span></li>
        <li><b>04</b><span>/ PUBLISHERS</span></li>
      </ul>
      <a class="hero__enter" href="#prism">进入季度棱镜 ↓</a>
      <p class="visually-hidden">9 条序列 · 75 个观察 · 4 家发行商 · 2024Q3—2026Q2</p>
    </div>
    <div class="hero__transition-band" aria-hidden="true"><i /><i /><i /><i /><i /></div>
  </section>
</template>

<style scoped>
.hero { position:relative; min-height:100svh; overflow:clip; padding:clamp(5.8rem,11vh,8rem) max(1.25rem,calc((100vw - 92rem)/2)) clamp(2rem,5vh,3.5rem); transition:opacity .6s ease; }
.hero--leaving{opacity:0}.hero__content{position:relative;z-index:3;width:min(46rem,58vw)}
.hero__kicker{font:.68rem var(--font-numeric);letter-spacing:.2em;color:var(--ink-3);margin-bottom:clamp(2rem,5vh,3.8rem)}
.hero__title{margin:0;color:var(--ink);line-height:.9;letter-spacing:-.055em}.hero__title span{display:block;font:760 clamp(4.8rem,10vw,9.4rem)/.86 var(--font-serif)}.hero__title small{display:block;margin-top:1.25rem;font:620 clamp(1.15rem,2.2vw,1.8rem)/1.2 var(--font-sans);letter-spacing:.06em;color:var(--ink-2)}
.hero__en{margin-top:.75rem;font:650 .78rem var(--font-numeric);letter-spacing:.22em;text-transform:uppercase;color:var(--data-teal)}
.hero__thesis{margin-top:clamp(2rem,5vh,3.4rem);max-width:34rem}.hero__thesis p{font:650 clamp(1.15rem,2vw,1.6rem) var(--font-serif);color:var(--ink)}.hero__thesis span{display:block;margin-top:.55rem;color:var(--ink-2);font-size:.92rem}
.hero__comparability{margin-top:1.3rem;font:.64rem var(--font-numeric);letter-spacing:.08em;color:var(--ink-3)}
.hero__stats{display:flex;gap:clamp(1.1rem,3vw,3rem);margin:clamp(1.8rem,4vh,3rem) 0 0;padding:0;list-style:none}.hero__stats li{display:flex;align-items:baseline;gap:.35rem;color:var(--ink-3);font:.62rem var(--font-numeric);letter-spacing:.12em}.hero__stats b{color:var(--ink);font-size:1rem}
.hero__enter{display:inline-block;margin-top:clamp(1.8rem,4vh,3rem);color:var(--ink);font:.68rem var(--font-numeric);letter-spacing:.18em;text-decoration:none;border-bottom:1px solid var(--data-teal);padding-bottom:.35rem}
.hero__field{position:absolute;z-index:1;inset:7vh max(1rem,calc((100vw - 94rem)/2)) 7vh 38%;display:grid;grid-template-rows:repeat(9,minmax(0,1fr)) auto;opacity:.74}
.hero-band{display:grid;grid-template-columns:2.2rem minmax(5rem,9rem) minmax(16rem,1fr);gap:.8rem;align-items:center;min-height:0;border-top:1px solid rgba(32,35,33,.08)}
.hero-band__index,.hero-band__name{font:.54rem var(--font-numeric);letter-spacing:.08em;color:var(--ink-3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.hero-band__index{color:rgba(32,35,33,.28)}
.hero-band :deep(.tidal-band){width:100%;height:100%;min-height:3rem}.hero-band:not(.hero-band--lead) :deep(.tidal-band__path){opacity:.38;stroke-width:5}.hero-band--lead :deep(.tidal-band__path){opacity:1;stroke-width:8}.hero-band--lead .hero-band__name{color:var(--ink-2)}.hero-band__loading{height:1px;background:var(--rule-dark)}
.hero__quarter-scale{margin-left:12.5rem;display:flex;justify-content:space-between;border-top:1px solid var(--rule-dark-strong);padding-top:.5rem;font:.56rem var(--font-numeric);letter-spacing:.08em;color:var(--ink-3)}
.hero__transition-band{position:absolute;left:0;right:0;bottom:0;height:18px;display:grid;grid-template-columns:repeat(5,1fr);align-items:end;opacity:.7}.hero__transition-band i{display:block;border-top:1px solid var(--data-teal);transform:translateY(calc(var(--n,0)*-2px))}.hero__transition-band i:nth-child(2){--n:1}.hero__transition-band i:nth-child(3){--n:2}.hero__transition-band i:nth-child(4){--n:1}
@media(max-width:900px){.hero__content{width:72%}.hero__field{left:32%;opacity:.56}.hero-band{grid-template-columns:1.6rem 5.5rem 1fr}.hero__quarter-scale{margin-left:7.9rem}}
@media(max-width:640px){.hero{min-height:100svh;padding:5.5rem 1rem 2rem;display:flex;align-items:flex-end}.hero__content{width:100%;padding-bottom:1.1rem}.hero__kicker{margin-bottom:1.5rem}.hero__title span{font-size:clamp(3.7rem,20vw,5.2rem)}.hero__title small{font-size:1.05rem}.hero__thesis{margin-top:1.4rem}.hero__thesis p{font-size:1.08rem}.hero__thesis span{font-size:.79rem;max-width:25rem}.hero__comparability{max-width:23rem}.hero__stats{margin-top:1.2rem;gap:.9rem}.hero__stats li{display:grid;gap:0;font-size:.5rem}.hero__stats b{font-size:.82rem}.hero__enter{margin-top:1.25rem}.hero__field{inset:4.7rem .8rem auto;height:34vh;grid-template-rows:repeat(4,1fr) auto;opacity:.85}.hero-band{grid-template-columns:1.2rem 4.5rem 1fr;gap:.4rem}.hero-band:nth-child(n+5){display:none}.hero-band__name{font-size:.48rem}.hero-band :deep(.tidal-band){min-height:2.2rem}.hero__quarter-scale{margin-left:6.1rem;font-size:.45rem}.hero__quarter-scale span:nth-child(2n){display:none}}
</style>
