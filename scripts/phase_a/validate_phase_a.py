#!/usr/bin/env python3
"""Lightweight standard-library validation for Phase A research artifacts."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PHASE = ROOT / "research" / "phase-a"


def rows(name: str) -> list[dict[str, str]]:
    with (PHASE / name).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        parsed = list(reader)
        if reader.fieldnames is None:
            raise AssertionError(f"{name}: missing header")
        for number, row in enumerate(parsed, start=2):
            if None in row:
                raise AssertionError(f"{name}:{number}: too many fields")
            if any(value is None for value in row.values()):
                raise AssertionError(f"{name}:{number}: too few fields")
        return parsed


def unique(values: list[str]) -> bool:
    return len(values) == len(set(values)) and all(values)


def run() -> int:
    tests: list[tuple[str, callable]] = []

    sources = rows("source_registry.csv")
    games = rows("pilot_games.csv")
    observations = rows("observation_candidates.csv")
    inventory = rows("monthly_source_inventory.csv")
    access = rows("access_test_results.csv")
    events = rows("live_event_samples.csv")
    claims = rows("attributed_claim_samples.csv")
    matrix = rows("metric_coverage_matrix.csv")

    source_ids = {r["source_id"] for r in sources}
    game_ids = {r["game_id"] for r in games}

    evidence = {
        "OFFICIAL_REPORTED",
        "INDUSTRY_ESTIMATE",
        "RANK_OBSERVED",
        "EVENT_OFFICIAL",
        "SECONDARY_CONTEXT",
        "UNKNOWN",
    }
    missing = {
        "AVAILABLE",
        "NOT_PUBLISHED",
        "LOGIN_REQUIRED",
        "PAID_ONLY",
        "NOT_APPLICABLE",
        "NOT_FOUND",
        "AMBIGUOUS",
        "ACCESS_ERROR",
    }

    tests.append(("every source has a URL", lambda: all(r["url"].startswith("http") for r in sources)))
    tests.append(("every saved snapshot has SHA-256", lambda: all((not r["snapshot_path"]) or bool(re.fullmatch(r"[0-9a-fA-F]{64}", r["sha256"])) for r in sources)))
    tests.append(("every observation candidate has an evidence class", lambda: all(r["evidence_class"] in evidence for r in observations)))

    metric_cols = [
        "exact_estimated_revenue", "estimated_consumer_spending", "revenue_rank",
        "revenue_growth_rank", "downloads", "download_rank", "download_growth_rank",
        "official_reported_amount", "market_aggregate_amount", "event_date",
    ]
    tests.append(("no missing state is encoded as numeric zero", lambda: all(r[col] in missing and r[col] != "0" for r in matrix for col in metric_cols) and all(r["missing_state"] in missing for r in observations)))
    tests.append(("game IDs are unique", lambda: unique([r["game_id"] for r in games])))
    tests.append(("source IDs are unique", lambda: unique([r["source_id"] for r in sources])))

    def fks_resolve() -> bool:
        source_ref_rows = inventory + access + observations + events + claims
        if not all(r["source_id"] in source_ids for r in source_ref_rows):
            return False
        game_ref_rows = access + observations + events + claims + matrix
        return all((not r.get("game_id")) or r["game_id"] in game_ids for r in game_ref_rows)

    tests.append(("known foreign keys resolve", fks_resolve))
    tests.append(("observation period and publication date are separate", lambda: all({"period_start", "period_end", "published_at"}.issubset(r.keys()) for r in observations) and all("observation_month" in r and "published_at" in r for r in inventory)))
    tests.append(("estimate versus official is explicit", lambda: all(r["is_estimate"] in {"true", "false"} and ((r["evidence_class"] == "OFFICIAL_REPORTED") == (r["is_estimate"] == "false")) for r in observations)))
    tests.append(("platform and market coverage are explicit", lambda: all(r["platform_scope"] and r["market"] for r in observations) and all(r["platform_scope"] and r["region_scope"] for r in games)))
    tests.append(("no Steam owners-times-price revenue proxy exists", lambda: all("OWNER" not in r["metric_type"].upper() and "PRICE" not in r["metric_type"].upper() for r in observations)))
    tests.append(("no unsupported causal statement is stored as fact", lambda: all(r["claim_status"] == "ATTRIBUTED_CLAIM" and r["our_causal_conclusion"] == "false" for r in claims)))
    tests.append(("all pilot games have identity status", lambda: all(r["identity_status"] for r in games)))
    tests.append(("monthly inventory has no duplicate months", lambda: unique([r["observation_month"] for r in inventory]) and len(inventory) == 22))

    def all_csv_parse() -> bool:
        for path in PHASE.glob("*.csv"):
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.reader(handle)
                parsed = list(reader)
                if not parsed:
                    return False
                width = len(parsed[0])
                if width == 0 or any(len(row) != width for row in parsed):
                    return False
        return True

    tests.append(("all Phase A CSV files parse successfully", all_csv_parse))

    passed = 0
    for index, (name, check) in enumerate(tests, start=1):
        try:
            ok = bool(check())
        except Exception as exc:  # concise diagnostic; validation must continue
            ok = False
            print(f"{index:02d}. FAIL — {name}: {exc}")
        else:
            print(f"{index:02d}. {'PASS' if ok else 'FAIL'} — {name}")
        passed += int(ok)

    print(f"\nRESULT: {passed}/{len(tests)} PASS")
    return 0 if passed == len(tests) else 1


if __name__ == "__main__":
    sys.exit(run())

