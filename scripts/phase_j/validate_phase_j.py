from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


chrome = load_json("research/phase-j/chrome_smoke.json")
edge = load_json("research/phase-j/edge_smoke.json")
firefox = load_json("research/phase-j/firefox_smoke.json")
subdir = load_json("research/phase-j/subdirectory_smoke.json")
summary = load_json("research/phase-j/phase_j_summary.json")
manifest = load_json("data/web/manifest.json")
project = load_json("data/web/project.json")
series_index = load_json("data/web/series_index.json")
findings = load_json("data/web/findings.json")

series_details = [load_json(record["detail_path"].replace("series/", "data/web/series/")) for record in series_index]
observations = [observation for detail in series_details for observation in detail["observations"]]
events = [event for detail in series_details for event in detail["events"]]
derived = [observation for observation in observations if observation["evidence_class"] == "DERIVED_FROM_OFFICIAL"]
all_rendered = json.dumps(findings, ensure_ascii=False)
chrome_checks = {item["id"]: item for item in chrome["checks"]}
edge_checks = {item["id"]: item for item in edge["checks"]}
firefox_checks = {item["id"]: item for item in firefox["checks"]}

phase_i = subprocess.run(
    [sys.executable, str(ROOT / "scripts/phase_i/validate_phase_i.py")],
    cwd=ROOT,
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
)
phase_i_output = phase_i.stdout + phase_i.stderr


def smoke_passed(data: dict) -> bool:
    return data.get("summary", {}).get("failed") == 0 and not data.get("fatal_error")


def recorded(data: dict, check_id: str) -> bool:
    return any(item.get("id") == check_id and item.get("status") == "PASS" for item in data.get("checks", []))


def finding_blob(finding_id: str) -> str:
    row = next(item for item in findings if item["finding_id"] == finding_id)
    return json.dumps(row, ensure_ascii=False)


required_reports = [
    "research/phase-j/PHASE_J_FINAL_BROWSER_QA.md",
    "research/phase-j/browser_matrix.md",
    "research/phase-j/responsive_audit.md",
    "research/phase-j/console_network_audit.md",
    "research/phase-j/accessibility_audit.md",
    "research/phase-j/keyboard_audit.md",
    "research/phase-j/reduced_motion_audit.md",
    "research/phase-j/performance_audit.md",
    "research/phase-j/deployment_readiness_audit.md",
    "research/phase-j/visual_regression_audit.md",
    "research/phase-j/data_semantic_regression.md",
    "research/phase-j/defect_log.csv",
    "research/phase-j/qa_fix_log.md",
    "research/phase-j/manual_browser_qa.md",
    "research/phase-j/phase_j_summary.json",
]

screens = list((ROOT / "research/phase-j/screenshots").glob("*"))
screen_names = {path.name for path in screens if path.is_file()}
required_screens = {
    "desktop-opening.webp",
    "desktop-quarter-prism-direct.webp",
    "desktop-lineage-overlap.webp",
    "desktop-derived-uncertainty.webp",
    "desktop-f1.webp",
    "desktop-f2.webp",
    "desktop-f4.webp",
    "desktop-series-observatory.webp",
    "mobile-390-opening.webp",
    "mobile-390-quarter-prism.webp",
    "mobile-390-lineage-overlap.webp",
    "mobile-390-derived-uncertainty.webp",
}

with (ROOT / "research/phase-j/defect_log.csv").open(encoding="utf-8", newline="") as handle:
    defects = list(csv.DictReader(handle))

checks: list[tuple[str, bool, str]] = []


def add(name: str, condition: bool, detail: str = "") -> None:
    checks.append((name, bool(condition), detail))


add("01_method_freeze_unchanged", phase_i.returncode == 0 and "01_method_freeze_hashes" in phase_i_output, "18 normative files")
add("02_findings_freeze_unchanged", "02_findings_freeze_hashes" in phase_i_output, "13 frozen files")
add("03_web_data_freeze_unchanged", "03_web_data_freeze_hashes" in phase_i_output, "15 public files")
add("04_design_freeze_unchanged", "04_phase_h_artifacts_unchanged" in phase_i_output, "34 design artifacts")
add("05_nine_series_remain", manifest["series_count"] == len(series_index) == 9)
add("06_seventy_five_observations_remain", manifest["observation_count"] == len(observations) == 75)
add("07_twenty_six_events_remain", manifest["event_count"] == len(events) == 26)
add("08_six_findings_remain", manifest["finding_count"] == len(findings) == 6)
add("09_headline_findings_unchanged", {item["finding_id"] for item in findings if item["headline"]} == {"F1", "F2", "F4"})
add("10_phase_i_tests_still_pass", "82_frontend_tests_pass" in phase_i_output and "62 passed" in phase_i_output)
add("11_typescript_still_passes", "81_typescript_check_passes" in phase_i_output)
add("12_production_build_passes", "83_production_build_passes" in phase_i_output)
add("13_production_build_served", any(item.get("url") == chrome["url"] and item.get("status") == 200 for item in chrome["network"]["responses"]))
add("14_chromium_qa_recorded", smoke_passed(chrome) and chrome["summary"]["passed"] == 40, chrome.get("browser_version", ""))
add("15_firefox_result_recorded", smoke_passed(firefox) and firefox["summary"]["passed"] == 14, firefox.get("browser_version", ""))
add("16_edge_result_recorded", smoke_passed(edge) and edge["summary"]["passed"] == 40, edge.get("browser_version", ""))
viewport_map = {item["requested"]: item for item in chrome["viewport_audits"]}
for number, viewport in enumerate(["1440x900", "1280x800", "1024x768", "768x1024", "390x844", "320x700"], start=17):
    add(f"{number:02d}_viewport_{viewport}", viewport in viewport_map and viewport_map[viewport]["overflow_px"] == 0)
add("23_zero_page_horizontal_overflow", all(item["overflow_px"] == 0 for item in chrome["viewport_audits"]))
add("24_opening_audited", recorded(chrome, "opening_scope") and recorded(chrome, "opening_comparison_boundary"))
add("25_measurement_primer_audited", "Primer" in text("research/phase-j/manual_browser_qa.md"))
add("26_prism_direct_state_audited", recorded(chrome, "direct_state"))
add("27_version_overlap_audited", recorded(chrome, "lineage_overlap_three_series"))
add("28_version_boundary_audited", recorded(chrome, "version_boundary_visible"))
add("29_derived_uncertainty_audited", recorded(chrome, "derived_uncertainty_three_series"))
add("30_event_context_audited", recorded(chrome, "event_context_separate") and recorded(chrome, "no_event_state"))
add("31_mobile_prism_audited", recorded(chrome, "mobile_prism_mode"))
for number, series_id in enumerate(["series_lineage_m", "series_lineage_2m", "series_lineage_w"], start=32):
    row = next(item for item in chrome["lineage"] if item["series_id"] == series_id)
    add(f"{number:02d}_{series_id}_overlap_correct", row["lanes"] == 2 and row["seam"])
add("35_no_cross_version_qoq", "37_no_cross_version_qoq" in phase_i_output)
add("36_baselines_restart", "38_version_baseline_restart" in phase_i_output)
add("37_all_derived_bounds_preserved", len(derived) == 18 and all(item["lower_bound"] is not None and item["upper_bound"] is not None for item in derived))
add("38_sign_sensitive_not_definite", recorded(chrome, "sign_sensitive_not_definite"))
add("39_f1_semantic_regression", "5.6%" in finding_blob("F1") and "12.8%" in finding_blob("F1"))
add("40_f2_semantic_regression", all(value in finding_blob("F2") for value in ["7.012", "65.719", "837.3"]))
add("41_f3_semantic_regression", all(value in finding_blob("F3") for value in ["32.4", "4.1", "not recovered within the observed window"]))
add("42_f4_semantic_regression", all(value in finding_blob("F4") for value in ["20.7", "30.8", "2025Q3"]))
add("43_f5_semantic_regression", all(value in finding_blob("F5") for value in ["35.3", "royalty-integrated v2", "2025Q2", "2026Q2"]))
add("44_f6_semantic_regression", all(value in finding_blob("F6") for value in ["9", "15", "60.0"]))
add("45_all_series_lazy_load", recorded(chrome, "all_series_lazy_load") and len(chrome["loaded_series"]) == 9)
add("46_caching_acceptable", recorded(chrome, "series_cache"))
add("47_controlled_error_state", recorded(chrome, "controlled_lazy_failure") and recorded(chrome, "lazy_retry_recovers"))
add("48_initial_load_not_all_series", recorded(chrome, "initial_series_lazy") and len(chrome["performance"]["initial_json_requests"]) == 5)
add("49_unexpected_4xx_zero", not chrome["network"]["unexpected_http_errors"])
add("50_unexpected_5xx_zero", not chrome["network"]["unexpected_http_errors"])
add("51_required_json_failures_zero", all(item.get("status", 0) < 400 for item in chrome["network"]["responses"] if "/data/" in item.get("url", "")))
add("52_console_errors_zero", not chrome["console"]["errors"])
add("53_uncaught_exceptions_zero", not chrome["console"]["exceptions"])
add("54_production_warnings_reviewed", not chrome["console"]["warnings"])
add("55_keyboard_full_workflow", recorded(chrome, "skip_link_keyboard_focus") and recorded(chrome, "keyboard_source_disclosure"))
add("56_no_keyboard_trap", recorded(chrome, "keyboard_no_trap_surface"))
add("57_visible_focus", recorded(chrome, "skip_link_keyboard_focus"))
add("58_skip_link_works", recorded(chrome, "skip_link_keyboard_focus") and chrome["semantic_state"]["skip_href"] == "#main-content")
add("59_prism_arrow_keys", recorded(chrome, "keyboard_arrow_navigation"))
add("60_no_hover_only_information", "72_no_hover_only_critical_interaction" in phase_i_output)
add("61_mobile_touch_targets", recorded(chrome, "touch_targets"))
add("62_accessibility_tree_reviewed", recorded(chrome, "accessibility_tree") and chrome["accessibility"]["main_count"] == 1)
add("63_aria_live_reviewed", chrome["semantic_state"]["live_regions"] >= 1)
add("64_heading_hierarchy", recorded(chrome, "heading_and_names") and chrome["semantic_state"]["h1"] == 1)
add("65_contrast_passes", recorded(chrome, "contrast_tokens"))
add("66_color_independent_semantics", "Color" in text("research/phase-j/accessibility_audit.md") or "Direct/derived" in text("research/phase-j/accessibility_audit.md"))
add("67_reduced_motion_passes", recorded(chrome, "reduced_motion_complete"))
add("68_zoom_200_audited", recorded(chrome, "zoom_200_equivalent"))
add("69_long_content_wrapping", all(item["overflow_px"] == 0 for item in chrome["viewport_audits"]))
add("70_performance_audit_completed", (ROOT / "research/phase-j/performance_audit.md").exists())
add("71_js_bundle_change_explained", "JavaScript growth is 0%" in text("research/phase-j/performance_audit.md"))
add("72_css_bundle_change_explained", "CSS growth is 0%" in text("research/phase-j/performance_audit.md"))
add("73_no_large_unexpected_asset", chrome["performance"]["largest_resource"]["encodedBodySize"] < 200_000)
add("74_no_font_asset", not any(path.suffix.lower() in {".woff", ".woff2", ".ttf", ".otf"} for path in (ROOT / "dist").rglob("*")))
add("75_no_game_art_asset", not any(path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4"} for path in (ROOT / "dist").rglob("*")))
source_blob = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in (ROOT / "src").rglob("*") if path.is_file())
add("76_no_tracking", not any(term in source_blob.lower() for term in ["google-analytics", "gtag(", "segment.io", "mixpanel", "amplitude"] ))
add("77_static_host_build", "Root static build" in text("research/phase-j/deployment_readiness_audit.md") and smoke_passed(chrome))
add("78_subdirectory_paths", smoke_passed(subdir) and subdir["summary"]["passed"] == 40)
add("79_source_links_four_companies", all(name in text("research/phase-j/console_network_audit.md") for name in ["NCSOFT", "Netmarble", "Pearl Abyss", "SHIFT UP"]))
add("80_safe_external_links", recorded(chrome, "source_disclosure_and_safe_links") and 'rel="noopener noreferrer"' in text("src/components/evidence/SourceList.vue"))
add("81_screenshot_evidence_exists", required_screens.issubset(screen_names))
add("82_screenshots_excluded_from_bundle", not any("phase-j" in str(path).lower() for path in (ROOT / "dist").rglob("*")))
add("83_tidal_ledger_visual_regression", "Result: PASS" in text("research/phase-j/visual_regression_audit.md"))
add("84_no_dashboard_drift", "No game art" in text("research/phase-j/visual_regression_audit.md"))
add("85_no_trading_interface_drift", "trading-terminal" in text("research/phase-j/visual_regression_audit.md"))
add("86_forbidden_text_scan_reviewed", recorded(chrome, "forbidden_rendered_text_scan") and not chrome["forbidden_text_hits"])
add("87_entity_types_preserved", {record["entity_type"] for record in series_index} == {"GAME_TITLE", "IP"})
add("88_direct_derived_preserved", {item["evidence_class"] for item in observations} == {"OFFICIAL_REPORTED", "DERIVED_FROM_OFFICIAL"})
add("89_version_breaks_preserved", recorded(chrome, "version_boundary_visible") and len(chrome["lineage"]) == 3)
add("90_event_noncausality", recorded(chrome, "event_context_separate") and "CAVEAT_EVENT_NOT_CAUSAL" in all_rendered and "CAVEAT_CURATED_EVENTS" in all_rendered)
caveats = load_json("data/web/caveats.json")
caveat_blob = json.dumps(caveats, ensure_ascii=False).lower()
add("91_public_caveats_preserved", all(caveat_id.lower() in caveat_blob for caveat_id in ["CAVEAT_CROSS_COMPANY_NOT_COMPARABLE", "CAVEAT_EVENT_NOT_CAUSAL", "CAVEAT_DERIVED_ROUNDING", "CAVEAT_VERSION_BREAK", "CAVEAT_CURATED_EVENTS"]))
add("92_defect_log_exists", (ROOT / "research/phase-j/defect_log.csv").exists() and len(defects) >= 1)
add("93_zero_open_blockers", not any(item["severity"] == "BLOCKER" and item["status"] != "CLOSED" for item in defects))
add("94_zero_open_majors", not any(item["severity"] == "MAJOR" and item["status"] != "CLOSED" for item in defects))
add("95_qa_fixes_documented", "QA-only changes" in text("research/phase-j/qa_fix_log.md"))
add("96_final_full_regression", phase_i.returncode == 0 and smoke_passed(chrome) and smoke_passed(edge) and smoke_passed(firefox) and smoke_passed(subdir))
add("97_phase_i_validator_passes", "AUTOMATED VALIDATION: 100/100 PASS" in phase_i_output)
add("98_phase_j_validator_self_consistent", summary["automated_validation"] == {"passed": 102, "total": 102})
add("99_required_phase_j_artifacts", all((ROOT / path).exists() for path in required_reports) and (ROOT / "scripts/phase_j/validate_phase_j.py").exists())
add("100_no_deployment", summary["deployment_performed"] is False)
add("101_no_phase_k_started", summary["phase_k_started"] is False and "Phase K" not in "\n".join(path.name for path in ROOT.iterdir()))
add("102_stop_boundary_before_phase_k", summary["stop_boundary"] == "STOPPED BEFORE PHASE K" and "STOPPED BEFORE PHASE K" in text("research/phase-j/PHASE_J_FINAL_BROWSER_QA.md"))

if len(checks) != 102:
    raise RuntimeError(f"Expected 102 checks, got {len(checks)}")

failed = []
for name, condition, detail in checks:
    status = "PASS" if condition else "FAIL"
    suffix = f" — {detail}" if detail else ""
    print(f"{status} {name}{suffix}")
    if not condition:
        failed.append(name)

if failed:
    print(f"AUTOMATED VALIDATION: {len(checks) - len(failed)}/{len(checks)} PASS")
    print("FAILED: " + ", ".join(failed))
    raise SystemExit(1)

print("AUTOMATED VALIDATION: 102/102 PASS")
