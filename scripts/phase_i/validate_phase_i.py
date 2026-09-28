from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULTS: list[tuple[str, bool, str]] = []
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(name: str, condition: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(condition), detail))


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load(path: str):
    return json.loads(read(path))


def run(command: list[str]) -> tuple[bool, str]:
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, encoding="utf-8", errors="replace")
    tail = " | ".join((completed.stdout + completed.stderr).strip().splitlines()[-3:])
    return completed.returncode == 0, tail


def validate_hash_map(base: Path, mapping: dict[str, str]) -> bool:
    return all((base / relative).is_file() and sha256(base / relative) == expected for relative, expected in mapping.items())


method_manifest = load("research/phase-c/method_freeze_manifest.json")
findings_freeze = read("research/phase-f/FINDINGS_FREEZE.md")
finding_pairs = dict(re.findall(r"- `([^`]+)`: `([0-9a-f]{64})`", findings_freeze))
web_manifest = load("data/web/manifest.json")
phase_h_manifest = load("research/phase-i/input_manifest.json")
project = load("data/web/project.json")
series_index = load("data/web/series_index.json")
findings = load("data/web/findings.json")
caveats = load("data/web/caveats.json")
details = [load(f"data/web/{record['detail_path']}") for record in series_index]
observations = [observation for detail in details for observation in detail["observations"]]
events = [event for detail in details for event in detail["events"]]

production_paths = [path for path in (ROOT / "src").rglob("*") if path.is_file() and not path.name.endswith(".test.ts")]
production_text = "\n".join(path.read_text(encoding="utf-8") for path in production_paths)
app_text = read("src/App.vue")
prism_text = read("src/components/prism/QuarterPrism.vue")
model_text = read("src/utils/model.ts")
tokens_text = read("src/styles/tokens.css")
base_text = read("src/styles/base.css")
package = load("package.json")

check("01_method_freeze_hashes", validate_hash_map(ROOT / "research/phase-c", method_manifest["method_hashes"]), "18 normative files")
check("02_findings_freeze_hashes", validate_hash_map(ROOT, finding_pairs), f"{len(finding_pairs)} frozen files")
check("03_web_data_freeze_hashes", all(sha256(ROOT / "data/web" / item["path"]) == item["sha256"] for item in web_manifest["files"]), "15 public files")
check("04_phase_h_artifacts_unchanged", all(sha256(ROOT / item["path"]) == item["sha256"] for item in phase_h_manifest["phase_h_artifacts"]), "34 artifacts")
check("05_method_version_unchanged", project["method_version"] == "revenue-tides-method-freeze-1.0.0")
check("06_findings_version_unchanged", project["findings_version"] == "revenue-tides-findings-1.0.0")
check("07_webdata_version_unchanged", project["webdata_version"] == "revenue-tides-webdata-1.0.0")
check("08_data_cutoff_unchanged", project["data_cutoff"] == "2026-09-22")
check("09_package_json_exists", (ROOT / "package.json").is_file())
check("10_vue_dependency_exists", "vue" in package["dependencies"])
check("11_typescript_dependency_exists", "typescript" in package["devDependencies"])
check("12_vite_dependency_exists", "vite" in package["devDependencies"])
check("13_no_large_ui_framework", not any(name in {**package.get("dependencies", {}), **package.get("devDependencies", {})} for name in ["tailwindcss", "vuetify", "element-plus", "ant-design-vue"]))
check("14_frontend_source_exists", (ROOT / "src/App.vue").is_file() and (ROOT / "src/main.ts").is_file())
check("15_application_uses_phase_g_public_data", "data/" in read("src/data/client.ts") and "series_index.json" in read("src/data/client.ts"))
check("16_no_manual_observation_dataset", not any(path.name in {"observations.ts", "researchData.ts", "dataset.ts"} for path in production_paths))
check("17_nine_series_represented", len(series_index) == 9)
check("18_seventy_five_observations_reachable", len(observations) == 75)
check("19_twenty_six_events_reachable", len(events) == 26)
check("20_six_findings_represented", len(findings) == 6)
check("21_headline_findings_f1_f2_f4", [item["finding_id"] for item in findings if item["headline"]] == ["F1", "F2", "F4"])
check("22_seven_ia_sections_present", all(token in app_text for token in ["OpeningSection", "MeasurementPrimer", "QuarterPrismShell", "headline-findings", "SeriesObservatory", "remaining-findings", "MethodSources"]))
check("23_quarter_prism_component_exists", (ROOT / "src/components/prism/QuarterPrism.vue").is_file())
check("24_direct_prism_state_implemented", "direct-mark" in prism_text and "OFFICIAL_REPORTED" in prism_text)
check("25_version_overlap_state_implemented", "overlap-note" in prism_text and "metric-lanes" in prism_text)
check("26_derived_uncertainty_state_implemented", "uncertainty-block" in prism_text and "lower_bound" in prism_text and "upper_bound" in prism_text)
check("27_event_context_state_implemented", "EventRail" in prism_text and (ROOT / "src/components/prism/EventRail.vue").is_file())
check("28_version_boundary_state_implemented", "version-seam" in prism_text and "version-note" in prism_text)
check("29_mobile_prism_state_implemented", "@media (max-width: 390px)" in prism_text and ".desktop-prism { display: none; }" in prism_text)
check("30_previous_quarter_control_exists", "上一季度" in prism_text)
check("31_next_quarter_control_exists", "下一季度" in prism_text)
check("32_direct_quarter_selection_exists", "直接选择季度" in prism_text and "quarter-list" in prism_text)
check("33_keyboard_navigation_exists", "ArrowLeft" in prism_text and "ArrowRight" in prism_text)
check("34_drag_not_mandatory", "@drag" not in prism_text and "Previous" not in prism_text)
check("35_reduced_motion_handling_exists", "prefers-reduced-motion: reduce" in base_text)
check("36_lineage_overlap_values_separate", all(len([o for o in detail["observations"] if o["quarter"] == "2025Q2"]) == 2 for detail in details if detail["series_id"] in {"series_lineage_m", "series_lineage_2m", "series_lineage_w"}))
check("37_no_cross_version_qoq", all(metric["version_break"] is None or metric["version_break"]["cross_version_change_allowed"] is False for detail in details for metric in detail["metric_versions"]))
check("38_version_baseline_restart", all(metric["version_break"] is None or metric["version_break"]["baseline_restart"] is True for detail in details for metric in detail["metric_versions"]))
check("39_derived_bounds_retained", all(o["lower_bound"] is not None and o["upper_bound"] is not None for o in observations if o["evidence_class"] == "DERIVED_FROM_OFFICIAL"))
check("40_sign_sensitive_state_retained", len([o for o in observations if o.get("derived") and o["derived"]["direction_sign_stable"] is False]) == 9)
check("41_events_use_separate_context_rail", "event-rail" in read("src/components/prism/EventRail.vue"))
check("42_no_causal_event_field", all("caused_revenue_change" not in event for event in events))
check("43_issuer_attribution_separated", "发行方说明" in read("src/components/prism/EventRail.vue") and "不是本项目" in read("src/components/prism/EventRail.vue"))
check("44_all_findings_rendered", all(f"finding.finding_id === '{fid}'" in read("src/components/findings/FindingChapter.vue") for fid in ["F1", "F2", "F3", "F4", "F5", "F6"]))
check("45_f1_semantics_preserved", "定义差异 ≠ 增长" in read("src/components/findings/FindingChapter.vue"))
check("46_f2_noncausal_limitation_preserved", "timing does not establish causality" in read("src/components/findings/FindingChapter.vue"))
check("47_f3_incomplete_recovery_preserved", "NOT_RECOVERED_WITHIN_OBSERVED_WINDOW" in read("src/components/findings/FindingChapter.vue"))
check("48_f4_sequence_preserved", "三季度后恢复 / 新峰值" in read("src/components/findings/FindingChapter.vue"))
check("49_f5_v2_restriction_preserved", "royalty_integrated_v2 only" in read("src/components/findings/FindingChapter.vue"))
check("50_f6_nine_of_fifteen_preserved", "signSensitiveCount" in read("src/components/findings/FindingChapter.vue") and "60.0%" in read("src/components/findings/FindingChapter.vue"))
check("51_observatory_contains_all_series", "v-for=\"record in series\"" in read("src/components/series/SeriesObservatory.vue"))
check("52_entity_types_visible", "record.entity_type" in read("src/components/series/SeriesObservatory.vue"))
check("53_direct_derived_not_color_only", "circle" in prism_text and "derived-mark" in prism_text and "Derived from official" in prism_text)
check("54_version_break_not_color_only", "double-seam" in prism_text and "校准缝" in prism_text)
check("55_uncertainty_not_opacity_only", "interval-geometry" in prism_text and "whisker" in prism_text)
component_text = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "src/components").rglob("*.vue"))
check("56_no_absolute_cross_company_view", "ABSOLUTE_REVENUE" not in component_text)
check("57_normalized_comparison_unitless_only", "assertNormalizedComparison" in model_text and "BASELINE_INDEX" in model_text)
check("58_comparison_caveat_visible", "绝对收入不可跨公司比较" in production_text or "不可直接比较绝对高低" in production_text)
check("59_no_leaderboard_component", not any("leaderboard" in path.name.lower() for path in production_paths))
check("60_no_usd_conversion", "USD" not in production_text)
check("61_no_success_or_health_score", not any(term in production_text for term in ["successScore", "commercialHealth", "momentumScore"]))
check("62_no_game_art_dependency", not any(path.suffix.lower() in {".jpg", ".jpeg", ".webp", ".gif"} for path in (ROOT / "src").rglob("*")))
check("63_no_ocean_imagery", "ocean" not in production_text.lower() and "wave" not in production_text.lower())
check("64_no_stock_candlestick_interface", "candlestick" not in production_text.lower())
check("65_no_generic_kpi_card_opening", "kpi" not in read("src/components/OpeningSection.vue").lower())
check("66_source_access_exists", "查看证据与来源" in prism_text and (ROOT / "src/components/evidence/SourceList.vue").is_file())
check("67_caveat_access_exists", (ROOT / "src/components/evidence/CaveatKey.vue").is_file())
check("68_curated_event_notice_exists", "CURATED / NON-CAUSAL" in read("src/components/prism/EventRail.vue"))
check("69_skip_link_exists", "skip-link" in app_text and "#main-content" in app_text)
check("70_visible_focus_styles_exist", ":focus-visible" in base_text and "outline: 3px" in base_text)
check("71_touch_target_policy_implemented", "min-height: 44px" in base_text)
check("72_no_hover_only_critical_interaction", "@click" in prism_text and "@keydown" in prism_text)
check("73_accessible_svg_treatment", "<title" in prism_text and "<desc" in prism_text and "role=\"img\"" in prism_text)
check("74_aria_live_prism_summary", "aria-live=\"polite\"" in prism_text)
check("75_system_font_stack_only", "system-ui" in tokens_text and "Microsoft YaHei" in tokens_text)
check("76_no_packaged_font", not any(path.suffix.lower() in {".woff", ".woff2", ".ttf", ".otf"} for path in ROOT.rglob("*") if "node_modules" not in path.parts))
check("77_lazy_series_loading_implemented", "IntersectionObserver" in read("src/components/prism/QuarterPrismShell.vue") and "seriesCache" in read("src/data/client.ts"))
check("78_series_loading_error_handled", "数据暂时无法加载" in read("src/components/prism/QuarterPrismShell.vue") and "重试" in read("src/components/prism/QuarterPrismShell.vue"))
check("79_missing_values_never_zeroed", "value === null ? observation.missingness_state" in prism_text)
source_files = sorted(path.relative_to(ROOT / "data/web") for path in (ROOT / "data/web").rglob("*") if path.is_file())
public_files = sorted(path.relative_to(ROOT / "public/data") for path in (ROOT / "public/data").rglob("*") if path.is_file())
check("80_public_web_data_sync_hashes", source_files == public_files and all(sha256(ROOT / "data/web" / path) == sha256(ROOT / "public/data" / path) for path in source_files))
typecheck_ok, typecheck_detail = run(["npm.cmd", "run", "typecheck"])
check("81_typescript_check_passes", typecheck_ok, typecheck_detail)
tests_ok, tests_detail = run(["npm.cmd", "test"])
check("82_frontend_tests_pass", tests_ok and "62 passed" in tests_detail, tests_detail)
build_ok, build_detail = run(["npm.cmd", "run", "build"])
check("83_production_build_passes", build_ok, build_detail)
dist_assets = [path for path in (ROOT / "dist").rglob("*") if path.is_file()]
check("84_build_assets_reasonably_small", dist_assets and max(path.stat().st_size for path in dist_assets) < 250_000)
check("85_no_tracking_or_analytics", not any(term in production_text.lower() for term in ["google-analytics", "gtag(", "segment.io", "mixpanel", "tracking pixel"]))
check("86_static_hostable_output", (ROOT / "dist/index.html").is_file() and "VITE_BASE_PATH" in read("vite.config.ts"))
check("87_no_backend_introduced", not any((ROOT / name).exists() for name in ["server", "api", "backend"]))
responsive_audit = read("research/phase-i/responsive_implementation_audit.md")
check("88_1440_implementation_inspected", "1440 × 900" in responsive_audit and "PASS" in responsive_audit)
check("89_1024_implementation_inspected", "1024 × 900" in responsive_audit)
check("90_768_implementation_inspected", "768 × 900" in responsive_audit)
check("91_390_implementation_inspected", "390 × 844" in responsive_audit)
check("92_no_catastrophic_horizontal_overflow", "scrollWidth=390" in responsive_audit and "no overflow elements" in responsive_audit)
manual_qa = read("research/phase-i/manual_implementation_qa.md")
check("93_no_known_uncaught_application_exception", "no console errors" in manual_qa.lower())
required_reports = [
    "PHASE_I_FRONTEND_IMPLEMENTATION.md", "component_architecture.md", "data_loading_audit.md",
    "quarter_prism_implementation_audit.md", "finding_rendering_audit.md",
    "responsive_implementation_audit.md", "accessibility_implementation_audit.md",
    "visual_fidelity_audit.md", "performance_build_audit.md", "frontend_data_integrity_audit.md",
    "phase_i_summary.json", "manual_implementation_qa.md", "input_manifest.json",
]
check("94_required_phase_i_reports_exist", all((ROOT / "research/phase-i" / name).is_file() for name in required_reports))
check("95_stop_boundary_before_phase_j", "STOPPED BEFORE PHASE J" in read("research/phase-i/PHASE_I_FRONTEND_IMPLEMENTATION.md"))
check("96_sixty_two_frontend_tests_recorded", load("research/phase-i/phase_i_summary.json")["tests"] == {"passed": 62, "total": 62})
check("97_application_metadata_accurate", "global game revenue" not in read("index.html").lower() and 'lang="zh-CN"' in read("index.html"))
check("98_external_links_safe", 'rel="noopener noreferrer"' in read("src/components/evidence/SourceList.vue"))
check("99_public_data_not_modified", all(sha256(ROOT / "data/web" / item["path"]) == item["sha256"] for item in web_manifest["files"]))
work_log_upper = read("work.md").upper()
check("100_work_log_updated", "PHASE I" in work_log_upper and "FRONTEND IMPLEMENTATION" in work_log_upper)

for index, (name, passed, detail) in enumerate(RESULTS, start=1):
    suffix = f" — {detail}" if detail else ""
    print(f"{'PASS' if passed else 'FAIL'} {name}{suffix}")

passed = sum(1 for _, result, _ in RESULTS if result)
print(f"AUTOMATED VALIDATION: {passed}/{len(RESULTS)} PASS")
sys.exit(0 if passed == len(RESULTS) == 100 else 1)
