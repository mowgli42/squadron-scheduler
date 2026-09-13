"""Squadron Scheduler API — FastAPI + SQLite.

Aircraft scheduling: land windows, spare tails, turn conflicts, config fit,
ER gate, rest gate, crew replace, pen-and-ink log, aircraft day board.
"""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from aircraft_rules import sortie_window, windows_overlap
from metrics import annotate, summarize
from sample_data import (
    AIRCRAFT,
    AIRCREW,
    CALLSIGNS,
    DEMO_STAGES,
    LOADOUTS,
    MISSIONS,
    STATUSES,
    load_crew_for,
    sortie_lands,
    sortie_takeoffs,
)

DB = Path(os.environ.get("SQUADRON_DB", Path(__file__).parent / "squadron.db"))
app = FastAPI(title="Squadron Scheduler")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    c.executescript(
        """
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
            land TEXT,
            mission TEXT,
            callsign TEXT,
            line_number INTEGER,
            tail TEXT,
            spare_tail TEXT,
            loadout TEXT,
            load_crew_minutes INTEGER,
            er_signed INTEGER DEFAULT 0,
            status TEXT DEFAULT 'planned'
        );
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY,
            sortie_id INTEGER,
            aircrew_id INTEGER,
            position TEXT,
            UNIQUE(sortie_id, position)
        );
        CREATE TABLE IF NOT EXISTS change_log (
            id INTEGER PRIMARY KEY,
            at TEXT,
            sortie_id INTEGER,
            field TEXT,
            old_value TEXT,
            new_value TEXT,
            note TEXT
        );
        """
    )


def _log(c, sortie_id, field, old, new, note=""):
    c.execute(
        "INSERT INTO change_log (at, sortie_id, field, old_value, new_value, note) "
        "VALUES (?,?,?,?,?,?)",
        (
            datetime.utcnow().isoformat(timespec="seconds") + "Z",
            sortie_id,
            field,
            None if old is None else str(old),
            None if new is None else str(new),
            note,
        ),
    )


def seed(c, *, force=False):
    if force:
        c.executescript(
            "DELETE FROM change_log; DELETE FROM assignments; "
            "DELETE FROM sorties; DELETE FROM aircrew; DELETE FROM aircraft;"
        )
    elif c.execute("SELECT COUNT(*) FROM aircraft").fetchone()[0] > 0:
        return
    c.executemany("INSERT INTO aircraft VALUES (?,?,?)", AIRCRAFT)
    c.executemany("INSERT INTO aircrew VALUES (?,?,?,?,?)", AIRCREW)
    takeoffs = sortie_takeoffs()
    lands = sortie_lands()
    rows = [
        (takeoffs[i], lands[i], MISSIONS[i], CALLSIGNS[i], i + 1, "planned")
        for i in range(len(MISSIONS))
    ]
    c.executemany(
        "INSERT INTO sorties "
        "(takeoff, land, mission, callsign, line_number, status) "
        "VALUES (?,?,?,?,?,?)",
        rows,
    )


def init():
    with db() as c:
        _schema(c)
        seed(c)


def configure(db_path):
    """Point the app at a fresh DB (tests / screenshots)."""
    global DB
    DB = Path(db_path)
    if DB.exists():
        DB.unlink()
    init()


def _aircraft_map(c):
    return {r["tail"]: dict(r) for r in c.execute("SELECT * FROM aircraft")}


def _sortie_row(c, sid):
    row = c.execute("SELECT * FROM sorties WHERE id=?", (sid,)).fetchone()
    if not row:
        return None
    s = dict(row)
    s["er_signed"] = bool(s.get("er_signed"))
    return s


def _sorties_with_crew(c):
    ac_map = _aircraft_map(c)
    rows = c.execute("SELECT * FROM sorties ORDER BY takeoff").fetchall()
    out = []
    for r in rows:
        s = dict(r)
        s["er_signed"] = bool(s.get("er_signed"))
        s["crew"] = [
            dict(a)
            for a in c.execute(
                "SELECT a.position, ac.name, ac.id as aircrew_id "
                "FROM assignments a JOIN aircrew ac ON a.aircrew_id=ac.id "
                "WHERE a.sortie_id=?",
                (r["id"],),
            )
        ]
        out.append(annotate(s, ac_map))
    return out


def _conflict_msg(tail, other_id, role):
    return f"tail {tail} already {role} on overlapping sortie {other_id}"


def _aircraft_window_conflict(c, sid, tail, *, as_primary: bool):
    """Primary consumes the window; ground spare may cover many lines.

    Conflict when:
    - this jet is already primary on an overlapping sortie, or
    - assigning as primary while the jet is spare on an overlapping sortie.
    """
    target = _sortie_row(c, sid)
    if not target:
        return "sortie not found"
    t0, t1 = sortie_window(target)
    others = c.execute(
        "SELECT * FROM sorties WHERE id!=? AND (tail=? OR spare_tail=?)",
        (sid, tail, tail),
    ).fetchall()
    for raw in others:
        other = dict(raw)
        o0, o1 = sortie_window(other)
        if not windows_overlap(t0, t1, o0, o1):
            continue
        if other.get("tail") == tail:
            return _conflict_msg(tail, other["id"], "primary")
        if as_primary and other.get("spare_tail") == tail:
            return _conflict_msg(tail, other["id"], "spare")
    return None


def apply_demo_stage(stage_id: str):
    stage = next((s for s in DEMO_STAGES if s["id"] == stage_id), None)
    if not stage:
        raise ValueError(f"unknown stage {stage_id}")
    with db() as c:
        seed(c, force=True)
        ids = [
            r["id"]
            for r in c.execute("SELECT id FROM sorties ORDER BY takeoff").fetchall()
        ]
        for idx, tail in stage["tails"].items():
            c.execute("UPDATE sorties SET tail=? WHERE id=?", (tail, ids[idx]))
        for idx, spare in stage["spares"].items():
            c.execute(
                "UPDATE sorties SET spare_tail=? WHERE id=?", (spare, ids[idx])
            )
        for idx, template in stage["loadouts"].items():
            c.execute(
                "UPDATE sorties SET loadout=?, load_crew_minutes=? WHERE id=?",
                (LOADOUTS[template], load_crew_for(template), ids[idx]),
            )
        for idx, members in stage["crew"].items():
            for aircrew_id, position in members:
                c.execute(
                    "INSERT INTO assignments (sortie_id, aircrew_id, position) "
                    "VALUES (?,?,?)",
                    (ids[idx], aircrew_id, position),
                )
        for idx, er in stage["er_signed"].items():
            c.execute(
                "UPDATE sorties SET er_signed=? WHERE id=?", (int(er), ids[idx])
            )
        for idx, status in stage["status"].items():
            c.execute(
                "UPDATE sorties SET status=? WHERE id=?", (status, ids[idx])
            )
    return stage


init()


class TailIn(BaseModel):
    tail: str


class SpareIn(BaseModel):
    spare_tail: str


class LoadoutIn(BaseModel):
    template: str


class CrewIn(BaseModel):
    aircrew_id: int
    position: str


class StatusIn(BaseModel):
    status: str


class ERIn(BaseModel):
    signed: bool = True


@app.get("/aircraft")
def list_aircraft():
    with db() as c:
        return [dict(r) for r in c.execute("SELECT * FROM aircraft")]


@app.get("/aircraft/schedule")
def aircraft_schedule():
    """Asset-centric day board: each jet and its primary/spare commitments."""
    with db() as c:
        aircraft = [dict(r) for r in c.execute("SELECT * FROM aircraft")]
        sorties = [
            dict(r) for r in c.execute("SELECT * FROM sorties ORDER BY takeoff")
        ]
    out = []
    for ac in aircraft:
        commitments = []
        for s in sorties:
            role = None
            if s.get("tail") == ac["tail"]:
                role = "primary"
            elif s.get("spare_tail") == ac["tail"]:
                role = "spare"
            if role:
                commitments.append(
                    {
                        "sortie_id": s["id"],
                        "role": role,
                        "callsign": s.get("callsign"),
                        "mission": s.get("mission"),
                        "takeoff": s.get("takeoff"),
                        "land": s.get("land"),
                        "status": s.get("status"),
                    }
                )
        out.append({**ac, "commitments": commitments})
    return out


@app.get("/aircrew")
def list_aircrew():
    with db() as c:
        return [dict(r) for r in c.execute("SELECT * FROM aircrew")]


@app.get("/sorties")
def list_sorties():
    with db() as c:
        return _sorties_with_crew(c)


@app.get("/metrics")
def get_metrics():
    with db() as c:
        sorties = _sorties_with_crew(c)
        aircraft = [dict(r) for r in c.execute("SELECT * FROM aircraft")]
    return summarize(sorties, aircraft)


@app.get("/changes")
def list_changes(limit: int = 50):
    with db() as c:
        rows = c.execute(
            "SELECT * FROM change_log ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


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
        ac = c.execute(
            "SELECT * FROM aircraft WHERE tail=?", (body.tail,)
        ).fetchone()
        if not ac:
            raise HTTPException(404, "tail not found")
        if ac["status"] not in ("MC", "PMC"):
            raise HTTPException(409, "aircraft not mission capable")
        s = _sortie_row(c, sid)
        if not s:
            raise HTTPException(404, "sortie not found")
        if s.get("spare_tail") == body.tail:
            raise HTTPException(409, "spare cannot equal primary")
        conflict = _aircraft_window_conflict(c, sid, body.tail, as_primary=True)
        if conflict:
            raise HTTPException(409, conflict)
        old = s.get("tail")
        c.execute("UPDATE sorties SET tail=? WHERE id=?", (body.tail, sid))
        _log(c, sid, "tail", old, body.tail)
    return {"ok": True}


@app.patch("/sorties/{sid}/spare")
def assign_spare(sid: int, body: SpareIn):
    with db() as c:
        ac = c.execute(
            "SELECT * FROM aircraft WHERE tail=?", (body.spare_tail,)
        ).fetchone()
        if not ac:
            raise HTTPException(404, "tail not found")
        if ac["status"] not in ("MC", "PMC"):
            raise HTTPException(409, "aircraft not mission capable")
        s = _sortie_row(c, sid)
        if not s:
            raise HTTPException(404, "sortie not found")
        if s.get("tail") == body.spare_tail:
            raise HTTPException(409, "spare cannot equal primary")
        conflict = _aircraft_window_conflict(
            c, sid, body.spare_tail, as_primary=False
        )
        if conflict:
            raise HTTPException(409, conflict)
        old = s.get("spare_tail")
        c.execute(
            "UPDATE sorties SET spare_tail=? WHERE id=?",
            (body.spare_tail, sid),
        )
        _log(c, sid, "spare_tail", old, body.spare_tail)
    return {"ok": True}


@app.patch("/sorties/{sid}/loadout")
def apply_loadout(sid: int, body: LoadoutIn):
    lo = LOADOUTS.get(body.template)
    if not lo:
        raise HTTPException(400, f"unknown template, use one of {list(LOADOUTS)}")
    mins = load_crew_for(body.template)
    with db() as c:
        s = _sortie_row(c, sid)
        if not s:
            raise HTTPException(404, "sortie not found")
        old = s.get("loadout")
        c.execute(
            "UPDATE sorties SET loadout=?, load_crew_minutes=? WHERE id=?",
            (lo, mins, sid),
        )
        _log(c, sid, "loadout", old, lo)
    return {"ok": True, "loadout": lo, "load_crew_minutes": mins}


@app.post("/sorties/{sid}/crew")
def assign_crew(sid: int, body: CrewIn):
    if body.position not in ("pilot", "wso"):
        raise HTTPException(400, "position must be pilot or wso")
    with db() as c:
        ac = c.execute(
            "SELECT * FROM aircrew WHERE id=?", (body.aircrew_id,)
        ).fetchone()
        if not ac:
            raise HTTPException(404, "aircrew not found")
        if ac["role"] != body.position:
            raise HTTPException(
                409, f"aircrew role is {ac['role']}, not {body.position}"
            )
        s = _sortie_row(c, sid)
        if not s:
            raise HTTPException(404, "sortie not found")
        if ac["rest_until"] and ac["rest_until"] > s["takeoff"]:
            raise HTTPException(
                409, f"insufficient rest until {ac['rest_until']}"
            )
        t0, t1 = sortie_window(s)
        others = c.execute(
            """
            SELECT s.id, s.takeoff, s.land FROM assignments a
            JOIN sorties s ON a.sortie_id = s.id
            WHERE a.aircrew_id=? AND s.id!=?
            """,
            (body.aircrew_id, sid),
        ).fetchall()
        for other in others:
            o0, o1 = sortie_window(dict(other))
            if windows_overlap(t0, t1, o0, o1):
                raise HTTPException(
                    409,
                    f"crew already assigned on overlapping sortie {other['id']}",
                )
        existing = c.execute(
            "SELECT aircrew_id FROM assignments "
            "WHERE sortie_id=? AND position=?",
            (sid, body.position),
        ).fetchone()
        old = existing["aircrew_id"] if existing else None
        if existing:
            c.execute(
                "UPDATE assignments SET aircrew_id=? "
                "WHERE sortie_id=? AND position=?",
                (body.aircrew_id, sid, body.position),
            )
        else:
            c.execute(
                "INSERT INTO assignments (sortie_id, aircrew_id, position) "
                "VALUES (?,?,?)",
                (sid, body.aircrew_id, body.position),
            )
        _log(c, sid, f"crew:{body.position}", old, body.aircrew_id)
    return {"ok": True}


@app.patch("/sorties/{sid}/er")
def set_er(sid: int, body: ERIn):
    with db() as c:
        s = _sortie_row(c, sid)
        if not s:
            raise HTTPException(404, "sortie not found")
        old = int(bool(s.get("er_signed")))
        new = int(bool(body.signed))
        c.execute("UPDATE sorties SET er_signed=? WHERE id=?", (new, sid))
        _log(c, sid, "er_signed", old, new, note="MX ER")
    return {"ok": True, "er_signed": bool(body.signed)}


@app.patch("/sorties/{sid}/status")
def set_status(sid: int, body: StatusIn):
    if body.status not in STATUSES:
        raise HTTPException(400, f"status must be one of {list(STATUSES)}")
    with db() as c:
        sorties = _sorties_with_crew(c)
        s = next((x for x in sorties if x["id"] == sid), None)
        if not s:
            raise HTTPException(404, "sortie not found")
        if body.status == "crew-ready":
            if not s.get("er_signed"):
                raise HTTPException(409, "ER not signed")
            if s.get("hard_blockers"):
                raise HTTPException(
                    409,
                    f"cannot go crew-ready: {', '.join(s['hard_blockers'])}",
                )
        if body.status == "airborne" and s.get("status") not in (
            "crew-ready",
            "airborne",
        ):
            raise HTTPException(409, "must be crew-ready before airborne")
        old = s.get("status")
        c.execute("UPDATE sorties SET status=? WHERE id=?", (body.status, sid))
        _log(c, sid, "status", old, body.status)
    return {"ok": True, "status": body.status}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
