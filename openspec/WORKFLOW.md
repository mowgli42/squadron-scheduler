# Agent Workflow: OpenSpec + Gherkin + Beads

Follow this order unless the user requests otherwise.

## 1. Discovery & Specification (OpenSpec)

- Update `openspec/specs/<capability>/spec.md` with Purpose, SHALL requirements,
  and GIVEN/WHEN/THEN scenarios.
- Keep scenarios specific enough to become `features/*.feature` and unit tests.
- Record architectural gaps in `docs/CRITICAL-REVIEW.md` when discovering debt.

## 2. Task Breakdown (Beads)

```bash
bd ready                    # pick next work
bd update <id> --status in_progress
# implement + test
bd close <id>
```

- Map each requirement/scenario to Beads (`scripts/beads-setup.sh` seeds them).
- Use deps so aircraft rules land before UI/metrics that consume them.

### Status labels

| Label | Meaning |
| --- | --- |
| `status:specified` | OpenSpec + Gherkin written |
| `status:implementing` | Code in progress |
| `status:verified` | Unit tests / feature scenarios pass |
| closed | Done |

## 3. Implementation

- One ready bead at a time when possible.
- Put aircraft rules in `aircraft_rules.py`; keep FastAPI thin.
- Preserve demo stages 01–06 as a coherent story (extend, don’t break).

## 4. Verification

```bash
cd backend && python -m unittest discover -v
# features/*.feature must match scenarios covered by tests / API
```

## 5. Living docs

- README: summary → architecture → remaining
- `beads/BEADS.md`: human mirror of prototype vs production backlog
- Archive speculative work as production beads, not silent code debt

## Commands

| Tool | Commands |
| --- | --- |
| Beads | `bd ready`, `bd list`, `bd show`, `bd create`, `bd close` |
| Tests | `cd backend && python -m unittest discover -v` |
| API | `cd backend && python main.py` |
| UI | `cd frontend && npm run dev` |
