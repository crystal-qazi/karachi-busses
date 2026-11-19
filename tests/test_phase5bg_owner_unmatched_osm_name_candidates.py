import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_phase5bg_owner_unmatched_osm_name_candidates.py"
SPEC = importlib.util.spec_from_file_location("phase5bg", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Phase5BGTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "owner.csv"
        self.inventory = self.root / "osm.geojson"
        self.output = self.root / "output.csv"
        self.report = self.root / "report.json"

    def tearDown(self):
        self.temp.cleanup()

    def write_csv(self, path, fields, rows):
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def inputs(self):
        fields = [
            "route_code", "sequence", "owner_reviewed_stop_name", "match_status",
        ]
        self.write_csv(self.source, fields, [
            {"route_code":"R2","sequence":"1","owner_reviewed_stop_name":"Johar Mor","match_status":"unmatched"},
            {"route_code":"R3","sequence":"2","owner_reviewed_stop_name":"Brookes Chowrangi","match_status":"unmatched"},
            {"route_code":"R1","sequence":"3","owner_reviewed_stop_name":"Unknown Stop","match_status":"unmatched"},
            {"route_code":"R1","sequence":"4","owner_reviewed_stop_name":"Matched Historical","match_status":"exact_normalized_name"},
        ])
        features = [
            {"type":"Feature","properties":{"osm_type":"node","osm_id":101,"name":"Johar Mor","name_en":None,"candidate_kind":"highway_bus_stop","tags":{"highway":"bus_stop"}},"geometry":{"type":"Point","coordinates":[67.1,24.9]}},
            {"type":"Feature","properties":{"osm_type":"node","osm_id":102,"name":"Brookes Chowrangi","name_en":None,"candidate_kind":"highway_bus_stop","tags":{"highway":"bus_stop"}},"geometry":{"type":"Point","coordinates":[67.2,24.8]}},
            {"type":"Feature","properties":{"osm_type":"node","osm_id":103,"name":"Brookes Chowrangi","name_en":None,"candidate_kind":"bus_station","tags":{"amenity":"bus_station"}},"geometry":{"type":"Point","coordinates":[67.21,24.81]}},
        ]
        self.inventory.write_text(json.dumps({"type":"FeatureCollection","features":features}), encoding="utf-8")

    def rows(self):
        with self.output.open(encoding="utf-8", newline="") as stream:
            return list(csv.DictReader(stream))

    def test_exact_normalized_names_are_candidate_only(self):
        self.inputs()
        report = MODULE.build(self.source, self.inventory, self.output, self.report)
        rows = self.rows()
        johar = next(r for r in rows if r["owner_reviewed_stop_name"] == "Johar Mor")
        self.assertEqual(johar["osm_id"], "101")
        self.assertEqual(johar["osm_name_match_status"], "exact_normalized_name_candidate")
        self.assertEqual(johar["coordinate_assignment"], "not_assigned")
        self.assertEqual(report["entries_with_exact_osm_name_candidate"], 2)

    def test_multiple_osm_objects_are_preserved(self):
        self.inputs()
        report = MODULE.build(self.source, self.inventory, self.output, self.report)
        rows = [r for r in self.rows() if r["owner_reviewed_stop_name"] == "Brookes Chowrangi"]
        self.assertEqual({r["osm_id"] for r in rows}, {"102", "103"})
        self.assertEqual(report["entries_with_multiple_exact_osm_objects"], 1)

    def test_no_match_is_explicit_and_existing_matched_rows_are_excluded(self):
        self.inputs()
        MODULE.build(self.source, self.inventory, self.output, self.report)
        rows = self.rows()
        unknown = next(r for r in rows if r["owner_reviewed_stop_name"] == "Unknown Stop")
        self.assertEqual(unknown["osm_name_match_status"], "no_exact_osm_name_candidate")
        self.assertFalse(any(r["owner_reviewed_stop_name"] == "Matched Historical" for r in rows))

    def test_all_rows_remain_unverified_and_unassigned(self):
        self.inputs()
        MODULE.build(self.source, self.inventory, self.output, self.report)
        for row in self.rows():
            self.assertEqual(row["physical_stop_verification"], "unverified")
            self.assertEqual(row["coordinate_assignment"], "not_assigned")
            self.assertEqual(row["route_assignment"], "not_assigned")


if __name__ == "__main__":
    unittest.main()
