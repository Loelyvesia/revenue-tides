# Legal / Reproducibility Notes

This is an access-and-terms audit, not legal advice.

## Sensor Tower and AppMagic

Current Terms: <https://sensortower.com/tos>

- The Terms define Sensor Tower websites and AppMagic as services and define numerical estimates/reports as Service Data.
- Section 2 describes limited use and restricts third-party redistribution absent an applicable Order Form.
- Section 3 prohibits accessing, scraping, copying, or indexing the services through bots, crawlers, browser extensions, or other automated mechanisms.
- Free-tier access may be changed or removed.
- Therefore, Phase A stopped after a bounded accessibility check. It did not mass scrape, call private endpoints, bypass login, archive pages, or OCR chart collections.
- A public project must not assume that a public URL grants database-republication rights. Permission, a documented citation-only approach, or a different primary source is required.

Practical retention rule for this project:

- Keep URL, retrieval time, source ID, evidence class, scope notes, and small derived observations.
- Do not mirror Sensor Tower/AppMagic HTML, PDFs, charts, screenshots, or bulk tables.
- Do not expose a downloadable reconstruction that substitutes for the commercial product.
- Re-check Terms before any later acquisition.

## Official financial reports

Tencent and NetEase investor materials are publicly accessible official documents. They are useful as issuer evidence, but their company/segment figures must stay at that aggregation level. Phase A saved no copies; future snapshots, if justified, must be small, hashed, and retain the public URL and publication date.

## Official game event pages

Official pages are publicly readable and stable enough for a small manually curated timeline. Reproduction rights were not separately analyzed. Retain factual dates and short summaries with citations; avoid copying full announcements or media.

## Steamworks

Public documentation is readable, while sales/financial data is partner-only. The Financial API requires publisher financial permission. No credentials, authentication, or private requests were attempted.

## API and rate-limit findings

- No public Sensor Tower or AppMagic API suitable for this free project was established.
- No rate limit was relied upon because automated acquisition is out of scope under the current Terms.
- Apple lookup/store pages were used only to resolve pilot identity metadata.
- Update frequency is monthly for Sensor Tower ranking articles, event-driven for game news, and quarterly/annual for investor materials.

## Snapshot policy

No raw web snapshots were saved in Phase A. Consequently there are no snapshot files requiring hashes. Any future snapshot row must contain both `snapshot_path` and a SHA-256 digest; the validator enforces this.

