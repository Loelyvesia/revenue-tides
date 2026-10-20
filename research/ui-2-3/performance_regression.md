# Performance Regression

| Asset group | UI 2.2 | UI 2.3 | Change |
|---|---:|---:|---:|
| JavaScript, raw | 147,521 B | 146,589 B | -932 B |
| CSS, raw | 63,101 B | 52,150 B | -10,951 B |
| Largest asset | 98,569 B | 98,849 B | +280 B |
| Runtime image/video assets | 0 | 0 | unchanged |

SVG complexity decreased in repeated views because default quarter circles, baselines, ticks, connector lines and frames were removed. New depth comes from deterministic paths and gradients; no canvas simulation, video, Three.js, D3 or motion dependency was added.

Motion remains event-driven (enter, selection and quarter change), with no constant breathing loop.
