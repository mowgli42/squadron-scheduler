# Critical review — Squadron Scheduler workflow & aircraft info

**Verdict:** 2.0 answers “can we generate today’s go?” for crew readiness, but the **aircraft scheduling model is incomplete**. The desk cannot yet reason about tails as scarce assets across time, spares, configuration, or MX release.

## What works today

| Capability | Evidence |
| --- | --- |
| Sortie-centric board | `GET /sorties`, Svelte board |
| Primary tail assign + same-day conflict | `PATCH /sorties/{id}/aircraft` |
| Loadout templates | `PATCH /sorties/{id}/loadout` |
| Pilot/WSO assign + same-day conflict | `POST /sorties/{id}/crew` |
| Derived process + executable % | `metrics.py`, `GET /metrics` |
| Demo 01–06 | `POST /demo/stages/{id}` |

## Workflow gaps (generation process)

1. **Aircraft is only a label on a sortie.** There is no aircraft-day board: which jet flies which line, when it lands, and whether it can turn for a later go.
2. **Same-calendar-day conflict is too coarse.** Four ships two hours apart with a spare pool need **time-window / turn** conflicts, not “already used today.”
3. **No spare / backup tail.** Real morning-go generation always names a spare; missing spare is a go-risk, not optional chrome.
4. **Config vs loadout is ignored.** Aircraft `config` exists but never blocks a mismatched weapons template.
5. **Landing time is missing.** Without `land`, turn time and double-booking windows cannot be computed.
6. **Line identity is thin.** No callsign / line number / formation position — schedulers talk in those terms, not only mission type + takeoff.
7. **Crew-ready is unsigned.** Status can flip to executable without Exceptional Release (ER) attribution.
8. **`rest_until` and quals are dead fields.** Seeded but never enforced on assign.
9. **Crew cannot be replaced.** `UNIQUE(sortie_id, position)` + INSERT-only → first assign sticks; pen-and-ink swaps fail.
10. **No change log.** Tail/crew swaps are invisible after the fact.
11. **Load-crew effort is invisible.** Weapons templates imply ground time; the board never shows it.
12. **Metrics under-report aircraft risk.** `aircraft_available` counts MC/PMC but not spare coverage, config mismatches, or NMC blockers on assigned lines.

## Missing aircraft scheduling information (data)

| Field / concept | Why the desk needs it | Status after this slice |
| --- | --- | --- |
| `land` (or duration) | Turn / overlap checks | Done |
| `spare_tail` | Go generation risk | Done |
| Config ↔ loadout match | Wrong jet for weapons | Done |
| Callsign / line number | Desk language | Done |
| Load-crew minutes | Ground timeline | Done |
| ER signed | Legal go | Done |
| Change events | Pen-and-ink | Done |
| Aircraft day schedule | Asset view | Done (`GET /aircraft/schedule`) |
| Rest / currency gate | Safe crew assign | Rest gate done; full RAP → P5 |

## Spec / process debt

- OpenSpec was a single Gherkin file, not living capability specs.
- Beads were a markdown backlog (`beads/BEADS.md`), not `bd` with deps.
- Production beads P1–P8 remain correct **non-goals** for the prototype; the gaps above are **prototype-complete** aircraft scheduling, not hosted multi-user MX.

## Closure strategy (this branch)

1. Document requirements in OpenSpec capability specs + Gherkin features.
2. Seed Beads (`bd`) from those requirements with dependency order.
3. Implement prototype aircraft scheduling: land, spare, turn conflicts, config match, aircraft day board, load-crew estimate, ER gate, rest gate, crew replace, pen-and-ink log, richer metrics.
4. Keep derived stages; do not pretend a production state machine (still bead P2).
