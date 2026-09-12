# Demo — 2.0 process dashboard

## Local

```bash
cd backend && python main.py          # :8000
cd frontend && npm i && npm run dev   # :5173
```

Click **Replay process 01–06**. Watch executable % and the funnel move.

| Stage | What the dashboard should say |
| --- | --- |
| 01 | Executable 0%. Next action: missing tail. Four exceptions. |
| 02 | Tails 4/4. Funnel sitting on "Tail assigned". Next: missing loadout. |
| 03 | Loadouts 4/4. Next: missing pilot. |
| 04 | Crew 4/4. Stage = Crew filled. Still 0% executable until signed off. |
| 05 | Executable 100%. Exceptions empty. |
| 06 | Airborne 2. Executable still 100%. |

Tests:

```bash
cd backend
python -m unittest test_metrics test_buildup -v
```

## Why this demo

1.0 proved assignment works. 2.0 proves a scheduler can answer
"can we generate today's go?" without reading every cell.
