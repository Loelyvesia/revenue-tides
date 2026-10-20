from __future__ import annotations

import csv
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
results: list[tuple[str, bool, str]] = []

def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, bool(ok), detail))

def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")

def unchanged(*paths: str) -> bool:
    return subprocess.run(["git", "diff", "--quiet", "HEAD", "--", *paths], cwd=ROOT).returncode == 0

manifest = json.loads(read("data/web/manifest.json"))
findings = json.loads(read("data/web/findings.json"))
index = json.loads(read("data/web/series_index.json"))
details = [json.loads(read(f"data/web/{item['detail_path']}")) for item in index]
observations = [item for detail in details for item in detail["observations"]]
events = [item for detail in details for item in detail["events"]]
primary = "\n".join(read(str(path.relative_to(ROOT)).replace("\\", "/")) for path in (ROOT / "src/components/v2").glob("*.vue"))
copy = read("src/content/displayCopy.zh.ts")

check("frozen_web_data_unchanged", unchanged("data/web"))
check("frozen_findings_unchanged", unchanged("research/phase-f", "data/phase-f"))
check("frozen_method_unchanged", unchanged("research/phase-c"))
check("display_copy_layer_exists", (ROOT / "src/content/displayCopy.zh.ts").is_file())
check("series_count", len(index) == 9)
check("observation_count", len(observations) == 75)
check("event_count", len(events) == 26)
check("derived_count", sum(item["evidence_class"] == "DERIVED_FROM_OFFICIAL" for item in observations) == 18)
check("finding_count", len(findings) == 6)
check("headline_set", [item["finding_id"] for item in findings if item["headline"]] == ["F1", "F2", "F4"])
check("no_forbidden_interpretation_label", "禁止解读" not in primary)
check("no_frozen_pipeline_copy", "冻结研究流水线" not in primary)
check("natural_navigation", all(label in copy for label in ["口径", "季度棱镜", "主要发现", "全部序列", "方法与来源"]))
check("four_measurement_steps", copy.count("label: '0") == 4)
check("f1_numbers", all(token in read("src/components/v2/HeadlineFindingsV2.vue") for token in ["f1Gap", "121.111", "127.908"]) or all(token in read("data/web/findings.json") for token in ["6.797", "13.455"]))
check("f2_numbers", all(token in primary + copy for token in ["obs_stellar_2025q1", "obs_stellar_2025q2", "70.12", "657.19", "837.3%"] ))
check("f4_numbers", all(token in primary + copy for token in ["69.2", "54.9", "79.5", "55.0", "20.7%", "30.8%"] ))
inventory_path = ROOT / "research/ui-2-2/copy_inventory.csv"
with inventory_path.open(encoding="utf-8-sig", newline="") as handle:
    inventory = list(csv.DictReader(handle))
check("copy_inventory_complete", len(inventory) >= 450 and all(set(["location","component","old_copy","type","problem","rewrite_needed","new_copy"]) <= set(row) for row in inventory))
check("rewrite_decisions_complete", all(row["rewrite_needed"] != "YES" or row["new_copy"] for row in inventory))
check("decorative_bilingual_titles_reduced", len(re.findall(r"[A-Za-z ]+\s*/\s*[\u4e00-\u9fff]", primary)) <= 1)
all_caps = re.findall(r">\s*([A-Z][A-Z0-9 _-]{3,})\s*<", primary)
check("visible_all_caps_reduced", len(all_caps) <= 8, str(all_caps))
check("monospace_metadata_reduced", "font-sans" in read("src/styles/v2/visualization.css") and "font-sans" in read("src/styles/v2/layout.css"))
check("mobile_screenshots", all((ROOT / f"research/ui-2-2/screenshots/{name}.webp").is_file() for name in ["mobile-390-hero","mobile-390-measurement","mobile-390-prism","mobile-390-f1","mobile-390-f2","mobile-390-f4","mobile-390-observatory"]))
check("desktop_screenshots", all((ROOT / f"research/ui-2-2/screenshots/{name}.webp").is_file() for name in ["desktop-hero","desktop-measurement","desktop-prism-direct","desktop-prism-overlap","desktop-f1","desktop-f2","desktop-f4","desktop-observatory","desktop-notes","desktop-method"]))
required = ["UI_2_2_EDITORIAL_VISUAL_REFINEMENT.md","copy_audit.md","visual_audit.md","mobile_audit.md","before_after.md","accessibility_regression.md","performance_regression.md"]
check("required_audits", all((ROOT / "research/ui-2-2" / name).is_file() for name in required))
check("browser_qa", all((ROOT / f"research/ui-2-2/{name}_qa.json").is_file() for name in ["chrome","edge","firefox"]))
check("stop_before_deployment", "STOPPED BEFORE DEPLOYMENT" in read("research/ui-2-2/UI_2_2_EDITORIAL_VISUAL_REFINEMENT.md"))

for i, (name, ok, detail) in enumerate(results, 1):
    print(f"{i:02d}. {'PASS' if ok else 'FAIL'} {name}" + (f" — {detail}" if detail else ""))
passed = sum(ok for _, ok, _ in results)
print(f"UI 2.2 VALIDATION: {passed}/{len(results)} PASS")
raise SystemExit(0 if passed == len(results) else 1)
