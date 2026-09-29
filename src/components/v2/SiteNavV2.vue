<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

const active = ref('opening')
const scrolled = ref(false)
const dark = ref(true)
const progress = ref(0)
let observer: IntersectionObserver | null = null
let raf = 0

function updateScroll(): void {
  if (raf) return
  raf = requestAnimationFrame(() => {
    raf = 0
    scrolled.value = window.scrollY > 24
    const max = document.documentElement.scrollHeight - window.innerHeight
    progress.value = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0
  })
}

onMounted(() => {
  updateScroll()
  window.addEventListener('scroll', updateScroll, { passive: true })
  observer = new IntersectionObserver((entries) => {
    const current = entries.filter((entry) => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0]
    if (!current?.target.id) return
    active.value = current.target.id
    dark.value = current.target.classList.contains('chapter--dark')
  }, { rootMargin: '-18% 0px -66% 0px', threshold: [0, .2, .6] })
  ;['opening', 'measurement', 'prism', 'headline-findings', 'observatory', 'research-notes', 'method'].forEach((id) => {
    const target = document.getElementById(id)
    if (target) observer?.observe(target)
  })
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', updateScroll)
  observer?.disconnect()
  if (raf) cancelAnimationFrame(raf)
})
</script>

<template>
  <div class="read-progress" :style="{ '--progress': progress }" aria-hidden="true" />
  <header class="site-nav" :class="{ 'is-scrolled': scrolled, 'site-nav--dark': dark && !scrolled }">
    <a class="site-nav__brand" href="#opening">REVENUE TIDES</a>
    <nav class="site-nav__links" aria-label="页面章节">
      <a href="#measurement" :aria-current="active === 'measurement' ? 'location' : undefined">I · NUMBER</a>
      <a href="#prism" :aria-current="active === 'prism' ? 'location' : undefined">II · PRISM</a>
      <a href="#headline-findings" :aria-current="active === 'headline-findings' ? 'location' : undefined">III · FINDINGS</a>
      <a href="#observatory" :aria-current="active === 'observatory' ? 'location' : undefined">IV · ARCHIVE</a>
    </nav>
  </header>
</template>
