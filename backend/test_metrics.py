"""Unit tests for derived process stages and readiness metrics."""
import unittest

from metrics import annotate, blockers, stage_of, summarize


def sortie(**kw):
    base = {
        "id": 1,
        "takeoff": "2026-08-04T08:00",
        "mission": "A/A",
        "tail": None,
        "loadout": None,
        "status": "planned",
        "crew": [],
    }
    base.update(kw)
    return base


class StageTests(unittest.TestCase):
    def test_empty_is_planned(self):
        self.assertEqual(stage_of(sortie()), "planned")
        self.assertEqual(blockers(sortie()), ["missing tail", "missing loadout", "missing pilot", "missing WSO"])

    def test_tail_only(self):
        self.assertEqual(stage_of(sortie(tail="87-0321")), "tail")

    def test_loadout_without_crew(self):
        self.assertEqual(stage_of(sortie(tail="87-0321", loadout="AIM-120 x4")), "loadout")

    def test_full_crew_is_crewed(self):
        s = sortie(
            tail="87-0321",
            loadout="AIM-120 x4",
            crew=[{"position": "pilot", "name": "Reyes"}, {"position": "wso", "name": "Torres"}],
        )
        self.assertEqual(stage_of(s), "crewed")
        self.assertEqual(blockers(s), [])

    def test_status_overrides_to_ready_and_airborne(self):
        crew = [{"position": "pilot"}, {"position": "wso"}]
        self.assertEqual(stage_of(sortie(status="crew-ready", crew=crew, tail="x", loadout="y")), "crew-ready")
        self.assertEqual(stage_of(sortie(status="airborne", crew=crew, tail="x", loadout="y")), "airborne")

    def test_annotate_flags_executable(self):
        ready = annotate(sortie(status="crew-ready", tail="x", loadout="y",
                                crew=[{"position": "pilot"}, {"position": "wso"}]))
        empty = annotate(sortie())
        self.assertTrue(ready["executable"])
        self.assertFalse(empty["executable"])


class SummaryTests(unittest.TestCase):
    def test_empty_board_points_at_missing_tail(self):
        snap = summarize([sortie(id=1), sortie(id=2, mission="A/G")])
        self.assertEqual(snap["executable_pct"], 0)
        self.assertEqual(snap["next_action"], "missing tail")
        self.assertEqual(len(snap["exceptions"]), 2)
        self.assertEqual(snap["funnel"]["planned"], 2)

    def test_launch_stage_metrics(self):
        crew = [{"position": "pilot"}, {"position": "wso"}]
        rows = [
            sortie(id=1, status="airborne", tail="a", loadout="x", crew=crew),
            sortie(id=2, status="airborne", tail="b", loadout="x", crew=crew),
            sortie(id=3, status="crew-ready", tail="c", loadout="x", crew=crew),
            sortie(id=4, status="crew-ready", tail="d", loadout="x", crew=crew),
        ]
        snap = summarize(rows, aircraft=[{"status": "MC"}] * 4)
        self.assertEqual(snap["executable_pct"], 100)
        self.assertEqual(snap["airborne"], 2)
        self.assertEqual(snap["next_action"], "all lines executable")
        self.assertEqual(snap["exceptions"], [])
        self.assertEqual(snap["aircraft_available"], 4)


if __name__ == "__main__":
    unittest.main()
