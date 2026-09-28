#!/usr/bin/env python3
"""Validate the Revenue Tides method/scope freeze and Phase B compatibility."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PHASE_C = ROOT / "research" / "phase-c"
PHASE_B_DATA = ROOT / "data" / "phase-b"
MANIFEST_PATH = PHASE_C / "method_freeze_manifest.json"
SUMMARY_PATH = PHASE_C / "phase_c_summary.json"
RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(condition), detail))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv(name: str) -> list[dict]:
    with (PHASE_B_DATA / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    manifest_parse_ok = summary_parse_ok = True
    try:
        manifest = load_json(MANIFEST_PATH)
    except Exception as exc:
        manifest, manifest_parse_ok = {}, False
        manifest_error = str(exc)
    else:
        manifest_error = ""
    try:
        summary = load_json(SUMMARY_PATH)
    except Exception as exc:
        summary, summary_parse_ok = {}, False
        summary_error = str(exc)
    else:
        summary_error = ""

    docs = {path.name: path.read_text(encoding="utf-8") for path in PHASE_C.glob("*.md")}
    all_text = "\n".join(docs.values())
    all_lower = all_text.lower()

    observations = load_csv("observations.csv")
    entities = load_csv("entities.csv")
    periods = load_csv("fiscal_periods.csv")
    metrics = load_csv("metric_definitions.csv")
    derivations = load_csv("derivations.csv")
    events = load_csv("events.csv")
    claims = load_csv("attributed_claims.csv")
    changes = load_csv("change_features.csv")
    public = load_csv("public_release_observations.csv")
    raw_manifest = load_csv("raw_manifest.csv")

    allowed_entities = {"GAME_TITLE", "GAME_EDITION", "IP", "FRANCHISE"}
    allowed_quant = {"OFFICIAL_REPORTED", "DERIVED_FROM_OFFICIAL"}
    missing_states = {"AVAILABLE", "NOT_REPORTED", "NOT_APPLICABLE", "METRIC_VERSION_BREAK", "DERIVATION_UNAVAILABLE", "SOURCE_UNAVAILABLE", "UNRESOLVED", "OUTSIDE_SERIES_WINDOW"}
    comparability = {"DIRECTLY_COMPARABLE", "WITHIN_SERIES_ONLY", "VERSION_BREAK", "CONTEXT_ONLY", "NOT_COMPARABLE"}

    check("01_method_version_exists", manifest.get("method_version") == "revenue-tides-method-freeze-1.0.0")
    titles = manifest.get("project_title", {})
    check("02_project_title_frozen", titles.get("zh") == "付费潮汐——游戏商业生命线" and titles.get("en") == "Revenue Tides — The Commercial Life of Games")
    check("03_temporal_unit_fiscal_quarter", manifest.get("primary_temporal_unit") == "FISCAL_QUARTER")
    check("04_corpus_target_10", manifest.get("target_corpus_size") == 10)
    check("05_corpus_minimum_8", manifest.get("minimum_corpus_size") == 8)
    check("06_corpus_maximum_12", manifest.get("maximum_corpus_size") == 12)
    check("07_contract_never_exceeds_maximum", manifest.get("target_corpus_size", 99) <= manifest.get("maximum_corpus_size", 0) and "hard maximum 12" in all_lower)
    check("08_core_minimum_6", manifest.get("core_min_quarters") == 6)
    check("09_core_preferred_8", manifest.get("core_preferred_quarters") == 8 and "8 are preferred" in all_text)
    check("10_launch_cohort_minimum_4", manifest.get("launch_cohort_min_quarters") == 4)
    check("11_launch_cohort_maximum_2", manifest.get("max_launch_cohort_series") == 2)
    check("12_allowed_entity_types_explicit", set(manifest.get("allowed_entity_types", [])) == allowed_entities)
    check("13_segment_not_primary", "SEGMENT" not in manifest.get("allowed_entity_types", []) and "SEGMENT" in manifest.get("context_entity_types", []))
    check("14_official_reported_allowed", "OFFICIAL_REPORTED" in manifest.get("allowed_quantitative_evidence_classes", []))
    check("15_derived_from_official_allowed", "DERIVED_FROM_OFFICIAL" in manifest.get("allowed_quantitative_evidence_classes", []))
    check("16_industry_estimate_not_primary", manifest.get("industry_estimate_primary_allowed") is False and "industry estimates are outside the primary quantitative corpus" in all_lower)
    check("17_derived_fraction_defined", 0 < manifest.get("derived_series_max_fraction", 0) <= 1 / 3)
    check("18_two_thirds_direct_policy", manifest.get("direct_series_min_fraction", 0) >= 2 / 3 and "at least two-thirds" in all_lower)
    check("19_fiscal_bounds_required", manifest.get("fiscal_period_bounds_required") is True and "exact period start and end" in all_lower)
    check("20_publication_date_separate", manifest.get("publication_date_separate_from_observation_period") is True and "publication date separately" in all_lower)
    check("21_raw_value_preservation", manifest.get("raw_value_and_unit_preservation_required") is True and "reported_value_raw" in all_text and "reported_unit_raw" in all_text)
    check("22_cross_company_absolute_forbidden", manifest.get("cross_company_absolute_comparison_allowed") is False and "cross-company absolute revenue levels" in all_lower)
    check("23_normalized_trajectory_allowed", manifest.get("normalized_within_series_trajectory_allowed") is True and "unitless trajectory" in all_lower)
    check("24_version_break_blocks_qoq", "cross_version_qoq" in manifest.get("prohibited_transformations", []) and "must not calculate qoq change" in all_lower)
    check("25_interpolation_forbidden", manifest.get("interpolation_allowed") is False and "interpolation" in manifest.get("prohibited_transformations", []))
    check("26_forward_fill_forbidden", manifest.get("forward_fill_allowed") is False and "forward_fill" in manifest.get("prohibited_transformations", []))
    check("27_missing_not_zero", "no missingness state may become numeric zero" in all_lower and "missingness_policy.md" in docs)
    check("28_event_correlation_not_causation", manifest.get("causal_claims_allowed") is False and "not causality" in all_lower)
    check("29_attributed_claims_separate", "attributed_claim" in all_lower and "issuer explanations remain" in all_lower)
    check("30_source_url_mandatory", manifest.get("provenance_source_url_required") is True and "canonical source url" in all_lower)
    check("31_pdf_page_mandatory", manifest.get("pdf_page_required_when_applicable") is True and "exact pdf page" in all_lower)
    check("32_public_internal_separation", manifest.get("public_internal_separation_required") is True and "two layers" in all_lower)
    check("33_storage_limits_frozen", manifest.get("raw_storage_soft_limit_mb") == 150 and manifest.get("raw_storage_hard_review_mb") == 250)
    check("34_no_sensor_tower_appmagic_backbone", "sensor tower or appmagic numerical reconstruction" in all_lower and "not permitted in the primary quantitative corpus" in all_lower)
    check("35_nexon_unresolved_excluded", "nexon remains `context_only`" in all_lower or "nexon remains context-only" in all_lower)
    finding_text = docs.get("findings_admissibility.md", "")
    check("36_findings_admissibility_exists", all(token in finding_text for token in ["`DIRECT`", "`DERIVED`", "`ATTRIBUTED`", "`DESCRIPTIVE`"]))
    forbidden_text = docs.get("forbidden_claims.md", "")
    check("37_forbidden_claims_exist", "world's highest-earning" in forbidden_text and "missing quarters represent zero" in forbidden_text)

    required_names = set(manifest.get("method_hashes", {})) | {"method_freeze_manifest.json", "phase_c_summary.json"}
    required_paths = [PHASE_C / name for name in required_names] + [Path(__file__), ROOT / "work.md"]
    check("38_required_phase_c_files_exist", len(manifest.get("method_hashes", {})) == 18 and all(path.is_file() for path in required_paths))
    hash_ok = all((PHASE_C / name).is_file() and sha256(PHASE_C / name) == expected for name, expected in manifest.get("method_hashes", {}).items())
    check("39_all_freeze_hashes_validate", hash_ok)
    check("40_manifest_parses", manifest_parse_ok, manifest_error)
    check("41_summary_parses", summary_parse_ok and summary.get("method_version") == manifest.get("method_version"), summary_error)

    analytical_ids = {"nikke_ip", "stellar_blade_ip", "lineage_m_title", "black_desert_ip", "marvel_contest_of_champions_title"}
    observed_ids = {row["entity_id"] for row in observations}
    evidence_by_entity = {entity: {row["evidence_class"] for row in observations if row["entity_id"] == entity} for entity in analytical_ids}
    check("42_phase_b_pilot_compatible", len(observations) == 41 and observed_ids == analytical_ids and all(classes <= allowed_quant for classes in evidence_by_entity.values()))

    lineage = [row for row in observations if row["entity_id"] == "lineage_m_title"]
    lineage_versions = {row["metric_version"] for row in lineage}
    lineage_changes_ok = all(not row["previous_observation_id"] or next(obs for obs in observations if obs["observation_id"] == row["previous_observation_id"])["metric_version"] == row["metric_version"] for row in changes if row["entity_id"] == "lineage_m_title")
    check("43_lineage_version_policy_compatible", lineage_versions == {"legacy_v1", "royalty_integrated_v2"} and lineage_changes_ok and any(row["null_reason"] == "METRIC_VERSION_BREAK" for row in changes))

    mcoc = [row for row in observations if row["entity_id"] == "marvel_contest_of_champions_title"]
    check("44_mcoc_derived_policy_compatible", len(mcoc) == 6 and all(row["evidence_class"] == "DERIVED_FROM_OFFICIAL" and row["derivation_id"] and row["lower_bound_krw_million"] and row["upper_bound_krw_million"] for row in mcoc) and len(derivations) == 6)
    entity_map = {row["entity_id"]: row for row in entities}
    check("45_black_desert_ip_policy_compatible", entity_map["black_desert_ip"]["entity_type"] == "IP" and all(row["metric_definition_id"] == "md_pa_black_desert_ip_v1" for row in observations if row["entity_id"] == "black_desert_ip"))
    stellar = [row for row in observations if row["entity_id"] == "stellar_blade_ip"]
    check("46_stellar_event_platform_policy_compatible", len({row["metric_definition_id"] for row in stellar}) == 1 and any(row["event_id"] == "evt_stellar_pc_launch" for row in events))

    primary_lane = {}
    for entity in analytical_ids:
        classes = evidence_by_entity[entity]
        primary_lane[entity] = "DERIVED" if classes == {"DERIVED_FROM_OFFICIAL"} else "DIRECT"
    direct_count = sum(value == "DIRECT" for value in primary_lane.values())
    derived_count = sum(value == "DERIVED" for value in primary_lane.values())
    check("47_phase_b_direct_derived_ratio", direct_count / len(primary_lane) >= manifest["direct_series_min_fraction"] and derived_count / len(primary_lane) <= manifest["derived_series_max_fraction"])

    counts = Counter(row["entity_id"] for row in observations)
    legacy_count = sum(row["metric_version"] == "legacy_v1" for row in lineage)
    continuity_ok = counts["nikke_ip"] >= 6 and counts["stellar_blade_ip"] >= 6 and legacy_count >= 6 and counts["black_desert_ip"] >= 6 and counts["marvel_contest_of_champions_title"] >= 6
    check("48_phase_b_core_continuity", continuity_ok)
    period_ids = {row["fiscal_period_id"] for row in periods}
    check("49_phase_b_fiscal_semantics", all(row["period_start"] and row["period_end"] and row["alignment_status"] for row in periods) and all(row["fiscal_period_id"] in period_ids and row["published_at"] for row in observations))
    check("50_phase_b_evidence_classes_allowed", {row["evidence_class"] for row in observations} <= allowed_quant and len(claims) == 2 and len(events) == 6)
    public_fields = set(public[0]) if public else set()
    check("51_phase_b_public_internal_separation", not ({"local_path", "sha256", "extractor_note", "qa_note"} & public_fields) and not any("E:\\" in str(row) or "research/raw" in str(row) for row in public))
    raw_bytes = sum(int(row["file_size"]) for row in raw_manifest)
    check("52_phase_b_storage_compatible", raw_bytes < manifest["raw_storage_hard_review_mb"] * 1024 * 1024)
    check("53_missingness_states_exact", set(manifest.get("missingness_states", [])) == missing_states)
    check("54_comparability_classes_exact", set(manifest.get("comparability_classes", [])) == comparability)
    amendment_fields = {"reason", "affected_fields", "affected_observations", "rebuild_required", "existing_findings_invalidated"}
    check("55_method_amendment_contract", set(manifest.get("method_amendment_required_fields", [])) == amendment_fields and "documented method amendment" in all_lower)
    work_text = (ROOT / "work.md").read_text(encoding="utf-8")
    no_frontend = not any((ROOT / name).exists() for name in ["src", "node_modules", "vite.config.js", "vite.config.ts", "package.json"])
    check("56_phase_boundary_integrity", "Phase C method/scope freeze completed" in work_text and len(observations) == 41 and no_frontend)

    passed = sum(ok for _, ok, _ in RESULTS)
    for name, ok, detail in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'} {name}" + (f": {detail}" if detail and not ok else ""))
    print(f"\n{passed}/{len(RESULTS)} PASS")
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
