# Beads — Squadron Scheduler

## Done (prototype)

- B1–B8 — 1.0 data model, APIs, board, demo 01–06, tests
- B9 — Derived process stages (planned → tail → loadout → crewed → crew-ready → airborne)
- B10 — GET /metrics + executable % as primary decision metric
- B11 — IxDF 2.0 layout: question, metric band, process funnel, exceptions, board
- B12 — metrics.py unit tests + stage assertions on demo buildup

## Production rebuild (do not implement in the prototype)

### P1 — Durable multi-user store
Replace single SQLite file with a real DB and concurrent writers.

### P2 — Explicit process state machine
Stop deriving stage. Store legal transitions and who moved the line.

### P3 — Auth + squadron tenancy
CAC / Platform One identity. One unit's schedule is not another unit's.

### P4 — Live Ops–MX feed
Aircraft MC/PMC and configuration from the maintenance system of record.

### P5 — Currency / rest engine
RAP events, FDP, crew rest. Block assign with the actual rule, not same-day only.

### P6 — Pen-and-ink audit
Every tail swap and crew change is a dated event, exportable.

### P7 — Observability
Structured logs and a readiness snapshot that a commander can trust.

### P8 — Hosted demo
Vercel (or equivalent) front door plus a hosted API so the desk works off-box.
