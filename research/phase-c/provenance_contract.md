# Provenance contract

Every quantitative observation must trace to source ID, canonical source URL, reporting company, source document, publication date, fiscal period, retrieval date, extraction method, evidence class, and exact PDF page where applicable.

Retained files additionally require an internal relative provenance path, SHA-256, and byte size. Third-party copies are not primary when an official original exists.

Keep only the minimum official files needed for deterministic reconstruction. Deduplicate by SHA-256, do not mirror IR archives, and avoid videos, screenshots, ZIP collections, and bulk webpage archives.

Future raw/provenance storage has a 150 MB soft warning. Review is mandatory before exceeding 250 MB. Public outputs must not expose local machine paths.
