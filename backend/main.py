"""Squadron Scheduler API — minimal FastAPI + SQLite."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime, timedelta

DB = Path(__file__).parent / "squadron.db"
app = FastAPI(title="Squadron Scheduler")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@contextmanager
def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init():
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS aircraft (
            tail TEXT PRIMARY KEY,
            status TEXT DEFAULT 'MC',
            config TEXT DEFAULT 'clean'
        );
        CREATE TABLE IF NOT EXISTS aircrew (
            id INTEGER PRIMARY KEY,
            name TEXT,
            role TEXT,
            quals TEXT,
            rest_until TEXT
        );
        CREATE TABLE IF NOT EXISTS sorties (
            id INTEGER PRIMARY KEY,
            takeoff TEXT,
            mission TEXT,
            tail TEXT,
            loadout TEXT,
            status TEXT DEFAULT 'planned'
        );
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY,
            sortie_id INTEGER,
            aircrew_id INTEGER,
            position TEXT,
            UNIQUE(sortie_id, position)
        );
        """)
        # seed only if empty
        if c.execute("SELECT COUNT(*) FROM aircraft").fetchone()[0] == 0:
            c.executemany("INSERT INTO aircraft VALUES (?,?,?)", [
                ("87-0321", "MC", "clean"),
                ("87-0322", "MC", "A/A"),
                ("87-0325", "PMC", "clean"),
            ])
            c.executemany("INSERT INTO aircrew VALUES (?,?,?,?,?)", [
                (1, "Capt Reyes", "pilot", "IP,A/A", None),
                (2, "Capt Kim", "pilot", "MP,A/A", None),
                (3, "1Lt Torres", "wso", "WSO,A/A", None),
                (4, "Capt Hale", "wso", "WSO,A/A", None),
            ])
            base = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
            c.executemany("INSERT INTO sorties (takeoff, mission, status) VALUES (?,?,?)", [
                ((base + timedelta(hours=i*2)).isoformat(timespec="minutes"), m, "planned")
                for i, m in enumerate(["A/A", "A/G", "A/A", "SEAD"])
            ])

init()

# --- models ---
class TailIn(BaseModel):
    tail: str

class LoadoutIn(BaseModel):
    template: str

class CrewIn(BaseModel):
    aircrew_id: int
    position: str

LOADOUTS = {
    "A/A": "AIM-120 x4 / AIM-9 x2 / centerline tank",
    "A/G": "GBU-12 x2 / AIM-9 x2 / fuel",
    "SEAD": "AGM-88 x2 / AIM-120 x2 / ECM",
    "clean": "none",
}

# --- endpoints ---
@app.get("/aircraft")
def list_aircraft():
    with db() as c:
        return [dict(r) for r in c.execute("SELECT * FROM aircraft")]

@app.get("/aircrew")
def list_aircrew():
    with db() as c:
        return [dict(r) for r in c.execute("SELECT * FROM aircrew")]

@app.get("/sorties")
def list_sorties():
    with db() as c:
        rows = c.execute("SELECT * FROM sorties ORDER BY takeoff").fetchall()
        out = []
        for r in rows:
            s = dict(r)
            s["crew"] = [dict(a) for a in c.execute(
                "SELECT a.position, ac.name, ac.id as aircrew_id FROM assignments a JOIN aircrew ac ON a.aircrew_id=ac.id WHERE a.sortie_id=?",
                (r["id"],)
            )]
            out.append(s)
        return out

@app.patch("/sorties/{sid}/aircraft")
def assign_aircraft(sid: int, body: TailIn):
    with db() as c:
        ac = c.execute("SELECT * FROM aircraft WHERE tail=?", (body.tail,)).fetchone()
        if not ac:
            raise HTTPException(404, "tail not found")
        if ac["status"] not in ("MC", "PMC"):
            raise HTTPException(409, "aircraft not mission capable")
        # simple overlap: any other sortie same tail same day
        s = c.execute("SELECT takeoff FROM sorties WHERE id=?", (sid,)).fetchone()
        if not s:
            raise HTTPException(404, "sortie not found")
        day = s["takeoff"][:10]
        conflict = c.execute(
            "SELECT id FROM sorties WHERE tail=? AND id!=? AND takeoff LIKE ?",
            (body.tail, sid, f"{day}%")
        ).fetchone()
        if conflict:
            raise HTTPException(409, f"tail already assigned that day (sortie {conflict['id']})")
        c.execute("UPDATE sorties SET tail=? WHERE id=?", (body.tail, sid))
    return {"ok": True}

@app.patch("/sorties/{sid}/loadout")
def apply_loadout(sid: int, body: LoadoutIn):
    lo = LOADOUTS.get(body.template)
    if not lo:
        raise HTTPException(400, f"unknown template, use one of {list(LOADOUTS)}")
    with db() as c:
        if not c.execute("SELECT 1 FROM sorties WHERE id=?", (sid,)).fetchone():
            raise HTTPException(404, "sortie not found")
        c.execute("UPDATE sorties SET loadout=? WHERE id=?", (lo, sid))
    return {"ok": True, "loadout": lo}

@app.post("/sorties/{sid}/crew")
def assign_crew(sid: int, body: CrewIn):
    with db() as c:
        ac = c.execute("SELECT * FROM aircrew WHERE id=?", (body.aircrew_id,)).fetchone()
        if not ac:
            raise HTTPException(404, "aircrew not found")
        s = c.execute("SELECT takeoff FROM sorties WHERE id=?", (sid,)).fetchone()
        if not s:
            raise HTTPException(404, "sortie not found")
        # overlap check
        day = s["takeoff"][:10]
        conflict = c.execute("""
            SELECT s.id FROM assignments a JOIN sorties s ON a.sortie_id=s.id
            WHERE a.aircrew_id=? AND s.id!=? AND s.takeoff LIKE ?
        """, (body.aircrew_id, sid, f"{day}%")).fetchone()
        if conflict:
            raise HTTPException(409, f"crew already assigned that day (sortie {conflict['id']})")
        try:
            c.execute(
                "INSERT INTO assignments (sortie_id, aircrew_id, position) VALUES (?,?,?)",
                (sid, body.aircrew_id, body.position)
            )
        except sqlite3.IntegrityError:
            raise HTTPException(409, "position already filled")
    return {"ok": True}

@app.patch("/sorties/{sid}/status")
def set_status(sid: int, status: str):
    with db() as c:
        c.execute("UPDATE sorties SET status=? WHERE id=?", (status, sid))
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
