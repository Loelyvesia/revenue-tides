# Data loading audit

## Initial payload

`loadBootstrap()` requests exactly five shared files: `manifest.json`, `project.json`, `series_index.json`, `findings.json`, and `caveats.json`. Runtime checks enforce the frozen web-data version and 9 / 75 / 6 counts before the application renders.

## Deferred payloads

- `sources.json` loads separately when S2 approaches the viewport.
- A series detail loads only when Quarter Prism approaches the viewport, a Finding visual approaches the viewport, or the reader selects an Observatory row.
- `Map<string, Promise<SeriesDetail>>` provides deterministic in-memory de-duplication.
- Failed promises are removed from cache so Retry performs a real new request.

## Failure behavior

Bootstrap and series failures show explicit errors and never insert zeroes. A stale prior series is cleared by the composable. Missing source metadata preserves the observation and reports the unavailable route. Unit tests cover bootstrap scope, source deferral, successful lazy loading, caching, wrong identity, 404 handling, and frozen-count rejection.

## Static build integration

`scripts/frontend/sync_web_data.py` validates every Phase G manifest hash, clears only the resolved `public/data` target, copies the 16 public files, and verifies a byte-identical inventory. Vite `base` is configurable with `VITE_BASE_PATH` and defaults to `./` for subdirectory hosting.
