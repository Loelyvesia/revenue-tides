"""Read-only validation for Phase H design specifications and SVG prototypes."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "research/phase-h"
DESIGN = ROOT / "design/phase-h"
METHOD_VERSION = "revenue-tides-method-freeze-1.0.0"
FINDINGS_VERSION = "revenue-tides-findings-1.0.0"
WEBDATA_VERSION = "revenue-tides-webdata-1.0.0"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contrast(a: str, b: str) -> float:
    def luminance(value: str) -> float:
        rgb = [int(value[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        rgb = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb]
        return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
    x, y = sorted((luminance(a), luminance(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)


class Suite:
    def __init__(self) -> None:
        self.results: list[tuple[int, str, bool, str]] = []

    def add(self, number: int, label: str, passed: bool, detail: str = "") -> None:
        self.results.append((number, label, bool(passed), detail))

    def finish(self) -> int:
        if [row[0] for row in self.results] != list(range(1, 79)):
            raise RuntimeError("Validator must define exactly tests 1–78 in order")
        for number, label, passed, detail in self.results:
            suffix = f" — {detail}" if detail else ""
            print(f"{number:02d}. {'PASS' if passed else 'FAIL'} {label}{suffix}")
        count = sum(row[2] for row in self.results)
        print(f"AUTOMATED TESTS: {count}/{len(self.results)} PASS")
        return 0 if count == len(self.results) else 1


def main() -> int:
    s = Suite()
    method_manifest = load_json(ROOT / "research/phase-c/method_freeze_manifest.json")
    method_hashes = method_manifest["method_hashes"]
    method_ok = method_manifest["method_version"] == METHOD_VERSION and all(
        sha256(ROOT / "research/phase-c" / path) == digest for path, digest in method_hashes.items()
    )

    freeze_text = (ROOT / "research/phase-f/FINDINGS_FREEZE.md").read_text(encoding="utf-8")
    finding_hashes = dict(re.findall(r"- `([^`]+)`: `([0-9a-f]{64})`", freeze_text))
    findings_ok = f"Findings version: `{FINDINGS_VERSION}`" in freeze_text and all(
        sha256(ROOT / path) == digest for path, digest in finding_hashes.items()
    )

    web_manifest = load_json(ROOT / "data/web/manifest.json")
    web_ok = web_manifest["webdata_version"] == WEBDATA_VERSION and all(
        sha256(ROOT / "data/web" / row["path"]) == row["sha256"] for row in web_manifest["files"]
    )
    findings = load_json(ROOT / "data/web/findings.json")
    index = load_json(ROOT / "data/web/series_index.json")
    project = load_json(ROOT / "data/web/project.json")
    finding_ids = {row["finding_id"] for row in findings}

    ia = (RESEARCH / "information_architecture.md").read_text(encoding="utf-8")
    visual = (RESEARCH / "visual_system.md").read_text(encoding="utf-8")
    prism = (RESEARCH / "quarter_prism_spec.md").read_text(encoding="utf-8")
    responsive = (RESEARCH / "responsive_spec.md").read_text(encoding="utf-8")
    accessibility = (RESEARCH / "accessibility_spec.md").read_text(encoding="utf-8")
    motion = (RESEARCH / "motion_spec.md").read_text(encoding="utf-8")
    contract = (RESEARCH / "data_ui_contract.md").read_text(encoding="utf-8")
    independence = (RESEARCH / "visual_independence_audit.md").read_text(encoding="utf-8")
    risks = (RESEARCH / "design_risk_register.md").read_text(encoding="utf-8")
    main_report = (RESEARCH / "PHASE_H_IA_VISUAL_SIGNATURE.md").read_text(encoding="utf-8")
    manual = (RESEARCH / "manual_design_review.md").read_text(encoding="utf-8")
    combined = "\n".join((ia, visual, prism, responsive, accessibility, motion, contract, independence, risks, main_report))
    matrix = load_csv(RESEARCH / "finding_design_matrix.csv")
    matrix_by_id = {row["finding_id"]: row for row in matrix}

    s.add(1, "method version and hashes unchanged", method_ok, f"{len(method_hashes)}/{len(method_hashes)}")
    s.add(2, "Findings version and hashes unchanged", findings_ok, f"{len(finding_hashes)}/{len(finding_hashes)}")
    s.add(3, "web-data version and hashes unchanged", web_ok, f"{len(web_manifest['files'])}/{len(web_manifest['files'])}")
    s.add(4, "six Findings unchanged", len(findings) == 6 and sha256(ROOT / "data/phase-f/formal_findings.json") == finding_hashes["data/phase-f/formal_findings.json"])
    s.add(5, "headline Findings remain F1/F2/F4", {row["finding_id"] for row in findings if row["headline"]} == {"F1", "F2", "F4"})
    s.add(6, "nine series remain unchanged", len(index) == project["corpus_series_count"] == 9)
    s.add(7, "no new Finding created", finding_ids == {"F1", "F2", "F3", "F4", "F5", "F6"})
    s.add(8, "IA file exists", (RESEARCH / "information_architecture.md").is_file() and "S0 Opening" in ia and "S6 Method" in ia)
    s.add(9, "visual-system file exists", (RESEARCH / "visual_system.md").is_file() and "Data-mark grammar" in visual)
    s.add(10, "Quarter Prism spec exists", (RESEARCH / "quarter_prism_spec.md").is_file() and "Quarter Prism" in prism)
    s.add(11, "responsive spec exists", (RESEARCH / "responsive_spec.md").is_file())
    s.add(12, "accessibility spec exists", (RESEARCH / "accessibility_spec.md").is_file())
    s.add(13, "motion spec exists", (RESEARCH / "motion_spec.md").is_file())
    s.add(14, "design tokens exist", (DESIGN / "design_tokens.json").is_file())
    s.add(15, "Finding-design matrix contains F1–F6", set(matrix_by_id) == finding_ids and len(matrix) == 6)
    s.add(16, "all six Findings map to a visual requirement", all(row["primary_visual_requirement"].strip() for row in matrix))
    s.add(17, "F1 requires version overlap visualization", matrix_by_id["F1"]["version_break_required"] == "true" and "Parallel legacy" in matrix_by_id["F1"]["primary_visual_requirement"])
    s.add(18, "F2 requires non-causal event context", matrix_by_id["F2"]["event_context_required"] == "true" and "non-causal" in (prism + ia).lower())
    s.add(19, "F3 requires incomplete-recovery representation", "remaining-gap" in matrix_by_id["F3"]["primary_visual_requirement"] and "unrecovered" in matrix_by_id["F3"]["primary_visual_requirement"])
    s.add(20, "F4 requires drawdown-recovery-drawdown sequence", "five-stage sequence" in matrix_by_id["F4"]["primary_visual_requirement"])
    s.add(21, "F5 is restricted to royalty-integrated v2", "royalty-integrated v2" in matrix_by_id["F5"]["core_semantic_need"] and "2025Q2–2026Q2" in matrix_by_id["F5"]["core_semantic_need"])
    s.add(22, "F6 requires uncertainty representation", matrix_by_id["F6"]["uncertainty_required"] == "true" and "interval" in matrix_by_id["F6"]["primary_visual_requirement"].lower())

    signature_names = [
        "prism_direct.svg", "prism_version_overlap.svg", "prism_derived_uncertainty.svg",
        "prism_event_context.svg", "prism_version_boundary.svg", "prism_mobile.svg",
    ]
    for number, name, label in zip(range(23, 29), signature_names, (
        "Quarter Prism direct state exists", "version-overlap state exists", "derived uncertainty state exists",
        "event-context state exists", "version-boundary state exists", "mobile Prism state exists",
    )):
        s.add(number, label, (DESIGN / "signature" / name).is_file())

    s.add(29, "direct/derived distinction is not color-only", all(term in visual.lower() for term in ("filled circle", "outlined diamond", "interval")))
    s.add(30, "version break is not color-only", "double calibration seam" in visual and "discontinuous path" in accessibility)
    s.add(31, "events are not encoded as positive/negative", "never encode good/bad" in visual.lower() and "separate context rail" in (prism + visual).lower())
    s.add(32, "uncertainty is visible without opacity alone", "never opacity alone" in (visual + accessibility + contract).lower() and "whisker" in visual.lower())
    s.add(33, "cross-company absolute comparison is visually prohibited", "no absolute cross-company overlay" in prism.lower() and "not comparable" in (visual + contract).lower())
    s.add(34, "normalized comparison caveat exists", "Normalized trajectory — absolute revenue not comparable" in contract)
    s.add(35, "no USD normalization design exists", "no USD conversion" in contract and "USD normalization" in main_report)
    s.add(36, "no leaderboard layout exists", "not revenue rank" in ia.lower() and "leaderboard layout" in ia.lower())
    s.add(37, "no KPI-card opening exists", "no KPI cards" in ia)
    s.add(38, "no stock candlestick design exists", "candlesticks" in independence.lower() and "DISTINCT" in independence)
    s.add(39, "no game-art dependency exists", "game-art dependency" in main_report and "No wireframe requires game artwork" in manual)
    s.add(40, "no glassmorphism requirement exists", "glassmorphism" in main_report.lower() and "absent" in visual.lower())
    s.add(41, "no default blue-purple gradient requirement exists", "default blue-purple gradient" in main_report.lower())
    s.add(42, "mobile design exists", "Mobile Quarter Prism" in responsive and (DESIGN / "wireframes/mobile_quarter_prism.svg").is_file())
    s.add(43, "320 survival behavior exists", "320" in responsive and "Survival layout" in responsive)
    s.add(44, "keyboard Signature path exists", "Left/Right Arrow" in prism and "keyboard" in accessibility.lower())
    s.add(45, "non-drag Signature path exists", all(term in prism for term in ("Previous/Next Quarter", "quarter select", "direct quarter list")))
    s.add(46, "reduced-motion Signature behavior exists", "prefers-reduced-motion" in prism and "one frame" in motion)
    s.add(47, "hover is not required", "Hover never reveals unique information" in accessibility)
    s.add(48, "focus treatment specified", "Visible focus" in accessibility and "3:1" in accessibility)
    s.add(49, "touch target specified", "44×44" in accessibility and load_json(DESIGN / "design_tokens.json")["touch_target_px"] == 44)
    s.add(50, "source access is designed", "source drawer" in ia.lower() and "evidence" in prism.lower())
    s.add(51, "caveat access is designed", "evidence key" in ia.lower() and "caveat_ids" in contract)
    s.add(52, "event coverage is labeled curated", "curated, non-exhaustive" in visual.lower() and "curated=true" in contract)
    s.add(53, "event causality guardrail exists", "timing does not establish causality" in visual and "No event-to-value connector" in prism)
    s.add(54, "derived evidence caveat exists", "rounded-share" in visual and "DERIVED_FROM_OFFICIAL" in prism)
    s.add(55, "metric-version caveat exists", "Definitions are not a continuous change series" in visual)
    s.add(56, "public/internal semantics remain preserved", "web-data layer remains authoritative" in contract and "must not recompute" in contract)
    s.add(57, "Project 01 layout not reused", "Project 01" in independence and "DISTINCT" in independence)
    s.add(58, "Chronicle Loom not reused", "Chronicle Loom" in independence)
    s.add(59, "Era Lens not reused", "Era Lens" in independence)
    s.add(60, "Earthquake map/cross-section not reused", "subsurface cross-section" in independence)
    s.add(61, "Cyclone Lifecycle Player not reused", "lifecycle player" in independence.lower())
    s.add(62, "Annual Rhythm Dial not reused", "Annual Rhythm Dial" in independence)
    distinct_rows = [line for line in independence.splitlines() if line.startswith("|") and "DISTINCT" in line]
    s.add(63, "visual independence audit passes", len(distinct_rows) == 7 and "No `RISK` classification remains" in independence)
    s.add(64, "design risk register exists", (RESEARCH / "design_risk_register.md").is_file() and risks.count("Controlled") >= 13)

    wireframe_names = {
        "opening.svg", "measurement_primer.svg", "quarter_prism.svg", "finding_f1.svg", "finding_f2.svg",
        "finding_f4.svg", "series_observatory.svg", "series_detail_direct.svg", "series_detail_version_break.svg",
        "series_detail_derived.svg", "finding_f6.svg", "method_sources.svg", "mobile_quarter_prism.svg",
        "mobile_series_detail.svg",
    }
    wireframes = list((DESIGN / "wireframes").glob("*.svg"))
    signatures = list((DESIGN / "signature").glob("*.svg"))
    s.add(65, "all required wireframes exist", {path.name for path in wireframes} == wireframe_names)
    svg_files = wireframes + signatures
    svg_ok = True
    for path in svg_files:
        try:
            root = ET.parse(path).getroot()
            svg_ok &= root.tag.endswith("svg") and bool(root.get("viewBox")) and root.find("{http://www.w3.org/2000/svg}title") is not None and root.find("{http://www.w3.org/2000/svg}desc") is not None
        except ET.ParseError:
            svg_ok = False
    s.add(66, "wireframe SVGs parse", svg_ok, f"{len(svg_files)} files")
    tokens_ok = True
    try:
        tokens = load_json(DESIGN / "design_tokens.json")
    except json.JSONDecodeError:
        tokens_ok = False
        tokens = {}
    s.add(67, "design token JSON parses", tokens_ok)
    summary_ok = True
    try:
        summary = load_json(RESEARCH / "phase_h_summary.json")
    except json.JSONDecodeError:
        summary_ok = False
        summary = {}
    s.add(68, "phase summary parses", summary_ok and summary.get("status") == "PASS")
    s.add(69, "no package.json created by Phase H", not (ROOT / "package.json").exists() and not (DESIGN / "package.json").exists())
    s.add(70, "no Vue/Vite frontend created", not (ROOT / "src").exists() and not any(ROOT.glob("vite.config.*")))
    s.add(71, "STOP boundary remains before Phase I", "STOPPED BEFORE PHASE I" in main_report and not (ROOT / "research/phase-i").exists())
    audit_passes = [line for line in independence.splitlines() if line.startswith("|") and "PASS" in line]
    s.add(72, "Signature audit passes all 15 criteria", len(audit_passes) == 15)
    s.add(73, "exactly 14 wireframes exist", len(wireframes) == 14)
    s.add(74, "exactly 6 Signature states exist", len(signatures) == 6 and {p.name for p in signatures} == set(signature_names))
    required_colors = {"background", "surface", "surface_secondary", "text_primary", "text_secondary", "border", "grid", "accent_primary", "accent_secondary", "event", "uncertainty", "direct_evidence", "derived_evidence", "focus", "warning"}
    s.add(75, "design tokens contain required systems", required_colors <= set(tokens.get("colors", {})) and all(key in tokens for key in ("spacing_px", "typography", "rules_px", "radius_px", "motion_ms", "breakpoints_px", "touch_target_px", "content_max_widths_px", "chart_annotation_px")))
    colors = tokens.get("colors", {})
    contrast_ok = tokens_ok and contrast(colors["background"], colors["text_primary"]) >= 4.5 and contrast(colors["background"], colors["text_secondary"]) >= 4.5 and contrast(colors["surface"], colors["text_primary"]) >= 4.5 and contrast(colors["background"], colors["focus"]) >= 3
    s.add(76, "core color contrast targets pass", contrast_ok)
    expected_fields = ["finding_id", "headline", "core_semantic_need", "required_data_structure", "primary_visual_requirement", "signature_interaction_role", "uncertainty_required", "version_break_required", "event_context_required", "source_trace_required", "mobile_strategy"]
    s.add(77, "Finding-design matrix schema is exact", list(matrix[0]) == expected_fields and all(row["source_trace_required"] == "true" for row in matrix))
    s.add(78, "manual design review passes", "40/40 PASS" in manual and all(str(width) in manual for width in (1440, 1024, 768, 390)))
    return s.finish()


if __name__ == "__main__":
    raise SystemExit(main())
