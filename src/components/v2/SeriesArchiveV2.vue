<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { loadSeriesDetail } from '../../data/client'
import type { Caveat, Finding, SeriesDetail, SeriesIndexRecord, SourceRecord } from '../../types/webData'
import { groupByQuarter, resolveSources } from '../../utils/model'
import SourceList from '../evidence/SourceList.vue'
import TidalBand from './TidalBand.vue'
import { displayCopy } from '../../content/displayCopy.zh'

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
      <header class="chapter-head"><span class="eyebrow">序列总览</span><h2 id="archive-title" class="display-chapter">{{ displayCopy.archive.title }}</h2><p class="lede">{{ displayCopy.archive.lede }}</p></header>
      <div class="archive-grid">
        <div class="archive-ledger" role="list" aria-label="九条分析序列">
          <button v-for="(record, index) in series" :key="record.series_id" class="ledger-row fingerprint-row" :class="{ 'is-active': selectedId === record.series_id }" :aria-expanded="selectedId === record.series_id" @click="select(record)">
            <span class="ledger-row__no">{{ String(index + 1).padStart(2,'0') }}</span>
            <span class="ledger-row__identity"><strong class="ledger-row__name">{{ record.name }}</strong><small>{{ record.company_name }} · {{ record.entity_type === 'IP' ? 'IP 汇总' : '单款游戏' }}</small></span>
            <span class="fingerprint-cell">
              <TidalBand v-if="fingerprint(record)" :detail="fingerprint(record)!" compact decorative />
              <i v-else />
            </span>
            <span class="ledger-row__evidence">{{ record.evidence_mode === 'OFFICIAL_REPORTED' ? '官方披露' : '推导值' }} · {{ record.quarter_count }} 季</span>
            <span class="ledger-row__arrow">→</span>
          </button>
        </div>
        <aside class="archive-detail" aria-live="polite">
          <p v-if="!detail && !loading" class="archive-prompt">选择一条序列，打开完整观察记录。</p>
          <p v-else-if="loading">正在读取序列…</p>
          <div v-else-if="error" role="alert">数据加载失败。<button class="native-control" @click="select(series.find((item) => item.series_id === selectedId)!, true)">重试</button></div>
          <template v-else-if="detail">
            <p class="eyebrow">{{ displayCopy.archive.selected }}</p><h3 class="headline-1">{{ detail.identity.entity }}</h3><p>{{ detail.identity.company }} · {{ detail.identity.entity_type === 'IP' ? 'IP 汇总' : '单款游戏' }}</p><p class="caption">{{ detail.identity.platform_scope }}</p>
            <div class="archive-detail__tide"><TidalBand :detail="detail" show-events /></div>
            <div class="detail-line"><span class="detail-line__k">{{ displayCopy.archive.window }}</span><span>{{ quarterLabel(groups[0]?.quarter) }}—{{ quarterLabel(groups.at(-1)?.quarter) }}</span></div>
            <div class="detail-line"><span class="detail-line__k">{{ displayCopy.archive.versions }}</span><span>{{ detail.metric_versions.map((item) => item.version).join(' / ') }}</span></div>
            <div class="detail-line"><span class="detail-line__k">{{ displayCopy.archive.findings }}</span><span>{{ detail.findings.map((id) => `${id} · ${findingTitle(id)}`).join('；') || '—' }}</span></div>
            <details><summary>查看指标口径</summary><article v-for="metric in detail.metric_versions" :key="metric.metric_definition_id" class="metric-card"><strong>{{ metric.version }}</strong><p>{{ metric.economic_meaning }}</p><p v-if="metric.version_break" class="caption">此处口径发生变化，基线重新计算，前后不做环比。</p></article></details>
            <div class="source-action"><button class="native-control" :aria-expanded="sourceOpen" @click="sourceOpen = !sourceOpen">{{ sourceOpen ? '收起来源' : '查看序列来源' }}</button><SourceList v-if="sourceOpen" :sources="resolveSources(detail.sources, sources)" /></div>
          </template>
        </aside>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* UI 2.4: selection is shown through depth and type weight, never lateral motion. */
.ledger-row.is-active{transform:none}
.ledger-row.is-active .ledger-row__name{font-weight:790;color:var(--petrol)}
.ledger-row.is-active .fingerprint-cell{height:6.15rem;opacity:1}
.archive-detail{min-height:62vh}
.archive-detail h3{margin:.25rem 0}
.archive-detail__tide{height:14rem;margin:.8rem -1.4rem .35rem}
.detail-line{padding-block:.42rem}
.archive-detail details{margin-top:.65rem}
@media(max-width:640px){
  .fingerprint-row{min-height:5.35rem;grid-template-rows:auto 3.65rem;padding-block:.35rem}
  .fingerprint-row.is-active{min-height:6.2rem}
  .fingerprint-cell{height:3.55rem}
  .ledger-row.is-active .fingerprint-cell{height:4.35rem}
  .archive-detail__tide{height:7.7rem;margin:.65rem -.45rem .25rem}
}
</style>
