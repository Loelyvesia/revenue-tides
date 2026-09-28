# Information architecture

Versions: method `revenue-tides-method-freeze-1.0.0`; Findings `revenue-tides-findings-1.0.0`; web data `revenue-tides-webdata-1.0.0`.

## Narrative route

The product follows one argument: a revenue observation is meaningful only with its entity, reporting definition, period, evidence class, uncertainty, and source. The reader moves from thesis, to measurement literacy, to manipulation, to Findings, and finally to open-ended series inspection.

| Section | Purpose and primary question | Data and Finding dependency | Entry state | Exit state | Responsive change |
| --- | --- | --- | --- | --- | --- |
| S0 Opening / Thesis | Establish that this is not a global revenue leaderboard. “What am I looking at?” | `project.json`; counts and global caveats | Title, thesis, 9 series / 75 observations / 4 publishers / 2024Q3–2026Q2 set typographically | Reader knows absolute cross-company comparison is forbidden and continues to measurement primer | At mobile, counts become one compact sentence; no KPI cards |
| S1 What Is a Revenue Number? | Explain entity type, evidence class, metric version, scope, and uncertainty. “Why can two numbers both be valid?” | `caveats.json`; schema; F1 and F6 concepts | Five short ledger rows with paired mark samples | Reader can decode the evidence key and enters the Prism | Rows stack at 390/320 without horizontal diagrams |
| S2 Quarter Prism | Decompose one quarter. “What constructed this observation?” | Selected series detail; observations, metric versions, events, claims, sources | Lineage M 2025Q2 overlap is the teaching default; direct clean state remains one action away | Reader has seen two definitions coexist and can follow F1 | Desktop uses movable reading window; tablet moves evidence below; mobile uses a quarter stepper |
| S3 Headline Finding chapters | Tell the strongest evidence-bounded stories. “What did the corpus establish?” | F1, F2, F4 plus their referenced observations/events/sources | F1 follows directly from Prism; F2 and F4 follow as editorial chapters | Reader understands reporting semantics, non-causal event alignment, and recovery sequence | Visual and prose stack below 768; numeric labels remain adjacent to marks |
| S4 Series Observatory | Browse all nine series deliberately. “Which measured trajectory should I inspect?” | `series_index.json`, then one lazy detail file | Structured ledger sorted by research order, not revenue | Selecting a row opens one series detail and preserves return position | Columns reflow to two-line ledger rows at 768; mobile uses disclosure rows, not cards |
| S5 Remaining Findings | Complete the research story. “What else is supported?” | F3, F5, F6 | F3 and F5 use compact Finding chapters; F6 uses 15 interval-change marks | Reader understands incomplete recovery, bounded v2 persistence, and sign sensitivity | F6 marks wrap 5×3 at tablet and 3×5 at mobile |
| S6 Method / Evidence / Sources | Expose versions, policies, sources, and limits. “Can I verify it?” | project, caveats, Findings, source registry | Compact version ledger and evidence/source access | Source drawer or direct document link; end of narrative | At mobile, source metadata becomes a definition list; long URLs stay behind labeled links |

## First understanding

The first screen uses the method-consistent thesis “流水不是一个统一数字。” The next sentence clarifies that entity scope, reporting definition, and evidence can change what is observed. It never presents total revenue, a winner, a ranking, a leaderboard layout, or a common absolute scale. The Observatory is research order, not revenue rank.

## Finding encounter model

- F1 is taught through direct manipulation in the Quarter Prism, then summarized as a headline chapter.
- F2 uses a trajectory and a physically separate event rail. The PC launch is labeled “same quarter,” never “effect.”
- F4 uses one continuous within-series trajectory with peak, drawdown, recovery/new peak, second drawdown, and observed-window non-recovery.
- F3, F5, and F6 follow the Observatory so readers can relate the Findings to the broader corpus.
- Finding references in series detail are compact links back to the canonical chapter; complete prose is not duplicated.

## Navigation model

A short section index exposes Thesis, Prism, Findings, Observatory, and Method. It is not a permanent dashboard sidebar. The current section is indicated by label and rule weight, not color alone. A persistent evidence key appears only after S1 and can expand contextually.

## Source and caveat access

Each important observation and Finding has an “Evidence” control opening a source drawer with company, document, reporting period, page, and link. Global caveats live in a compact evidence key. Context-specific caveats appear beside the relevant metric version, derived interval, or event rail. A redirecting or unavailable link remains visible as “Source link unavailable”; the observation is never replaced.

## Loading and failure states

- Lazy series loading: three ledger rules and the text “Loading validated series…”; never a wall of skeleton cards.
- Series load failure: preserve identity and index metadata, then show “Series data unavailable” with retry and Method links.
- Invalid reference: show the affected evidence route as unavailable and retain the value only if it was already present in the validated detail payload.
- Empty event, claim, or Finding association: use “No curated event / issuer explanation / formal Finding in this window,” never an error style.
