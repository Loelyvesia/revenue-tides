# UI 2.4 FINAL REVIEW FIX

2026-10-08. Scope: final presentation/access fixes only. No UI 2.5 or deployment.

## Root causes and repairs

Mobile F4 had actual layout clipping, not just an unfinished animation: an inherited 42rem minimum SVG width combined with 112% width and negative margins. Mobile now uses min-width:0, width/max-width:100% and zero lateral negative margins. ViewBox and curve anchors are unchanged. Four normal-flow readings reinforce 2024Q4 69.2 → 2025Q2 54.9 → 2025Q3 79.5 → 2026Q2 55.0 (billion KRW), plus the first drawdown, three-quarter recovery/new high and second drawdown. No permanent non-recovery claim is added.

Chrome measured after reveal: at 390px SVG x=16–374, last value x=339.10–353.15; at 320px SVG x=16–304, last value x=275.93–287.02. Band opacity=1 in both. All four readings and the second drawdown fit.

Mobile Prism keeps 121.111/127.908 in two columns. Its formerly clipped absolute event text now wraps in normal flow below the graphic, followed by the source button. Non-causal context is explicit. Event bounds: x=16–374 at 390px, x=16–304 at 320px; no text overflow. Source target is 40px high and opens original-disclosure links in all three browsers. Testing found an async mount race in source loading: if the parent queried Prism before its component mounted, no observer target was bound. A fallback now loads the existing public registry when that target is absent; source records are unchanged.

F2: 65.719 is primary, 7.012 is comparison, +837.3% is a smaller opaque left-side QoQ note. PC launch occupies a separate context rail outside the graph; the orange peak-adjacent event halo is removed. Causal wording is unchanged.

Measurement: desktop-only leading padding/visual alignment/header spacing adjustments bring explanations and tide closer. Chapter/step heights and scrollytelling remain unchanged. Labels were inspected at 390/320px. F4 readable document-flow labels supplement small graphic annotations; Prism version/event text wraps. No extra glow was added.

## Frozen integrity

Method/Findings/Web Data unchanged, confirmed by hash validators and clean Git status for frozen directories. Counts: 9 series, 75 observations, 26 events, 18 derived observations, F1–F6; headlines F1/F2/F4. Versions, uncertainty, sources, currencies and quarters preserved. No new dependency/chart type.

Original Phase G validator remains unchanged and reports **89/90 PASS**. All 89 data/provenance checks pass. Its remaining rule requires Phase H not to exist, which is historical after authorized later phases:

`HISTORICAL_STOP_BOUNDARY — NOT_APPLICABLE_AFTER_AUTHORIZED_PHASES`

Current audit: **89/89 data and provenance checks PASS; 1 historical phase-boundary check NOT APPLICABLE**. No fabricated 90/90 or frozen-rule edit.

## Verification

- TypeScript/build PASS; Vitest 62/62 PASS.
- UI 2.2 27/27; UI 2.3 36/36; UI 2.4 38/38 PASS.
- Phase I 100/100; Phase J 102/102 PASS. Their historical browser evidence remains historical; current evidence is the UI 2.4 browser reports.
- Current Chrome/Edge cover 1440×900, 1280×800, 1024×768, 768×1024, 390×844, 320×700; mobile F4 bounds/four labels, overlap layout, event wrapping, source expansion, keyboard ArrowRight and reduced-motion behavior.
- Current Firefox covers 1440×900, 1280×800, 390×844, 320×700; mobile F4/event/source operation, overlap/derived/event semantics, safe external links.
- Current browser totals: Chrome 24/24, Edge 24/24, Firefox 20/20 PASS. Chromium reduced-motion checks verify tidal reveal/refraction transition duration is zero, not just the media preference.
- Current browser console/runtime/local network checks: clean. This does not claim all remote issuer PDFs were re-downloaded.
- Manual inspection: five requested before/after pairs and additional 320px F4/overlap/F2 PASS for visibility, hierarchy, wrapping and semantics.
- Assets: JS 151,296 B / CSS 60,375 B raw, versus previous UI 2.4 JS 150,133 B / CSS 57,230 B. No added library/media.

320px Prism context/source may require normal vertical scrolling; this is not clipping. Quarter ruler retains horizontal scrolling. No open P0/P1 in requested scope. See [before_after.md](before_after.md); current browser reports are one directory above.

Local preview: http://127.0.0.1:4173/ . Release candidate ready for explicit approval; no commit/push/deployment performed.

STOP BOUNDARY: STOPPED BEFORE DEPLOYMENT
