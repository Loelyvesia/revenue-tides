# Entity model freeze

## Entity types

Primary analytical types: `GAME_TITLE`, `GAME_EDITION`, `IP`, `FRANCHISE`.

Context-only type: `SEGMENT`.

Structural types: `COMPANY`, `PLATFORM`.

The publisher-defined reporting entity is authoritative for quantitative observations. Black Desert reported as an IP remains `IP`; no platform edition is inferred from branding.

## Identity requirements

Every analytical entity must retain canonical project name, publisher-defined reporting name, entity type, reporting company, verified relationships, relevant validity dates, and unresolved identity notes. Regional or platform editions are not merged merely because they share branding.

When entity scope materially changes, create a new entity-scope or metric version. Do not overwrite historical identity or fabricate edition relationships.
