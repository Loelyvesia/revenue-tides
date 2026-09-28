# Phase J QA fix log

No production frontend, configuration, frozen artifact, public data, Finding, or research method was changed.

## QA-only changes

1. Added dependency-free Chrome/Edge CDP smoke automation for production rendering, network/console collection, responsive checks, interactions, accessibility-tree inspection, failure/retry, screenshots, and subdirectory validation.
2. Added Firefox WebDriver BiDi smoke automation using the installed system browser.
3. Corrected QA screenshot positioning to use immediate scroll coordinates rather than waiting on the application's intentional smooth scroll. This changed evidence capture only.
4. Moved the deliberate blocked-request test before other lazy loads so the target could not already be satisfied from cache. This changed test determinism only.
5. Removed a duplicate Firefox CLI screenshot captured before asynchronous hash relocation; the valid Firefox opening screenshot and BiDi results remain.

Frozen semantics remain unchanged because every modification is confined to `scripts/phase_j/` and `research/phase-j/`.
