<script setup lang="ts">
import { computed } from 'vue'
import type { Observation, SeriesDetail } from '../../types/webData'
import { ribbonPath, smoothPath } from '../../utils/tidalGeometry'

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
  const geometry = points.map(({ x: px, y: py }) => ({ x: px, y: py }))
  return {
    id: metric.metric_definition_id,
    version: metric.version,
    laneIndex,
    points,
    path: smoothPath(geometry),
    bandPath: ribbonPath(geometry, props.compact ? 3.8 : 7.5),
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

const svgId = computed(() => props.detail.series_id.replace(/[^a-z0-9_-]/gi, '-'))
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
    <defs>
      <linearGradient :id="`${svgId}-tide-1`" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stop-color="#168b8d" stop-opacity=".28" />
        <stop offset=".52" stop-color="#24a8a0" stop-opacity=".76" />
        <stop offset="1" stop-color="#7de2cc" stop-opacity=".34" />
      </linearGradient>
      <linearGradient :id="`${svgId}-tide-2`" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stop-color="#a95d3b" stop-opacity=".22" />
        <stop offset=".55" stop-color="#ee8d64" stop-opacity=".68" />
        <stop offset="1" stop-color="#ffc09f" stop-opacity=".3" />
      </linearGradient>
      <pattern :id="`${svgId}-derived`" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(25)">
        <line x1="0" y1="0" x2="0" y2="7" stroke="#8f75c9" stroke-width="1" opacity=".55" />
      </pattern>
      <filter :id="`${svgId}-glow`" x="-20%" y="-80%" width="140%" height="260%">
        <feGaussianBlur stdDeviation="3" result="blur" />
      </filter>
    </defs>
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
    <g v-for="lane in lanes" :key="lane.id" class="tidal-band__lane" :class="`tidal-band__lane--${lane.laneIndex + 1}`">
      <path class="tidal-band__bloom" :d="lane.path" :stroke="lane.laneIndex ? '#ee8d64' : '#24a8a0'" :filter="`url(#${svgId}-glow)`" />
      <path class="tidal-band__area" :class="`tidal-band__area--${lane.laneIndex + 1}`" :d="lane.bandPath" :fill="`url(#${svgId}-tide-${Math.min(lane.laneIndex + 1, 2)})`" />
      <path class="tidal-band__path" :class="`tidal-band__path--${lane.laneIndex + 1}`" :d="lane.path" />
      <g class="tidal-band__nodes">
        <circle v-for="point in lane.points" :key="`${point.item.observation_id}-node`" :cx="point.x" :cy="point.y" :r="compact ? 1.5 : 2.6" />
      </g>
    </g>
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
