# Observation-grid reconciliation

The expected grid contains 66 unique `series_id × fiscal_period_id` rows. The canonical observation table contains 75 rows. The nine additional rows are legitimate same-quarter metric-version overlaps: Lineage M contributes three, Lineage 2M contributes three, and Lineage W contributes three, all in 2025Q2–2025Q4.

`66 unique series-period rows + 9 additional version-overlap observations = 75 canonical observations`

Every surplus row appears in `version_overlap_matrix.csv`; no unexplained surplus remains.
