<script setup lang="ts">
import type { Caveat, ProjectMetadata, SourceRecord, WebManifest } from '../../types/webData'
import SourceList from '../evidence/SourceList.vue'
defineProps<{ project: ProjectMetadata; manifest: WebManifest; caveats: Caveat[]; sources: SourceRecord[] }>()
</script>

<template>
  <footer id="method" class="chapter chapter--dark appendix" aria-labelledby="method-title">
    <div class="shell"><header class="chapter-head"><span class="eyebrow">RESEARCH APPENDIX</span><h2 id="method-title" class="display-chapter">方法、边界与来源</h2><p class="lede">浏览器只负责呈现；计算、可比性与 Finding 均由冻结研究流水线决定。</p></header>
      <div class="appendix-grid">
        <section><h3>Frozen versions</h3><dl><div><dt>Method</dt><dd>{{ project.method_version }}</dd></div><div><dt>Findings</dt><dd>{{ project.findings_version }}</dd></div><div><dt>Web data</dt><dd>{{ project.webdata_version }}</dd></div><div><dt>Cutoff</dt><dd>{{ project.data_cutoff }}</dd></div></dl></section>
        <section><h3>Comparison policy</h3><ul><li>只在稳定口径的同一序列内比较。</li><li>跨公司绝对收入不可比较。</li><li>事件是同期语境，不证明因果。</li><li>派生值保留点估计、区间和方向稳定性。</li></ul></section>
      </div>
      <details class="caveat-list"><summary>结构化研究边界（{{ caveats.length }}）</summary><ul><li v-for="caveat in caveats" :key="caveat.caveat_id"><strong>{{ caveat.caveat_id }}</strong><br>{{ caveat.text_zh }}</li></ul></details>
      <details class="all-sources"><summary>公共来源登记（{{ manifest.source_count }}）</summary><SourceList :sources="sources" title="PUBLIC SOURCE REGISTRY" /></details>
      <p class="appendix-notice">数据由所列公司公开披露整理；来源版权归原权利人。本项目复用结构化事实观察，不复制报告版面或艺术作品。</p>
    </div>
  </footer>
</template>
