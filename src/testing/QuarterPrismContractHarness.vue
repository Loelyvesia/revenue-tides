<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Caveat, SeriesDetail, SourceRecord } from '../types/webData'
import { groupByQuarter } from '../utils/model'

const props = defineProps<{ detail: SeriesDetail; sources: SourceRecord[]; caveats: Caveat[]; initialQuarter?: string }>()
const groups = computed(() => groupByQuarter(props.detail))
const selectedQuarter = ref(props.initialQuarter ?? groups.value[0]?.quarter ?? '')
const selected = computed(() => groups.value.find((item) => item.quarter === selectedQuarter.value) ?? groups.value[0])
const index = computed(() => groups.value.findIndex((item) => item.quarter === selectedQuarter.value))
function move(delta: number): void {
  const next = groups.value[Math.max(0, Math.min(groups.value.length - 1, index.value + delta))]
  if (next) selectedQuarter.value = next.quarter
}
</script>

<template>
  <section class="quarter-prism" tabindex="0" @keydown.left.prevent="move(-1)" @keydown.right.prevent="move(1)">
    <svg role="img" aria-labelledby="prism-title-contract"><title id="prism-title-contract">Quarter Prism contract</title></svg>
    <p aria-live="polite">{{ detail.identity.entity }} · {{ selected?.quarter }}</p>
    <div class="prism-controls"><button :disabled="index === 0" @click="move(-1)">Previous</button><button :disabled="index === groups.length - 1" @click="move(1)">Next</button></div>
    <select v-model="selectedQuarter" aria-label="直接选择季度"><option v-for="group in groups" :key="group.quarter" :value="group.quarter">{{ group.quarter }}</option></select>
    <div class="reading-pane"><h3>{{ selected?.quarter }}</h3><div v-for="observation in selected?.observations" :key="observation.observation_id" class="metric-lane">{{ observation.metric_version }}</div></div>
    <div class="quarter-list"><button v-for="group in groups" :key="group.quarter" @click="selectedQuarter = group.quarter">{{ group.quarter }}</button></div>
  </section>
</template>
