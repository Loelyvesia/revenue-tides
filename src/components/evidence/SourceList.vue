<script setup lang="ts">
import type { SourceRecord } from '../../types/webData'

defineProps<{
  sources: SourceRecord[]
  title?: string
}>()
</script>

<template>
  <section class="source-list" aria-label="证据来源">
    <h4>{{ title ?? '证据与来源' }}</h4>
    <p v-if="sources.length === 0" class="annotation">来源记录暂不可用；已保留当前观察的证据标识。</p>
    <dl v-for="source in sources" :key="source.source_id" class="source-record">
      <div><dt>公司</dt><dd>{{ source.company }}</dd></div>
      <div><dt>文件</dt><dd>{{ source.document_title ?? source.document_type }}</dd></div>
      <div><dt>报告期</dt><dd class="numeric">{{ source.reporting_period ?? '未标注' }}</dd></div>
      <div><dt>页码</dt><dd class="numeric">{{ source.source_pages.join('、') || '网页来源' }}</dd></div>
      <div class="source-link-row">
        <dt>公开链接</dt>
        <dd>
          <a :href="source.specific_document_url || source.canonical_url" target="_blank" rel="noopener noreferrer">
            打开原始披露 ↗
          </a>
        </dd>
      </div>
    </dl>
  </section>
</template>

<style scoped>
.source-list { padding: 1.25rem 1.5rem; border-left: 3px solid var(--data-teal); border-block: 1px solid var(--rule-dark); background: var(--surface-bg); color: var(--ink); }
h4 { margin: 0 0 0.75rem; font-size: 1rem; }
.source-record { margin: 0; padding: 0.75rem 0; border-top: 1px solid var(--rule-dark); }
.source-record div { display: grid; grid-template-columns: 5.5rem 1fr; gap: 0.75rem; }
dt { color: var(--ink-3); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; }
dd { margin: 0; font-size: 0.875rem; overflow-wrap: anywhere; }
.source-link-row { margin-top: 0.35rem; }
@media (max-width: 390px) { .source-list { padding: 1rem; }.source-record div { grid-template-columns: 4.5rem minmax(0,1fr); }.source-record dd { overflow-wrap: anywhere; } }
</style>
