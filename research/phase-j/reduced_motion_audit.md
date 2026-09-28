# Reduced-motion audit

Chrome was run with `prefers-reduced-motion: reduce`.

- `matchMedia` reported the reduced-motion preference.
- Prism transition duration resolved to `0.00001s`.
- Reading pane, metric lanes, uncertainty, event rail, controls, and live-region content remained present.
- Quarter and series navigation remained functional.
- No continuous or automatic animation exists.

**Result: PASS.** The semantic result matches normal-motion mode; motion is not required to reveal meaning.
