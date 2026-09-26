# AGENTS.md — squadron-scheduler

Local overlay for agents. Shared Cursor pack (`.cursor/skills/*`, `repo-health.mdc`, `ponytail.mdc`) is the baseline.

**Age:** >30 days → Ponytail by default (YAGNI → reuse → stdlib → native → installed dep → one-liner → minimal). Prototype origins remain; do not expand into production beads P1–P8 unless asked.

## Commands (copy-paste)

```bash
# Backend
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py                    # :8000
python -m unittest test_metrics test_buildup -v

# Frontend
cd frontend && npm i && npm run dev   # :5173
```

Demo: click **01–06** under Replay process, or `POST /demo/stages/{id}`.

## Hard prohibitions

- Do **not** implement production beads P1–P8 (multi-user DB, auth, live MX feed, RAP/rest, pen-and-ink, hosted API) in this prototype slice.
- Do **not** invent new dependencies for trivial work; climb Ponytail first.
- Do **not** put payload/secrets in Catcher-style paths that do not exist here — this is assignment board + metrics only.

## Verify by change type

| Change | Verify |
| --- | --- |
| metrics / stages | `python -m unittest test_metrics test_buildup -v` |
| API routes | hit `/metrics`, `/demo/stages/{id}`; board still loads |
| UI layout | local `:5173` — question, metric band, funnel, exceptions, board |
| OpenSpec / Gherkin | scenarios in `openspec/squadron-scheduler.feature` match code; keep `@wip` for unbuilt |

## House vocabulary

- **Executable %** — primary decision metric (crew-ready or airborne lines).
- **Process stages** — planned → tail → loadout → crewed → crew-ready → airborne.
- **Next action** — derived from most common blocker.
- **Four-ship morning go** — sample day `2026-08-04` (demo 01–06).

## Source of truth

- Spec: `openspec/squadron-scheduler.feature`
- Tracking: `beads/BEADS.md`
- Demo: `DEMO.md`, screenshots under `docs/images/demo/`
- Learnings: `LEARNINGS.md`

Patterns borrowed (ossrules): hard prohibitions + verification-by-change-type + house vocabulary + single source of truth. Keep this file short.
