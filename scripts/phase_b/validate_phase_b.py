#!/usr/bin/env python3
"""Automated validation for the Phase B controlled pilot."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "phase-b"
RESEARCH = ROOT / "research" / "phase-b"
BUILD = ROOT / "scripts" / "phase_b" / "build_pilot.py"
RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(condition), detail))


def rows(name: str) -> list[dict]:
    with (DATA / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def unique(table: list[dict], key: str) -> bool:
    values = [row[key] for row in table]
    return len(values) == len(set(values)) and all(values)


def main() -> int:
    generated = [
        "companies.csv", "entities.csv", "fiscal_periods.csv", "metric_definitions.csv", "sources.csv",
        "observations.csv", "derivations.csv", "events.csv", "attributed_claims.csv",
        "comparability_matrix.csv", "change_features.csv", "raw_manifest.csv",
        "public_release_observations.csv", "manual_qa.csv", "build_metadata.json",
    ]
    first_run = subprocess.run([sys.executable, str(BUILD)], cwd=ROOT, capture_output=True, text=True)
    first_hashes = {name: digest(DATA / name) for name in generated if (DATA / name).is_file()}
    second_run = subprocess.run([sys.executable, str(BUILD)], cwd=ROOT, capture_output=True, text=True)
    second_hashes = {name: digest(DATA / name) for name in generated if (DATA / name).is_file()}

    companies = rows("companies.csv")
    entities = rows("entities.csv")
    periods = rows("fiscal_periods.csv")
    metrics = rows("metric_definitions.csv")
    sources = rows("sources.csv")
    observations = rows("observations.csv")
    derivations = rows("derivations.csv")
    events = rows("events.csv")
    claims = rows("attributed_claims.csv")
    comparisons = rows("comparability_matrix.csv")
    changes = rows("change_features.csv")
    manifest = rows("raw_manifest.csv")
    public = rows("public_release_observations.csv")
    qa = rows("manual_qa.csv")
    extractions = rows("input/manual_extractions.csv")

    company_ids = {r["company_id"] for r in companies}
    entity_ids = {r["entity_id"] for r in entities}
    period_ids = {r["fiscal_period_id"] for r in periods}
    metric_ids = {r["metric_definition_id"] for r in metrics}
    source_ids = {r["source_id"] for r in sources}
    observation_ids = {r["observation_id"] for r in observations}
    derivation_ids = {r["derivation_id"] for r in derivations}
    source_map = {r["source_id"]: r for r in sources}
    derivation_map = {r["derivation_id"]: r for r in derivations}
    entity_map = {r["entity_id"]: r for r in entities}
    metric_map = {r["metric_definition_id"]: r for r in metrics}

    check("01_unique_ids", all([
        unique(companies, "company_id"), unique(entities, "entity_id"), unique(periods, "fiscal_period_id"),
        unique(metrics, "metric_definition_id"), unique(sources, "source_id"), unique(observations, "observation_id"),
        unique(derivations, "derivation_id"), unique(events, "event_id"), unique(claims, "claim_id"),
    ]))
    check("02_foreign_keys_resolve", all([
        all(r["company_id"] in company_ids and r["entity_id"] in entity_ids and r["fiscal_period_id"] in period_ids and r["metric_definition_id"] in metric_ids and r["source_id"] in source_ids for r in observations),
        all(r["entity_id"] in entity_ids and r["fiscal_period_id"] in period_ids and r["source_id"] in source_ids for r in events),
        all(r["entity_id"] in entity_ids and r["fiscal_period_id"] in period_ids and r["source_id"] in source_ids for r in claims),
    ]))
    check("03_observations_have_entity_ids", all(r["entity_id"] for r in observations))
    check("04_observations_have_company_ids", all(r["company_id"] for r in observations))
    check("05_observations_have_fiscal_periods", all(r["fiscal_period_id"] for r in observations))
    check("06_observations_have_metric_definitions", all(r["metric_definition_id"] for r in observations))
    check("07_quantitative_evidence_classes", all(r["evidence_class"] in {"OFFICIAL_REPORTED", "DERIVED_FROM_OFFICIAL"} for r in observations))
    check("08_official_values_reference_official_source", all(source_map[r["source_id"]]["officiality"] == "OFFICIAL" for r in observations if r["evidence_class"] == "OFFICIAL_REPORTED"))
    check("09_pdf_values_have_pages", all(r["source_page"] for r in observations if source_map[r["source_id"]]["source_type"].endswith("PDF")))
    check("10_retained_files_have_valid_sha256", all(len(r["sha256"]) == 64 and r["sha256"] == digest(ROOT / r["local_path"]) for r in manifest))
    check("11_derived_observations_have_derivation_ids", all(r["derivation_id"] in derivation_ids for r in observations if r["evidence_class"] == "DERIVED_FROM_OFFICIAL"))
    check("12_derivations_have_formulas", all(r["formula_text"] for r in derivations))
    reproduced_points = all(Decimal(r["point_estimate"]) == Decimal(r["input_total_value"]) * Decimal(r["input_share_percent"]) / 100 for r in derivations)
    check("13_derived_values_reproduce", reproduced_points and all(Decimal(r["reported_value_raw"]) == Decimal(derivation_map[r["derivation_id"]]["point_estimate"]) for r in observations if r["derivation_id"]))
    interval_ok = True
    for r in derivations:
        total, share = Decimal(r["input_total_value"]), Decimal(r["input_share_percent"])
        expected_low = (total * (share - Decimal("0.5")) / 100).quantize(Decimal("0.01"), rounding=ROUND_FLOOR)
        expected_high = (total * (share + Decimal("0.5")) / 100).quantize(Decimal("0.01"), rounding=ROUND_CEILING)
        interval_ok &= Decimal(r["lower_bound"]) == expected_low and Decimal(r["upper_bound"]) == expected_high
    check("14_derived_intervals_reproduce", interval_ok)
    check("15_bounds_contain_point", all(Decimal(r["lower_bound"]) <= Decimal(r["point_estimate"]) <= Decimal(r["upper_bound"]) for r in derivations))
    check("16_raw_values_and_units_preserved", all(r["reported_value_raw"] and r["reported_unit_raw"] in {"KRW", "KRW_million", "KRW_billion"} for r in observations))
    scale_ok = all(Decimal(r["value_krw_million"]) == (Decimal(r["reported_value_raw"]) / 1_000_000 if r["reported_unit_raw"] == "KRW" else Decimal(r["reported_value_raw"]) if r["reported_unit_raw"] == "KRW_million" else Decimal(r["reported_value_raw"]) * 1000) for r in observations)
    check("17_krw_scale_normalization", scale_ok)
    check("18_no_fx_conversion", all(r["currency"] == "KRW" for r in observations) and not any("USD" in str(r) for r in observations))
    check("19_missingness_not_zero", all(not (r["missingness_state"] != "AVAILABLE" and r["reported_value_raw"] == "0") for r in observations))
    lineage = [r for r in observations if r["entity_id"] == "lineage_m_title"]
    check("20_lineage_metric_versions_separate", {r["metric_version"] for r in lineage} == {"legacy_v1", "royalty_integrated_v2"} and len(lineage) == 11)
    keys = [(r["entity_id"], r["fiscal_period_id"], r["metric_definition_id"]) for r in observations]
    check("21_duplicate_observation_key_rejected", len(keys) == len(set(keys)))
    overlap = Counter(r["fiscal_period_id"] for r in lineage)
    check("22_legitimate_version_overlap_allowed", all(overlap[f"fp_ncsoft_2025q{q}"] == 2 for q in (2, 3, 4)))
    version_by_obs = {r["observation_id"]: r["metric_version"] for r in observations}
    check("23_qoq_never_crosses_version_break", all(not r["previous_observation_id"] or version_by_obs[r["previous_observation_id"]] == r["metric_version"] for r in changes) and any(r["null_reason"] == "METRIC_VERSION_BREAK" for r in changes))
    check("24_black_desert_remains_ip", entity_map["black_desert_ip"]["entity_type"] == "IP" and all(r["entity_id"] == "black_desert_ip" for r in observations if r["metric_definition_id"] == "md_pa_black_desert_ip_v1"))
    stellar = [r for r in observations if r["entity_id"] == "stellar_blade_ip"]
    check("25_stellar_platform_event_separate", len({r["metric_definition_id"] for r in stellar}) == 1 and any(r["event_id"] == "evt_stellar_pc_launch" for r in events))
    check("26_mcoc_never_official_reported", all(r["evidence_class"] == "DERIVED_FROM_OFFICIAL" for r in observations if r["entity_id"] == "marvel_contest_of_champions_title"))
    combined_obs = json.dumps(observations, ensure_ascii=False).lower()
    check("27_no_sensor_tower_quantitative_record", "sensor tower" not in combined_obs and "sensortower" not in combined_obs)
    check("28_no_appmagic_quantitative_record", "appmagic" not in combined_obs)
    check("29_no_nexon_amount", "nexon" not in combined_obs)
    check("30_events_link_valid", all(r["entity_id"] in entity_ids and r["fiscal_period_id"] in period_ids for r in events))
    check("31_events_use_official_sources", all(source_map[r["source_id"]]["officiality"] == "OFFICIAL" for r in events))
    check("32_claims_separate", all(r["claim_id"] and r["strength_note"] for r in claims) and not any("ATTRIBUTED_CLAIM" in r["evidence_class"] for r in observations))
    forbidden_causal = ["caused revenue", "event caused", "proved that", "必然导致"]
    stored_text = json.dumps(events + claims, ensure_ascii=False).lower()
    check("33_no_unsupported_causal_conclusion", not any(term in stored_text for term in forbidden_causal))
    check("34_public_table_has_no_assets", not ({"local_path", "sha256", "snapshot_path", "slide_image", "chart_asset"} & set(public[0])) and all("research/raw" not in str(r) for r in public))
    storage = sum(int(r["file_size"]) for r in manifest)
    check("35_snapshot_storage_within_ceiling", storage < 250 * 1024 * 1024, str(storage))
    check("36_deterministic_rebuild_succeeds", first_run.returncode == 0 and second_run.returncode == 0, first_run.stderr + second_run.stderr)
    check("37_second_rebuild_matches_first", first_hashes == second_hashes and len(first_hashes) == len(generated))
    csv_files = list(DATA.rglob("*.csv"))
    csv_ok = True
    for path in csv_files:
        try:
            with path.open(encoding="utf-8", newline="") as handle:
                list(csv.reader(handle))
        except Exception:
            csv_ok = False
    check("38_all_csv_parse", csv_ok and bool(csv_files))
    json_files = list(DATA.rglob("*.json")) + list(RESEARCH.rglob("*.json"))
    json_ok = True
    for path in json_files:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            json_ok = False
    check("39_all_json_parse", json_ok and bool(json_files))
    required = [
        DATA / "entities.csv", DATA / "companies.csv", DATA / "fiscal_periods.csv", DATA / "metric_definitions.csv",
        DATA / "sources.csv", DATA / "input" / "manual_extractions.csv", DATA / "observations.csv", DATA / "derivations.csv",
        DATA / "events.csv", DATA / "attributed_claims.csv", DATA / "comparability_matrix.csv", DATA / "change_features.csv", DATA / "raw_manifest.csv",
        RESEARCH / "PHASE_B_CONTROLLED_PILOT.md", RESEARCH / "entity_identity_audit.md", RESEARCH / "fiscal_period_audit.md",
        RESEARCH / "metric_versioning_audit.md", RESEARCH / "lineage_m_metric_break_audit.md", RESEARCH / "stellar_blade_platform_scope_audit.md",
        RESEARCH / "black_desert_entity_scope_audit.md", RESEARCH / "derived_value_audit.md", RESEARCH / "missingness_audit.md",
        RESEARCH / "event_linkage_audit.md", RESEARCH / "source_provenance_audit.md", RESEARCH / "public_release_field_policy.md",
        RESEARCH / "storage_audit.md", RESEARCH / "phase_b_summary.json", BUILD, Path(__file__), ROOT / "work.md",
    ]
    check("40_required_files_exist", all(path.is_file() for path in required), ", ".join(str(p) for p in required if not p.is_file()))
    check("41_pilot_scope_and_counts", len(observations) == 41 and len({r["entity_id"] for r in observations}) == 5 and len({r["company_id"] for r in observations}) == 4 and len(observations) <= 50)
    expected_counts = {"nikke_ip": 8, "stellar_blade_ip": 8, "lineage_m_title": 11, "black_desert_ip": 8, "marvel_contest_of_champions_title": 6}
    check("42_series_continuity_counts", Counter(r["entity_id"] for r in observations) == expected_counts)
    check("43_event_target", 6 <= len(events) <= 8 and len({r["entity_id"] for r in events}) >= 3)
    qa_counts = Counter("lineage_m_title" if "lm_" in r["observation_id"] else next(o["entity_id"] for o in observations if o["observation_id"] == r["observation_id"]) for r in qa)
    check("44_manual_qa_coverage", all(qa_counts[e] >= 2 for e in expected_counts) and any("lm_v2" in r["observation_id"] for r in qa) and sum("mcoc" in r["observation_id"] for r in qa) >= 2)
    check("45_fiscal_period_alignment_explicit", all(r["period_start"] and r["period_end"] and r["alignment_status"] == "VERIFIED_CALENDAR_ALIGNED" for r in periods))
    check("46_entity_type_vocabulary", {"COMPANY", "GAME_TITLE", "GAME_EDITION", "IP", "FRANCHISE", "PLATFORM"} <= {r["entity_type"] for r in entities})
    check("47_metric_unknowns_explicit", all(r["includes_royalties"] and r["includes_licensing"] and r["includes_platform_receipts"] for r in metrics))
    check("48_lineage_comparability_version_break", any(r["comparability_status"] == "VERSION_BREAK" and {r["left_metric_definition_id"], r["right_metric_definition_id"]} == {"md_nc_lineage_m_legacy_v1", "md_nc_lineage_m_royalty_v2"} for r in comparisons))
    official_domains = {"shiftup.co.kr", "ncsoft-brand-web.s3.ap-northeast-2.amazonaws.com", "www.pearlabyss.com", "sgimage.netmarble.com", "blog.playstation.com", "about.ncsoft.com", "blackdesert.pearlabyss.com"}
    check("49_sources_public_official_urls", all(urlparse(r["source_url"]).netloc in official_domains and r["access_class"] == "PUBLIC_NO_LOGIN" for r in sources))
    check("50_no_ocr_or_chart_geometry", all(r["extraction_method"] == "TEXT_TABLE" for r in extractions))
    check("51_no_frontend_created", not any((ROOT / name).exists() for name in ["src", "node_modules", "vite.config.js", "vite.config.ts", "package.json"]))
    check("52_public_release_traceability", len(public) == len(observations) and all(r["canonical_source_url"] and r["source_page"] for r in public))

    passed = sum(ok for _, ok, _ in RESULTS)
    for name, ok, detail in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'} {name}" + (f": {detail}" if detail and not ok else ""))
    print(f"\n{passed}/{len(RESULTS)} PASS")
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
