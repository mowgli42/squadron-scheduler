"""Aircraft scheduling rules: windows, turns, config fit, load-crew estimates.

Choice: time-window conflicts with a turn buffer (not same-calendar-day only).
Reason: four-ship days reuse jets; day-level locks are too coarse for the desk.
Revisit: live MX pad/turn times from Ops–MX feed → production bead P4.
"""
from __future__ import annotations

from datetime import datetime, timedelta

TURN_BUFFER_MINUTES = 30

LOAD_CREW_MINUTES = {
    "A/A": 45,
    "A/G": 60,
    "SEAD": 75,
    "clean": 15,
}

# Aircraft config → loadout templates it can accept (clean fits all).
CONFIG_ALLOWS = {
    "clean": {"A/A", "A/G", "SEAD", "clean"},
    "A/A": {"A/A", "clean"},
    "A/G": {"A/G", "clean"},
    "SEAD": {"SEAD", "clean"},
}


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def sortie_window(sortie: dict, default_duration_minutes: int = 90):
    """Return (takeoff, land) datetimes. Land defaults to takeoff + duration."""
    takeoff = parse_iso(sortie.get("takeoff"))
    if not takeoff:
        return None, None
    land = parse_iso(sortie.get("land"))
    if not land:
        land = takeoff + timedelta(minutes=default_duration_minutes)
    return takeoff, land


def windows_overlap(a0, a1, b0, b1, buffer_minutes: int = TURN_BUFFER_MINUTES) -> bool:
    """True if windows conflict including post-land turn buffer on each side."""
    if not all((a0, a1, b0, b1)):
        return False
    buf = timedelta(minutes=buffer_minutes)
    # Inclusive at the boundary: next takeoff must be after land + turn buffer.
    return a0 <= (b1 + buf) and b0 <= (a1 + buf)


def template_of_loadout(loadout_text: str | None, loadouts: dict) -> str | None:
    if not loadout_text:
        return None
    for name, text in loadouts.items():
        if text == loadout_text:
            return name
    return None


def config_compatible(aircraft_config: str | None, template: str | None) -> bool:
    if not template:
        return True
    allowed = CONFIG_ALLOWS.get(aircraft_config or "clean", {"clean"})
    return template in allowed


def load_crew_minutes(template: str | None) -> int | None:
    if not template:
        return None
    return LOAD_CREW_MINUTES.get(template)
