"""Process stage + readiness metrics.

Choice: derive stage from existing fields instead of a new status column.
Alternative: replace planned/crew-ready/airborne with a six-step enum.
Reason: demo stages 01–06 and assignment APIs stay intact; stage is insight.
Revisit in production: explicit state machine with legal transitions → bead P2.
"""
from aircraft_rules import config_compatible, load_crew_minutes, template_of_loadout
from sample_data import LOADOUTS


# Alias kept for readability in callers / older notes.

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


def _template(sortie):
    if sortie.get("loadout_template"):
        return sortie["loadout_template"]
    return template_of_loadout(sortie.get("loadout"), LOADOUTS)


def blockers(sortie, aircraft_by_tail=None):
    """Missing pieces / aircraft risks that keep a line from being clear."""
    out = []
    if not sortie.get("tail"):
        out.append("missing tail")
    if not sortie.get("spare_tail"):
        out.append("missing spare")
    if not sortie.get("loadout"):
        out.append("missing loadout")
    if not _has_role(sortie, "pilot"):
        out.append("missing pilot")
    if not _has_role(sortie, "wso"):
        out.append("missing WSO")
    if not sortie.get("er_signed"):
        out.append("missing ER")
    ac_map = aircraft_by_tail or {}
    tail = sortie.get("tail")
    tmpl = _template(sortie)
    if tail and tmpl and tail in ac_map:
        if not config_compatible(ac_map[tail].get("config"), tmpl):
            out.append("config mismatch")
    return out


def hard_blockers(sortie, aircraft_by_tail=None):
    """Blockers that prevent crew-ready (spare is soft pressure only)."""
    soft = {"missing spare"}
    return [b for b in blockers(sortie, aircraft_by_tail) if b not in soft]


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


def annotate(sortie, aircraft_by_tail=None):
    s = dict(sortie)
    tmpl = _template(s)
    s["loadout_template"] = tmpl
    s["load_crew_minutes"] = s.get("load_crew_minutes") or load_crew_minutes(tmpl)
    s["stage"] = stage_of(s)
    s["blockers"] = blockers(s, aircraft_by_tail)
    s["hard_blockers"] = hard_blockers(s, aircraft_by_tail)
    s["executable"] = s["stage"] in ("crew-ready", "airborne")
    s["er_signed"] = bool(s.get("er_signed"))
    return s


def summarize(sorties, aircraft=None):
    """Decision-first snapshot for the scheduler desk.

    Primary question: can we generate today's go?
    Primary metric: executable_pct (crew-ready or airborne / total).
    """
    ac_list = aircraft or []
    ac_map = {a["tail"]: a for a in ac_list if a.get("tail")}
    rows = [annotate(s, ac_map) for s in sorties]
    total = len(rows) or 0
    funnel = {k: 0 for k in STAGES}
    for r in rows:
        funnel[r["stage"]] += 1

    tails = sum(1 for r in rows if r.get("tail"))
    spares = sum(1 for r in rows if r.get("spare_tail"))
    loads = sum(1 for r in rows if r.get("loadout"))
    crewed = sum(1 for r in rows if r["stage"] in ("crewed", "crew-ready", "airborne"))
    executable = sum(1 for r in rows if r["executable"])
    airborne = funnel["airborne"]
    er_signed = sum(1 for r in rows if r.get("er_signed"))
    config_mismatches = sum(1 for r in rows if "config mismatch" in r["blockers"])
    mc = sum(1 for a in ac_list if a.get("status") in ("MC", "PMC"))

    gap_counts = {}
    for r in rows:
        if r["blockers"] and r["stage"] not in ("crew-ready", "airborne"):
            gap_counts[r["blockers"][0]] = gap_counts.get(r["blockers"][0], 0) + 1
    next_action = (
        max(gap_counts, key=gap_counts.get) if gap_counts else "all lines executable"
    )

    return {
        "sorties_total": total,
        "executable": executable,
        "executable_pct": round(100 * executable / total) if total else 0,
        "tails_assigned": tails,
        "spares_assigned": spares,
        "loadouts_applied": loads,
        "crew_complete": crewed,
        "er_signed": er_signed,
        "airborne": airborne,
        "aircraft_available": mc,
        "aircraft_total": len(ac_list),
        "config_mismatches": config_mismatches,
        "funnel": funnel,
        "next_action": next_action,
        "exceptions": [
            {
                "id": r.get("id"),
                "mission": r.get("mission"),
                "callsign": r.get("callsign"),
                "takeoff": r.get("takeoff"),
                "stage": r["stage"],
                "blockers": r["blockers"],
            }
            for r in rows
            if r["blockers"] and r["stage"] not in ("crew-ready", "airborne")
        ],
    }
