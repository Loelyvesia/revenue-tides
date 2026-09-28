# Public/internal separation audit

Public observation and event tables contain structured facts and source URLs, but no local paths, SHA-256 hashes, extractor names, QA notes, raw PDF paths, or copied chart assets. Internal tables retain the provenance fields required for reconstruction. The findings-ready layer contains validated analytical fields and source IDs only; it contains no local path or raw hash.
