# Preliminary Causality Policy

The default relationship between a commercial observation and a live-ops event is temporal proximity, not causation.

Allowed language:

- “The revenue estimate increased in the same period as Event X.”
- “Sensor Tower attributed part of the month's performance to Event X.”
- “Event X occurred near an observed revenue-rank peak.”

Disallowed language without a causal design and evidence:

- “Event X caused revenue to increase.”
- “The character release generated $Y” when only a period aggregate is observed.
- “The event explains the entire rank change.”

Third-party causal or explanatory wording is stored as `ATTRIBUTED_CLAIM` with `attributed_to`, `source_id`, period, and a neutral summary. `our_causal_conclusion` must remain false in Phase A/B.

Temporal analysis must show possible confounders where known: concurrent events, user acquisition, holidays, launches, price changes, platform expansion, and regional differences.

