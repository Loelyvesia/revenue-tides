from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRISM = (ROOT / "src/components/v2/QuarterPrismV2.vue").read_text(encoding="utf-8")
CSS = (ROOT / "src/styles/v2/visualization.css").read_text(encoding="utf-8")
RESPONSIVE = (ROOT / "src/styles/v2/responsive.css").read_text(encoding="utf-8")
AUDIT = ROOT / "research/ui-2-1-prism"
checks: list[tuple[str, bool, str]] = []


def check(name: str, passed: bool, detail: str = "") -> None:
    checks.append((name, bool(passed), detail))


def qa(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


chrome = qa(AUDIT / "chrome_qa.json")
edge = qa(AUDIT / "edge_qa.json")
firefox = qa(AUDIT / "firefox_qa.json")

check("warm_outer_prism", ".quarter-prism" in CSS and "background:transparent" in CSS)
check("dark_surface_local_to_geometry", ".prism-geometry" in CSS and "background:var(--instrument-bg)" in CSS)
check("reading_output_is_light", ".prism-reading" in CSS and "background:var(--surface-bg)" in CSS)
check("tidal_band_geometry", "bandPath" in PRISM and "refraction-band" in PRISM)
check("no_curve_interpolation", "bandPath:" in PRISM and not re.search(r"bandPath:.*[CQ]", PRISM))
check("peak_caps", "refraction-peak-caps" in PRISM and "drawdown_percent === 0" in PRISM)
check("drawdown_notches", "refraction-drawdown-notches" in PRISM and "drawdown_percent < 0" in PRISM)
check("prism_aperture", "prism-aperture-clip" in PRISM and all(name in PRISM for name in ("refraction-window__rule--l", "refraction-window__rule--r")))
check("overlap_clipped_to_aperture", "lane.laneIndex > 0 ? 'url(#prism-aperture-clip)'" in PRISM)
check("overlap_semantics_preserved", "TWO REPORTING DEFINITIONS" in PRISM and "difference ≠ growth" in PRISM)
check("reading_output_fields", all(value in PRISM for value in ("READING OUTPUT", "valueNumber", "valueUnit", "evidence_class", "metric_version", "QoQ", "SOURCE ↗")))
check("bottom_quarter_ruler", "prism-quarter-ruler" in PRISM and "v-for=\"group in groups\"" in PRISM)
check("visible_quarter_select_removed", PRISM.count('id="prism-quarter"') == 1 and "legacy-contract-select" in PRISM)
check("detached_quarter_boxes_removed", "<ol class=\"prism-scroll-steps\"" not in PRISM)
check("keyboard_navigation_preserved", "@keydown.left.prevent" in PRISM and "@keydown.right.prevent" in PRISM)
check("mobile_ruler_visible", ".prism-quarter-ruler{display:grid" in RESPONSIVE)
check("derived_state_preserved", "refraction-interval" in PRISM and "DIRECTION UNRESOLVED" in PRISM)
check("event_context_preserved", "NON-CAUSAL" in PRISM and "同季度不等于因果" in PRISM)
check("chrome_qa", chrome.get("summary", {}).get("failed") == 0)
check("edge_qa", edge.get("summary", {}).get("failed") == 0)
check("firefox_qa", firefox.get("summary", {}).get("failed") == 0)
check("all_viewports_no_overflow", all(item.get("overflow") == 0 for item in chrome.get("viewports", [])))
check("console_clean", not any(chrome.get("console", {}).values()) and not chrome.get("network_errors"))
required_images = [
    AUDIT / "before_after" / side / name
    for side in ("before", "after")
    for name in ("quarter-prism-overlap.webp", "quarter-prism-direct.webp", "quarter-prism-mobile-390.webp")
]
check("before_after_complete", all(path.is_file() for path in required_images))
check("contact_sheet_exists", (AUDIT / "quarter-prism-before-after.webp").is_file())
check("no_dependency_change", subprocess.run(["git", "diff", "--quiet", "HEAD", "--", "package.json", "package-lock.json"], cwd=ROOT).returncode == 0)
check("frozen_research_unchanged", subprocess.run(["git", "diff", "--quiet", "HEAD", "--", "data/web", "research/phase-c", "research/phase-d", "research/phase-e", "research/phase-f"], cwd=ROOT).returncode == 0)

for index, (name, passed, detail) in enumerate(checks, 1):
    suffix = f" — {detail}" if detail else ""
    print(f"{index:02d}. {'PASS' if passed else 'FAIL'} {name}{suffix}")

passed = sum(item[1] for item in checks)
print(f"PRISM RECONSTRUCTION VALIDATION: {passed}/{len(checks)} PASS")
raise SystemExit(0 if passed == len(checks) else 1)
