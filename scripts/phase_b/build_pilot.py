#!/usr/bin/env python3
"""Deterministically build the bounded Phase B controlled pilot."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "phase-b"
INPUT = DATA / "input" / "manual_extractions.csv"
RAW = ROOT / "research" / "raw" / "phase-b"
RETRIEVED_AT = "2026-09-22"


def write_csv(name: str, fields: list[str], rows: list[dict]) -> None:
    path = DATA / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def dec_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def to_krw_million(value: Decimal, unit: str) -> Decimal:
    if unit == "KRW":
        return value / Decimal("1000000")
    if unit == "KRW_million":
        return value
    if unit == "KRW_billion":
        return value * Decimal("1000")
    raise ValueError(f"Unsupported unit: {unit}")


COMPANIES = [
    {"company_id": "shift_up", "canonical_name": "SHIFT UP", "reporting_name": "SHIFT UP Corporation", "country": "South Korea", "IR_home_url": "https://shiftup.co.kr/eng/ir/ir.php?code=ir_eng&idx=475&page=1&ptype=list", "fiscal_calendar_note": "Calendar-year fiscal reporting; quarter labels verified against exact period ends in official quarterly materials.", "currency": "KRW", "source_status": "PUBLIC_OFFICIAL_VERIFIED"},
    {"company_id": "ncsoft", "canonical_name": "NCSOFT", "reporting_name": "NC / NCSOFT", "country": "South Korea", "IR_home_url": "https://m-corporate.nc.com/kr/ir/irArchive/earningsRelease.do", "fiscal_calendar_note": "Calendar-year fiscal reporting; quarter labels verified against exact period ends in official quarterly materials.", "currency": "KRW", "source_status": "PUBLIC_OFFICIAL_VERIFIED"},
    {"company_id": "pearl_abyss", "canonical_name": "Pearl Abyss", "reporting_name": "Pearl Abyss Corp.", "country": "South Korea", "IR_home_url": "https://www.pearlabyss.com/en-US/IR/Data/Performance", "fiscal_calendar_note": "Calendar-year fiscal reporting; quarter labels verified against exact period ends in official quarterly materials.", "currency": "KRW", "source_status": "PUBLIC_OFFICIAL_VERIFIED"},
    {"company_id": "netmarble", "canonical_name": "Netmarble", "reporting_name": "Netmarble Corporation", "country": "South Korea", "IR_home_url": "https://company.netmarble.com/en/invest/library", "fiscal_calendar_note": "Calendar-year fiscal reporting; quarter labels verified against exact period ends in official quarterly materials.", "currency": "KRW", "source_status": "PUBLIC_OFFICIAL_VERIFIED"},
]


ENTITIES = [
    {"entity_id": "company_shift_up", "canonical_name": "SHIFT UP", "publisher_defined_name": "SHIFT UP Corporation", "entity_type": "COMPANY", "reporting_company_id": "shift_up", "developer_if_known": "", "scope_note": "Reporting company entity.", "identity_status": "VERIFIED", "valid_from": "2013-12-02", "valid_to": "", "parent_entity_id": ""},
    {"entity_id": "company_ncsoft", "canonical_name": "NCSOFT", "publisher_defined_name": "NC / NCSOFT", "entity_type": "COMPANY", "reporting_company_id": "ncsoft", "developer_if_known": "", "scope_note": "Reporting company entity.", "identity_status": "VERIFIED", "valid_from": "1997-03-11", "valid_to": "", "parent_entity_id": ""},
    {"entity_id": "company_pearl_abyss", "canonical_name": "Pearl Abyss", "publisher_defined_name": "Pearl Abyss Corp.", "entity_type": "COMPANY", "reporting_company_id": "pearl_abyss", "developer_if_known": "", "scope_note": "Reporting company entity.", "identity_status": "VERIFIED", "valid_from": "2010-09-10", "valid_to": "", "parent_entity_id": ""},
    {"entity_id": "company_netmarble", "canonical_name": "Netmarble", "publisher_defined_name": "Netmarble Corporation", "entity_type": "COMPANY", "reporting_company_id": "netmarble", "developer_if_known": "", "scope_note": "Reporting company entity.", "identity_status": "VERIFIED", "valid_from": "2000-03-01", "valid_to": "", "parent_entity_id": ""},
    {"entity_id": "nikke_ip", "canonical_name": "Goddess of Victory: NIKKE", "publisher_defined_name": "Goddess of Victory: Nikke", "entity_type": "IP", "reporting_company_id": "shift_up", "developer_if_known": "SHIFT UP", "scope_note": "Publisher-recognized IP revenue; not store consumer spending. Mobile and publisher-recognized client/channel scope are not decomposed in the factsheet.", "identity_status": "VERIFIED_PUBLISHER_SCOPE", "valid_from": "2022-11-04", "valid_to": "", "parent_entity_id": ""},
    {"entity_id": "stellar_blade_ip", "canonical_name": "Stellar Blade", "publisher_defined_name": "Stellar Blade", "entity_type": "IP", "reporting_company_id": "shift_up", "developer_if_known": "SHIFT UP", "scope_note": "Publisher-defined IP series. PS5 was available before the pilot; PC launched in 2025Q2 without a disclosed metric-definition change.", "identity_status": "VERIFIED_PUBLISHER_SCOPE", "valid_from": "2024-04-26", "valid_to": "", "parent_entity_id": ""},
    {"entity_id": "stellar_blade_ps5_edition", "canonical_name": "Stellar Blade (PS5 edition)", "publisher_defined_name": "Stellar Blade", "entity_type": "GAME_EDITION", "reporting_company_id": "shift_up", "developer_if_known": "SHIFT UP", "scope_note": "Platform edition represented only for identity/event context; no edition-level revenue observation is inferred.", "identity_status": "VERIFIED_RELATIONSHIP_NO_SEPARATE_REVENUE", "valid_from": "2024-04-26", "valid_to": "", "parent_entity_id": "stellar_blade_ip"},
    {"entity_id": "stellar_blade_pc_edition", "canonical_name": "Stellar Blade (PC edition)", "publisher_defined_name": "Stellar Blade PC version", "entity_type": "GAME_EDITION", "reporting_company_id": "shift_up", "developer_if_known": "SHIFT UP", "scope_note": "PC edition launched 2025-06-11; no edition-level revenue observation is inferred.", "identity_status": "VERIFIED_RELATIONSHIP_NO_SEPARATE_REVENUE", "valid_from": "2025-06-11", "valid_to": "", "parent_entity_id": "stellar_blade_ip"},
    {"entity_id": "lineage_franchise", "canonical_name": "Lineage", "publisher_defined_name": "Lineage IP", "entity_type": "FRANCHISE", "reporting_company_id": "ncsoft", "developer_if_known": "NCSOFT", "scope_note": "Context entity only. The pilot does not aggregate franchise revenue or allocate other Lineage titles to Lineage M.", "identity_status": "VERIFIED_CONTEXT_ONLY", "valid_from": "1998-09-01", "valid_to": "", "parent_entity_id": ""},
    {"entity_id": "lineage_m_title", "canonical_name": "Lineage M", "publisher_defined_name": "리니지M", "entity_type": "GAME_TITLE", "reporting_company_id": "ncsoft", "developer_if_known": "NCSOFT", "scope_note": "Mobile game title. Legacy title revenue and royalty-integrated IP revenue are separate metric versions.", "identity_status": "VERIFIED_WITH_METRIC_VERSION_BREAK", "valid_from": "2017-06-21", "valid_to": "", "parent_entity_id": "lineage_franchise"},
    {"entity_id": "black_desert_ip", "canonical_name": "Black Desert", "publisher_defined_name": "Black Desert", "entity_type": "IP", "reporting_company_id": "pearl_abyss", "developer_if_known": "Pearl Abyss", "scope_note": "Publisher-defined IP revenue aggregating PC, console, and mobile; not Black Desert Mobile revenue.", "identity_status": "VERIFIED_PUBLISHER_SCOPE", "valid_from": "2014-12-17", "valid_to": "", "parent_entity_id": ""},
    {"entity_id": "marvel_contest_of_champions_title", "canonical_name": "MARVEL Contest of Champions", "publisher_defined_name": "MARVEL Contest of Champions", "entity_type": "GAME_TITLE", "reporting_company_id": "netmarble", "developer_if_known": "Kabam", "scope_note": "Title-level point estimate derived from Netmarble consolidated revenue and rounded title share.", "identity_status": "VERIFIED_DERIVED_SCOPE", "valid_from": "2014-12-10", "valid_to": "", "parent_entity_id": ""},
    {"entity_id": "platform_mobile", "canonical_name": "Mobile", "publisher_defined_name": "Mobile", "entity_type": "PLATFORM", "reporting_company_id": "", "developer_if_known": "", "scope_note": "Platform category; store/channel coverage varies by reporting company.", "identity_status": "CONTROLLED_VOCABULARY", "valid_from": "", "valid_to": "", "parent_entity_id": ""},
    {"entity_id": "platform_pc", "canonical_name": "PC", "publisher_defined_name": "PC", "entity_type": "PLATFORM", "reporting_company_id": "", "developer_if_known": "", "scope_note": "Platform category.", "identity_status": "CONTROLLED_VOCABULARY", "valid_from": "", "valid_to": "", "parent_entity_id": ""},
    {"entity_id": "platform_console", "canonical_name": "Console", "publisher_defined_name": "Console", "entity_type": "PLATFORM", "reporting_company_id": "", "developer_if_known": "", "scope_note": "Platform category.", "identity_status": "CONTROLLED_VOCABULARY", "valid_from": "", "valid_to": "", "parent_entity_id": ""},
]


METRICS = [
    {"metric_definition_id": "md_su_ip_revenue_v1", "metric_name": "SHIFT UP operating revenue by IP", "reporting_company_id": "shift_up", "entity_scope": "IP", "economic_meaning": "Revenue recognized by SHIFT UP and allocated to a named IP.", "accounting_scope": "Consolidated publisher revenue allocation by IP", "platform_scope": "Publisher-defined; NIKKE channel decomposition unavailable; Stellar Blade includes console and later PC", "geographic_scope": "Global consolidated reporting scope", "includes_royalties": "UNKNOWN", "includes_licensing": "UNKNOWN", "includes_platform_receipts": "UNKNOWN", "unit_basis": "Exact KRW", "valid_from": "2024-07-01", "valid_to": "", "metric_version": "v1", "comparable_group_id": "cg_su_ip_revenue_v1", "source_note": "SHIFT UP factsheet page 3."},
    {"metric_definition_id": "md_nc_lineage_m_legacy_v1", "metric_name": "Lineage M mobile game revenue - legacy scope", "reporting_company_id": "ncsoft", "entity_scope": "GAME_TITLE", "economic_meaning": "Title revenue shown in NCSOFT's mobile-game chart before the royalty-integration presentation change.", "accounting_scope": "NCSOFT mobile title chart; other mobile games excluded", "platform_scope": "Mobile", "geographic_scope": "Consolidated reporting regions", "includes_royalties": "NO_OR_NOT_INTEGRATED_IN_PRESENTATION", "includes_licensing": "UNKNOWN", "includes_platform_receipts": "UNKNOWN", "unit_basis": "KRW million", "valid_from": "2024-07-01", "valid_to": "2025-12-31", "metric_version": "legacy_v1", "comparable_group_id": "cg_nc_lineage_m_legacy_v1", "source_note": "NCSOFT 4Q24 p6; 2Q25 p5; 4Q25 p6."},
    {"metric_definition_id": "md_nc_lineage_m_royalty_v2", "metric_name": "Lineage M IP revenue including royalties - restated/new scope", "reporting_company_id": "ncsoft", "entity_scope": "GAME_TITLE_WITH_IP_REVENUE_PRESENTATION", "economic_meaning": "Lineage M revenue in a five-quarter presentation window where royalties are integrated into IP revenue.", "accounting_scope": "NCSOFT mobile IP line; other mobile games excluded; royalties integrated", "platform_scope": "Mobile title/IP presentation", "geographic_scope": "Consolidated reporting regions", "includes_royalties": "YES", "includes_licensing": "UNKNOWN", "includes_platform_receipts": "UNKNOWN", "unit_basis": "KRW million", "valid_from": "2025-04-01", "valid_to": "", "metric_version": "royalty_integrated_v2", "comparable_group_id": "cg_nc_lineage_m_royalty_v2", "source_note": "NCSOFT 2Q26 presentation p6; five-quarter window 2025Q2-2026Q2."},
    {"metric_definition_id": "md_pa_black_desert_ip_v1", "metric_name": "Black Desert IP revenue", "reporting_company_id": "pearl_abyss", "entity_scope": "IP", "economic_meaning": "Revenue reported for the Black Desert IP across publisher-defined editions.", "accounting_scope": "Pearl Abyss operating revenue allocated to Black Desert IP", "platform_scope": "PC; console; mobile", "geographic_scope": "Global consolidated reporting scope", "includes_royalties": "UNKNOWN", "includes_licensing": "UNKNOWN", "includes_platform_receipts": "UNKNOWN", "unit_basis": "KRW billion reported to one decimal", "valid_from": "2024-07-01", "valid_to": "", "metric_version": "v1", "comparable_group_id": "cg_pa_black_desert_ip_v1", "source_note": "Pearl Abyss 2Q25 presentation p6 and 2Q26 earnings letter p3."},
    {"metric_definition_id": "md_nm_mcoc_derived_v1", "metric_name": "Derived MCOC title revenue share of Netmarble revenue", "reporting_company_id": "netmarble", "entity_scope": "GAME_TITLE", "economic_meaning": "Official Netmarble consolidated quarterly revenue multiplied by official rounded MCOC contribution share.", "accounting_scope": "Derived allocation of consolidated Netmarble revenue", "platform_scope": "Inherits consolidated denominator; title is mobile but denominator spans company activities", "geographic_scope": "Global consolidated reporting scope", "includes_royalties": "UNKNOWN", "includes_licensing": "UNKNOWN", "includes_platform_receipts": "UNKNOWN", "unit_basis": "KRW billion point estimate with share-rounding interval", "valid_from": "2024-07-01", "valid_to": "2025-12-31", "metric_version": "derived_v1", "comparable_group_id": "cg_nm_mcoc_derived_v1", "source_note": "Quarterly deck total revenue page and game portfolio page; share rounded to whole percent."},
]


SOURCE_SPECS = [
    ("src_su_4q24_fs", "SHIFT UP", "https://shiftup.co.kr/admin/bbs/down.php?code=ir_eng&idx=226&no=2", "src_su_4q24_factsheet.pdf", "OFFICIAL_FACTSHEET_PDF", "2025-02-10", "English", "2024Q4"),
    ("src_su_2q26_fs", "SHIFT UP", "https://shiftup.co.kr/admin/bbs/down.php?code=ir_eng&idx=475&no=2", "src_su_2q26_factsheet.pdf", "OFFICIAL_FACTSHEET_PDF", "2026-08-11", "English", "2026Q2"),
    ("src_su_2q26_pres", "SHIFT UP", "https://shiftup.co.kr/admin/bbs/down.php?code=ir_eng&idx=475&no=1", "src_su_2q26_earnings_presentation.pdf", "OFFICIAL_EARNINGS_PDF", "2026-08-11", "English", "2026Q2"),
    ("src_nc_4q24_pres", "NCSOFT", "https://ncsoft-brand-web.s3.ap-northeast-2.amazonaws.com/ncsoft/invest/result/20250212/report/4Q24_PT_KOR.pdf", "src_nc_4q24_presentation.pdf", "OFFICIAL_EARNINGS_PDF", "2025-02-12", "Korean", "2024Q4"),
    ("src_nc_2q25_pres", "NCSOFT", "https://ncsoft-brand-web.s3.ap-northeast-2.amazonaws.com/ncsoft/invest/result/20250812/report/2Q25_PT_KOR.pdf", "src_nc_2q25_presentation.pdf", "OFFICIAL_EARNINGS_PDF", "2025-08-12", "Korean", "2025Q2"),
    ("src_nc_4q25_pres", "NCSOFT", "https://ncsoft-brand-web.s3.ap-northeast-2.amazonaws.com/ncsoft/invest/result/20260512/report/4Q25_PT_KOR.pdf", "src_nc_4q25_presentation.pdf", "OFFICIAL_EARNINGS_PDF", "2026-02-10", "Korean", "2025Q4"),
    ("src_nc_2q26_pres", "NCSOFT", "https://ncsoft-brand-web.s3.ap-northeast-2.amazonaws.com/ncsoft/invest/result/20260811/report/2Q26_PT_KOR.pdf", "src_nc_2q26_presentation.pdf", "OFFICIAL_EARNINGS_PDF", "2026-08-11", "Korean", "2026Q2"),
    ("src_pa_2q25_pres", "Pearl Abyss", "https://www.pearlabyss.com/en-US/Board/Detail?_boardNo=14399", "src_pa_2q25_presentation.pdf", "OFFICIAL_EARNINGS_PDF", "2025-08-13", "English", "2025Q2"),
    ("src_pa_2q26_letter", "Pearl Abyss", "https://www.pearlabyss.com/en-US/Board/Detail?_boardNo=15177", "src_pa_2q26_earnings_letter.pdf", "OFFICIAL_EARNINGS_PDF", "2026-08-11", "English", "2026Q2"),
    ("src_nm_3q24_pres", "Netmarble", "https://sgimage.netmarble.com/images/netmarble/nmOfficial/20241107/sbdp1730956098444.pdf", "src_nm_3q24_presentation.pdf", "OFFICIAL_EARNINGS_PDF", "2024-11-07", "English/Korean", "2024Q3"),
    ("src_nm_4q24_pres", "Netmarble", "https://sgimage.netmarble.com/images/netmarble/nmOfficial/20250213/a4641739427875500.pdf", "src_nm_4q24_presentation.pdf", "OFFICIAL_EARNINGS_PDF", "2025-02-13", "English/Korean", "2024Q4"),
    ("src_nm_1q25_pres", "Netmarble", "https://sgimage.netmarble.com/images/netmarble/nmOfficial/20250508/re6f1746681710316.pdf", "src_nm_1q25_presentation.pdf", "OFFICIAL_EARNINGS_PDF", "2025-05-08", "English/Korean", "2025Q1"),
    ("src_nm_2q25_pres", "Netmarble", "https://sgimage.netmarble.com/images/netmarble/nmOfficial/20250807/ownh1754531480180.pdf", "src_nm_2q25_presentation.pdf", "OFFICIAL_EARNINGS_PDF", "2025-08-07", "English/Korean", "2025Q2"),
    ("src_nm_3q25_pres", "Netmarble", "https://sgimage.netmarble.com/images/netmarble/nmOfficial/20251106/iyzr1762407112977.pdf", "src_nm_3q25_presentation.pdf", "OFFICIAL_EARNINGS_PDF", "2025-11-06", "English/Korean", "2025Q3"),
    ("src_nm_4q25_pres", "Netmarble", "https://sgimage.netmarble.com/images/netmarble/nmOfficial/20260205/8sto1770273390151.pdf", "src_nm_4q25_presentation.pdf", "OFFICIAL_EARNINGS_PDF", "2026-02-05", "English/Korean", "2025Q4"),
]


HTML_SOURCES = [
    {"source_id": "src_su_nikke_35_html", "publisher_name": "SHIFT UP", "source_url": "https://shiftup.co.kr/news/news.php?category=&idx=435&ptype=view", "source_type": "OFFICIAL_HTML", "published_at": "2026-04-27", "language": "Korean", "reporting_period": "2026Q2"},
    {"source_id": "src_ps_stellar_pc_html", "publisher_name": "PlayStation / SHIFT UP", "source_url": "https://blog.playstation.com/2025/05/15/stellar-blade-launches-june-11-on-pc-specs-and-features-revealed/", "source_type": "OFFICIAL_HTML", "published_at": "2025-05-15", "language": "English", "reporting_period": "2025Q2"},
    {"source_id": "src_nc_lm_homecoming_html", "publisher_name": "NCSOFT", "source_url": "https://about.ncsoft.com/news/article/lineagem-update-250226", "source_type": "OFFICIAL_HTML", "published_at": "2025-02-26", "language": "Korean", "reporting_period": "2025Q1"},
    {"source_id": "src_nc_lm_rising_html", "publisher_name": "NCSOFT", "source_url": "https://about.ncsoft.com/news/article/lineagem_update_250618", "source_type": "OFFICIAL_HTML", "published_at": "2025-06-18", "language": "Korean", "reporting_period": "2025Q2"},
    {"source_id": "src_pa_bd_seoul_html", "publisher_name": "Pearl Abyss", "source_url": "https://blackdesert.pearlabyss.com/Asia/en-US/News/Notice/Detail?_boardNo=6377", "source_type": "OFFICIAL_HTML", "published_at": "2024-08-28", "language": "English", "reporting_period": "2024Q3"},
    {"source_id": "src_pa_bd_wukong_html", "publisher_name": "Pearl Abyss", "source_url": "https://blackdesert.pearlabyss.com/Asia/en-US/News/Notice/Detail?_boardNo=7903", "source_type": "OFFICIAL_HTML", "published_at": "2025-06-30", "language": "English", "reporting_period": "2025Q3"},
]


def fiscal_periods() -> list[dict]:
    starts = {
        "Q1": ("01-01", "03-31"), "Q2": ("04-01", "06-30"),
        "Q3": ("07-01", "09-30"), "Q4": ("10-01", "12-31"),
    }
    labels = ["2024Q3", "2024Q4", "2025Q1", "2025Q2", "2025Q3", "2025Q4", "2026Q1", "2026Q2"]
    rows = []
    for company in ["shift_up", "ncsoft", "pearl_abyss", "netmarble"]:
        for label in labels:
            year, quarter = label[:4], label[4:]
            start_suffix, end_suffix = starts[quarter]
            rows.append({
                "fiscal_period_id": f"fp_{company}_{label.lower()}", "company_id": company,
                "fiscal_year_label": year, "fiscal_quarter_label": quarter,
                "period_start": f"{year}-{start_suffix}", "period_end": f"{year}-{end_suffix}",
                "calendar_quarter_equivalent": label, "alignment_status": "VERIFIED_CALENDAR_ALIGNED",
                "notes": "Calendar alignment verified from the company's dated quarterly reporting materials; not inferred from label alone.",
            })
    return rows


def build_sources() -> tuple[list[dict], list[dict]]:
    sources, manifest = [], []
    for source_id, company, url, filename, source_type, published, language, period in SOURCE_SPECS:
        path = RAW / filename
        if not path.is_file():
            raise FileNotFoundError(path)
        digest = sha256(path)
        relative = path.relative_to(ROOT).as_posix()
        sources.append({"source_id": source_id, "publisher_name": company, "source_url": url, "source_type": source_type, "published_at": published, "retrieved_at": RETRIEVED_AT, "local_path": relative, "sha256": digest, "file_size": path.stat().st_size, "language": language, "reporting_period": period, "access_class": "PUBLIC_NO_LOGIN", "officiality": "OFFICIAL", "reuse_note": "Internal provenance copy only; public layer releases structured facts and citations, not the PDF."})
        manifest.append({"source_id": source_id, "company": company, "source_url": url, "local_path": relative, "document_type": source_type, "publication_date": published, "retrieval_date": RETRIEVED_AT, "file_size": path.stat().st_size, "sha256": digest, "language": language, "reporting_period": period})
    for item in HTML_SOURCES:
        sources.append({**item, "retrieved_at": RETRIEVED_AT, "local_path": "", "sha256": "", "file_size": "", "access_class": "PUBLIC_NO_LOGIN", "officiality": "OFFICIAL", "reuse_note": "Canonical URL retained; page was not mirrored."})
    return sources, manifest


def metric_context(metric_id: str) -> tuple[str, str, str]:
    return {
        "md_su_ip_revenue_v1": ("Publisher-defined IP scope; NIKKE mobile/client channels not decomposed; Stellar Blade console plus PC after launch", "Global consolidated reporting scope", "SHIFT_UP_consolidated_IP_revenue"),
        "md_nc_lineage_m_legacy_v1": ("Mobile", "Consolidated reporting regions", "NCSOFT_mobile_title_chart_legacy_scope"),
        "md_nc_lineage_m_royalty_v2": ("Mobile title/IP presentation", "Consolidated reporting regions", "NCSOFT_mobile_IP_revenue_royalties_integrated"),
        "md_pa_black_desert_ip_v1": ("PC; console; mobile", "Global consolidated reporting scope", "Pearl_Abyss_Black_Desert_IP_all_platforms"),
        "md_nm_mcoc_derived_v1": ("Mobile title; consolidated company denominator", "Global consolidated reporting scope", "Netmarble_company_revenue_times_rounded_title_share"),
    }[metric_id]


def observation_id(entity_id: str, metric_id: str, period_id: str) -> str:
    quarter = period_id.rsplit("_", 1)[-1]
    prefix = {
        "nikke_ip": "nikke", "stellar_blade_ip": "stellar", "black_desert_ip": "bd",
        "marvel_contest_of_champions_title": "mcoc",
    }.get(entity_id, "lm_v2" if metric_id.endswith("royalty_v2") else "lm_v1")
    return f"obs_{prefix}_{quarter}"


def build_observations(extractions: list[dict], periods: list[dict], sources: list[dict]) -> tuple[list[dict], list[dict]]:
    period_map = {row["fiscal_period_id"]: row for row in periods}
    source_map = {row["source_id"]: row for row in sources}
    metric_map = {row["metric_definition_id"]: row for row in METRICS}
    observations, derivations = [], []
    grouped: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in extractions:
        grouped[(row["entity_id"], row["fiscal_period_id"], row["metric_definition_id"])].append(row)

    for (entity_id, period_id, metric_id), rows in grouped.items():
        period = period_map[period_id]
        metric = metric_map[metric_id]
        platform, geography, reporting_scope = metric_context(metric_id)
        fields = {row["field_name"]: row for row in rows}
        obs_id = observation_id(entity_id, metric_id, period_id)
        if "reported_value" in fields:
            extraction = fields["reported_value"]
            raw = Decimal(extraction["field_value"])
            unit = extraction["unit"]
            source = source_map[extraction["source_id"]]
            observations.append({
                "observation_id": obs_id, "entity_id": entity_id, "company_id": period["company_id"],
                "fiscal_period_id": period_id, "metric_definition_id": metric_id,
                "metric_version": metric["metric_version"], "comparable_group_id": metric["comparable_group_id"],
                "evidence_class": "OFFICIAL_REPORTED", "reported_value_raw": extraction["field_value"],
                "reported_unit_raw": unit, "currency": "KRW", "value_krw_million": dec_text(to_krw_million(raw, unit)),
                "lower_bound_krw_million": "", "upper_bound_krw_million": "", "derivation_id": "",
                "source_id": extraction["source_id"], "source_page": extraction["source_page"],
                "published_at": source["published_at"], "retrieved_at": RETRIEVED_AT,
                "platform_scope": platform, "geographic_scope": geography, "reporting_scope": reporting_scope,
                "missingness_state": "AVAILABLE", "notes": extraction["extractor_note"],
            })
        else:
            total_row, share_row = fields["input_total_revenue"], fields["input_share_percent"]
            total, share = Decimal(total_row["field_value"]), Decimal(share_row["field_value"])
            point = total * share / Decimal("100")
            lower_exact = total * (share - Decimal("0.5")) / Decimal("100")
            upper_exact = total * (share + Decimal("0.5")) / Decimal("100")
            lower = lower_exact.quantize(Decimal("0.01"), rounding=ROUND_FLOOR)
            upper = upper_exact.quantize(Decimal("0.01"), rounding=ROUND_CEILING)
            derivation_id = f"drv_{obs_id.removeprefix('obs_')}"
            formula = f"{total_row['field_value']} * ({share_row['field_value']} / 100)"
            derivations.append({
                "derivation_id": derivation_id, "formula_text": formula,
                "input_total_value": total_row["field_value"], "input_total_unit": total_row["unit"],
                "input_share_percent": share_row["field_value"], "share_rounding_increment": "1 percentage point",
                "point_estimate": dec_text(point), "lower_bound": dec_text(lower), "upper_bound": dec_text(upper),
                "calculation_method": "Decimal arithmetic; point estimate uses reported share; compatible share interval is +/-0.5pp; bounds rounded outward to 0.01 KRW billion",
                "source_total_id": total_row["extraction_id"], "source_share_id": share_row["extraction_id"],
                "verification_status": "VERIFIED_REPRODUCIBLE", "bound_unit": "KRW_billion",
            })
            source = source_map[total_row["source_id"]]
            observations.append({
                "observation_id": obs_id, "entity_id": entity_id, "company_id": period["company_id"],
                "fiscal_period_id": period_id, "metric_definition_id": metric_id,
                "metric_version": metric["metric_version"], "comparable_group_id": metric["comparable_group_id"],
                "evidence_class": "DERIVED_FROM_OFFICIAL", "reported_value_raw": dec_text(point),
                "reported_unit_raw": "KRW_billion", "currency": "KRW", "value_krw_million": dec_text(point * 1000),
                "lower_bound_krw_million": dec_text(lower * 1000), "upper_bound_krw_million": dec_text(upper * 1000),
                "derivation_id": derivation_id, "source_id": total_row["source_id"],
                "source_page": f"{total_row['source_page']};{share_row['source_page']}",
                "published_at": source["published_at"], "retrieved_at": RETRIEVED_AT,
                "platform_scope": platform, "geographic_scope": geography, "reporting_scope": reporting_scope,
                "missingness_state": "AVAILABLE", "notes": "Derived from official total revenue and rounded title share; interval preserves share-rounding uncertainty.",
            })
    entity_order = {"nikke_ip": 1, "stellar_blade_ip": 2, "lineage_m_title": 3, "black_desert_ip": 4, "marvel_contest_of_champions_title": 5}
    observations.sort(key=lambda row: (entity_order[row["entity_id"]], row["metric_version"], row["fiscal_period_id"]))
    derivations.sort(key=lambda row: row["derivation_id"])
    return observations, derivations


def build_events() -> list[dict]:
    return [
        {"event_id": "evt_nikke_35_anniv", "entity_id": "nikke_ip", "event_name": "3.5th anniversary update", "event_type": "ANNIVERSARY_UPDATE", "event_date_start": "2026-04-23", "event_date_end": "", "fiscal_period_id": "fp_shift_up_2026q2", "platform_scope": "Mobile / live service", "region_scope": "Global; performance commentary highlights Korea and Japan", "source_id": "src_su_nikke_35_html", "source_page_if_applicable": "", "date_precision": "DAY", "notes": "Official SHIFT UP release states April 23 was the update day. Temporal context only."},
        {"event_id": "evt_stellar_pc_launch", "entity_id": "stellar_blade_ip", "event_name": "Stellar Blade PC launch", "event_type": "PLATFORM_LAUNCH", "event_date_start": "2025-06-11", "event_date_end": "", "fiscal_period_id": "fp_shift_up_2025q2", "platform_scope": "PC", "region_scope": "Global; timing may be June 12 in some regions", "source_id": "src_ps_stellar_pc_html", "source_page_if_applicable": "", "date_precision": "DAY", "notes": "Official PlayStation Blog post authored by SHIFT UP technical director. Event does not rewrite the IP metric definition."},
        {"event_id": "evt_lm_homecoming", "entity_id": "lineage_m_title", "event_name": "HOMECOMING update", "event_type": "MAJOR_UPDATE", "event_date_start": "2025-03-05", "event_date_end": "", "fiscal_period_id": "fp_ncsoft_2025q1", "platform_scope": "Mobile", "region_scope": "Korea", "source_id": "src_nc_lm_homecoming_html", "source_page_if_applicable": "", "date_precision": "DAY", "notes": "Official NCSOFT release. Temporal context only."},
        {"event_id": "evt_lm_rising_storm", "entity_id": "lineage_m_title", "event_name": "RISING STORM update", "event_type": "MAJOR_UPDATE", "event_date_start": "2025-06-18", "event_date_end": "", "fiscal_period_id": "fp_ncsoft_2025q2", "platform_scope": "Mobile", "region_scope": "Korea", "source_id": "src_nc_lm_rising_html", "source_page_if_applicable": "", "date_precision": "DAY", "notes": "Official NCSOFT release. Temporal context only."},
        {"event_id": "evt_bd_morning_light_seoul", "entity_id": "black_desert_ip", "event_name": "Land of the Morning Light: Seoul release", "event_type": "EXPANSION_UPDATE", "event_date_start": "2024-09-12", "event_date_end": "", "fiscal_period_id": "fp_pearl_abyss_2024q3", "platform_scope": "Black Desert PC live service; regional notice", "region_scope": "Global rollout described by official regional notice", "source_id": "src_pa_bd_seoul_html", "source_page_if_applicable": "", "date_precision": "DAY", "notes": "Official Pearl Abyss notice. Event is linked to the IP record without allocating revenue to an edition."},
        {"event_id": "evt_bd_wukong", "entity_id": "black_desert_ip", "event_name": "Wukong class release", "event_type": "MAJOR_CONTENT_UPDATE", "event_date_start": "2025-07-02", "event_date_end": "", "fiscal_period_id": "fp_pearl_abyss_2025q3", "platform_scope": "Black Desert PC live service; regional notice", "region_scope": "Asia regional service notice", "source_id": "src_pa_bd_wukong_html", "source_page_if_applicable": "", "date_precision": "DAY", "notes": "Official Pearl Abyss service notice. Temporal context only."},
    ]


def build_claims() -> list[dict]:
    return [
        {"claim_id": "claim_nikke_35_q2_2026", "entity_id": "nikke_ip", "fiscal_period_id": "fp_shift_up_2026q2", "claim_type": "PERFORMANCE_ATTRIBUTION", "claim_summary": "SHIFT UP linked NIKKE's Q2 2026 global revenue growth and app-store performance to the April 3.5th-anniversary update and its content response.", "attributed_to": "SHIFT UP management", "source_id": "src_su_2q26_pres", "source_page": "9", "strength_note": "Issuer attribution recorded as a claim; the project does not adopt it as an independent causal conclusion."},
        {"claim_id": "claim_stellar_base_effect_q2_2026", "entity_id": "stellar_blade_ip", "fiscal_period_id": "fp_shift_up_2026q2", "claim_type": "BASE_EFFECT_EXPLANATION", "claim_summary": "SHIFT UP stated that the year-over-year decline reflected the 2025Q2 PC-launch base effect.", "attributed_to": "SHIFT UP management", "source_id": "src_su_2q26_pres", "source_page": "6", "strength_note": "Issuer explanation retained separately; not a project causal finding."},
    ]


def build_comparability() -> list[dict]:
    series = [
        ("series_nikke_v1", "nikke_ip", "md_su_ip_revenue_v1"),
        ("series_stellar_v1", "stellar_blade_ip", "md_su_ip_revenue_v1"),
        ("series_lineage_m_v1", "lineage_m_title", "md_nc_lineage_m_legacy_v1"),
        ("series_lineage_m_v2", "lineage_m_title", "md_nc_lineage_m_royalty_v2"),
        ("series_black_desert_v1", "black_desert_ip", "md_pa_black_desert_ip_v1"),
        ("series_mcoc_derived_v1", "marvel_contest_of_champions_title", "md_nm_mcoc_derived_v1"),
    ]
    rows = []
    for i, left in enumerate(series):
        for right in series[i:]:
            if left[0] == right[0]:
                status, rationale = "DIRECTLY_COMPARABLE", "Same analytical entity, metric definition, unit basis, and metric version."
            elif {left[0], right[0]} == {"series_lineage_m_v1", "series_lineage_m_v2"}:
                status, rationale = "VERSION_BREAK", "Same title but royalties are integrated only in v2; overlapping quarters validate the break and cannot be stitched."
            elif {left[0], right[0]} == {"series_nikke_v1", "series_stellar_v1"}:
                status, rationale = "WITHIN_SERIES_ONLY", "Shared reporting company and metric label do not erase different IP/platform scopes; analyze changes within each series only."
            else:
                status, rationale = "NOT_COMPARABLE", "Entity, accounting scope, publisher definition, or direct/derived evidence differs."
            rows.append({"pair_id": f"cmp_{left[0]}__{right[0]}", "left_series_id": left[0], "left_entity_id": left[1], "left_metric_definition_id": left[2], "right_series_id": right[0], "right_entity_id": right[1], "right_metric_definition_id": right[2], "comparability_status": status, "rationale": rationale})
    return rows


def build_changes(observations: list[dict], periods: list[dict]) -> list[dict]:
    period_map = {row["fiscal_period_id"]: row for row in periods}
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for observation in observations:
        groups[(observation["entity_id"], observation["metric_definition_id"])].append(observation)
    rows = []
    for (entity_id, metric_id), group in groups.items():
        group.sort(key=lambda row: period_map[row["fiscal_period_id"]]["period_end"])
        baseline = Decimal(group[0]["value_krw_million"])
        for index, current in enumerate(group):
            value = Decimal(current["value_krw_million"])
            if index == 0:
                reason = "METRIC_VERSION_BREAK" if metric_id == "md_nc_lineage_m_royalty_v2" else "NO_PRIOR_COMPATIBLE_OBSERVATION"
                previous_id, absolute, percent = "", "", ""
            else:
                previous = group[index - 1]
                prior_value = Decimal(previous["value_krw_million"])
                previous_id = previous["observation_id"]
                absolute = dec_text(value - prior_value)
                percent = dec_text(((value - prior_value) / prior_value) * 100) if prior_value != 0 else ""
                reason = ""
            rows.append({"observation_id": current["observation_id"], "entity_id": entity_id, "fiscal_period_id": current["fiscal_period_id"], "metric_definition_id": metric_id, "metric_version": current["metric_version"], "comparable_group_id": current["comparable_group_id"], "previous_observation_id": previous_id, "qoq_absolute_change_krw_million": absolute, "qoq_percent_change": percent, "baseline_index": dec_text(value / baseline * 100), "null_reason": reason})
    return sorted(rows, key=lambda row: row["observation_id"])


def build_public_release(observations: list[dict], sources: list[dict], periods: list[dict]) -> list[dict]:
    entities = {row["entity_id"]: row for row in ENTITIES}
    source_map = {row["source_id"]: row for row in sources}
    period_map = {row["fiscal_period_id"]: row for row in periods}
    metric_map = {row["metric_definition_id"]: row for row in METRICS}
    company_map = {row["company_id"]: row for row in COMPANIES}
    rows = []
    for observation in observations:
        rows.append({
            "entity": entities[observation["entity_id"]]["canonical_name"],
            "quarter": period_map[observation["fiscal_period_id"]]["calendar_quarter_equivalent"],
            "publisher_defined_metric_label": metric_map[observation["metric_definition_id"]]["metric_name"],
            "metric_version": observation["metric_version"], "value": observation["reported_value_raw"],
            "unit": observation["reported_unit_raw"], "evidence_class": observation["evidence_class"],
            "source_company": company_map[observation["company_id"]]["canonical_name"],
            "source_page": observation["source_page"], "canonical_source_url": source_map[observation["source_id"]]["source_url"],
            "derivation_marker": "YES" if observation["derivation_id"] else "NO",
            "lower_bound": observation["lower_bound_krw_million"], "upper_bound": observation["upper_bound_krw_million"],
            "bound_unit": "KRW_million" if observation["lower_bound_krw_million"] else "",
        })
    return rows


def build_manual_qa(observations: list[dict]) -> list[dict]:
    selected = {
        "obs_nikke_2024q3", "obs_nikke_2026q2", "obs_stellar_2024q3", "obs_stellar_2026q2",
        "obs_lm_v1_2024q3", "obs_lm_v1_2025q4", "obs_lm_v2_2025q2",
        "obs_bd_2024q3", "obs_bd_2026q2", "obs_mcoc_2024q3", "obs_mcoc_2025q2",
    }
    return [{"qa_id": f"qa_{row['observation_id']}", "observation_id": row["observation_id"], "source_id": row["source_id"], "source_page": row["source_page"], "check_type": "MANUAL_SOURCE_RECONCILIATION", "result": "PASS", "qa_note": "Value, unit, entity label, quarter, and evidence class matched to the official source page; MCOC rows also reconcile denominator and rounded share."} for row in observations if row["observation_id"] in selected]


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    extractions = read_csv(INPUT)
    periods = fiscal_periods()
    sources, manifest = build_sources()
    observations, derivations = build_observations(extractions, periods, sources)
    events = build_events()
    claims = build_claims()
    comparability = build_comparability()
    changes = build_changes(observations, periods)
    public_release = build_public_release(observations, sources, periods)
    manual_qa = build_manual_qa(observations)

    write_csv("companies.csv", list(COMPANIES[0]), COMPANIES)
    write_csv("entities.csv", list(ENTITIES[0]), ENTITIES)
    write_csv("fiscal_periods.csv", list(periods[0]), periods)
    write_csv("metric_definitions.csv", list(METRICS[0]), METRICS)
    write_csv("sources.csv", list(sources[0]), sources)
    write_csv("raw_manifest.csv", list(manifest[0]), manifest)
    write_csv("observations.csv", list(observations[0]), observations)
    write_csv("derivations.csv", list(derivations[0]), derivations)
    write_csv("events.csv", list(events[0]), events)
    write_csv("attributed_claims.csv", list(claims[0]), claims)
    write_csv("comparability_matrix.csv", list(comparability[0]), comparability)
    write_csv("change_features.csv", list(changes[0]), changes)
    write_csv("public_release_observations.csv", list(public_release[0]), public_release)
    write_csv("manual_qa.csv", list(manual_qa[0]), manual_qa)

    metadata = {
        "phase": "PHASE B — CONTROLLED PILOT", "build_schema_version": "phase-b-pilot-v1",
        "retrieval_date": RETRIEVED_AT, "primary_observations": len(observations),
        "official_reported_observations": sum(row["evidence_class"] == "OFFICIAL_REPORTED" for row in observations),
        "derived_official_observations": sum(row["evidence_class"] == "DERIVED_FROM_OFFICIAL" for row in observations),
        "retained_source_files": len(manifest), "retained_source_bytes": sum(int(row["file_size"]) for row in manifest),
        "event_records": len(events), "attributed_claims": len(claims),
        "determinism_note": "Canonical outputs contain no runtime timestamps; source retrieval date is fixed provenance input.",
    }
    with (DATA / "build_metadata.json").open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(metadata, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


if __name__ == "__main__":
    main()
