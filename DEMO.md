# Demo — 2.1 aircraft scheduling

## Local

```bash
cd backend && python main.py          # :8000
cd frontend && npm i && npm run dev   # :5173
```

Click **Replay process 01–06**. Watch executable %, spares, ER, and the funnel move.

| Stage | What the dashboard should say |
| --- | --- |
| 01 | Executable 0%. Next action: missing tail. Four exceptions. |
| 02 | Tails 4/4, spares 4/4. Funnel on "Tail assigned". Next: missing loadout. |
| 03 | Loadouts 4/4 with load-crew minutes. Next: missing pilot. |
| 04 | Crew 4/4. Stage = Crew filled. Still 0% executable (ER missing). |
| 05 | ER signed. Executable 100%. Exceptions empty. |
| 06 | Airborne 2. Executable still 100%. |

Also check:

- **Aircraft day board** — each jet’s primary/spare commitments
- **Pen-and-ink** — tail/spare/crew/ER/status changes logged

Tests:

```bash
cd backend
python -m unittest test_metrics test_buildup -v
```
