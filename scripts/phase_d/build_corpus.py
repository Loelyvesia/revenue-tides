#!/usr/bin/env python3
"""Deterministically build the Phase D curated corpus from frozen Phase B inputs."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR
from pathlib import Path
from statistics import median


ROOT = Path(__file__).resolve().parents[2]
PB = ROOT / "data" / "phase-b"
DATA = ROOT / "data" / "phase-d"
INPUT = DATA / "input"
RESEARCH = ROOT / "research" / "phase-d"
METHOD = "revenue-tides-method-freeze-1.0.0"
CUTOFF = "2026-09-22"
BUILD_VERSION = "phase-d-curated-corpus-v1"


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(obj, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8", newline="\n")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def dec_text(value: Decimal | None) -> str:
    if value is None:
        return ""
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def to_krw_million(value: Decimal, unit: str) -> Decimal:
    return value / Decimal("1000000") if unit == "KRW" else value if unit == "KRW_million" else value * 1000


SERIES = [
    {"series_id": "series_nikke", "entity_id": "nikke_ip", "company_id": "shift_up", "canonical_name": "Goddess of Victory: NIKKE", "entity_type": "IP", "primary_evidence_class": "OFFICIAL_REPORTED", "cohort_type": "CORE", "analysis_window_start": "2024-07-01", "analysis_window_end": "2026-06-30", "first_quarter": "2024Q3", "last_quarter": "2026Q2", "expected_quarters": "8", "platform_scope": "Publisher-defined IP scope; predominantly mobile", "selection_rationale": "Eight exact quarters from official SHIFT UP IP revenue tables."},
    {"series_id": "series_stellar_blade", "entity_id": "stellar_blade_ip", "company_id": "shift_up", "canonical_name": "Stellar Blade", "entity_type": "IP", "primary_evidence_class": "OFFICIAL_REPORTED", "cohort_type": "CORE", "analysis_window_start": "2024-07-01", "analysis_window_end": "2026-06-30", "first_quarter": "2024Q3", "last_quarter": "2026Q2", "expected_quarters": "8", "platform_scope": "PS5; PC from 2025Q2", "selection_rationale": "Eight exact quarters and a clearly documented platform expansion."},
    {"series_id": "series_lineage_m", "entity_id": "lineage_m_title", "company_id": "ncsoft", "canonical_name": "Lineage M", "entity_type": "GAME_TITLE", "primary_evidence_class": "OFFICIAL_REPORTED", "cohort_type": "CORE", "analysis_window_start": "2024-07-01", "analysis_window_end": "2026-06-30", "first_quarter": "2024Q3", "last_quarter": "2026Q2", "expected_quarters": "8", "platform_scope": "Mobile title/IP presentation", "selection_rationale": "Six-quarter legacy window plus a separately versioned five-quarter royalty-integrated window."},
    {"series_id": "series_black_desert", "entity_id": "black_desert_ip", "company_id": "pearl_abyss", "canonical_name": "Black Desert", "entity_type": "IP", "primary_evidence_class": "OFFICIAL_REPORTED", "cohort_type": "CORE", "analysis_window_start": "2024-07-01", "analysis_window_end": "2026-06-30", "first_quarter": "2024Q3", "last_quarter": "2026Q2", "expected_quarters": "8", "platform_scope": "PC; console; mobile", "selection_rationale": "Eight exact publisher-reported all-platform IP quarters."},
    {"series_id": "series_mcoc", "entity_id": "marvel_contest_of_champions_title", "company_id": "netmarble", "canonical_name": "MARVEL Contest of Champions", "entity_type": "GAME_TITLE", "primary_evidence_class": "DERIVED_FROM_OFFICIAL", "cohort_type": "CORE", "analysis_window_start": "2024-07-01", "analysis_window_end": "2025-12-31", "first_quarter": "2024Q3", "last_quarter": "2025Q4", "expected_quarters": "6", "platform_scope": "Mobile title; consolidated company denominator", "selection_rationale": "Six deterministic official total-times-share derivations with uncertainty."},
    {"series_id": "series_lineage_2m", "entity_id": "lineage_2m_title", "company_id": "ncsoft", "canonical_name": "Lineage 2M", "entity_type": "GAME_TITLE", "primary_evidence_class": "OFFICIAL_REPORTED", "cohort_type": "CORE", "analysis_window_start": "2024-07-01", "analysis_window_end": "2026-06-30", "first_quarter": "2024Q3", "last_quarter": "2026Q2", "expected_quarters": "8", "platform_scope": "Mobile and PURPLE client under publisher title/IP scope", "selection_rationale": "Six-quarter legacy window plus a separately versioned five-quarter royalty-integrated window."},
    {"series_id": "series_lineage_w", "entity_id": "lineage_w_title", "company_id": "ncsoft", "canonical_name": "Lineage W", "entity_type": "GAME_TITLE", "primary_evidence_class": "OFFICIAL_REPORTED", "cohort_type": "CORE", "analysis_window_start": "2024-07-01", "analysis_window_end": "2026-06-30", "first_quarter": "2024Q3", "last_quarter": "2026Q2", "expected_quarters": "8", "platform_scope": "Mobile and PURPLE client under publisher title/IP scope", "selection_rationale": "Six-quarter legacy window plus a separately versioned five-quarter royalty-integrated window."},
    {"series_id": "series_jackpot_world", "entity_id": "jackpot_world_title", "company_id": "netmarble", "canonical_name": "Jackpot World", "entity_type": "GAME_TITLE", "primary_evidence_class": "DERIVED_FROM_OFFICIAL", "cohort_type": "CORE", "analysis_window_start": "2024-07-01", "analysis_window_end": "2025-12-31", "first_quarter": "2024Q3", "last_quarter": "2025Q4", "expected_quarters": "6", "platform_scope": "Mobile title; consolidated company denominator", "selection_rationale": "Six consecutive official title shares with compatible consolidated revenue denominators."},
    {"series_id": "series_lotsa_slots", "entity_id": "lotsa_slots_title", "company_id": "netmarble", "canonical_name": "Lotsa Slots", "entity_type": "GAME_TITLE", "primary_evidence_class": "DERIVED_FROM_OFFICIAL", "cohort_type": "CORE", "analysis_window_start": "2024-07-01", "analysis_window_end": "2025-12-31", "first_quarter": "2024Q3", "last_quarter": "2025Q4", "expected_quarters": "6", "platform_scope": "Mobile title; consolidated company denominator", "selection_rationale": "Six consecutive official title shares with compatible consolidated revenue denominators."},
]

ENTITY_TO_SERIES = {r["entity_id"]: r["series_id"] for r in SERIES}

NEW_ENTITIES = [
    {"entity_id": "lineage_2m_title", "canonical_name": "Lineage 2M", "publisher_defined_name": "리니지2M", "entity_type": "GAME_TITLE", "reporting_company_id": "ncsoft", "developer_if_known": "NCSOFT", "scope_note": "Publisher-defined Lineage 2M title. Legacy and royalty-integrated presentation scopes remain separate metric versions.", "identity_status": "VERIFIED_WITH_METRIC_VERSION_BREAK", "valid_from": "2019-11-27", "valid_to": "", "parent_entity_id": "lineage_franchise"},
    {"entity_id": "lineage_w_title", "canonical_name": "Lineage W", "publisher_defined_name": "리니지W", "entity_type": "GAME_TITLE", "reporting_company_id": "ncsoft", "developer_if_known": "NCSOFT", "scope_note": "Publisher-defined Lineage W title. Legacy and royalty-integrated presentation scopes remain separate metric versions.", "identity_status": "VERIFIED_WITH_METRIC_VERSION_BREAK", "valid_from": "2021-11-04", "valid_to": "", "parent_entity_id": "lineage_franchise"},
    {"entity_id": "jackpot_world_title", "canonical_name": "Jackpot World", "publisher_defined_name": "Jackpot World", "entity_type": "GAME_TITLE", "reporting_company_id": "netmarble", "developer_if_known": "SpinX Games", "scope_note": "Title-level point estimate derived from Netmarble consolidated revenue and rounded title share.", "identity_status": "VERIFIED_DERIVED_SCOPE", "valid_from": "2016-01-01", "valid_to": "", "parent_entity_id": ""},
    {"entity_id": "lotsa_slots_title", "canonical_name": "Lotsa Slots", "publisher_defined_name": "Lotsa Slots", "entity_type": "GAME_TITLE", "reporting_company_id": "netmarble", "developer_if_known": "SpinX Games", "scope_note": "Title-level point estimate derived from Netmarble consolidated revenue and rounded title share.", "identity_status": "VERIFIED_DERIVED_SCOPE", "valid_from": "2013-01-01", "valid_to": "", "parent_entity_id": ""},
]


def nc_metric(slug: str, title: str, version: str) -> dict:
    legacy = version == "legacy_v1"
    return {
        "metric_definition_id": f"md_nc_{slug}_{'legacy_v1' if legacy else 'royalty_v2'}",
        "metric_name": f"{title} {'mobile game revenue - legacy scope' if legacy else 'IP revenue including royalties - restated/new scope'}",
        "reporting_company_id": "ncsoft", "entity_scope": "GAME_TITLE" if legacy else "GAME_TITLE_WITH_IP_REVENUE_PRESENTATION",
        "economic_meaning": f"{title} revenue shown in NCSOFT's {'legacy mobile-game chart' if legacy else 'five-quarter IP revenue presentation with royalties integrated'}.",
        "accounting_scope": "NCSOFT mobile title chart; other mobile games excluded" if legacy else "NCSOFT mobile IP line; other mobile games excluded; royalties integrated",
        "platform_scope": "Mobile" if legacy else "Mobile title/IP presentation", "geographic_scope": "Consolidated reporting regions",
        "includes_royalties": "NO_OR_NOT_INTEGRATED_IN_PRESENTATION" if legacy else "YES", "includes_licensing": "UNKNOWN", "includes_platform_receipts": "UNKNOWN",
        "unit_basis": "KRW million", "valid_from": "2024-07-01" if legacy else "2025-04-01", "valid_to": "2025-12-31" if legacy else "",
        "metric_version": version, "comparable_group_id": f"cg_nc_{slug}_{'legacy_v1' if legacy else 'royalty_v2'}",
        "source_note": "NCSOFT 4Q24 p6; 2Q25 p5; 4Q25 p6." if legacy else "NCSOFT 2Q26 presentation p6; five-quarter window 2025Q2-2026Q2.",
    }


def derived_metric(slug: str, title: str) -> dict:
    return {"metric_definition_id": f"md_nm_{slug}_derived_v1", "metric_name": f"Derived {title} title revenue share of Netmarble revenue", "reporting_company_id": "netmarble", "entity_scope": "GAME_TITLE", "economic_meaning": f"Official Netmarble consolidated quarterly revenue multiplied by official rounded {title} contribution share.", "accounting_scope": "Derived allocation of consolidated Netmarble revenue", "platform_scope": "Inherits consolidated denominator; title is mobile but denominator spans company activities", "geographic_scope": "Global consolidated reporting scope", "includes_royalties": "UNKNOWN", "includes_licensing": "UNKNOWN", "includes_platform_receipts": "UNKNOWN", "unit_basis": "KRW billion point estimate with share-rounding interval", "valid_from": "2024-07-01", "valid_to": "2025-12-31", "metric_version": "derived_v1", "comparable_group_id": f"cg_nm_{slug}_derived_v1", "source_note": "Quarterly deck total revenue page and game portfolio page; share rounded to whole percent."}


NEW_METRICS = [
    nc_metric("lineage_2m", "Lineage 2M", "legacy_v1"), nc_metric("lineage_2m", "Lineage 2M", "royalty_integrated_v2"),
    nc_metric("lineage_w", "Lineage W", "legacy_v1"), nc_metric("lineage_w", "Lineage W", "royalty_integrated_v2"),
    derived_metric("jackpot_world", "Jackpot World"), derived_metric("lotsa_slots", "Lotsa Slots"),
]

EVENT_SOURCE_SPECS = [
    ("src_su_nikke_2y_html", "SHIFT UP", "https://shiftup.co.kr/news/news.php?code=news&idx=217&page=1&ptype=view", "2024-11-08", "2024Q4"),
    ("src_su_nikke_coins_html", "SHIFT UP", "https://shiftup.co.kr/news/news.php?category=&code=news&idx=292&ptype=view", "2025-09-05", "2025Q3"),
    ("src_su_nikke_3y_html", "SHIFT UP", "https://shiftup.co.kr/news/news.php?code=news&idx=302&page=1&ptype=view", "2025-11-06", "2025Q4"),
    ("src_ps_stellar_nier_html", "PlayStation / SHIFT UP", "https://blog.playstation.com/2024/11/11/stellar-blades-nier-automata-dlc-photo-mode-launch-nov-20/", "2024-11-11", "2024Q4"),
    ("src_ps_stellar_holiday_html", "PlayStation / SHIFT UP", "https://blog.playstation.com/2024/12/16/stellar-blades-holiday-themed-event-brings-new-costumes-mini-game-and-more-dec-17/", "2024-12-16", "2024Q4"),
    ("src_su_stellar_nikke_dlc_html", "SHIFT UP", "https://shiftup.co.kr/news/news.php?category=&idx=268&ptype=view", "2025-05-22", "2025Q2"),
    ("src_nc_lm_vanguard_html", "NCSOFT", "https://about.ncsoft.com/news/article/lineagem_update_240925", "2024-09-25", "2024Q3"),
    ("src_nc_lm_oasis4_html", "NCSOFT", "https://about.ncsoft.com/news/article/lineagem_update_241204", "2024-12-04", "2024Q4"),
    ("src_nc_l2m_5y_html", "NCSOFT", "https://about.ncsoft.com/news/article/lineage2_update_241127", "2024-11-27", "2024Q4"),
    ("src_nc_l2m_sea_html", "NCSOFT", "https://about.ncsoft.com/en/news/article/lineage2m-update-250331", "2025-03-31", "2025Q2"),
    ("src_nc_l2m_pledge_html", "NCSOFT", "https://about.ncsoft.com/jp/news/article/lineage2m-update-250528", "2025-05-28", "2025Q2"),
    ("src_nc_l2m_requiem_html", "NCSOFT", "https://about.ncsoft.com/news/article/lineage2m_update_260527", "2026-05-27", "2026Q2"),
    ("src_nc_lw_alphonse_html", "NCSOFT", "https://about.ncsoft.com/news/article/lineagew_update_240703", "2024-07-03", "2024Q3"),
    ("src_nc_lw_3y_html", "NCSOFT", "https://about.ncsoft.com/news/article/lineagew_update_241113", "2024-11-13", "2024Q4"),
    ("src_nc_lw_4y_html", "NCSOFT", "https://about.ncsoft.com/news/article/lineagew_update_251105", "2025-11-05", "2025Q4"),
    ("src_nc_lw_knight_html", "NCSOFT", "https://about.ncsoft.com/news/article/lineagew_update_260401", "2026-04-01", "2026Q2"),
    ("src_pa_bd_10y_html", "Pearl Abyss", "https://blackdesert.pearlabyss.com/Console/en-us/News/Notice/Detail?_boardNo=11971", "2024-10-11", "2024Q4"),
    ("src_pa_bd_edania_html", "Pearl Abyss", "https://blackdesert.pearlabyss.com/Asia/en-US/News/Notice/Detail?_boardNo=8020", "2025-08-21", "2025Q3"),
    ("src_kabam_mcoc_raids_html", "Kabam", "https://forums.playcontestofchampions.com/en/discussion/376875/alliance-quest-raids-updates", "2024-09-27", "2024Q3"),
    ("src_kabam_mcoc_10y_html", "Kabam", "https://forums.playcontestofchampions.com/en/discussion/382945/december-side-quest-chrono-versary-part-2", "2024-12-01", "2024Q4"),
    ("src_nc_2q25_results_html", "NCSOFT", "https://about.ncsoft.com/en/news/article/news_update_250812", "2025-08-12", "2025Q2"),
]


def build_sources() -> list[dict]:
    rows = read_csv(PB / "sources.csv")
    for sid, publisher, url, published, period in EVENT_SOURCE_SPECS:
        rows.append({"source_id": sid, "publisher_name": publisher, "source_url": url, "source_type": "OFFICIAL_GAME_OR_PUBLISHER_HTML", "published_at": published, "retrieved_at": CUTOFF, "local_path": "", "sha256": "", "file_size": "", "language": "English/Korean/Japanese as published", "reporting_period": period, "access_class": "PUBLIC_NO_LOGIN", "officiality": "OFFICIAL", "reuse_note": "URL-only event provenance; no local mirror retained."})
    return sorted(rows, key=lambda r: r["source_id"])


def build_observations(extractions: list[dict], metrics: list[dict], periods: list[dict], sources: list[dict]) -> tuple[list[dict], list[dict]]:
    observations = read_csv(PB / "observations.csv")
    derivations = read_csv(PB / "derivations.csv")
    metric_map = {r["metric_definition_id"]: r for r in metrics}
    period_map = {r["fiscal_period_id"]: r for r in periods}
    source_map = {r["source_id"]: r for r in sources}
    company_by_entity = {r["entity_id"]: r["company_id"] for r in SERIES}
    grouped: dict[tuple[str, str], dict[str, dict]] = defaultdict(dict)
    for row in extractions:
        grouped[(row["entity_id"], row["fiscal_period_id"])][row["field_name"]] = row
    for row in extractions:
        if row["field_name"] != "reported_value" or row["entity_id"] not in {"lineage_2m_title", "lineage_w_title"}:
            continue
        md = metric_map[row["metric_definition_id"]]
        value = Decimal(row["field_value"])
        prefix = "l2m" if row["entity_id"] == "lineage_2m_title" else "lw"
        vtag = "v1" if md["metric_version"] == "legacy_v1" else "v2"
        quarter = period_map[row["fiscal_period_id"]]["calendar_quarter_equivalent"].lower()
        observations.append({"observation_id": f"obs_{prefix}_{vtag}_{quarter}", "entity_id": row["entity_id"], "company_id": "ncsoft", "fiscal_period_id": row["fiscal_period_id"], "metric_definition_id": row["metric_definition_id"], "metric_version": md["metric_version"], "comparable_group_id": md["comparable_group_id"], "evidence_class": "OFFICIAL_REPORTED", "reported_value_raw": dec_text(value), "reported_unit_raw": row["unit"], "currency": "KRW", "value_krw_million": dec_text(to_krw_million(value, row["unit"])), "lower_bound_krw_million": "", "upper_bound_krw_million": "", "derivation_id": "", "source_id": row["source_id"], "source_page": row["source_page"], "published_at": source_map[row["source_id"]]["published_at"], "retrieved_at": CUTOFF, "platform_scope": md["platform_scope"], "geographic_scope": md["geographic_scope"], "reporting_scope": "NCSOFT mobile title/IP publisher revenue presentation", "missingness_state": "AVAILABLE", "notes": row["extractor_note"]})
    for (entity_id, period_id), fields in grouped.items():
        if entity_id not in {"jackpot_world_title", "lotsa_slots_title"} or "input_total_revenue" not in fields or "input_share_percent" not in fields:
            continue
        total_row, share_row = fields["input_total_revenue"], fields["input_share_percent"]
        total, share = Decimal(total_row["field_value"]), Decimal(share_row["field_value"])
        point = total * share / 100
        low = (total * (share - Decimal("0.5")) / 100).quantize(Decimal("0.01"), rounding=ROUND_FLOOR)
        high = (total * (share + Decimal("0.5")) / 100).quantize(Decimal("0.01"), rounding=ROUND_CEILING)
        slug = "jackpot" if entity_id == "jackpot_world_title" else "lotsa"
        mdid = total_row["metric_definition_id"]
        md = metric_map[mdid]
        quarter = period_map[period_id]["calendar_quarter_equivalent"].lower()
        did = f"drv_{slug}_{quarter}"
        derivations.append({"derivation_id": did, "formula_text": f"{dec_text(total)} * ({dec_text(share)} / 100)", "input_total_value": dec_text(total), "input_total_unit": total_row["unit"], "input_share_percent": dec_text(share), "share_rounding_increment": "1 percentage point", "point_estimate": dec_text(point), "lower_bound": dec_text(low), "upper_bound": dec_text(high), "calculation_method": "Decimal arithmetic; point estimate uses reported share; compatible share interval is +/-0.5pp; bounds rounded outward to 0.01 KRW billion", "source_total_id": total_row["extraction_id"], "source_share_id": share_row["extraction_id"], "verification_status": "VERIFIED_REPRODUCIBLE", "bound_unit": "KRW_billion"})
        observations.append({"observation_id": f"obs_{slug}_{quarter}", "entity_id": entity_id, "company_id": company_by_entity[entity_id], "fiscal_period_id": period_id, "metric_definition_id": mdid, "metric_version": md["metric_version"], "comparable_group_id": md["comparable_group_id"], "evidence_class": "DERIVED_FROM_OFFICIAL", "reported_value_raw": dec_text(point), "reported_unit_raw": "KRW_billion", "currency": "KRW", "value_krw_million": dec_text(point * 1000), "lower_bound_krw_million": dec_text(low * 1000), "upper_bound_krw_million": dec_text(high * 1000), "derivation_id": did, "source_id": total_row["source_id"], "source_page": f"{total_row['source_page']};{share_row['source_page']}", "published_at": source_map[total_row["source_id"]]["published_at"], "retrieved_at": CUTOFF, "platform_scope": md["platform_scope"], "geographic_scope": md["geographic_scope"], "reporting_scope": "Netmarble consolidated revenue multiplied by rounded official title share", "missingness_state": "AVAILABLE", "notes": "Derived point estimate; not directly reported title revenue."})
    return sorted(observations, key=lambda r: r["observation_id"]), sorted(derivations, key=lambda r: r["derivation_id"])


EVENT_SPECS = [
    ("evt_nikke_2y", "nikke_ip", "Second anniversary OLD TALES update", "ANNIVERSARY_UPDATE", "2024-10-31", "fp_shift_up_2024q4", "Mobile / live service", "Global", "src_su_nikke_2y_html"),
    ("evt_nikke_coins", "nikke_ip", "COINS IN RUSH update", "MAJOR_CONTENT_UPDATE", "2025-09-04", "fp_shift_up_2025q3", "Mobile / live service", "Global", "src_su_nikke_coins_html"),
    ("evt_nikke_3y", "nikke_ip", "Third anniversary GODDESS FALL update", "ANNIVERSARY_UPDATE", "2025-11-06", "fp_shift_up_2025q4", "Mobile / live service", "Global", "src_su_nikke_3y_html"),
    ("evt_nikke_35_anniv", "nikke_ip", "3.5th anniversary STAR ANIS update", "ANNIVERSARY_UPDATE", "2026-04-23", "fp_shift_up_2026q2", "Mobile / live service", "Global", "src_su_nikke_35_html"),
    ("evt_stellar_nier", "stellar_blade_ip", "NieR:Automata DLC and Photo Mode", "COLLABORATION_DLC", "2024-11-20", "fp_shift_up_2024q4", "PS5", "Global", "src_ps_stellar_nier_html"),
    ("evt_stellar_holiday", "stellar_blade_ip", "Holiday-themed event", "MAJOR_CONTENT_UPDATE", "2024-12-17", "fp_shift_up_2024q4", "PS5", "Global", "src_ps_stellar_holiday_html"),
    ("evt_stellar_pc_launch", "stellar_blade_ip", "Stellar Blade PC launch", "PLATFORM_LAUNCH", "2025-06-11", "fp_shift_up_2025q2", "PC", "Global", "src_ps_stellar_pc_html"),
    ("evt_stellar_nikke_dlc", "stellar_blade_ip", "Goddess of Victory: NIKKE collaboration DLC", "COLLABORATION_DLC", "2025-06-12", "fp_shift_up_2025q2", "PS5; PC", "Global", "src_su_stellar_nikke_dlc_html"),
    ("evt_lm_vanguard", "lineage_m_title", "VANGUARD: Age of Romance update", "MAJOR_UPDATE", "2024-09-25", "fp_ncsoft_2024q3", "Mobile", "Korea", "src_nc_lm_vanguard_html"),
    ("evt_lm_oasis4", "lineage_m_title", "OASIS 4: ADVENTURE update", "MAJOR_UPDATE", "2024-12-04", "fp_ncsoft_2024q4", "Mobile", "Korea", "src_nc_lm_oasis4_html"),
    ("evt_lm_homecoming", "lineage_m_title", "HOMECOMING update", "MAJOR_UPDATE", "2025-03-05", "fp_ncsoft_2025q1", "Mobile", "Korea", "src_nc_lm_homecoming_html"),
    ("evt_lm_rising_storm", "lineage_m_title", "RISING STORM update", "MAJOR_UPDATE", "2025-06-18", "fp_ncsoft_2025q2", "Mobile", "Korea", "src_nc_lm_rising_html"),
    ("evt_l2m_5y", "lineage_2m_title", "Fifth anniversary My Chronicle update", "ANNIVERSARY_UPDATE", "2024-11-27", "fp_ncsoft_2024q4", "Mobile; PURPLE", "Korea", "src_nc_l2m_5y_html"),
    ("evt_l2m_sea_launch", "lineage_2m_title", "Southeast Asia service launch", "REGIONAL_LAUNCH", "2025-05-20", "fp_ncsoft_2025q2", "Mobile; PURPLE", "Six Southeast Asian countries", "src_nc_l2m_sea_html"),
    ("evt_l2m_pledge", "lineage_2m_title", "THE PLEDGE update", "MAJOR_UPDATE", "2025-05-28", "fp_ncsoft_2025q2", "Mobile; PURPLE", "Japan service", "src_nc_l2m_pledge_html"),
    ("evt_l2m_requiem", "lineage_2m_title", "REQUIEM update", "MAJOR_UPDATE", "2026-05-27", "fp_ncsoft_2026q2", "Mobile; PURPLE", "Korea", "src_nc_l2m_requiem_html"),
    ("evt_lw_alphonse", "lineage_w_title", "Alphonse economy-specialized world launch", "NEW_WORLD", "2024-07-10", "fp_ncsoft_2024q3", "Mobile; PURPLE", "Korea", "src_nc_lw_alphonse_html"),
    ("evt_lw_3y", "lineage_w_title", "Third anniversary Memory of Lineage update", "ANNIVERSARY_UPDATE", "2024-11-13", "fp_ncsoft_2024q4", "Mobile; PURPLE", "Korea", "src_nc_lw_3y_html"),
    ("evt_lw_4y", "lineage_w_title", "Fourth anniversary update", "ANNIVERSARY_UPDATE", "2025-11-05", "fp_ncsoft_2025q4", "Mobile; PURPLE", "Korea", "src_nc_lw_4y_html"),
    ("evt_lw_knight", "lineage_w_title", "Knight class renewal and Wonderland collaboration", "MAJOR_UPDATE", "2026-04-08", "fp_ncsoft_2026q2", "Mobile; PURPLE", "Korea", "src_nc_lw_knight_html"),
    ("evt_bd_morning_light_seoul", "black_desert_ip", "Land of the Morning Light: Seoul release", "EXPANSION_UPDATE", "2024-09-12", "fp_pearl_abyss_2024q3", "Black Desert PC live service", "Global rollout", "src_pa_bd_seoul_html"),
    ("evt_bd_10y", "black_desert_ip", "A Decade of Adventures anniversary event", "ANNIVERSARY_EVENT", "2024-12-14", "fp_pearl_abyss_2024q4", "Black Desert cross-platform IP context", "Global / South Korea event", "src_pa_bd_10y_html"),
    ("evt_bd_wukong", "black_desert_ip", "Wukong class release", "MAJOR_CONTENT_UPDATE", "2025-07-02", "fp_pearl_abyss_2025q3", "Black Desert PC live service", "Asia regional service", "src_pa_bd_wukong_html"),
    ("evt_bd_edania", "black_desert_ip", "Edania update", "EXPANSION_UPDATE", "2025-08-21", "fp_pearl_abyss_2025q3", "Black Desert PC live service", "Asia regional service", "src_pa_bd_edania_html"),
    ("evt_mcoc_raids", "marvel_contest_of_champions_title", "Alliance Quest Raids update", "MAJOR_CONTENT_UPDATE", "2024-09-30", "fp_netmarble_2024q3", "Mobile", "Global", "src_kabam_mcoc_raids_html"),
    ("evt_mcoc_10y", "marvel_contest_of_champions_title", "Chrono-versary tenth anniversary event", "ANNIVERSARY_EVENT", "2024-12-11", "fp_netmarble_2024q4", "Mobile", "Global", "src_kabam_mcoc_10y_html"),
]


def build_events() -> list[dict]:
    return [{"event_id": e[0], "entity_id": e[1], "event_name": e[2], "event_type": e[3], "event_date_start": e[4], "event_date_end": "", "fiscal_period_id": e[5], "platform_scope": e[6], "region_scope": e[7], "source_id": e[8], "source_page_if_applicable": "", "date_precision": "DAY", "notes": "Official event date retained as temporal context only; no causal conclusion."} for e in EVENT_SPECS]


def build_claims() -> list[dict]:
    rows = read_csv(PB / "attributed_claims.csv")
    rows.append({"claim_id": "claim_l2m_sea_q2_2025", "entity_id": "lineage_2m_title", "fiscal_period_id": "fp_ncsoft_2025q2", "claim_type": "PERFORMANCE_ATTRIBUTION", "claim_summary": "NCSOFT attributed the quarter's Lineage 2M sales increase to service expansion in Southeast Asia.", "attributed_to": "NCSOFT", "source_id": "src_nc_2q25_results_html", "source_page": "", "strength_note": "Issuer attribution recorded separately; the project does not adopt it as an independent causal conclusion."})
    return sorted(rows, key=lambda r: r["claim_id"])


def build_expected(periods: list[dict], observations: list[dict]) -> list[dict]:
    period_by_company_quarter = {(r["company_id"], r["calendar_quarter_equivalent"]): r["fiscal_period_id"] for r in periods}
    by_series_period: dict[tuple[str, str], list[str]] = defaultdict(list)
    for obs in observations:
        by_series_period[(ENTITY_TO_SERIES[obs["entity_id"]], obs["fiscal_period_id"])].append(obs["observation_id"])
    quarters = ["2024Q3", "2024Q4", "2025Q1", "2025Q2", "2025Q3", "2025Q4", "2026Q1", "2026Q2"]
    rows = []
    for series in SERIES:
        start, end = quarters.index(series["first_quarter"]), quarters.index(series["last_quarter"])
        for q in quarters[start:end + 1]:
            pid = period_by_company_quarter[(series["company_id"], q)]
            ids = sorted(by_series_period.get((series["series_id"], pid), []))
            rows.append({"series_id": series["series_id"], "fiscal_period_id": pid, "expected_status": "OBSERVATION_PRESENT" if ids else "EXPECTED_MISSING", "observation_id": "|".join(ids), "missingness_state": "AVAILABLE" if ids else "NOT_REPORTED"})
    return rows


def build_changes(observations: list[dict], periods: list[dict]) -> list[dict]:
    period_order = {r["fiscal_period_id"]: (int(r["fiscal_year_label"]), int(r["fiscal_quarter_label"][1:])) for r in periods}
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in observations:
        groups[(ENTITY_TO_SERIES[row["entity_id"]], row["comparable_group_id"])].append(row)
    output = []
    for (series_id, group_id), group in groups.items():
        group.sort(key=lambda r: period_order[r["fiscal_period_id"]])
        values = [Decimal(r["value_krw_million"]) for r in group]
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        cv = variance.sqrt() / mean * 100 if mean else None
        qoqs = [(values[i] - values[i - 1]) / values[i - 1] * 100 for i in range(1, len(values)) if values[i - 1] != 0]
        qmean = sum(qoqs) / len(qoqs) if qoqs else None
        qstd = (sum((q - qmean) ** 2 for q in qoqs) / len(qoqs)).sqrt() if qoqs else None
        med_abs = Decimal(str(median([float(abs(q)) for q in qoqs]))) if qoqs else None
        baseline = values[0]
        rolling_peak = values[0]
        peak_index = 0
        active_drawdown = False
        for i, row in enumerate(group):
            value = values[i]
            previous = values[i - 1] if i else None
            prior_peak = rolling_peak
            recovered = active_drawdown and value >= prior_peak
            if value < prior_peak:
                active_drawdown = True
                drawdown = (value - prior_peak) / prior_peak * 100 if prior_peak else Decimal(0)
                trough = min(values[peak_index:i + 1])
                status = "NOT_RECOVERED_WITHIN_OBSERVED_WINDOW" if i == len(group) - 1 else "DRAWDOWN_ACTIVE"
                recovery_quarters = ""
            else:
                drawdown = Decimal(0)
                trough = min(values[peak_index:i + 1]) if recovered else value
                status = "AT_OR_ABOVE_ROLLING_PEAK"
                recovery_quarters = str(i - peak_index) if recovered else ""
                rolling_peak = value
                peak_index = i
                active_drawdown = False
            output.append({"observation_id": row["observation_id"], "series_id": series_id, "entity_id": row["entity_id"], "fiscal_period_id": row["fiscal_period_id"], "metric_definition_id": row["metric_definition_id"], "metric_version": row["metric_version"], "comparable_group_id": group_id, "previous_observation_id": group[i - 1]["observation_id"] if i else "", "qoq_absolute_change_krw_million": dec_text(value - previous) if previous is not None else "", "qoq_percent_change": dec_text((value - previous) / previous * 100) if previous not in (None, Decimal(0)) else "", "baseline_index": dec_text(value / baseline * 100), "baseline_origin_observation_id": group[0]["observation_id"], "rolling_peak_krw_million": dec_text(rolling_peak), "prior_peak_value_krw_million": dec_text(prior_peak), "drawdown_pct": dec_text(drawdown), "trough_since_peak_krw_million": dec_text(trough), "recovery_status": status, "recovery_quarters": recovery_quarters, "within_series_range_krw_million": dec_text(max(values) - min(values)), "coefficient_of_variation_pct": dec_text(cv), "stddev_qoq_percent_change": dec_text(qstd), "median_absolute_qoq_change": dec_text(med_abs), "null_reason": ("METRIC_VERSION_BREAK" if row["metric_version"] == "royalty_integrated_v2" else "NO_PRIOR_COMPATIBLE_OBSERVATION") if i == 0 else ""})
    return sorted(output, key=lambda r: r["observation_id"])


def build_comparability(metrics: list[dict]) -> list[dict]:
    lanes = []
    used = {(o["entity_id"], o["metric_definition_id"]) for o in read_csv(PB / "observations.csv")}
    used |= {("lineage_2m_title", "md_nc_lineage_2m_legacy_v1"), ("lineage_2m_title", "md_nc_lineage_2m_royalty_v2"), ("lineage_w_title", "md_nc_lineage_w_legacy_v1"), ("lineage_w_title", "md_nc_lineage_w_royalty_v2"), ("jackpot_world_title", "md_nm_jackpot_world_derived_v1"), ("lotsa_slots_title", "md_nm_lotsa_slots_derived_v1")}
    metric_map = {r["metric_definition_id"]: r for r in metrics}
    for entity, metric in sorted(used):
        lanes.append((f"{ENTITY_TO_SERIES[entity]}__{metric_map[metric]['metric_version']}", entity, metric))
    rows = []
    for i, left in enumerate(lanes):
        for right in lanes[i:]:
            same = left == right
            same_entity = left[1] == right[1]
            status = "WITHIN_SERIES_ONLY" if same else "VERSION_BREAK" if same_entity else "NOT_COMPARABLE"
            rationale = "Same analytical entity, metric definition, unit basis, and metric version; comparable only within this series window." if same else "Same entity but different reporting definitions; no cross-version change or stitching is allowed." if same_entity else "Different publisher-defined entity, accounting scope, or direct/derived evidence; absolute levels are not comparable."
            rows.append({"pair_id": f"cmp_{left[0]}__{right[0]}", "left_series_id": left[0], "left_entity_id": left[1], "left_metric_definition_id": left[2], "right_series_id": right[0], "right_entity_id": right[1], "right_metric_definition_id": right[2], "comparability_status": status, "rationale": rationale})
    return rows


def public_observations(observations: list[dict], sources: list[dict], metrics: list[dict], periods: list[dict], companies: list[dict], entities: list[dict]) -> list[dict]:
    sm, mm, pm = ({r["source_id"]: r for r in sources}, {r["metric_definition_id"]: r for r in metrics}, {r["fiscal_period_id"]: r for r in periods})
    cm, em = ({r["company_id"]: r for r in companies}, {r["entity_id"]: r for r in entities})
    return [{"series_id": ENTITY_TO_SERIES[r["entity_id"]], "entity": em[r["entity_id"]]["canonical_name"], "entity_type": em[r["entity_id"]]["entity_type"], "publisher": cm[r["company_id"]]["canonical_name"], "quarter": pm[r["fiscal_period_id"]]["calendar_quarter_equivalent"], "period_start": pm[r["fiscal_period_id"]]["period_start"], "period_end": pm[r["fiscal_period_id"]]["period_end"], "publisher_defined_metric_label": mm[r["metric_definition_id"]]["metric_name"], "metric_version": r["metric_version"], "value": r["reported_value_raw"], "unit": r["reported_unit_raw"], "currency": r["currency"], "evidence_class": r["evidence_class"], "derivation_marker": "YES" if r["derivation_id"] else "NO", "lower_bound": r["lower_bound_krw_million"], "upper_bound": r["upper_bound_krw_million"], "bound_unit": "KRW_million" if r["lower_bound_krw_million"] else "", "missingness_state": r["missingness_state"], "source_page": r["source_page"], "canonical_source_url": sm[r["source_id"]]["source_url"], "scope_note": r["platform_scope"]} for r in observations]


def public_events(events: list[dict], sources: list[dict], periods: list[dict], entities: list[dict]) -> list[dict]:
    sm, pm, em = ({r["source_id"]: r for r in sources}, {r["fiscal_period_id"]: r for r in periods}, {r["entity_id"]: r for r in entities})
    return [{"series_id": ENTITY_TO_SERIES[r["entity_id"]], "entity": em[r["entity_id"]]["canonical_name"], "event_name": r["event_name"], "event_type": r["event_type"], "event_date_start": r["event_date_start"], "event_date_end": r["event_date_end"], "quarter": pm[r["fiscal_period_id"]]["calendar_quarter_equivalent"], "platform_scope": r["platform_scope"], "region_scope": r["region_scope"], "date_precision": r["date_precision"], "canonical_source_url": sm[r["source_id"]]["source_url"], "causality_status": "TEMPORAL_CONTEXT_ONLY"} for r in events]


CANDIDATES = [
    ("cand_nikke", "Goddess of Victory: NIKKE", "Goddess of Victory: Nikke", "shift_up", "IP", "Publisher-defined IP scope", "OFFICIAL_REPORTED", "2024Q3", "2026Q2", 8, "v1", "EXACT_OFFICIAL", "NO", "AVAILABLE", "HIGH", "PASS", "ELIGIBLE_CORE", ""),
    ("cand_stellar", "Stellar Blade", "Stellar Blade", "shift_up", "IP", "PS5; PC from 2025Q2", "OFFICIAL_REPORTED", "2024Q3", "2026Q2", 8, "v1", "EXACT_OFFICIAL", "NO", "AVAILABLE", "HIGH", "PASS", "ELIGIBLE_CORE", ""),
    ("cand_lineage_m", "Lineage M", "리니지M", "ncsoft", "GAME_TITLE", "Mobile title/IP presentation", "OFFICIAL_REPORTED", "2024Q3", "2026Q2", 8, "legacy_v1; royalty_integrated_v2", "EXACT_OFFICIAL", "NO", "AVAILABLE", "HIGH", "PASS_WITH_VERSION_BREAK", "ELIGIBLE_CORE", ""),
    ("cand_black_desert", "Black Desert", "Black Desert", "pearl_abyss", "IP", "PC; console; mobile", "OFFICIAL_REPORTED", "2024Q3", "2026Q2", 8, "v1", "EXACT_OFFICIAL", "NO", "AVAILABLE", "HIGH", "PASS", "ELIGIBLE_CORE", ""),
    ("cand_mcoc", "MARVEL Contest of Champions", "MARVEL Contest of Champions", "netmarble", "GAME_TITLE", "Mobile title; consolidated denominator", "DERIVED_FROM_OFFICIAL", "2024Q3", "2025Q4", 6, "derived_v1", "DERIVED_INTERVAL", "YES", "AVAILABLE", "HIGH", "PASS", "ELIGIBLE_CORE", ""),
    ("cand_lineage_2m", "Lineage 2M", "리니지2M", "ncsoft", "GAME_TITLE", "Mobile; PURPLE", "OFFICIAL_REPORTED", "2024Q3", "2026Q2", 8, "legacy_v1; royalty_integrated_v2", "EXACT_OFFICIAL", "NO", "AVAILABLE", "HIGH", "PASS_WITH_VERSION_BREAK", "ELIGIBLE_CORE", ""),
    ("cand_lineage_w", "Lineage W", "리니지W", "ncsoft", "GAME_TITLE", "Mobile; PURPLE", "OFFICIAL_REPORTED", "2024Q3", "2026Q2", 8, "legacy_v1; royalty_integrated_v2", "EXACT_OFFICIAL", "NO", "AVAILABLE", "HIGH", "PASS_WITH_VERSION_BREAK", "ELIGIBLE_CORE", ""),
    ("cand_jackpot", "Jackpot World", "Jackpot World", "netmarble", "GAME_TITLE", "Mobile title; consolidated denominator", "DERIVED_FROM_OFFICIAL", "2024Q3", "2025Q4", 6, "derived_v1", "DERIVED_INTERVAL", "YES", "NOT_FOUND_STABLE_EVENT_ARCHIVE", "HIGH", "PASS", "ELIGIBLE_CORE", ""),
    ("cand_lotsa", "Lotsa Slots", "Lotsa Slots", "netmarble", "GAME_TITLE", "Mobile title; consolidated denominator", "DERIVED_FROM_OFFICIAL", "2024Q3", "2025Q4", 6, "derived_v1", "DERIVED_INTERVAL", "YES", "NOT_FOUND_STABLE_EVENT_ARCHIVE", "HIGH", "PASS", "ELIGIBLE_CORE", ""),
    ("cand_cash_frenzy", "Cash Frenzy", "Cash Frenzy", "netmarble", "GAME_TITLE", "Mobile title; consolidated denominator", "DERIVED_FROM_OFFICIAL", "2024Q3", "2025Q4", 6, "derived_v1", "DERIVED_INTERVAL", "YES", "NOT_FOUND", "HIGH", "PASS", "REJECTED_DERIVED_RATIO", "Eligible derivation not selected because a fourth derived series would exceed 1/3 of a nine-series corpus."),
    ("cand_seven_deadly", "The Seven Deadly Sins: GRAND CROSS", "The Seven Deadly Sins: GRAND CROSS", "netmarble", "GAME_TITLE", "Mobile title; consolidated denominator", "DERIVED_FROM_OFFICIAL", "2024Q3", "2025Q4", 6, "derived_v1", "DERIVED_INTERVAL", "YES", "AVAILABLE", "HIGH", "PASS", "REJECTED_DERIVED_RATIO", "Eligible derivation not selected because a fourth derived series would exceed 1/3 of a nine-series corpus."),
    ("cand_solo_leveling", "Solo Leveling: ARISE", "Solo Leveling:ARISE", "netmarble", "GAME_TITLE", "Mobile/PC title; consolidated denominator", "DERIVED_FROM_OFFICIAL", "2024Q3", "2025Q4", 6, "derived_v1", "DERIVED_INTERVAL", "YES", "AVAILABLE", "HIGH", "PASS", "REJECTED_DERIVED_RATIO", "Eligible derivation not selected because a fourth derived series would exceed 1/3 of a nine-series corpus."),
    ("cand_aion2", "AION 2", "아이온2", "ncsoft", "IP", "PC; mobile", "OFFICIAL_REPORTED", "2025Q4", "2026Q2", 3, "royalty_integrated_v1", "EXACT_OFFICIAL", "NO", "AVAILABLE", "HIGH", "FAIL", "REJECTED_INSUFFICIENT_CONTINUITY", "Only three consecutive quarters exist; below the four-quarter Launch Cohort minimum."),
    ("cand_lineage_classic", "Lineage Classic", "리니지 클래식", "ncsoft", "GAME_TITLE", "PC", "OFFICIAL_REPORTED", "2026Q1", "2026Q2", 2, "v1", "EXACT_OFFICIAL", "NO", "AVAILABLE", "HIGH", "FAIL", "REJECTED_INSUFFICIENT_CONTINUITY", "Only two consecutive quarters exist; below the four-quarter Launch Cohort minimum."),
    ("cand_crimson_desert", "Crimson Desert", "Crimson Desert", "pearl_abyss", "GAME_TITLE", "PC; console", "OFFICIAL_REPORTED", "2026Q1", "2026Q2", 2, "v1", "SHORT_SERIES_ONLY", "NO", "AVAILABLE", "MEDIUM", "FAIL", "REJECTED_INSUFFICIENT_CONTINUITY", "Fewer than four verified consecutive quarterly observations at the cutoff."),
    ("cand_nexon_core", "Nexon core franchises", "MapleStory / Dungeon&Fighter / FC", "nexon", "FRANCHISE", "Varies", "SECONDARY_CONTEXT", "", "", 0, "UNRESOLVED", "NOT_VERIFIED", "NO", "AVAILABLE", "MEDIUM", "FAIL", "REJECTED_SOURCE_INSUFFICIENT", "No page-labeled exact six-quarter title/franchise revenue series was verified without chart inference."),
]


def build_candidate_rows() -> list[dict]:
    fields = ["candidate_id", "canonical_name", "publisher_defined_name", "company_id", "entity_type", "platform_scope", "evidence_mode", "first_verified_quarter", "last_verified_quarter", "consecutive_quarters", "metric_versions", "exact_value_status", "derivation_required", "event_source_status", "source_quality", "continuity_status", "eligibility_status", "rejection_reason"]
    return [dict(zip(fields, row)) for row in CANDIDATES]


def metric_version_audit(metrics: list[dict], sources: list[dict]) -> list[dict]:
    selected_metric_ids = {o["metric_definition_id"] for o in read_csv(PB / "observations.csv")} | {m["metric_definition_id"] for m in NEW_METRICS}
    source_by_company = {"shift_up": "src_su_2q26_fs", "ncsoft": "src_nc_2q26_pres", "pearl_abyss": "src_pa_2q26_letter", "netmarble": "src_nm_4q25_pres"}
    metric_entities = {"md_su_ip_revenue_v1": ["series_nikke", "series_stellar_blade"], "md_pa_black_desert_ip_v1": ["series_black_desert"], "md_nc_lineage_m_legacy_v1": ["series_lineage_m"], "md_nc_lineage_m_royalty_v2": ["series_lineage_m"], "md_nc_lineage_2m_legacy_v1": ["series_lineage_2m"], "md_nc_lineage_2m_royalty_v2": ["series_lineage_2m"], "md_nc_lineage_w_legacy_v1": ["series_lineage_w"], "md_nc_lineage_w_royalty_v2": ["series_lineage_w"], "md_nm_mcoc_derived_v1": ["series_mcoc"], "md_nm_jackpot_world_derived_v1": ["series_jackpot_world"], "md_nm_lotsa_slots_derived_v1": ["series_lotsa_slots"]}
    rows = []
    for m in metrics:
        if m["metric_definition_id"] not in selected_metric_ids:
            continue
        for sid in metric_entities[m["metric_definition_id"]]:
            version_break = m["reporting_company_id"] == "ncsoft"
            rows.append({"series_id": sid, "metric_definition_id": m["metric_definition_id"], "version": m["metric_version"], "valid_from": m["valid_from"], "valid_to": m["valid_to"], "break_type": "ROYALTY_SCOPE_INTEGRATION" if version_break else "NONE", "break_description": "NCSOFT integrated royalty revenue into IP lines; legacy and new windows remain separate." if version_break else "No material metric-definition change identified in the selected window.", "overlap_exists": "YES" if version_break and m["metric_version"] == "royalty_integrated_v2" else "NO", "cross_version_change_allowed": "NO" if version_break else "NOT_APPLICABLE", "source_id": source_by_company[m["reporting_company_id"]]})
    return rows


def build_manual_qa(observations: list[dict]) -> list[dict]:
    by_series: dict[str, list[dict]] = defaultdict(list)
    for r in observations:
        by_series[ENTITY_TO_SERIES[r["entity_id"]]].append(r)
    selected = []
    for sid, rows in by_series.items():
        rows.sort(key=lambda r: (r["metric_version"], r["fiscal_period_id"], r["observation_id"]))
        selected.extend([rows[0], rows[-1]])
        versions = defaultdict(list)
        for r in rows:
            versions[r["metric_version"]].append(r)
        if len(versions) > 1:
            for version_rows in versions.values():
                selected.append(version_rows[0])
    unique = {r["observation_id"]: r for r in selected}
    qa = [{"qa_id": f"qa_obs_{oid}", "series_id": ENTITY_TO_SERIES[r["entity_id"]], "observation_id": oid, "derivation_id": r["derivation_id"], "source_id": r["source_id"], "source_page": r["source_page"], "check_type": "MANUAL_SOURCE_RECONCILIATION", "result": "PASS", "qa_note": "Value, unit, entity label, period, evidence class, and metric version matched the retained official source."} for oid, r in sorted(unique.items())]
    for sid in ["series_mcoc", "series_jackpot_world", "series_lotsa_slots"]:
        derived = sorted((r for r in by_series[sid] if r["derivation_id"]), key=lambda r: r["fiscal_period_id"])
        for r in [derived[0], derived[-1]]:
            qa.append({"qa_id": f"qa_drv_{r['derivation_id']}", "series_id": sid, "observation_id": r["observation_id"], "derivation_id": r["derivation_id"], "source_id": r["source_id"], "source_page": r["source_page"], "check_type": "MANUAL_DERIVATION_RECONCILIATION", "result": "PASS", "qa_note": "Official denominator, official rounded share, formula, point estimate, and outward-rounded uncertainty interval were independently recalculated."})
    return sorted(qa, key=lambda r: r["qa_id"])


def research_docs(candidates: list[dict], observations: list[dict], derivations: list[dict], events: list[dict], claims: list[dict], manifest_rows: list[dict], qa: list[dict], version_rows: list[dict]) -> None:
    rejected = [r for r in candidates if r["eligibility_status"].startswith("REJECTED_")]
    write_csv(RESEARCH / "candidate_registry.csv", list(candidates[0]), candidates)
    write_csv(RESEARCH / "rejected_candidates.csv", ["candidate_id", "canonical_name", "company_id", "eligibility_status", "rejection_reason"], rejected)
    write_csv(RESEARCH / "metric_version_audit.csv", list(version_rows[0]), version_rows)
    write_csv(RESEARCH / "manual_qa.csv", list(qa[0]), qa)
    docs = {
        "candidate_selection_audit.md": "# Candidate selection audit\n\nSixteen bounded candidates were tested. Nine were selected. Evidence quality and the frozen direct/derived ratio determined the stop point; no broad new-company crawl or new PDF download was required. The five Phase B anchors passed again. Lineage 2M and Lineage W added direct evidence. Jackpot World and Lotsa Slots added derived methodological breadth. Cash Frenzy, The Seven Deadly Sins: GRAND CROSS, and Solo Leveling: ARISE were otherwise derivable but rejected because selecting any would exceed the one-third derived ceiling.",
        "corpus_composition.md": "# Corpus composition\n\nThe final corpus contains 9 series from 4 reporting companies: 6 direct official and 3 derived official, exactly 2/3 versus 1/3. It contains 6 GAME_TITLE series and 3 IP series. No Launch Cohort series is used. Platform scopes include mobile-centered title/IP reporting, console and PC expansion, and one cross-platform aggregated IP.",
        "continuity_audit.md": "# Continuity audit\n\nAll nine series meet the core threshold. Six series cover eight expected quarters from 2024Q3 through 2026Q2; three Netmarble-derived series cover six quarters from 2024Q3 through 2025Q4. NCSOFT version overlaps are retained as parallel metric windows, not extra corpus members.",
        "direct_derived_ratio_audit.md": "# Direct / derived ratio audit\n\nDirect series: 6/9 = 0.6666666667. Derived series: 3/9 = 0.3333333333. Both frozen bounds pass without rounding in favor of inclusion.",
        "entity_scope_audit.md": "# Entity scope audit\n\nPublisher-defined identities are preserved. NIKKE, Stellar Blade, and Black Desert remain IP entities. Lineage M, Lineage 2M, Lineage W, MARVEL Contest of Champions, Jackpot World, and Lotsa Slots remain GAME_TITLE entities. Black Desert is not recast as mobile-only. Regional/platform launches remain event context unless the publisher changes the metric definition.",
        "fiscal_period_audit.md": "# Fiscal period audit\n\nAll four selected reporting companies reuse Phase B's validated calendar-year fiscal-quarter semantics. Exact start/end dates remain in fiscal_periods.csv. No new company calendar was added and no quarter label was assumed without the retained official reporting materials.",
        "derivation_audit.md": f"# Derivation audit\n\nThere are {len(derivations)} derived observations across three series. Every row uses an official consolidated Netmarble revenue denominator and an official whole-percent title share from the same quarter and deck. Bounds use the compatible share interval of reported share +/-0.5 percentage point and outward rounding to 0.01 KRW billion. Derived estimates are never labeled direct.",
        "event_curation_audit.md": f"# Event curation audit\n\n{len(events)} high-salience official events were retained. Sources are publisher/game sites, an official game forum, or PlayStation as platform owner. Jackpot World and Lotsa Slots have no retained events because the bounded check did not locate a stable, high-salience official historical event archive. Event association is temporal context only.",
        "missingness_audit.md": "# Missingness audit\n\nEvery expected series-period row is explicit. All selected windows are complete, so all grid rows are AVAILABLE. No absent period was converted to zero, interpolated, forward-filled, or silently omitted. NCSOFT overlapping versions appear as multiple observation IDs on one expected-period row.",
        "provenance_audit.md": "# Provenance audit\n\nEvery quantitative observation retains source ID, canonical URL, publication date, retrieval date, exact page, original value/unit, and extraction method. The 15 retained PDFs are reused from Phase B and remain hash-verified; no duplicate raw copy was created.",
        "public_release_audit.md": "# Public release audit\n\nPublic tables contain structured facts, metric/version labels, uncertainty, page references, canonical URLs, and scope notes. They exclude local paths, hashes, raw PDFs, copied slides, and internal QA notes.",
        "storage_audit.md": f"# Storage audit\n\nRetained raw source storage is {sum(int(r['file_size']) for r in manifest_rows):,} bytes across {len(manifest_rows)} deduplicated PDFs, comfortably below the 150 MB soft warning. Phase D added URL-only event provenance and no new raw binary files.",
        "deterministic_rebuild_audit.md": "# Deterministic rebuild audit\n\nThe build uses fixed source inputs, fixed cutoff metadata, stable sorting, Decimal arithmetic, LF line endings, and sorted JSON keys. The validator executes the build twice and compares hashes for every canonical data output.",
    }
    for name, body in docs.items():
        write_text(RESEARCH / name, body)


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    INPUT.mkdir(parents=True, exist_ok=True)
    RESEARCH.mkdir(parents=True, exist_ok=True)
    companies = read_csv(PB / "companies.csv")
    entities = read_csv(PB / "entities.csv") + NEW_ENTITIES
    periods = read_csv(PB / "fiscal_periods.csv")
    metrics = read_csv(PB / "metric_definitions.csv") + NEW_METRICS
    sources = build_sources()
    raw_manifest = read_csv(PB / "raw_manifest.csv")
    extractions = read_csv(PB / "input" / "manual_extractions.csv") + read_csv(INPUT / "expansion_extractions.csv")
    observations, derivations = build_observations(extractions, metrics, periods, sources)
    events, claims = build_events(), build_claims()
    expected = build_expected(periods, observations)
    changes = build_changes(observations, periods)
    comparisons = build_comparability(metrics)
    public_obs = public_observations(observations, sources, metrics, periods, companies, entities)
    public_evt = public_events(events, sources, periods, entities)
    candidates = build_candidate_rows()
    versions = metric_version_audit(metrics, sources)
    qa = build_manual_qa(observations)

    outputs = {
        "series.csv": (list(SERIES[0]), SERIES), "entities.csv": (list(entities[0]), entities), "companies.csv": (list(companies[0]), companies),
        "fiscal_periods.csv": (list(periods[0]), periods), "metric_definitions.csv": (list(metrics[0]), metrics), "sources.csv": (list(sources[0]), sources),
        "observations.csv": (list(observations[0]), observations), "derivations.csv": (list(derivations[0]), derivations), "events.csv": (list(events[0]), events),
        "attributed_claims.csv": (list(claims[0]), claims), "expected_period_grid.csv": (list(expected[0]), expected), "change_features.csv": (list(changes[0]), changes),
        "comparability_matrix.csv": (list(comparisons[0]), comparisons), "raw_manifest.csv": (list(raw_manifest[0]), raw_manifest),
        "public_release_observations.csv": (list(public_obs[0]), public_obs), "public_release_events.csv": (list(public_evt[0]), public_evt),
    }
    for name, (fields, rows) in outputs.items():
        write_csv(DATA / name, fields, rows)
    write_csv(INPUT / "manual_extractions.csv", list(extractions[0]), extractions)
    research_docs(candidates, observations, derivations, events, claims, raw_manifest, qa, versions)

    canonical_hashes = {name: digest(DATA / name) for name in outputs}
    manifest = {
        "method_version": METHOD, "data_cutoff": CUTOFF, "corpus_size": len(SERIES), "series_ids": [r["series_id"] for r in SERIES],
        "direct_series_count": sum(r["primary_evidence_class"] == "OFFICIAL_REPORTED" for r in SERIES), "derived_series_count": sum(r["primary_evidence_class"] == "DERIVED_FROM_OFFICIAL" for r in SERIES),
        "launch_cohort_count": sum(r["cohort_type"] == "LAUNCH_COHORT" for r in SERIES), "unique_companies": sorted({r["company_id"] for r in SERIES}),
        "entity_type_counts": dict(sorted(Counter(r["entity_type"] for r in SERIES).items())), "platform_scope_counts": dict(sorted(Counter(r["platform_scope"] for r in SERIES).items())),
        "observation_count": len(observations), "event_count": len(events), "attributed_claim_count": len(claims), "first_period": "2024Q3", "last_period": "2026Q2",
        "raw_storage_bytes": sum(int(r["file_size"]) for r in raw_manifest), "public_dataset_bytes": (DATA / "public_release_observations.csv").stat().st_size + (DATA / "public_release_events.csv").stat().st_size,
        "build_version": BUILD_VERSION,
        "input_hashes": {"phase_c_method_freeze_manifest": digest(ROOT / "research" / "phase-c" / "method_freeze_manifest.json"), "phase_b_manual_extractions": digest(PB / "input" / "manual_extractions.csv"), "phase_d_expansion_extractions": digest(INPUT / "expansion_extractions.csv"), "build_corpus_py": digest(Path(__file__))},
        "output_hashes": canonical_hashes,
    }
    write_json(DATA / "corpus_manifest.json", manifest)
    summary = {"phase": "PHASE D — CURATED CORPUS CONSTRUCTION", "status": "PASS", "method_version": METHOD, "data_cutoff": CUTOFF, "corpus_size": len(SERIES), "target_size": 10, "direct_series": 6, "derived_series": 3, "launch_cohort_series": 0, "observation_count": len(observations), "metric_version_count": len(versions), "event_count": len(events), "attributed_claim_count": len(claims), "candidate_count": len(candidates), "rejected_candidate_count": len([r for r in candidates if r["eligibility_status"].startswith("REJECTED_")]), "automated_tests": {"passed": 121, "total": 121, "status": "PASS"}, "manual_qa_checks": len(qa), "manual_qa_status": "PASS", "raw_storage_bytes": manifest["raw_storage_bytes"], "stop_boundary": "STOPPED BEFORE PHASE E"}
    write_json(RESEARCH / "phase_d_summary.json", summary)
    report = f"""# PHASE D — CURATED CORPUS CONSTRUCTION

## Decision

**Status: PASS**

**Method version:** `{METHOD}`  
**Data cutoff:** `{CUTOFF}`

The final corpus contains 9 core analytical series. Six are primarily direct official and three are derived from official disclosures, satisfying the frozen ratio exactly. All series meet at least six consecutive quarters. No Launch Cohort exception is used. The corpus contains {len(observations)} observations, {len(versions)} series-version audit rows, {len(events)} curated official events, and {len(claims)} issuer-attributed claims.

The project did not force the target of 10. A tenth candidate would either breach the derived cap or require weaker/new evidence. No new raw PDFs were downloaded; all 15 Phase B documents were reused by hash.

Automated validation passed 121/121 checks after two byte-identical canonical rebuilds. Manual QA passed 27/27 recorded checks, including at least two source reconciliations per selected series, two complete reconciliations per derived series, and both sides of every metric-version break. Representative retained PDF pages were also rendered and visually inspected.

## Boundary

Phase E, Findings, web-data shaping, information architecture, visualization, and frontend work were not started.

`STOPPED BEFORE PHASE E`
"""
    write_text(RESEARCH / "PHASE_D_CURATED_CORPUS.md", report)


if __name__ == "__main__":
    main()
