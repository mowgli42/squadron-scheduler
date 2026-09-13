# Beads — Squadron Scheduler

## Workflow

```bash
./scripts/beads-setup.sh   # once
bd ready
bd update <id> --status in_progress
# implement + tests
bd close <id>
```

See `openspec/WORKFLOW.md` and `docs/CRITICAL-REVIEW.md`.

## Prototype gap-close (this branch)

| Bead | Capability | Status |
| --- | --- | --- |
| A1 Land + turn conflicts | aircraft-assignment | Done |
| A2 Spare tail | aircraft-assignment | Done |
| A3 Config mismatch | aircraft-assignment | Done |
| A4 Aircraft day board | aircraft-day-board | Done |
| A5 Line + callsign | flying-schedule | Done |
| A6 Load-crew minutes | loadout-and-mx | Done |
| A7 Rest gate | crew-assignment | Done |
| A8 Pen-and-ink log | pen-and-ink | Done |
| A9 ER before crew-ready | loadout-and-mx | Done |
| A10 Crew replace | crew-assignment | Done |
| A11 Richer metrics | readiness-metrics | Done |
| A12 Demo 01–06 + spare/ER | demo-buildup | Done |
| A13 Frontend board updates | flying-schedule | Done |

## Earlier prototype (still done)

- B1–B8 — 1.0 data model, APIs, board, demo, tests
- B9–B12 — derived stages, `/metrics`, IxDF 2.0 layout, stage assertions

## Production rebuild (do not implement in the prototype)

| Bead | Topic |
| --- | --- |
| P1 | Durable multi-user store |
| P2 | Explicit process state machine |
| P3 | Auth + squadron tenancy |
| P4 | Live Ops–MX feed |
| P5 | Full RAP / currency engine |
| P6 | Hosted demo |

Machine tracking: `.beads/` via `bd`.
