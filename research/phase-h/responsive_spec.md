# Responsive specification

| Width | Layout transformation | Quarter Prism | Navigation and series exploration | Sources |
| --- | --- | --- | --- | --- |
| 1440 | 12-column narrative rail, wide analytical canvas, optional narrow evidence rail | Trajectory and context rail remain side by side with reading pane; overlap lanes have full labels | Inline section index; Observatory shows all research columns | Evidence drawer may occupy the right rail without covering marks |
| 1280 | 12 columns with reduced gutters; no permanent sidebar | Full prism geometry; reading pane narrows but stays adjacent | Observatory retains structured ledger | Drawer overlays only empty evidence rail, never the trajectory |
| 1024 | 8 columns; context/evidence moves below main plot | Prism remains horizontal; split lanes use abbreviated label plus full text below | Section index condenses; Observatory hides secondary counts behind row disclosure | Source metadata expands below selected observation |
| 768 | 8 columns with one dominant rail | Horizontal quarter track remains, but the reading pane and event rail stack beneath it | Observatory becomes two-line rows: identity first, evidence/window second | Source list becomes an inline evidence footer |
| 390 | Single column | Quarter stepper with Previous/Next, native select, and direct quarter list; selected quarter expands into stacked metric lanes | No hover or drag dependency; one series at a time; Observatory rows disclose in place | Source fields use a definition list and labeled links |
| 320 | Survival layout with 16 px outer inset | Same mobile decomposition; values may wrap but unit/version stay attached; event context follows quantitative block | Text labels replace nonessential icons; controls remain 44 px and wrap to two rows | Long titles wrap; URLs are never printed raw |

## Desktop composition

Opening and Finding chapters use editorial columns rather than cards. Quarter Prism receives the widest canvas. Context and evidence are aligned but visually secondary. No permanent dashboard sidebar is required.

## Tablet behavior

The trajectory keeps a shared quarter axis. Context and evidence move below the quantitative track so the version split retains width. Nothing is scaled down as a fixed desktop canvas.

## Mobile Quarter Prism

The selected series and quarter appear first. Controls follow: Previous, quarter select, Next. A vertical sequence then presents observation, reporting lane(s), uncertainty, event context, issuer explanation, and source. Overlap quarters keep two simultaneous stacked lanes. The direct quarter list is available after the expanded selected quarter.

## Mobile Series Detail

Identity and scope lead. The Tide Strip becomes a vertical quarter strip. Metric definition, Findings, events, and sources are disclosures in that order. Empty optional associations use neutral sentences. Technical tables use a local scroller only if reflow would destroy field relationships.

## Acceptance requirements for Phase I

- No page-level horizontal overflow at 1440, 1280, 1024, 768, 390, or 320.
- Text remains at least 12 px for annotations and 16 px for controls/input text.
- Every interactive target remains at least 44×44 px on coarse pointers.
- No content depends on hover.
- F1 overlap and F6 uncertainty remain visible at all target widths.
- Source access remains reachable after lazy-load failure or link redirect.
