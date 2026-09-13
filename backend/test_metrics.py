"""Unit tests for aircraft rules and readiness metrics."""
import unittest

from aircraft_rules import (
    config_compatible,
    load_crew_minutes,
    sortie_window,
    windows_overlap,
)
from metrics import annotate, blockers, hard_blockers, stage_of, summarize
from sample_data import LOADOUTS


def sortie(**kw):
    base = {
        "id": 1,
        "takeoff": "2026-08-04T08:00",
        "land": "2026-08-04T09:30",
        "mission": "A/A",
        "callsign": "Viper 1",
        "line_number": 1,
        "tail": None,
        "spare_tail": None,
        "loadout": None,
        "status": "planned",
        "er_signed": False,
        "crew": [],
    }
    base.update(kw)
    return base


class RulesTests(unittest.TestCase):
    def test_turn_buffer_blocks_exact_boundary(self):
        a0, a1 = sortie_window(
            {"takeoff": "2026-08-04T08:00", "land": "2026-08-04T09:30"}
        )
        b0, b1 = sortie_window(
            {"takeoff": "2026-08-04T10:00", "land": "2026-08-04T11:30"}
        )
        self.assertTrue(windows_overlap(a0, a1, b0, b1))

    def test_non_overlapping_after_buffer(self):
        a0, a1 = sortie_window(
            {"takeoff": "2026-08-04T08:00", "land": "2026-08-04T09:30"}
        )
        b0, b1 = sortie_window(
            {"takeoff": "2026-08-04T10:01", "land": "2026-08-04T11:31"}
        )
        self.assertFalse(windows_overlap(a0, a1, b0, b1))

    def test_config_fit(self):
        self.assertTrue(config_compatible("clean", "A/G"))
        self.assertTrue(config_compatible("A/A", "A/A"))
        self.assertFalse(config_compatible("A/A", "A/G"))

    def test_load_crew_minutes(self):
        self.assertEqual(load_crew_minutes("SEAD"), 75)


class StageTests(unittest.TestCase):
    def test_empty_is_planned(self):
        s = sortie()
        self.assertEqual(stage_of(s), "planned")
        self.assertIn("missing tail", blockers(s))
        self.assertIn("missing spare", blockers(s))
        self.assertNotIn("missing spare", hard_blockers(s))

    def test_config_mismatch_blocker(self):
        s = annotate(
            sortie(tail="87-0322", loadout=LOADOUTS["A/G"]),
            {"87-0322": {"tail": "87-0322", "config": "A/A", "status": "MC"}},
        )
        self.assertIn("config mismatch", s["blockers"])

    def test_executable_requires_crew_ready_status(self):
        crew = [{"position": "pilot"}, {"position": "wso"}]
        ready = annotate(
            sortie(
                status="crew-ready",
                tail="x",
                spare_tail="y",
                loadout="z",
                er_signed=True,
                crew=crew,
            )
        )
        empty = annotate(sortie())
        self.assertTrue(ready["executable"])
        self.assertFalse(empty["executable"])


class SummaryTests(unittest.TestCase):
    def test_empty_board_points_at_missing_tail(self):
        snap = summarize([sortie(id=1), sortie(id=2, mission="A/G")])
        self.assertEqual(snap["executable_pct"], 0)
        self.assertEqual(snap["next_action"], "missing tail")
        self.assertEqual(len(snap["exceptions"]), 2)

    def test_launch_metrics_include_spares(self):
        crew = [{"position": "pilot"}, {"position": "wso"}]
        rows = [
            sortie(
                id=i,
                status="airborne" if i < 3 else "crew-ready",
                tail=f"a{i}",
                spare_tail="spare",
                loadout="x",
                er_signed=True,
                crew=crew,
            )
            for i in range(1, 5)
        ]
        snap = summarize(rows, aircraft=[{"tail": f"t{i}", "status": "MC"} for i in range(5)])
        self.assertEqual(snap["executable_pct"], 100)
        self.assertEqual(snap["spares_assigned"], 4)
        self.assertEqual(snap["airborne"], 2)
        self.assertEqual(snap["exceptions"], [])


if __name__ == "__main__":
    unittest.main()
