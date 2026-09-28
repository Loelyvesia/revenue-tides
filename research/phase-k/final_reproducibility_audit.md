# Final Reproducibility Audit

## Environment

- Node.js `v24.19.0`
- npm `11.17.0`
- Python `3.13.2`
- Static Vue 3 + TypeScript + Vite frontend

## Freeze integrity

Phase C method hashes, Phase F Finding hashes, Phase G public-data hashes, and Phase H design hashes validate. Phase J's full forward-compatible validator passes 102/102.

## Historical validator boundary

The original Phase C and Phase F validators include historical stop checks that intentionally reject any later-phase directory. Their content/hash checks pass, but those historical boundary assertions are not applicable to a completed A–K tree. The frozen files were not edited.

The Phase G validator was run in an isolated copy containing the authentic Phase C–G tree and no later phase directories. Result: **90/90 PASS**. This preserves its original stop-boundary meaning while proving the current Phase G data and build remain valid. The temporary copy was deleted after hash comparison.

## Current validators

- Phase I: 100/100 PASS
- Phase J: 102/102 PASS
- Vitest: 62/62 PASS
- Phase K: final result recorded in the Phase K report and summary after freeze

## Build and offline behavior

Canonical Phase G web data builds from retained local Phase D/E/F inputs and does not require network access, login, Sensor Tower, or AppMagic. The frontend sync verifies and copies `data/web/` into `public/data/`, then type-checks and builds one `dist/` tree.

## Release integrity

`release/final_hashes.csv` is external to `final_manifest.json` and therefore safely records the manifest hash without self-reference. `release/file_inventory.csv` excludes itself, `node_modules`, caches, temporary browser profiles, and temporary builds. The final browser smoke uses the production `dist` over HTTP.
