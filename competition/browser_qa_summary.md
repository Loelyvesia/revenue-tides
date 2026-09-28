# Browser QA Summary

The static production build was tested over HTTP in:

| Browser | Version | Result |
| --- | --- | --- |
| Google Chrome | 153.0.8010.53 | PASS, 40/40 Phase J checks |
| Microsoft Edge | 149.0.4022.62 | PASS, 40/40 Phase J checks |
| Mozilla Firefox | 156.0.1 | PASS, 14/14 Phase J checks |
| WebKit / Safari-equivalent | Not available | Not tested |

Viewports: 1440×900, 1280×800, 1024×768, 768×1024, 390×844, and 320×700. Every audited viewport recorded 0 px page-level horizontal overflow.

Console errors: 0. Console warnings: 0. Uncaught exceptions: 0. Unexpected required 4xx/5xx responses: 0. Required JSON failures: 0. Root hosting and `/revenue-tides/` subdirectory hosting both passed.

Quarter Prism direct, version-overlap, version-boundary, derived-uncertainty, event, no-event, mobile, keyboard, reduced-motion, cache, failure/retry, source, and hash-navigation paths were exercised. WebKit/Safari-equivalent was not available in the local environment and is a release limitation.
