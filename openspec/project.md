# Squadron Scheduler — Project Context

## Purpose

A squadron-desk flying schedule that assigns **aircraft tails** (primary + spare),
**loadouts**, and **crew**, then answers whether today’s go is executable and
what to fix next.

## Tech Stack

- **Svelte 5** + Vite (dashboard)
- **FastAPI** + **SQLite** (API + store)
- **unittest** for metrics, buildup, aircraft rules
- **OpenSpec** living specs in `openspec/specs/`
- **Gherkin** in `features/`
- **Beads** (`.beads/` + `bd`) for task tracking

## Domain map

| Practice | Capability |
| --- | --- |
| Sortie board | `flying-schedule` |
| Primary / spare / turn conflicts | `aircraft-assignment` |
| Jet-day asset view | `aircraft-day-board` |
| Weapons templates + load-crew + ER | `loadout-and-mx` |
| Pilot / WSO + rest | `crew-assignment` |
| Executable % / funnel / exceptions | `readiness-metrics` |
| Tail / crew change audit | `pen-and-ink` |
| Morning-go replay 01–06 | `demo-buildup` |

## Conventions

- Domain rules: `backend/metrics.py`, `backend/aircraft_rules.py`
- Seed + demo: `backend/sample_data.py`
- API: `backend/main.py`
- Spec → Beads → implement → Gherkin/unit tests (see `openspec/WORKFLOW.md`)
- Critical review of gaps: `docs/CRITICAL-REVIEW.md`

## Phase map

- **Prototype (this repo):** All capability specs except production markers
- **Production (do not implement here):** durable multi-user DB, auth/tenancy,
  live MX feed, full RAP engine, hosted demo — beads P1–P8
