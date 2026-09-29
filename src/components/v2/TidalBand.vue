<script setup lang="ts">
import { computed } from 'vue'
import type { Observation, SeriesDetail } from '../../types/webData'

const props = withDefaults(defineProps<{
  detail: SeriesDetail
  compact?: boolean
  showEvents?: boolean
  decorative?: boolean
}>(), {
  compact: false,
  showEvents: false,
  decorative: false,
})

const width = 1000
const height = computed(() => props.compact ? 54 : 76)
const usableTop = computed(() => props.compact ? 8 : 10)
const usableBottom = computed(() => props.compact ? 43 : 58)

const observed = computed(() => props.detail.observations
  .filter((item): item is Observation & { value: number } => item.value !== null)
  .sort((a, b) => a.period_index - b.period_index || a.metric_version.localeCompare(b.metric_version)))

const indices = computed(() => [...new Set(observed.value.map((item) => item.period_index))].sort((a, b) => a - b))
const minIndex = computed(() => indices.value[0] ?? 0)
const maxIndex = computed(() => indices.value.at(-1) ?? minIndex.value + 1)
const x = (index: number): number => 18 + (index - minIndex.value) / Math.max(maxIndex.value - minIndex.value, 1) * 964

function versionObservations(metricId: string): Array<Observation & { value: number }> {
  return observed.value.filter((item) => item.metric_definition_id === metricId)
}

function versionY(item: Observation & { value: number }, list: Array<Observation & { value: number }>): number {
  const values = list.map((entry) => entry.baseline_index ?? entry.value)
  const low = Math.min(...values)
  const high = Math.max(...values)
  const current = item.baseline_index ?? item.value
  const ratio = high === low ? .5 : (current - low) / (high - low)
  return usableBottom.value - ratio * (usableBottom.value - usableTop.value)
}

const lanes = computed(() => props.detail.metric_versions.map((metric, laneIndex) => {
  const items = versionObservations(metric.metric_definition_id)
  const points = items.map((item) => ({ item, x: x(item.period_index), y: versionY(item, items) }))
  return {
    id: metric.metric_definition_id,
    version: metric.version,
    laneIndex,
    points,
    path: points.map((point, index) => `${index ? 'L' : 'M'}${point.x.toFixed(1)},${point.y.toFixed(1)}`).join(' '),
  }
}).filter((lane) => lane.points.length))

const seams = computed(() => props.detail.metric_versions
  .filter((metric) => metric.version_break?.break_after)
  .map((metric) => {
    const first = observed.value.find((item) => item.quarter === metric.version_break?.break_after && item.metric_definition_id === metric.metric_definition_id)
    return first ? { id: metric.metric_definition_id, x: x(first.period_index) } : null
  }).filter((item): item is { id: string; x: number } => item !== null))

const peaks = computed(() => lanes.value.flatMap((lane) => lane.points.filter((point) => point.item.drawdown_percent === 0)))
const derived = computed(() => lanes.value.flatMap((lane) => lane.points.filter((point) => point.item.derived && point.item.lower_bound !== null)))
const eventTicks = computed(() => props.showEvents ? props.detail.events.map((event) => {
  const match = observed.value.find((item) => item.quarter === event.fiscal_period)
  return match ? { id: event.event_id, x: x(match.period_index) } : null
}).filter((item): item is { id: string; x: number } => item !== null) : [])
</script>

<template>
  <svg
    class="tidal-band"
    :class="{ 'tidal-band--compact': compact }"
    :viewBox="`0 0 ${width} ${height}`"
    preserveAspectRatio="none"
    :aria-hidden="decorative ? 'true' : undefined"
    :role="decorative ? undefined : 'img'"
    :aria-label="decorative ? undefined : `${detail.identity.entity} normalized quarterly trajectory`"
  >
    <line class="tidal-band__baseline" x1="18" :y1="usableBottom" x2="982" :y2="usableBottom" />
    <g class="tidal-band__ticks">
      <line v-for="index in indices" :key="index" :x1="x(index)" :x2="x(index)" :y1="usableBottom - 3" :y2="usableBottom + 4" />
    </g>
    <g class="tidal-band__seams">
      <template v-for="seam in seams" :key="seam.id">
        <line :x1="seam.x - 3" :x2="seam.x - 3" y1="4" :y2="height - 3" />
        <line :x1="seam.x + 3" :x2="seam.x + 3" y1="4" :y2="height - 3" />
      </template>
    </g>
    <path v-for="lane in lanes" :key="lane.id" class="tidal-band__path" :class="`tidal-band__path--${lane.laneIndex + 1}`" :d="lane.path" />
    <g class="tidal-band__peaks">
      <path v-for="peak in peaks" :key="peak.item.observation_id" :d="`M${peak.x - 5},${peak.y - 4}H${peak.x + 5}`" />
    </g>
    <g class="tidal-band__derived">
      <template v-for="point in derived" :key="point.item.observation_id">
        <line :x1="point.x" :x2="point.x" :y1="point.y - 7" :y2="point.y + 7" />
        <line :x1="point.x - 4" :x2="point.x + 4" :y1="point.y - 7" :y2="point.y - 7" />
        <line :x1="point.x - 4" :x2="point.x + 4" :y1="point.y + 7" :y2="point.y + 7" />
        <rect :x="point.x - 3.5" :y="point.y - 3.5" width="7" height="7" :transform="`rotate(45 ${point.x} ${point.y})`" />
      </template>
    </g>
    <g class="tidal-band__events">
      <line v-for="event in eventTicks" :key="event.id" :x1="event.x" :x2="event.x" y1="1" y2="13" />
    </g>
  </svg>
</template>
