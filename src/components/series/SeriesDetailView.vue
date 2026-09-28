<script setup lang="ts">
import type { Caveat, Finding, SeriesDetail, SourceRecord } from '../../types/webData'
import { resolveSources } from '../../utils/model'
import SourceList from '../evidence/SourceList.vue'
import EventRail from '../prism/EventRail.vue'
import TideStrip from './TideStrip.vue'

const props = defineProps<{
  detail: SeriesDetail
  findings: Finding[]
  sources: SourceRecord[]
  caveats: Caveat[]
}>()

function relatedFinding(id: string): Finding | undefined { return props.findings.find((finding) => finding.finding_id === id) }
function caveatText(id: string): string { return props.caveats.find((item) => item.caveat_id === id)?.text_zh ?? id }
</script>

<template>
  <article class="series-detail" :id="`series-${detail.series_id}`">
    <header>
      <div>
        <p class="eyebrow">SELECTED SERIES / VALIDATED</p>
        <h3>{{ detail.identity.entity }}</h3>
        <p>{{ detail.identity.company }} · {{ detail.identity.entity_type }} · {{ detail.identity.platform_scope }}</p>
      </div>
      <div class="finding-links">
        <a v-for="id in detail.findings" :key="id" :href="`#finding-${id}`">{{ id }} →</a>
      </div>
    </header>
    <TideStrip :detail="detail" />
    <div class="detail-grid">
      <details open>
        <summary>指标定义 · Metric versions</summary>
        <article v-for="metric in detail.metric_versions" :key="metric.metric_definition_id" class="metric-definition">
          <strong>{{ metric.version }} · {{ metric.label }}</strong>
          <p>{{ metric.economic_meaning }}</p>
          <p class="annotation">{{ metric.accounting_scope }} · {{ metric.comparison_scope }}</p>
          <p v-if="metric.version_break" class="version-warning">校准缝：{{ metric.version_break.break_reason }} 跨版本变化不可计算；新版本基线重启。</p>
        </article>
      </details>
      <details>
        <summary>相关 Findings</summary>
        <article v-for="id in detail.findings" :key="id">
          <strong>{{ id }} · {{ relatedFinding(id)?.title_zh }}</strong>
          <p>{{ relatedFinding(id)?.statement_zh }}</p>
        </article>
      </details>
      <details>
        <summary>事件与发行方说明</summary>
        <EventRail :events="detail.events" :claims="detail.attributed_claims" quarter="完整观察窗口" />
      </details>
      <details>
        <summary>来源与证据边界</summary>
        <SourceList :sources="resolveSources(detail.sources, sources)" />
        <ul class="caveat-list">
          <li v-for="id in detail.identity.caveat_ids" :key="id">{{ caveatText(id) }}</li>
        </ul>
      </details>
    </div>
  </article>
</template>

<style scoped>
.series-detail { margin-top: 2rem; padding: clamp(1.5rem, 4vw, 3rem) 0; border-block: 2px solid var(--text-primary); }
header { display: flex; justify-content: space-between; gap: 1rem; }
header p { margin: 0.35rem 0 0; }
.finding-links { display: flex; gap: 0.5rem; }
.finding-links a { min-width: 44px; min-height: 44px; display: inline-flex; align-items: center; justify-content: center; border-bottom: 1px solid var(--rule-border); text-decoration: none; }
.detail-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0 3rem; border-top: 1px solid var(--rule-border); }
details { border-bottom: 1px solid var(--rule-border); }
summary { display: flex; align-items: center; min-height: 52px; cursor: pointer; font-weight: 650; }
.metric-definition { padding-bottom: 1rem; }
.metric-definition p { margin: 0.25rem 0; }
.version-warning { padding-left: 0.75rem; border-left: 4px double var(--text-primary); }
.caveat-list { padding-left: 1.2rem; color: var(--text-secondary); }
@media (max-width: 767px) { header { display: block; } .detail-grid { grid-template-columns: 1fr; } }
</style>
