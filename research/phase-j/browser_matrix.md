# Browser matrix

| Browser | Version | Method | Result | Notes |
| --- | --- | --- | --- | --- |
| Google Chrome | 153.0.8010.53 | Headless system Chrome + CDP | PASS, 40/40 | Full semantic, responsive, console/network, keyboard, reduced-motion, accessibility-tree, screenshot workflow |
| Microsoft Edge | 149.0.4022.62 | Headless system Edge + CDP | PASS, 40/40 | Same complete smoke workflow as Chrome |
| Mozilla Firefox | 156.0.1 | Headless system Firefox + WebDriver BiDi | PASS, 14/14 | Production load, opening, Findings/series counts, overlap, uncertainty, event context, 1280/390/320 responsiveness, hash, console/network |
| WebKit / Safari-equivalent | — | — | NOT_AVAILABLE | No installed WebKit/Safari engine; no large browser suite installed solely for this gate |

Production testing used `http://127.0.0.1:4173/`, never `file://`. The installed browser binaries were reused; Playwright, Cypress, Puppeteer, axe-core, and geckodriver were not installed.
