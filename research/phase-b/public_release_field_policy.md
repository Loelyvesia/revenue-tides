# Public release field policy

This is a technical/provenance policy, not legal advice.

## PUBLIC_SAFE

- Canonical entity name and entity type.
- Fiscal quarter and exact period bounds.
- Publisher-defined metric label and metric version.
- Original factual value, unit, and currency.
- Evidence class and derivation marker.
- Derived formula inputs, point estimate, and uncertainty interval.
- Source company, publication date, exact source page, and canonical official URL.
- Concise original scope notes and missingness state.

## INTERNAL_PROVENANCE

- Local raw-file path.
- SHA-256 and byte size.
- Manual extraction IDs, extractor notes, and verification workflow fields.
- Build diagnostics and internal QA records.

These fields may be published later if useful, but the default public table omits them.

## DO_NOT_PUBLISH

- Copied slide images, charts, or full PDF pages.
- Mirrored IR archives or site feeds.
- Large verbatim excerpts.
- Authentication material, private endpoints, or paid-source data.
- Any field that relabels publisher revenue as total consumer spending.

`public_release_observations.csv` implements the small proposed public-safe table.
