# Accessibility regression

Status: `PASS`

- Skip link remains first in the keyboard order and visibly focused.
- Prism container remains keyboard-focusable; Left/Right Arrow changes quarters.
- Previous, direct-select, next, source disclosure, ledger rows, and links remain keyboard reachable.
- Focus uses a 3 px non-color-only outline.
- Touch targets remain at least 44 px at 390×844 and 320×700.
- SVGs preserve `role=img`, title, description, and textual summaries.
- Prism selection changes remain announced through `aria-live=polite`.
- Direct/derived evidence differs by circle/diamond geometry; version breaks use a double seam; uncertainty uses interval caps and hatching.
- Event context remains a separate labeled rail and explicitly non-causal.
- Reduced motion removes transition duration without removing content or interaction.
- 200% zoom-equivalent reflow passes with no page-level horizontal overflow.
- Long source titles and metric definitions wrap rather than clip.

No accessibility capability present in 1.0.0 was removed for visual simplification.
