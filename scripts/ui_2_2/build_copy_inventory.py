from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "research" / "ui-2-2" / "copy_inventory.csv"
VUE_FILES = [ROOT / "src/App.vue", *(ROOT / "src/components/v2").glob("*.vue"), *(ROOT / "src/components/evidence").glob("*.vue")]
MD_FILES = [ROOT / "README.md", *(ROOT / "competition").glob("*.md")]

PROBLEM_PATTERNS = {
    "decorative bilingual slash title": re.compile(r"[A-Za-z][^\n]{0,50}\s/\s[^\n]{0,80}[\u3400-\u9fff]|[\u3400-\u9fff][^\n]{0,50}\s/\s[A-Za-z]"),
    "all-caps technical label": re.compile(r"\b[A-Z][A-Z0-9 _·/—-]{3,}\b"),
    "AI / method-spec phrasing": re.compile(r"不是.{0,30}而是|合法|保持.{0,12}边界|语境|冻结|流水线|观察窗口|禁止解读|不被压缩|研究层|呈现层"),
    "translation-like metadata": re.compile(r"ACT [IVX]+|READING OUTPUT|SAME QUARTER|REPORTING DEFINITION|RESEARCH APPENDIX|WINDOW PEAK|SELECTED SERIES|PUBLIC SOURCE"),
}

REWRITES = {
    "流水不是一个统一数字。": "同一款游戏，在不同财报里未必只有一个收入数字。",
    "报告口径、实体范围与证据方式，会改变我们看到的商业轨迹。": "先看清统计口径，再看它怎么变化。",
    "Normalized within each series · absolute revenue is not compared · 不同公司绝对收入不可比较": "各公司披露口径不同，这里不做绝对收入排名。",
    "实体范围可能不同": "这个数字统计的是什么？",
    "同一季度，两个合法口径": "同一个季度，为什么会有两个数字？",
    "推导值必须带着区间": "有些数字是算出来的。",
    "事件只提供时间语境": "同季度发生，不代表存在因果。",
    "改变的不是时间，而是报告定义。": "NCSOFT 调整了报告口径。2025Q2—Q4，旧口径和纳入 royalties 的新口径同时存在。",
    "The Spike / 同期尖峰": "Stellar Blade 在 2025Q2 出现了八个季度里的最高收入",
    "一轮恢复之后，\n潮位再次退去": "Black Desert 恢复到新高后，又连续回落",
    "Series Observatory / 序列观察站": "全部九条序列",
    "恢复、窗口与不确定性": "另外三条值得注意的变化",
    "RESEARCH APPENDIX / 研究附录": "数据怎么来，哪些比较能做",
    "禁止解读": "需要注意",
}


def classify(text: str, context: str) -> str:
    lowered = context.lower()
    if "nav" in lowered: return "NAV"
    if any(token in lowered for token in ("button", "select", "option")): return "CONTROL"
    if any(token in lowered for token in ("source", "evidence")): return "SOURCE"
    if any(token in lowered for token in ("finding", "f1", "f2", "f4")): return "FINDING"
    if any(token in lowered for token in ("caveat", "limitation", "forbidden")): return "CAVEAT"
    if re.search(r"<h[1-6]|^#", context): return "TITLE"
    if any(token in lowered for token in ("aria-label", "eyebrow", "meta", "caption")): return "TECHNICAL"
    if len(text) > 55: return "LEDE"
    return "ANNOTATION"


def problems(text: str) -> str:
    found = [label for label, pattern in PROBLEM_PATTERNS.items() if pattern.search(text)]
    if text.count("·") >= 2: found.append("dense dot-separated metadata")
    if len(text) > 90: found.append("long sentence / paragraph")
    return "; ".join(dict.fromkeys(found))


rows: list[dict[str, str]] = []
seen: set[tuple[str, str]] = set()

for path in sorted(VUE_FILES):
    source = path.read_text(encoding="utf-8")
    template = source.split("<template>", 1)[-1].split("</template>", 1)[0]
    for line_number, line in enumerate(template.splitlines(), 1):
        candidates = []
        candidates.extend(re.findall(r">\s*([^<>{}\n][^<>{}\n]*?)\s*<", line))
        candidates.extend(re.findall(r"(?:aria-label|title|placeholder)=\"([^\"]+)\"", line))
        for raw in candidates:
            text = re.sub(r"\s+", " ", raw).strip()
            if not text or text in {"/", "—", "·", "↗", "←", "→"} or text.startswith(":"):
                continue
            key = (path.as_posix(), text)
            if key in seen: continue
            seen.add(key)
            issue = problems(text)
            rows.append({
                "location": f"{path.relative_to(ROOT).as_posix()}:{line_number}",
                "component": path.stem,
                "old_copy": text,
                "type": classify(text, line),
                "problem": issue,
                "rewrite_needed": "YES" if issue or text in REWRITES else "NO",
                "new_copy": REWRITES.get(text, ""),
            })

for path in sorted(MD_FILES):
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        text = raw.strip()
        if not text or text.startswith(("```", "---", "![", "|---")) or re.match(r"^\|?\s*:?-+:?", text):
            continue
        text = re.sub(r"^#{1,6}\s+", "", text)
        text = re.sub(r"^[-*]\s+", "", text)
        if not text: continue
        issue = problems(text)
        rows.append({
            "location": f"{path.relative_to(ROOT).as_posix()}:{line_number}",
            "component": path.stem,
            "old_copy": text,
            "type": classify(text, raw),
            "problem": issue,
            "rewrite_needed": "YES" if issue else "NO",
            "new_copy": REWRITES.get(text, ""),
        })

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=["location", "component", "old_copy", "type", "problem", "rewrite_needed", "new_copy"])
    writer.writeheader()
    writer.writerows(rows)

print(f"COPY INVENTORY: {len(rows)} strings")
print(f"REWRITE REVIEW: {sum(row['rewrite_needed'] == 'YES' for row in rows)} strings")
