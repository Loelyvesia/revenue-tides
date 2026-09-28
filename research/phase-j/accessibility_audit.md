# Accessibility audit

**Result: PASS; zero known serious or critical violations.**

- Accessibility tree: 1,076 nodes reviewed; exactly one `main`; one page `h1`; ordered section/Finding headings; named buttons and links.
- Quarter Prism exposes an accessible interaction label, SVG title/description, adjacent text summary, native select/buttons, `aria-current`, `aria-expanded`, and one polite live region.
- Direct/derived evidence uses shape, outline/fill, text, and intervals. Version breaks use double seams, discontinuity, and text. Events use a separate labeled rail. Selection uses border and text as well as color.
- Contrast ratios against rendered palette surfaces: primary text 14.14:1; secondary text 6.61:1; event/context 6.50:1; focus color 5.68:1. All audited ratios meet the stated target.
- Mobile controls are at least 44 px high, critical information is not hover-only, and no keyboard trap was found.
- Skip link, visible focus, source disclosures, long labels, reduced motion, and 200% equivalent reflow passed.

No axe-core or equivalent scanner was already installed, so no dependency was added. Chrome's accessibility tree and deterministic semantic checks were used alongside manual keyboard and visual review. `REAL_SCREEN_READER_NOT_AVAILABLE`: a controlled Narrator/NVDA session was not available in this headless QA environment.
