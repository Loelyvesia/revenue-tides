<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { displayCopy } from '../../content/displayCopy.zh'

const active = ref('opening')
const scrolled = ref(false)
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
  <header class="site-nav" :class="{ 'is-scrolled': scrolled }">
    <a class="site-nav__brand" href="#opening">REVENUE TIDES</a>
    <nav class="site-nav__links" aria-label="页面章节">
      <a v-for="item in displayCopy.nav" :key="item.href" :href="item.href" :aria-current="active === item.href.slice(1) ? 'location' : undefined">{{ item.label }}</a>
    </nav>
  </header>
</template>
