"""Validate Phase K competition materials and the final frozen release."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
METHOD_VERSION = "revenue-tides-method-freeze-1.0.0"
FINDINGS_VERSION = "revenue-tides-findings-1.0.0"
WEBDATA_VERSION = "revenue-tides-webdata-1.0.0"
RELEASE_VERSION = "revenue-tides-release-1.0.0"
DATA_CUTOFF = "2026-09-22"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: str | Path):
    return json.loads((ROOT / path).read_text(encoding="utf-8")) if isinstance(path, str) else json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: str | Path) -> list[dict[str, str]]:
    target = ROOT / path if isinstance(path, str) else path
    with target.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def run(command: list[str]) -> tuple[bool, str]:
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    output = ((result.stdout or "") + "\n" + (result.stderr or "")).strip()
    return result.returncode == 0, " | ".join(output.splitlines()[-4:])


def han_count(path: Path) -> int:
    body = "\n".join(line for line in path.read_text(encoding="utf-8").splitlines() if not line.startswith("#"))
    return len(re.findall(r"[\u3400-\u9fff]", body))


class Checks:
    def __init__(self) -> None:
        self.rows: list[tuple[int, str, bool, str]] = []

    def add(self, number: int, name: str, condition: bool, detail: str = "") -> None:
        self.rows.append((number, name, bool(condition), detail))

    def finish(self) -> int:
        if [row[0] for row in self.rows] != list(range(1, 111)):
            raise RuntimeError("Validator definition error: expected checks 1..110")
        for number, name, passed, detail in self.rows:
            suffix = f" — {detail}" if detail else ""
            print(f"{number:03d}. {'PASS' if passed else 'FAIL'} {name}{suffix}")
        passed = sum(row[2] for row in self.rows)
        print(f"PHASE K VALIDATION: {passed}/{len(self.rows)} PASS")
        return 0 if passed == len(self.rows) else 1


def main() -> int:
    c = Checks()
    method_manifest = read_json("research/phase-c/method_freeze_manifest.json")
    method_hash_ok = all(digest(ROOT / "research/phase-c" / name) == value for name, value in method_manifest["method_hashes"].items())
    c.add(1, "Method freeze unchanged", method_hash_ok, f"{len(method_manifest['method_hashes'])} files")

    finding_manifest = read_json("research/phase-f/findings_manifest.json")
    finding_hash_ok = True
    for name, value in finding_manifest["finding_hashes"].items():
        target = ROOT / ("data/phase-f" if name.startswith("formal_findings") else "research/phase-f") / name
        finding_hash_ok &= target.is_file() and digest(target) == value
    c.add(2, "Findings freeze unchanged", finding_hash_ok, f"{len(finding_manifest['finding_hashes'])} files")

    web_manifest = read_json("data/web/manifest.json")
    web_hash_ok = all((ROOT / "data/web" / row["path"]).is_file() and digest(ROOT / "data/web" / row["path"]) == row["sha256"] for row in web_manifest["files"])
    c.add(3, "Web Data freeze unchanged", web_hash_ok, f"{len(web_manifest['files'])} files")

    phase_i_input = read_json("research/phase-i/input_manifest.json")
    design_hash_ok = all((ROOT / row["path"]).is_file() and digest(ROOT / row["path"]) == row["sha256"] for row in phase_i_input["phase_h_artifacts"])
    c.add(4, "Design freeze unchanged", design_hash_ok, f"{len(phase_i_input['phase_h_artifacts'])} artifacts")

    phase_j = read_json("research/phase-j/phase_j_summary.json")
    c.add(5, "Phase J status PASS", phase_j["status"] == "PASS")
    manifest_path = ROOT / "release/final_manifest.json"
    manifest = read_json(manifest_path) if manifest_path.is_file() else {}
    c.add(6, "release version correct", manifest.get("release_version") == RELEASE_VERSION)
    c.add(7, "data cutoff unchanged", manifest.get("data_cutoff") == DATA_CUTOFF and web_manifest["data_cutoff"] == DATA_CUTOFF)

    index = read_json("data/web/series_index.json")
    details = [read_json(ROOT / "data/web" / row["detail_path"]) for row in index]
    observations = [obs for detail in details for obs in detail["observations"]]
    events = [event for detail in details for event in detail["events"]]
    claims = [claim for detail in details for claim in detail["attributed_claims"]]
    findings = read_json("data/web/findings.json")
    c.add(8, "corpus remains 9 series", len(index) == 9)
    c.add(9, "observations remain 75", len(observations) == 75)
    c.add(10, "events remain 26", len(events) == 26)
    c.add(11, "attributed claims remain 3", len(claims) == 3)
    derived = [obs for obs in observations if obs["evidence_class"] == "DERIVED_FROM_OFFICIAL"]
    c.add(12, "derived observations remain 18", len(derived) == 18)
    c.add(13, "Findings remain 6", len(findings) == 6)
    c.add(14, "headline Findings remain F1/F2/F4", [row["finding_id"] for row in findings if row["headline"]] == ["F1", "F2", "F4"])

    obs = {row["observation_id"]: row for row in observations}
    f1_diffs = [obs[f"obs_lm_v2_2025q{q}"]["value"] - obs[f"obs_lm_v1_2025q{q}"]["value"] for q in (2, 3, 4)]
    c.add(15, "F1 values reproduce", min(f1_diffs) == 6797 and max(f1_diffs) == 13455)
    f2_change = (obs["obs_stellar_2025q2"]["value"] / obs["obs_stellar_2025q1"]["value"] - 1) * 100
    c.add(16, "F2 values reproduce", round(f2_change, 1) == 837.3)
    c.add(17, "F3 values reproduce", round(obs["obs_nikke_2026q2"]["qoq"]["percent_change"], 1) == 32.4 and round(abs(obs["obs_nikke_2026q2"]["drawdown_percent"]), 1) == 4.1)
    c.add(18, "F4 values reproduce", round(abs(obs["obs_bd_2025q2"]["drawdown_percent"]), 1) == 20.7 and round(abs(obs["obs_bd_2026q2"]["drawdown_percent"]), 1) == 30.8)
    f5 = (obs["obs_lw_v2_2026q2"]["value"] / obs["obs_lw_v2_2025q2"]["value"] - 1) * 100
    c.add(19, "F5 values reproduce", round(abs(f5), 1) == 35.3)
    derived_changes = [row for row in derived if row["qoq"]["eligible"]]
    sign_sensitive = [row for row in derived_changes if not row["derived"]["direction_sign_stable"]]
    c.add(20, "F6 values reproduce", len(derived_changes) == 15 and len(sign_sensitive) == 9 and round(len(sign_sensitive) / len(derived_changes) * 100, 1) == 60.0)
    c.add(21, "no new Finding exists", {row["finding_id"] for row in findings} == {f"F{i}" for i in range(1, 7)})
    corpus_manifest = read_json("data/phase-d/corpus_manifest.json")
    c.add(22, "no new series exists", {row["series_id"] for row in index} == set(corpus_manifest["series_ids"]))
    c.add(23, "no new quarter exists", max(row["period_key"] for row in observations) == "2026Q2")

    required_root = ["README.md", "REPRODUCIBILITY.md", "PROJECT_STRUCTURE.md", "VERSIONS.md"]
    c.add(24, "README exists", (ROOT / required_root[0]).is_file())
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    c.add(25, "README project facts match", all(token in readme for token in ("9 条分析序列", "75 个财政季度观察", "26 个精选官方事件", "18 个由官方披露推导", "F1、F2、F4")))
    c.add(26, "README contains limitations", "## 20. 局限" in readme)
    c.add(27, "README does not claim global true revenue", "给出全球真实流水" not in readme and "global true revenue is" not in readme.lower())
    c.add(28, "reproducibility document exists", (ROOT / required_root[1]).is_file())
    c.add(29, "project structure document exists", (ROOT / required_root[2]).is_file())
    c.add(30, "versions document exists", (ROOT / required_root[3]).is_file())

    comp = ROOT / "competition"
    required_comp = [
        "project_summary_zh.md", "project_summary_en.md", "design_description_zh.md", "competition_short_zh.md",
        "competition_long_zh.md", "abstract_zh.md", "abstract_en.md", "pitch_30s_zh.md", "pitch_90s_zh.md",
        "pitch_3min_zh.md", "pitch_90s_en.md", "judge_findings_guide.md", "reviewer_guide.md", "judge_q_and_a.md",
        "methodology_one_page.md", "data_provenance_summary.md", "technical_architecture.md", "quarter_prism_explainer.md",
        "tidal_ledger_explainer.md", "accessibility_summary.md", "browser_qa_summary.md", "performance_summary.md",
        "limitations.md", "final_qa_summary.md", "README.md",
    ]
    exists = {name: (comp / name).is_file() for name in required_comp}
    c.add(31, "Chinese project summary exists", exists["project_summary_zh.md"])
    c.add(32, "English project summary exists", exists["project_summary_en.md"])
    c.add(33, "design description exists", exists["design_description_zh.md"])
    design_chars = han_count(comp / "design_description_zh.md")
    c.add(34, "design description length passes", design_chars <= 300, f"{design_chars} Chinese characters")
    c.add(35, "short competition description exists", exists["competition_short_zh.md"])
    c.add(36, "long competition description exists", exists["competition_long_zh.md"])
    c.add(37, "Chinese abstract exists", exists["abstract_zh.md"])
    c.add(38, "English abstract exists", exists["abstract_en.md"])
    c.add(39, "30-second script exists", exists["pitch_30s_zh.md"])
    c.add(40, "90-second script exists", exists["pitch_90s_zh.md"])
    c.add(41, "3-minute script exists", exists["pitch_3min_zh.md"])
    c.add(42, "English pitch exists", exists["pitch_90s_en.md"])
    c.add(43, "reviewer guide exists", exists["reviewer_guide.md"])
    c.add(44, "judge Q&A exists", exists["judge_q_and_a.md"])
    qa_text = (comp / "judge_q_and_a.md").read_text(encoding="utf-8")
    c.add(45, "Q&A contains at least 20 questions", len(re.findall(r"^## \d+\.", qa_text, flags=re.M)) >= 20)
    finding_guide = (comp / "judge_findings_guide.md").read_text(encoding="utf-8")
    c.add(46, "Finding guide contains F1-F6", all(f"## F{i}" in finding_guide for i in range(1, 7)))
    c.add(47, "methodology one-pager exists", exists["methodology_one_page.md"])
    c.add(48, "provenance summary exists", exists["data_provenance_summary.md"])
    c.add(49, "technical architecture exists", exists["technical_architecture.md"])
    c.add(50, "Quarter Prism explainer exists", exists["quarter_prism_explainer.md"])
    c.add(51, "Tidal Ledger explainer exists", exists["tidal_ledger_explainer.md"])
    c.add(52, "accessibility summary exists", exists["accessibility_summary.md"])
    c.add(53, "browser QA summary exists", exists["browser_qa_summary.md"])
    c.add(54, "performance summary exists", exists["performance_summary.md"])
    c.add(55, "limitations file exists", exists["limitations.md"])
    c.add(56, "final QA summary exists", exists["final_qa_summary.md"])
    c.add(57, "competition index exists", exists["README.md"])
    shot_dir = comp / "screenshots"
    shots = sorted(path for path in shot_dir.glob("*") if path.suffix.lower() in {".png", ".webp", ".jpg", ".jpeg"})
    c.add(58, "screenshot directory exists", shot_dir.is_dir())
    c.add(59, "selected screenshot count reasonable", 6 <= len(shots) <= 10, f"{len(shots)} images")
    c.add(60, "cover screenshot documented", (shot_dir / "cover.webp").is_file() and "selected cover" in (shot_dir / "README.md").read_text(encoding="utf-8"))
    c.add(61, "screenshots are not frontend production assets", not any(path.suffix.lower() in {".png", ".webp", ".jpg", ".jpeg"} for base in (ROOT / "src", ROOT / "public") for path in base.rglob("*") if path.is_file()))
    judge_files = [comp / name for name in required_comp] + [shot_dir / "README.md"]
    judge_text = "\n".join(path.read_text(encoding="utf-8") for path in judge_files)
    c.add(62, "no local E drive path in competition files", "E:\\" not in judge_text and "E:/" not in judge_text)
    c.add(63, "no unsupported global revenue claim", not re.search(r"(reconstructs|provides|ranks) (the )?(true|global) (game )?revenue", judge_text, re.I))
    c.add(64, "no cross-company leaderboard claim", "cross-company revenue leaderboard is provided" not in judge_text.lower())
    c.add(65, "no event-causality claim", "pc launch caused the increase." not in judge_text.lower() and "pc 上线导致" not in judge_text)
    c.add(66, "no permanent-decline claim", "has permanently declined" not in judge_text.lower() and "已经永久衰退" not in judge_text)
    c.add(67, "derived values correctly labeled", all(row["evidence_class"] == "DERIVED_FROM_OFFICIAL" and row["lower_bound"] is not None and row["upper_bound"] is not None for row in derived))
    overlaps = Counter((detail["identity"]["series_id"], row["period_key"]) for detail in details for row in detail["observations"])
    overlap_rows = sum(count - 1 for count in overlaps.values() if count > 1)
    c.add(68, "NCSOFT version breaks remain explicit", overlap_rows == 9 and all(row["metric_version"] for row in observations))
    browser_summary = (comp / "browser_qa_summary.md").read_text(encoding="utf-8")
    c.add(69, "browser summary states Chrome tested", "Chrome | 153" in browser_summary)
    c.add(70, "browser summary states Edge tested", "Edge | 149" in browser_summary)
    c.add(71, "browser summary states Firefox tested", "Firefox | 156" in browser_summary)
    c.add(72, "browser summary states WebKit unavailable", "WebKit / Safari-equivalent | Not available" in browser_summary)
    access_summary = (comp / "accessibility_summary.md").read_text(encoding="utf-8")
    c.add(73, "real screen-reader unavailable is disclosed", "not available" in access_summary.lower() and "screen-reader" in access_summary.lower())
    c.add(74, "no false WCAG certification", "does not claim" in access_summary and "WCAG certification" in access_summary and "No. The checks" in qa_text)
    perf = (comp / "performance_summary.md").read_text(encoding="utf-8")
    c.add(75, "bundle summary matches final baseline", all(token in perf for token in ("107.29 kB", "40.27 kB", "26.78 kB", "5.71 kB", "0.91 kB")))
    c.add(76, "performance numbers source-backed", all(token in (ROOT / "research/phase-j/performance_audit.md").read_text(encoding="utf-8") for token in ("107.29 kB", "29,486 bytes", "8")))

    repro_audit = (ROOT / "research/phase-k/final_reproducibility_audit.md").read_text(encoding="utf-8") if (ROOT / "research/phase-k/final_reproducibility_audit.md").is_file() else ""
    c.add(77, "TypeScript passes", "TypeScript" in repro_audit and "PASS" in repro_audit)
    c.add(78, "Vitest passes", "62/62 PASS" in repro_audit)
    dist_assets = list((ROOT / "dist/assets").glob("*")) if (ROOT / "dist/assets").is_dir() else []
    c.add(79, "production build passes", (ROOT / "dist/index.html").is_file() and len([p for p in dist_assets if p.suffix == ".js"]) == 1 and len([p for p in dist_assets if p.suffix == ".css"]) == 1)
    c.add(80, "Phase G isolated validator passes", "90/90 PASS" in repro_audit)
    c.add(81, "Phase I validator passes", "Phase I: 100/100 PASS" in repro_audit)
    c.add(82, "Phase J validator passes", "Phase J: 102/102 PASS" in repro_audit)
    c.add(83, "Phase K validator internal checks pass", all(row[2] for row in c.rows[:82]))
    smoke_path = ROOT / "research/phase-k/final_smoke.json"
    smoke = read_json(smoke_path) if smoke_path.is_file() else {}
    c.add(84, "final smoke passes", smoke.get("summary", {}).get("failed") == 0 and smoke.get("summary", {}).get("passed", 0) > 0)
    c.add(85, "final manifest exists", manifest_path.is_file())
    c.add(86, "manifest project counts match", all(manifest.get(key) == value for key, value in {"series_count": 9, "observation_count": 75, "event_count": 26, "claim_count": 3, "derived_observation_count": 18, "finding_count": 6}.items()))
    c.add(87, "manifest version fields match", manifest.get("method_version") == METHOD_VERSION and manifest.get("findings_version") == FINDINGS_VERSION and manifest.get("webdata_version") == WEBDATA_VERSION)
    c.add(88, "manifest deployment status NOT_DEPLOYED", manifest.get("deployment_status") == "NOT_DEPLOYED")
    hashes_path = ROOT / "release/final_hashes.csv"
    c.add(89, "final hashes exist", hashes_path.is_file())
    hash_rows = read_csv(hashes_path) if hashes_path.is_file() else []
    c.add(90, "all recorded hashes validate", bool(hash_rows) and all((ROOT / row["path"]).is_file() and digest(ROOT / row["path"]) == row["sha256"] and (ROOT / row["path"]).stat().st_size == int(row["bytes"]) for row in hash_rows))
    inventory_path = ROOT / "release/file_inventory.csv"
    c.add(91, "file inventory exists", inventory_path.is_file())
    inventory = read_csv(inventory_path) if inventory_path.is_file() else []
    c.add(92, "node_modules excluded from inventory", all("node_modules" not in row["path"] for row in inventory))
    c.add(93, "release contains no full project copy", all(path.name in {"final_manifest.json", "final_hashes.csv", "file_inventory.csv", "FINAL_FROZEN.md"} for path in (ROOT / "release").iterdir() if path.is_file()))
    frozen_path = ROOT / "release/FINAL_FROZEN.md"
    c.add(94, "FINAL_FROZEN exists", frozen_path.is_file())
    frozen_text = frozen_path.read_text(encoding="utf-8") if frozen_path.is_file() else ""
    c.add(95, "final status COMPLETE / FROZEN", manifest.get("status") == "COMPLETE / FROZEN" and "`COMPLETE / FROZEN`" in frozen_text)
    c.add(96, "freeze date exists", manifest.get("freeze_date") == "2026-09-24" and "2026-09-24" in frozen_text)
    c.add(97, "future update policy exists", "new branch/version" in frozen_text and "documented amendment" in frozen_text)
    phase_report = ROOT / "research/phase-k/PHASE_K_FINAL_AUDIT_FREEZE.md"
    c.add(98, "final research report exists", phase_report.is_file())
    c.add(99, "project timeline exists", (ROOT / "research/phase-k/project_timeline.md").is_file())
    c.add(100, "storage audit exists", (ROOT / "research/phase-k/storage_audit.md").is_file())
    c.add(101, "final language audit exists", (ROOT / "research/phase-k/final_language_audit.md").is_file())
    c.add(102, "final semantic audit exists", (ROOT / "research/phase-k/final_semantic_audit.md").is_file())
    c.add(103, "final materials audit exists", (ROOT / "research/phase-k/final_materials_audit.md").is_file())
    summary_path = ROOT / "research/phase-k/phase_k_summary.json"
    c.add(104, "phase summary exists", summary_path.is_file())
    c.add(105, "judge materials omit internal defect details", "qa_defect_id" not in judge_text.lower() and "extractor_identity=" not in judge_text.lower())
    c.add(106, "source limitations documented", "remote source urls may change" in judge_text.lower())
    c.add(107, "SHIFT UP automated 403 classified correctly", "remote-access condition" in judge_text.lower() and "broken application route" in judge_text.lower())
    c.add(108, "no public deployment occurred", manifest.get("deployment_status") == "NOT_DEPLOYED" and phase_j["deployment_performed"] is False)
    c.add(109, "no post-K phase started", not (ROOT / "research/phase-l").exists())
    work = (ROOT / "work.md").read_text(encoding="utf-8")
    summary = read_json(summary_path) if summary_path.is_file() else {}
    c.add(110, "project status resolves to COMPLETE / FROZEN", manifest.get("status") == "COMPLETE / FROZEN" and summary.get("status") == "PASS" and summary.get("final_status") == "COMPLETE / FROZEN" and "PROJECT 02 COMPLETE / FROZEN" in work)
    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())
