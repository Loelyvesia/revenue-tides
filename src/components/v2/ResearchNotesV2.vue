<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { loadSeriesDetail } from '../../data/client'
import type { Finding, Observation, SeriesDetail, SeriesIndexRecord } from '../../types/webData'

const props = defineProps<{ findings: Finding[]; series: SeriesIndexRecord[] }>()
const root = ref<HTMLElement | null>(null)
const details = ref<SeriesDetail[]>([])
let observer: IntersectionObserver | null = null
const notes = computed(() => props.findings.filter((item) => !item.headline))
const derivedChanges = computed(() => details.value.flatMap((item) => item.observations).filter((item: Observation) => item.qoq.eligible && item.derived?.direction_sign_stable !== null))
onMounted(() => {
  const load = async () => { details.value = await Promise.all(props.series.filter((item) => ['series_mcoc','series_jackpot_world','series_lotsa_slots'].includes(item.series_id)).map((item) => loadSeriesDetail(item))) }
  if (!('IntersectionObserver' in window)) { void load(); return }
  observer = new IntersectionObserver((entries) => { if (entries.some((entry) => entry.isIntersecting)) { void load(); observer?.disconnect() } }, { rootMargin: '400px' })
  if (root.value) observer.observe(root.value)
})
onBeforeUnmount(() => observer?.disconnect())
</script>

<template>
  <section id="research-notes" ref="root" class="chapter chapter--paper notes" aria-labelledby="notes-title">
    <div class="shell"><header class="chapter-head"><span class="eyebrow">RESEARCH NOTES</span><h2 id="notes-title" class="display-chapter">恢复、窗口与不确定性</h2><p class="lede">三条补充结论保留它们的限制，不被压缩成趋势标签。</p></header>
      <div class="notes-grid">
        <article v-for="finding in notes" :id="`finding-${finding.finding_id}`" :key="finding.finding_id" class="note-card">
          <p class="eyebrow">{{ finding.finding_id }} · {{ finding.strength }}</p><h3>{{ finding.title_zh }}</h3><p>{{ finding.statement_zh }}</p>
          <div v-if="finding.finding_id === 'F3'" class="note-figure"><strong class="display-figure">+32.4%</strong><span>2026 Q2 rebound</span><b>4.1% below peak</b></div>
          <div v-else-if="finding.finding_id === 'F5'" class="note-figure"><strong class="display-figure">−35.3%</strong><span>2025 Q2—2026 Q2</span><b>royalty-integrated v2 only</b></div>
          <div v-else-if="finding.finding_id === 'F6'" class="interval-matrix" aria-label="15 个派生变化中 9 个方向敏感，6 个方向稳定"><i v-for="(item,index) in derivedChanges" :key="item.observation_id" :class="{ stable: item.derived?.direction_sign_stable, sensitive: !item.derived?.direction_sign_stable }" :title="`${index + 1}: ${item.derived?.direction_sign_stable ? 'sign-stable' : 'sign-sensitive'}`"/><strong>9 / 15 · 60.0%</strong></div>
          <p class="note-limit"><strong>禁止解读</strong> {{ finding.forbidden_interpretation }}</p>
        </article>
      </div>
    </div>
  </section>
</template>
