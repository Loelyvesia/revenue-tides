# Performance Summary

Final Phase J production baseline:

| Asset | Uncompressed | Gzip |
| --- | ---: | ---: |
| JavaScript | 107.29 kB | 40.27 kB |
| CSS | 26.78 kB | 5.71 kB |
| HTML | 0.91 kB | — |

The initial production load uses 8 requests: HTML, JavaScript, CSS, and 5 bootstrap JSON files. Those bootstrap JSON files total 29,486 bytes uncompressed. The source registry and nine series-detail files are deferred; the browser does not eagerly fetch every series.

No fonts, game art, video, source maps, analytics, router, chart library, or UI framework beyond Vue are shipped. No Lighthouse score is reported because Lighthouse was not measured.
