<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { loadSeriesDetail } from '../../data/client'
import type { Caveat, Finding, SeriesDetail, SeriesIndexRecord, SourceRecord } from '../../types/webData'
import { groupByQuarter, resolveSources } from '../../utils/model'
import SourceList from '../evidence/SourceList.vue'
import TidalBand from './TidalBand.vue'

const props = defineProps<{ series: SeriesIndexRecord[]; findings: Finding[]; sources: SourceRecord[]; caveats: Caveat[] }>()
const selectedId = ref(props.series[0]?.series_id ?? '')
const detail = ref<SeriesDetail | null>(null)
const fingerprints = ref<SeriesDetail[]>([])
const loading = ref(false)
const error = ref(false)
const sourceOpen = ref(false)
const groups = computed(() => detail.value ? groupByQuarter(detail.value) : [])

async function loadFingerprints(): Promise<void> {
  fingerprints.value = await Promise.all(props.series.map((record) => loadSeriesDetail(record)))
  if (!detail.value) detail.value = fingerprints.value.find((item) => item.series_id === selectedId.value) ?? null
}
async function select(record: SeriesIndexRecord, force = false): Promise<void> {
  selectedId.value = record.series_id; loading.value = true; error.value = false; sourceOpen.value = false
  try { detail.value = force ? await loadSeriesDetail(record, true) : fingerprints.value.find((item) => item.series_id === record.series_id) ?? await loadSeriesDetail(record) } catch { error.value = true } finally { loading.value = false }
}
function fingerprint(record: SeriesIndexRecord): SeriesDetail | null { return fingerprints.value.find((item) => item.series_id === record.series_id) ?? null }
function quarterLabel(value: string | undefined): string { return value ? value.replace(/(\d{4})Q(\d)/, '$1 Q$2') : '—' }
function findingTitle(id: string): string { return props.findings.find((item) => item.finding_id === id)?.title_zh ?? id }
onMounted(() => { void loadFingerprints() })
</script>

<template>
  <section id="observatory" class="chapter chapter--inklight archive observatory-signature" aria-labelledby="archive-title">
    <div class="shell shell--wide">
      <header class="chapter-head"><span class="eyebrow">ACT IV — THE ARCHIVE</span><h2 id="archive-title" class="display-chapter">Series Observatory / 序列观察站</h2><p class="lede">九条标准化轨迹指纹。它们描述序列内部形状，不构成收入排名。</p><p class="archive-comparability">NORMALIZED SHAPE · ABSOLUTE REVENUE IS NOT COMPARED</p></header>
      <div class="archive-grid">
        <div class="archive-ledger" role="list" aria-label="九条分析序列">
          <button v-for="(record, index) in series" :key="record.series_id" class="ledger-row fingerprint-row" :class="{ 'is-active': selectedId === record.series_id }" :aria-expanded="selectedId === record.series_id" @click="select(record)">
            <span class="ledger-row__mark" aria-hidden="true"/><span class="ledger-row__no">{{ String(index + 1).padStart(2,'0') }}</span>
            <span class="ledger-row__identity"><strong class="ledger-row__name">{{ record.name }}</strong><small>{{ record.entity_type }} · {{ record.company_name }}</small></span>
            <span class="fingerprint-cell">
              <TidalBand v-if="fingerprint(record)" :detail="fingerprint(record)!" compact decorative />
              <i v-else />
            </span>
            <span class="ledger-row__evidence">{{ record.evidence_mode === 'OFFICIAL_REPORTED' ? 'DIRECT' : 'DERIVED' }} · {{ record.quarter_count }}Q</span>
            <span class="ledger-row__arrow">→</span>
          </button>
        </div>
        <aside class="archive-detail" aria-live="polite">
          <p v-if="!detail && !loading" class="archive-prompt">选择一条序列，打开完整观察记录。</p>
          <p v-else-if="loading">Loading validated series…</p>
          <div v-else-if="error" role="alert">数据加载失败。<button class="native-control" @click="select(series.find((item) => item.series_id === selectedId)!, true)">重试</button></div>
          <template v-else-if="detail">
            <p class="eyebrow">SELECTED SERIES</p><h3 class="headline-1">{{ detail.identity.entity }}</h3><p>{{ detail.identity.company }} · {{ detail.identity.entity_type }}</p><p class="caption">{{ detail.identity.platform_scope }}</p>
            <div class="archive-detail__tide"><TidalBand :detail="detail" show-events /></div>
            <div class="detail-line"><span class="detail-line__k">WINDOW</span><span>{{ quarterLabel(groups[0]?.quarter) }}—{{ quarterLabel(groups.at(-1)?.quarter) }}</span></div>
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
