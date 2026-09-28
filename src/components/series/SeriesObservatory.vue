<script setup lang="ts">
import { ref } from 'vue'
import { useSeriesDetail } from '../../composables/useSeriesDetail'
import type { Caveat, Finding, SeriesIndexRecord, SourceRecord } from '../../types/webData'
import SeriesDetailView from './SeriesDetailView.vue'

defineProps<{
  series: SeriesIndexRecord[]
  findings: Finding[]
  sources: SourceRecord[]
  caveats: Caveat[]
}>()

const selectedId = ref<string | null>(null)
const { detail, state, error, load } = useSeriesDetail()

async function selectSeries(record: SeriesIndexRecord, force = false): Promise<void> {
  selectedId.value = record.series_id
  await load(record, force)
}
</script>

<template>
  <div class="observatory">
    <div class="ledger-head" aria-hidden="true">
      <span>序列</span><span>实体</span><span>发行商</span><span>证据</span><span>窗口</span><span>版本 / Findings</span>
    </div>
    <button v-for="record in series" :key="record.series_id" class="ledger-row" :aria-expanded="selectedId === record.series_id" @click="selectSeries(record)">
      <strong>{{ record.name }}</strong>
      <span><b class="mobile-label">实体 </b>{{ record.entity_type }}</span>
      <span><b class="mobile-label">发行商 </b>{{ record.company_name }}</span>
      <span><b class="evidence-shape" :class="record.evidence_mode === 'DERIVED_FROM_OFFICIAL' ? 'diamond' : 'circle'" aria-hidden="true"></b>{{ record.evidence_mode === 'OFFICIAL_REPORTED' ? 'Official' : 'Derived + interval' }}</span>
      <span class="numeric"><b class="mobile-label">窗口 </b>{{ record.first_period }}—{{ record.last_period }}</span>
      <span class="numeric"><b class="mobile-label">版本 / Findings </b>{{ record.metric_version_count }} · {{ record.finding_ids.join(' ') || '—' }}</span>
    </button>
    <div v-if="state === 'loading'" class="observatory-status" aria-live="polite">正在加载已验证序列…</div>
    <div v-else-if="state === 'error'" class="observatory-status error" role="alert">
      <strong>数据暂时无法加载</strong><p>{{ error }}</p>
      <button v-if="selectedId" class="native-control" @click="selectSeries(series.find((record) => record.series_id === selectedId)!, true)">重试</button>
      <a href="#method">查看方法</a>
    </div>
    <SeriesDetailView v-else-if="detail" :detail="detail" :findings="findings" :sources="sources" :caveats="caveats" />
  </div>
</template>

<style scoped>
.ledger-head, .ledger-row { display: grid; grid-template-columns: 1.5fr 0.7fr 0.9fr 1.1fr 1.2fr 1fr; gap: 1rem; align-items: center; }
.ledger-head { padding: 0.75rem 1rem; border-block: 2px solid var(--text-primary); font-size: 0.75rem; font-weight: 650; text-transform: uppercase; }
.ledger-row { width: 100%; min-height: 58px; padding: 0.75rem 1rem; border: 0; border-bottom: 1px solid var(--rule-border); color: inherit; background: transparent; text-align: left; cursor: pointer; }
.ledger-row:hover, .ledger-row[aria-expanded="true"] { background: var(--surface-secondary); }
.ledger-row span { font-size: 0.875rem; }
.evidence-shape { display: inline-block; width: 0.7rem; height: 0.7rem; margin-right: 0.4rem; background: var(--evidence-direct); }
.evidence-shape.circle { border-radius: 50%; }
.evidence-shape.diamond { border: 2px solid var(--evidence-derived); background: transparent; transform: rotate(45deg); }
.mobile-label { display: none; color: var(--text-secondary); font-weight: 500; }
.observatory-status { padding: 2rem; border-bottom: 1px solid var(--rule-border); }
.observatory-status.error { border-left: 3px solid var(--warning); }
.observatory-status a { margin-left: 1rem; }
@media (max-width: 900px) {
  .ledger-head { display: none; }
  .ledger-row { grid-template-columns: 1fr 1fr; gap: 0.35rem 1rem; padding-block: 1rem; }
  .ledger-row strong { grid-column: 1 / -1; }
  .mobile-label { display: inline; }
}
@media (max-width: 390px) { .ledger-row { grid-template-columns: 1fr; } .ledger-row strong { grid-column: auto; } }
</style>
