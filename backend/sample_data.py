"""Sample squadron data and demo build-up stages (empty board → launch)."""
from datetime import datetime, timedelta

# Fixed demo day so tests and screenshots stay deterministic.
DEMO_DAY = datetime(2026, 8, 4, 8, 0, 0)

AIRCRAFT = [
    ("87-0321", "MC", "clean"),
    ("87-0322", "MC", "A/A"),
    ("87-0325", "PMC", "clean"),
    ("87-0330", "MC", "clean"),
]

AIRCREW = [
    (1, "Capt Reyes", "pilot", "IP,A/A", None),
    (2, "Capt Kim", "pilot", "MP,A/A", None),
    (3, "1Lt Torres", "wso", "WSO,A/A", None),
    (4, "Capt Hale", "wso", "WSO,A/A", None),
    (5, "Maj Ortiz", "pilot", "IP,SEAD", None),
    (6, "Capt Nguyen", "wso", "WSO,SEAD", None),
    (7, "Capt Brooks", "pilot", "MP,A/G", None),
    (8, "1Lt Park", "wso", "WSO,A/G", None),
]

# Four-ship morning go: A/A, A/G, A/A, SEAD every two hours from 08:00.
MISSIONS = ["A/A", "A/G", "A/A", "SEAD"]

LOADOUTS = {
    "A/A": "AIM-120 x4 / AIM-9 x2 / centerline tank",
    "A/G": "GBU-12 x2 / AIM-9 x2 / fuel",
    "SEAD": "AGM-88 x2 / AIM-120 x2 / ECM",
    "clean": "none",
}

STATUSES = ("planned", "crew-ready", "airborne")

# Cumulative stages for the morning-go demo (sortie index 0..3).
DEMO_STAGES = [
    {
        "id": "01-empty-board",
        "title": "Empty board — sorties planned, nothing assigned",
        "tails": {},
        "loadouts": {},
        "crew": {},
        "status": {},
    },
    {
        "id": "02-tails-assigned",
        "title": "Tails on the line — primary aircraft assigned",
        "tails": {0: "87-0321", 1: "87-0322", 2: "87-0325", 3: "87-0330"},
        "loadouts": {},
        "crew": {},
        "status": {},
    },
    {
        "id": "03-loadouts-applied",
        "title": "Loadouts applied — weapons templates set",
        "tails": {0: "87-0321", 1: "87-0322", 2: "87-0325", 3: "87-0330"},
        "loadouts": {0: "A/A", 1: "A/G", 2: "A/A", 3: "SEAD"},
        "crew": {},
        "status": {},
    },
    {
        "id": "04-crew-filled",
        "title": "Crew filled — pilot and WSO on every jet",
        "tails": {0: "87-0321", 1: "87-0322", 2: "87-0325", 3: "87-0330"},
        "loadouts": {0: "A/A", 1: "A/G", 2: "A/A", 3: "SEAD"},
        "crew": {
            0: [(1, "pilot"), (3, "wso")],
            1: [(2, "pilot"), (4, "wso")],
            2: [(7, "pilot"), (8, "wso")],
            3: [(5, "pilot"), (6, "wso")],
        },
        "status": {},
    },
    {
        "id": "05-crew-ready",
        "title": "Crew-ready — jets signed off for step",
        "tails": {0: "87-0321", 1: "87-0322", 2: "87-0325", 3: "87-0330"},
        "loadouts": {0: "A/A", 1: "A/G", 2: "A/A", 3: "SEAD"},
        "crew": {
            0: [(1, "pilot"), (3, "wso")],
            1: [(2, "pilot"), (4, "wso")],
            2: [(7, "pilot"), (8, "wso")],
            3: [(5, "pilot"), (6, "wso")],
        },
        "status": {0: "crew-ready", 1: "crew-ready", 2: "crew-ready", 3: "crew-ready"},
    },
    {
        "id": "06-launched",
        "title": "Launch — lead elements airborne",
        "tails": {0: "87-0321", 1: "87-0322", 2: "87-0325", 3: "87-0330"},
        "loadouts": {0: "A/A", 1: "A/G", 2: "A/A", 3: "SEAD"},
        "crew": {
            0: [(1, "pilot"), (3, "wso")],
            1: [(2, "pilot"), (4, "wso")],
            2: [(7, "pilot"), (8, "wso")],
            3: [(5, "pilot"), (6, "wso")],
        },
        "status": {0: "airborne", 1: "airborne", 2: "crew-ready", 3: "crew-ready"},
    },
]


def sortie_takeoffs(day: datetime | None = None):
    base = day or DEMO_DAY
    return [
        (base + timedelta(hours=i * 2)).isoformat(timespec="minutes")
        for i in range(len(MISSIONS))
    ]
