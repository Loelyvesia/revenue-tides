from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
results: list[tuple[str, bool, str]] = []


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, bool(ok), detail))


def unchanged(*paths: str) -> bool:
    return subprocess.run(["git", "diff", "--quiet", "HEAD", "--", *paths], cwd=ROOT).returncode == 0


manifest = json.loads(read("data/web/manifest.json"))
findings = json.loads(read("data/web/findings.json"))
index = json.loads(read("data/web/series_index.json"))
details = [json.loads(read(f"data/web/{item['detail_path']}")) for item in index]
observations = [item for detail in details for item in detail["observations"]]
events = [item for detail in details for item in detail["events"]]
geometry = read("src/utils/tidalGeometry.ts")
band = read("src/components/v2/TidalBand.vue")
prism = read("src/components/v2/QuarterPrismV2.vue")
findings_component = read("src/components/v2/HeadlineFindingsV2.vue")
archive = read("src/components/v2/SeriesArchiveV2.vue")
styles = read("src/styles/v2/visualization.css")
responsive = read("src/styles/v2/responsive.css")

check("frozen_web_data_unchanged", unchanged("data/web"))
check("frozen_findings_unchanged", unchanged("research/phase-f", "data/phase-f"))
check("frozen_method_unchanged", unchanged("research/phase-c"))
check("series_count", len(index) == 9)
check("observation_count", len(observations) == 75)
check("event_count", len(events) == 26)
check("derived_count", sum(item["evidence_class"] == "DERIVED_FROM_OFFICIAL" for item in observations) == 18)
check("finding_count", len(findings) == 6)
check("headline_set", [item["finding_id"] for item in findings if item["headline"]] == ["F1", "F2", "F4"])
check("surface_geometry_exists", all(token in geometry for token in ["tidalAreaPath", "tidalEnvelopePath", "tidalSplitPaths", "tidalFadeMask"]))
check("tidal_band_not_fixed_ribbon", "ribbonPath" not in band and ("tidalAreaPath" in band or "tidalBodyPath" in band))
check("tidal_band_no_default_axis", all(token not in band for token in ["tidal-band__baseline", "tidal-band__ticks", "tidal-band__nodes"]))
check("tidal_band_critical_markers_only", "tidal-band__peaks" in band and "tidal-band__derived" in band)
check("prism_soft_mask", "prism-refraction-mask" in prism and "prism-field-mask-gradient" in prism)
check("prism_no_hard_frame", all(token not in prism for token in ["refraction-window__rule", "refraction-baseline", "refraction-quarter-ticks"]))
check("prism_overlap_state", "同一季度" in prism and "两种报告口径" in prism and "非收入拆分" in prism)
check("prism_no_connector_line", "overlap-refraction\"><span>旧口径</span><i" not in prism)
check("version_disturbance_zone", "refraction-seam" in prism and "<rect :x=\"seamX - 24\"" in prism)
check("f1_no_giant_frame", ".f1-dual-reading .f1-stage" in styles and "border-radius" not in styles[styles.find(".f1-dual-reading .f1-stage"):styles.find(".f1-primary__series")])
check("f1_current_split", "f1-primary__ribbons" in findings_component and "f1-mini-current" in findings_component)
check("f2_semantics_unchanged", all(token in findings_component + read("src/content/displayCopy.zh.ts") for token in ["+837.3%", "PC 版上线", "八季度最高"]))
check("f2_construction_removed", all(token not in findings_component for token in ["spike-baseline", "spike-event-tick", "spike-nodes"]))
check("f4_semantics_unchanged", all(token in findings_component for token in ["20.7%", "三季度后恢复", "30.8%"]))
check("f4_axis_removed", all(token not in findings_component for token in ["f4-baseline", "f4-quarter-ticks"]))
check("event_context_noncausal", "同季度不等于因果" in prism and "不能把这次增长直接归因于 PC 版" in read("src/content/displayCopy.zh.ts"))
check("archive_fingerprints", "TidalBand" in archive and "fingerprint-cell" in archive)
check("archive_no_row_mark", "ledger-row__mark" not in archive and "border:0" in styles[styles.find(".ledger-row{"):styles.find(".ledger-row::before")])
canonical_selectors = [".prism-geometry", ".f1-heading h2", ".f2-number", ".f4-heading", ".archive-detail"]
check("canonical_selector_definitions", all(len(re.findall(r"(?:^|\})" + re.escape(selector) + r"\{", styles)) == 1 for selector in canonical_selectors))
check("mobile_continuous_prism", "prism-composition" in responsive and ("position:absolute" in responsive or "flex-direction:column" in responsive))

desktop = ["desktop-hero", "desktop-measurement", "desktop-prism-direct", "desktop-prism-overlap", "desktop-f1", "desktop-f2", "desktop-f4", "desktop-observatory"]
mobile = ["mobile-390-hero", "mobile-390-prism", "mobile-390-overlap", "mobile-390-f2", "mobile-390-f4", "mobile-390-observatory"]
check("desktop_screenshots", all((ROOT / f"research/ui-2-3/screenshots/{name}.webp").is_file() for name in desktop))
check("mobile_screenshots", all((ROOT / f"research/ui-2-3/screenshots/{name}.webp").is_file() for name in mobile))

for browser, expected in [("chrome", 15), ("edge", 15), ("firefox", 13)]:
    path = ROOT / f"research/ui-2-3/{browser}_qa.json"
    payload = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    summary = payload.get("summary", {})
    check(f"{browser}_qa", summary.get("passed") == expected and summary.get("failed") == 0, str(summary))

required = [
    "UI_2_3_FLOW_CONTINUITY.md", "line_audit.md", "flow_audit.md", "before_after.md",
    "prism_refraction_audit.md", "tidal_geometry_audit.md", "mobile_audit.md",
    "accessibility_regression.md", "performance_regression.md",
]
check("required_audits", all((ROOT / "research/ui-2-3" / name).is_file() for name in required))
check("stop_before_deployment", (ROOT / "research/ui-2-3/UI_2_3_FLOW_CONTINUITY.md").is_file() and "STOPPED BEFORE DEPLOYMENT" in read("research/ui-2-3/UI_2_3_FLOW_CONTINUITY.md"))

for number, (name, ok, detail) in enumerate(results, 1):
    print(f"{number:02d}. {'PASS' if ok else 'FAIL'} {name}" + (f" — {detail}" if detail else ""))
passed = sum(ok for _, ok, _ in results)
print(f"UI 2.3 VALIDATION: {passed}/{len(results)} PASS")
raise SystemExit(0 if passed == len(results) else 1)
