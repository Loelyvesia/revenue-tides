<script setup lang="ts">
import type { Caveat, ProjectMetadata, SourceRecord, WebManifest } from '../types/webData'
import SourceList from './evidence/SourceList.vue'
import CaveatKey from './evidence/CaveatKey.vue'

defineProps<{
  project: ProjectMetadata
  manifest: WebManifest
  caveats: Caveat[]
  sources: SourceRecord[]
}>()
</script>

<template>
  <section id="method" class="section method-section">
    <div class="shell">
      <p class="eyebrow">S6 / METHOD · EVIDENCE · SOURCES</p>
      <h2>如何验证这些观察？</h2>
      <p class="lede">方法、Finding 与网页数据各自有冻结版本；来源保持可追溯，事件与发行方解释不替代定量证据。</p>
      <div class="method-grid">
        <section>
          <h3>Version ledger</h3>
          <dl class="version-ledger">
            <div><dt>Method</dt><dd class="numeric">{{ project.method_version }}</dd></div>
            <div><dt>Findings</dt><dd class="numeric">{{ project.findings_version }}</dd></div>
            <div><dt>Web data</dt><dd class="numeric">{{ project.webdata_version }}</dd></div>
            <div><dt>Data cutoff</dt><dd class="numeric">{{ project.data_cutoff }}</dd></div>
            <div><dt>Temporal unit</dt><dd>{{ project.primary_temporal_unit }}</dd></div>
          </dl>
        </section>
        <section>
          <h3>Comparison & causality</h3>
          <ul>
            <li>只在稳定口径的同一序列内部比较。</li>
            <li>跨公司绝对水平不可比较。</li>
            <li>事件时间只提供同期语境，不建立因果。</li>
            <li>派生值必须保留点估计、区间与方向稳定性。</li>
          </ul>
        </section>
      </div>
      <CaveatKey :caveats="caveats" />
      <details class="all-sources">
        <summary>打开完整公共来源登记（{{ manifest.source_count }} 条）</summary>
        <SourceList :sources="sources" title="公共来源登记" />
      </details>
      <p class="notice">数据由所列公司公开披露整理；来源版权归原权利人。本项目复用结构化事实观察，不复制报告版面或艺术作品。</p>
    </div>
  </section>
</template>

<style scoped>
.method-section { padding-bottom: 8rem; }.method-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 3rem; margin-block: 2rem; }.version-ledger { border-top: 2px solid var(--text-primary); }.version-ledger div { display: grid; grid-template-columns: 7rem 1fr; gap: 1rem; padding-block: .65rem; border-bottom: 1px solid var(--rule-border); }.version-ledger dd { margin: 0; overflow-wrap: anywhere; }.method-grid ul { padding-left: 1.25rem; }.all-sources { margin-top: 2rem; }.all-sources summary { min-height: 52px; display: flex; align-items: center; border-block: 1px solid var(--rule-border); cursor: pointer; font-weight: 650; }.notice { margin-top: 2rem; max-width: var(--reading-width); color: var(--text-secondary); font-size: .875rem; }
@media (max-width: 767px) { .method-grid { grid-template-columns: 1fr; gap: 1rem; } }
</style>
