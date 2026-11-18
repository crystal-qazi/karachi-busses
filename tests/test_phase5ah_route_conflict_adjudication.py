import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "data/research/PHASE_5AH_ROUTE_CONFLICT_ADJUDICATION.csv"

class Phase5AHTests(unittest.TestCase):
    def test_expected_routes_and_geometry_gate(self):
        with REGISTER.open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        by_route = {r["route_code"]: r for r in rows}
        expected = {"R1","R2","R3","R4","R8","R11","R12","R13","R14",
                    "EV-01","EV-02","EV-03","EV-04","EV-05","GREEN_LINE","ORANGE_LINE"}
        self.assertEqual(set(by_route), expected)
        self.assertTrue(all(r["geometry_gate"] == "blocked" for r in rows))
        self.assertTrue(all(r["required_evidence"].strip() for r in rows))

    def test_no_conflict_claimed_fully_resolved(self):
        with REGISTER.open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertTrue(all("fully_resolved" not in r["resolution_status"] for r in rows))
        self.assertTrue(all(r["resolution_status"] for r in rows))

    def test_detail_sources_are_smta_for_bus_routes(self):
        with REGISTER.open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        for row in rows:
            if row["route_code"].startswith("R") or row["route_code"].startswith("EV-"):
                self.assertTrue(row["primary_detail_source_url"].startswith("https://smta.gos.pk/routes/"))

if __name__ == "__main__":
    unittest.main()
