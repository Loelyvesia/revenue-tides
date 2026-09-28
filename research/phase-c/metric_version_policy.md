# Metric-version policy

A new metric version is mandatory when a change materially affects entity scope, royalty or licensing treatment, platform composition embedded in the definition, revenue-recognition basis, denominator, consolidation scope, or economic meaning.

Across `VERSION_BREAK` boundaries, the project must not calculate QoQ change, stitch curves, interpolate, average versions, overwrite older values, or describe one version as correcting another unless the issuer explicitly defines a restatement.

Overlapping versions are valid and must use a unique key that includes metric-definition identity. Baseline indexes restart after a break.

Lineage M is the canonical reference: legacy v1 and royalty-integrated v2 overlap in three quarters but remain separate analytical lanes.
