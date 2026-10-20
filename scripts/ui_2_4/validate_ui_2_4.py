from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research/ui-2-4/validation.json"
results: list[dict[str, object]] = []


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append({"name": name, "status": "PASS" if ok else "FAIL", "detail": detail})


def unchanged(*paths: str) -> bool:
    return subprocess.run(["git", "diff", "--quiet", "HEAD", "--", *paths], cwd=ROOT).returncode == 0


geometry = read("src/utils/tidalGeometry.ts")
band = read("src/components/v2/TidalBand.vue")
hero = read("src/components/v2/HeroV2.vue")
measurement = read("src/components/v2/MeasurementStory.vue")
prism = read("src/components/v2/QuarterPrismV2.vue")
findings_component = read("src/components/v2/HeadlineFindingsV2.vue")
archive = read("src/components/v2/SeriesArchiveV2.vue")
responsive = read("src/styles/v2/responsive.css")
package = json.loads(read("package.json"))
manifest = json.loads(read("data/web/manifest.json"))
index = json.loads(read("data/web/series_index.json"))
details = [json.loads(read(f"data/web/{record['detail_path']}")) for record in index]
observations = [item for detail in details for item in detail["observations"]]
events = [item for detail in details for item in detail["events"]]
findings = json.loads(read("data/web/findings.json"))

check("frozen_web_data_unchanged", unchanged("data/web"))
check("frozen_method_unchanged", unchanged("research/phase-c"))
check("frozen_findings_unchanged", unchanged("research/phase-f", "data/phase-f"))
check("frozen_web_product_audit_unchanged", unchanged("research/phase-g"))
check("frozen_counts", len(index) == 9 and len(observations) == 75 and len(events) == 26 and len(findings) == 6)
check("derived_count", sum(item["evidence_class"] == "DERIVED_FROM_OFFICIAL" for item in observations) == 18)
check("headline_findings", [item["finding_id"] for item in findings if item["headline"]] == ["F1", "F2", "F4"])
check("webdata_version", manifest["webdata_version"] == "revenue-tides-webdata-1.0.0")

check("floating_body_utility", "export function tidalBodyPath" in geometry and "baseDepth" in geometry and "slopeContribution" in geometry)
check("exact_upper_anchor_contract", "smoothPath(points, tension)" in geometry and "smoothPath(lower, tension)" in geometry)
check("floating_lower_contour", "const lower = points.map" in geometry and "y: point.y + depth" in geometry)
check("shared_body_adoption", all("tidalBodyPath" in text for text in [band, hero, prism, findings_component]))
check("vertical_body_dissolve", all(token in band + hero + prism for token in ["body-fade", "body-mask"]))
check("no_component_uses_flat_area", all("tidalAreaPath" not in text for text in [band, hero, prism, findings_component]))

check("hero_field_behind_title", "inset:2.5rem -4% -1rem -6%" in hero and "radial-gradient" in hero)
check("measurement_compressed", "height:min(47svh,31rem)" in measurement and "min-height:54vh" in measurement)
check("measurement_tide_enlarged", "height:94%" in measurement and "top:.4rem" in measurement)
check("prism_readout_unboxed", "background:transparent" in read("src/styles/v2/visualization.css") and "prism-reading::before" in read("src/styles/v2/visualization.css"))
check("prism_mobile_order", "order:1" in responsive and "order:2" in responsive and "order:3" in responsive)
check("mobile_overlap_two_column", "grid-template-columns:minmax(0,1fr) minmax(0,1fr)" in responsive and "display:block;min-width:0" in responsive)
check("mobile_overlap_chart_simplified", ".refraction-seam text{display:none}" in responsive and "overlap-refraction strong" in responsive)
check("mobile_overlap_source_after_chart", "prism-source-link--mobile-overlap" in prism and "prism-source-link--mobile-overlap{display:block;order:3" in responsive)

check("f1_title_reduced", "5.2vw" in findings_component and "5.25rem" in findings_component)
check("f1_currents_thickened", "baseDepth: 26 + ratio * 8" in findings_component and "height:13rem" in findings_component)
check("f2_title_reduced", "5.55vw" in findings_component and "54svh" in findings_component)
stellar = next(detail for detail in details if detail["series_id"] == "series_stellar_blade")
stellar_values = {item["quarter"]: item["value"] for item in stellar["observations"]}
check("f2_first_view_values", round(stellar_values["2025Q1"] / 1000, 3) == 7.012 and round(stellar_values["2025Q2"] / 1000, 3) == 65.719 and "+837.3%" in findings_component, "7.012 / 65.719 / +837.3%")
check("f2_percentage_deemphasized", 'class="f2-change"' in findings_component and 'class="f2-number"' not in findings_component)
check("f4_semantics_preserved", all(token in findings_component for token in ["20.7%", "三季度后恢复", "30.8%", "Black Desert"]))
check("archive_detail_enlarged", "height:14rem" in archive and "height:7.7rem" in archive)
check("archive_no_lateral_selection", ".ledger-row.is-active{transform:none}" in archive)
check("no_new_runtime_dependency", package.get("dependencies") == {"vue": "^3.5.42"})

required_desktop = ["desktop-hero", "desktop-measurement", "desktop-prism-direct", "desktop-prism-overlap", "desktop-f1", "desktop-f2", "desktop-f4", "desktop-observatory"]
required_mobile = ["mobile-390-hero", "mobile-390-prism", "mobile-390-overlap", "mobile-390-observatory"]
check("required_desktop_screenshots", all((ROOT / f"research/ui-2-4/screenshots/{name}.webp").is_file() for name in required_desktop))
check("required_mobile_screenshots", all((ROOT / f"research/ui-2-4/screenshots/{name}.webp").is_file() for name in required_mobile))

for browser, expected in [("chrome", 16), ("edge", 16), ("firefox", 13)]:
    path = ROOT / f"research/ui-2-4/{browser}_qa.json"
    payload = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    summary = payload.get("summary", {})
    check(f"{browser}_qa", summary.get("passed", 0) >= expected and summary.get("failed") == 0, str(summary))

required_docs = [
    "UI_2_4_FINAL_POLISH.md", "geometry_audit.md", "composition_audit.md",
    "mobile_overlap_audit.md", "first_view_audit.md", "before_after.md",
]
check("required_audits", all((ROOT / "research/ui-2-4" / name).is_file() for name in required_docs))
check("stop_before_deployment", (ROOT / "research/ui-2-4/UI_2_4_FINAL_POLISH.md").is_file() and "STOPPED BEFORE DEPLOYMENT" in read("research/ui-2-4/UI_2_4_FINAL_POLISH.md"))

passed = sum(item["status"] == "PASS" for item in results)
payload = {"suite": "UI 2.4", "passed": passed, "total": len(results), "results": results}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
for number, item in enumerate(results, 1):
    suffix = f" — {item['detail']}" if item["detail"] else ""
    print(f"{number:02d}. {item['status']} {item['name']}{suffix}")
print(f"UI 2.4 VALIDATION: {passed}/{len(results)} PASS")
raise SystemExit(0 if passed == len(results) else 1)
