import csv
import unittest
from pathlib import Path

REGISTER = Path(__file__).resolve().parents[1] / "data/research/PHASE_5AE_OPERATOR_EVIDENCE_COVERAGE.csv"

class Phase5AETests(unittest.TestCase):
    def test_register_has_all_target_routes_and_published_counts(self):
        with REGISTER.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 14)
        expected = {
            "R1":"18","R2":"15","R3":"13","R4":"14","R8":"13",
            "R11":"11","R12":"15","R13":"10","R14":"16",
            "EV-01":"18","EV-02":"8","EV-03":"16","EV-04":"10","EV-05":"10"
        }
        self.assertEqual({r["route_code"]: r["source_sequence_stop_count"] for r in rows}, expected)
        self.assertTrue(all(r["official_status"] == "Active" for r in rows))
        self.assertTrue(all(r["sequence_scope"] == "numbered_route_page_sequence" for r in rows))

if __name__ == "__main__":
    unittest.main()
