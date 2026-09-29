import { onBeforeUnmount, onMounted, ref, type Ref } from 'vue'

export interface ScrollyOptions {
  /** Root container element (holding both steps and the sticky visual) */
  container: Ref<HTMLElement | null>
  /** Number of narrative steps */
  stepCount: number
  /** Root margin for the intersection observer */
  rootMargin?: string
}

/**
 * Native IntersectionObserver-based scrolly orchestration.
 * Exactly one scroll system in the app (see reference_audit.md).
 * Returns the index of the step currently dominating the viewport.
 */
export function useScrolly(options: ScrollyOptions): { activeIndex: Ref<number> } {
  const activeIndex = ref(0)
  let observer: IntersectionObserver | null = null
  const { container, stepCount, rootMargin = '0px 0px -45% 0px' } = options

  function connect(): void {
    const root = container.value
    if (!root) return
    const steps: (HTMLElement | null)[] = []
    for (let i = 0; i < stepCount; i += 1) {
      steps.push(root.querySelector(`[data-scrolly-step="${i}"]`))
    }
    observer = new IntersectionObserver(
      (entries) => {
        // pick the entry with the largest intersectionRatio as the active step
        let best = -1
        let bestRatio = 0
        for (const entry of entries) {
          if (!entry.isIntersecting) continue
          const index = Number((entry.target as HTMLElement).dataset.scrollyStep)
          if (Number.isFinite(index) && entry.intersectionRatio > bestRatio) {
            best = index
            bestRatio = entry.intersectionRatio
          }
        }
        if (best >= 0) activeIndex.value = best
      },
      { rootMargin, threshold: [0.15, 0.4, 0.65] },
    )
    for (const step of steps) {
      if (step) observer.observe(step)
    }
  }

  onMounted(() => {
    // allow the layout to settle before observing
    requestAnimationFrame(() => connect())
  })
  onBeforeUnmount(() => observer?.disconnect())

  return { activeIndex }
}

export function prefersReducedMotion(): boolean {
  return typeof window !== 'undefined'
    && typeof window.matchMedia === 'function'
    && window.matchMedia('(prefers-reduced-motion: reduce)').matches
}