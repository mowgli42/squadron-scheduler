"""Process stage + readiness metrics.

Choice: derive stage from existing fields instead of a new status column.
Alternative considered: replace planned/crew-ready/airborne with a six-step enum.
Reason: demo stages 01–06 and existing tests keep working; stage is insight, not storage.
Revisit in production: explicit state machine with legal transitions → bead P2.
"""

STAGES = ("planned", "tail", "loadout", "crewed", "crew-ready", "airborne")

STAGE_LABELS = {
    "planned": "Planned",
    "tail": "Tail assigned",
    "loadout": "Loadout set",
    "crewed": "Crew filled",
    "crew-ready": "Crew-ready",
    "airborne": "Airborne",
}


def _has_role(sortie, role):
    return any(c.get("position") == role for c in sortie.get("crew") or [])


def blockers(sortie):
    """Missing pieces that keep a sortie from being executable."""
    out = []
    if not sortie.get("tail"):
        out.append("missing tail")
    if not sortie.get("loadout"):
        out.append("missing loadout")
    if not _has_role(sortie, "pilot"):
        out.append("missing pilot")
    if not _has_role(sortie, "wso"):
        out.append("missing WSO")
    return out


def stage_of(sortie):
    """Furthest process step this sortie has actually completed."""
    status = sortie.get("status") or "planned"
    if status == "airborne":
        return "airborne"
    if status == "crew-ready":
        return "crew-ready"
    if _has_role(sortie, "pilot") and _has_role(sortie, "wso"):
        return "crewed"
    if sortie.get("loadout"):
        return "loadout"
    if sortie.get("tail"):
        return "tail"
    return "planned"


def annotate(sortie):
    s = dict(sortie)
    s["stage"] = stage_of(s)
    s["blockers"] = blockers(s)
    s["executable"] = s["stage"] in ("crew-ready", "airborne")
    return s


def summarize(sorties, aircraft=None):
    """Decision-first snapshot for the scheduler desk.

    Primary question: can we generate today's go?
    Primary metric: executable_pct (crew-ready or airborne / total).
    """
    rows = [annotate(s) for s in sorties]
    total = len(rows) or 0
    funnel = {k: 0 for k in STAGES}
    for r in rows:
        funnel[r["stage"]] += 1

    tails = sum(1 for r in rows if r.get("tail"))
    loads = sum(1 for r in rows if r.get("loadout"))
    crewed = sum(1 for r in rows if r["stage"] in ("crewed", "crew-ready", "airborne"))
    executable = sum(1 for r in rows if r["executable"])
    airborne = funnel["airborne"]

    ac = aircraft or []
    mc = sum(1 for a in ac if a.get("status") in ("MC", "PMC"))

    gap_counts = {}
    for r in rows:
        if r["blockers"]:
            gap_counts[r["blockers"][0]] = gap_counts.get(r["blockers"][0], 0) + 1
    next_action = max(gap_counts, key=gap_counts.get) if gap_counts else "all lines executable"

    return {
        "sorties_total": total,
        "executable": executable,
        "executable_pct": round(100 * executable / total) if total else 0,
        "tails_assigned": tails,
        "loadouts_applied": loads,
        "crew_complete": crewed,
        "airborne": airborne,
        "aircraft_available": mc,
        "aircraft_total": len(ac),
        "funnel": funnel,
        "next_action": next_action,
        "exceptions": [
            {
                "id": r.get("id"),
                "mission": r.get("mission"),
                "takeoff": r.get("takeoff"),
                "stage": r["stage"],
                "blockers": r["blockers"],
            }
            for r in rows
            if r["blockers"] and r["stage"] not in ("crew-ready", "airborne")
        ],
    }
