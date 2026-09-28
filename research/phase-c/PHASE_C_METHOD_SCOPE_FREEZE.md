# PHASE C — METHOD / SCOPE FREEZE

## Decision

**Status: PASS**

**Method version:** `revenue-tides-method-freeze-1.0.0`

**Freeze date:** `2026-09-22`

This contract freezes the analytical scope and methodology for 《付费潮汐——游戏商业生命线》 / Revenue Tides — The Commercial Life of Games. Later phases must follow it unless a documented method amendment increments the version and identifies the reason, affected fields and observations, rebuild requirement, and effect on existing Findings.

## Frozen project definition

> 《付费潮汐——游戏商业生命线》研究上市游戏公司公开披露资料中，游戏、IP 或 franchise 商业收入指标随财政季度发生的变化。项目以发行商定义的实体与财务口径为基础，重点分析同一稳定指标序列内部的变化、持续性、波动、恢复、平台扩张及同期官方事件。项目不试图重建“全球真实游戏流水”，也不把不同公司的会计口径视为统一市场指标。

> Revenue Tides studies fiscal-quarter changes in officially disclosed revenue metrics for publisher-defined games, IPs, and franchises. It prioritizes within-series change under stable reporting definitions and links official product events as contemporaneous context. It does not reconstruct true global consumer spending and does not assume different publishers' accounting metrics are directly comparable.

## Frozen scope

- Primary temporal unit: `FISCAL_QUARTER`.
- Analytical corpus target: 10 series; allowed range 8–12; hard maximum 12.
- Normal core continuity: at least 6 consecutive fiscal quarters; 8 preferred.
- Launch Cohort: at least 4 consecutive quarters; maximum 2 series.
- Quantitative evidence: `OFFICIAL_REPORTED` and `DERIVED_FROM_OFFICIAL` only.
- At least two-thirds of analytical series must be primarily direct official series; no more than one-third may be primarily derived.
- Industry estimates are outside the primary quantitative corpus.
- Cross-company absolute level comparison is forbidden by default.
- Stable within-series change and unitless trajectory comparison are permitted under the contracts below.

## Phase B compatibility

The five pilot series conform. Four of five are primarily direct official series. MCOC is the sole derived series. NIKKE, Stellar Blade, Black Desert, Lineage M legacy v1, and MCOC each meet the six-quarter core threshold. Lineage M v2 is a metric-version window for the same analytical series, not a separate corpus member. No Phase B observation or source was changed.

## Stop boundary

Phase D data acquisition, corpus expansion, Findings, visualization, and frontend work were not started.

`STOPPED BEFORE PHASE D`
