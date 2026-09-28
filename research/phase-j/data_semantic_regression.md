# Data and semantic regression

**Result: PASS.**

- Corpus: 9 series, 75 observations, 26 curated events, 6 Findings; F1/F2/F4 remain headline.
- Entity types remain `GAME_TITLE` or `IP`; Black Desert, NIKKE, and Stellar Blade remain IP.
- Evidence remains `OFFICIAL_REPORTED` or `DERIVED_FROM_OFFICIAL`; no derived value is presented as direct.
- All 18 derived observations retain point value, lower/upper bounds, share, derivation reference, and sign stability.
- Nine NCSOFT same-quarter overlap observations remain representable: three each for Lineage M, Lineage 2M, and Lineage W.
- Legacy and royalty-integrated versions are not stitched; cross-version QoQ is unavailable and the new baseline restarts.
- F1–F6 frozen wording, values, limits, forbidden interpretations, IDs, and source routes remain unchanged.
- F2 retains 7.012 → 65.719 billion KRW, +837.3%, same-quarter PC launch context, unknown PC-only amount, and no causal conclusion.
- Event coverage remains curated/non-exhaustive and event timing remains non-causal. Cross-company publisher-defined absolute values remain non-comparable.
- No USD conversion, market-share layer, leaderboard, success/health score, fabricated trend label, Sensor Tower/AppMagic value, or causal event field was introduced.

The rendered forbidden-text scan found no prohibited affirmative claim. Causal terms remain only in explicit limitation/forbidden-interpretation copy.

The legacy Phase G validator was also rerun under Python 3.13. Its 89 still-applicable integrity/build checks passed; only its historical check that `research/phase-h/` must not exist failed, as expected after the explicitly authorized Phases H–J. Phase J replaces that obsolete boundary with `STOPPED BEFORE PHASE K` and independently validates the frozen hashes and full public-data semantics.
