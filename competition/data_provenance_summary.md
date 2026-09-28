# Data Provenance Summary

## Primary source family

The quantitative backbone consists of official public investor-relations materials: earnings presentations, earnings letters, factsheets, and related official company pages. The four reporting companies are NCSOFT, SHIFT UP, Pearl Abyss, and Netmarble. Official game or publisher pages supply curated event dates.

## Direct and derived observations

`OFFICIAL_REPORTED` observations reproduce publisher-disclosed values under their original entity, currency, platform, and reporting scope. `DERIVED_FROM_OFFICIAL` observations are deterministic calculations from official company totals and rounded title shares. They retain compatible bounds and are never relabeled as directly reported title revenue.

## Source resolution

Canonical source records preserve document title, type, publication date, reporting period, page when applicable, and public URL. The application deduplicates those records in one public source registry; series and Findings reference stable `source_id` values.

## Integrity process

Retained official PDFs were hashed during research. Method and Finding freezes record hashes for normative artifacts. Phase G converts the validated corpus into deterministic public JSON and records output hashes. The final release adds hashes for critical reports, application entry files, production assets, and competition summaries.

## Public/internal separation

Judge-facing and frontend data expose structured observations and public links. They do not expose local paths, raw PDF hashes, extractor identities, QA defect notes, or internal provenance files. Raw report artwork is not republished in the site.

Sensor Tower and AppMagic were tested during feasibility work but are not the quantitative backbone. No paid account, login bypass, private API, or mass scraping was used.
