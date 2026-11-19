import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_phase5aq_owner_route_osm_candidate_crosswalk.py"
SPEC = importlib.util.spec_from_file_location("phase5aq", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Phase5AQTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "owner.csv"
        self.audit = self.root / "osm.csv"
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
            "candidate_source_node_id", "candidate_latitude", "candidate_longitude",
            "candidate_coordinate_collision", "candidate_review_note",
        ]
        self.write_csv(self.source, fields, [
            {"route_code":"R1","sequence":"1","owner_reviewed_stop_name":"Exact Stop",
             "match_status":"exact_normalized_name","candidate_source_node_id":"exact_stop",
             "candidate_latitude":"24.9","candidate_longitude":"67.1","candidate_coordinate_collision":"no"},
            {"route_code":"R2","sequence":"2","owner_reviewed_stop_name":"Shafiq Mor",
             "match_status":"coordinate_review_required","candidate_source_node_id":"shafiq_mor",
             "candidate_latitude":"24.85","candidate_longitude":"67.0","candidate_coordinate_collision":"no"},
            {"route_code":"R14","sequence":"3","owner_reviewed_stop_name":"Sorab Goth",
             "match_status":"user_confirmed_name_alias","candidate_source_node_id":"sohrab_goth",
             "candidate_latitude":"","candidate_longitude":"","candidate_coordinate_collision":"no"},
            {"route_code":"R4","sequence":"4","owner_reviewed_stop_name":"Ayesha Manzil",
             "match_status":"ambiguous_name_variant","candidate_source_node_id":"ayesha_manzil|aisha_manzil",
             "candidate_latitude":"","candidate_longitude":"","candidate_coordinate_collision":"no"},
            {"route_code":"R1","sequence":"5","owner_reviewed_stop_name":"Unknown Stop",
             "match_status":"unmatched","candidate_source_node_id":"",
             "candidate_latitude":"","candidate_longitude":"","candidate_coordinate_collision":"no"},
            {"route_code":"R3","sequence":"6","owner_reviewed_stop_name":"Outside Radius",
             "match_status":"exact_normalized_name","candidate_source_node_id":"outside_stop",
             "candidate_latitude":"24.91","candidate_longitude":"67.12","candidate_coordinate_collision":"no"},
        ])
        audit_fields = [
            "historical_node_id","nearby_candidate_count_within_250m",
            "exact_name_candidate_count_within_250m","exact_name_candidate_osm_ids",
            "nearest_osm_type","nearest_osm_id","nearest_osm_name","nearest_osm_kind",
            "nearest_candidate_distance_m",
            "candidate_1_osm_type","candidate_1_osm_id","candidate_1_name","candidate_1_kind","candidate_1_distance_m",
            "candidate_2_osm_type","candidate_2_osm_id","candidate_2_name","candidate_2_kind","candidate_2_distance_m",
            "candidate_3_osm_type","candidate_3_osm_id","candidate_3_name","candidate_3_kind","candidate_3_distance_m",
        ]
        self.write_csv(self.audit, audit_fields, [
            {"historical_node_id":"exact_stop","nearby_candidate_count_within_250m":"2",
             "exact_name_candidate_count_within_250m":"1","exact_name_candidate_osm_ids":"node/101",
             "nearest_osm_type":"node","nearest_osm_id":"101","nearest_osm_name":"Exact Stop",
             "nearest_osm_kind":"highway_bus_stop","nearest_candidate_distance_m":"12.5",
             "candidate_1_osm_type":"node","candidate_1_osm_id":"101","candidate_1_name":"Exact Stop",
             "candidate_1_kind":"highway_bus_stop","candidate_1_distance_m":"12.5",
             "candidate_2_osm_type":"node","candidate_2_osm_id":"102","candidate_2_name":"Nearby Stop",
             "candidate_2_kind":"highway_bus_stop","candidate_2_distance_m":"99.0"},
            {"historical_node_id":"shafiq_mor","nearby_candidate_count_within_250m":"1",
             "exact_name_candidate_count_within_250m":"0","exact_name_candidate_osm_ids":"",
             "nearest_osm_type":"node","nearest_osm_id":"201","nearest_osm_name":"Shafiq Mor Bus Stop",
             "nearest_osm_kind":"highway_bus_stop","nearest_candidate_distance_m":"80.0",
             "candidate_1_osm_type":"node","candidate_1_osm_id":"201","candidate_1_name":"Shafiq Mor Bus Stop",
             "candidate_1_kind":"highway_bus_stop","candidate_1_distance_m":"80.0"},
            {"historical_node_id":"outside_stop","nearby_candidate_count_within_250m":"0",
             "exact_name_candidate_count_within_250m":"0","exact_name_candidate_osm_ids":"",
             "nearest_osm_type":"node","nearest_osm_id":"301","nearest_osm_name":"Distant Stop",
             "nearest_osm_kind":"highway_bus_stop","nearest_candidate_distance_m":"420.0"},
        ])

    def rows(self):
        with self.output.open(encoding="utf-8", newline="") as stream:
            return list(csv.DictReader(stream))

    def test_exact_match_expands_all_nearby_osm_candidates(self):
        self.inputs()
        report = MODULE.build(self.source, self.audit, self.output, self.report)
        rows = [r for r in self.rows() if r["route_code"] == "R1" and r["sequence"] == "1"]
        self.assertEqual(len(rows), 2)
        self.assertEqual({r["osm_id"] for r in rows}, {"101", "102"})
        self.assertTrue(all(r["osm_review_relation"] == "within_250m_proximity_only" for r in rows))
        self.assertEqual(report["input_owner_route_stop_rows"], 6)

    def test_alias_ambiguous_and_unmatched_rows_are_not_joined(self):
        self.inputs()
        MODULE.build(self.source, self.audit, self.output, self.report)
        rows = self.rows()
        alias = next(r for r in rows if r["match_status"] == "user_confirmed_name_alias")
        ambiguous = next(r for r in rows if r["match_status"] == "ambiguous_name_variant")
        unmatched = next(r for r in rows if r["match_status"] == "unmatched")
        self.assertEqual(alias["osm_review_relation"], "not_joined_coordinate_not_authorized")
        self.assertEqual(ambiguous["osm_review_relation"], "not_joined_coordinate_not_authorized")
        self.assertEqual(unmatched["osm_review_relation"], "no_historical_node_match")
        self.assertEqual(alias["osm_id"], "")
        self.assertEqual(ambiguous["osm_id"], "")

    def test_coordinate_review_row_shows_context_without_promotion(self):
        self.inputs()
        MODULE.build(self.source, self.audit, self.output, self.report)
        row = next(r for r in self.rows() if r["match_status"] == "coordinate_review_required")
        self.assertEqual(row["osm_id"], "201")
        self.assertEqual(row["coordinate_assignment"], "not_assigned")
        self.assertEqual(row["physical_stop_verification"], "unverified")

    def test_nearest_outside_radius_is_context_only(self):
        self.inputs()
        MODULE.build(self.source, self.audit, self.output, self.report)
        row = next(r for r in self.rows() if r["owner_reviewed_stop_name"] == "Outside Radius")
        self.assertEqual(row["osm_review_relation"], "nearest_outside_250m_context_only")
        self.assertEqual(row["osm_distance_m"], "420.0")

    def test_every_output_row_remains_unverified_and_unassigned(self):
        self.inputs()
        MODULE.build(self.source, self.audit, self.output, self.report)
        for row in self.rows():
            self.assertEqual(row["physical_stop_verification"], "unverified")
            self.assertEqual(row["coordinate_assignment"], "not_assigned")
            self.assertEqual(row["route_assignment"], "not_assigned")


if __name__ == "__main__":
    unittest.main()
