from __future__ import annotations

import gzip
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS: list[tuple[str, bool, str]] = []


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def check(name: str, condition: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(condition), detail))


def baseline_bytes(path: str) -> bytes:
    run = subprocess.run(
        ["git", "show", f"ui-rebuild-2.0:{path}"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    return run.stdout


def sha(data: bytes) -> str:
    # Git stores LF while the Windows worktree may materialize CRLF.
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


hero = text("src/components/v2/HeroV2.vue")
band = text("src/components/v2/TidalBand.vue")
prism = text("src/components/v2/QuarterPrismV2.vue")
findings = text("src/components/v2/HeadlineFindingsV2.vue")
archive = text("src/components/v2/SeriesArchiveV2.vue")
responsive = text("src/styles/v2/responsive.css")
visual = text("src/styles/v2/visualization.css")
package = json.loads(text("package.json"))
manifest = json.loads(text("data/web/manifest.json"))

check("branch_is_ui_signature_2_1", subprocess.run(["git", "branch", "--show-current"], cwd=ROOT, capture_output=True, text=True).stdout.strip() == "ui-signature-2.1")
check("release_candidate_version", package["version"] == "2.1.0")
check("hero_v2_exists", "hero-signature" in hero and "付费潮汐" in hero)
check("real_data_drives_hero", "loadSeriesDetail" in hero and "detail" in hero and "TidalBand" in hero)
check("tidal_band_exists", "tidal-band__baseline" in band and "tidal-band__path" in band and "tidal-band__ticks" in band)
check("tidal_band_peak_cap", "tidal-band__peaks" in band and "drawdown_percent === 0" in band)
check("tidal_band_version_seam", "tidal-band__seams" in band and "metric_versions" in band)
check("tidal_band_derived_interval", "tidal-band__derived" in band and "lower_bound" in band)
check("hero_comparability_notice", "absolute revenue is not compared" in hero and "不同公司绝对收入不可比较" in hero)
check("quarter_prism_refraction", "refraction-field" in prism and "refraction-window__rule--l2" in prism and "refraction-window__rule--r2" in prism)
check("lineage_overlap_split", "overlap-refraction" in prism and "TWO REPORTING DEFINITIONS" in prism and "ROYALTY-INTEGRATED" in prism)
check("derived_interval_state", "refraction-interval" in prism and "refraction-diamond" in prism and "DIRECTION UNRESOLVED" in prism)
check("event_rail_separate", "event-prism-rail" in prism and "NON-CAUSAL" in prism and "同季度不等于因果" in prism)
check("f1_split_layout", "f1-dual-reading" in findings and "f1-definition--legacy" in findings and "f1-definition--royalty" in findings)
check("f2_spike_layout", "f2-spike-stage" in findings and "+837.3%" in findings and "spike-event-tick" in findings)
check("f4_tidal_layout", "f4-tidal-sequence" in findings and "f4-band-core" in findings and "DRAW DOWN 30.8%" in findings)
check("observatory_fingerprint", "fingerprint-row" in archive and "TidalBand" in archive and "NORMALIZED SHAPE" in archive)
check("mobile_signature_layouts", all(token in responsive for token in [".prism-composition", ".f1-dual-reading", ".f2-spike-stage", ".fingerprint-row"]))
check("no_new_runtime_dependency", set(package["dependencies"]) == {"vue"})
check("corpus_counts_unchanged", (manifest["series_count"], manifest["observation_count"], manifest["event_count"], manifest["finding_count"]) == (9, 75, 26, 6))

frozen_paths = ["research/phase-c/method_freeze_manifest.json", "research/phase-f/findings_manifest.json", "data/web/findings.json", "data/web/manifest.json"]
for path in frozen_paths:
    current = (ROOT / path).read_bytes()
    baseline = baseline_bytes(path)
    check(f"frozen_hash_{Path(path).stem}", sha(current) == sha(baseline), sha(current))

web_diff = subprocess.run(["git", "diff", "--quiet", "ui-rebuild-2.0", "--", "data/web"], cwd=ROOT).returncode
research_diff = subprocess.run(["git", "diff", "--quiet", "ui-rebuild-2.0", "--", "research/phase-c", "research/phase-f", "data/phase-e", "data/phase-f"], cwd=ROOT).returncode
check("web_data_unchanged", web_diff == 0)
check("research_data_unchanged", research_diff == 0)

js_files = sorted((ROOT / "dist/assets").glob("*.js"))
css_files = sorted((ROOT / "dist/assets").glob("*.css"))
js_gzip = len(gzip.compress(js_files[-1].read_bytes(), compresslevel=9)) if js_files else 0
css_gzip = len(gzip.compress(css_files[-1].read_bytes(), compresslevel=9)) if css_files else 0
check("js_gzip_within_ui2_limit", js_gzip <= 47_300, f"{js_gzip} bytes")
check("build_assets_present", bool(js_files and css_files), f"JS {js_gzip}; CSS {css_gzip}")

for index, (name, passed, detail) in enumerate(RESULTS, 1):
    suffix = f" — {detail}" if detail else ""
    print(f"{index:02d}. {'PASS' if passed else 'FAIL'} {name}{suffix}")

passed = sum(item[1] for item in RESULTS)
print(f"UI 2.1 VALIDATION: {passed}/{len(RESULTS)} PASS")
raise SystemExit(0 if passed == len(RESULTS) else 1)
