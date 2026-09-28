# Phase K Storage Audit

Approximate uncompressed project storage at the Phase K audit point:

| Area | Bytes | Approximate size | Notes |
| --- | ---: | ---: | --- |
| `research/` | 12,119,279 | 11.56 MiB | Includes retained evidence and all phase audits. |
| `data/` | 523,993 | 0.50 MiB | Canonical tables plus 182,030-byte public web-data layer. |
| `src/` | 101,986 | 0.10 MiB | Vue/TypeScript/CSS source. |
| `dist/` | 317,003 | 0.30 MiB | One canonical production build. |
| `competition/` | 479,464 | 0.46 MiB | Markdown materials plus nine selected screenshots. |
| Phase J QA screenshots | 643,846 | 0.61 MiB | Thirteen compact captures; originals retained once. |
| Retained raw evidence | 10,855,955 | 10.35 MiB | Fifteen official Phase B PDFs; no new binary source added later. |
| `node_modules/` | 126,688,027 | 120.82 MiB | Local dependency state; excluded from inventory and release metadata. |

No archive, site mirror, duplicate `dist`, duplicate raw evidence, or copied `node_modules` was created. `release/` contains metadata only. The competition screenshots are nine selected copies totaling 432,888 bytes; originals remain in the Phase J QA record and are not production assets.
