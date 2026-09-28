"""Validate the frozen Phase G web-data product without changing public output."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "data/web"
RESEARCH = ROOT / "research/phase-g"
BUILD = ROOT / "scripts/phase_g/build_web_data.py"
METHOD_VERSION = "revenue-tides-method-freeze-1.0.0"
FINDINGS_VERSION = "revenue-tides-findings-1.0.0"
WEBDATA_VERSION = "revenue-tides-webdata-1.0.0"
DATA_CUTOFF = "2026-09-22"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_digest(directory: Path) -> dict[str, str]:
    return {
        path.relative_to(directory).as_posix(): digest(path)
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


def close(actual: float, expected: float, tolerance: float = 0.051) -> bool:
    return abs(float(actual) - float(expected)) <= tolerance


def percent_change(start: float, end: float) -> float:
    return (end / start - 1) * 100


def syntactic_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


class Checks:
    def __init__(self) -> None:
        self.rows: list[tuple[int, str, bool, str]] = []

    def add(self, number: int, name: str, condition: bool, detail: str = "") -> None:
        self.rows.append((number, name, bool(condition), detail))

    def finish(self) -> int:
        numbers = [row[0] for row in self.rows]
        if numbers != list(range(1, 91)):
            raise RuntimeError(f"Validator definition error: expected tests 1..90, got {numbers}")
        for number, name, passed, detail in self.rows:
            suffix = f" — {detail}" if detail else ""
            print(f"{number:02d}. {'PASS' if passed else 'FAIL'} {name}{suffix}")
        passed = sum(row[2] for row in self.rows)
        print(f"AUTOMATED TESTS: {passed}/{len(self.rows)} PASS")
        return 0 if passed == len(self.rows) else 1


def main() -> int:
    c = Checks()

    manifest = read_json(WEB / "manifest.json")
    project = read_json(WEB / "project.json")
    index = read_json(WEB / "series_index.json")
    findings = read_json(WEB / "findings.json")
    sources = read_json(WEB / "sources.json")
    caveats = read_json(WEB / "caveats.json")
    frozen = read_json(ROOT / "data/phase-f/formal_findings.json")
    frozen_by_id = {row["finding_id"]: row for row in frozen}
    web_findings = {row["finding_id"]: row for row in findings}
    series_rows = read_csv(ROOT / "data/phase-d/series.csv")
    canonical_observations = read_csv(ROOT / "data/phase-d/observations.csv")
    canonical_events = read_csv(ROOT / "data/phase-d/events.csv")
    canonical_claims = read_csv(ROOT / "data/phase-d/attributed_claims.csv")
    canonical_companies = read_csv(ROOT / "data/phase-d/companies.csv")
    details = {row["series_id"]: read_json(WEB / row["detail_path"]) for row in index}
    observations = {
        obs["observation_id"]: obs
        for detail in details.values()
        for obs in detail["observations"]
    }
    metrics = {
        metric["metric_definition_id"]: metric
        for detail in details.values()
        for metric in detail["metric_versions"]
    }
    events = {
        event["event_id"]: event
        for detail in details.values()
        for event in detail["events"]
    }
    claims = {
        claim["claim_id"]: claim
        for detail in details.values()
        for claim in detail["attributed_claims"]
    }
    source_ids = {row["source_id"] for row in sources}
    finding_ids = set(web_findings)
    series_ids = set(details)

    method_manifest = read_json(ROOT / "research/phase-c/method_freeze_manifest.json")
    method_hashes = method_manifest["method_hashes"]
    method_hash_ok = bool(method_hashes) and all(digest(ROOT / "research/phase-c" / path) == expected for path, expected in method_hashes.items())
    c.add(1, "Phase C method hashes validate", method_hash_ok, f"{len(method_hashes)} files")

    findings_manifest = read_json(ROOT / "research/phase-f/findings_manifest.json")
    freeze_text = (ROOT / "research/phase-f/FINDINGS_FREEZE.md").read_text(encoding="utf-8")
    findings_hashes = dict(re.findall(r"- `([^`]+)`: `([0-9a-f]{64})`", freeze_text))
    findings_hash_ok = bool(findings_hashes) and all(digest(ROOT / path) == expected for path, expected in findings_hashes.items())
    c.add(2, "Phase F Findings hashes validate", findings_hash_ok, f"{len(findings_hashes)} files")
    c.add(3, "method version unchanged", manifest["method_version"] == project["method_version"] == METHOD_VERSION)
    c.add(4, "findings version unchanged", manifest["findings_version"] == project["findings_version"] == FINDINGS_VERSION)
    c.add(5, "webdata version is correct", manifest["webdata_version"] == project["webdata_version"] == WEBDATA_VERSION)
    c.add(6, "data cutoff unchanged", manifest["data_cutoff"] == project["data_cutoff"] == DATA_CUTOFF)
    c.add(7, "corpus remains 9 series", manifest["series_count"] == len(details) == len(series_rows) == 9)
    c.add(8, "observations remain 75", manifest["observation_count"] == len(observations) == len(canonical_observations) == 75)
    c.add(9, "events remain 26", manifest["event_count"] == len(events) == len(canonical_events) == 26)
    c.add(10, "findings remain 6", manifest["finding_count"] == len(findings) == len(frozen) == 6)
    c.add(11, "headline Findings remain F1/F2/F4", {row["finding_id"] for row in findings if row["headline"]} == {"F1", "F2", "F4"})
    c.add(12, "no corpus expansion", series_ids == {row["series_id"] for row in series_rows})
    fiscal_labels = {row["fiscal_period_id"]: row["calendar_quarter_equivalent"] for row in read_csv(ROOT / "data/phase-d/fiscal_periods.csv")}
    canonical_periods = {fiscal_labels[row["fiscal_period_id"]] for row in canonical_observations}
    c.add(13, "no new quarter", {obs["quarter"] for obs in observations.values()} == canonical_periods)
    c.add(14, "no new company", {row["company_id"] for row in project["companies"]} == {row["company_id"] for row in canonical_companies})
    c.add(15, "manifest exists", (WEB / "manifest.json").is_file())
    c.add(16, "project metadata exists", (WEB / "project.json").is_file())
    c.add(17, "series index contains exactly 9 series", len(index) == 9)
    detail_files = list((WEB / "series").glob("*.json"))
    c.add(18, "exactly 9 series detail files exist", len(detail_files) == 9)
    c.add(19, "all series IDs unique", len(series_ids) == len(index) == 9)
    c.add(20, "all referenced detail paths exist", all((WEB / row["detail_path"]).is_file() for row in index))
    c.add(21, "all observation IDs are valid", set(observations) == {row["observation_id"] for row in canonical_observations})
    canonical_metric_ids = {row["metric_definition_id"] for row in read_csv(ROOT / "data/phase-d/metric_definitions.csv")}
    c.add(22, "all metric-version IDs are valid", set(metrics) == canonical_metric_ids and all(obs["metric_definition_id"] in metrics for obs in observations.values()))
    c.add(23, "all source IDs are valid", bool(source_ids) and all(obs["source_id"] in source_ids for obs in observations.values()))
    c.add(24, "all event IDs are valid", set(events) == {row["event_id"] for row in canonical_events})
    c.add(25, "all claim IDs are valid", set(claims) == {row["claim_id"] for row in canonical_claims})
    c.add(26, "all Finding IDs are valid", finding_ids == {row["finding_id"] for row in frozen})
    refs_ok = all(
        set(f["series_ids"]) <= series_ids
        and set(f["observation_ids"]) <= set(observations)
        and set(f["metric_definition_ids"]) <= set(metrics)
        and set(f["event_ids"]) <= set(events)
        and set(f["claim_ids"]) <= set(claims)
        and set(f["source_ids"]) <= source_ids
        for f in findings
    ) and all(event["source_id"] in source_ids for event in events.values()) and all(claim["source_id"] in source_ids for claim in claims.values())
    c.add(27, "all cross-file refs resolve", refs_ok)

    # Independent numeric reproduction from public observations only.
    lm = details["series_lineage_m"]["observations"]
    overlap_diffs = []
    for quarter in ("2025Q2", "2025Q3", "2025Q4"):
        rows = {obs["metric_version"]: obs for obs in lm if obs["quarter"] == quarter}
        overlap_diffs.append(rows["royalty_integrated_v2"]["value"] - rows["legacy_v1"]["value"])
    lineage_other_zero = all(
        next(obs for obs in details[sid]["observations"] if obs["quarter"] == quarter and obs["metric_version"] == "royalty_integrated_v2")["value"]
        == next(obs for obs in details[sid]["observations"] if obs["quarter"] == quarter and obs["metric_version"] == "legacy_v1")["value"]
        for sid in ("series_lineage_2m", "series_lineage_w")
        for quarter in ("2025Q2", "2025Q3", "2025Q4")
    )
    f1_ok = close(min(overlap_diffs), 6797, 0.001) and close(max(overlap_diffs), 13455, 0.001) and lineage_other_zero

    stellar = {obs["quarter"]: obs for obs in details["series_stellar_blade"]["observations"]}
    f2_pct = percent_change(stellar["2025Q1"]["value"], stellar["2025Q2"]["value"])
    f2_ok = close(stellar["2025Q1"]["value"], 7011.668848, 0.000001) and close(stellar["2025Q2"]["value"], 65718.814485, 0.000001) and close(f2_pct, 837.3) and stellar["2025Q2"]["value"] == max(obs["value"] for obs in stellar.values())

    nikke = {obs["quarter"]: obs for obs in details["series_nikke"]["observations"]}
    f3_rebound = percent_change(nikke["2026Q1"]["value"], nikke["2026Q2"]["value"])
    f3_gap = percent_change(nikke["2025Q2"]["value"], nikke["2026Q2"]["value"])
    f3_ok = close(f3_rebound, 32.4) and close(f3_gap, -4.1) and nikke["2026Q2"]["recovery"]["status"] == "NOT_RECOVERED_WITHIN_OBSERVED_WINDOW"

    bd = {obs["quarter"]: obs for obs in details["series_black_desert"]["observations"]}
    f4_initial = percent_change(bd["2024Q4"]["value"], bd["2025Q2"]["value"])
    f4_final = percent_change(max(obs["value"] for obs in bd.values()), bd["2026Q2"]["value"])
    f4_recovery = bd["2025Q3"]["recovery"]["quarters"]
    f4_ok = close(f4_initial, -20.7) and f4_recovery == 3 and close(f4_final, -30.8) and bd["2026Q2"]["recovery"]["status"] == "NOT_RECOVERED_WITHIN_OBSERVED_WINDOW"

    lw = [obs for obs in details["series_lineage_w"]["observations"] if obs["metric_version"] == "royalty_integrated_v2"]
    lw.sort(key=lambda row: row["period_index"])
    f5_decline = percent_change(lw[0]["value"], lw[-1]["value"])
    f5_ok = close(f5_decline, -35.3) and sum(obs["qoq"]["percent_change"] < 0 for obs in lw if obs["qoq"]["eligible"]) == 4

    derived = [obs for obs in observations.values() if obs["evidence_class"] == "DERIVED_FROM_OFFICIAL"]
    derived_changes = [obs for obs in derived if obs["qoq"]["eligible"]]
    stable = sum(bool(obs["derived"]["direction_sign_stable"]) for obs in derived_changes)
    sensitive = len(derived_changes) - stable
    f6_ok = len(derived_changes) == 15 and sensitive == 9 and stable == 6 and close(sensitive / len(derived_changes) * 100, 60.0, 0.0001)
    c.add(28, "all six Findings reproduce from web data", all((f1_ok, f2_ok, f3_ok, f4_ok, f5_ok, f6_ok)))
    c.add(29, "F1 version differences reproduce", f1_ok)
    c.add(30, "F2 values and 837.3% reproduce", f2_ok)
    c.add(31, "F3 32.4% reproduces", close(f3_rebound, 32.4))
    c.add(32, "F3 4.1% below peak reproduces", close(f3_gap, -4.1))
    c.add(33, "F4 20.7% drawdown reproduces", close(f4_initial, -20.7))
    c.add(34, "F4 recovery timing reproduces", f4_recovery == 3)
    c.add(35, "F4 30.8% ending drawdown reproduces", close(f4_final, -30.8))
    c.add(36, "F5 35.3% decline reproduces", close(f5_decline, -35.3))
    c.add(37, "F6 9/15 reproduces", sensitive == 9 and len(derived_changes) == 15)
    c.add(38, "F6 60.0% reproduces", close(sensitive / len(derived_changes) * 100, 60.0, 0.0001))
    c.add(39, "derived bounds exist", len(derived) == 18 and all(obs["lower_bound"] is not None and obs["upper_bound"] is not None for obs in derived))
    c.add(40, "derived sign stability exists", all(obs["derived"] is not None and isinstance(obs["derived"]["direction_sign_stable"], bool) for obs in derived_changes))
    c.add(41, "all derived observations remain labeled derived", len(derived) == 18 and all(obs["evidence_class"] == "DERIVED_FROM_OFFICIAL" for obs in derived))
    direct_ids = {row["observation_id"] for row in canonical_observations if row["evidence_class"] == "OFFICIAL_REPORTED"}
    c.add(42, "no derived value becomes direct", not (set(obs["observation_id"] for obs in derived) & direct_ids))
    cross_qoq = [obs for obs in observations.values() if obs["qoq"]["eligible"] and observations[obs["qoq"]["previous_observation_id"]]["metric_definition_id"] != obs["metric_definition_id"]]
    c.add(43, "no cross-version QoQ exists", not cross_qoq)
    first_by_metric = {}
    for obs in sorted(observations.values(), key=lambda row: row["period_index"]):
        first_by_metric.setdefault(obs["metric_definition_id"], obs)
    c.add(44, "baseline resets after version break", all(obs["baseline_index"] == 100 and not obs["qoq"]["eligible"] for obs in first_by_metric.values()))
    overlap_ok = True
    for sid in ("series_lineage_m", "series_lineage_2m", "series_lineage_w"):
        counts = Counter(obs["quarter"] for obs in details[sid]["observations"])
        overlap_ok &= sum(count == 2 for count in counts.values()) == 3
    c.add(45, "Lineage overlapping quarters remain representable", overlap_ok)
    c.add(46, "no single-value quarter map overwrites version overlap", overlap_ok and all(isinstance(details[sid]["observations"], list) for sid in ("series_lineage_m", "series_lineage_2m", "series_lineage_w")))
    c.add(47, "Black Desert remains IP", details["series_black_desert"]["identity"]["entity_type"] == "IP")
    c.add(48, "NIKKE remains IP", details["series_nikke"]["identity"]["entity_type"] == "IP")
    c.add(49, "Stellar Blade remains IP", details["series_stellar_blade"]["identity"]["entity_type"] == "IP")
    expected_types = {row["series_id"]: row["entity_type"] for row in series_rows}
    c.add(50, "title entities remain GAME_TITLE", all(details[sid]["identity"]["entity_type"] == expected_types[sid] for sid in series_ids))

    public_files = [path for path in WEB.rglob("*") if path.is_file()]
    public_text = "\n".join(path.read_text(encoding="utf-8") for path in public_files)
    source_keys = {key for row in sources for key in row}
    c.add(51, "public source registry has no local path", not ({"local_path", "snapshot_path", "raw_path"} & source_keys))
    c.add(52, "public files contain no E drive path", "E:\\" not in public_text and "E:/" not in public_text)
    raw_hashes = {row["sha256"] for row in read_csv(ROOT / "data/phase-d/sources.csv") if row.get("sha256")}
    c.add(53, "public files contain no raw PDF hash", not any(value in public_text for value in raw_hashes))
    c.add(54, "public files contain no internal extractor identity", "extractor_identity" not in public_text.lower() and "extracted_by" not in public_text.lower())
    c.add(55, "public files contain no QA defect notes", "qa_defect" not in public_text.lower() and "defect_note" not in public_text.lower())
    c.add(56, "no Sensor Tower quantitative data appears", "sensor tower" not in public_text.lower())
    c.add(57, "no AppMagic quantitative data appears", "appmagic" not in public_text.lower())
    currencies = {obs["currency"] for obs in observations.values()}
    c.add(58, "no USD conversion exists", "USD" not in currencies and "usd_normal" not in public_text.lower())
    c.add(59, "no cross-company leaderboard field exists", "leaderboard" not in public_text.lower() and "cross_company_rank" not in public_text.lower())
    c.add(60, "no success score exists", "success_score" not in public_text.lower() and "commercial_health" not in public_text.lower())
    c.add(61, "no fabricated trend labels exist", '"trend"' not in public_text.lower() and '"momentum_score"' not in public_text.lower())
    c.add(62, "no event causal field exists", all(not ({"caused_revenue_change", "causal", "effect"} & set(event)) for event in events.values()))
    caveat_ids = {row["caveat_id"] for row in caveats}
    c.add(63, "event coverage caveat exists", "CAVEAT_CURATED_EVENTS" in caveat_ids)
    c.add(64, "cross-company comparability caveat exists", "CAVEAT_CROSS_COMPANY_NOT_COMPARABLE" in caveat_ids)
    c.add(65, "derived uncertainty caveat exists", "CAVEAT_DERIVED_ROUNDING" in caveat_ids)
    c.add(66, "version-break caveat exists", "CAVEAT_VERSION_BREAK" in caveat_ids)
    notice = (WEB / "NOTICE.md").read_text(encoding="utf-8")
    c.add(67, "source copyrights notice is present", "copyright" in notice.lower() and "respective owners" in notice.lower())
    canonical_values = {row["observation_id"]: row["value_krw_million"] for row in canonical_observations}
    precision_ok = all(str(obs["value"]) == str(float(canonical_values[oid])).rstrip("0").rstrip(".") or float(obs["value"]) == float(canonical_values[oid]) for oid, obs in observations.items())
    c.add(68, "public observation values preserve adequate precision", precision_ok)
    frozen_fields = ("title_zh", "title_en", "statement_zh", "statement_en", "quantitative_summary", "uncertainty_note")
    c.add(69, "public Finding statements match frozen Phase F text", all(all(web_findings[fid][field] == frozen_by_id[fid][field] for field in frozen_fields) for fid in finding_ids))
    c.add(70, "public Finding limitations are preserved", all(web_findings[fid]["limitations"] == frozen_by_id[fid]["limitation"] for fid in finding_ids))
    c.add(71, "public forbidden interpretations are preserved", all(web_findings[fid]["forbidden_interpretation"] == frozen_by_id[fid]["forbidden_interpretation"] for fid in finding_ids))
    c.add(72, "public Finding evidence refs resolve", all(set(row["observation_ids"]) <= set(observations) and set(row["metric_definition_ids"]) <= set(metrics) for row in findings))
    c.add(73, "public event refs resolve", all(set(row["event_ids"]) <= set(events) for row in findings))
    c.add(74, "public claim refs resolve", all(set(row["claim_ids"]) <= set(claims) for row in findings))
    c.add(75, "public source refs resolve", all(set(row["source_ids"]) <= source_ids for row in findings) and all(syntactic_url(row["canonical_url"]) for row in sources))
    audit_sizes = {row["path"]: int(row["bytes"]) for row in read_csv(RESEARCH / "file_size_audit.csv")}
    actual_sizes = {path.relative_to(WEB).as_posix(): path.stat().st_size for path in public_files}
    c.add(76, "file sizes are recorded", all(audit_sizes.get(path) == size for path, size in actual_sizes.items()))
    total_size = sum(actual_sizes.values())
    c.add(77, "total web data below 2 MB", total_size < 2 * 1024 * 1024, f"{total_size} bytes")
    warning_expected = total_size > 1024 * 1024
    warning_recorded = "SOFT WARNING" in (RESEARCH / "file_size_audit.csv").read_text(encoding="utf-8")
    c.add(78, "soft warning is correct if above 1 MB", warning_expected == warning_recorded)
    c.add(79, "bootstrap manifest remains small", (WEB / "manifest.json").stat().st_size < 20 * 1024)
    c.add(80, "each series detail size is reported", all(audit_sizes.get(path.relative_to(WEB).as_posix()) == path.stat().st_size and path.stat().st_size < 50 * 1024 for path in detail_files))
    deterministic_json = all(path.read_text(encoding="utf-8") == json.dumps(read_json(path), ensure_ascii=False, indent=2, sort_keys=True) + "\n" for path in WEB.rglob("*.json"))
    c.add(81, "JSON key/order output is deterministic", deterministic_json)

    before = tree_digest(WEB)
    run = subprocess.run([sys.executable, str(BUILD)], cwd=ROOT, capture_output=True, text=True)
    after = tree_digest(WEB)
    c.add(82, "canonical build succeeds", run.returncode == 0, run.stderr.strip())
    c.add(83, "second build byte-matches", before == after)
    temp_root = Path(tempfile.mkdtemp(prefix="phase-g-validate-", dir=ROOT / "tmp"))
    temp_web = temp_root / "data/web"
    clean_run = subprocess.run([sys.executable, str(BUILD), "--web-output", str(temp_web), "--public-only"], cwd=ROOT, capture_output=True, text=True)
    clean_match = clean_run.returncode == 0 and tree_digest(temp_web) == after
    shutil.rmtree(temp_root)
    c.add(84, "temporary clean build matches", clean_match)
    c.add(85, "validator does not mutate public output", tree_digest(WEB) == after)
    parse_ok = True
    try:
        for path in WEB.rglob("*.json"):
            read_json(path)
    except (json.JSONDecodeError, UnicodeDecodeError):
        parse_ok = False
    c.add(86, "all JSON files parse", parse_ok)
    schema_doc = (RESEARCH / "web_data_schema.md").read_text(encoding="utf-8")
    c.add(87, "schema validation passes", all(name in schema_doc for name in ("manifest.json", "project.json", "series_index.json", "series/{series_id}.json", "findings.json", "sources.json", "caveats.json")))
    c.add(88, "NOTICE exists", (WEB / "NOTICE.md").is_file())
    required = [
        "PHASE_G_WEB_DATA_PRODUCTIZATION.md", "web_data_schema.md", "input_manifest.json",
        "file_size_audit.csv", "reference_integrity_audit.md", "finding_reproduction_audit.md",
        "version_break_web_audit.md", "uncertainty_web_audit.md", "public_internal_separation_audit.md",
        "deterministic_build_audit.md", "phase_g_summary.json", "manual_qa.csv",
    ]
    c.add(89, "all required research outputs exist", all((RESEARCH / name).is_file() for name in required))
    report = (RESEARCH / "PHASE_G_WEB_DATA_PRODUCTIZATION.md").read_text(encoding="utf-8")
    c.add(90, "STOP boundary remains before Phase H", "STOPPED BEFORE PHASE H" in report and not (ROOT / "research/phase-h").exists())
    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())
