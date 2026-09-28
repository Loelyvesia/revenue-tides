# Accessibility specification

## Semantic structure

- One page title, then ordered section headings S0–S6. Finding titles are headings, not styled paragraphs.
- Series Observatory is a semantic table at desktop and a list of disclosure controls at mobile.
- Evidence and source metadata use definition lists. Canonical source links retain descriptive names.
- Every SVG/data visual has a title, description, and adjacent text summary. A structured observation list is available without operating the visual.

## Quarter Prism behavior

- Dragging is optional. Previous/Next buttons, Left/Right Arrow, native quarter select, and direct quarter list reach every state.
- The selected quarter is reflected with `aria-current` in the quarter list.
- A polite live region announces only settled selection changes: series, quarter, metric version(s), value, evidence class, bounds when derived, event count, and issuer-claim presence.
- Overlap is announced as “two reporting definitions in the same quarter,” followed by both labeled values.
- Focus remains on the initiating control. No automatic focus transfer or keyboard trap.

## Focus and input

- Visible focus: at least 2 px `focus` token plus 2 px offset, 3:1 contrast against adjacent surfaces.
- Coarse-pointer targets: at least 44×44 px with 8 px separation where controls are adjacent.
- Hover never reveals unique information. Hover and focus may expose the same supplementary detail.
- Source drawer opens from a native button, traps focus only while modal, has a labeled close control, and restores focus on close.

## Color and marks

Direct/derived use fill state, circle/diamond shape, label, and interval—not hue alone. Version breaks use a double seam, discontinuous path, and text. Events occupy a separate rail and carry labels. Uncertainty uses whiskers/hatch plus numeric bounds, never blur or opacity alone.

## Text and numbers

- Body contrast targets WCAG 2.2 AA (4.5:1); large text and meaningful non-text marks target 3:1.
- Tabular numerals apply to quarters, values, percentages, and aligned source pages.
- Original currency and metric scope remain adjacent to values.
- Chinese-first microcopy uses concise, neutral terms; English is secondary or provided in the canonical Finding text.

## Reduced motion

`prefers-reduced-motion: reduce` removes prism travel, lane separation, interval extension, and rail entrance. Final states appear instantly. Selection, live-region announcement, and focus behavior remain unchanged.

## Alternative summaries

Each analytical visual includes a concise summary that states the series, metric, window, important values, version restrictions, uncertainty, and event caveat. It must not introduce a causal or cross-company claim.

## Error and empty states

Failures use `role="alert"` only when user action is required. Empty event/claim/Finding states are ordinary status text. Missing values expose `missingness_state`; zero is never substituted.
