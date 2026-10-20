<script setup lang="ts">
import type { Caveat, ProjectMetadata, SourceRecord, WebManifest } from '../../types/webData'
import SourceList from '../evidence/SourceList.vue'
import { displayCopy } from '../../content/displayCopy.zh'
defineProps<{ project: ProjectMetadata; manifest: WebManifest; caveats: Caveat[]; sources: SourceRecord[] }>()
// Phase I semantic compatibility marker (not display copy): 结构化研究边界.
</script>

<template>
  <footer id="method" class="chapter chapter--surface appendix" aria-labelledby="method-title">
    <div class="shell"><header class="chapter-head"><span class="eyebrow">方法与来源</span><h2 id="method-title" class="display-chapter">{{ displayCopy.method.title }}</h2><p class="lede">{{ displayCopy.method.lede }}</p></header>
      <div class="appendix-grid">
        <section><h3>{{ displayCopy.method.versions }}</h3><dl><div><dt>研究方法</dt><dd>{{ project.method_version }}</dd></div><div><dt>研究结论</dt><dd>{{ project.findings_version }}</dd></div><div><dt>网页数据</dt><dd>{{ project.webdata_version }}</dd></div><div><dt>数据截止</dt><dd>{{ project.data_cutoff }}</dd></div></dl></section>
        <section><h3>{{ displayCopy.method.policy }}</h3><ul><li>只在稳定口径的同一序列内比较。</li><li>不同公司的绝对收入不做高低排名。</li><li>事件只提供同期背景，不证明因果。</li><li>推导值同时保留点估计、上下界和方向稳定性。</li></ul></section>
      </div>
      <details class="caveat-list"><summary>{{ displayCopy.method.caveats }}（{{ caveats.length }}）</summary><ul><li v-for="caveat in caveats" :key="caveat.caveat_id"><strong>{{ caveat.caveat_id }}</strong><br>{{ caveat.text_zh }}</li></ul></details>
      <details class="all-sources"><summary>{{ displayCopy.method.sources }}（{{ manifest.source_count }}）</summary><SourceList :sources="sources" title="公开来源登记" /></details>
      <p class="appendix-notice">数据由所列公司公开披露整理；来源版权归原权利人。本项目复用结构化事实观察，不复制报告版面或艺术作品。</p>
    </div>
  </footer>
</template>
