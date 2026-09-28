# Methodology in One Page

## Research object

Fiscal-quarter commercial trajectories for publisher-defined games, IPs, and franchises in official public company disclosures.

## Temporal unit

`FISCAL_QUARTER`. Observation-period bounds and publication dates are separate. The final window is 2024Q3–2026Q2.

## Evidence classes

Primary quantitative evidence is limited to `OFFICIAL_REPORTED` and `DERIVED_FROM_OFFICIAL`. Official events and issuer explanations are context layers, not substitutes for observations.

## Corpus rules

The frozen range is 8–12 analytical series, normally with at least six consecutive quarters. At least two-thirds must be primarily direct official; no more than one-third may be primarily derived. The final corpus has 9 series: 6 direct and 3 derived.

## Metric-version policy

Stable versions define comparison windows. Legacy and royalty-integrated NCSOFT metrics remain separate, including same-quarter overlaps. Cross-version QoQ is unavailable and baselines restart after the break.

## Derived policy

Derived values use only official inputs and deterministic formulas. The public layer retains point value, lower/upper bounds, rounded share, rounding note, derivation reference, and direction-sign stability. Derived does not mean directly reported.

## Comparability

Absolute cross-company comparison and global revenue rankings are forbidden. Stable within-series change is allowed. No canonical FX conversion is used.

## Missingness

Unavailable, not reported, outside-window, version-break, and unresolved states remain explicit. Missingness is never encoded as numeric zero; no interpolation or forward fill is allowed.

## Events and causality

Events are curated official context. “Occurred in the same quarter” is allowed; “caused the change” is not. Issuer explanations remain attributed claims.

## Reproducibility

Stable IDs link Finding → observation → metric version → source and Finding → event/claim → source. Freeze manifests and final release metadata use SHA-256. Builders and validators use local retained inputs.

## Public source policy

Public web data contains structured facts and source links, not copied report artwork, internal extraction identities, raw local paths, or private APIs. Sensor Tower and AppMagic are not the quantitative backbone.
