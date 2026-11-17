import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.build_stop_review_register import build_register


class StopReviewRegisterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.crosswalk = self.root / "crosswalk.csv"
        self.audit = self.root / "audit.csv"
        self.out = self.root / "out"

    def tearDown(self):
        self.temp.cleanup()

    def write_csv(self, path, fields, rows):
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def fixture(self):
        self.write_csv(self.crosswalk,
            ["route_code", "route_name", "source_stop_sequence", "source_stop_name", "coordinate_node_id", "latitude", "longitude", "match_method", "review_status"],
            [
                {"route_code":"R1","route_name":"SMTA Route 01","source_stop_sequence":"1","source_stop_name":"Alpha","coordinate_node_id":"alpha","latitude":"24.9","longitude":"67.0","match_method":"exact_normalized_name","review_status":"candidate_name_match"},
                {"route_code":"R1","route_name":"SMTA Route 01","source_stop_sequence":"2","source_stop_name":"Beta","coordinate_node_id":"","latitude":"","longitude":"","match_method":"no_exact_match","review_status":"unmatched"},
            ])
        self.write_csv(self.audit,
            ["route_code", "source_stop_sequence", "source_stop_name", "audit_status", "nearest_osm_way_id", "nearest_distance_m", "proximity_band"],
            [
                {"route_code":"R1","source_stop_sequence":"1","source_stop_name":"Alpha","audit_status":"proximity_only_unverified","nearest_osm_way_id":"123","nearest_distance_m":"8.2","proximity_band":"0-15m"},
                {"route_code":"R1","source_stop_sequence":"2","source_stop_name":"Beta","audit_status":"no_coordinate_candidate","nearest_osm_way_id":"","nearest_distance_m":"","proximity_band":""},
            ])

    def test_builds_exact_join_and_never_approves(self):
        self.fixture()
        report = build_register(self.crosswalk, self.audit, self.out)
        with (self.out / "karachi-stop-review-register.csv").open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(report["rows"], 2)
        self.assertEqual(report["join_validation"], "exact_one_to_one")
        self.assertEqual(rows[0]["stop_verification_status"], "unverified")
        self.assertEqual(rows[0]["route_approval_status"], "not_approved")
        self.assertEqual(rows[0]["nearest_osm_way_id"], "123")
        self.assertEqual(rows[1]["coordinate_review_status"], "no_coordinate_candidate")
        self.assertEqual(rows[1]["reviewer_decision"], "")
        self.assertTrue((self.out / "karachi-stop-review-register-report.json").is_file())

    def test_rejects_missing_join_row(self):
        self.fixture()
        with self.audit.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=["route_code","source_stop_sequence","source_stop_name","audit_status","nearest_osm_way_id","nearest_distance_m","proximity_band"])
            writer.writeheader()
            writer.writerow({"route_code":"R1","source_stop_sequence":"1","source_stop_name":"Alpha","audit_status":"proximity_only_unverified","nearest_osm_way_id":"123","nearest_distance_m":"8.2","proximity_band":"0-15m"})
        with self.assertRaisesRegex(ValueError, "do not match exactly"):
            build_register(self.crosswalk, self.audit, self.out)

    def test_rejects_duplicate_join_key(self):
        self.fixture()
        with self.audit.open("a", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=["route_code","source_stop_sequence","source_stop_name","audit_status","nearest_osm_way_id","nearest_distance_m","proximity_band"])
            writer.writerow({"route_code":"R1","source_stop_sequence":"1","source_stop_name":"Alpha","audit_status":"proximity_only_unverified","nearest_osm_way_id":"123","nearest_distance_m":"8.2","proximity_band":"0-15m"})
        with self.assertRaisesRegex(ValueError, "duplicate join key"):
            build_register(self.crosswalk, self.audit, self.out)

    def test_rejects_stop_name_mismatch(self):
        self.fixture()
        rows = list(csv.DictReader(self.audit.open(encoding="utf-8", newline="")))
        rows[0]["source_stop_name"] = "Wrong"
        self.write_csv(self.audit, list(rows[0]), rows)
        with self.assertRaisesRegex(ValueError, "Stop-name mismatch"):
            build_register(self.crosswalk, self.audit, self.out)


if __name__ == "__main__":
    unittest.main()
