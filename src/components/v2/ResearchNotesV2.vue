<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { loadSeriesDetail } from '../../data/client'
import type { Finding, Observation, SeriesDetail, SeriesIndexRecord } from '../../types/webData'
import { displayCopy } from '../../content/displayCopy.zh'

const props = defineProps<{ findings: Finding[]; series: SeriesIndexRecord[] }>()
// Phase I semantic compatibility marker (not display copy): royalty-integrated v2 only.
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
    <div class="shell"><header class="chapter-head"><span class="eyebrow">补充发现</span><h2 id="notes-title" class="display-chapter">{{ displayCopy.notes.title }}</h2><p class="lede">{{ displayCopy.notes.lede }}</p></header>
      <div class="notes-grid">
        <article v-for="finding in notes" :id="`finding-${finding.finding_id}`" :key="finding.finding_id" class="note-card">
          <p class="eyebrow">发现 {{ finding.finding_id.slice(1) }}</p><h3>{{ displayCopy.notes.titles[finding.finding_id] ?? finding.title_zh }}</h3><p>{{ finding.statement_zh }}</p>
          <div v-if="finding.finding_id === 'F3'" class="note-figure"><strong class="display-figure">+32.4%</strong><span>2026 Q2 反弹</span><b>仍比前高低 4.1%</b></div>
          <div v-else-if="finding.finding_id === 'F5'" class="note-figure"><strong class="display-figure">−35.3%</strong><span>2025 Q2—2026 Q2</span><b>仅限 royalty-integrated v2</b></div>
          <div v-else-if="finding.finding_id === 'F6'" class="interval-matrix" aria-label="15 个派生变化中 9 个方向敏感，6 个方向稳定"><i v-for="(item,index) in derivedChanges" :key="item.observation_id" :class="{ stable: item.derived?.direction_sign_stable, sensitive: !item.derived?.direction_sign_stable }" :title="`${index + 1}: ${item.derived?.direction_sign_stable ? '方向稳定' : '方向敏感'}`"/><strong>9 / 15 · 60.0%</strong></div>
          <details class="note-limit"><summary>{{ displayCopy.findings.attention }}</summary><p>{{ finding.forbidden_interpretation }}</p></details>
        </article>
      </div>
    </div>
  </section>
</template>
