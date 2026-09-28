# Technical Architecture

## Stack

The application is a static Vue 3 + TypeScript + Vite site. Quarter Prism uses project-specific SVG and CSS; there is no chart library, backend, database, analytics, or tracking.

## Data flow

```text
Official disclosures
        ↓
Validated canonical corpus
        ↓
Frozen Findings
        ↓
Deterministic Phase G Web Data
        ↓
Static Vue frontend
```

## Public data layer

Phase G produces a small manifest, project metadata, series index, Findings, caveats, source registry, and nine per-series detail files. The browser never reads raw IR PDFs, extraction spreadsheets, or internal QA tables.

## Loading strategy

The initial production page requests HTML, JavaScript, CSS, and five bootstrap JSON files. The bootstrap JSON totals 29,486 bytes. The source registry is deferred until the analytical area approaches the viewport, and each series detail is fetched only when selected, then cached in memory. There is no eager all-series request.

## Determinism

`scripts/frontend/sync_web_data.py` verifies and copies `data/web/` byte-for-byte into the public tree. TypeScript validation, Vitest, Vite build, phase validators, and final SHA-256 manifests protect the release boundary.

## Hosting

The build is static and works at a root path or configured subdirectory. No public deployment was performed during final freeze.
