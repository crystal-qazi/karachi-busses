import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_historical_edge_source_delta.py"
SPEC = importlib.util.spec_from_file_location("phase5bi", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class HistoricalEdgeDeltaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "source.csv"
        self.local = self.root / "local.csv"
        self.output = self.root / "delta.csv"
        self.report = self.root / "report.json"

    def tearDown(self):
        self.temp.cleanup()

    def write_edges(self, path, rows):
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=["stop1", "stop2", "bus_name"])
            writer.writeheader()
            for a, b, route in rows:
                writer.writerow({"stop1":a,"stop2":b,"bus_name":route})

    def test_multiset_diff_preserves_duplicates_and_route_codes(self):
        self.write_edges(self.source, [
            ("a","b","R1"), ("a","b","R1"), ("b","c","R1"), ("x","y","EV-01")
        ])
        self.write_edges(self.local, [
            ("a","b","R1"), ("a","b","R1"), ("c","d","R2")
        ])
        report = MODULE.compare(self.source, self.local, self.output, self.report)
        self.assertEqual(report["source"]["edge_rows"], 4)
        self.assertEqual(report["project_cleaned_file"]["edge_rows"], 3)
        self.assertEqual(report["source"]["exact_duplicate_occurrences"], 1)
        self.assertEqual(report["comparison"]["matched_edge_occurrences"], 2)
        self.assertEqual(report["comparison"]["rows_present_in_zenodo_missing_from_project"], 2)
        self.assertEqual(report["comparison"]["rows_present_in_project_missing_from_zenodo"], 1)
        self.assertEqual(report["comparison"]["missing_rows_by_route"], {"EV-01":1,"R1":1})
        with self.output.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 3)
        self.assertEqual({r["delta_type"] for r in rows}, {
            "present_in_zenodo_missing_from_project",
            "present_in_project_missing_from_zenodo",
        })

    def test_identical_files_reconcile(self):
        rows=[("a","b","R1"),("b","c","R2")]
        self.write_edges(self.source, rows)
        self.write_edges(self.local, rows)
        report=MODULE.compare(self.source,self.local,self.output,self.report)
        self.assertEqual(report["status"],"reconciled")
        self.assertEqual(report["comparison"]["rows_present_in_zenodo_missing_from_project"],0)
        self.assertEqual(report["comparison"]["rows_present_in_project_missing_from_zenodo"],0)

    def test_direction_and_route_code_are_not_normalized_away(self):
        self.write_edges(self.source,[("a","b","R1")])
        self.write_edges(self.local,[("b","a","R1")])
        report=MODULE.compare(self.source,self.local,self.output,self.report)
        self.assertEqual(report["comparison"]["rows_present_in_zenodo_missing_from_project"],1)
        self.assertEqual(report["comparison"]["rows_present_in_project_missing_from_zenodo"],1)

    def test_schema_mismatch_is_rejected(self):
        self.source.write_text("from,to,route\na,b,R1\n",encoding="utf-8")
        self.write_edges(self.local,[("a","b","R1")])
        with self.assertRaises(ValueError):
            MODULE.compare(self.source,self.local,self.output,self.report)


if __name__ == "__main__":
    unittest.main()
