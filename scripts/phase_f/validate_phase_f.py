"""Validate Phase F outputs against the frozen method and 70 required checks."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RF = ROOT / "research/phase-f"
DF = ROOT / "data/phase-f"
METHOD = "revenue-tides-method-freeze-1.0.0"
FINDINGS = "revenue-tides-findings-1.0.0"
failures: list[str] = []
passed = 0


def rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(condition: bool, label: str) -> None:
    global passed
    if condition:
        passed += 1
    else:
        failures.append(label)


def rounded(value: Decimal, places: int = 1) -> Decimal:
    quantum = Decimal(1).scaleb(-places)
    return value.quantize(quantum, rounding=ROUND_HALF_UP)


method_manifest = load(ROOT / "research/phase-c/method_freeze_manifest.json")
readiness = load(ROOT / "data/phase-e/findings_readiness_manifest.json")
series = rows(ROOT / "data/phase-d/series.csv")
observations = rows(ROOT / "data/phase-d/observations.csv")
ready = rows(ROOT / "data/phase-e/findings_ready_observations.csv")
metrics = rows(ROOT / "data/phase-d/metric_definitions.csv")
periods = rows(ROOT / "data/phase-d/fiscal_periods.csv")
events = rows(ROOT / "data/phase-d/events.csv")
claims = rows(ROOT / "data/phase-d/attributed_claims.csv")
changes = rows(ROOT / "data/phase-d/change_features.csv")
derivations = rows(ROOT / "data/phase-d/derivations.csv")
sensitivity = rows(ROOT / "research/phase-e/derived_uncertainty_sensitivity.csv")
overlaps = rows(ROOT / "research/phase-e/version_overlap_matrix.csv")
candidates = rows(RF / "candidate_findings.csv")
rejected = rows(RF / "rejected_findings.csv")
validity = rows(RF / "finding_validity_matrix.csv")
robustness = rows(RF / "finding_robustness.csv")
normalized = rows(RF / "normalized_comparison_eligibility.csv")
event_matrix = rows(RF / "event_evidence_matrix.csv")
technical = rows(RF / "series_technical_summary.csv")
formal = load(DF / "formal_findings.json")
formal_csv = rows(DF / "formal_findings.csv")
manifest = load(RF / "findings_manifest.json")
summary = load(RF / "phase_f_summary.json")
manual = rows(RF / "manual_qa.csv")

series_ids = {r["series_id"] for r in series}
obs_ids = {r["observation_id"] for r in observations}
metric_ids = {r["metric_definition_id"] for r in metrics}
period_names = {r["calendar_quarter_equivalent"] for r in periods}
event_ids = {r["event_id"] for r in events}
claim_ids = {r["claim_id"] for r in claims}
formal_ids = [r["finding_id"] for r in formal]
formal_by_id = {r["finding_id"]: r for r in formal}
candidate_by_id = {r["candidate_id"]: r for r in candidates}
validity_by_id = {r["candidate_id"]: r for r in validity}
obs_by_id = {r["observation_id"]: r for r in observations}
change_by_obs = {r["observation_id"]: r for r in changes}
text = "\n".join(str(v) for r in formal for v in r.values() if isinstance(v, str))
statement_text = "\n".join(r["statement_zh"] + "\n" + r["statement_en"] for r in formal).lower()

# 1–14: frozen inputs and structural gates.
check(all(sha(ROOT / "research/phase-c" / name) == digest for name, digest in method_manifest["method_hashes"].items()), "1 method hashes")
check(method_manifest["method_version"] == readiness["method_version"] == manifest["method_version"] == METHOD, "2 method version")
check(readiness["eligible_for_phase_f"] and load(ROOT / "research/phase-e/phase_e_summary.json")["status"] == "PASS", "3 Phase E gate")
check(len(series) == 9 and readiness["validated_series_count"] == 9, "4 corpus nine")
check(len(ready) == 75 and readiness["validated_observation_count"] == 75, "5 observations 75")
check({x for r in formal for x in r["series_ids"]}.issubset(series_ids), "6 no corpus expansion")
check(len(candidates) <= 24, "7 candidate cap")
check(len(formal) >= 3, "8 formal minimum")
check(len(formal) <= 7, "9 formal maximum")
check(len(formal_ids) == len(set(formal_ids)), "10 unique finding IDs")
check(all((RF / "evidence" / f"{fid}.json").is_file() for fid in formal_ids), "11 evidence packs")
series_entity = {r["series_id"]: r["entity_id"] for r in series}
check(all(set(r["observation_ids"]).issubset(obs_ids) and all(obs_by_id[oid]["entity_id"] in {series_entity[sid] for sid in r["series_ids"]} for oid in r["observation_ids"]) for r in formal), "12 observation references")
check(all(set(r["metric_definition_ids"]).issubset(metric_ids) for r in formal), "13 metric references")
check(all(r["period_start"] in period_names and r["period_end"] in period_names for r in formal), "14 valid periods")

# 15: reproduce every numeric claim from observations or validated transformations.
numeric_ok = True
for finding in formal:
    pack = load(RF / "evidence" / f"{finding['finding_id']}.json")
    for claim in pack["numeric_claims"]:
        op, expected = claim["operation"], Decimal(claim["value"])
        actual = None
        if op in {"observation_value", "window_max"}:
            actual = Decimal(obs_by_id[claim["observation_id"]]["value_krw_million"])
        elif op in {"qoq_percent", "endpoint_change_percent"}:
            a = Decimal(obs_by_id[claim["from_observation_id"]]["value_krw_million"])
            b = Decimal(obs_by_id[claim["to_observation_id"]]["value_krw_million"])
            actual = rounded((b / a - 1) * 100, claim.get("precision", 1))
        elif op == "drawdown_percent":
            a = Decimal(obs_by_id[claim["peak_observation_id"]]["value_krw_million"])
            b = Decimal(obs_by_id[claim["end_observation_id"]]["value_krw_million"])
            actual = rounded((b / a - 1) * 100, claim.get("precision", 1))
        elif op == "recovery_duration":
            actual = Decimal(change_by_obs[claim["observation_id"]]["recovery_quarters"])
        elif op == "negative_change_count":
            actual = Decimal(sum(Decimal(r["qoq_percent_change"]) < 0 for r in ready if r["series_id"] == claim["series_id"] and r["metric_definition_id"] == claim["metric_definition_id"] and r["qoq_percent_change"]))
        elif op == "min_same_quarter_difference":
            actual = min(Decimal(r["difference_krw_million"]) for r in overlaps if Decimal(r["difference_krw_million"]) > 0)
        elif op == "max_same_quarter_difference":
            actual = max(Decimal(r["difference_krw_million"]) for r in overlaps)
        elif op in {"min_lineage_m_relative_difference", "max_lineage_m_relative_difference"}:
            vals = [rounded(Decimal(r["difference_krw_million"]) / Decimal(r["legacy_value_krw_million"]) * 100, 1) for r in overlaps if r["series_id"] == "series_lineage_m"]
            actual = min(vals) if op.startswith("min") else max(vals)
        elif op == "zero_difference_pair_count":
            actual = Decimal(sum(Decimal(r["difference_krw_million"]) == 0 for r in overlaps))
        elif op == "sign_sensitive_count":
            actual = Decimal(sum(r["sign_stable"] == "NO" for r in sensitivity))
        elif op == "eligible_derived_change_count":
            actual = Decimal(sum(r["sign_stable"] in {"YES", "NO"} for r in sensitivity))
        elif op == "sign_stable_count":
            actual = Decimal(sum(r["sign_stable"] == "YES" for r in sensitivity))
        elif op == "sign_sensitive_share":
            sens = sum(r["sign_stable"] == "NO" for r in sensitivity)
            eligible = sum(r["sign_stable"] in {"YES", "NO"} for r in sensitivity)
            actual = rounded(Decimal(sens) / Decimal(eligible) * 100, 1)
        else:
            numeric_ok = False
        numeric_ok = numeric_ok and actual == expected
check(numeric_ok, "15 numeric reproduction")

# 16–30: method restrictions.
check(all(not (r["finding_class"] in {"F1_TRAJECTORY", "F2_DRAWDOWN_RECOVERY", "F3_PERSISTENCE"} and len(r["metric_versions"]) > 1) for r in formal), "16 no unauthorized version crossing")
qoq_claims_ok = True
for fid in formal_ids:
    for c in load(RF / "evidence" / f"{fid}.json")["numeric_claims"]:
        if c["operation"] == "qoq_percent":
            qoq_claims_ok &= obs_by_id[c["from_observation_id"]]["metric_definition_id"] == obs_by_id[c["to_observation_id"]]["metric_definition_id"]
check(qoq_claims_ok, "17 no cross-version QoQ")
check("leaderboard" not in statement_text and "排行榜" not in statement_text, "18 no absolute ranking")
check(all(obs_by_id[oid]["evidence_class"] != "INDUSTRY_ESTIMATE" for r in formal for oid in r["observation_ids"]), "19 no industry estimate")
check(sum(r["primary_evidence_basis"] == "DIRECT_OFFICIAL" for r in formal) >= 3, "20 direct official basis minimum")
check(sum(r["primary_evidence_basis"] == "DERIVED_OFFICIAL" for r in formal) <= 2, "21 derived finding cap")
check(all(r["finding_class"] == "F8_DERIVED_UNCERTAINTY" for r in formal if r["evidence_class"] == "DERIVED"), "22 derived directional claims stable")
check(not {"CF16", "CF17"}.intersection({r["candidate_id"] for r in formal}), "23 sign-sensitive directions not formal")
check(sum(r["sign_stable"] == "NO" for r in sensitivity) == 9 and sum(r["sign_stable"] in {"YES", "NO"} for r in sensitivity) == 15, "24 reproduce 9/15")
derived_obs = {r["derivation_id"]: r for r in observations if r["derivation_id"]}
bounds_ok = all(Decimal(derived_obs[d["derivation_id"]]["value_krw_million"]) == Decimal(d["point_estimate"]) * 1000 and Decimal(derived_obs[d["derivation_id"]]["lower_bound_krw_million"]) == Decimal(d["lower_bound"]) * 1000 and Decimal(derived_obs[d["derivation_id"]]["upper_bound_krw_million"]) == Decimal(d["upper_bound"]) * 1000 for d in derivations)
check(bounds_ok, "25 derived bounds")
check(all(obs_by_id[oid]["evidence_class"] == "DERIVED_FROM_OFFICIAL" for r in formal if r["evidence_class"] == "DERIVED" for oid in r["observation_ids"]), "26 derived labels")
check(all(r["causal_inference_allowed"] == "FALSE" for r in event_matrix), "27 event non-causal")
check(all(r["attributed_to"] for r in claims), "28 issuers named")
check("project proves" not in statement_text and "项目证明" not in statement_text, "29 attribution not project causality")
check(all(not ({"legacy_v1", "royalty_v2"}.issubset(set(r["metric_versions"])) and r["finding_class"] != "F7_REPORTING_SEMANTICS") for r in formal), "30 Lineage versions separate")

# 31–43: required candidate families, robustness, and normalized analysis.
check(any(r["finding_type"] == "F7_REPORTING_SEMANTICS" for r in candidates), "31 measurement semantics tested")
check(any(r["finding_type"] == "F8_DERIVED_UNCERTAINTY" for r in candidates), "32 derived uncertainty tested")
check("series_stellar_blade" in candidate_by_id["CF03"]["series_ids"] and candidate_by_id["CF03"]["event_context_used"] == "YES", "33 platform event tested")
recovery_sids = {sid for r in candidates if r["finding_type"] == "F2_DRAWDOWN_RECOVERY" for sid in r["series_ids"].split("|")}
check({"series_nikke", "series_stellar_blade", "series_black_desert", "series_lineage_m", "series_lineage_2m", "series_lineage_w"}.issubset(recovery_sids), "34 recovery systematic")
check(any(r["finding_type"] == "F3_PERSISTENCE" for r in candidates), "35 persistence tested")
check(any(r["finding_type"] == "F4_VOLATILITY" for r in candidates), "36 volatility tested")
check(len(rejected) == len(candidates) - len(formal) and all(r["rejection_reason"] and r["rationale"] for r in rejected), "37 rejection reasons")
check(all(all(validity_by_id[r["candidate_id"]][k] == "YES" for k in ["stable_metric", "continuity_ok", "evidence_ok", "uncertainty_ok", "comparability_ok", "causality_ok", "traceability_ok", "robustness_ok", "language_ok", "formal_eligible"]) for r in formal), "38 validity matrix")
check({r["candidate_id"] for r in formal}.issubset({r["candidate_id"] for r in robustness}), "39 robustness formal coverage")
check(any("LEAVE_ONE" in r["check_type"] for r in robustness) and any(r["candidate_id"] == "CF13" and r["interpretation_stable"] == "NO" for r in robustness), "40 LOO sensitivity")
check(all(r["normalization"] == "BASELINE_INDEX_FIRST_VALID_OBSERVATION" for r in normalized), "41 normalized unitless")
tech = {(r["series_id"], r["metric_definition_id"]): r for r in technical}
eligible_ok = all(r["series_a"] != r["series_b"] and tech[(r["series_a"], r["metric_a"])]["evidence_class"] == "OFFICIAL_REPORTED" and tech[(r["series_b"], r["metric_b"])]["evidence_class"] == "OFFICIAL_REPORTED" and r["window_a"] == r["window_b"] for r in normalized if r["eligible"] == "YES")
check(eligible_ok, "42 eligible normalized windows")
check(all("quarters" in r["window_a"] and "quarters" in r["window_b"] for r in normalized), "43 window length disclosure")

# 44–57: language, completeness, and headline controls.
check(not any(term in statement_text for term in ["winner", "loser", "dominated", "赢家", "输家", "碾压"]), "44 no winner loser")
check("true global revenue" not in statement_text and "真实全球收入" not in statement_text, "45 no true global claim")
check("permanent decline" not in statement_text and "永久下降" not in statement_text, "46 no permanent decline")
check(" caused " not in f" {statement_text} " and "导致" not in statement_text, "47 no unsupported caused")
check(all(r["limitation"].strip() for r in formal), "48 limitations")
check(all(r["forbidden_interpretation"].strip() for r in formal), "49 forbidden interpretations")
check(all(r["title_zh"].strip() for r in formal), "50 Chinese titles")
check(all(r["title_en"].strip() for r in formal), "51 English titles")
check(all(r["statement_zh"].strip() for r in formal), "52 Chinese statements")
check(all(r["statement_en"].strip() for r in formal), "53 English statements")
check(all(r["evidence_class"] in {"DIRECT", "DERIVED", "DESCRIPTIVE", "ATTRIBUTED"} for r in formal), "54 evidence classes")
check(all(r["strength"] in {"STRONG", "MODERATE", "WEAK"} and r["strength"] != "WEAK" for r in formal), "55 strength labels")
check(set(manifest["headline_finding_ids"]).issubset(set(formal_ids)), "56 headlines subset")
check(2 <= len(manifest["headline_finding_ids"]) <= 3, "57 headline count")

# 58–70: traceability, manifests, determinism, parsing, and stop boundary.
check(all(load(RF / "evidence" / f"{r['finding_id']}.json")["numeric_claims"] and set(r["numeric_claim_ids"]) == {c["claim_id"] for c in load(RF / "evidence" / f"{r['finding_id']}.json")["numeric_claims"]} for r in formal), "58 machine numeric trace")
csv_by_id = {r["finding_id"]: r for r in formal_csv}
check(set(csv_by_id) == set(formal_ids) and all(csv_by_id[r["finding_id"]]["title_zh"] == r["title_zh"] and csv_by_id[r["finding_id"]]["statement_en"] == r["statement_en"] for r in formal), "59 CSV JSON agreement")
check(all(load(RF / "evidence" / f"{r['finding_id']}.json")["observation_ids"] == r["observation_ids"] and load(RF / "evidence" / f"{r['finding_id']}.json")["metric_definition_ids"] == r["metric_definition_ids"] for r in formal), "60 packs agree")
check(manifest["candidate_count"] == len(candidates) and manifest["formal_finding_count"] == len(formal) and manifest["rejected_candidate_count"] == len(rejected) and manifest["finding_ids"] == formal_ids, "61 manifest reconcile")
check(not any(k in {"color", "chart", "layout", "animation", "component", "interaction", "style"} for r in formal for k in r), "62 no UI metadata")
check(not any((ROOT / name).exists() for name in ["package.json", "vite.config.js", "vite.config.ts", "node_modules", "src"]), "63 no frontend files")
freeze_text = (RF / "FINDINGS_FREEZE.md").read_text(encoding="utf-8")
freeze_pairs = re.findall(r"- `([^`]+)`: `([0-9a-f]{64})`", freeze_text)
check(bool(freeze_pairs) and all(sha(ROOT / name) == digest for name, digest in freeze_pairs), "64 freeze hashes")
script_text = (ROOT / "scripts/phase_f/analyze_findings.py").read_text(encoding="utf-8")
check(not any(token in script_text for token in ["datetime.now", "date.today", "random.", "uuid."]), "65 deterministic analysis code")
generated = [p for p in RF.rglob("*") if p.is_file()] + [p for p in DF.rglob("*") if p.is_file()]
before = {p.relative_to(ROOT).as_posix(): sha(p) for p in generated}
subprocess.run([sys.executable, str(ROOT / "scripts/phase_f/analyze_findings.py")], cwd=ROOT, check=True)
after = {p.relative_to(ROOT).as_posix(): sha(p) for p in generated}
check(before == after, "66 second run reproducibility")
phase_f_csv = list(RF.glob("*.csv")) + [DF / "formal_findings.csv"]
check(len(phase_f_csv) == 9 and all(rows(p) is not None for p in phase_f_csv), "67 CSV parse")
phase_f_json = list(RF.glob("*.json")) + list((RF / "evidence").glob("*.json")) + [DF / "formal_findings.json"]
check(all(load(p) is not None for p in phase_f_json), "68 JSON parse")
required = [
    RF / "PHASE_F_FINDINGS.md", RF / "series_technical_summary.csv", RF / "candidate_findings.csv",
    RF / "rejected_findings.csv", RF / "finding_validity_matrix.csv", RF / "finding_robustness.csv",
    RF / "normalized_comparison_eligibility.csv", RF / "event_evidence_matrix.csv", RF / "headline_findings.md",
    RF / "FINDINGS_FREEZE.md", RF / "findings_manifest.json", RF / "phase_f_summary.json",
    RF / "manual_qa.csv", DF / "formal_findings.json", DF / "formal_findings.csv",
    ROOT / "scripts/phase_f/analyze_findings.py", ROOT / "scripts/phase_f/validate_phase_f.py", ROOT / "work.md",
]
check(all(p.is_file() for p in required), "69 required files")
check(summary["stop_boundary"] == "STOPPED BEFORE PHASE G" and "STOPPED BEFORE PHASE G" in (RF / "PHASE_F_FINDINGS.md").read_text(encoding="utf-8"), "70 stop boundary")

if passed + len(failures) != 70:
    failures.append(f"validator definition count is {passed + len(failures)}, expected 70")

if failures:
    print(f"AUTOMATED TESTS: {passed}/{passed + len(failures)} PASS")
    for failure in failures:
        print(f"FAIL: {failure}")
    raise SystemExit(1)

print("AUTOMATED TESTS: 70/70 PASS")
