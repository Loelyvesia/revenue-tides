# Final QA Summary

## Data QA

The final corpus remains 9 series, 75 observations, 26 events, 3 attributed claims, and 18 derived observations. Nine legitimate NCSOFT same-quarter version overlaps remain separate. Missing values are not zero.

## Research QA

Method, Findings, and web-data freeze hashes validate. All six frozen Findings reproduce from the public data layer; F1/F2/F4 remain the headline set. Definition differences, uncertainty, event context, and observation-window recovery status retain their limits.

## Frontend QA

TypeScript, 62 Vitest tests, production build, and Phase I validation pass. The frontend reads only the frozen Phase G public-data layer. No research calculation is moved into the browser.

## Browser QA

Chrome 153, Edge 149, and Firefox 156 passed production checks. Six desktop/mobile viewports showed no page-level horizontal overflow, console errors, warnings, uncaught exceptions, or unexpected required network failures. WebKit/Safari-equivalent was unavailable.

## Accessibility

Keyboard, focus, skip link, native controls, ARIA/live region, accessible SVG, non-color encodings, reduced motion, 44 px touch targets, 200% equivalent reflow, and the accessibility tree were reviewed. A real interactive screen-reader session was unavailable.

## Performance

JS is 107.29 kB / 40.27 kB gzip; CSS is 26.78 kB / 5.71 kB gzip; HTML is 0.91 kB. Initial load uses 8 requests and 29,486 bytes of bootstrap JSON; series details remain lazy-loaded.

## Reproducibility

Deterministic builders, stable IDs, source references, freeze manifests, final SHA-256 hashes, and a release inventory support independent verification from retained local inputs.

## Limitations

Publisher-defined values are not globally uniform or cross-company comparable. Derived observations inherit rounded-share uncertainty. Events are curated and non-causal. Observed-window non-recovery is not permanent decline. Some remote source links may change or reject automation.
