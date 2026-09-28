# Responsive audit

| Viewport | Chromium client/scroll width | Overflow | Prism mode | Result |
| --- | ---: | ---: | --- | --- |
| 1440 × 900 | 1425 / 1425 | 0 px | Desktop | PASS |
| 1280 × 800 | 1265 / 1265 | 0 px | Desktop | PASS |
| 1024 × 768 | 1009 / 1009 | 0 px | Desktop/compact | PASS |
| 768 × 1024 | 753 / 753 | 0 px | Narrow | PASS |
| 390 × 844 | 390 / 390 | 0 px | Mobile stacked | PASS |
| 320 × 700 | 320 / 320 | 0 px | Survival mobile | PASS |

Firefox independently passed 1280 × 800, exact 390 × 844, and 320 × 700 with zero page-level overflow. Long publisher names, metric labels, Finding limitations, source titles, Chinese copy, Observatory rows, and native selects wrap without clipping. No local horizontal scroller is required. Visible mobile buttons and selects retain at least 44 px height.

At an effective 720 CSS-pixel layout corresponding to 200% zoom on a 1440-pixel desktop, critical Prism content remained visible, controls remained usable, and page overflow remained 0 px.
