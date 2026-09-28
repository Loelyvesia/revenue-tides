# Performance audit

| Item | Final value |
| --- | ---: |
| JavaScript | 107.29 kB; 40.27 kB gzip |
| CSS | 26.78 kB; 5.71 kB gzip |
| HTML | 0.91 kB |
| Initial application requests | 8 |
| Initial JSON files | 5 |
| Initial JSON payload | 29,486 bytes uncompressed |
| Example lazy Lineage M payload | 18,225 bytes |
| Deferred source registry | 21,653 bytes |
| Largest content asset | JavaScript, 107,290 bytes |

Bundle size is unchanged from the Phase I baseline; JavaScript growth is 0% and CSS growth is 0%. No source maps, fonts, game art, video, telemetry, router, chart library, or UI framework were added. No all-series eager request, runaway duplicate request, visible interaction freeze, constant rendering loop, or disruptive Prism control shift was observed.

Local cached navigation recorded approximately 13.6 ms to DOMContentLoaded and 14.5 ms to load; these local values are diagnostic, not public-network benchmarks. Lighthouse was not installed and was not added solely for a score.
