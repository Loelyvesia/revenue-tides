<script setup lang="ts">
import type { ProjectMetadata } from '../types/webData'
defineProps<{ project: ProjectMetadata }>()
</script>

<template>
  <section id="opening" class="opening">
    <div class="shell opening-grid">
      <div class="opening-title">
        <div class="cover-kicker"><span class="numeric">RT / 01</span><p class="eyebrow">FISCAL-QUARTER RESEARCH · 2024—2026</p></div>
        <h1>{{ project.title_zh }}</h1>
        <p class="title-en" lang="en">{{ project.title_en }}</p>
      </div>
      <div class="thesis">
        <span class="calibration-mark" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></span>
        <p class="thesis-line">流水不是一个统一数字。</p>
        <p class="lede">同一个季度，报告口径、实体范围和证据方式都可能改变我们看到的数值。</p>
        <p class="annotation" lang="en">Publisher-defined fiscal-quarter observations, kept inside their own definitions.</p>
      </div>
      <div class="scope-line" aria-label="项目范围">
        <p class="visually-hidden">{{ project.corpus_series_count }} 条序列 · {{ project.observation_count }} 个观察 · {{ project.companies.length }} 家发行商 · 2024Q3—2026Q2</p>
        <span><b class="numeric">0{{ project.corpus_series_count }}</b><small>SERIES / 序列</small></span>
        <span><b class="numeric">{{ project.observation_count }}</b><small>OBSERVATIONS / 观察</small></span>
        <span><b class="numeric">0{{ project.companies.length }}</b><small>PUBLISHERS / 发行商</small></span>
        <span><b class="numeric range">2024 Q3<br>— 2026 Q2</b><small>FISCAL WINDOW / 财季窗口</small></span>
      </div>
      <aside class="opening-boundary">
        <span class="double-rule" aria-hidden="true"></span>
        <div><strong>比较边界</strong><p>不同公司的发行商定义收入指标不可直接比较绝对高低。</p><small lang="en">No global revenue leaderboard. Compare trajectories only under explicit compatible rules.</small></div>
      </aside>
      <a class="continue-link" href="#primer"><span lang="en">READ THE QUARTER</span><small>进入季度观测</small><b aria-hidden="true">↓</b></a>
    </div>
  </section>
</template>

<style scoped>
.opening { min-height: min(960px, calc(100vh - 58px)); display: grid; align-items: center; padding-block: clamp(4rem, 8vw, 7.5rem); overflow: hidden; }
.opening-grid { position: relative; display: grid; grid-template-columns: minmax(0, 1.35fr) minmax(20rem, .65fr); gap: clamp(2.5rem, 7vw, 7rem); }
.opening-grid::after { content: ''; position: absolute; z-index: -1; top: -5rem; right: -14rem; width: 34rem; height: 34rem; border: 1px solid var(--rule-faint); border-radius: 50%; box-shadow: 0 0 0 4rem rgba(23,107,102,.018), 0 0 0 8rem rgba(23,107,102,.014); }
.cover-kicker { display: flex; gap: 1rem; align-items: center; margin-bottom: 1.5rem; }.cover-kicker > span { color: var(--accent-primary); font-size: .75rem; }.cover-kicker .eyebrow { margin: 0; }
.opening-title h1 { max-width: 12ch; font-size: clamp(4rem, 7.1vw, 5.5rem); line-height: 1.02; letter-spacing: -.065em; text-wrap: balance; }
.title-en { max-width: 34rem; margin-top: 1.25rem; color: var(--text-secondary); font-size: clamp(.95rem, 1.4vw, 1.15rem); letter-spacing: .015em; }
.thesis { align-self: end; padding-bottom: .5rem; }.thesis-line { max-width: 9ch; margin: 1.4rem 0 1.25rem; font-size: clamp(2.1rem, 4.3vw, 3.5rem); line-height: 1.08; font-weight: 660; letter-spacing: -0.05em; }.thesis .lede { font-size: 1.05rem; }.thesis .annotation { max-width: 28rem; }
.calibration-mark { display: flex; align-items: end; gap: .45rem; height: 1.6rem; color: var(--accent-primary); }.calibration-mark::before { content: ''; width: 5.5rem; border-top: 2px solid currentColor; }.calibration-mark i { display: block; height: .45rem; border-left: 1px solid currentColor; }.calibration-mark i:nth-child(3) { height: 1rem; }
.scope-line { grid-column: 1 / -1; display: grid; grid-template-columns: repeat(3, .72fr) 1.5fr; gap: 0; margin-top: 1rem; padding-block: 1.5rem; border-block: 1px solid var(--rule-border); }.scope-line span { display: grid; gap: .25rem; align-content: start; min-height: 5rem; padding-inline: 1.25rem; border-left: 1px solid var(--rule-grid); }.scope-line span:first-child { padding-left: 0; border-left: 0; }.scope-line b { font-size: clamp(1.8rem, 3vw, 2.7rem); line-height: 1; font-weight: 560; letter-spacing: -.04em; }.scope-line b.range { font-size: clamp(1.3rem, 2vw, 1.7rem); line-height: 1.15; }.scope-line small { color: var(--text-secondary); font: 600 .65rem/1.3 var(--font-numeric); letter-spacing: .08em; }
.opening-boundary { grid-column: 1; display: grid; grid-template-columns: 1rem 1fr; gap: 1rem; max-width: var(--reading-width); margin-top: .5rem; }.double-rule { border-inline: 2px solid var(--text-primary); }.opening-boundary p { margin: 0.25rem 0; }.opening-boundary small { color: var(--text-secondary); }
.continue-link { grid-column: 2; justify-self: end; align-self: end; min-height: 44px; display: grid; grid-template-columns: auto auto; gap: .1rem 1rem; align-items: center; text-decoration: none; font: 650 .78rem/1.2 var(--font-numeric); letter-spacing: .08em; }.continue-link small { grid-column: 1; color: var(--text-secondary); letter-spacing: 0; }.continue-link b { grid-column: 2; grid-row: 1 / span 2; font-size: 1.5rem; font-weight: 400; transition: transform var(--motion-micro) ease-out; }.continue-link:hover b { transform: translateY(2px); }
@media (max-width: 767px) { .opening { min-height: auto; padding-block: 3.5rem 4.5rem; }.opening-grid { grid-template-columns: 1fr; gap: 2.75rem; }.opening-grid::after { top: 7rem; right: -22rem; }.opening-title h1 { max-width: 11ch; font-size: clamp(2.8rem, 13.5vw, 3.4rem); line-height: 1.04; }.thesis { padding-top: 1.25rem; border-top: 1px solid var(--rule-border); }.thesis-line { font-size: clamp(2rem, 9vw, 2.7rem); }.scope-line, .opening-boundary, .continue-link { grid-column: 1; }.scope-line { grid-template-columns: 1fr 1fr; row-gap: 1.5rem; }.scope-line span:nth-child(3) { padding-left: 0; border-left: 0; }.continue-link { justify-self: start; }.cover-kicker { align-items: start; }.cover-kicker .eyebrow { max-width: 20rem; } }
@media (max-width: 390px) { .scope-line { grid-template-columns: 1fr 1fr; }.scope-line span { min-height: 4.25rem; padding-inline: .75rem; }.scope-line b { font-size: 1.7rem; }.scope-line b.range { font-size: 1.1rem; }.opening-title h1 { font-size: clamp(2.75rem, 13vw, 3.2rem); } }
</style>
