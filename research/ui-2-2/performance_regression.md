# UI 2.2 performance regression

| Asset group | Bold rebuild | UI 2.2 | Change |
|---|---:|---:|---:|
| JavaScript raw | 146,012 B | 147,521 B | +1,509 B |
| JavaScript gzip | 58,210 B | 58,719 B | +509 B |
| CSS raw | 62,530 B | 63,101 B | +571 B |
| CSS gzip | 14,450 B | 14,473 B | +23 B |

The small JavaScript increase is the centralized Chinese display-copy layer and revised presentation markup. CSS growth comes from mobile hierarchy rules for overlap readings and Finding headlines. No dependency, font, image, chart library, tracking code, or new visual-effect system was added. Largest emitted asset: 98,569 bytes raw.
