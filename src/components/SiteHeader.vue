<template>
  <header class="site-header">
    <a class="wordmark" href="#opening"><span>付费潮汐</span><small>REVENUE TIDES</small></a>
    <nav aria-label="页面章节">
      <a href="#opening">命题</a>
      <a href="#prism">棱镜</a>
      <a href="#headline-findings">Findings</a>
      <a href="#observatory">序列</a>
      <a href="#method">方法</a>
    </nav>
  </header>
</template>

<style scoped>
.site-header { position: sticky; z-index: 20; top: 0; display: flex; justify-content: space-between; align-items: center; gap: 1rem; min-height: 64px; padding: 0.6rem max(1.5rem, calc((100vw - var(--narrative-width)) / 2)); border-bottom: 1px solid var(--rule-border); background: rgba(243, 240, 231, 0.94); backdrop-filter: blur(8px); }
.wordmark { display: grid; text-decoration: none; line-height: 1.15; }.wordmark span { font-weight: 650; }.wordmark small { font: 0.65rem var(--font-numeric); letter-spacing: 0.12em; }
nav { display: flex; gap: clamp(0.75rem, 2vw, 1.5rem); }nav a { min-height: 44px; display: inline-flex; align-items: center; font-size: 0.875rem; text-decoration-thickness: 1px; }
@media (max-width: 680px) { .site-header { align-items: start; padding-inline: 1rem; }.wordmark small { display: none; } nav { overflow-x: auto; }.site-header nav a { white-space: nowrap; } }
</style>
