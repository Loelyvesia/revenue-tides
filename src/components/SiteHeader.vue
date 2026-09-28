<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

const active = ref('opening')
let observer: IntersectionObserver | null = null

onMounted(() => {
  observer = new IntersectionObserver((entries) => {
    const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0]
    if (visible?.target.id) active.value = visible.target.id
  }, { rootMargin: '-18% 0px -70% 0px', threshold: [0, .15, .5] })
  ;['opening', 'prism', 'headline-findings', 'observatory', 'method'].forEach((id) => {
    const section = document.getElementById(id)
    if (section) observer?.observe(section)
  })
})

onBeforeUnmount(() => observer?.disconnect())
</script>

<template>
  <header class="site-header">
    <a class="wordmark" href="#opening"><span>付费潮汐</span><small>REVENUE TIDES</small></a>
    <nav aria-label="页面章节">
      <a href="#prism" :aria-current="active === 'prism' ? 'location' : undefined">PRISM</a>
      <a href="#headline-findings" :aria-current="active === 'headline-findings' ? 'location' : undefined">FINDINGS</a>
      <a href="#observatory" :aria-current="active === 'observatory' ? 'location' : undefined">SERIES</a>
      <a href="#method" :aria-current="active === 'method' ? 'location' : undefined">METHOD</a>
    </nav>
  </header>
</template>

<style scoped>
.site-header { position: sticky; z-index: 20; top: 0; display: flex; justify-content: space-between; align-items: center; gap: 1rem; min-height: 58px; padding: 0.45rem max(1.5rem, calc((100vw - var(--narrative-width)) / 2)); border-bottom: 1px solid rgba(86,94,89,.32); background: rgba(240, 237, 227, 0.94); backdrop-filter: blur(9px); }
.wordmark { display: grid; text-decoration: none; line-height: 1.15; }.wordmark span { font-weight: 650; }.wordmark small { font: 0.65rem var(--font-numeric); letter-spacing: 0.12em; }
nav { display: flex; gap: clamp(1rem, 2.5vw, 2rem); }nav a { position: relative; min-height: 44px; display: inline-flex; align-items: center; color: var(--text-secondary); font: 600 .7rem var(--font-numeric); letter-spacing: .08em; text-decoration: none; }nav a::after { content: ''; position: absolute; inset: auto 0 5px; border-top: 2px solid var(--accent-primary); transform: scaleX(0); transform-origin: left; transition: transform var(--motion-micro) ease-out; }nav a:hover, nav a[aria-current] { color: var(--text-primary); }nav a:hover::after, nav a[aria-current]::after { transform: scaleX(1); }
@media (max-width: 680px) { .site-header { padding-inline: 1rem; }.wordmark small { display: none; } nav { gap: .85rem; overflow-x: auto; }.site-header nav a { white-space: nowrap; font-size: .65rem; } }
@media (max-width: 360px) { nav a { letter-spacing: 0; } nav { gap: .7rem; } }
</style>
