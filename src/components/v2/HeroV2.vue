<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { loadSeriesDetail } from '../../data/client'
import type { Observation, SeriesIndexRecord } from '../../types/webData'
import { prefersReducedMotion } from '../../composables/useScrolly'

const props = defineProps<{ series: SeriesIndexRecord[] }>()

const paths = ref<string[]>([])
const leaving = ref(false)
let scrollRaf = 0
let trailTimer = 0

interface TrailPoint { x: number; y: number }

function buildTrail(obs: Observation[]): TrailPoint[] {
  const sorted = [...obs].sort((a, b) => a.period_index - b.period_index)
  const values = sorted
    .map((o) => o.baseline_index)
    .filter((v): v is number => v !== null && Number.isFinite(v))
  if (values.length < 2) return []
  const max = Math.max(...values)
  const floor = Math.min(...values)
  const cap = Math.max(150, max)
  const W = 1200
  const H = 620
  const padTop = 30
  const padBottom = 40
  return sorted.map((o, i) => {
    const v = o.baseline_index ?? floor
    const x = values.length > 1 ? (i / (values.length - 1)) * W : W / 2
    const y = padTop + (1 - (v - floor) / (cap - floor)) * (H - padTop - padBottom)
    return { x, y }
  })
}

function toPath(points: TrailPoint[]): string {
  if (points.length === 0) return ''
  return points.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ')
}

async function loadTrails(): Promise<void> {
  const all = await Promise.all(props.series.map((record) => loadSeriesDetail(record)))
  const next: string[] = []
  for (const detail of all) {
    for (const version of detail.metric_versions) {
      const path = toPath(buildTrail(detail.observations.filter((item) => item.metric_definition_id === version.metric_definition_id)))
      if (path) next.push(path)
    }
  }
  paths.value = next
}

function onScroll(): void {
  if (scrollRaf) return
  scrollRaf = requestAnimationFrame(() => {
    scrollRaf = 0
    const el = root.value
    if (!el) return
    const rect = el.getBoundingClientRect()
    leaving.value = rect.bottom < window.innerHeight * 0.55
  })
}

const root = ref<HTMLElement | null>(null)
const stats = computed(() => [
  `${props.series.length.toString().padStart(2, '0')} SERIES`,
  '75 OBSERVATIONS',
  '04 PUBLISHERS',
])

onMounted(() => {
  trailTimer = window.setTimeout(() => { void loadTrails() }, 1400)
  if (!prefersReducedMotion()) window.addEventListener('scroll', onScroll, { passive: true })
})
onBeforeUnmount(() => {
  window.clearTimeout(trailTimer)
  window.removeEventListener('scroll', onScroll)
  if (scrollRaf) cancelAnimationFrame(scrollRaf)
})
</script>

<template>
  <section id="opening" ref="root" class="hero chapter--dark" :class="{ 'hero--leaving': leaving }" aria-label="封面">
    <svg
      class="traj-field"
      viewBox="0 0 1200 620"
      preserveAspectRatio="xMidYMid slice"
      aria-hidden="true"
    >
      <path
        v-for="(path, i) in paths"
        :key="i"
        :d="path"
        class="traj"
        :class="`traj--${(i % 5) + 1}`"
      />
    </svg>
    <div class="hero__content">
      <p class="hero__kicker">REVENUE TIDES · 2024Q3 — 2026Q2</p>
      <h1 class="display-hero hero__title">付费潮汐</h1>
      <p class="hero__subtitle">游戏商业生命线</p>
      <p class="hero__en">The Commercial Life of Games</p>
      <p class="hero__note">Normalized shapes — not absolute revenue comparison. 不同公司绝对收入不可比较；指标版本保持分离。</p>
      <ul class="hero__stats">
        <li v-for="stat in stats" :key="stat">{{ stat }}</li>
      </ul>
    </div>
    <div class="hero__ruler quarter-ruler" aria-hidden="true">
      <span>2024 Q3</span><span>2025 Q1</span><span>2025 Q3</span><span>2026 Q1</span><span>2026 Q2</span>
    </div>
    <p class="hero__scroll-hint">SCROLL</p>
  </section>
</template>

<style scoped>
.hero {
  position: relative;
  min-height: 100svh;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: clamp(5.5rem, 12vh, 8rem) max(1.25rem, calc((100vw - 76rem) / 2)) clamp(2.5rem, 6vh, 4rem);
  transition: opacity 0.6s ease;
}
.hero--leaving { opacity: 0; }

.hero__content { position: relative; z-index: 2; }
.hero__kicker {
  font-family: var(--font-numeric);
  font-size: 0.78rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--on-dark-2);
  margin-bottom: clamp(2rem, 5vh, 3.5rem);
}
.hero__title { color: var(--on-dark); }
.hero__subtitle {
  font-size: clamp(1.15rem, 2.2vw, 1.7rem);
  font-weight: 600;
  color: var(--on-dark-2);
  margin-top: 0.9rem;
}
.hero__en {
  font-family: var(--font-numeric);
  font-size: 0.82rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--on-dark-3);
  margin-top: 1.6rem;
}
.hero__note {
  font-size: 0.72rem;
  color: var(--on-dark-3);
  margin-top: 2.4rem;
  max-width: 30em;
}
.hero__stats {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem 2.4rem;
  list-style: none;
  padding: 0;
  margin: clamp(2.5rem, 6vh, 4rem) 0 0;
}
.hero__stats li {
  font-family: var(--font-numeric);
  font-size: 0.8rem;
  letter-spacing: 0.16em;
  color: var(--teal-bright);
}
.hero__ruler {
  position: relative;
  z-index: 2;
  margin-top: 2.5rem;
}
.hero__scroll-hint {
  position: absolute;
  right: max(1.25rem, calc((100vw - 76rem) / 2));
  bottom: clamp(2.5rem, 6vh, 4rem);
  writing-mode: vertical-rl;
  font-family: var(--font-numeric);
  font-size: 0.66rem;
  letter-spacing: 0.24em;
  color: var(--on-dark-3);
}

@media (max-width: 640px) {
  .hero__stats { gap: 0.7rem 1.4rem; }
  .hero__scroll-hint { display: none; }
}
</style>
