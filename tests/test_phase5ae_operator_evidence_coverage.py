import csv
import unittest
from pathlib import Path

REGISTER = Path(__file__).resolve().parents[1] / "data/research/PHASE_5AE_OPERATOR_EVIDENCE_COVERAGE.csv"

class Phase5AETests(unittest.TestCase):
    def test_register_has_all_target_routes_and_published_counts(self):
        with REGISTER.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        expected = {
            "R1":"18", "R2":"15", "R3":"13", "R4":"14", "R5":"8", "R6":"16",
            "R7":"10", "R8":"13", "R9":"18", "R10":"15", "R11":"11",
            "R12":"15", "R13":"10", "R14":"16",
            "EV-01":"18", "EV-02":"8", "EV-03":"16", "EV-04":"10", "EV-05":"10",
            "DD01":"14",
        }
        self.assertEqual(len(rows), len(expected))
        self.assertEqual({r["route_code"]: r["source_sequence_stop_count"] for r in rows}, expected)
        inactive = {"R5", "R6", "R7"}
        self.assertEqual(
            {r["route_code"]: r["official_status"] for r in rows},
            {code: ("Inactive" if code in inactive else "Active") for code in expected},
        )
        self.assertTrue(all(r["sequence_scope"] == "numbered_route_page_sequence" for r in rows))
        self.assertTrue(all(r["official_source_url"] for r in rows))

if __name__ == "__main__":
    unittest.main()
