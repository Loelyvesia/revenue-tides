#!/usr/bin/env python3
"""Validate the frozen-method Phase D curated corpus."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR
from pathlib import Path
from statistics import median


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "phase-d"
INPUT = DATA / "input"
RESEARCH = ROOT / "research" / "phase-d"
PHASE_C = ROOT / "research" / "phase-c"
BUILD = ROOT / "scripts" / "phase_d" / "build_corpus.py"
METHOD = "revenue-tides-method-freeze-1.0.0"

REQUIRED_DATA = [
    "series.csv", "entities.csv", "companies.csv", "fiscal_periods.csv",
    "metric_definitions.csv", "sources.csv", "observations.csv",
    "derivations.csv", "events.csv", "attributed_claims.csv",
    "expected_period_grid.csv", "change_features.csv",
    "comparability_matrix.csv", "raw_manifest.csv",
    "public_release_observations.csv", "public_release_events.csv",
    "corpus_manifest.json",
]
REQUIRED_RESEARCH = [
    "PHASE_D_CURATED_CORPUS.md", "candidate_registry.csv",
    "candidate_selection_audit.md", "rejected_candidates.csv",
    "corpus_composition.md", "continuity_audit.md",
    "direct_derived_ratio_audit.md", "entity_scope_audit.md",
    "metric_version_audit.csv", "fiscal_period_audit.md",
    "derivation_audit.md", "event_curation_audit.md",
    "missingness_audit.md", "provenance_audit.md",
    "public_release_audit.md", "storage_audit.md",
    "deterministic_rebuild_audit.md", "phase_d_summary.json", "manual_qa.csv",
]
CANONICAL = [name for name in REQUIRED_DATA if name.endswith(".csv")]


def rows(name: str, base: Path = DATA) -> list[dict[str, str]]:
    with (base / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def d(value: str) -> Decimal:
    return Decimal(value)


def same_decimal(actual: str, expected: Decimal) -> bool:
    return actual != "" and d(actual) == expected


def quarter_key(label: str) -> tuple[int, int]:
    return int(label[:4]), int(label[-1])


def main() -> int:
    results: list[tuple[str, bool, str]] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        results.append((name, bool(condition), detail))

    # Required files and parseability are checked before the rebuild.
    check("required_data_outputs_exist", all((DATA / p).is_file() for p in REQUIRED_DATA))
    check("required_research_outputs_exist", all((RESEARCH / p).is_file() for p in REQUIRED_RESEARCH))
    check("build_script_exists", BUILD.is_file())
    check("controlled_input_exists", (INPUT / "manual_extractions.csv").is_file())
    check("expansion_input_exists", (INPUT / "expansion_extractions.csv").is_file())

    csv_parse_ok = True
    for path in list(DATA.glob("*.csv")) + list(RESEARCH.glob("*.csv")) + list(INPUT.glob("*.csv")):
        try:
            with path.open(encoding="utf-8", newline="") as handle:
                list(csv.DictReader(handle))
        except Exception:
            csv_parse_ok = False
    check("all_phase_d_csv_files_parse", csv_parse_ok)
    json_parse_ok = True
    for path in list(DATA.glob("*.json")) + list(RESEARCH.glob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            json_parse_ok = False
    check("all_phase_d_json_files_parse", json_parse_ok)

    first = subprocess.run([sys.executable, str(BUILD)], cwd=ROOT, capture_output=True, text=True)
    check("first_build_completes", first.returncode == 0, first.stderr.strip())
    first_hashes = {name: sha256(DATA / name) for name in CANONICAL}
    second = subprocess.run([sys.executable, str(BUILD)], cwd=ROOT, capture_output=True, text=True)
    check("second_build_completes", second.returncode == 0, second.stderr.strip())
    second_hashes = {name: sha256(DATA / name) for name in CANONICAL}
    check("canonical_outputs_byte_identical", first_hashes == second_hashes)

    manifest = json.loads((DATA / "corpus_manifest.json").read_text(encoding="utf-8"))
    summary = json.loads((RESEARCH / "phase_d_summary.json").read_text(encoding="utf-8"))
    freeze = json.loads((PHASE_C / "method_freeze_manifest.json").read_text(encoding="utf-8"))
    series = rows("series.csv")
    entities = rows("entities.csv")
    companies = rows("companies.csv")
    periods = rows("fiscal_periods.csv")
    metrics = rows("metric_definitions.csv")
    sources = rows("sources.csv")
    observations = rows("observations.csv")
    derivations = rows("derivations.csv")
    events = rows("events.csv")
    claims = rows("attributed_claims.csv")
    grid = rows("expected_period_grid.csv")
    changes = rows("change_features.csv")
    comparisons = rows("comparability_matrix.csv")
    raw = rows("raw_manifest.csv")
    public_obs = rows("public_release_observations.csv")
    public_events = rows("public_release_events.csv")
    candidates = rows("candidate_registry.csv", RESEARCH)
    rejected = rows("rejected_candidates.csv", RESEARCH)
    versions = rows("metric_version_audit.csv", RESEARCH)
    qa = rows("manual_qa.csv", RESEARCH)
    extracts = rows("manual_extractions.csv", INPUT)

    # Frozen method integrity.
    freeze_hashes_ok = all(sha256(PHASE_C / name) == expected for name, expected in freeze["method_hashes"].items())
    check("phase_c_all_18_freeze_hashes_validate", freeze_hashes_ok and len(freeze["method_hashes"]) == 18)
    check("method_version_unchanged", manifest["method_version"] == summary["method_version"] == freeze["method_version"] == METHOD)
    check("primary_temporal_unit_remains_fiscal_quarter", freeze["primary_temporal_unit"] == "FISCAL_QUARTER")
    check("data_cutoff_is_current_phase_d_cutoff", manifest["data_cutoff"] == "2026-09-22")
    check("target_size_report_is_explicit", summary["target_size"] == freeze["target_corpus_size"] == 10)

    # Corpus gates and identity.
    direct = [r for r in series if r["primary_evidence_class"] == "OFFICIAL_REPORTED"]
    derived = [r for r in series if r["primary_evidence_class"] == "DERIVED_FROM_OFFICIAL"]
    launch = [r for r in series if r["cohort_type"] == "LAUNCH_COHORT"]
    check("corpus_size_at_least_8", len(series) >= 8)
    check("corpus_size_at_most_12", len(series) <= 12)
    check("corpus_size_manifest_matches", manifest["corpus_size"] == len(series))
    check("derived_ratio_at_most_one_third", len(derived) * 3 <= len(series))
    check("direct_ratio_at_least_two_thirds", len(direct) * 3 >= len(series) * 2)
    check("launch_cohort_count_at_most_2", len(launch) <= 2)
    check("manifest_ratio_counts_match", manifest["direct_series_count"] == len(direct) and manifest["derived_series_count"] == len(derived))
    check("all_series_ids_unique", len({r["series_id"] for r in series}) == len(series))
    check("all_selected_entity_ids_unique", len({r["entity_id"] for r in series}) == len(series))
    check("all_entity_types_allowed", all(r["entity_type"] in freeze["allowed_entity_types"] for r in series))
    check("all_series_have_explicit_platform_scope", all(r["platform_scope"].strip() for r in series))
    check("all_series_have_selection_rationale", all(r["selection_rationale"].strip() for r in series))
    check("manifest_series_ids_match", manifest["series_ids"] == [r["series_id"] for r in series])
    check("manifest_company_list_matches", manifest["unique_companies"] == sorted({r["company_id"] for r in series}))
    check("no_forced_tenth_series", len(series) == 9 and summary["target_size"] == 10)

    entity_ids = {r["entity_id"] for r in entities}
    company_ids = {r["company_id"] for r in companies}
    period_ids = {r["fiscal_period_id"] for r in periods}
    metric_ids = {r["metric_definition_id"] for r in metrics}
    source_ids = {r["source_id"] for r in sources}
    observation_ids = {r["observation_id"] for r in observations}
    derivation_ids = {r["derivation_id"] for r in derivations}
    series_ids = {r["series_id"] for r in series}
    check("all_series_entity_foreign_keys_resolve", all(r["entity_id"] in entity_ids for r in series))
    check("all_series_company_foreign_keys_resolve", all(r["company_id"] in company_ids for r in series))
    check("all_observation_entity_foreign_keys_resolve", all(r["entity_id"] in entity_ids for r in observations))
    check("all_observation_company_foreign_keys_resolve", all(r["company_id"] in company_ids for r in observations))
    check("all_observation_period_foreign_keys_resolve", all(r["fiscal_period_id"] in period_ids for r in observations))
    check("all_observation_metric_foreign_keys_resolve", all(r["metric_definition_id"] in metric_ids for r in observations))
    check("all_observation_source_foreign_keys_resolve", all(r["source_id"] in source_ids for r in observations))
    check("all_event_foreign_keys_resolve", all(r["entity_id"] in entity_ids and r["fiscal_period_id"] in period_ids and r["source_id"] in source_ids for r in events))
    check("all_claim_foreign_keys_resolve", all(r["entity_id"] in entity_ids and r["fiscal_period_id"] in period_ids and r["source_id"] in source_ids for r in claims))
    check("all_grid_foreign_keys_resolve", all(r["series_id"] in series_ids and r["fiscal_period_id"] in period_ids for r in grid))

    # Continuity and expected-period construction.
    grid_by_series: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in grid:
        grid_by_series[row["series_id"]].append(row)
    check("all_core_series_have_at_least_6_quarters", all(len(grid_by_series[r["series_id"]]) >= 6 for r in series if r["cohort_type"] == "CORE"))
    check("all_launch_series_have_at_least_4_quarters", all(len(grid_by_series[r["series_id"]]) >= 4 for r in launch))
    check("all_launch_series_have_launch_event", all(any(e["entity_id"] == r["entity_id"] and "LAUNCH" in e["event_type"] for e in events) for r in launch))
    check("expected_grid_row_count_matches_windows", len(grid) == sum(int(r["expected_quarters"]) for r in series))
    check("expected_grid_has_unique_series_period_pairs", len({(r["series_id"], r["fiscal_period_id"]) for r in grid}) == len(grid))
    check("every_expected_period_is_accounted_for", all(r["observation_id"] or r["missingness_state"] in freeze["missingness_states"] for r in grid))
    check("present_grid_observations_resolve", all(all(oid in observation_ids for oid in r["observation_id"].split("|") if oid) for r in grid))
    check("no_missing_value_encoded_as_zero", all(not (r["missingness_state"] != "AVAILABLE" and r["value_krw_million"] in {"0", "0.0", "0.00"}) for r in observations))
    check("no_interpolation", all("interpol" not in (r["notes"] + r["reporting_scope"]).lower() for r in observations))
    check("no_forward_fill", all("forward fill" not in (r["notes"] + r["reporting_scope"]).lower() and "forward-fill" not in (r["notes"] + r["reporting_scope"]).lower() for r in observations))
    check("all_periods_have_exact_bounds", all(r["period_start"] and r["period_end"] for r in periods))
    check("publication_date_separate_from_observation_period", all(r["published_at"] and r["fiscal_period_id"] for r in observations))

    # Evidence and provenance.
    src_map = {r["source_id"]: r for r in sources}
    check("all_observations_have_allowed_evidence_class", all(r["evidence_class"] in freeze["allowed_quantitative_evidence_classes"] for r in observations))
    check("all_direct_observations_use_official_sources", all(src_map[r["source_id"]]["officiality"] == "OFFICIAL" for r in observations if r["evidence_class"] == "OFFICIAL_REPORTED"))
    check("all_derived_observations_have_derivations", all(r["derivation_id"] in derivation_ids for r in observations if r["evidence_class"] == "DERIVED_FROM_OFFICIAL"))
    check("no_derived_record_labeled_direct", all(not r["derivation_id"] for r in observations if r["evidence_class"] == "OFFICIAL_REPORTED"))
    check("no_industry_estimate_in_primary_observations", all(r["evidence_class"] != "INDUSTRY_ESTIMATE" for r in observations))
    joined_numeric = " ".join(" ".join(r.values()) for r in observations).lower()
    check("no_sensor_tower_numeric_record", "sensor tower" not in joined_numeric and "sensortower" not in joined_numeric)
    check("no_appmagic_numeric_record", "appmagic" not in joined_numeric)
    check("no_chart_geometry_inference", all("geometry" not in r["notes"].lower() and "chart height" not in r["notes"].lower() for r in observations))
    check("no_unofficial_leak", all("leak" not in src_map[r["source_id"]]["source_type"].lower() for r in observations))
    check("all_quantitative_sources_have_urls", all(src_map[r["source_id"]]["source_url"].startswith("http") for r in observations))
    check("all_official_pdf_observations_have_pages", all(r["source_page"].strip() for r in observations if "PDF" in src_map[r["source_id"]]["source_type"]))
    check("all_retained_pdfs_have_sha256", all(len(r["sha256"]) == 64 for r in raw))
    check("retained_pdf_files_exist", all((ROOT / r["local_path"]).is_file() for r in raw))
    check("retained_pdf_hashes_validate", all(sha256(ROOT / r["local_path"]) == r["sha256"] for r in raw))
    raw_hash_counts = Counter(r["sha256"] for r in raw)
    check("no_duplicate_retained_pdf_hash", all(n == 1 for n in raw_hash_counts.values()))
    check("raw_storage_below_soft_limit", manifest["raw_storage_bytes"] < freeze["raw_storage_soft_limit_mb"] * 1024 * 1024)
    check("raw_storage_below_review_limit", manifest["raw_storage_bytes"] < freeze["raw_storage_hard_review_mb"] * 1024 * 1024)
    check("raw_storage_manifest_reproduces", manifest["raw_storage_bytes"] == sum(int(r["file_size"]) for r in raw))

    # Derivations and uncertainty intervals.
    extract_ids = {r["extraction_id"] for r in extracts}
    derivation_ok = True
    interval_ok = True
    ordering_ok = True
    for row in derivations:
        total, share = d(row["input_total_value"]), d(row["input_share_percent"])
        point = total * share / Decimal(100)
        low = (total * (share - Decimal("0.5")) / 100).quantize(Decimal("0.01"), rounding=ROUND_FLOOR)
        high = (total * (share + Decimal("0.5")) / 100).quantize(Decimal("0.01"), rounding=ROUND_CEILING)
        derivation_ok &= d(row["point_estimate"]) == point
        interval_ok &= d(row["lower_bound"]) == low and d(row["upper_bound"]) == high
        ordering_ok &= low <= point <= high
    check("all_derivation_formulas_reproduce", derivation_ok)
    check("all_uncertainty_intervals_reproduce", interval_ok)
    check("all_derived_bounds_are_ordered", ordering_ok)
    check("all_derivation_source_inputs_resolve", all(r["source_total_id"] in extract_ids and r["source_share_id"] in extract_ids for r in derivations))
    check("all_derivations_verified", all(r["verification_status"] == "VERIFIED_REPRODUCIBLE" for r in derivations))
    derived_obs_map = {r["derivation_id"]: r for r in observations if r["derivation_id"]}
    check("derived_observation_values_match_derivations", all(d(derived_obs_map[r["derivation_id"]]["value_krw_million"]) == d(r["point_estimate"]) * 1000 for r in derivations))
    check("derived_observation_bounds_match_derivations", all(d(derived_obs_map[r["derivation_id"]]["lower_bound_krw_million"]) == d(r["lower_bound"]) * 1000 and d(derived_obs_map[r["derivation_id"]]["upper_bound_krw_million"]) == d(r["upper_bound"]) * 1000 for r in derivations))
    check("mcoc_retains_derived_uncertainty", all(r["lower_bound_krw_million"] and r["upper_bound_krw_million"] for r in observations if r["entity_id"] == "marvel_contest_of_champions_title"))

    # Metric versions and transformation reproduction.
    period_map = {r["fiscal_period_id"]: r for r in periods}
    obs_map = {r["observation_id"]: r for r in observations}
    change_map = {r["observation_id"]: r for r in changes}
    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in observations:
        row_series = next(s["series_id"] for s in series if s["entity_id"] == row["entity_id"])
        groups[(row_series, row["comparable_group_id"])].append(row)
    feature_ok = True
    drawdown_ok = True
    recovery_ok = True
    volatility_ok = True
    no_cross_break = True
    baseline_restart = True
    for (series_id, group_id), group in groups.items():
        group.sort(key=lambda r: quarter_key(period_map[r["fiscal_period_id"]]["calendar_quarter_equivalent"]))
        vals = [d(r["value_krw_million"]) for r in group]
        mean = sum(vals) / len(vals)
        variance = sum((v - mean) ** 2 for v in vals) / len(vals)
        cv = variance.sqrt() / mean * 100 if mean else None
        qoqs = [(vals[i] - vals[i - 1]) / vals[i - 1] * 100 for i in range(1, len(vals)) if vals[i - 1] != 0]
        qmean = sum(qoqs) / len(qoqs) if qoqs else None
        qstd = (sum((q - qmean) ** 2 for q in qoqs) / len(qoqs)).sqrt() if qoqs else None
        med_abs = Decimal(str(median([float(abs(q)) for q in qoqs]))) if qoqs else None
        rolling_peak = vals[0]
        peak_index = 0
        active_drawdown = False
        for i, obs in enumerate(group):
            out = change_map[obs["observation_id"]]
            previous = vals[i - 1] if i else None
            prior_peak = rolling_peak
            recovered = active_drawdown and vals[i] >= prior_peak
            if vals[i] < prior_peak:
                active_drawdown = True
                expected_drawdown = (vals[i] - prior_peak) / prior_peak * 100 if prior_peak else Decimal(0)
                expected_trough = min(vals[peak_index:i + 1])
                expected_recovery = "NOT_RECOVERED_WITHIN_OBSERVED_WINDOW" if i == len(group) - 1 else "DRAWDOWN_ACTIVE"
                expected_recovery_quarters = ""
            else:
                expected_drawdown = Decimal(0)
                expected_trough = min(vals[peak_index:i + 1]) if recovered else vals[i]
                expected_recovery = "AT_OR_ABOVE_ROLLING_PEAK"
                expected_recovery_quarters = str(i - peak_index) if recovered else ""
                rolling_peak = vals[i]
                peak_index = i
                active_drawdown = False
            feature_ok &= same_decimal(out["baseline_index"], vals[i] / vals[0] * 100)
            feature_ok &= (out["qoq_absolute_change_krw_million"] == "" if previous is None else same_decimal(out["qoq_absolute_change_krw_million"], vals[i] - previous))
            feature_ok &= (out["qoq_percent_change"] == "" if previous is None else same_decimal(out["qoq_percent_change"], (vals[i] - previous) / previous * 100))
            drawdown_ok &= same_decimal(out["rolling_peak_krw_million"], rolling_peak) and same_decimal(out["prior_peak_value_krw_million"], prior_peak) and same_decimal(out["drawdown_pct"], expected_drawdown)
            drawdown_ok &= same_decimal(out["trough_since_peak_krw_million"], expected_trough)
            recovery_ok &= out["recovery_status"] == expected_recovery and out["recovery_quarters"] == expected_recovery_quarters
            volatility_ok &= same_decimal(out["coefficient_of_variation_pct"], cv) and same_decimal(out["within_series_range_krw_million"], max(vals) - min(vals))
            volatility_ok &= (qstd is None and out["stddev_qoq_percent_change"] == "" or qstd is not None and same_decimal(out["stddev_qoq_percent_change"], qstd))
            volatility_ok &= (med_abs is None and out["median_absolute_qoq_change"] == "" or med_abs is not None and same_decimal(out["median_absolute_qoq_change"], med_abs))
            baseline_restart &= out["baseline_origin_observation_id"] == group[0]["observation_id"]
            if out["previous_observation_id"]:
                previous_obs = obs_map[out["previous_observation_id"]]
                no_cross_break &= previous_obs["metric_version"] == obs["metric_version"] and previous_obs["entity_id"] == obs["entity_id"] and out["series_id"] == series_id
    check("change_features_reproduce", feature_ok)
    check("drawdown_features_reproduce", drawdown_ok)
    check("recovery_features_reproduce", recovery_ok)
    check("volatility_features_reproduce_within_groups", volatility_ok)
    check("no_qoq_crosses_metric_versions", no_cross_break)
    check("baseline_restarts_after_metric_break", baseline_restart)
    check("change_feature_count_matches_observations", len(changes) == len(observations))
    check("all_change_rows_resolve_to_observations", set(change_map) == observation_ids)
    check("metric_version_audit_covers_every_series_version", {(r["series_id"], r["version"]) for r in versions} == {(next(s["series_id"] for s in series if s["entity_id"] == o["entity_id"]), o["metric_version"]) for o in observations})
    lineage_versions = {r["metric_version"] for r in observations if r["entity_id"] == "lineage_m_title"}
    check("lineage_m_versions_remain_separate", lineage_versions == {"legacy_v1", "royalty_integrated_v2"} and len({r["comparable_group_id"] for r in observations if r["entity_id"] == "lineage_m_title"}) == 2)
    check("all_version_breaks_forbid_cross_version_change", all(r["cross_version_change_allowed"] == "NO" for r in versions if r["break_type"] != "NONE"))

    # Required named special cases and eligibility audit.
    black = next(r for r in series if r["series_id"] == "series_black_desert")
    stellar_events = [r for r in events if r["entity_id"] == "stellar_blade_ip"]
    check("black_desert_remains_ip_scope", black["entity_type"] == "IP" and "PC; console; mobile" in black["platform_scope"])
    check("stellar_blade_platform_launch_is_context", any(r["event_type"] == "PLATFORM_LAUNCH" and "context only" in r["notes"].lower() for r in stellar_events))
    selected_names = {r["canonical_name"] for r in series}
    selected_candidate_rows = [r for r in candidates if r["canonical_name"] in selected_names]
    check("all_selected_series_pass_frozen_eligibility", len(selected_candidate_rows) == len(series) and all(r["eligibility_status"] in {"ELIGIBLE_CORE", "ELIGIBLE_LAUNCH_COHORT"} for r in selected_candidate_rows))
    check("candidate_pool_at_most_20", len(candidates) <= 20)
    check("all_rejected_candidates_have_reasons", all(r["eligibility_status"].startswith("REJECTED_") and r["rejection_reason"].strip() for r in rejected))
    check("rejected_registry_and_audit_match", {r["candidate_id"] for r in rejected} == {r["candidate_id"] for r in candidates if r["eligibility_status"].startswith("REJECTED_")})

    # Events, claims, comparability, public release, QA.
    check("event_count_within_curated_target", 20 <= len(events) <= 40)
    check("all_event_sources_are_official", all(src_map[r["source_id"]]["officiality"] == "OFFICIAL" for r in events))
    check("events_do_not_contain_causal_conclusions", all("caused" not in (r["event_name"] + r["notes"]).lower() and "causal conclusion" in r["notes"].lower() for r in events))
    check("event_dates_have_declared_precision", all(r["date_precision"] in {"DAY", "MONTH", "QUARTER"} for r in events))
    check("attributed_claim_count_at_most_20", len(claims) <= 20)
    check("attributed_claims_stored_separately", not any("ATTRIBUTED_CLAIM" in r["evidence_class"] for r in observations) and all(r["claim_type"] for r in claims))
    check("comparability_defaults_are_conservative", all(r["comparability_status"] in {"WITHIN_SERIES_ONLY", "VERSION_BREAK", "NOT_COMPARABLE"} for r in comparisons) and all(r["comparability_status"] == "NOT_COMPARABLE" for r in comparisons if r["left_entity_id"] != r["right_entity_id"]) and all(r["comparability_status"] == "WITHIN_SERIES_ONLY" for r in comparisons if r["left_series_id"] == r["right_series_id"]))
    check("no_cross_company_revenue_leaderboard", not any("leaderboard" in p.name.lower() for p in list(DATA.iterdir()) + list(RESEARCH.iterdir())))
    forbidden_public = {"local_path", "sha256", "file_size", "qa_note", "extraction_method", "verification_status"}
    check("public_observations_contain_no_internal_columns", forbidden_public.isdisjoint(public_obs[0].keys()))
    check("public_events_contain_no_internal_columns", forbidden_public.isdisjoint(public_events[0].keys()))
    public_text = " ".join(" ".join(r.values()) for r in public_obs + public_events).lower()
    check("public_tables_contain_no_local_paths", "research/raw" not in public_text and ":\\" not in public_text)
    check("public_tables_contain_no_raw_hashes", not any(len(token) == 64 and all(c in "0123456789abcdef" for c in token) for token in public_text.split()))
    check("public_observation_count_matches_internal", len(public_obs) == len(observations))
    check("public_event_count_matches_internal", len(public_events) == len(events))
    check("manual_qa_all_pass", all(r["result"] == "PASS" for r in qa))
    source_qa = Counter(r["series_id"] for r in qa if r["check_type"] == "MANUAL_SOURCE_RECONCILIATION")
    derivation_qa = Counter(r["series_id"] for r in qa if r["check_type"] == "MANUAL_DERIVATION_RECONCILIATION")
    check("manual_qa_has_two_observations_per_series", all(source_qa[r["series_id"]] >= 2 for r in series))
    check("manual_qa_has_two_derivations_per_derived_series", all(derivation_qa[r["series_id"]] >= 2 for r in derived))
    qa_obs = {r["observation_id"] for r in qa if r["check_type"] == "MANUAL_SOURCE_RECONCILIATION"}
    check("manual_qa_covers_each_metric_version", all(any(o["observation_id"] in qa_obs for o in observations if o["entity_id"] == s["entity_id"] and o["metric_version"] == v) for s in series for v in {o["metric_version"] for o in observations if o["entity_id"] == s["entity_id"]}))

    # Manifest, counts, and hashes.
    check("manifest_observation_count_matches", manifest["observation_count"] == len(observations))
    check("manifest_event_count_matches", manifest["event_count"] == len(events))
    check("manifest_claim_count_matches", manifest["attributed_claim_count"] == len(claims))
    check("manifest_first_last_period_match", manifest["first_period"] == "2024Q3" and manifest["last_period"] == "2026Q2")
    check("manifest_output_hashes_validate", all((DATA / name).is_file() and sha256(DATA / name) == expected for name, expected in manifest["output_hashes"].items()))
    check("manifest_input_hashes_validate", manifest["input_hashes"]["phase_c_method_freeze_manifest"] == sha256(PHASE_C / "method_freeze_manifest.json") and manifest["input_hashes"]["phase_d_expansion_extractions"] == sha256(INPUT / "expansion_extractions.csv") and manifest["input_hashes"]["build_corpus_py"] == sha256(BUILD))
    check("summary_counts_match_manifest", summary["corpus_size"] == manifest["corpus_size"] and summary["observation_count"] == manifest["observation_count"] and summary["event_count"] == manifest["event_count"])
    check("stop_boundary_is_phase_e", summary["stop_boundary"] == "STOPPED BEFORE PHASE E")

    passed = sum(ok for _, ok, _ in results)
    total = len(results)
    for name, ok, detail in results:
        suffix = f" — {detail}" if detail and not ok else ""
        print(f"{'PASS' if ok else 'FAIL'}: {name}{suffix}")
    print(f"\nAutomated Tests: {passed}/{total} {'PASS' if passed == total else 'FAIL'}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
