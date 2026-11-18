import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_phase5al_smta_historical_node_osm_candidate_crosswalk.py"
SPEC = importlib.util.spec_from_file_location("phase5al", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Phase5ALTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.sequences = self.root / "sequences.csv"
        self.aliases = self.root / "aliases.csv"
        self.nodes = self.root / "nodes.csv"
        self.audit = self.root / "audit.csv"
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
            {"route_code":"R1","official_route_label":"Route 01","route_family":"Pink Bus",
             "official_status":"Active","sequence_number":"1","entry_name":"Direction text",
             "entry_type":"direction_descriptor","official_source_url":"https://example.test/r1"},
            {"route_code":"R1","official_route_label":"Route 01","route_family":"Pink Bus",
             "official_status":"Active","sequence_number":"2","entry_name":"Model Colony",
             "entry_type":"operator_published_named_entry","official_source_url":"https://example.test/r1"},
            {"route_code":"R2","official_route_label":"Route 02","route_family":"Pink Bus",
             "official_status":"Active","sequence_number":"3","entry_name":"Sorab Goth",
             "entry_type":"operator_published_named_entry","official_source_url":"https://example.test/r2"},
            {"route_code":"R9","official_route_label":"Route 09","route_family":"PBS",
             "official_status":"Active","sequence_number":"4","entry_name":"Sorab Goth",
             "entry_type":"operator_published_named_entry","official_source_url":"https://example.test/r9"},
            {"route_code":"R1","official_route_label":"Route 01","route_family":"Pink Bus",
             "official_status":"Active","sequence_number":"5","entry_name":"Missing Stop",
             "entry_type":"operator_published_named_entry","official_source_url":"https://example.test/r1"},
        ])
        self.write_csv(self.aliases, [
            "source_stop_name","historical_node_id","route_codes","name_alias_status",
        ], [
            {"source_stop_name":"Sorab Goth","historical_node_id":"sohrab_goth",
             "route_codes":"R2;R4","name_alias_status":"confirmed_by_user"},
        ])
        self.write_csv(self.nodes, [
            "node_id","latitude","longitude","historical_route_labels",
            "coordinate_collision_group","verification_status","review_note",
        ], [
            {"node_id":"model_colony","latitude":"24.9","longitude":"67.1",
             "historical_route_labels":"old-route","coordinate_collision_group":"",
             "verification_status":"under_review","review_note":"historical coordinate"},
            {"node_id":"sohrab_goth","latitude":"24.8","longitude":"67.2",
             "historical_route_labels":"old-route","coordinate_collision_group":"",
             "verification_status":"under_review","review_note":"historical coordinate"},
        ])
        self.write_csv(self.audit, [
            "historical_node_id","candidate_review_status","nearby_candidate_count_within_250m",
            "exact_name_candidate_count_within_250m","exact_name_candidate_osm_ids",
            "nearest_osm_type","nearest_osm_id","nearest_osm_name","nearest_osm_kind",
            "nearest_candidate_distance_m",
            "candidate_1_osm_type","candidate_1_osm_id","candidate_1_name","candidate_1_kind","candidate_1_distance_m",
            "candidate_2_osm_type","candidate_2_osm_id","candidate_2_name","candidate_2_kind","candidate_2_distance_m",
            "candidate_3_osm_type","candidate_3_osm_id","candidate_3_name","candidate_3_kind","candidate_3_distance_m",
        ], [
            {"historical_node_id":"model_colony","nearby_candidate_count_within_250m":"2",
             "exact_name_candidate_count_within_250m":"1","exact_name_candidate_osm_ids":"node/101",
             "nearest_osm_type":"node","nearest_osm_id":"101","nearest_osm_name":"Model Colony Stop",
             "nearest_osm_kind":"highway_bus_stop","nearest_candidate_distance_m":"12.5",
             "candidate_1_osm_type":"node","candidate_1_osm_id":"101","candidate_1_name":"Model Colony Stop",
             "candidate_1_kind":"highway_bus_stop","candidate_1_distance_m":"12.5",
             "candidate_2_osm_type":"node","candidate_2_osm_id":"102","candidate_2_name":"Airport Road Stop",
             "candidate_2_kind":"highway_bus_stop","candidate_2_distance_m":"99.0"},
            {"historical_node_id":"sohrab_goth","nearby_candidate_count_within_250m":"0",
             "exact_name_candidate_count_within_250m":"0","exact_name_candidate_osm_ids":"",
             "nearest_osm_type":"node","nearest_osm_id":"201","nearest_osm_name":"Sohrab Goth Bus Stop",
             "nearest_osm_kind":"highway_bus_stop","nearest_candidate_distance_m":"300.0"},
        ])

    def load_rows(self):
        with self.output.open(encoding="utf-8", newline="") as stream:
            return list(csv.DictReader(stream))

    def test_exact_name_match_expands_to_all_nearby_candidates(self):
        self.build_inputs()
        report = MODULE.reconcile(self.sequences, self.aliases, self.nodes, self.audit, self.output, self.report)
        rows = [r for r in self.load_rows() if r["route_code"] == "R1" and r["sequence_number"] == "2"]
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(r["historical_match_type"] == "exact_historical_node_name" for r in rows))
        self.assertEqual({r["osm_id"] for r in rows}, {"101", "102"})
        self.assertTrue(all(r["osm_candidate_relation"] == "within_250m_proximity_only" for r in rows))
        self.assertEqual(report["direction_descriptors_excluded"], 1)

    def test_alias_is_route_scoped_and_outside_radius_is_context_only(self):
        self.build_inputs()
        MODULE.reconcile(self.sequences, self.aliases, self.nodes, self.audit, self.output, self.report)
        rows = self.load_rows()
        r2 = next(r for r in rows if r["route_code"] == "R2")
        r9 = next(r for r in rows if r["route_code"] == "R9")
        self.assertEqual(r2["historical_match_type"], "user_approved_route_scoped_alias")
        self.assertEqual(r2["historical_node_id"], "sohrab_goth")
        self.assertEqual(r2["osm_candidate_relation"], "nearest_outside_250m_context_only")
        self.assertEqual(r2["osm_distance_m"], "300.0")
        self.assertEqual(r9["historical_match_type"], "unmatched")
        self.assertEqual(r9["historical_node_id"], "")

    def test_all_rows_remain_unverified_and_unassigned(self):
        self.build_inputs()
        MODULE.reconcile(self.sequences, self.aliases, self.nodes, self.audit, self.output, self.report)
        for row in self.load_rows():
            self.assertEqual(row["physical_stop_verification"], "unverified")
            self.assertEqual(row["coordinate_assignment"], "not_assigned")
            self.assertEqual(row["route_assignment"], "not_assigned")

    def test_unconfirmed_alias_is_ignored(self):
        self.build_inputs()
        aliases = MODULE.read_csv(self.aliases)
        aliases[0]["name_alias_status"] = "pending"
        self.write_csv(self.aliases, list(aliases[0]), aliases)
        MODULE.reconcile(self.sequences, self.aliases, self.nodes, self.audit, self.output, self.report)
        r2 = next(r for r in self.load_rows() if r["route_code"] == "R2")
        self.assertEqual(r2["historical_match_type"], "unmatched")


if __name__ == "__main__":
    unittest.main()
