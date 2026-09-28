<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import type { Caveat, SeriesIndexRecord, SourceRecord } from '../../types/webData'
import { useSeriesDetail } from '../../composables/useSeriesDetail'
import QuarterPrism from './QuarterPrism.vue'

const props = defineProps<{
  series: SeriesIndexRecord[]
  sources: SourceRecord[]
  caveats: Caveat[]
}>()

const root = ref<HTMLElement | null>(null)
const requestedSeries = new URLSearchParams(window.location.search).get('series')
const requestedQuarter = new URLSearchParams(window.location.search).get('quarter') ?? undefined
const selectedId = ref(props.series.some((record) => record.series_id === requestedSeries) ? requestedSeries! : 'series_lineage_m')
const activated = ref(false)
const { detail, state, error, load } = useSeriesDetail()
let observer: IntersectionObserver | null = null

function selectedRecord(): SeriesIndexRecord | undefined {
  return props.series.find((record) => record.series_id === selectedId.value)
}

async function ensureLoaded(force = false): Promise<void> {
  const record = selectedRecord()
  if (!record) return
  activated.value = true
  await load(record, force)
}

watch(selectedId, () => {
  const url = new URL(window.location.href)
  url.searchParams.set('series', selectedId.value)
  url.hash = 'prism'
  window.history.replaceState(null, '', url)
  if (activated.value) void ensureLoaded()
})

onMounted(() => {
  if (!('IntersectionObserver' in window)) { void ensureLoaded(); return }
  observer = new IntersectionObserver((entries) => {
    if (entries.some((entry) => entry.isIntersecting)) {
      void ensureLoaded()
      observer?.disconnect()
    }
  }, { rootMargin: '300px' })
  if (root.value) observer.observe(root.value)
})

onBeforeUnmount(() => observer?.disconnect())
</script>

<template>
  <div ref="root" class="prism-shell">
    <div class="series-picker">
      <label for="prism-series"><span class="numeric">SERIES INPUT</span>选择一条发行商定义序列</label>
      <select id="prism-series" v-model="selectedId" class="native-control">
        <option v-for="record in series" :key="record.series_id" :value="record.series_id">
          {{ record.name }} · {{ record.entity_type }} · {{ record.company_name }}
        </option>
      </select>
      <p class="annotation">序列之间不提供绝对收入对比；棱镜只在当前序列内读取季度。</p>
    </div>
    <div v-if="state === 'idle' || state === 'loading'" class="loading-ledger" aria-live="polite">
      <span></span><span></span><span></span>
      <p>正在加载已验证序列… Loading validated series…</p>
    </div>
    <div v-else-if="state === 'error'" class="load-error" role="alert">
      <strong>数据暂时无法加载</strong>
      <p>{{ error }}</p>
      <button class="native-control" @click="ensureLoaded(true)">重试</button>
      <a href="#method">查看方法与来源</a>
    </div>
    <QuarterPrism v-else-if="detail" :detail="detail" :sources="sources" :caveats="caveats" :initial-quarter="requestedQuarter ?? (detail.series_id === 'series_lineage_m' ? '2025Q2' : undefined)" />
  </div>
</template>

<style scoped>
.prism-shell { position: relative; }
.series-picker { display: grid; grid-template-columns: minmax(16rem, 28rem) 1fr; gap: 0.4rem 2rem; align-items: end; margin-bottom: 1.75rem; padding-bottom: 1.25rem; border-bottom: 1px solid var(--rule-border); }
.series-picker > * { min-width: 0; }
.series-picker label { grid-column: 1; display: grid; gap: .3rem; font-weight: 650; }.series-picker label span { color: var(--text-secondary); font-size: .68rem; letter-spacing: .12em; }
.series-picker select { grid-column: 1; width: 100%; max-width: 100%; }
.series-picker p { grid-column: 2; grid-row: 2; margin: 0; }
.loading-ledger { padding: 5rem 1rem; border-block: 1px solid var(--rule-border); }
.loading-ledger span { display: block; height: 1px; margin-block: 1rem; background: var(--rule-grid); }
.load-error { padding: 2rem; border: 2px solid var(--warning); background: var(--surface-primary); }
.load-error a { margin-left: 1rem; }
@media (max-width: 767px) {
  .series-picker { grid-template-columns: 1fr; }
  .series-picker label, .series-picker select, .series-picker p { grid-column: 1; grid-row: auto; }
}
</style>
