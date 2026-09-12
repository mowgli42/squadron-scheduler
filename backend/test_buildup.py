"""Unit tests: sample-data demo build-up from empty board to launch."""
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import main
from sample_data import DEMO_STAGES, LOADOUTS, MISSIONS


class DemoBuildupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        main.configure(self.tmp.name)
        self.client = TestClient(main.app)

    def tearDown(self):
        Path(self.tmp.name).unlink(missing_ok=True)

    def test_sample_seed_has_four_ship_go(self):
        aircraft = self.client.get("/aircraft").json()
        aircrew = self.client.get("/aircrew").json()
        sorties = self.client.get("/sorties").json()
        self.assertEqual(len(aircraft), 4)
        self.assertEqual(len(aircrew), 8)
        self.assertEqual([s["mission"] for s in sorties], MISSIONS)
        self.assertTrue(all(s["takeoff"].startswith("2026-08-04T") for s in sorties))
        self.assertTrue(all(s["status"] == "planned" and not s["tail"] for s in sorties))

    def test_demo_stages_listed(self):
        stages = self.client.get("/demo/stages").json()
        self.assertEqual([s["id"] for s in stages], [s["id"] for s in DEMO_STAGES])

    def test_stage_01_empty_board(self):
        r = self.client.post("/demo/stages/01-empty-board")
        self.assertEqual(r.status_code, 200)
        sorties = self.client.get("/sorties").json()
        self.assertEqual(len(sorties), 4)
        for s in sorties:
            self.assertIsNone(s["tail"])
            self.assertIsNone(s["loadout"])
            self.assertEqual(s["crew"], [])
            self.assertEqual(s["status"], "planned")
            self.assertEqual(s["stage"], "planned")

    def test_stage_02_tails_assigned(self):
        self.client.post("/demo/stages/02-tails-assigned")
        sorties = self.client.get("/sorties").json()
        tails = [s["tail"] for s in sorties]
        self.assertEqual(tails, ["87-0321", "87-0322", "87-0325", "87-0330"])
        self.assertTrue(all(s["loadout"] is None for s in sorties))
        self.assertTrue(all(s["stage"] == "tail" for s in sorties))

    def test_stage_03_loadouts_applied(self):
        self.client.post("/demo/stages/03-loadouts-applied")
        sorties = self.client.get("/sorties").json()
        expected = [LOADOUTS[m] for m in MISSIONS]
        self.assertEqual([s["loadout"] for s in sorties], expected)
        self.assertTrue(all(s["stage"] == "loadout" for s in sorties))

    def test_stage_04_crew_filled(self):
        self.client.post("/demo/stages/04-crew-filled")
        sorties = self.client.get("/sorties").json()
        for s in sorties:
            positions = {c["position"] for c in s["crew"]}
            self.assertEqual(positions, {"pilot", "wso"})
            self.assertEqual(s["status"], "planned")
            self.assertEqual(s["stage"], "crewed")

    def test_stage_05_crew_ready(self):
        self.client.post("/demo/stages/05-crew-ready")
        sorties = self.client.get("/sorties").json()
        self.assertTrue(all(s["status"] == "crew-ready" for s in sorties))
        snap = self.client.get("/metrics").json()
        self.assertEqual(snap["executable_pct"], 100)
        self.assertEqual(snap["next_action"], "all lines executable")

    def test_stage_06_launched(self):
        self.client.post("/demo/stages/06-launched")
        sorties = self.client.get("/sorties").json()
        self.assertEqual(
            [s["status"] for s in sorties],
            ["airborne", "airborne", "crew-ready", "crew-ready"],
        )
        snap = self.client.get("/metrics").json()
        self.assertEqual(snap["airborne"], 2)
        self.assertEqual(snap["executable_pct"], 100)

    def test_empty_metrics_point_at_missing_tail(self):
        self.client.post("/demo/stages/01-empty-board")
        snap = self.client.get("/metrics").json()
        self.assertEqual(snap["executable_pct"], 0)
        self.assertEqual(snap["next_action"], "missing tail")
        self.assertEqual(len(snap["exceptions"]), 4)

    def test_full_buildup_sequence(self):
        """Walk every stage in order; each response stays coherent."""
        for stage in DEMO_STAGES:
            r = self.client.post(f"/demo/stages/{stage['id']}")
            self.assertEqual(r.status_code, 200, stage["id"])
            sorties = self.client.get("/sorties").json()
            self.assertEqual(len(sorties), 4)
            if stage["tails"]:
                self.assertEqual(
                    [s["tail"] for s in sorties],
                    ["87-0321", "87-0322", "87-0325", "87-0330"],
                )

    def test_assign_tail_conflict_with_sample_data(self):
        self.client.post("/demo/stages/02-tails-assigned")
        sorties = self.client.get("/sorties").json()
        sid = sorties[1]["id"]
        r = self.client.patch(
            f"/sorties/{sid}/aircraft",
            json={"tail": "87-0321"},
        )
        self.assertEqual(r.status_code, 409)

    def test_status_rejects_unknown(self):
        sorties = self.client.get("/sorties").json()
        r = self.client.patch(
            f"/sorties/{sorties[0]['id']}/status",
            json={"status": "scrambled"},
        )
        self.assertEqual(r.status_code, 400)


if __name__ == "__main__":
    unittest.main()
