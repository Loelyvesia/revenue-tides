# Judge Q&A

## 1. Why not use Sensor Tower as the main dataset?

The public layer did not provide a sufficiently continuous, exact, title-level monetary history under reproducible public access. Official company disclosures offered stronger provenance and stable fiscal-quarter records. Sensor Tower and AppMagic therefore remain context, not the quantitative backbone.

## 2. Why quarterly rather than monthly?

Quarterly granularity matches the stable cadence of investor-relations disclosures. Forcing monthly values would require paid/private data, interpolation, or inconsistent public fragments.

## 3. Why only nine series?

The frozen method allowed 8–12 and preferred continuity of at least six quarters. A tenth candidate would have weakened evidence quality or exceeded the one-third cap on primarily derived series, so the target was not forced.

## 4. Why are different publishers not directly comparable?

Each publisher defines entity scope, platform coverage, accounting treatment, and reporting currency differently. Those amounts are valid inside their own definitions but do not form a common global market measure.

## 5. Why does Lineage M have two values in the same quarter?

NCSOFT published overlapping legacy and royalty-integrated definitions. Both observations are retained under separate metric-version IDs; neither replaces the other.

## 6. Is the difference between those Lineage M values growth?

No. F1 treats KRW 6.797–13.455 billion as a same-quarter definition effect. Cross-version change, correction, and restatement claims are forbidden.

## 7. What is `DERIVED_FROM_OFFICIAL`?

It is a deterministic observation calculated from official disclosed inputs, such as a company total and a rounded title share. It remains distinct from a directly reported title amount.

## 8. Why can a derived QoQ direction be uncertain?

An officially published share such as a whole-number percentage represents a compatible interval. If the prior and current value intervals overlap in direction, the point-estimate sign is not stable.

## 9. Does Stellar Blade's PC launch prove the increase was caused by PC?

No. PC launch and the eight-quarter peak occurred in the same quarter. The publisher-defined IP total contains no PC-only amount, so the project makes no causal or contribution claim.

## 10. Why are events curated rather than exhaustive?

The event layer exists to test whether stable official dates can provide useful context. It is deliberately small and source-backed, not a complete live-ops archive.

## 11. Why no global revenue ranking?

The underlying values do not share one economic definition. Ranking them would imply comparability that the sources do not support.

## 12. Why no USD conversion?

Currency conversion would standardize denomination but not entity scope, platform coverage, accounting meaning, or metric version. It would create an appearance of comparability without fixing the underlying mismatch.

## 13. Why are some games represented as IP rather than title?

The publisher's own disclosure controls the entity. NIKKE, Stellar Blade, and Black Desert are reported as publisher-defined IP scopes, and the project does not silently narrow them to one app or title SKU.

## 14. How do you ensure reproducibility?

Each canonical observation has stable IDs, periods, metric versions, evidence classes, and source references. Frozen method and Finding artifacts are hashed. Deterministic scripts rebuild the web-data layer and frontend, and the release records critical SHA-256 hashes.

## 15. What makes Quarter Prism different from a tooltip?

A tooltip usually reveals one value after a hover. Quarter Prism is a persistent, keyboard-operable analytical state that can show multiple same-quarter observations, version seams, uncertainty bounds, event context, attribution, and sources together.

## 16. Why is F1 important?

It demonstrates that measurement semantics can change the displayed number before any commercial change is considered. That lesson governs how the rest of the project is read.

## 17. What are the biggest limitations?

Publisher metrics are heterogeneous; events are non-exhaustive and non-causal; derived values inherit rounded-share uncertainty; the observation window is bounded; remote source availability may change; WebKit and a real screen-reader session were unavailable.

## 18. How was accessibility tested?

Keyboard paths, focus visibility, skip link, native controls, ARIA/live region, accessible SVG descriptions, non-color encodings, reduced motion, 44 px touch targets, 200% equivalent reflow, and the accessibility tree were reviewed.

## 19. Is the site WCAG certified or fully screen-reader certified?

No. The checks establish a strong tested baseline, but no real interactive screen-reader session or formal certification was available.

## 20. Which browsers were tested?

Chrome 153, Edge 149, and Firefox 156 were tested against the production build over HTTP.

## 21. Why was WebKit not tested?

No WebKit/Safari-equivalent engine was available in the local QA environment, and a large new browser suite was not installed solely for the gate. This remains a documented limitation.

## 22. Why is “not recovered” not the same as decline forever?

Recovery status is evaluated only inside the observed window ending 2026Q2. Later quarters are unknown, so permanent-decline language would exceed the evidence.

## 23. How are issuer explanations handled?

They remain attributed claims with issuer and source. The project does not rewrite management explanations as independent Findings or causal facts.

## 24. What would a future update require?

A new quarter, source correction, metric definition, Finding, series, or redesign requires a new branch/version or documented amendment. Release 1.0.0 cannot be silently overwritten.
