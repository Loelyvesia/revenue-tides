# Console and network audit

Normal Chrome and Edge workflows produced:

- `console.error`: 0
- `console.warn`: 0
- uncaught exceptions: 0
- unexpected required HTTP 4xx: 0
- unexpected required HTTP 5xx: 0
- required JSON failures: 0
- mixed-content/CORS/production-asset failures: 0

The Chrome run recorded one intentionally blocked `series_black_desert.json` request during the failure-state test. It produced the controlled error and retry UI, was then unblocked, and loaded successfully; it is excluded from normal-workflow failure counts.

Initial load made 8 application requests: document, CSS, JavaScript, and five bootstrap JSON files. It did not request all nine series. Sources and individual series loaded later as designed; cached series were not re-fetched.

External source links are not fetched by the application. Independent samples returned 200 for NCSOFT, Netmarble, and Pearl Abyss; SHIFT UP returned 403 to automated HEAD access. This remote response does not represent a broken application request.
