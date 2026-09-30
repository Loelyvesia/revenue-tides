from __future__ import annotations

import gzip
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "research" / "bold-rebuild"
WEB = ROOT / "data" / "web"
RESULTS: list[dict[str, str]] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    RESULTS.append({"name": name, "status": "PASS" if condition else "FAIL", "detail": detail})


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def data(path: Path):
    return json.loads(read(path))


def git_unchanged(*paths: str) -> bool:
    return subprocess.run(
        ["git", "diff", "--quiet", "HEAD", "--", *paths], cwd=ROOT
    ).returncode == 0


manifest = data(WEB / "manifest.json")
project = data(WEB / "project.json")
index = data(WEB / "series_index.json")
findings = data(WEB / "findings.json")
details = [data(WEB / item["detail_path"]) for item in index]
observations = [obs for detail in details for obs in detail["observations"]]
events = [event for detail in details for event in detail["events"]]
derived = [obs for obs in observations if obs["evidence_class"] == "DERIVED_FROM_OFFICIAL"]

hero = read(ROOT / "src/components/v2/HeroV2.vue")
measurement = read(ROOT / "src/components/v2/MeasurementStory.vue")
prism = read(ROOT / "src/components/v2/QuarterPrismV2.vue")
findings_component = read(ROOT / "src/components/v2/HeadlineFindingsV2.vue")
archive = read(ROOT / "src/components/v2/SeriesArchiveV2.vue")
band = read(ROOT / "src/components/v2/TidalBand.vue")
geometry = read(ROOT / "src/utils/tidalGeometry.ts")
styles = "\n".join(read(path) for path in (ROOT / "src/styles/v2").glob("*.css"))
package = data(ROOT / "package.json")

check("method_version", project["method_version"] == "revenue-tides-method-freeze-1.0.0")
check("findings_version", project["findings_version"] == "revenue-tides-findings-1.0.0")
check("webdata_version", project["webdata_version"] == "revenue-tides-webdata-1.0.0")
check("series_count", len(index) == manifest["series_count"] == 9)
check("observation_count", len(observations) == manifest["observation_count"] == 75)
check("event_count", len(events) == manifest["event_count"] == 26)
check("derived_count", len(derived) == 18)
check("finding_count", len(findings) == 6)
check("headline_set", {item["finding_id"] for item in findings if item["headline"]} == {"F1", "F2", "F4"})
check("frozen_data_unchanged", git_unchanged("data/web", "data/phase-e", "data/phase-f"))
check("frozen_research_unchanged", git_unchanged("research/phase-c", "research/phase-f"))
check("dependencies_unchanged", git_unchanged("package.json", "package-lock.json"))
check("no_chart_dependency", set(package["dependencies"]) == {"vue"})

check("hero_loads_real_details", "loadSeriesDetail" in hero and "props.series" in hero)
check("hero_normalizes_within_series", "Normalized within each series" in hero and "absolute revenue is not compared" in hero)
check("hero_ribbons", "hero-tide__area" in hero and "ribbonPath" in hero)
check("hero_nodes", "hero-tide__node" in hero)
check("hero_stagger", "--stagger" in hero and "hero-tide-arrive" in hero)
check("hero_parallax", "@pointermove" in hero and "--field-x" in hero)
check("measurement_five_states", all(token in measurement for token in ("direct", "entity", "version", "derived", "event")))
check("measurement_uncertainty_pattern", "measurement-uncertainty" in measurement)
check("measurement_event_separate", "measurement-event-tick" in measurement and "measurement-event-pulse" in measurement)

check("prism_liquid_band", "ribbonPath" in prism and "refraction-band" in prism)
check("prism_real_nodes", "refraction-nodes" in prism and "lane.points" in prism)
check("prism_aperture", "prism-aperture-clip" in prism and "refraction-window" in prism)
check("prism_overlap_local", ":clip-path=" in prism and "url(#prism-aperture-clip)" in prism)
check("prism_derived_pattern", "derived-pattern" in prism and "lower_bound" in prism)
check("prism_event_noncausal", "NON-CAUSAL" in prism and "同季度不等于因果" in prism)
check("prism_quarter_ruler", "prism-quarter-ruler" in prism)
check("prism_keyboard", "@keydown.left.prevent" in prism and "@keydown.right.prevent" in prism)

check("f1_dual_ribbon", "f1-flow-field" in findings_component and "f1Ribbon" in findings_component)
check("f2_surge", "f2-spike-stage" in findings_component and "+837.3%" in findings_component)
check("f2_event_separate", "PC RELEASE" in findings_component and "not causal" in findings_component)
check("f4_landscape", "f4-tidal-sequence" in findings_component and "30.8%" in findings_component)
check("archive_filled_fingerprints", "fingerprint-cell" in archive and "TidalBand" in archive)

check("smooth_is_presentational", "presentational geometry only" in geometry)
check("smooth_passes_anchors", "smoothPath" in geometry and "points[0]" in geometry and "points.at(-1)" in geometry)
check("band_volume", "ribbonPath" in geometry and "tidal-band__area" in band)
check("gradient_system", all(token in styles for token in ("--aqua", "--aqua-light", "--context-coral", "--uncertainty-lavender")))
check("local_glow", "filter:drop-shadow" in styles and "text-shadow" in styles)
check("reduced_motion", "prefers-reduced-motion: reduce" in styles and "animation:none" in styles)
check("mobile_390", "max-width: 640px" in styles and "mobile" in read(RESEARCH / "chrome_qa.json"))
check("non_color_version", "border-inline:3px double" in styles)
check("non_color_uncertainty", "repeating-linear-gradient" in styles)

required_desktop = ["desktop-hero", "desktop-measurement", "desktop-prism-direct", "desktop-prism-overlap", "desktop-f1", "desktop-f2", "desktop-f4", "desktop-observatory"]
required_mobile = ["mobile-390-hero", "mobile-390-prism", "mobile-390-f2", "mobile-390-f4", "mobile-390-observatory"]
check("desktop_screenshots", all((RESEARCH / "screenshots" / f"{name}.webp").is_file() for name in required_desktop))
check("mobile_screenshots", all((RESEARCH / "screenshots" / f"{name}.webp").is_file() for name in required_mobile))
check("before_after_sheet", (RESEARCH / "before-after-desktop.webp").is_file())
check("promotional_sheet", (RESEARCH / "promotional-screens.webp").is_file())

for browser, expected in (("chrome", 15), ("edge", 15), ("firefox", 13)):
    qa = data(RESEARCH / f"{browser}_qa.json")
    summary = qa["summary"]
    check(f"{browser}_qa", summary["failed"] == 0 and summary["passed"] >= expected, f"{summary['passed']}/{summary['passed'] + summary['failed']}")
chrome = data(RESEARCH / "chrome_qa.json")
check("six_viewports", len(chrome["viewports"]) == 6 and all(item["overflow"] == 0 for item in chrome["viewports"]))
check("console_clean", not chrome["console"]["errors"] and not chrome["console"]["warnings"] and not chrome["console"]["exceptions"])
check("network_clean", not chrome["network_errors"])

js_files = list((ROOT / "dist/assets").glob("*.js"))
css_files = list((ROOT / "dist/assets").glob("*.css"))
js_raw = sum(path.stat().st_size for path in js_files)
js_gzip = sum(len(gzip.compress(path.read_bytes(), compresslevel=9)) for path in js_files)
css_raw = sum(path.stat().st_size for path in css_files)
css_gzip = sum(len(gzip.compress(path.read_bytes(), compresslevel=9)) for path in css_files)
check("chapter_code_split", len(js_files) >= 7 and max(len(gzip.compress(path.read_bytes(), compresslevel=9)) for path in js_files) < 47_300)
check("bundle_documented", js_raw == 146_012 and css_raw == 62_530, f"JS {js_raw}; CSS {css_raw}")
check("no_large_asset", max(path.stat().st_size for path in (ROOT / "dist/assets").iterdir()) < 100_000)

required_reports = [
    "github_visual_research.md", "github_reference_implementation.md", "before_after.md",
    "performance_report.md", "beauty_gate.md", "BOLD_TIDAL_VISUAL_REBUILD.md",
]
check("required_reports", all((RESEARCH / name).is_file() for name in required_reports))
check("beauty_gate_pass", "10/10 PASS" in read(RESEARCH / "beauty_gate.md"))
check("stop_before_deployment", "STOPPED BEFORE DEPLOYMENT" in read(RESEARCH / "BOLD_TIDAL_VISUAL_REBUILD.md"))

summary = {
    "passed": sum(item["status"] == "PASS" for item in RESULTS),
    "failed": sum(item["status"] == "FAIL" for item in RESULTS),
    "js_raw_bytes": js_raw,
    "js_gzip_bytes": js_gzip,
    "css_raw_bytes": css_raw,
    "css_gzip_bytes": css_gzip,
}
(RESEARCH / "validation.json").write_text(json.dumps({"summary": summary, "checks": RESULTS}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
for index_number, result in enumerate(RESULTS, 1):
    detail = f" — {result['detail']}" if result["detail"] else ""
    print(f"{index_number:02d}. {result['status']} {result['name']}{detail}")
print(f"BOLD REBUILD VALIDATION: {summary['passed']}/{len(RESULTS)} PASS")
raise SystemExit(1 if summary["failed"] else 0)
