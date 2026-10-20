# UI 2.4 Mobile Overlap Audit

Test case: Lineage M, 2025 Q2, 390×844.

The mobile overlap state follows this explicit reading order:

1. 当前季度 / 2025 Q2
2. 旧口径 / 121.111 / legacy v1
3. 纳入 royalties / 127.908 / royalty-integrated v2
4. “同一季度，两种报告口径” explanation
5. Refraction tide with two anchor beads
6. Source disclosure after the geometry

The two readings use equal minmax columns, block-level numeric lines and an 11vw capped type scale. The former `121.111127.908` collision is removed. Details are hidden inside the compact readings; the chart hides its repeated quarter label, long center explanation and seam text. Metric-version labels and the two non-color-coded anchor states remain.

Chrome 390×844 screenshot: `screenshots/mobile-390-overlap.webp`. The automated layout audit measured a 12.8 px gap between the two numeric bounding boxes and exact contact between the reading block bottom and chart top (521.4 px), with no overlay.

Result: PASS — no collision, no clipped numeric value, no viewport overflow.
