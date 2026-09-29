# Reference Audit — Revenue Tides UI 2.0

Date: 2026-09-28
Branch: ui-rebuild-2.0
Purpose: Decide, per reference pattern, whether to adopt or reject before writing any UI code.

## Reference projects studied

| Ref | Project | Studied aspect |
|-----|---------|----------------|
| REF A | The Pudding (github.com/the-pudding/website) | Editorial data story, scrollytelling, narrative pacing, sticky visual + text, full-width graphic, mobile storytelling, typography hierarchy |
| REF B | Scrollama (github.com/russellsamora/scrollama) | Sticky graphic, scrolling steps, IntersectionObserver, responsive scrollytelling, progressive visual state changes, no scroll-jacking |
| REF C | Inspira UI (github.com/unovue/inspira-ui) | Refined Vue micro-interactions, text reveal, subtle background treatments, motion primitives |
| REF D | Vue Bits (github.com/DavidHDev/vue-bits) | Text reveal, subtle pointer response, section entrance, dynamic typography |
| REF E | Motion for Vue (github.com/motiondivision/motion-vue) | Layout transition, reveal, Prism motion, SVG animation, scroll-linked state |

## Pattern audit

| Reference pattern | Studied | Adopt | Reject | Reason |
|-------------------|:------:|:-----:|:------:|--------|
| Sticky scrollytelling (text steps + pinned visual) | yes | yes | | Editorial data stories read best when the visual stays pinned while prose advances; native IntersectionObserver gives this without dependencies |
| Text reveal (progressive line / word reveal) | yes | yes | | Low-cost, high-signal chapter feel; implemented with CSS only, not a library |
| Pinned visualization (Prism as sticky stage) | yes | yes | | Quarter Prism becomes a 100svh analytical stage; sticky positioning with scroll-linked quarter index |
| Smooth layout transitions (ledger row to detail pane) | yes | yes | | Vue transition + CSS transforms for Series Observatory detail swap |
| Progress indicator (reading progress) | yes | yes | | 2px top line, story progress only; static fallback under reduced motion |
| Background effects (subtle washes, spotlight) | yes | yes | | One soft radial spotlight per chapter surface; no beams, no aurora |
| Glass cards / glassmorphism | yes | | no | Conflicts with the paper/ledger editorial language; rejected |
| WebGL / Three.js | yes | | no | Data narrative must be the visual; no 3D dependency |
| Parallax | yes | | no | Adds motion cost without narrative value; hero transition uses opacity/translate only |
| Particles | yes | | no | Noise, not information; rejected everywhere |
| 3D / globe / meteor / marquee / dock | yes | | no | Component-showcase direction; rejected |
| Lenis smooth scroll | yes | | no | Native scroll preserved; no scroll-jacking |
| Scrollama dependency | yes | | no | Native IntersectionObserver covers sticky + step logic; avoids a second orchestration system |
| motion-vue dependency | yes | | no | CSS transitions + Vue Transition satisfy all planned motion; keeps JS bundle at target |
| Scroll-driven number crossfade | yes | yes | | Implemented with a scroll-progress computed + CSS transition on opacity |

## Dependency decision

- New JS dependencies: **0**
- New scroll helper: **0** (native IntersectionObserver + rAF-throttled scroll listener)
- Orchestration systems: exactly **1** (native IntersectionObserver)

## Motion vocabulary actually used (max 3 patterns)

1. Text reveal (chapter headlines: clip + translateY + opacity)
2. Sticky pinned stage (Prism, F1 split, Series pane) — scroll-linked state only, no scroll-jacking
3. Line reveal (SVG path draw for hero trajectories and F4 tidal sequence)

## Reduced motion

`prefers-reduced-motion: reduce` disables path drawing, large translate, and scroll-linked interpolation; all content order and visual states remain readable.