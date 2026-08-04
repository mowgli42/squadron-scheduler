# Beads — Squadron Scheduler Prototype

Atomic units derived from openspec/squadron-scheduler.feature.
Ponytail rule: each bead is the smallest shippable slice. No extras.

## Done

### B1 — Core data model (SQLite) ✅
- Tables: aircraft, aircrew, sorties, assignments
- Seed 3–5 example rows
- Done when: schema exists and seeds load without error

### B2 — FastAPI read endpoints ✅
- GET /aircraft, /aircrew, /sorties
- Return JSON only
- Done when: curl returns seeded data

### B3 — Assign aircraft ✅
- PATCH /sorties/{id}/aircraft {tail}
- Validate availability window (simple same-day overlap check)
- Done when: assignment persists and conflicts return 409

### B4 — Apply loadout ✅
- PATCH /sorties/{id}/loadout {template}
- Templates stored as simple dict in code
- Done when: loadout fields update

### B5 — Assign crew ✅
- POST /sorties/{id}/crew {position, aircrew_id}
- Block on same-day overlap (minimal rules; rest/currency still @wip)
- Done when: assignment works or returns clear 409

### B6 — Svelte board (light grey IxDF) ✅
- Single App.svelte showing list of sorties
- Columns: time | mission | tail | loadout | pilot | wso | status
- Light grey background, high-contrast text, minimal chrome
- Done when: board renders live data from API

### B7 — Inline assignment controls ✅
- Dropdowns on the board for tail / loadout / crew
- Call the PATCH/POST endpoints
- Done when: change appears without page reload

## Remaining (from @wip Gherkin)

- Rest / currency conflict checks on crew assign
- Load-crew estimate on board
- Crew-ready / Exceptional Release workflow
- Pen-and-ink change log

## Out of scope (YAGNI)

Auth, multi-user real-time, AI optimizer, full RAP currency engine, munitions inventory, AF Form 2407 PDF, mobile PWA, Docker, production deploy until asked.
