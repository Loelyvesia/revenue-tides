#!/usr/bin/env python3
"""Comprehensive structural, semantic, and reproducibility validation for Phase E."""

from __future__ import annotations

import calendar
import csv
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR
from pathlib import Path
from statistics import median


ROOT = Path(__file__).resolve().parents[2]
PD = ROOT / "data" / "phase-d"
DATA = ROOT / "data" / "phase-e"
RESEARCH = ROOT / "research" / "phase-e"
PHASE_C = ROOT / "research" / "phase-c"
BUILD_D = ROOT / "scripts" / "phase_d" / "build_corpus.py"
BUILD_E = ROOT / "scripts" / "phase_e" / "build_phase_e.py"
METHOD = "revenue-tides-method-freeze-1.0.0"

REQUIRED_RESEARCH = [
    "PHASE_E_DATA_QUALITY.md", "series_reconciliation.csv",
    "observation_grid_reconciliation.md", "version_overlap_matrix.csv",
    "entity_identity_audit.md", "fiscal_chronology_audit.md",
    "continuity_audit.md", "metric_semantics_audit.md",
    "comparability_audit.md", "evidence_class_audit.md",
    "derivation_revalidation.md", "derived_uncertainty_sensitivity.csv",
    "missingness_audit.md", "zero_audit.md",
    "transformation_revalidation.md", "event_structural_audit.md",
    "attributed_claim_audit.md", "provenance_audit.md",
    "public_internal_separation_audit.md", "value_anomaly_audit.csv",
    "defect_log.csv", "data_corrections.csv",
    "deterministic_rebuild_audit.md", "storage_audit.md",
    "phase_e_summary.json", "manual_qa.csv",
]
REQUIRED_DATA = ["findings_ready_observations.csv", "findings_readiness_manifest.json"]
CANONICAL_D = [
    "series.csv", "entities.csv", "companies.csv", "fiscal_periods.csv",
    "metric_definitions.csv", "sources.csv", "observations.csv",
    "derivations.csv", "events.csv", "attributed_claims.csv",
    "expected_period_grid.csv", "change_features.csv",
    "comparability_matrix.csv", "raw_manifest.csv",
    "public_release_observations.csv", "public_release_events.csv",
    "corpus_manifest.json",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def qkey(label: str) -> tuple[int, int]:
    return int(label[:4]), int(label[-1])


def d(value: str) -> Decimal:
    return Decimal(value)


def deq(actual: str, expected: Decimal) -> bool:
    return actual != "" and d(actual) == expected


def sign(value: Decimal) -> str:
    return "POSITIVE" if value > 0 else "NEGATIVE" if value < 0 else "ZERO"


def main() -> int:
    results: list[tuple[str, bool, str]] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        results.append((name, bool(condition), detail))

    # Required outputs and parseability.
    check("001_required_phase_e_research_files_exist", all((RESEARCH / name).is_file() for name in REQUIRED_RESEARCH))
    check("002_required_phase_e_data_files_exist", all((DATA / name).is_file() for name in REQUIRED_DATA))
    check("003_phase_e_builder_exists", BUILD_E.is_file())
    check("004_phase_e_validator_exists", Path(__file__).is_file())
    phase_e_csvs = list(RESEARCH.glob("*.csv")) + list(DATA.glob("*.csv"))
    phase_e_jsons = list(RESEARCH.glob("*.json")) + list(DATA.glob("*.json"))
    check("005_phase_e_csvs_parse", all(isinstance(read_csv(path), list) for path in phase_e_csvs))
    json_ok = True
    for path in phase_e_jsons:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            json_ok = False
    check("006_phase_e_jsons_parse", json_ok)
    check("007_canonical_phase_d_csvs_parse", all(isinstance(read_csv(PD / name), list) for name in CANONICAL_D if name.endswith(".csv")))
    check("008_canonical_phase_d_json_parses", isinstance(json.loads((PD / "corpus_manifest.json").read_text(encoding="utf-8")), dict))

    series = read_csv(PD / "series.csv")
    entities = read_csv(PD / "entities.csv")
    companies = read_csv(PD / "companies.csv")
    periods = read_csv(PD / "fiscal_periods.csv")
    metrics = read_csv(PD / "metric_definitions.csv")
    sources = read_csv(PD / "sources.csv")
    observations = read_csv(PD / "observations.csv")
    derivations = read_csv(PD / "derivations.csv")
    events = read_csv(PD / "events.csv")
    claims = read_csv(PD / "attributed_claims.csv")
    grid = read_csv(PD / "expected_period_grid.csv")
    changes = read_csv(PD / "change_features.csv")
    comparisons = read_csv(PD / "comparability_matrix.csv")
    raw = read_csv(PD / "raw_manifest.csv")
    public_obs = read_csv(PD / "public_release_observations.csv")
    public_events = read_csv(PD / "public_release_events.csv")
    extracts = read_csv(PD / "input" / "manual_extractions.csv")
    series_rec = read_csv(RESEARCH / "series_reconciliation.csv")
    overlap = read_csv(RESEARCH / "version_overlap_matrix.csv")
    sensitivity = read_csv(RESEARCH / "derived_uncertainty_sensitivity.csv")
    anomalies = read_csv(RESEARCH / "value_anomaly_audit.csv")
    defects = read_csv(RESEARCH / "defect_log.csv")
    corrections = read_csv(RESEARCH / "data_corrections.csv")
    manual_qa = read_csv(RESEARCH / "manual_qa.csv")
    findings = read_csv(DATA / "findings_ready_observations.csv")
    manifest_d = json.loads((PD / "corpus_manifest.json").read_text(encoding="utf-8"))
    manifest_e = json.loads((DATA / "findings_readiness_manifest.json").read_text(encoding="utf-8"))
    summary_e = json.loads((RESEARCH / "phase_e_summary.json").read_text(encoding="utf-8"))
    freeze = json.loads((PHASE_C / "method_freeze_manifest.json").read_text(encoding="utf-8"))

    smap = {r["series_id"]: r for r in series}
    emap = {r["entity_id"]: r for r in entities}
    cmap = {r["company_id"]: r for r in companies}
    pmap = {r["fiscal_period_id"]: r for r in periods}
    mmap = {r["metric_definition_id"]: r for r in metrics}
    srcmap = {r["source_id"]: r for r in sources}
    entity_to_series = {r["entity_id"]: r["series_id"] for r in series}
    obsmap = {r["observation_id"]: r for r in observations}
    drvmap = {r["derivation_id"]: r for r in derivations}
    changemap = {r["observation_id"]: r for r in changes}

    # Freeze and corpus invariants.
    check("009_phase_c_freeze_has_18_documents", len(freeze["method_hashes"]) == 18)
    check("010_phase_c_freeze_hashes_validate", all(sha256(PHASE_C / name) == expected for name, expected in freeze["method_hashes"].items()))
    check("011_method_version_unchanged", manifest_d["method_version"] == manifest_e["method_version"] == summary_e["method_version"] == METHOD)
    check("012_corpus_contains_exactly_9_series", len(series) == 9)
    check("013_no_new_series_introduced", set(smap) == set(manifest_d["series_ids"]))
    check("014_exactly_4_selected_companies", len({r["company_id"] for r in series}) == 4)
    check("015_no_new_company_introduced", {r["company_id"] for r in series} == set(manifest_d["unique_companies"]))
    check("016_data_cutoff_unchanged", manifest_d["data_cutoff"] == manifest_e["data_cutoff"] == "2026-09-22")
    check("017_no_launch_cohort", all(r["cohort_type"] == "CORE" for r in series))
    check("018_no_future_series_window", all(r["analysis_window_end"] <= "2026-06-30" for r in series))

    # Primary keys.
    for no, name, rows_, key in [
        (19, "series", series, "series_id"), (20, "entity", entities, "entity_id"),
        (21, "company", companies, "company_id"), (22, "fiscal_period", periods, "fiscal_period_id"),
        (23, "metric_definition", metrics, "metric_definition_id"), (24, "source", sources, "source_id"),
        (25, "observation", observations, "observation_id"), (26, "derivation", derivations, "derivation_id"),
        (27, "event", events, "event_id"), (28, "claim", claims, "claim_id"),
    ]:
        check(f"{no:03d}_{name}_ids_unique", len({r[key] for r in rows_}) == len(rows_))

    # Effective and semantic observation uniqueness.
    effective_keys = [(entity_to_series[r["entity_id"]], r["fiscal_period_id"], r["metric_definition_id"], r["evidence_class"]) for r in observations]
    semantic_keys = [(r["entity_id"], r["fiscal_period_id"], r["metric_version"], r["value_krw_million"], r["source_id"]) for r in observations]
    check("029_effective_observation_keys_unique", len(set(effective_keys)) == len(effective_keys))
    check("030_no_semantic_duplicate_observation", len(set(semantic_keys)) == len(semantic_keys))
    check("031_no_duplicate_manual_extraction_id", len({r["extraction_id"] for r in extracts}) == len(extracts))
    check("032_no_direct_derived_copy_collision", not any(a["entity_id"] == b["entity_id"] and a["fiscal_period_id"] == b["fiscal_period_id"] and a["value_krw_million"] == b["value_krw_million"] and a["evidence_class"] != b["evidence_class"] for i, a in enumerate(observations) for b in observations[i + 1:]))

    # Foreign keys.
    entity_ids, company_ids = set(emap), set(cmap)
    period_ids, metric_ids, source_ids = set(pmap), set(mmap), set(srcmap)
    derivation_ids, observation_ids = set(drvmap), set(obsmap)
    check("033_series_entity_fks_resolve", all(r["entity_id"] in entity_ids for r in series))
    check("034_series_company_fks_resolve", all(r["company_id"] in company_ids for r in series))
    check("035_observation_entity_fks_resolve", all(r["entity_id"] in entity_ids for r in observations))
    check("036_observation_company_fks_resolve", all(r["company_id"] in company_ids for r in observations))
    check("037_observation_period_fks_resolve", all(r["fiscal_period_id"] in period_ids for r in observations))
    check("038_observation_metric_fks_resolve", all(r["metric_definition_id"] in metric_ids for r in observations))
    check("039_observation_source_fks_resolve", all(r["source_id"] in source_ids for r in observations))
    check("040_observation_derivation_fks_resolve", all(not r["derivation_id"] or r["derivation_id"] in derivation_ids for r in observations))
    check("041_event_fks_resolve", all(r["entity_id"] in entity_ids and r["fiscal_period_id"] in period_ids and r["source_id"] in source_ids for r in events))
    check("042_claim_fks_resolve", all(r["entity_id"] in entity_ids and r["fiscal_period_id"] in period_ids and r["source_id"] in source_ids for r in claims))
    extract_ids = {r["extraction_id"] for r in extracts}
    check("043_derivation_input_fks_resolve", all(r["source_total_id"] in extract_ids and r["source_share_id"] in extract_ids for r in derivations))
    check("044_grid_fks_resolve", all(r["series_id"] in smap and r["fiscal_period_id"] in period_ids for r in grid))
    check("045_change_fks_resolve", set(changemap) == observation_ids)
    check("046_comparability_metric_fks_resolve", all(r["left_metric_definition_id"] in metric_ids and r["right_metric_definition_id"] in metric_ids for r in comparisons))

    # Fiscal period and chronology.
    selected_company_ids = {r["company_id"] for r in series}
    check("047_companies_calendar_aligned", all(r["source_status"] == "PUBLIC_OFFICIAL_VERIFIED" and "Calendar-year fiscal reporting" in r["fiscal_calendar_note"] and "quarter labels verified" in r["fiscal_calendar_note"] for r in companies if r["company_id"] in selected_company_ids))
    bounds_ok = all(date.fromisoformat(r["period_start"]) < date.fromisoformat(r["period_end"]) for r in periods)
    check("048_period_start_before_end", bounds_ok)
    quarter_bounds_ok = True
    labels_ok = True
    for r in periods:
        year, quarter = int(r["fiscal_year_label"]), int(r["fiscal_quarter_label"][1:])
        month_start = (quarter - 1) * 3 + 1
        expected_start = date(year, month_start, 1)
        month_end = month_start + 2
        expected_end = date(year, month_end, calendar.monthrange(year, month_end)[1])
        quarter_bounds_ok &= date.fromisoformat(r["period_start"]) == expected_start and date.fromisoformat(r["period_end"]) == expected_end
        labels_ok &= r["calendar_quarter_equivalent"] == f"{year}Q{quarter}"
    check("049_calendar_quarter_bounds_reproduce", quarter_bounds_ok)
    check("050_quarter_labels_match_dates", labels_ok)
    no_overlap = True
    for company in selected_company_ids:
        rows_ = sorted((r for r in periods if r["company_id"] == company), key=lambda r: r["period_start"])
        no_overlap &= all(rows_[i]["period_start"] > rows_[i - 1]["period_end"] for i in range(1, len(rows_)))
    check("051_no_overlapping_fiscal_periods", no_overlap)
    check("052_publication_dates_separate", all(r["published_at"] and r["fiscal_period_id"] for r in observations))
    check("053_publication_after_period_end", all(date.fromisoformat(r["published_at"]) > date.fromisoformat(pmap[r["fiscal_period_id"]]["period_end"]) for r in observations))
    check("054_event_dates_map_to_period", all(date.fromisoformat(pmap[r["fiscal_period_id"]]["period_start"]) <= date.fromisoformat(r["event_date_start"]) <= date.fromisoformat(pmap[r["fiscal_period_id"]]["period_end"]) for r in events))

    # Continuity and grid reconciliation.
    grid_by_series: dict[str, list[dict]] = defaultdict(list)
    obs_by_series: dict[str, list[dict]] = defaultdict(list)
    for r in grid:
        grid_by_series[r["series_id"]].append(r)
    for r in observations:
        obs_by_series[entity_to_series[r["entity_id"]]].append(r)
    check("055_expected_grid_has_66_rows", len(grid) == 66)
    check("056_expected_grid_pairs_unique", len({(r["series_id"], r["fiscal_period_id"]) for r in grid}) == len(grid))
    check("057_six_series_have_8_periods", sum(len(v) == 8 for v in grid_by_series.values()) == 6)
    check("058_three_series_have_6_periods", sum(len(v) == 6 for v in grid_by_series.values()) == 3)
    check("059_all_series_have_6_period_minimum", all(len(v) >= 6 for v in grid_by_series.values()))
    consecutive_ok = True
    for rows_ in grid_by_series.values():
        labels = sorted([pmap[r["fiscal_period_id"]]["calendar_quarter_equivalent"] for r in rows_], key=qkey)
        ordinals = [year * 4 + quarter for year, quarter in map(qkey, labels)]
        consecutive_ok &= all(ordinals[i] == ordinals[i - 1] + 1 for i in range(1, len(ordinals)))
    check("060_all_series_periods_consecutive", consecutive_ok)
    check("061_grid_reconstructs_analysis_windows", all(min(pmap[r["fiscal_period_id"]]["period_start"] for r in grid_by_series[s["series_id"]]) == s["analysis_window_start"] and max(pmap[r["fiscal_period_id"]]["period_end"] for r in grid_by_series[s["series_id"]]) == s["analysis_window_end"] for s in series))
    check("062_every_grid_row_available", all(r["missingness_state"] == "AVAILABLE" and r["observation_id"] for r in grid))
    check("063_grid_observation_ids_resolve", all(all(oid in observation_ids for oid in r["observation_id"].split("|")) for r in grid))
    check("064_canonical_observation_count_75", len(observations) == 75)
    check("065_unique_series_period_count_66", len({(entity_to_series[r["entity_id"]], r["fiscal_period_id"]) for r in observations}) == 66)
    check("066_metric_overlap_additions_9", len(observations) - len(grid) == 9 and len(overlap) == 9)
    check("067_overlap_only_three_lineage_series", {r["series_id"] for r in overlap} == {"series_lineage_m", "series_lineage_2m", "series_lineage_w"})
    check("068_overlap_only_2025q2_to_q4", {r["quarter"] for r in overlap} == {"2025Q2", "2025Q3", "2025Q4"})
    check("069_each_overlap_series_contributes_3", all(count == 3 for count in Counter(r["series_id"] for r in overlap).values()))
    check("070_observation_equation_reconciles", 66 + 9 == len(observations))

    # Entity identity.
    expected_types = {
        "series_nikke": "IP", "series_stellar_blade": "IP", "series_black_desert": "IP",
        "series_lineage_m": "GAME_TITLE", "series_lineage_2m": "GAME_TITLE", "series_lineage_w": "GAME_TITLE",
        "series_mcoc": "GAME_TITLE", "series_jackpot_world": "GAME_TITLE", "series_lotsa_slots": "GAME_TITLE",
    }
    check("071_entity_types_match_frozen_scope", all(smap[sid]["entity_type"] == etype for sid, etype in expected_types.items()))
    check("072_nikke_remains_ip", smap["series_nikke"]["entity_type"] == "IP")
    check("073_stellar_blade_remains_ip", smap["series_stellar_blade"]["entity_type"] == "IP")
    check("074_black_desert_remains_ip", smap["series_black_desert"]["entity_type"] == "IP")
    check("075_mcoc_remains_game_title", smap["series_mcoc"]["entity_type"] == "GAME_TITLE")
    check("076_lineage_titles_remain_game_title", all(smap[sid]["entity_type"] == "GAME_TITLE" for sid in ["series_lineage_m", "series_lineage_2m", "series_lineage_w"]))
    check("077_slot_titles_remain_game_title", all(smap[sid]["entity_type"] == "GAME_TITLE" for sid in ["series_jackpot_world", "series_lotsa_slots"]))
    check("078_selected_entities_have_identity_status", all(emap[r["entity_id"]]["identity_status"] for r in series))
    check("079_series_platform_scope_explicit", all(r["platform_scope"] for r in series))

    # Metric semantics, validity, and version isolation.
    used_metric_ids = {r["metric_definition_id"] for r in observations}
    semantic_fields = ["metric_name", "reporting_company_id", "entity_scope", "economic_meaning", "accounting_scope", "platform_scope", "geographic_scope", "includes_royalties", "includes_licensing", "unit_basis", "valid_from", "metric_version", "comparable_group_id"]
    check("080_used_metric_definitions_complete", all(all(mmap[mid][field] for field in semantic_fields) for mid in used_metric_ids))
    check("081_unknown_metric_semantics_explicit", all(mmap[mid]["includes_licensing"] != "" and mmap[mid]["includes_platform_receipts"] != "" for mid in used_metric_ids))
    check("082_metric_reporting_company_matches_observation", all(mmap[r["metric_definition_id"]]["reporting_company_id"] == r["company_id"] for r in observations))
    validity_ok = True
    for r in observations:
        metric, period = mmap[r["metric_definition_id"]], pmap[r["fiscal_period_id"]]
        validity_ok &= period["period_start"] >= metric["valid_from"] and (not metric["valid_to"] or period["period_end"] <= metric["valid_to"])
    check("083_observations_inside_metric_validity", validity_ok)
    check("084_open_ended_metric_windows_documented", all(r["valid_from"] for r in metrics if not r["valid_to"]))
    for no, sid in [(85, "series_lineage_m"), (86, "series_lineage_2m"), (87, "series_lineage_w")]:
        rows_ = obs_by_series[sid]
        check(f"{no:03d}_{sid}_versions_separate", {r["metric_version"] for r in rows_} == {"legacy_v1", "royalty_integrated_v2"} and len({r["comparable_group_id"] for r in rows_}) == 2)
    check("088_no_version_overwrite", all(r["legacy_observation_id"] in observation_ids and r["new_observation_id"] in observation_ids for r in overlap))
    check("089_overlap_definitions_are_distinct", all(r["legacy_metric_definition_id"] != r["new_metric_definition_id"] for r in overlap))
    check("090_overlap_qoq_forbidden", all(r["qoq_between_versions_allowed"] == "NO" for r in overlap))

    # Comparability.
    allowed_comparability = set(freeze["comparability_classes"])
    check("091_comparability_classes_valid", all(r["comparability_status"] in allowed_comparability for r in comparisons))
    check("092_self_windows_within_series_only", all(r["comparability_status"] == "WITHIN_SERIES_ONLY" for r in comparisons if r["left_series_id"] == r["right_series_id"]))
    check("093_same_entity_cross_version_is_version_break", all(r["comparability_status"] == "VERSION_BREAK" for r in comparisons if r["left_entity_id"] == r["right_entity_id"] and r["left_metric_definition_id"] != r["right_metric_definition_id"]))
    check("094_cross_entity_absolute_not_comparable", all(r["comparability_status"] == "NOT_COMPARABLE" for r in comparisons if r["left_entity_id"] != r["right_entity_id"]))
    check("095_no_directly_comparable_relationship", all(r["comparability_status"] != "DIRECTLY_COMPARABLE" for r in comparisons))

    # Evidence classes and ratios.
    direct_series = [r for r in series if r["primary_evidence_class"] == "OFFICIAL_REPORTED"]
    derived_series = [r for r in series if r["primary_evidence_class"] == "DERIVED_FROM_OFFICIAL"]
    direct_obs = [r for r in observations if r["evidence_class"] == "OFFICIAL_REPORTED"]
    derived_obs = [r for r in observations if r["evidence_class"] == "DERIVED_FROM_OFFICIAL"]
    check("096_six_direct_series", len(direct_series) == 6)
    check("097_three_derived_series", len(derived_series) == 3)
    check("098_derived_series_ratio_at_most_one_third", len(derived_series) * 3 <= len(series))
    check("099_direct_series_ratio_at_least_two_thirds", len(direct_series) * 3 >= len(series) * 2)
    check("100_only_allowed_quantitative_evidence_classes", all(r["evidence_class"] in freeze["allowed_quantitative_evidence_classes"] for r in observations))
    check("101_no_industry_estimate", all(r["evidence_class"] != "INDUSTRY_ESTIMATE" for r in observations))
    check("102_direct_observation_count_57", len(direct_obs) == 57)
    check("103_derived_observation_count_18", len(derived_obs) == 18)
    check("104_derived_series_are_expected_titles", {entity_to_series[r["entity_id"]] for r in derived_obs} == {"series_mcoc", "series_jackpot_world", "series_lotsa_slots"})

    # Derivation reproduction and unit normalization.
    derivation_ok = interval_ok = ordered_ok = True
    max_discrepancy = Decimal(0)
    for row in derivations:
        total, share = d(row["input_total_value"]), d(row["input_share_percent"])
        point = total * share / 100
        low = (total * (share - Decimal("0.5")) / 100).quantize(Decimal("0.01"), rounding=ROUND_FLOOR)
        high = (total * (share + Decimal("0.5")) / 100).quantize(Decimal("0.01"), rounding=ROUND_CEILING)
        derivation_ok &= d(row["point_estimate"]) == point
        interval_ok &= d(row["lower_bound"]) == low and d(row["upper_bound"]) == high
        ordered_ok &= low <= point <= high
        max_discrepancy = max(max_discrepancy, abs(d(row["point_estimate"]) - point), abs(d(row["lower_bound"]) - low), abs(d(row["upper_bound"]) - high))
    check("105_every_derived_observation_has_derivation", all(r["derivation_id"] in derivation_ids for r in derived_obs))
    check("106_all_derivations_reproduce_decimal", derivation_ok)
    check("107_all_uncertainty_bounds_reproduce", interval_ok)
    check("108_lower_point_upper_ordered", ordered_ok)
    check("109_max_arithmetic_discrepancy_zero", max_discrepancy == 0)
    check("110_rounding_increment_present", all(r["share_rounding_increment"] == "1 percentage point" for r in derivations))
    check("111_rounding_interval_is_half_point", all("+/-0.5pp" in r["calculation_method"] for r in derivations))
    check("112_derived_observation_values_match", all(d(r["value_krw_million"]) == d(drvmap[r["derivation_id"]]["point_estimate"]) * 1000 for r in derived_obs))
    check("113_derived_observation_bounds_match", all(d(r["lower_bound_krw_million"]) == d(drvmap[r["derivation_id"]]["lower_bound"]) * 1000 and d(r["upper_bound_krw_million"]) == d(drvmap[r["derivation_id"]]["upper_bound"]) * 1000 for r in derived_obs))
    check("114_original_value_and_unit_retained", all(r["reported_value_raw"] and r["reported_unit_raw"] for r in observations))
    check("115_all_observation_currencies_krw", all(r["currency"] == "KRW" for r in observations))
    check("116_no_fx_conversion", all("USD" not in " ".join(r.values()) and "exchange rate" not in " ".join(r.values()).lower() for r in observations))
    scaling_ok = True
    for r in observations:
        raw_value = d(r["reported_value_raw"])
        expected = raw_value / 1_000_000 if r["reported_unit_raw"] == "KRW" else raw_value if r["reported_unit_raw"] == "KRW_million" else raw_value * 1000 if r["reported_unit_raw"] == "KRW_billion" else None
        scaling_ok &= expected is not None and d(r["value_krw_million"]) == expected
    check("117_same_currency_scaling_reproduces", scaling_ok)
    check("118_all_revenue_values_finite_nonnegative", all(d(r["value_krw_million"]).is_finite() and d(r["value_krw_million"]) >= 0 for r in observations))
    check("119_all_shares_in_valid_range", all(0 <= d(r["input_share_percent"]) <= 100 for r in derivations))

    # Zero, null, missingness, and forbidden fill.
    check("120_no_primary_observation_value_zero", all(d(r["value_krw_million"]) != 0 for r in observations))
    check("121_no_missing_value_encoded_zero", all(not (r["missingness_state"] != "AVAILABLE" and r["value_krw_million"] in {"0", "0.0", "0.00"}) for r in observations))
    check("122_every_numeric_zero_is_transformation_supported", all(not r[field] or d(r[field]).is_finite() for r in changes for field in ["qoq_absolute_change_krw_million", "qoq_percent_change", "drawdown_pct", "recovery_quarters"]))
    corpus_text = "\n".join(path.read_text(encoding="utf-8") for path in list(PD.glob("*.csv")) + [PD / "corpus_manifest.json"])
    lowered = corpus_text.lower()
    check("123_no_nan_token", re.search(r"(?<![A-Za-z0-9_])nan(?![A-Za-z0-9_])", lowered) is None)
    check("124_no_infinity_token", "infinity" not in lowered and "-infinity" not in lowered)
    check("125_no_undefined_token", "undefined" not in lowered)
    check("126_no_string_null_or_none", not any(token in lowered for token in ['"null"', ',null,', '"none"', ',none,']))
    allowed_missing = set(freeze["missingness_states"])
    check("127_no_undocumented_missingness_state", all(r["missingness_state"] in allowed_missing for r in observations + grid))
    check("128_no_interpolation", "interpolat" not in " ".join(" ".join(r.values()) for r in observations).lower())
    check("129_no_forward_fill", "forward fill" not in " ".join(" ".join(r.values()) for r in observations).lower() and "forward-fill" not in " ".join(" ".join(r.values()) for r in observations).lower())
    check("130_no_synthetic_future_quarter", all(pmap[r["fiscal_period_id"]]["period_end"] <= "2026-06-30" for r in observations))

    # Independent transformation reproduction, scoped by series and comparable group.
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in observations:
        groups[(entity_to_series[r["entity_id"]], r["comparable_group_id"])].append(r)
    qoq_ok = baseline_ok = peak_ok = drawdown_ok = recovery_ok = volatility_ok = True
    boundary_ok = first_flags_ok = True
    for (sid, group_id), rows_ in groups.items():
        rows_.sort(key=lambda r: qkey(pmap[r["fiscal_period_id"]]["calendar_quarter_equivalent"]))
        vals = [d(r["value_krw_million"]) for r in rows_]
        mean = sum(vals) / len(vals)
        variance = sum((v - mean) ** 2 for v in vals) / len(vals)
        cv = variance.sqrt() / mean * 100
        qoqs = [(vals[i] - vals[i - 1]) / vals[i - 1] * 100 for i in range(1, len(vals))]
        qmean = sum(qoqs) / len(qoqs)
        qstd = (sum((q - qmean) ** 2 for q in qoqs) / len(qoqs)).sqrt()
        med_abs = Decimal(str(median([float(abs(q)) for q in qoqs])))
        rolling_peak, peak_index, active = vals[0], 0, False
        for i, obs in enumerate(rows_):
            out, value = changemap[obs["observation_id"]], vals[i]
            prev, prior_peak = vals[i - 1] if i else None, rolling_peak
            recovered = active and value >= prior_peak
            if value < prior_peak:
                active = True
                exp_drawdown = (value - prior_peak) / prior_peak * 100
                exp_trough = min(vals[peak_index:i + 1])
                exp_status = "NOT_RECOVERED_WITHIN_OBSERVED_WINDOW" if i == len(rows_) - 1 else "DRAWDOWN_ACTIVE"
                exp_recovery_quarters = ""
            else:
                exp_drawdown = Decimal(0)
                exp_trough = min(vals[peak_index:i + 1]) if recovered else value
                exp_status = "AT_OR_ABOVE_ROLLING_PEAK"
                exp_recovery_quarters = str(i - peak_index) if recovered else ""
                rolling_peak, peak_index, active = value, i, False
            qoq_ok &= (out["qoq_absolute_change_krw_million"] == "" if prev is None else deq(out["qoq_absolute_change_krw_million"], value - prev))
            qoq_ok &= (out["qoq_percent_change"] == "" if prev is None else deq(out["qoq_percent_change"], (value - prev) / prev * 100))
            baseline_ok &= deq(out["baseline_index"], value / vals[0] * 100) and out["baseline_origin_observation_id"] == rows_[0]["observation_id"]
            peak_ok &= deq(out["rolling_peak_krw_million"], rolling_peak) and deq(out["prior_peak_value_krw_million"], prior_peak)
            drawdown_ok &= deq(out["drawdown_pct"], exp_drawdown) and deq(out["trough_since_peak_krw_million"], exp_trough)
            recovery_ok &= out["recovery_status"] == exp_status and out["recovery_quarters"] == exp_recovery_quarters and "PERMANENT_DECLINE" not in out["recovery_status"]
            volatility_ok &= deq(out["within_series_range_krw_million"], max(vals) - min(vals)) and deq(out["coefficient_of_variation_pct"], cv) and deq(out["stddev_qoq_percent_change"], qstd) and deq(out["median_absolute_qoq_change"], med_abs)
            first_flags_ok &= (i != 0 or (out["previous_observation_id"] == "" and out["baseline_index"] == "100"))
            if out["previous_observation_id"]:
                prev_obs = obsmap[out["previous_observation_id"]]
                boundary_ok &= entity_to_series[prev_obs["entity_id"]] == sid and prev_obs["comparable_group_id"] == group_id and prev_obs["metric_version"] == obs["metric_version"]
    check("131_qoq_reproduces", qoq_ok)
    check("132_baseline_index_reproduces", baseline_ok)
    check("133_rolling_peak_reproduces", peak_ok)
    check("134_drawdown_reproduces", drawdown_ok)
    check("135_recovery_reproduces", recovery_ok)
    check("136_volatility_metrics_reproduce", volatility_ok)
    check("137_transformations_stay_inside_series_groups", boundary_ok)
    check("138_first_window_rows_restart_baseline", first_flags_ok)
    check("139_change_row_count_matches_observations", len(changes) == len(observations))
    check("140_nikke_stellar_no_longer_cross_linked", all((not r["previous_observation_id"] or entity_to_series[obsmap[r["previous_observation_id"]]["entity_id"]] == r["series_id"]) for r in changes if r["series_id"] in {"series_nikke", "series_stellar_blade"}))

    # Events, claims, and causality.
    check("141_event_count_26", len(events) == 26)
    check("142_every_event_uses_official_source", all(srcmap[r["source_id"]]["officiality"] == "OFFICIAL" for r in events))
    check("143_every_event_inside_selected_corpus", all(r["entity_id"] in entity_to_series for r in events))
    check("144_event_precision_declared", all(r["date_precision"] in {"DAY", "MONTH", "QUARTER"} for r in events))
    check("145_event_platform_and_region_present", all(r["platform_scope"] and r["region_scope"] for r in events))
    caveat_text = (RESEARCH / "event_structural_audit.md").read_text(encoding="utf-8").lower()
    check("146_event_coverage_marked_curated", "curated" in caveat_text and "non-exhaustive" in caveat_text)
    check("147_event_absence_caveat_present", "absence" in caveat_text and "must never" in caveat_text)
    check("148_claim_count_3", len(claims) == 3)
    check("149_claims_have_required_fields", all(r["attributed_to"] and r["claim_summary"] and r["claim_type"] and r["source_id"] for r in claims))
    check("150_claims_remain_separate", all("ATTRIBUTED_CLAIM" not in r["evidence_class"] for r in observations))
    public_causal_text = " ".join(" ".join(r.values()) for r in public_obs + public_events).lower()
    check("151_no_project_level_causal_conclusion", not any(phrase in public_causal_text for phrase in ["caused", "because of", "led to", "resulted in", "drove", "boosted", "due to"]))

    # Provenance, raw files, extraction methods.
    check("152_every_quantitative_record_traces_to_source", all(r["source_id"] in srcmap and srcmap[r["source_id"]]["source_url"].startswith("http") for r in observations))
    check("153_every_pdf_observation_has_page", all(r["source_page"] for r in observations if "PDF" in srcmap[r["source_id"]]["source_type"]))
    check("154_source_publication_retrieval_present", all(srcmap[r["source_id"]]["published_at"] and srcmap[r["source_id"]]["retrieved_at"] for r in observations))
    check("155_expected_15_raw_pdfs", len(raw) == 15)
    check("156_raw_files_exist", all((ROOT / r["local_path"]).is_file() for r in raw))
    check("157_raw_hashes_validate", all(sha256(ROOT / r["local_path"]) == r["sha256"] for r in raw))
    check("158_raw_sizes_validate", all((ROOT / r["local_path"]).stat().st_size == int(r["file_size"]) for r in raw))
    check("159_raw_total_size_10855955", sum(int(r["file_size"]) for r in raw) == 10_855_955)
    check("160_no_duplicate_raw_hash", len({r["sha256"] for r in raw}) == len(raw))
    methods = Counter(r["extraction_method"] for r in extracts)
    check("161_ocr_count_zero", not any("OCR" in method.upper() for method in methods))
    check("162_chart_geometry_inference_zero", not any("GEOMETRY" in method.upper() for method in methods))
    check("163_all_extractions_verified", all(r["verification_status"] == "VERIFIED" for r in extracts))
    check("164_manual_extraction_count_93", len(extracts) == 93)
    check("165_reported_extractions_count_57", sum(r["field_name"] == "reported_value" for r in extracts) == 57)
    check("166_derived_input_extractions_count_36", sum(r["field_name"] in {"input_total_revenue", "input_share_percent"} for r in extracts) == 36)
    direct_extract_keys = {(r["entity_id"], r["fiscal_period_id"], r["metric_definition_id"], r["source_id"]) for r in extracts if r["field_name"] == "reported_value"}
    check("167_every_direct_observation_has_extraction", all((r["entity_id"], r["fiscal_period_id"], r["metric_definition_id"], r["source_id"]) in direct_extract_keys for r in direct_obs))
    used_extracts = {r["source_total_id"] for r in derivations} | {r["source_share_id"] for r in derivations} | {r["extraction_id"] for r in extracts if r["field_name"] == "reported_value"}
    check("168_no_unused_accidental_extraction", used_extracts == extract_ids)

    # Public/internal separation and counts.
    forbidden_columns = {"local_path", "sha256", "file_size", "extractor", "qa_note", "extraction_method", "verification_status"}
    check("169_public_observation_count_75", len(public_obs) == 75)
    check("170_public_event_count_26", len(public_events) == 26)
    check("171_public_observation_context_complete", all(r["series_id"] and r["entity"] and r["entity_type"] and r["publisher"] and r["quarter"] and r["publisher_defined_metric_label"] and r["metric_version"] and r["value"] and r["unit"] and r["evidence_class"] and r["canonical_source_url"] for r in public_obs))
    check("172_public_derived_uncertainty_present", all(r["lower_bound"] and r["upper_bound"] and r["derivation_marker"] == "YES" for r in public_obs if r["evidence_class"] == "DERIVED_FROM_OFFICIAL"))
    check("173_public_tables_no_internal_columns", forbidden_columns.isdisjoint(public_obs[0]) and forbidden_columns.isdisjoint(public_events[0]))
    public_text = " ".join(" ".join(r.values()) for r in public_obs + public_events)
    check("174_public_tables_no_local_paths", "E:\\" not in public_text and "research/raw" not in public_text)
    check("175_public_tables_no_raw_hashes", not any(len(token) == 64 and all(c in "0123456789abcdefABCDEF" for c in token) for token in public_text.replace(",", " ").split()))
    check("176_public_tables_no_copied_asset_reference", not any(ext in public_text.lower() for ext in [".png", ".jpg", ".jpeg", ".svg"]))
    check("177_public_events_are_short_structured_metadata", all(len(r["event_name"]) < 160 for r in public_events))

    # Phase D manifest integrity.
    check("178_manifest_corpus_size_recomputes", manifest_d["corpus_size"] == len(series))
    check("179_manifest_company_count_recomputes", len(manifest_d["unique_companies"]) == len({r["company_id"] for r in series}))
    check("180_manifest_direct_derived_counts_recompute", manifest_d["direct_series_count"] == len(direct_series) and manifest_d["derived_series_count"] == len(derived_series))
    check("181_manifest_observation_count_recomputes", manifest_d["observation_count"] == len(observations))
    check("182_manifest_event_claim_counts_recompute", manifest_d["event_count"] == len(events) and manifest_d["attributed_claim_count"] == len(claims))
    check("183_manifest_first_last_period_recompute", manifest_d["first_period"] == "2024Q3" and manifest_d["last_period"] == "2026Q2")
    check("184_manifest_raw_bytes_recompute", manifest_d["raw_storage_bytes"] == sum(int(r["file_size"]) for r in raw))
    check("185_manifest_public_bytes_recompute", manifest_d["public_dataset_bytes"] == (PD / "public_release_observations.csv").stat().st_size + (PD / "public_release_events.csv").stat().st_size)
    check("186_manifest_output_hashes_validate", all(sha256(PD / name) == expected for name, expected in manifest_d["output_hashes"].items()))
    check("187_manifest_build_hash_validates", manifest_d["input_hashes"]["build_corpus_py"] == sha256(BUILD_D))
    check("188_manifest_freeze_hash_validates", manifest_d["input_hashes"]["phase_c_method_freeze_manifest"] == sha256(PHASE_C / "method_freeze_manifest.json"))

    # Phase E reconciliation, corrections, sensitivity, and readiness.
    check("189_series_reconciliation_has_all_9", len(series_rec) == 9 and {r["series_id"] for r in series_rec} == set(smap))
    check("190_series_reconciliation_all_pass", all(r["validation_status"] == "PASS" for r in series_rec))
    check("191_series_reconciliation_counts_match", all(int(r["available_series_periods"]) == len(grid_by_series[r["series_id"]]) and int(r["observation_rows"]) == len(obs_by_series[r["series_id"]]) for r in series_rec))
    check("192_defect_log_no_unresolved_blocker", not any(r["severity"] == "BLOCKER" and r["resolved"] != "YES" for r in defects))
    check("193_defect_log_no_unresolved_error", not any(r["severity"] == "ERROR" and r["resolved"] != "YES" for r in defects))
    check("194_three_resolved_root_errors", sum(r["severity"] == "ERROR" and r["resolved"] == "YES" for r in defects) == 3)
    check("195_four_documented_warnings", sum(r["severity"] == "WARNING" for r in defects) == 4)
    check("196_corrections_have_before_after", all(r["before_value"] != r["after_value"] for r in corrections))
    check("197_corrections_source_backed", all(r["source_evidence"] for r in corrections))
    check("198_corrections_triggered_rebuild", all(r["rebuild_required"] == "YES" for r in corrections))
    check("199_corrections_all_validated", all(r["validation_status"] == "PASS" for r in corrections))
    check("200_correction_roots_match_resolved_errors", {r["root_defect_id"] for r in corrections} == {"TF-001", "TF-002", "CP-001"})
    check("201_sensitivity_has_18_rows", len(sensitivity) == 18)
    sensitivity_ok = True
    derived_by_series: dict[str, list[dict]] = defaultdict(list)
    for r in derived_obs:
        derived_by_series[entity_to_series[r["entity_id"]]].append(r)
    sens_map = {(r["series_id"], r["period"]): r for r in sensitivity}
    for sid, rows_ in derived_by_series.items():
        rows_.sort(key=lambda r: qkey(pmap[r["fiscal_period_id"]]["calendar_quarter_equivalent"]))
        for i, r in enumerate(rows_):
            quarter = pmap[r["fiscal_period_id"]]["calendar_quarter_equivalent"]
            out = sens_map[(sid, quarter)]
            if i == 0:
                sensitivity_ok &= out["sign_stable"] == "NOT_APPLICABLE"
            else:
                prev = rows_[i - 1]
                expected = [sign(d(r["value_krw_million"]) - d(prev["value_krw_million"])), sign(d(r["lower_bound_krw_million"]) - d(prev["upper_bound_krw_million"])), sign(d(r["upper_bound_krw_million"]) - d(prev["lower_bound_krw_million"]))]
                sensitivity_ok &= [out["point_change_sign"], out["lower_case_sign"], out["upper_case_sign"]] == expected and out["sign_stable"] == ("YES" if len(set(expected)) == 1 else "NO")
    check("202_derived_sensitivity_reproduces", sensitivity_ok)
    check("203_sensitive_change_count_reconciles", sum(r["sign_stable"] == "NO" for r in sensitivity) == manifest_e["derived_sign_sensitive_changes"])
    check("204_anomaly_rows_have_allowed_status", all(r["status"] in {"EXPECTED", "SOURCE_VERIFIED", "NEEDS_CORRECTION", "UNRESOLVED"} for r in anomalies))
    check("205_anomaly_rows_are_qa_only", all("winner" not in r["qa_note"].lower() and "loser" not in r["qa_note"].lower() for r in anomalies))
    check("206_findings_ready_has_75_validated_rows", len(findings) == 75 and all(r["quality_status"] == "VALIDATED" for r in findings))
    check("207_findings_ready_ids_match_canonical", {r["source_id"] for r in findings}.issubset(source_ids) and {(r["series_id"], r["period"], r["metric_version"]) for r in findings} == {(entity_to_series[o["entity_id"]], pmap[o["fiscal_period_id"]]["calendar_quarter_equivalent"], o["metric_version"]) for o in observations})
    check("208_findings_ready_has_eligibility_flags", all(r["qoq_eligible"] in {"YES", "NO"} and r["baseline_eligible"] == "YES" and r["drawdown_eligible"] == "YES" and r["volatility_eligible"] in {"YES", "NO"} for r in findings))
    check("209_qoq_flags_match_previous_links", all((r["qoq_eligible"] == "YES") == bool(changemap[next(o["observation_id"] for o in observations if entity_to_series[o["entity_id"]] == r["series_id"] and pmap[o["fiscal_period_id"]]["calendar_quarter_equivalent"] == r["period"] and o["metric_version"] == r["metric_version"])]["previous_observation_id"]) for r in findings))
    narrative_text = " ".join(" ".join(r.values()) for r in findings).lower()
    check("210_findings_ready_contains_no_narrative_findings", not any(term in narrative_text for term in ["winner", "loser", "commercial success", "caused by", "most successful", "best performing"]))
    check("211_readiness_manifest_series_count", manifest_e["validated_series_count"] == 9)
    check("212_readiness_manifest_observation_count", manifest_e["validated_observation_count"] == 75)
    check("213_readiness_manifest_stable_windows", manifest_e["stable_metric_windows"] == len(groups) == 12)
    check("214_readiness_manifest_version_break_count", manifest_e["version_break_count"] == 3)
    check("215_readiness_manifest_derived_count", manifest_e["derived_observation_count"] == 18)
    check("216_readiness_manifest_events_claims", manifest_e["events"] == 26 and manifest_e["claims"] == 3)
    check("217_readiness_manifest_zero_unresolved", manifest_e["unresolved_quality_issues"] == 0)
    check("218_eligible_for_phase_f_matches_gate", manifest_e["eligible_for_phase_f"] is True and summary_e["eligible_for_phase_f"] is True)
    check("219_findings_ready_hash_validates", manifest_e["findings_ready_sha256"] == sha256(DATA / "findings_ready_observations.csv"))
    check("220_readiness_input_hashes_validate", all(sha256(PD / name) == expected for name, expected in manifest_e["input_hashes"].items()))

    # Manual QA coverage.
    check("221_manual_qa_all_pass", all(r["result"] == "PASS" for r in manual_qa))
    obs_qa = Counter(r["series_id"] for r in manual_qa if r["check_type"] == "OBSERVATION_SOURCE_RECONCILIATION")
    drv_qa = Counter(r["series_id"] for r in manual_qa if r["check_type"] == "DERIVATION_RECONCILIATION")
    version_qa = {r["series_id"] for r in manual_qa if r["check_type"] == "METRIC_VERSION_OVERLAP_RECONCILIATION"}
    event_qa = {r["series_id"] for r in manual_qa if r["check_type"] == "EVENT_SOURCE_RECONCILIATION"}
    check("222_manual_qa_two_observations_per_series", all(obs_qa[sid] >= 2 for sid in smap))
    check("223_manual_qa_two_derivations_per_derived_series", all(drv_qa[sid] >= 2 for sid in {r["series_id"] for r in series if r["primary_evidence_class"] == "DERIVED_FROM_OFFICIAL"}))
    check("224_manual_qa_all_three_version_breaks", version_qa == {"series_lineage_m", "series_lineage_2m", "series_lineage_w"})
    event_series = {entity_to_series[r["entity_id"]] for r in events}
    check("225_manual_qa_one_event_per_covered_series", event_qa == event_series)
    check("226_manual_qa_count_34", len(manual_qa) == 34)

    # Deterministic Phase D and Phase E rebuilds, clean temporary root, and validator non-mutation.
    before_hashes = {name: sha256(PD / name) for name in CANONICAL_D}
    first = subprocess.run([sys.executable, str(BUILD_D)], cwd=ROOT, capture_output=True, text=True)
    first_hashes = {name: sha256(PD / name) for name in CANONICAL_D}
    second = subprocess.run([sys.executable, str(BUILD_D)], cwd=ROOT, capture_output=True, text=True)
    second_hashes = {name: sha256(PD / name) for name in CANONICAL_D}
    check("227_first_canonical_build_succeeds", first.returncode == 0, first.stderr.strip())
    check("228_second_canonical_build_succeeds", second.returncode == 0, second.stderr.strip())
    check("229_second_canonical_build_byte_identical", first_hashes == second_hashes)
    phase_e_files = [RESEARCH / name for name in REQUIRED_RESEARCH] + [DATA / name for name in REQUIRED_DATA]
    phase_e_before = {str(p): sha256(p) for p in phase_e_files}
    eb1 = subprocess.run([sys.executable, str(BUILD_E)], cwd=ROOT, capture_output=True, text=True)
    phase_e_first = {str(p): sha256(p) for p in phase_e_files}
    eb2 = subprocess.run([sys.executable, str(BUILD_E)], cwd=ROOT, capture_output=True, text=True)
    phase_e_second = {str(p): sha256(p) for p in phase_e_files}
    check("230_phase_e_first_build_succeeds", eb1.returncode == 0, eb1.stderr.strip())
    check("231_phase_e_second_build_succeeds", eb2.returncode == 0, eb2.stderr.strip())
    check("232_phase_e_outputs_byte_identical", phase_e_first == phase_e_second)
    check("233_phase_e_rebuild_matches_prevalidation", phase_e_before == phase_e_second)
    clean_ok = clean_match = False
    with tempfile.TemporaryDirectory(prefix="revenue-tides-phase-e-") as tmp:
        clean_root = Path(tmp) / "02-revenue-tides"
        shutil.copytree(ROOT / "data" / "phase-b", clean_root / "data" / "phase-b")
        (clean_root / "data" / "phase-d" / "input").mkdir(parents=True)
        shutil.copy2(PD / "input" / "expansion_extractions.csv", clean_root / "data" / "phase-d" / "input" / "expansion_extractions.csv")
        (clean_root / "scripts" / "phase_d").mkdir(parents=True)
        shutil.copy2(BUILD_D, clean_root / "scripts" / "phase_d" / "build_corpus.py")
        (clean_root / "research" / "phase-c").mkdir(parents=True)
        shutil.copy2(PHASE_C / "method_freeze_manifest.json", clean_root / "research" / "phase-c" / "method_freeze_manifest.json")
        clean_run = subprocess.run([sys.executable, str(clean_root / "scripts" / "phase_d" / "build_corpus.py")], cwd=clean_root, capture_output=True, text=True)
        clean_ok = clean_run.returncode == 0
        if clean_ok:
            clean_match = all(sha256(clean_root / "data" / "phase-d" / name) == sha256(PD / name) for name in CANONICAL_D)
    check("234_temporary_clean_build_succeeds", clean_ok)
    check("235_temporary_clean_build_matches_canonical", clean_match)
    after_hashes = {name: sha256(PD / name) for name in CANONICAL_D}
    check("236_validator_does_not_mutate_canonical_bytes", before_hashes == after_hashes)
    check("237_rebuild_requires_no_network", "requests" not in BUILD_D.read_text(encoding="utf-8") and "urllib" not in BUILD_D.read_text(encoding="utf-8"))
    check("238_rebuild_requires_no_private_credentials", not any(term in BUILD_D.read_text(encoding="utf-8").lower() for term in ["api_key", "password", "token="]))
    check("239_rebuild_has_no_sensor_tower_dependency", "sensor tower" not in BUILD_D.read_text(encoding="utf-8").lower())
    check("240_rebuild_has_no_appmagic_dependency", "appmagic" not in BUILD_D.read_text(encoding="utf-8").lower())

    passed = sum(ok for _, ok, _ in results)
    total = len(results)
    for name, ok, detail in results:
        suffix = f" — {detail}" if detail and not ok else ""
        print(f"{'PASS' if ok else 'FAIL'}: {name}{suffix}")
    print(f"\nAutomated Tests: {passed}/{total} {'PASS' if passed == total else 'FAIL'}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
