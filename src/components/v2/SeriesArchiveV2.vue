<script setup lang="ts">
import { computed, ref } from 'vue'
import { loadSeriesDetail } from '../../data/client'
import type { Caveat, Finding, Observation, SeriesDetail, SeriesIndexRecord, SourceRecord } from '../../types/webData'
import { formatKrwMillion, groupByQuarter, resolveSources } from '../../utils/model'
import SourceList from '../evidence/SourceList.vue'

const props = defineProps<{ series: SeriesIndexRecord[]; findings: Finding[]; sources: SourceRecord[]; caveats: Caveat[] }>()
const selectedId = ref(props.series[0]?.series_id ?? '')
const detail = ref<SeriesDetail | null>(null)
const loading = ref(false)
const error = ref(false)
const sourceOpen = ref(false)
const groups = computed(() => detail.value ? groupByQuarter(detail.value) : [])

async function select(record: SeriesIndexRecord, force = false): Promise<void> {
  selectedId.value = record.series_id; loading.value = true; error.value = false; sourceOpen.value = false
  try { detail.value = await loadSeriesDetail(record, force) } catch { error.value = true } finally { loading.value = false }
}
function barHeight(observation: Observation): number {
  const values = detail.value?.observations.filter((item): item is Observation & { value: number } => item.value !== null).map((item) => item.value) ?? []
  return observation.value === null ? 0 : 12 + observation.value / Math.max(...values, 1) * 48
}
function findingTitle(id: string): string { return props.findings.find((item) => item.finding_id === id)?.title_zh ?? id }
</script>

<template>
  <section id="observatory" class="chapter chapter--inklight archive" aria-labelledby="archive-title">
    <div class="shell shell--wide">
      <header class="chapter-head"><span class="eyebrow">ACT IV — THE ARCHIVE</span><h2 id="archive-title" class="display-chapter">Series Observatory / 序列观察站</h2><p class="lede">九条研究序列，不是收入榜单。左侧选择一条序列，右侧才按需读取它的完整观察。</p></header>
      <div class="archive-grid">
        <div class="archive-ledger" role="list" aria-label="九条分析序列">
          <button v-for="(record, index) in series" :key="record.series_id" class="ledger-row" :class="{ 'is-active': selectedId === record.series_id }" :aria-expanded="selectedId === record.series_id" @click="select(record)">
            <span class="ledger-row__no">{{ String(index + 1).padStart(2,'0') }}</span><strong class="ledger-row__name">{{ record.name }}</strong><span class="ledger-row__meta">{{ record.entity_type }} · {{ record.company_name }}</span><span class="ledger-row__meta">{{ record.first_period }}—{{ record.last_period }} · {{ record.evidence_mode === 'OFFICIAL_REPORTED' ? 'DIRECT' : 'DERIVED' }}</span>
          </button>
        </div>
        <aside class="archive-detail" aria-live="polite">
          <p v-if="!detail && !loading" class="archive-prompt">选择一条序列，打开完整观察记录。</p>
          <p v-else-if="loading">Loading validated series…</p>
          <div v-else-if="error" role="alert">数据加载失败。<button class="native-control" @click="select(series.find((item) => item.series_id === selectedId)!, true)">重试</button></div>
          <template v-else-if="detail">
            <p class="eyebrow">SELECTED SERIES</p><h3 class="headline-1">{{ detail.identity.entity }}</h3><p>{{ detail.identity.company }} · {{ detail.identity.entity_type }}</p><p class="caption">{{ detail.identity.platform_scope }}</p>
            <div class="tide-strip" aria-label="序列内季度轨迹">
              <template v-for="group in groups" :key="group.quarter"><span v-for="observation in group.observations" :key="observation.observation_id" class="tide-strip__bar" :class="{ 'tide-strip__bar--peak': observation.drawdown_percent === 0, 'tide-strip__bar--derived': observation.derived }" :style="{ height: `${barHeight(observation)}px` }" :title="`${observation.quarter} ${formatKrwMillion(observation.value)}`" /></template>
            </div>
            <div class="detail-line"><span class="detail-line__k">WINDOW</span><span>{{ groups[0]?.quarter }}—{{ groups.at(-1)?.quarter }}</span></div>
            <div class="detail-line"><span class="detail-line__k">VERSIONS</span><span>{{ detail.metric_versions.map((item) => item.version).join(' / ') }}</span></div>
            <div class="detail-line"><span class="detail-line__k">FINDINGS</span><span>{{ detail.findings.map((id) => `${id} · ${findingTitle(id)}`).join('；') || '—' }}</span></div>
            <details><summary>指标版本与比较边界</summary><article v-for="metric in detail.metric_versions" :key="metric.metric_definition_id" class="metric-card"><strong>{{ metric.version }}</strong><p>{{ metric.economic_meaning }}</p><p v-if="metric.version_break" class="caption">VERSION BREAK · baseline restarts · cross-version change forbidden</p></article></details>
            <div class="source-action"><button class="native-control" :aria-expanded="sourceOpen" @click="sourceOpen = !sourceOpen">{{ sourceOpen ? '收起来源' : '查看序列来源' }}</button><SourceList v-if="sourceOpen" :sources="resolveSources(detail.sources, sources)" /></div>
          </template>
        </aside>
      </div>
    </div>
  </section>
</template>
