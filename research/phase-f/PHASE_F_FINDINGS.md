# PHASE F — EVIDENCE-BOUNDED FINDINGS

## Decision

**Status: PASS**

**Method version:** `revenue-tides-method-freeze-1.0.0`  
**Findings version:** `revenue-tides-findings-1.0.0`  
**Data cutoff:** `2026-09-22`

The systematic pass evaluated all 12 stable metric windows, 66 normalized pair proposals, 26 curated event associations, three issuer claims, nine version overlaps, and 15 eligible derived changes. It generated 19 candidates, rejected 13 with reasons, and promoted six formal Findings.

## Formal Findings

### F1 — 同一季度，报告口径也会改变数值

在 2025Q2–2025Q4 的同季度重叠中，Lineage M 的 royalty-integrated 数值比 legacy 高 67.97亿–134.55亿韩元（5.6%–12.8%）；Lineage 2M 与 Lineage W 的对应差异为零。

- Scope/window: series_lineage_m, series_lineage_2m, series_lineage_w; 2025Q2–2025Q4.
- Metric/version: md_nc_lineage_2m_legacy_v1, md_nc_lineage_2m_royalty_v2, md_nc_lineage_m_legacy_v1, md_nc_lineage_m_royalty_v2, md_nc_lineage_w_legacy_v1, md_nc_lineage_w_royalty_v2; legacy_v1, royalty_v2.
- Evidence/strength: `DESCRIPTIVE`; `STRONG`.
- Limitation: The difference is a reporting-definition effect, not growth, a correction, or a restatement.
- Forbidden interpretation: Do not stitch versions or interpret same-quarter differences as commercial growth.

### F2 — Stellar Blade 的 PC 上线季度形成窗口峰值

Stellar Blade IP 收入从 2025Q1 的 70.12亿韩元升至 2025Q2 的 657.19亿韩元，环比增加 837.3%，并在 PC 上线同季度达到八季度窗口峰值。

- Scope/window: series_stellar_blade; 2025Q1–2025Q2.
- Metric/version: md_su_ip_revenue_v1; v1.
- Evidence/strength: `DESCRIPTIVE`; `STRONG`.
- Limitation: The publisher-defined IP total combines platform receipts and does not disclose a PC-only amount.
- Forbidden interpretation: This does not prove that the PC launch caused the increase or quantify PC-specific revenue.

### F3 — NIKKE 反弹，但尚未回到前高

NIKKE IP 收入在 2026Q2 环比增加 32.4% 至 432.66亿韩元，但仍比 2025Q2 的 451.12亿韩元峰值低 4.1%，因此状态是“在观察窗口内尚未恢复”。

- Scope/window: series_nikke; 2025Q2–2026Q2.
- Metric/version: md_su_ip_revenue_v1; v1.
- Evidence/strength: `DESCRIPTIVE`; `STRONG`.
- Limitation: The series is publisher-defined IP revenue and the event list is curated, not exhaustive.
- Forbidden interpretation: Do not claim the anniversary caused the rebound or that the remaining gap is permanent.

### F4 — Black Desert 在一次恢复后再次进入回撤

Black Desert IP 收入从 2024Q4 的 692亿韩元峰值回撤至 2025Q2 的 549亿韩元（-20.7%），三季度后在 2025Q3 升至 795亿韩元并恢复；到 2026Q2 又降至 550亿韩元，较新峰值低 30.8%，在观察窗口内尚未恢复。

- Scope/window: series_black_desert; 2024Q4–2026Q2.
- Metric/version: md_pa_black_desert_ip_v1; v1.
- Evidence/strength: `DESCRIPTIVE`; `STRONG`.
- Limitation: This is publisher-defined cross-platform IP revenue over eight quarters; later recovery cannot yet be observed.
- Forbidden interpretation: Do not describe the ending drawdown as a permanent decline.

### F5 — Lineage W 新口径窗口连续四季下降

在独立的 royalty-integrated v2 窗口内，Lineage W 从 2025Q2 的 476.40亿韩元连续四季下降至 2026Q2 的 308.33亿韩元，累计低 35.3%，且在观察窗口内尚未恢复。

- Scope/window: series_lineage_w; 2025Q2–2026Q2.
- Metric/version: md_nc_lineage_w_royalty_v2; royalty_v2.
- Evidence/strength: `DIRECT`; `MODERATE`.
- Limitation: The window contains five quarters and must not be extended backward across the version break.
- Forbidden interpretation: Do not stitch the legacy series to v2 or call the observed-window pattern permanent.

### F6 — 取整占比使多数派生环比方向无法确定

三个派生序列的 15 个可比较环比中，有 9 个（60.0%）在兼容取整区间内会改变方向，只有 6 个方向稳定。

- Scope/window: series_mcoc, series_jackpot_world, series_lotsa_slots; 2024Q3–2025Q4.
- Metric/version: md_nm_mcoc_derived_v1, md_nm_jackpot_world_derived_v1, md_nm_lotsa_slots_derived_v1; derived_v1.
- Evidence/strength: `DERIVED`; `STRONG`.
- Limitation: Applies to deterministic estimates from rounded official shares, not directly reported title revenue.
- Forbidden interpretation: Do not call issuers unreliable or present sign-sensitive changes as definite directions.

## Required test results

- Measurement semantics: promoted as F1. Same-quarter differences are definition effects, not growth.
- Derived uncertainty: promoted as F6. Phase E's 9/15 sign-sensitive result reproduces exactly; 6/15 are stable.
- Platform/event: promoted as F2. The PC launch and collaboration DLC occurred in Stellar Blade's 2025Q2 peak quarter; no PC-only amount or causal effect is inferred.
- Recovery: all requested series/windows were tested. Black Desert and NIKKE were promoted; Stellar Blade and stable NCSOFT windows remain documented candidates/rejections.
- Persistence: threshold was at least three consecutive non-zero same-direction changes inside one stable window. Lineage W v2 was promoted with four decreases.
- Volatility: CV, QoQ standard deviation, and median absolute QoQ were computed for every window. The common eight-quarter comparison was rejected as launch-quarter-sensitive.

## Issuer-attributed claim audit

- `claim_l2m_sea_q2_2025`: NCSOFT attributed the 2025Q2 Lineage 2M sales increase to Southeast Asia service expansion. Retained as issuer attribution only; not promoted.
- `claim_nikke_35_q2_2026`: SHIFT UP management linked 2026Q2 NIKKE growth/app-store performance to the 3.5th-anniversary update. Retained as issuer attribution only; F3 remains independently descriptive.
- `claim_stellar_base_effect_q2_2026`: SHIFT UP management described the 2026Q2 year-over-year decline as a 2025Q2 PC-launch base effect. Retained as issuer explanation only; F2 does not rely on it.

## Robustness and traceability

Every formal Finding has a machine-readable pack with valid observation and metric references, transformations, numeric claims, limitations, and forbidden interpretations. Leave-one-out checks were used where meaningful. All three issuer claims were audited; none became project causality and no formal Finding depends on one.

## Critical limitations

- Publisher-defined metrics are not true global game revenue or a common market measure.
- Cross-company absolute levels remain incompatible.
- Event coverage is curated and timing alone does not establish causality.
- NCSOFT legacy and royalty-integrated versions remain separate.
- Derived title estimates inherit rounded-share uncertainty.
- Observed-window non-recovery is not permanent decline.

## Boundary

No corpus expansion, new quarters, external quantitative data, web-data shaping, IA, visual design, frontend, or Phase G work was performed.

`STOPPED BEFORE PHASE G`
