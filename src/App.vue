<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { loadBootstrap, loadSources } from './data/client'
import type { BootstrapData, SourceRecord } from './types/webData'
import SiteNavV2 from './components/v2/SiteNavV2.vue'
import HeroV2 from './components/v2/HeroV2.vue'
import MeasurementStory from './components/v2/MeasurementStory.vue'
import QuarterPrismV2 from './components/v2/QuarterPrismV2.vue'
import HeadlineFindingsV2 from './components/v2/HeadlineFindingsV2.vue'
import SeriesArchiveV2 from './components/v2/SeriesArchiveV2.vue'
import ResearchNotesV2 from './components/v2/ResearchNotesV2.vue'
import ResearchAppendixV2 from './components/v2/ResearchAppendixV2.vue'

const data = ref<BootstrapData | null>(null)
const sources = ref<SourceRecord[]>([])
const state = ref<'loading' | 'ready' | 'error'>('loading')
const error = ref('')
let sourceObserver: IntersectionObserver | null = null
let hashTimer = 0

async function initialize(): Promise<void> {
  state.value = 'loading'; error.value = ''
  try {
    data.value = await loadBootstrap(); state.value = 'ready'; await nextTick()
    const target = document.getElementById('prism')
    if (!('IntersectionObserver' in window)) sources.value = await loadSources()
    else {
      sourceObserver = new IntersectionObserver((entries) => {
        if (entries.some((entry) => entry.isIntersecting)) { void loadSources().then((items) => { sources.value = items }); sourceObserver?.disconnect() }
      }, { rootMargin: '900px' })
      if (target) sourceObserver.observe(target)
    }
    if (location.hash) hashTimer = window.setTimeout(() => document.querySelector(location.hash)?.scrollIntoView({ block: 'start' }), 80)
  } catch (reason) { error.value = reason instanceof Error ? reason.message : 'Unknown data error'; state.value = 'error' }
}

onMounted(() => { void initialize() })
onBeforeUnmount(() => { sourceObserver?.disconnect(); window.clearTimeout(hashTimer) })
</script>

<template>
  <a class="skip-link" href="#main-content">跳到主要内容</a>
  <main v-if="state === 'loading'" id="main-content" class="boot chapter--dark" aria-live="polite"><p class="eyebrow">REVENUE TIDES</p><h1>正在读取冻结数据…</h1></main>
  <main v-else-if="state === 'error'" id="main-content" class="boot"><p class="eyebrow">DATA LOAD ERROR</p><h1>数据暂时无法加载</h1><p>{{ error }}</p><button class="native-control" @click="initialize">重试</button></main>
  <template v-else-if="data">
    <SiteNavV2 />
    <main id="main-content">
      <HeroV2 :series="data.series" />
      <MeasurementStory :series="data.series" />
      <QuarterPrismV2 :series="data.series" :sources="sources" :caveats="data.caveats" />
      <HeadlineFindingsV2 :findings="data.findings" :series="data.series" :sources="sources" />
      <SeriesArchiveV2 :series="data.series" :findings="data.findings" :sources="sources" :caveats="data.caveats" />
      <ResearchNotesV2 :findings="data.findings" :series="data.series" />
      <ResearchAppendixV2 :project="data.project" :manifest="data.manifest" :caveats="data.caveats" :sources="sources" />
    </main>
  </template>
</template>

<style scoped>
.boot { min-height: 100svh; display: grid; place-content: center; gap: 1rem; padding: 2rem; }.boot h1 { font-size: clamp(2rem, 5vw, 4rem); }
</style>
