# Quarter Prism Main Interface Reconstruction

Status: `PASS`

This is a presentation-only reconstruction of the Quarter Prism main interface. It does not change source data, frozen Findings, evidence classes, metric versions, uncertainty, event non-causality, or source traceability.

## Dark area reduction

The previous interface placed the chart, reading output, and navigation inside one continuous dark panel. The redesigned interface keeps the page, controls, entity header, reading output, source disclosure, and quarter navigation on warm mineral surfaces. Deep graphite is limited to the measured tidal-band stage.

Using a luminance threshold below 60 on the same 1440×900 Lineage overlap screenshot, dark pixels decreased from `71.1%` to `35.4%`: a reduction of `35.7 percentage points`, or approximately `50.2%` of the former dark area.

## Line → measured tidal band

- Each metric lane is now a straight-edged closed band generated only from canonical quarterly points.
- The geometry uses `M`/`L` segments; no Bézier or intermediate observations are introduced.
- A restrained center calibration line sits inside the band rather than acting as the primary mark.
- Peak caps identify observations whose validated drawdown is zero.
- Drawdown notches mark observations with a negative validated drawdown.
- Derived observations retain their interval and diamond encoding.

## Selection box → prism aperture

The former translucent rectangular selection is replaced by a reading aperture:

- paired outer calibration rails;
- secondary inner rails;
- repeated rail ticks;
- a subtle center reading field;
- a top quarter label;
- alignment with the chart baseline and bottom quarter ruler.

There is no enclosing top/bottom selection-box border. The selected quarter is visually read through the aperture rather than boxed.

## Overlap refraction

For Lineage overlap quarters, the legacy lane remains the carrier trajectory. The royalty-integrated lane is clipped to the aperture using an SVG `clipPath`, so the second definition becomes most visible only inside the reading field. The same-quarter/different-definition annotation remains explicit, and cross-version growth remains forbidden.

## Reading output

The reading output is a compact warm-surface result block containing:

- quarter;
- canonical value and unit;
- entity and entity type;
- evidence class and metric version;
- concise metric/QoQ note;
- uncertainty or issuer attribution when applicable;
- source disclosure.

It no longer shares the dark chart background and no longer stretches into a full-height empty sidebar.

## Quarter selector redesign

The visible boxed quarter select and detached right-side buttons were removed. Quarter navigation now uses a bottom calibration ruler with text labels and selected ticks. Previous/next arrows, direct quarter access, Left/Right keyboard navigation, and the hidden native contract select remain available for accessibility and regression compatibility.

## Validation

- Prism reconstruction: `27/27 PASS`.
- Vitest: `62/62 PASS`.
- UI 2.1: `28/28 PASS`.
- Phase I: `100/100 PASS`.
- Phase J: `102/102 PASS`.
- Chrome 153: `15/15 PASS`.
- Edge 149: `15/15 PASS`.
- Firefox 156: `14/14 PASS`.
- Required viewports: `0 px` page-level horizontal overflow.
- Console errors, warnings, exceptions, and required network failures: `0`.

## Bundle effect

- Before: JS `125.02 kB / 46.31 kB gzip`; CSS `50.40 kB / 10.52 kB gzip`.
- After: JS `125.67 kB / 46.53 kB gzip`; CSS `50.01 kB / 10.50 kB gzip`.
- No dependency was added.

No deployment or release freeze was performed.
