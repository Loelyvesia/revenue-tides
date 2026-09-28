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
      <div class="section-heading">
        <span class="section-index">06 / APPENDIX</span>
        <div class="section-copy"><p class="eyebrow">RESEARCH APPENDIX</p><h2>如何验证这些观察？</h2><p class="lede">方法、Finding 与网页数据各自有冻结版本；来源保持可追溯，事件与发行方解释不替代定量证据。</p></div>
      </div>
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
        <section>
          <h3>Evidence</h3>
          <p>官方披露与官方披露派生观察保持分层；所有派生值保留兼容区间。</p>
          <p class="numeric appendix-count">75 OBS · 26 EVENTS</p>
        </section>
        <section>
          <h3>Sources</h3>
          <p>每条 Finding 可追溯到观察、指标版本与公开文件。</p>
          <p class="numeric appendix-count">{{ manifest.source_count }} PUBLIC RECORDS</p>
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
.method-section { padding-bottom: 8rem; background: rgba(23,33,31,.035); }.method-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0 3rem; margin-block: 2rem; border-top: 2px solid var(--text-primary); }.method-grid > section { min-height: 14rem; padding-block: 1.5rem; border-bottom: 1px solid var(--rule-border); }.method-grid h3 { margin-bottom: 1rem; font-size: 1rem; text-transform: uppercase; letter-spacing: .04em; }.version-ledger { border-top: 1px solid var(--rule-grid); }.version-ledger div { display: grid; grid-template-columns: 7rem 1fr; gap: 1rem; padding-block: .55rem; border-bottom: 1px solid var(--rule-grid); }.version-ledger dd { margin: 0; overflow-wrap: anywhere; }.method-grid ul { padding-left: 1.25rem; }.appendix-count { margin-top: 2rem; color: var(--accent-primary); font-size: 1.15rem; }.all-sources { margin-top: 2rem; }.all-sources summary { min-height: 52px; display: flex; align-items: center; border-block: 1px solid var(--rule-border); cursor: pointer; font-weight: 650; }.notice { margin-top: 3rem; padding-top: 1rem; max-width: var(--reading-width); border-top: 1px solid var(--rule-border); color: var(--text-secondary); font-size: .875rem; }
@media (max-width: 767px) { .method-grid { grid-template-columns: 1fr; gap: 1rem; } }
</style>
