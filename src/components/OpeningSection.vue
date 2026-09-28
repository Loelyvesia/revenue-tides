<script setup lang="ts">
import type { ProjectMetadata } from '../types/webData'
defineProps<{ project: ProjectMetadata }>()
</script>

<template>
  <section id="opening" class="opening">
    <div class="shell opening-grid">
      <div class="opening-title">
        <p class="eyebrow">REVENUE TIDES / FISCAL-QUARTER RESEARCH</p>
        <h1>{{ project.title_zh }}</h1>
        <p class="title-en" lang="en">{{ project.title_en }}</p>
      </div>
      <div class="thesis">
        <p class="thesis-line">流水不是一个统一数字。</p>
        <p class="lede">同一个季度，报告口径、实体范围和证据方式都可能改变我们看到的数值。</p>
        <p class="annotation" lang="en">Publisher-defined fiscal-quarter observations, kept inside their own definitions.</p>
      </div>
      <div class="scope-line" aria-label="项目范围">
        <span><b class="numeric">{{ project.corpus_series_count }}</b> 条序列</span>
        <span><b class="numeric">{{ project.observation_count }}</b> 个观察</span>
        <span><b class="numeric">{{ project.companies.length }}</b> 家发行商</span>
        <span><b class="numeric">2024Q3—2026Q2</b> 财季窗口</span>
      </div>
      <aside class="opening-boundary">
        <span class="double-rule" aria-hidden="true"></span>
        <div><strong>比较边界</strong><p>不同公司的发行商定义收入指标不可直接比较绝对高低。</p><small lang="en">No global revenue leaderboard. Compare trajectories only under explicit compatible rules.</small></div>
      </aside>
      <a class="continue-link" href="#primer">继续：一个收入数字由什么构成？ ↓</a>
    </div>
  </section>
</template>

<style scoped>
.opening { min-height: min(920px, calc(100vh - 64px)); display: grid; align-items: center; padding-block: clamp(4rem, 10vw, 8rem); }
.opening-grid { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: clamp(2rem, 6vw, 6rem); }.title-en { margin-top: 0.65rem; color: var(--text-secondary); font-size: 1.05rem; }.thesis-line { margin: 0 0 1rem; font-size: clamp(1.8rem, 4vw, 3.4rem); line-height: 1.15; font-weight: 650; letter-spacing: -0.03em; }
.scope-line { grid-column: 1 / -1; display: flex; flex-wrap: wrap; gap: 1rem 2rem; padding-block: 1rem; border-block: 1px solid var(--rule-border); }.scope-line span { display: flex; gap: 0.5rem; align-items: baseline; }.scope-line b { font-size: 1.25rem; }
.opening-boundary { grid-column: 1 / -1; display: grid; grid-template-columns: 1rem 1fr; gap: 1rem; max-width: var(--reading-width); }.double-rule { border-inline: 2px solid var(--text-primary); }.opening-boundary p { margin: 0.25rem 0; }.opening-boundary small { color: var(--text-secondary); }.continue-link { grid-column: 1 / -1; justify-self: start; min-height: 44px; display: inline-flex; align-items: center; }
@media (max-width: 767px) { .opening-grid { grid-template-columns: 1fr; }.scope-line, .opening-boundary, .continue-link { grid-column: 1; }.scope-line { display: grid; grid-template-columns: 1fr 1fr; } }
@media (max-width: 390px) { .scope-line { grid-template-columns: 1fr; }.opening { min-height: auto; } }
</style>
