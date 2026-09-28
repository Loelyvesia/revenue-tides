# Quarter Prism / 季度棱镜

## Concept

Quarter Prism is a movable reading window laid over one fiscal-quarter trajectory. Outside the window, the reader sees within-series context. Inside it, the selected quarter is decomposed into value, entity scope, metric version, evidence class, uncertainty, event context, issuer attribution, and source trail. Its core lesson is that a number is a measurement under a definition.

It is signature-worthy because the frozen data model directly changes the geometry: overlapping metric versions split into simultaneous lanes, derived evidence expands into an interval, and events occupy a separate rail. A filter or tooltip cannot replace this structural decomposition.

## Data dependencies

- `series_index.detail_path` selects one lazy detail payload.
- `observations[].period_index` establishes order.
- `metric_definition_id`, `metric_version`, and `metric_versions[].version_break` create reporting lanes and seams.
- `value`, `unit`, `currency`, `evidence_class`, `lower_bound`, `upper_bound`, and `derived` populate the reading window.
- `events[].fiscal_period` aligns the context rail.
- `attributed_claims[].period` adds a separately labeled issuer explanation.
- `source_id` and `source_page` open the source trail.
- `findings[]` links the selected series to canonical Finding chapters.

## Core action and interaction flow

1. Choose a series from the research-order list; no cross-company amount comparison is offered.
2. Move the prism by dragging its wide handle, using Previous/Next Quarter, arrow keys, a quarter select, or the direct quarter list.
3. The prism snaps to one `period_index`; the trajectory remains visible around it.
4. The reading pane announces the selected series and quarter, then lists entity scope, reporting lane, value, evidence, uncertainty, event count, and source access.
5. If the quarter has multiple metric versions, the prism widens and splits vertically into simultaneous labeled lanes.
6. If the value is derived, a whisker and hatched compatible range replace any confident direction arrow.
7. Events align on a separate rail below the quantitative track. Issuer language appears under “Issuer explanation,” never “Project Finding.”

## Required states

### A. Direct clean observation

NIKKE or Black Desert. One solid circular mark, a thin trajectory, the original KRW unit, `OFFICIAL_REPORTED`, entity type, scope, and source. No uncertainty geometry is shown.

### B. Same-quarter version overlap

Lineage M 2025Q2–2025Q4. The same quarter contains two vertically separated lanes labeled `legacy_v1` and `royalty_integrated_v2`. Both values remain visible at once. The quarter label is shared. There is no arrow, growth language, or implied chronological ordering between lanes.

### C. Derived uncertainty

MCOC. An outlined diamond marks the point estimate; a capped whisker and hatch show compatible bounds. The evidence label remains `DERIVED_FROM_OFFICIAL`. The official rounded share and rounding note remain adjacent. If `direction_sign_stable=false`, the change label reads “Direction not robust to rounding” and the interval-change geometry crosses the zero reference.

### D. Event-context quarter

Stellar Blade 2025Q2. The quantitative track shows KRW 65.719 bn and the window peak. A separate copper context rail aligns “PC launch” to the same quarter. Copy reads “same quarter”; no connector, impact score, contribution, or cause arrow is permitted.

### E. Metric-version boundary

Lineage W or Lineage M. A double calibration seam spans the analytical canvas. Labels identify `break_before`, `break_after`, and the frozen reason. The first compatible observation after the seam restarts baseline 100 and has no cross-version QoQ.

### F. No associated event

The context rail remains present but quiet, labeled “No curated event in this quarter.” It is not hidden and does not suggest source failure.

### G. Mobile

At 390 px and below, the trajectory becomes a vertical quarter list with a fixed step control. One selected quarter expands into stacked reporting lanes, uncertainty block, event context, issuer explanation, and source access. The decomposition remains the primary action.

## Finding-specific behavior

- F1: default teaching state. Split the same quarter into two definition lanes and expose version-break metadata. The interaction must prevent a legacy-to-v2 growth reading.
- F2: preserve 2025Q1 KRW 7.012 bn, 2025Q2 KRW 65.719 bn, +837.3%, and the eight-quarter peak. PC launch remains non-causal event context on the separate context rail; PC-only contribution is unavailable.
- F6: show all derived observation bounds and the sign-stability label. The Prism must not emit green/red directional treatment when sign is sensitive.
- F3: annotate rebound and remaining 4.1% gap separately. “Not recovered within observed window” is the recovery status.
- F4: the full trajectory remains visible while the prism steps through peak, drawdown, recovery/new peak, and second drawdown.
- F5: only `royalty_integrated_v2` is active for the Finding window. Legacy may appear behind the boundary as context, never in one continuous line.

## Keyboard and assistive flow

- The series select precedes the Quarter Prism in document order.
- Previous Quarter and Next Quarter are native buttons; Left/Right Arrow provide the same step action while the Prism control has focus.
- A native quarter select and direct quarter list provide non-drag access.
- The reading pane uses `aria-live="polite"` after discrete selection changes only.
- Announcement order: series; quarter; metric version or number of simultaneous versions; formatted value; evidence class; uncertainty bounds if present; event count; issuer-claim presence.
- Source controls remain normal keyboard-focusable links. Focus never moves automatically after a quarter change.

## Motion and reduced motion

Pointer movement previews position, but data updates only on the snapped quarter. A 350–650 ms decomposition may separate lanes, extend uncertainty, and reveal the event rail. Motion never encodes meaning alone. Under `prefers-reduced-motion`, the selected quarter and all final lanes appear immediately; the live-region announcement is unchanged.

## Error handling

- Missing series detail: retain the index label and show “Series data unavailable.”
- Missing optional event/claim: render the explicit empty state, not an error.
- Invalid metric reference: do not infer a lane; show “Metric definition unavailable” and preserve the source route.
- Source link failure: keep document metadata and label the link unavailable.
- Missing numeric value: show the canonical `missingness_state`; never zero.

## Semantic guardrails

- No absolute cross-company overlay exists in the Prism.
- No cross-version line segment, QoQ, baseline continuation, or before/after commercial language.
- No event-to-value connector or causal verb.
- No derived point without bounds, share, evidence class, and sign stability where applicable.
- No inferred trend, health, momentum, or success score.

## Success criteria

After one direct state, one overlap state, and one derived/event state, a reviewer can explain why a quarter can contain two values, what a metric version is, which values are derived, why rounded-share changes may be directionally indeterminate, and why an event marker is only temporal context. The task should take less than 30 seconds in the default guided sequence.
