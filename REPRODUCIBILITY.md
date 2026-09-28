# Reproducibility

## Environment

The final local audit used Windows, Node.js `v24.19.0`, npm `11.17.0`, and Python `3.13.2`. The application uses Vue 3, TypeScript, Vite, and Vitest. No backend, account, private API, or browser session is required to rebuild the validated public data and frontend from the retained local inputs.

## Install and application workflow

```bash
npm install
npm run dev
npm run typecheck
npm test
npm run build
npm run preview
```

`npm run build` first executes `scripts/frontend/sync_web_data.py`, which verifies and copies the frozen `data/web/` files into `public/data/`, then type-checks and builds the static site into `dist/`.

## Research pipeline

The research pipeline is staged and intentionally not collapsed into one command:

1. Phase B constructs the controlled pilot from retained extraction inputs.
2. Phase C freezes the method.
3. Phase D constructs the nine-series corpus.
4. Phase E validates and computes findings-ready transformations.
5. Phase F produces and freezes six Findings.
6. Phase G produces the public-safe web-data layer.
7. Phase I consumes only the Phase G layer.

Representative local rebuild commands are:

```bash
py -3.13 scripts/phase_d/build_corpus.py
py -3.13 scripts/phase_e/build_phase_e.py
py -3.13 scripts/phase_f/analyze_findings.py
py -3.13 scripts/phase_g/build_web_data.py
```

These commands use retained local inputs. Network access is not required for the canonical/web rebuild. Rebuilding research stages may overwrite generated outputs, so a frozen-release verifier should normally run validators rather than rebuilding earlier stages in place.

## Validation

```bash
py -3.13 scripts/phase_c/validate_phase_c.py
py -3.13 scripts/phase_f/validate_phase_f.py
py -3.13 scripts/phase_g/validate_phase_g.py
py -3.13 scripts/phase_i/validate_phase_i.py
py -3.13 scripts/phase_j/validate_phase_j.py
py -3.13 scripts/phase_k/validate_phase_k.py
```

The Phase C, F, and G validators include historical stop-boundary assertions. In a completed A–K tree, their semantic/hash checks remain applicable, while their original “later phase must not exist” check is expected to fail. Phase K therefore validates those frozen hashes directly and also records a Phase G isolated-boundary validation run. Phase I and J validators are forward-compatible through Phase K.

## Frozen versions

- Method: `revenue-tides-method-freeze-1.0.0`
- Findings: `revenue-tides-findings-1.0.0`
- Web Data: `revenue-tides-webdata-1.0.0`
- Release: `revenue-tides-release-1.0.0`
- Data cutoff: `2026-09-22`

## Production preview

Build with `npm run build`, then run `npm run preview`. The Phase J release audit tested HTTP hosting at the root and under `/revenue-tides/`. The project was not publicly deployed.

## Integrity

`release/final_hashes.csv` records SHA-256 values for critical frozen, application, build, and competition files. `release/file_inventory.csv` lists relevant deliverables while excluding `node_modules`, caches, temporary browser data, and duplicate builds. `release/final_manifest.json` is the machine-readable release summary; its own hash is stored externally in `final_hashes.csv` to avoid self-reference.
