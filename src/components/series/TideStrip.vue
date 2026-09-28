<script setup lang="ts">
import { computed } from 'vue'
import type { Observation, SeriesDetail } from '../../types/webData'
import { groupByQuarter } from '../../utils/model'

const props = defineProps<{ detail: SeriesDetail }>()
const groups = computed(() => groupByQuarter(props.detail))
const available = computed(() => props.detail.observations.filter((item): item is Observation & { value: number } => item.value !== null))
const min = computed(() => Math.min(...available.value.map((item) => item.value)))
const max = computed(() => Math.max(...available.value.map((item) => item.value)))

function x(quarter: string): number {
  const index = groups.value.findIndex((group) => group.quarter === quarter)
  return groups.value.length > 1 ? 40 + (index / (groups.value.length - 1)) * 720 : 400
}
function y(value: number): number {
  return max.value === min.value ? 100 : 160 - ((value - min.value) / (max.value - min.value)) * 110
}
function points(version: string): string {
  return available.value.filter((item) => item.metric_version === version).sort((a, b) => a.period_index - b.period_index).map((item) => `${x(item.quarter)},${y(item.value)}`).join(' ')
}
</script>

<template>
  <figure class="tide-strip">
    <svg viewBox="0 0 800 210" role="img" :aria-labelledby="`tide-title-${detail.series_id} tide-desc-${detail.series_id}`">
      <title :id="`tide-title-${detail.series_id}`">{{ detail.identity.entity }} 序列内季度轨迹</title>
      <desc :id="`tide-desc-${detail.series_id}`">只显示同一序列内变化；不同指标版本使用断开的轨迹，绝对收入不可跨公司比较。</desc>
      <line x1="35" y1="165" x2="765" y2="165" class="axis" />
      <polyline v-for="(metric, index) in detail.metric_versions" :key="metric.metric_definition_id" :points="points(metric.version)" :class="['strip-line', `line-${index}`]" />
      <g v-for="observation in available" :key="observation.observation_id">
        <circle v-if="observation.evidence_class === 'OFFICIAL_REPORTED'" :cx="x(observation.quarter)" :cy="y(observation.value)" r="4" class="direct" />
        <path v-else :d="`M ${x(observation.quarter)} ${y(observation.value)-5} l 5 5 -5 5 -5 -5 Z`" class="derived" />
      </g>
      <text v-for="group in groups" :key="group.quarter" :x="x(group.quarter)" y="190" text-anchor="middle">{{ group.quarter }}</text>
    </svg>
    <figcaption>序列内轨迹；各指标版本保持独立。Absolute revenue levels are not comparable across companies.</figcaption>
  </figure>
</template>

<style scoped>
.tide-strip { margin: 1rem 0; }
svg { display: block; width: 100%; min-width: 42rem; }
.tide-strip { overflow-x: auto; }
.axis { stroke: var(--rule-border); }
.strip-line { fill: none; stroke: var(--accent-primary); stroke-width: 2; }
.line-1 { stroke: var(--text-primary); stroke-dasharray: 7 5; }
.direct { fill: var(--evidence-direct); }
.derived { fill: var(--surface-primary); stroke: var(--evidence-derived); stroke-width: 2; }
text { fill: var(--text-secondary); font: 11px var(--font-numeric); }
figcaption { color: var(--text-secondary); font-size: 0.75rem; }
@media (max-width: 767px) { svg { min-width: 38rem; } }
</style>
