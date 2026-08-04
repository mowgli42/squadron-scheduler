"""Squadron Scheduler API — minimal FastAPI + SQLite."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from contextlib import contextmanager
from pathlib import Path
import os

from sample_data import (
    AIRCRAFT,
    AIRCREW,
    DEMO_STAGES,
    LOADOUTS,
    MISSIONS,
    STATUSES,
    sortie_takeoffs,
)

DB = Path(os.environ.get("SQUADRON_DB", Path(__file__).parent / "squadron.db"))
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


def _schema(c):
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


def seed(c, *, force=False):
    """Load sample aircraft/aircrew/sorties. force=True wipes assignments first."""
    if force:
        c.executescript(
            "DELETE FROM assignments; DELETE FROM sorties; DELETE FROM aircrew; DELETE FROM aircraft;"
        )
    elif c.execute("SELECT COUNT(*) FROM aircraft").fetchone()[0] > 0:
        return
    c.executemany("INSERT INTO aircraft VALUES (?,?,?)", AIRCRAFT)
    c.executemany("INSERT INTO aircrew VALUES (?,?,?,?,?)", AIRCREW)
    c.executemany(
        "INSERT INTO sorties (takeoff, mission, status) VALUES (?,?,?)",
        [(t, m, "planned") for t, m in zip(sortie_takeoffs(), MISSIONS)],
    )


def init():
    with db() as c:
        _schema(c)
        seed(c)


def configure(db_path):
    """Point the app at a fresh DB (tests / demo screenshots)."""
    global DB
    DB = Path(db_path)
    if DB.exists():
        DB.unlink()
    init()


def apply_demo_stage(stage_id: str):
    """Reset DB and apply one DEMO_STAGES entry by id. Returns the stage dict."""
    stage = next((s for s in DEMO_STAGES if s["id"] == stage_id), None)
    if not stage:
        raise ValueError(f"unknown stage {stage_id}")
    with db() as c:
        seed(c, force=True)
        sorties = c.execute("SELECT id FROM sorties ORDER BY takeoff").fetchall()
        ids = [r["id"] for r in sorties]
        for idx, tail in stage["tails"].items():
            c.execute("UPDATE sorties SET tail=? WHERE id=?", (tail, ids[idx]))
        for idx, template in stage["loadouts"].items():
            c.execute(
                "UPDATE sorties SET loadout=? WHERE id=?",
                (LOADOUTS[template], ids[idx]),
            )
        for idx, members in stage["crew"].items():
            for aircrew_id, position in members:
                c.execute(
                    "INSERT INTO assignments (sortie_id, aircrew_id, position) VALUES (?,?,?)",
                    (ids[idx], aircrew_id, position),
                )
        for idx, status in stage["status"].items():
            c.execute("UPDATE sorties SET status=? WHERE id=?", (status, ids[idx]))
    return stage


init()


class TailIn(BaseModel):
    tail: str


class LoadoutIn(BaseModel):
    template: str


class CrewIn(BaseModel):
    aircrew_id: int
    position: str


class StatusIn(BaseModel):
    status: str


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
            s["crew"] = [
                dict(a)
                for a in c.execute(
                    "SELECT a.position, ac.name, ac.id as aircrew_id FROM assignments a "
                    "JOIN aircrew ac ON a.aircrew_id=ac.id WHERE a.sortie_id=?",
                    (r["id"],),
                )
            ]
            out.append(s)
        return out


@app.get("/demo/stages")
def demo_stages():
    return [{"id": s["id"], "title": s["title"]} for s in DEMO_STAGES]


@app.post("/demo/stages/{stage_id}")
def demo_apply(stage_id: str):
    try:
        stage = apply_demo_stage(stage_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return {"ok": True, "id": stage["id"], "title": stage["title"]}


@app.patch("/sorties/{sid}/aircraft")
def assign_aircraft(sid: int, body: TailIn):
    with db() as c:
        ac = c.execute("SELECT * FROM aircraft WHERE tail=?", (body.tail,)).fetchone()
        if not ac:
            raise HTTPException(404, "tail not found")
        if ac["status"] not in ("MC", "PMC"):
            raise HTTPException(409, "aircraft not mission capable")
        s = c.execute("SELECT takeoff FROM sorties WHERE id=?", (sid,)).fetchone()
        if not s:
            raise HTTPException(404, "sortie not found")
        day = s["takeoff"][:10]
        conflict = c.execute(
            "SELECT id FROM sorties WHERE tail=? AND id!=? AND takeoff LIKE ?",
            (body.tail, sid, f"{day}%"),
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
        day = s["takeoff"][:10]
        conflict = c.execute(
            """
            SELECT s.id FROM assignments a JOIN sorties s ON a.sortie_id=s.id
            WHERE a.aircrew_id=? AND s.id!=? AND s.takeoff LIKE ?
            """,
            (body.aircrew_id, sid, f"{day}%"),
        ).fetchone()
        if conflict:
            raise HTTPException(409, f"crew already assigned that day (sortie {conflict['id']})")
        try:
            c.execute(
                "INSERT INTO assignments (sortie_id, aircrew_id, position) VALUES (?,?,?)",
                (sid, body.aircrew_id, body.position),
            )
        except sqlite3.IntegrityError:
            raise HTTPException(409, "position already filled")
    return {"ok": True}


@app.patch("/sorties/{sid}/status")
def set_status(sid: int, body: StatusIn):
    if body.status not in STATUSES:
        raise HTTPException(400, f"status must be one of {list(STATUSES)}")
    with db() as c:
        if not c.execute("SELECT 1 FROM sorties WHERE id=?", (sid,)).fetchone():
            raise HTTPException(404, "sortie not found")
        c.execute("UPDATE sorties SET status=? WHERE id=?", (body.status, sid))
    return {"ok": True, "status": body.status}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
