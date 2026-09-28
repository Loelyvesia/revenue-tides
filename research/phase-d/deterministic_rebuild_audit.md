# Deterministic rebuild audit

The build uses fixed source inputs, fixed cutoff metadata, stable sorting, Decimal arithmetic, LF line endings, and sorted JSON keys. The validator executes the build twice and compares hashes for every canonical data output.
