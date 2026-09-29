from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
TOKENS = SRC / "styles" / "v2" / "tokens.css"
VIS = SRC / "styles" / "v2" / "visualization.css"
REPORT = ROOT / "research" / "ui-2-1-color"


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def hex_rgb(value: str) -> tuple[float, float, float]:
    value = value.removeprefix("#")
    return tuple(int(value[index:index + 2], 16) / 255 for index in (0, 2, 4))


def luminance(value: str) -> float:
    channels = []
    for channel in hex_rgb(value):
        channels.append(channel / 12.92 if channel <= 0.03928 else ((channel + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def contrast(first: str, second: str) -> float:
    high, low = sorted((luminance(first), luminance(second)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def qa_pass(path: Path) -> bool:
    payload = json.loads(text(path))
    return payload.get("summary", {}).get("failed") == 0


all_source = "\n".join(text(path) for path in SRC.rglob("*") if path.suffix in {".css", ".vue", ".ts"})
tokens = text(TOKENS)
visualization = text(VIS)
checks: list[tuple[str, bool, str]] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    checks.append((name, bool(condition), detail))


check("legacy_dark_chapter_tokens_removed", not re.search(r"chapter--dark|surface-dark|on-dark|site-nav--dark", all_source))
check("pure_black_and_white_absent", not re.search(r"#(?:000|000000|fff|ffffff)(?![0-9a-f])", all_source, re.I))
for token in ("page-bg", "surface-bg", "ink", "data-teal", "context-copper", "uncertainty-violet", "instrument-bg"):
    check(f"semantic_role_{token}", f"--{token}:" in tokens)
check("body_uses_page_canvas", "background: var(--page-bg);" in text(SRC / "styles" / "v2" / "base.css"))
check("hero_is_warm_surface", 'chapter--surface' in text(SRC / "components" / "v2" / "HeroV2.vue"))
check("prism_section_is_warm", 'chapter--paper prism-chapter' in text(SRC / "components" / "v2" / "QuarterPrismV2.vue"))
check("prism_instrument_is_local", ".prism-scroll-story .quarter-prism" in visualization and "background:var(--instrument-bg)" in visualization)
check("f2_is_warm_surface", 'chapter--surface finding-f2' in text(SRC / "components" / "v2" / "HeadlineFindingsV2.vue"))
check("appendix_is_warm_surface", 'chapter--surface appendix' in text(SRC / "components" / "v2" / "ResearchAppendixV2.vue"))
check("navigation_has_one_theme", "site-nav--dark" not in text(SRC / "components" / "v2" / "SiteNavV2.vue"))
check("source_drawer_is_warm", "background: var(--surface-bg)" in text(SRC / "components" / "evidence" / "SourceList.vue"))
check("warm_text_contrast", contrast("#666c67", "#eeece5") >= 4.5, f"{contrast('#666c67', '#eeece5'):.2f}:1")
check("teal_text_contrast", contrast("#1f716d", "#eeece5") >= 4.5, f"{contrast('#1f716d', '#eeece5'):.2f}:1")
check("copper_text_contrast", contrast("#955a3b", "#eeece5") >= 4.5, f"{contrast('#955a3b', '#eeece5'):.2f}:1")
check("instrument_muted_contrast", contrast("#838e89", "#1c2423") >= 4.5, f"{contrast('#838e89', '#1c2423'):.2f}:1")
check("instrument_uncertainty_contrast", contrast("#948ca3", "#1c2423") >= 4.5, f"{contrast('#948ca3', '#1c2423'):.2f}:1")
check("chrome_qa", qa_pass(REPORT / "chrome_qa.json"))
check("edge_qa", qa_pass(REPORT / "edge_qa.json"))
check("firefox_qa", qa_pass(REPORT / "firefox_qa.json"))
screens = REPORT / "screenshots"
check("seven_desktop_screenshots", all((screens / name).exists() for name in (
    "desktop-hero.webp", "desktop-measurement.webp", "desktop-prism-overlap.webp",
    "desktop-f1.webp", "desktop-f2.webp", "desktop-f4.webp", "desktop-observatory.webp",
)))
check("five_before_after_pairs", all((REPORT / "before_after" / side / name).exists() for side in ("before", "after") for name in (
    "hero.webp", "prism.webp", "f2.webp", "f4.webp", "mobile-390-prism.webp",
)))
check("no_dependency_change", not subprocess.run(
    ["git", "diff", "--quiet", "HEAD", "--", "package.json", "package-lock.json"], cwd=ROOT
).returncode)
check("research_data_unchanged", not subprocess.run(
    ["git", "diff", "--quiet", "HEAD", "--", "data", "research/phase-c", "research/phase-d", "research/phase-e", "research/phase-f"], cwd=ROOT
).returncode)

for index, (name, passed, detail) in enumerate(checks, 1):
    suffix = f" — {detail}" if detail else ""
    print(f"{index:02d}. {'PASS' if passed else 'FAIL'} {name}{suffix}")

passed = sum(item[1] for item in checks)
print(f"COLOR CONTINUITY VALIDATION: {passed}/{len(checks)} PASS")
raise SystemExit(0 if passed == len(checks) else 1)
