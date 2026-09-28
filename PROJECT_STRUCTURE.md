# Project Structure

| Directory | Role |
| --- | --- |
| `data/` | Canonical Phase B–F tables and the frozen public-safe `data/web/` layer. |
| `research/` | Method, provenance, audits, evidence packs, QA reports, and retained official source PDFs. |
| `scripts/` | Deterministic builders, synchronizers, browser checks, and phase validators. |
| `design/` | Phase H Tidal Ledger tokens, wireframes, and Quarter Prism state prototypes. |
| `src/` | Vue 3 + TypeScript application source. |
| `public/` | Static public data copied byte-for-byte from `data/web/`. |
| `dist/` | Single canonical production build. |
| `competition/` | Judge-facing summaries, scripts, guides, audits, and selected screenshots. |
| `release/` | Lightweight final manifest, hashes, inventory, and freeze declaration only. |

`node_modules/` is local dependency state and is not part of the release inventory. Temporary and cache directories are not deliverables.
