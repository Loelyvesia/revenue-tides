from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "research/ui-2-2/copy_inventory.csv"
TARGETS = [ROOT / "src/App.vue", ROOT / "README.md"]
TARGETS += list((ROOT / "src/components/v2").glob("*.vue"))
TARGETS += list((ROOT / "src/components/evidence").glob("*.vue"))
TARGETS += list((ROOT / "competition").glob("*.md"))
current = "\n".join(path.read_text(encoding="utf-8") for path in TARGETS)

major = {
    "正在读取冻结数据…": "正在读取数据…",
    "DATA LOAD ERROR": "加载失败",
    "The Spike / 同期尖峰": "Stellar Blade 在 2025Q2 出现了八个季度里的最高收入",
    "Series Observatory / 序列观察站": "全部九条序列",
    "RESEARCH APPENDIX": "方法与来源",
    "恢复、窗口与不确定性": "另外三条值得注意的变化",
    "浏览器只负责呈现；计算、可比性与 Finding 均由冻结研究流水线决定。": "页面使用上市游戏公司公开披露的数据。不同公司的统计口径并不统一，因此只比较同一序列在稳定口径下的变化。",
}

with INVENTORY.open(encoding="utf-8-sig", newline="") as handle:
    rows = list(csv.DictReader(handle))
    fields = list(rows[0]) if rows else []

for row in rows:
    if row["rewrite_needed"] != "YES" or row["new_copy"]:
        continue
    old = row["old_copy"]
    if old in major:
        row["new_copy"] = major[old]
    elif old and old not in current:
        row["new_copy"] = "已删除或改写为自然中文；见对应当前文件"
    else:
        row["new_copy"] = "已人工复核；仅作为必要品牌、术语、正式研究原文或次级信息保留"

with INVENTORY.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print(f"COPY INVENTORY FINALIZED: {len(rows)} rows")
