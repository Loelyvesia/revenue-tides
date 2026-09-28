# Revenue Tides — Visual Refresh 1.1

Status: `PASS / RELEASE CANDIDATE`

Branch: `visual-refresh-1.1`

Release candidate: `revenue-tides-release-1.1.0`

This is a UI, art-direction, and interaction-refinement release. It does not amend the frozen research corpus.

## Frozen invariants

- Method: `revenue-tides-method-freeze-1.0.0`
- Findings: `revenue-tides-findings-1.0.0`
- Web Data: `revenue-tides-webdata-1.0.0`
- 9 series, 75 observations, 26 events, 3 attributed claims, 18 derived observations, and F1–F6 are unchanged.
- Headline Findings remain F1, F2, and F4.
- `GAME_TITLE` and `IP`, direct and derived evidence, metric versions, uncertainty, and event non-causality remain explicit.

## Art direction

The refreshed interface sharpens the existing **Tidal Ledger / 潮汐账本** direction: mineral paper, ledger rules, calibrated marks, restrained teal evidence accents, and copper context rails. No game art, ocean imagery, gradients, chart library, animation library, or UI framework was introduced.

## Primary changes

- Rebuilt the opening as an asymmetrical editorial cover with a 09 / 75 / 04 / 2024Q3–2026Q2 scope ledger.
- Replaced the primer list with one continuous Measurement Grammar diagram.
- Reframed Quarter Prism as a border-light reading instrument with a calibration window, definition seam, event rail, and instrument strip controls.
- Gave F1, F2, and F4 distinct editorial compositions.
- Recast the Observatory as a Research Ledger with row expansion rather than a card wall.
- Added lightweight active navigation and reduced-motion-safe section reveals.
- Reworked 390 px and 320 px layouts as mobile compositions rather than stacked desktop cards.

## Verification

- TypeScript: PASS
- Vitest: 62/62 PASS
- Production build: PASS
- Phase G isolated validation: 90/90 PASS
- Phase I validation: 100/100 PASS
- Phase J validation: 102/102 PASS
- Phase K frozen-release validation: 110/110 PASS in an isolated 1.0.0 worktree
- Chrome: 40/40 PASS
- Edge: 40/40 PASS
- Firefox: 14/14 PASS
- Required viewports: 1440×900, 1280×800, 1024×768, 768×1024, 390×844, and 320×700 PASS
- Console errors / warnings / uncaught exceptions: 0 / 0 / 0

## Release boundary

No GitHub Pages deployment and no release tag were created. The frozen 1.0.0 release remains intact pending manual approval of this candidate.

`STOPPED BEFORE RELEASE 1.1 FREEZE`
