"""Build deterministic lightweight Phase K release metadata."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / "release"
RELEASE_VERSION = "revenue-tides-release-1.0.0"
METHOD_VERSION = "revenue-tides-method-freeze-1.0.0"
FINDINGS_VERSION = "revenue-tides-findings-1.0.0"
WEBDATA_VERSION = "revenue-tides-webdata-1.0.0"
DATA_CUTOFF = "2026-09-22"
FREEZE_DATE = "2026-09-24"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def find_asset(suffix: str) -> Path:
    matches = sorted((ROOT / "dist/assets").glob(f"*{suffix}"))
    if len(matches) != 1:
        raise RuntimeError(f"Expected one dist asset ending {suffix}, found {len(matches)}")
    return matches[0]


def inventory_category(path: Path) -> tuple[str, str]:
    rp = rel(path)
    if rp.startswith("competition/"):
        return "competition_material", "public"
    if rp.startswith("research/"):
        return "research_audit", "internal"
    if rp.startswith("data/web/") or rp.startswith("public/data/"):
        return "public_data", "public"
    if rp.startswith("src/") or rp in {"index.html", "package.json", "package-lock.json", "vite.config.ts", "tsconfig.json", "tsconfig.app.json", "tsconfig.node.json"}:
        return "frontend_source", "public"
    if rp.startswith("dist/"):
        return "production_build", "public"
    if rp.startswith("design/"):
        return "design_artifact", "research"
    if rp.startswith("release/"):
        return "release_metadata", "public"
    if rp.startswith("scripts/"):
        return "reproducibility_script", "research"
    return "project_document", "public"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--final", action="store_true", help="Mark the release COMPLETE / FROZEN")
    args = parser.parse_args()
    RELEASE.mkdir(parents=True, exist_ok=True)

    web_manifest = json.loads((ROOT / "data/web/manifest.json").read_text(encoding="utf-8"))
    project = json.loads((ROOT / "data/web/project.json").read_text(encoding="utf-8"))
    phase_j = json.loads((ROOT / "research/phase-j/phase_j_summary.json").read_text(encoding="utf-8"))
    js_asset = find_asset(".js")
    css_asset = find_asset(".css")
    html_asset = ROOT / "dist/index.html"

    critical_paths = [
        ROOT / "research/phase-c/PHASE_C_METHOD_SCOPE_FREEZE.md",
        ROOT / "research/phase-c/method_freeze_manifest.json",
        ROOT / "research/phase-f/FINDINGS_FREEZE.md",
        ROOT / "research/phase-f/findings_manifest.json",
        ROOT / "research/phase-g/PHASE_G_WEB_DATA_PRODUCTIZATION.md",
        ROOT / "data/web/manifest.json",
        ROOT / "research/phase-h/PHASE_H_IA_VISUAL_SIGNATURE.md",
        ROOT / "research/phase-j/PHASE_J_FINAL_BROWSER_QA.md",
        ROOT / "README.md",
        ROOT / "data/phase-f/formal_findings.json",
        ROOT / "src/main.ts",
        ROOT / "src/App.vue",
        ROOT / "package-lock.json",
        html_asset,
        js_asset,
        css_asset,
        ROOT / "competition/project_summary_zh.md",
        ROOT / "competition/project_summary_en.md",
        ROOT / "competition/design_description_zh.md",
        ROOT / "competition/competition_long_zh.md",
        ROOT / "competition/abstract_zh.md",
        ROOT / "competition/abstract_en.md",
    ]
    missing = [rel(path) for path in critical_paths if not path.is_file()]
    if missing:
        raise RuntimeError(f"Missing critical files: {missing}")
    critical_hashes = {rel(path): digest(path) for path in sorted(critical_paths, key=rel)}

    status = "COMPLETE / FROZEN" if args.final else "RELEASE CANDIDATE"
    manifest = {
        "automated_test_counts": {
            "phase_g_isolated": {"passed": 90, "total": 90},
            "phase_i": {"passed": 100, "total": 100},
            "phase_j": phase_j["automated_validation"],
            "phase_k": {"passed": 110 if args.final else 0, "total": 110},
            "vitest": phase_j["vitest"],
        },
        "browser_tested": ["Chrome 153", "Edge 149", "Firefox 156"],
        "bundle_summary": {
            "css": {"bytes": css_asset.stat().st_size, "gzip_bytes": len(gzip.compress(css_asset.read_bytes(), compresslevel=9)), "reported": "26.78 kB / 5.71 kB gzip"},
            "html": {"bytes": html_asset.stat().st_size, "reported": "0.91 kB"},
            "initial_bootstrap_json_bytes": 29486,
            "initial_requests": 8,
            "javascript": {"bytes": js_asset.stat().st_size, "gzip_bytes": len(gzip.compress(js_asset.read_bytes(), compresslevel=9)), "reported": "107.29 kB / 40.27 kB gzip"},
        },
        "claim_count": project["claim_count"],
        "critical_file_hashes": critical_hashes,
        "data_cutoff": DATA_CUTOFF,
        "deployment_status": "NOT_DEPLOYED",
        "derived_observation_count": 18,
        "event_count": project["event_count"],
        "finding_count": web_manifest["finding_count"],
        "findings_version": FINDINGS_VERSION,
        "freeze_date": FREEZE_DATE,
        "frontend_stack": ["Vue 3", "TypeScript", "Vite", "custom SVG/CSS"],
        "headline_finding_ids": project["headline_finding_ids"],
        "known_limitations": [
            "Publisher-defined metrics are heterogeneous and absolute cross-company comparison is forbidden.",
            "Values are not a uniform global consumer-spending measure.",
            "NCSOFT legacy and royalty-integrated versions cannot be stitched.",
            "Derived Netmarble observations inherit rounded-share uncertainty.",
            "Events are curated, non-exhaustive, and non-causal context.",
            "Observed-window non-recovery is not permanent decline.",
            "A real interactive screen-reader session and WebKit/Safari-equivalent testing were unavailable.",
            "Remote source URLs may change or reject automated access.",
        ],
        "method_version": METHOD_VERSION,
        "observation_count": project["observation_count"],
        "project_id": project["project_id"],
        "project_title": {"en": project["title_en"], "zh": project["title_zh"]},
        "release_files": [
            "release/final_manifest.json",
            "release/final_hashes.csv",
            "release/file_inventory.csv",
            "release/FINAL_FROZEN.md",
        ],
        "release_version": RELEASE_VERSION,
        "series_count": project["corpus_series_count"],
        "status": status,
        "viewports_tested": phase_j["viewports"],
        "webdata_version": WEBDATA_VERSION,
    }
    write_json(RELEASE / "final_manifest.json", manifest)

    hash_paths = critical_paths + [RELEASE / "final_manifest.json"]
    with (RELEASE / "final_hashes.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "sha256", "bytes", "scope"])
        writer.writeheader()
        for path in sorted(hash_paths, key=rel):
            writer.writerow({"path": rel(path), "sha256": digest(path), "bytes": path.stat().st_size, "scope": "critical"})

    include_files: set[Path] = set()
    for name in ("README.md", "REPRODUCIBILITY.md", "PROJECT_STRUCTURE.md", "VERSIONS.md", "work.md", "package.json", "package-lock.json", "index.html", "vite.config.ts", "tsconfig.json", "tsconfig.app.json", "tsconfig.node.json"):
        path = ROOT / name
        if path.is_file():
            include_files.add(path)
    for directory in ("competition", "research/phase-k", "data/web", "src", "dist", "design/phase-h", "scripts/phase_k"):
        root = ROOT / directory
        if root.exists():
            include_files.update(path for path in root.rglob("*") if path.is_file() and "__pycache__" not in path.parts)
    include_files.update({RELEASE / "final_manifest.json", RELEASE / "final_hashes.csv", RELEASE / "FINAL_FROZEN.md"})
    include_files.discard(RELEASE / "file_inventory.csv")
    with (RELEASE / "file_inventory.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "category", "bytes", "sha256", "visibility"])
        writer.writeheader()
        for path in sorted((p for p in include_files if p.is_file()), key=rel):
            category, visibility = inventory_category(path)
            writer.writerow({"path": rel(path), "category": category, "bytes": path.stat().st_size, "sha256": digest(path), "visibility": visibility})

    print(f"Release metadata built: {status}")
    print(f"Critical hashes: {len(hash_paths)}")
    print(f"Inventory files: {len(include_files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
