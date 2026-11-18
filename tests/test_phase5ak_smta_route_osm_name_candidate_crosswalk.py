import csv
import json
import tempfile
import unittest
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_phase5ak_smta_route_osm_name_candidate_crosswalk.py"
SPEC = importlib.util.spec_from_file_location("phase5ak", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Phase5AKTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.sequences = self.root / "sequences.csv"
        self.aliases = self.root / "aliases.csv"
        self.candidates = self.root / "candidates.geojson"
        self.output = self.root / "crosswalk.csv"
        self.report = self.root / "report.json"

    def tearDown(self):
        self.temp.cleanup()

    def write_csv(self, path, fields, rows):
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def build_inputs(self):
        self.write_csv(self.sequences, [
            "route_code", "official_route_label", "route_family", "official_status",
            "sequence_number", "entry_name", "entry_type", "official_source_url",
        ], [
            {"route_code":"R2","official_route_label":"Route 02","route_family":"Pink Bus",
             "official_status":"Active","sequence_number":"1","entry_name":"North Karachi to Korangi",
             "entry_type":"direction_descriptor","official_source_url":"https://example.test/r2"},
            {"route_code":"R2","official_route_label":"Route 02","route_family":"Pink Bus",
             "official_status":"Active","sequence_number":"2","entry_name":"Sorab Goth",
             "entry_type":"operator_published_named_entry","official_source_url":"https://example.test/r2"},
            {"route_code":"R4","official_route_label":"Route 04","route_family":"PBS",
             "official_status":"Active","sequence_number":"3","entry_name":"Sorab Goth",
             "entry_type":"operator_published_named_entry","official_source_url":"https://example.test/r4"},
            {"route_code":"R3","official_route_label":"Route 03","route_family":"Pink Bus",
             "official_status":"Active","sequence_number":"4","entry_name":"FTC",
             "entry_type":"operator_published_named_entry","official_source_url":"https://example.test/r3"},
            {"route_code":"R1","official_route_label":"Route 01","route_family":"Pink Bus",
             "official_status":"Active","sequence_number":"5","entry_name":"No Such Stop",
             "entry_type":"operator_published_named_entry","official_source_url":"https://example.test/r1"},
        ])
        self.write_csv(self.aliases, [
            "source_stop_name","historical_node_id","route_codes","name_alias_status",
        ], [
            {"source_stop_name":"Sorab Goth","historical_node_id":"sohrab_goth",
             "route_codes":"R2;R4","name_alias_status":"confirmed_by_user"},
        ])
        self.candidates.write_text(json.dumps({"type":"FeatureCollection","features":[
            {"type":"Feature","properties":{"osm_type":"node","osm_id":10,"name":"Sohrab Goth",
              "candidate_kind":"highway_bus_stop","tags":{"highway":"bus_stop"}},"geometry":{"type":"Point","coordinates":[67.1,24.9]}},
            {"type":"Feature","properties":{"osm_type":"node","osm_id":11,"name":"Sohrab Goth",
              "candidate_kind":"highway_bus_stop","tags":{"highway":"bus_stop"}},"geometry":{"type":"Point","coordinates":[67.2,24.9]}},
            {"type":"Feature","properties":{"osm_type":"node","osm_id":12,"name":"FTC",
              "candidate_kind":"highway_bus_stop","tags":{"highway":"bus_stop"}},"geometry":{"type":"Point","coordinates":[67.3,24.9}},
        ]}), encoding="utf-8")

    def test_route_scoped_alias_and_all_duplicate_candidates_are_preserved(self):
        self.build_inputs()
        report = MODULE.reconcile(self.sequences, self.aliases, self.candidates, self.output, self.report)
        with self.output.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        r2 = [r for r in rows if r["route_code"] == "R2"]
        r4 = [r for r in rows if r["route_code"] == "R4"]
        self.assertEqual(len(r2), 2)
        self.assertEqual(len(r4), 2)
        self.assertTrue(all(r["match_type"] == "user_approved_route_scoped_alias" for r in r2 + r4))
        self.assertTrue(all(r["physical_stop_verification"] == "unverified" for r in rows))
        self.assertTrue(all(r["coordinate_assignment"] == "not_assigned" for r in rows))
        self.assertTrue(all(r["route_assignment"] == "not_assigned" for r in rows))
        self.assertEqual(report["direction_descriptors_excluded"], 1)
        self.assertEqual(report["entries_with_multiple_osm_candidates"], 2)

    def test_exact_name_and_unmatched_entry_are_distinct(self):
        self.build_inputs()
        MODULE.reconcile(self.sequences, self.aliases, self.candidates, self.output, self.report)
        with self.output.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        ftc = next(r for r in rows if r["route_code"] == "R3")
        missing = next(r for r in rows if r["route_code"] == "R1")
        self.assertEqual(ftc["match_type"], "exact_normalized_name")
        self.assertEqual(ftc["osm_id"], "12")
        self.assertEqual(missing["match_type"], "unmatched")
        self.assertEqual(missing["candidate_status"], "no_osm_name_candidate")
        self.assertEqual(missing["osm_id"], "")

    def test_alias_is_not_applied_to_unlisted_route(self):
        self.build_inputs()
        # Add an R9 entry with the same source spelling, but no R9 alias scope.
        with self.sequences.open("a", encoding="utf-8", newline="") as stream:
            stream.write('R9,Route 09,PBS,Active,6,Sorab Goth,operator_published_named_entry,https://example.test/r9\n')
        MODULE.reconcile(self.sequences, self.aliases, self.candidates, self.output, self.report)
        with self.output.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        r9 = next(r for r in rows if r["route_code"] == "R9")
        self.assertEqual(r9["match_type"], "unmatched")

    def test_unconfirmed_alias_is_ignored(self):
        self.build_inputs()
        rows = MODULE.read_csv(self.aliases)
        rows[0]["name_alias_status"] = "pending"
        self.write_csv(self.aliases, list(rows[0].keys()), rows)
        MODULE.reconcile(self.sequences, self.aliases, self.candidates, self.output, self.report)
        with self.output.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        r2 = [r for r in rows if r["route_code"] == "R2"]
        self.assertTrue(all(r["match_type"] == "unmatched" for r in r2))


if __name__ == "__main__":
    unittest.main()
