# GitHub visual research — Bold Tidal Rebuild

Research date: 2026-09-29  
Scope: visual presentation only. Frozen research data and Finding semantics are not changed.

## Repositories inspected

| Repository | Material inspected beyond README | What is visually strong | Applicable pattern for Revenue Tides | What not to copy |
| --- | --- | --- | --- | --- |
| [hrbrmstr/streamgraph](https://github.com/hrbrmstr/streamgraph) @ `76f7173` | `example.png`; `inst/htmlwidgets/streamgraph.js`; SVG area construction, stack offset/order, hover opacity, markers and interpolation | A centered mass reads as one flowing object rather than nine unrelated lines. Layer thickness, negative/positive space and a shared temporal axis create rhythm. | Use nine **within-series normalized** ribbons around a common visual center in the Hero. Keep real quarter anchors visible and use the flow only as presentational geometry. | Do not stack publisher-defined absolute revenue. Do not port the R/htmlwidget implementation or treat a stream layer’s thickness as cross-company market share. |
| [plouc/nivo](https://github.com/plouc/nivo) @ `0dae2c3` | `packages/stream/src/hooks.ts`; `StreamLayer.tsx`; `packages/line/src/Areas.tsx`; line area generators; defs/gradient binding; animated path logic; responsive examples | Separating area mass, ridge, dots, interaction slices, defs and motion produces depth without sacrificing precise anchors. Path interpolation is handled as a rendering concern while points remain data objects. | Build each tide as a filled gradient area plus a luminous ridge and explicit quarter nodes. Use SVG defs, masks and short easing transitions; keep keyboard-visible controls outside the SVG. | Do not install React/Nivo or import its visual defaults. Do not let smooth paths create selectable intermediate observations. |
| [galiat/State-of-the-Union-Viz](https://github.com/galiat/State-of-the-Union-Viz) @ `4bf1afe` | `README-media/Screenshot.png`; `media/hashtagVolume.png`; `script.js`; stream demo; mouse/time scrub updating video, transcript, map and chart | One dominant streamgraph makes time the primary navigation surface. A single scrub coordinate synchronizes multiple evidence views and makes temporal focus immediate. | Treat the Quarter Prism aperture/ruler as a synchronized temporal focus: selected quarter, tide emphasis, reading output, events and sources update together. | Do not copy its dated chrome, video dependence, hard-coded dominant-topic logic or causal-looking synchronization. Events remain contextual only. |
| [Boring-Software-Inc/dither-kit](https://github.com/Boring-Software-Inc/dither-kit) @ `1e7faee` | live demo; `registry/dither-kit/area.tsx`; `cartesian-canvas.tsx`; `dither-paint.ts`; active dot, bloom and scrub logic | Textured fills, a bright ridge, restrained bloom and an active scrub column give a data area material character. The crisp layer and blurred bloom layer have separate responsibilities. | Add light SVG grain/dot texture to derived uncertainty and selected areas; duplicate only selected ridges into a soft filtered glow; use a luminous scrub column at the true selected quarter. | Do not copy pixel-art styling, Canvas engine, sparkles or React/Tailwind components. Texture must not obscure uncertainty bounds or become whole-site decoration. |
| [openai/plugins — build-web-data-visualization](https://github.com/openai/plugins/tree/main/plugins/build-web-data-visualization) @ `5fd93af` | data-visualization router; D3, scrollytelling, uncertainty, accessibility and testing skills; visual-design contract; mobile and meaning-preserving references | The strongest reusable principle is a semantic visual contract: renderer ownership, mobile sibling states, evidence-bearing motion, still-valid scenes, explicit reduced-motion and browser QA. | Keep SVG ownership inside Vue components, preserve raw anchors and non-color encodings, make mobile a composed state rather than a scaled desktop, and ensure every animation lands on a complete static frame. | Do not add WebGL, particles or decorative cinematic layers that cannot be tied to data, selection or uncertainty. The plugin is a process reference, not a runtime dependency. |

## Source-level observations

- `streamgraph.js` constructs closed SVG areas from explicit `y0` and `y1` boundaries, then dims non-hovered layers instead of replacing the chart with floating cards.
- Nivo’s stream implementation stores points and generated area paths separately. Its `StreamLayer` animates path geometry while slice/dot logic remains anchored to actual data positions.
- State-of-the-Union uses one time fraction to update the scrub bar and synchronized views. Revenue Tides can use the same interaction principle without adopting its video or causal framing.
- Dither Kit deliberately separates the crisp data canvas from an optional blurred bloom copy. Revenue Tides should likewise glow only selected/peak data energy, not every surface.
- OpenAI’s visualization guidance requires mobile recomposition, reduced-motion final states, accessible alternatives and motion that reveals sequence rather than inventing evidence.

## Patterns selected for implementation

### 1. Normalized central-axis tidal field

Hero uses nine ribbons generated from each series’ own normalized quarterly shape. The shared center is visual composition only; no absolute cross-company value or stack total is encoded.

### 2. Filled tide + precise ridge + visible anchors

The primary mark becomes a substantial area/ribbon. A bright ridge and real quarter nodes preserve the exact observation positions. Smooth geometry is explicitly presentational and never selectable between quarters.

### 3. Synchronized aperture scrub

Quarter Prism uses a single selected-quarter state to drive the luminous column, refracted lane(s), ruler, reading output, event context and source. Overlap and derived uncertainty receive different non-color shapes/patterns.

### 4. Layered material treatment

SVG gradient supplies volume; a low-opacity pattern supplies texture; a filtered duplicate supplies local glow. These layers are limited to data marks, selected states and Prism glass edges.

### 5. Evidence-bearing staged motion

Entrance reveals direction, surge, split or recovery. Quarter nodes remain fixed. Reduced motion shows the complete final state immediately. Every section remains legible as a still image.

## Patterns rejected

- Actual-value streamgraph stacking across companies or currencies.
- Continuous tooltips or values at visually interpolated positions.
- Whole-page glassmorphism, neon outlines or permanent bloom.
- Particle fields, Three.js and video backgrounds.
- Pixel-art UI or generic purple/blue SaaS gradients.
- Event-to-revenue connectors, arrows or animation timing that implies causality.
- React/Nivo/Dither Kit runtime dependencies; the implementation remains Vue + native SVG/CSS.

## Implementation contract

- Renderer: Vue-owned native SVG and CSS; no new visualization dependency.
- Instances: one Hero field, one Measurement morph, one Quarter Prism, three headline stages and nine archive mini-ribbons.
- Interaction: pointer/keyboard quarter selection only at real observations; tiny desktop-only Hero parallax; mobile disables parallax.
- Mobile: fewer Hero layers, full-width Prism, reading-first hierarchy, preserved filled tides and large figures.
- Motion: 400–1500 ms transforms/reveals, no bounce; `prefers-reduced-motion` removes path reveal, parallax, pulse, gradient drift and morphing.
- Accessibility: SVG summaries/labels, visible focus, non-color pattern/labels for version and derived states, minimum interactive hit area, static fallbacks.
- Truth boundary: normalization is within-series; smoothing is presentational; event markers are context; metric versions never stitch.

