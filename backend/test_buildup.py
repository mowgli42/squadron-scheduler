"""API tests: demo buildup + aircraft scheduling gaps."""
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import main
from sample_data import DEMO_STAGES, LOADOUTS, MISSIONS


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        main.configure(self.tmp.name)
        self.client = TestClient(main.app)

    def tearDown(self):
        Path(self.tmp.name).unlink(missing_ok=True)

    def test_seed_has_line_identity_and_lands(self):
        aircraft = self.client.get("/aircraft").json()
        aircrew = self.client.get("/aircrew").json()
        sorties = self.client.get("/sorties").json()
        self.assertEqual(len(aircraft), 6)
        self.assertEqual(len(aircrew), 10)
        self.assertEqual([s["mission"] for s in sorties], MISSIONS)
        self.assertEqual([s["line_number"] for s in sorties], [1, 2, 3, 4])
        self.assertTrue(all(s["callsign"] for s in sorties))
        self.assertTrue(all(s["land"] for s in sorties))
        self.assertTrue(all(s["status"] == "planned" and not s["tail"] for s in sorties))

    def test_demo_stages_listed(self):
        stages = self.client.get("/demo/stages").json()
        self.assertEqual([s["id"] for s in stages], [s["id"] for s in DEMO_STAGES])

    def test_stage_01_empty_board(self):
        self.client.post("/demo/stages/01-empty-board")
        sorties = self.client.get("/sorties").json()
        for s in sorties:
            self.assertIsNone(s["tail"])
            self.assertIsNone(s["spare_tail"])
            self.assertEqual(s["stage"], "planned")

    def test_stage_02_tails_and_spares(self):
        self.client.post("/demo/stages/02-tails-assigned")
        sorties = self.client.get("/sorties").json()
        self.assertEqual(
            [s["tail"] for s in sorties],
            ["87-0321", "87-0322", "87-0325", "87-0330"],
        )
        self.assertTrue(all(s["spare_tail"] == "87-0335" for s in sorties))
        self.assertTrue(all(s["stage"] == "tail" for s in sorties))

    def test_stage_05_crew_ready_requires_er_and_is_executable(self):
        self.client.post("/demo/stages/05-crew-ready")
        sorties = self.client.get("/sorties").json()
        self.assertTrue(all(s["status"] == "crew-ready" for s in sorties))
        self.assertTrue(all(s["er_signed"] for s in sorties))
        snap = self.client.get("/metrics").json()
        self.assertEqual(snap["executable_pct"], 100)
        self.assertEqual(snap["spares_assigned"], 4)
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

    def test_full_buildup_sequence(self):
        for stage in DEMO_STAGES:
            r = self.client.post(f"/demo/stages/{stage['id']}")
            self.assertEqual(r.status_code, 200, stage["id"])

    def test_reject_nmc_and_spare_equals_primary(self):
        sorties = self.client.get("/sorties").json()
        sid = sorties[0]["id"]
        r = self.client.patch(f"/sorties/{sid}/aircraft", json={"tail": "87-0340"})
        self.assertEqual(r.status_code, 409)
        self.client.patch(f"/sorties/{sid}/aircraft", json={"tail": "87-0321"})
        r = self.client.patch(f"/sorties/{sid}/spare", json={"spare_tail": "87-0321"})
        self.assertEqual(r.status_code, 409)

    def test_turn_conflict_on_overlapping_window(self):
        self.client.post("/demo/stages/02-tails-assigned")
        sorties = self.client.get("/sorties").json()
        r = self.client.patch(
            f"/sorties/{sorties[1]['id']}/aircraft",
            json={"tail": sorties[0]["tail"]},
        )
        self.assertEqual(r.status_code, 409)

    def test_loadout_sets_load_crew_minutes(self):
        sid = self.client.get("/sorties").json()[0]["id"]
        r = self.client.patch(f"/sorties/{sid}/loadout", json={"template": "A/G"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["load_crew_minutes"], 60)
        s = self.client.get("/sorties").json()[0]
        self.assertEqual(s["loadout"], LOADOUTS["A/G"])
        self.assertEqual(s["load_crew_minutes"], 60)

    def test_er_gate_and_crew_replace(self):
        self.client.post("/demo/stages/04-crew-filled")
        sid = self.client.get("/sorties").json()[0]["id"]
        r = self.client.patch(f"/sorties/{sid}/status", json={"status": "crew-ready"})
        self.assertEqual(r.status_code, 409)
        self.client.patch(f"/sorties/{sid}/er", json={"signed": True})
        r = self.client.patch(f"/sorties/{sid}/status", json={"status": "crew-ready"})
        self.assertEqual(r.status_code, 200)
        r = self.client.post(
            f"/sorties/{sid}/crew", json={"aircrew_id": 10, "position": "pilot"}
        )
        self.assertEqual(r.status_code, 200)
        s = self.client.get("/sorties").json()[0]
        pilot = next(c for c in s["crew"] if c["position"] == "pilot")
        self.assertEqual(pilot["aircrew_id"], 10)
        changes = self.client.get("/changes").json()
        self.assertTrue(any(ch["field"] == "crew:pilot" for ch in changes))

    def test_rest_gate(self):
        sid = self.client.get("/sorties").json()[0]["id"]
        r = self.client.post(
            f"/sorties/{sid}/crew", json={"aircrew_id": 9, "position": "pilot"}
        )
        self.assertEqual(r.status_code, 409)

    def test_aircraft_schedule(self):
        self.client.post("/demo/stages/02-tails-assigned")
        board = self.client.get("/aircraft/schedule").json()
        by_tail = {a["tail"]: a for a in board}
        self.assertEqual(len(by_tail["87-0321"]["commitments"]), 1)
        self.assertEqual(by_tail["87-0321"]["commitments"][0]["role"], "primary")
        self.assertEqual(len(by_tail["87-0335"]["commitments"]), 4)
        self.assertEqual(by_tail["87-0335"]["commitments"][0]["role"], "spare")
        self.assertEqual(by_tail["87-0340"]["commitments"], [])


if __name__ == "__main__":
    unittest.main()
