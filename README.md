# Squadron Scheduler (prototype)

Minimal web tool for squadron flying schedule: aircraft tails, loadouts, crew.

**Stack:** Svelte 5 + FastAPI + SQLite  
**UI:** light-grey IxDF style  
**Method:** OpenSpec (Gherkin) → beads → ponytail implementation

## Quick start

```bash
# backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py          # http://localhost:8000

# frontend (new terminal)
cd frontend
npm i
npm run dev             # http://localhost:5173  (proxies /api → :8000)
```

## Spec & beads

- `openspec/squadron-scheduler.feature` — Gherkin scenarios
- `beads/BEADS.md` — atomic slices (B1–B7)
- `.cursor/rules/ponytail.mdc` — YAGNI / minimal code rule

## Scope (YAGNI)

Working: view board, assign tail, apply loadout template, assign pilot/WSO, basic same-day conflict checks.

Not in this prototype: auth, real-time multi-user, full currency engine, munitions inventory, AF Form 2407, Docker, AI optimizer.
