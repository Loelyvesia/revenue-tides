# Entity identity audit

The pilot preserves the publisher-defined analytical entity instead of forcing every row into a game-app identity.

- NIKKE and Stellar Blade are `IP` rows because SHIFT UP reports operating revenue by IP.
- Lineage M and MARVEL Contest of Champions are `GAME_TITLE` rows.
- Black Desert is an `IP`, not Black Desert Mobile or a single PC/console edition.
- Stellar Blade PS5 and PC editions exist only as identity/event context. No edition-level revenue is inferred.
- The Lineage franchise entity is context only. No revenue is aggregated to it.
- Platform entities are controlled vocabulary records, not reporting companies or revenue recipients.

All five analytical entities have explicit identity status and scope notes. No unresolved edition relationship is used to create an observation.
