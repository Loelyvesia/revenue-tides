# Deployment readiness audit

## Root static build

`dist/` was served through Python's static HTTP server at `http://127.0.0.1:4173/`. HTML, hashed JS/CSS, five bootstrap JSON files, source registry, and all nine lazy series files resolved successfully. No backend, authentication, database, runtime API, or server-side rendering is required.

## Subdirectory build

A temporary production build used `VITE_BASE_PATH=/revenue-tides/` and was served at `http://127.0.0.1:4174/revenue-tides/`. Chrome passed 40/40 smoke checks. Hashed assets, bootstrap data, deferred sources, and lazy series paths all resolved below the subdirectory. The temporary build was deleted after verification.

## Navigation and links

Fresh `#finding-F1` load, post-load hash change, browser Back, and Forward passed. External links use `target="_blank"` with `rel="noopener noreferrer"`. No public deployment occurred.

**Result: PASS / release-ready for a static host after an explicit deployment decision.**
