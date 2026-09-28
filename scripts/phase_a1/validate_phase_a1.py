from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "research" / "phase-a1"


def rows(name: str) -> list[dict[str, str]]:
    with (DATA / name).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def quarter_index(label: str) -> int:
    year = int(label[:4])
    quarter = int(label[-1])
    return year * 4 + quarter - 1


def main() -> int:
    observations = rows("official_observation_samples.csv")
    companies = rows("company_source_matrix.csv")
    series = rows("game_series_candidates.csv")
    continuity = rows("continuity_matrix.csv")
    derivations = rows("derivation_samples.csv")

    results: list[tuple[str, bool]] = []
    add = lambda name, ok: results.append((name, bool(ok)))

    add("1 source URL exists for every quantitative sample", all(r["source_url"].startswith(("http://", "https://")) for r in observations))
    add("2 reporting company is present", all(r["company_id"] and r["company_name"] for r in observations))
    add("3 reporting period is explicit", all(r["period_start"] and r["period_end"] and r["fiscal_quarter"] for r in observations))
    add("4 PDF-derived observations include source page", all(r["source_page"] for r in observations))
    add("5 original unit and currency are stored", all(r["reported_unit"] and r["original_currency"] for r in observations))

    allowed_evidence = {"OFFICIAL_REPORTED", "DERIVED_FROM_OFFICIAL", "INDUSTRY_ESTIMATE", "RANK_OBSERVED", "EVENT_OFFICIAL", "SECONDARY_CONTEXT", "UNKNOWN"}
    add("6 evidence class is explicit", all(r["evidence_class"] in allowed_evidence for r in observations))
    add("7 OFFICIAL_REPORTED has no derivation formula", all(not r["derivation_formula"] for r in observations if r["evidence_class"] == "OFFICIAL_REPORTED"))
    add("8 DERIVED_FROM_OFFICIAL has a formula", all(r["derivation_formula"] for r in observations if r["evidence_class"] == "DERIVED_FROM_OFFICIAL"))
    add("9 no INDUSTRY_ESTIMATE is labeled official", all(not (r["evidence_class"] == "INDUSTRY_ESTIMATE" and "official" in r["metric_type"].lower()) for r in observations))
    add("10 no company or segment amount is assigned to a title", all(not (r["entity_type"] in {"GAME_TITLE", "GAME_EDITION"} and r["metric_type"] in {"company_revenue", "segment_revenue"}) for r in observations))
    add("11 no missing amount becomes zero", all(r["reported_value"] not in {"", "0", "0.0", "0.00"} for r in observations))

    forbidden_geometry = ("pixel", "chart area", "bar height", "geometry")
    add("12 no chart geometry fabricates numeric values", all(not any(term in (r["derivation_formula"] + " " + r["notes"]).lower() for term in forbidden_geometry) for r in observations))

    allowed_entities = {"GAME_TITLE", "GAME_EDITION", "FRANCHISE", "IP", "SEGMENT"}
    add("13 entity type is explicit", all(r["entity_type"] in allowed_entities for r in observations) and all(r["entity_type"] in allowed_entities for r in series))

    keys = [(r["company_id"], r["entity_id"], r["period_start"], r["period_end"], r["metric_type"]) for r in observations]
    add("14 duplicate company game period metric observations are absent", len(keys) == len(set(keys)))

    snapshots_ok = True
    for r in observations:
        if r["snapshot_path"]:
            path = ROOT / r["snapshot_path"]
            snapshots_ok = snapshots_ok and path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == r["snapshot_sha256"]
    add("15 saved snapshot hashes validate", snapshots_ok)

    non_overlap = True
    grouped: dict[tuple[str, str, str], list[tuple[date, date]]] = defaultdict(list)
    for r in observations:
        grouped[(r["company_id"], r["entity_id"], r["metric_type"])].append((date.fromisoformat(r["period_start"]), date.fromisoformat(r["period_end"])))
    for periods in grouped.values():
        periods.sort()
        non_overlap = non_overlap and all(periods[i - 1][1] < periods[i][0] for i in range(1, len(periods)))
    add("16 reporting periods do not overlap unexpectedly", non_overlap)

    continuity_ok = True
    sample_counts = defaultdict(int)
    for r in observations:
        sample_counts[(r["company_id"], r["entity_id"], r["metric_type"])] += 1
    for r in continuity:
        verified = int(r["verified_consecutive_quarters"])
        if verified:
            reproducible = quarter_index(r["last_fiscal_period"]) - quarter_index(r["first_fiscal_period"]) + 1
            continuity_ok = continuity_ok and reproducible == verified
            key = (r["company_id"], r["entity_id"], r["metric_type"])
            if sample_counts[key]:
                continuity_ok = continuity_ok and sample_counts[key] == verified
    add("17 continuity counts are reproducible", continuity_ok)

    parse_ok = True
    for path in DATA.glob("*.csv"):
        with path.open("r", encoding="utf-8", newline="") as handle:
            parsed = list(csv.reader(handle))
            parse_ok = parse_ok and bool(parsed) and len({len(row) for row in parsed}) == 1
    with (DATA / "phase_a1_summary.json").open("r", encoding="utf-8") as handle:
        json.load(handle)
    add("18 all CSV and JSON artifacts parse successfully", parse_ok)

    for name, ok in results:
        print(f"{'PASS' if ok else 'FAIL'} - {name}")
    passed = sum(ok for _, ok in results)
    print(f"\n{passed}/{len(results)} PASS")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

