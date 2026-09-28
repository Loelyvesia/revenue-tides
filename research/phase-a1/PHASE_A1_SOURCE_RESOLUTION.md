# PHASE A.1 — PUBLIC RELEASE SOURCE RESOLUTION

## Decision

**Status: CONDITIONAL PASS**

An official-disclosure-led quantitative project is feasible. Phase A.1 verified six exact longitudinal series and one transparently derived series across four usable reporting companies. Three series reach eight consecutive quarters and four more reach six. This clears the evidence-volume target without Sensor Tower or AppMagic as a redistributable backbone.

The pass remains conditional because the viable object is broader and coarser than the original mobile-monthly concept. Phase B may proceed only if the project is explicitly re-scoped to quarterly game/IP/franchise revenue across platforms, with metric-version breaks and publisher-defined entity scopes preserved.

## Recommended project definition

> **《付费潮汐——游戏商业生命线》 / Revenue Tides — The Commercial Life of Games** studies how officially disclosed game, IP, and franchise revenue changes by fiscal quarter. It compares only like-for-like series within stable reporting definitions and links major official product events to the quarter in which they occurred. It does not claim global consumer spending, and it does not treat corporate revenue, segment revenue, bookings, billings, royalties, or derived share allocations as interchangeable.

Recommended temporal unit: **fiscal quarter**. Half-year and annual values may be contextual cross-checks, not substitutes for missing quarters.

Recommended primary evidence:

- `OFFICIAL_REPORTED` exact title/IP revenue from public company IR materials.
- `DERIVED_FROM_OFFICIAL` only when the official denominator and official title share have the same period and scope, with the formula and rounding band retained.
- `EVENT_OFFICIAL` for period-linked event context.

## Companies tested

| Company | Result | Strongest public signal | Longest verified series |
| --- | --- | --- | ---: |
| NCSOFT | Usable | Exact mobile-title revenue in KRW million | 6 quarters before a royalty-allocation scope break |
| SHIFT UP | Usable | Exact IP revenue in KRW | 8 quarters |
| Netmarble | Usable with derivation | Total company revenue plus integer-percent title contribution | 6 quarters with uncertainty intervals |
| Nexon | Context only | Franchise commentary, growth metrics, and charts | No exact six-quarter series verified |
| Pearl Abyss | Usable | Exact IP revenue in KRW billion | 8 quarters |

Five companies were tested, below the ten-company ceiling.

## Verified quantitative backbone

| Series | Entity type | Evidence | Periods | Scope note |
| --- | --- | --- | ---: | --- |
| Goddess of Victory: NIKKE | IP | `OFFICIAL_REPORTED` | 2024Q3–2026Q2 (8) | SHIFT UP recognized IP revenue, not store spending |
| Stellar Blade | IP | `OFFICIAL_REPORTED` | 2024Q3–2026Q2 (8) | Console plus PC after the PC launch |
| Lineage M | Game title | `OFFICIAL_REPORTED` | 2024Q3–2025Q4 (6) | Mobile chart on the legacy reporting scope |
| Lineage 2M | Game title | `OFFICIAL_REPORTED` | 2024Q3–2025Q4 (6) | Mobile chart on the legacy reporting scope |
| Lineage W | Game title | `OFFICIAL_REPORTED` | 2024Q3–2025Q4 (6) | Mobile chart on the legacy reporting scope |
| Black Desert | IP | `OFFICIAL_REPORTED` | 2024Q3–2026Q2 (8) | Aggregates PC, console, and mobile editions |
| MARVEL Contest of Champions | Game title | `DERIVED_FROM_OFFICIAL` | 2024Q3–2025Q4 (6) | Company revenue × rounded title share |

This is a feasibility sample, not the future full corpus. An eventual curated set of roughly 8–12 strong series is realistic from the verified companies alone, while 20 should not be promised until additional continuity checks are completed.

## Company findings

### NCSOFT

The public [earnings archive](https://m-corporate.nc.com/kr/ir/irArchive/earningsRelease.do) exposes quarterly presentations and factsheets without login. Exact quarterly values for Lineage M, Lineage 2M, and Lineage W are available on presentation charts for six consecutive quarters from 2024Q3 through 2025Q4.

A metric-version break is mandatory after 2025Q4. The 2Q26 presentation states that royalties are integrated into IP revenue lines and restates a five-quarter window. The restated values must not be appended to the legacy series as if the definition were unchanged. AION 2 and Lineage Classic provide useful newer-game exceptions, but their histories are currently shorter than six quarters.

### SHIFT UP

The official [IR archive](https://shiftup.co.kr/eng/ir/ir.php?code=ir_eng&idx=475&page=1&ptype=list) covers every required quarter. The 4Q24 and 2Q26 factsheets provide exact NIKKE and Stellar Blade revenue rows in KRW on page 3, jointly covering 2024Q3–2026Q2. This is the cleanest tested source family.

The values are publisher-recognized IP revenue. They are not mobile-store estimates or gross consumer spending. Stellar Blade's 2025Q2 PC launch is an event within the stable IP series, not a reason to relabel the pre-launch quarters.

### Netmarble

Official quarterly decks publish consolidated revenue and the percentage contributed by leading titles. The denominator and title share refer to the same quarter and reporting entity, so a deterministic derivation is legitimate. However, the title shares are rounded to whole percentages. Every derived result therefore carries a range based on ±0.5 percentage point share rounding plus the disclosed total's rounding.

Example: 2025Q2 Netmarble revenue of KRW 717.6 billion × a 9% MARVEL Contest of Champions share = KRW 64.584 billion. The compatible range is approximately KRW 60.99–68.18 billion. The point estimate is `DERIVED_FROM_OFFICIAL`, never `OFFICIAL_REPORTED`.

### Nexon

The official [quarterly disclosure archive](https://www.nexon.co.jp/en/ir/quarterly-disclosure/) is public and useful for franchise narrative, growth rates, outlooks, and launch context. Phase A.1 did not verify a page-labeled exact six-quarter game/franchise revenue series for MapleStory, Dungeon&Fighter, FC, or ARC Raiders without relying on unlabeled chart geometry or mixing regional/product views.

Nexon therefore remains supplementary for this gate. Its IRPocket data feed also carries an explicit notice against unauthorized reproduction, transfer, sale, or other secondary use; the feed was not copied into the project.

### Pearl Abyss

The public [earnings archive](https://www.pearlabyss.com/en-US/IR/Data/Performance) provides a clean eight-quarter Black Desert IP series. The 2Q25 presentation page 6 covers 2024Q3–2025Q2, and the 2Q26 earnings letter page 3 covers 2025Q3–2026Q2. Values are exact at one decimal KRW billion.

The entity is the Black Desert IP across PC, console, and mobile. It cannot be presented as Black Desert Mobile revenue. EVE was excluded from the selected backbone because its divestment/discontinued-operation treatment creates a later scope discontinuity.

## Event-layer feasibility

Three official series passed the fiscal-period event-link test:

- **NIKKE, 2026Q2:** SHIFT UP's 2Q26 presentation pages 4 and 9 identifies the April 3.5th-anniversary update and discusses the same-quarter performance. The company's attribution may be stored as an `ATTRIBUTED_CLAIM`; it is not our causal conclusion.
- **Lineage M, 2025Q2:** NCSOFT's official [RISING STORM update page](https://about.ncsoft.com/news/article/lineagem_update_250618) records the June 18, 2025 update, which maps unambiguously to 2025Q2.
- **Black Desert IP, 2024Q3:** the official [Morning Light – Seoul update notice](https://blackdesert.pearlabyss.com/Asia/en-US/News/Notice/Detail?_boardNo=6377) announces a September 12, 2024 release, mapping to 2024Q3.

Allowed wording: “The event occurred in the same fiscal quarter as the reported observation.” Forbidden wording: “The event caused the quarterly change,” unless the statement is explicitly attributed to the reporting company or another named source.

## Metric compatibility

The project should use separate analytical lanes:

1. Exact official revenue within a stable title/IP definition.
2. Values derived from official total revenue and official title share.
3. Official event dates and attributed management explanations.
4. Company/segment totals as context only.

Cross-company level comparisons remain hazardous because publishers allocate royalties, platform receipts, licensing income, and consolidated subsidiaries differently. The strongest findings should be within-series change, duration, volatility, and event proximity—not a universal ranking of “true game revenue.”

## Mobile-only decision

Mobile-only remains possible but is materially weaker. It retains NIKKE and the three NCSOFT Lineage titles, plus derived Netmarble mobile titles, but loses the exact Black Desert and Stellar Blade series and becomes concentrated in three Korean publishers. Exact-value diversity falls and reliance on rounded-share derivations rises.

The evidence therefore supports **Option G: games across mobile, PC, and console where official product-level commercial disclosure exists**. Platform scope remains a field and a filter; it is not erased.

## Public-release and provenance assessment

All selected sources are reachable without login. None of the tested company sites grants a general open license for copying complete decks or charts. The safest public product is an original structured table of factual observations, formulas, units, page references, and canonical links. Do not ship copied presentation pages, ranking charts, or mirrored IR libraries.

No raw PDFs were retained in Phase A.1. This keeps disk use near zero and avoids unnecessary redistribution. If Phase B is authorized, retain only the minimum official documents needed for deterministic reconstruction, deduplicate company-quarter files, hash each retained file, and keep public distribution limited to structured observations unless source terms or permission clearly allow more.

Sensor Tower and AppMagic remain `SECONDARY_CONTEXT` / `INDUSTRY_CONTEXT` only and are not part of the distributable quantitative backbone.

## Gate conditions before Phase B

Phase B requires explicit approval of all of the following:

1. Freeze the title as **《付费潮汐——游戏商业生命线》**.
2. Freeze the primary time unit as **fiscal quarter**.
3. Use official title/IP/franchise revenue as the backbone; company and segment values remain context.
4. Preserve original currency, entity type, platform scope, reporting scope, evidence class, and metric-version breaks.
5. Label every share-derived value `DERIVED_FROM_OFFICIAL` and expose its formula and rounding interval.
6. Publish source-linked factual data rather than copied IR slides or mirrored PDF collections.
7. Exclude unresolved Nexon franchise amounts from the quantitative backbone until exact, page-labeled values are verified.
8. Treat events as contemporaneous context or attributed claims, never automatic causal proof.

## Stop boundary

Phase B, the full corpus, findings analysis, visual design, and frontend work were not started.

