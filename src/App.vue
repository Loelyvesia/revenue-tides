<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { loadBootstrap, loadSources } from './data/client'
import type { BootstrapData, SourceRecord } from './types/webData'
import SiteHeader from './components/SiteHeader.vue'
import OpeningSection from './components/OpeningSection.vue'
import MeasurementPrimer from './components/MeasurementPrimer.vue'
import QuarterPrismShell from './components/prism/QuarterPrismShell.vue'
import FindingChapter from './components/findings/FindingChapter.vue'
import SeriesObservatory from './components/series/SeriesObservatory.vue'
import MethodSources from './components/MethodSources.vue'

const data = ref<BootstrapData | null>(null)
const sources = ref<SourceRecord[]>([])
const state = ref<'loading' | 'ready' | 'error'>('loading')
const error = ref<string | null>(null)
const prismSection = ref<HTMLElement | null>(null)
let sourceObserver: IntersectionObserver | null = null
let hashScrollTimer: number | null = null

const headlineFindings = computed(() => data.value?.findings.filter((finding) => finding.headline) ?? [])
const remainingFindings = computed(() => data.value?.findings.filter((finding) => !finding.headline) ?? [])

async function initialize(): Promise<void> {
  state.value = 'loading'
  error.value = null
  try {
    data.value = await loadBootstrap()
    state.value = 'ready'
    await nextTick()
    if (window.location.hash) {
      const scrollToHash = () => document.querySelector(window.location.hash)?.scrollIntoView({ block: 'start' })
      scrollToHash()
      hashScrollTimer = window.setTimeout(scrollToHash, 900)
    }
    if (!('IntersectionObserver' in window)) sources.value = await loadSources()
    else {
      sourceObserver = new IntersectionObserver((entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          void loadSources().then((loaded) => { sources.value = loaded })
          sourceObserver?.disconnect()
        }
      }, { rootMargin: '400px' })
      if (prismSection.value) sourceObserver.observe(prismSection.value)
    }
  } catch (reason) {
    error.value = reason instanceof Error ? reason.message : 'Unknown application loading error'
    state.value = 'error'
  }
}

onMounted(() => { void initialize() })
onBeforeUnmount(() => {
  sourceObserver?.disconnect()
  if (hashScrollTimer !== null) window.clearTimeout(hashScrollTimer)
})
</script>

<template>
  <a class="skip-link" href="#main-content">跳到主要内容</a>
  <div v-if="state === 'loading'" class="boot-state" aria-live="polite">
    <p class="eyebrow">REVENUE TIDES</p>
    <h1>正在读取冻结数据…</h1>
    <div><span></span><span></span><span></span></div>
  </div>
  <main v-else-if="state === 'error'" id="main-content" class="boot-state error-state">
    <p class="eyebrow">DATA LOAD ERROR</p>
    <h1>数据暂时无法加载</h1>
    <p>{{ error }}</p>
    <button class="native-control" @click="initialize">重试</button>
  </main>
  <template v-else-if="data">
    <SiteHeader />
    <main id="main-content">
      <OpeningSection :project="data.project" />
      <MeasurementPrimer />
      <section id="prism" ref="prismSection" class="section prism-section">
        <div class="analytical-shell">
          <p class="eyebrow">S2 / SIGNATURE INTERACTION</p>
          <h2>Quarter Prism / 季度棱镜</h2>
          <p class="lede">移动一个财政季度，观察数值如何由实体、口径、证据、区间、事件与来源共同构成。</p>
          <QuarterPrismShell :series="data.series" :sources="sources" :caveats="data.caveats" />
        </div>
      </section>
      <section id="headline-findings" class="section findings-section">
        <div class="shell">
          <p class="eyebrow">S3 / HEADLINE FINDINGS</p>
          <h2>三个核心证据章节</h2>
          <FindingChapter v-for="finding in headlineFindings" :key="finding.finding_id" :finding="finding" :series="data.series" :sources="sources" />
        </div>
      </section>
      <section id="observatory" class="section observatory-section">
        <div class="analytical-shell">
          <p class="eyebrow">S4 / SERIES OBSERVATORY</p>
          <h2>九条被报告的商业轨迹</h2>
          <p class="lede">研究顺序，不是收入排名。选择一行后才按需读取该序列的完整季度数据。</p>
          <SeriesObservatory :series="data.series" :findings="data.findings" :sources="sources" :caveats="data.caveats" />
        </div>
      </section>
      <section id="remaining-findings" class="section remaining-section">
        <div class="shell">
          <p class="eyebrow">S5 / REMAINING FINDINGS</p>
          <h2>恢复、口径窗口与不确定性</h2>
          <FindingChapter v-for="finding in remainingFindings" :key="finding.finding_id" :finding="finding" :series="data.series" :sources="sources" compact />
        </div>
      </section>
      <MethodSources :project="data.project" :manifest="data.manifest" :caveats="data.caveats" :sources="sources" />
    </main>
  </template>
</template>

<style scoped>
.boot-state { min-height: 100vh; display: grid; place-content: center; width: min(calc(100% - 2rem), 42rem); margin: auto; }.boot-state div { margin-top: 2rem; }.boot-state div span { display: block; width: min(32rem, 80vw); height: 1px; margin-block: 1rem; background: var(--rule-border); }.error-state { border-left: 4px solid var(--warning); padding-left: 2rem; }.prism-section { background: rgba(232, 227, 214, .4); }.findings-section { border-top-width: 2px; }.observatory-section { background: rgba(251, 249, 242, .58); }.remaining-section { border-top-width: 2px; }
</style>
