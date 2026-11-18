import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEQUENCES = ROOT / "data/research/PHASE_5AF_OFFICIAL_ROUTE_STOP_SEQUENCES.csv"
COVERAGE = ROOT / "data/research/PHASE_5AE_OPERATOR_EVIDENCE_COVERAGE.csv"

EXPECTED = {
    "R1": 18, "R2": 15, "R3": 13, "R4": 14, "R5": 8, "R6": 16,
    "R7": 10, "R8": 13, "R9": 18, "R10": 15, "R11": 11,
    "R12": 15, "R13": 10, "R14": 16,
    "EV-01": 18, "EV-02": 8, "EV-03": 16, "EV-04": 10, "EV-05": 10,
    "DD01": 14,
}
INACTIVE = {"R5", "R6", "R7"}

class Phase5AFTests(unittest.TestCase):
    def read(self, path):
        with path.open(encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def test_all_pages_and_sequential_entries_match_coverage(self):
        rows = self.read(SEQUENCES)
        coverage = {r["route_code"]: r for r in self.read(COVERAGE)}
        self.assertEqual(len(coverage), len(EXPECTED))
        self.assertEqual(len(rows), sum(EXPECTED.values()))
        keys = [(r["route_code"], r["sequence_number"]) for r in rows]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertTrue(all(r["entry_name"].strip() for r in rows))
        self.assertEqual(set(coverage), set(EXPECTED))
        for route, count in EXPECTED.items():
            route_rows = [r for r in rows if r["route_code"] == route]
            self.assertEqual(len(route_rows), count)
            self.assertEqual([int(r["sequence_number"]) for r in route_rows], list(range(1, count + 1)))
            self.assertEqual(route_rows[0]["entry_type"], "direction_descriptor")
            self.assertTrue(all(r["entry_type"] == "operator_published_named_entry" for r in route_rows[1:]))
            self.assertEqual(coverage[route]["source_sequence_stop_count"], str(count))
            expected_status = "Inactive" if route in INACTIVE else "Active"
            self.assertTrue(all(r["official_status"] == expected_status for r in route_rows))
            self.assertEqual(coverage[route]["official_status"], expected_status)
            self.assertEqual(len({r["official_source_url"] for r in route_rows}), 1)
            self.assertEqual(coverage[route]["official_source_url"], route_rows[0]["official_source_url"])

    def test_route_codes_are_unique_per_sequence_and_sources_are_current(self):
        rows = self.read(SEQUENCES)
        self.assertEqual(len({r["route_code"] for r in rows}), len(EXPECTED))
        self.assertTrue(all(r["official_source_url"].startswith("https://smta.gos.pk/routes/") for r in rows))
        self.assertTrue(all(r["source_access_date"] == "2026-11-18" for r in rows))

if __name__ == "__main__":
    unittest.main()
