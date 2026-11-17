import csv
import tempfile
import unittest
from pathlib import Path

from scripts.build_phase5ab_coordinate_collision_review import build


class CoordinateCollisionTests(unittest.TestCase):
    def write(self, path, rows):
        fields = ["node_id", "latitude", "longitude", "historical_route_labels", "route_label_count", "verification_status"]
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def test_groups_exact_decimal_coordinates_and_preserves_nodes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, output, report = root / "nodes.csv", root / "review.csv", root / "report.json"
            self.write(source, [
                {"node_id": "alpha", "latitude": "24.1000", "longitude": "67.200", "historical_route_labels": "R1;R2", "route_label_count": "2", "verification_status": "under_review"},
                {"node_id": "beta", "latitude": "24.1", "longitude": "67.2000", "historical_route_labels": "R2;R3", "route_label_count": "2", "verification_status": "under_review"},
                {"node_id": "gamma", "latitude": "24.1001", "longitude": "67.2000", "historical_route_labels": "R4", "route_label_count": "1", "verification_status": "under_review"},
            ])
            result = build(source, output, report)
            with output.open(encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(result["exact_duplicate_coordinate_clusters"], 1)
            self.assertEqual(result["nodes_in_duplicate_clusters"], 2)
            self.assertEqual({r["node_id"] for r in rows}, {"alpha", "beta"})
            self.assertEqual(rows[0]["route_labels_shared_by_all_nodes"], "R2")
            self.assertTrue(all(r["coordinate_collision_review_status"] == "exact_duplicate_coordinate_manual_review" for r in rows))
            self.assertEqual(result["non_collision_nodes"], 1)

    def test_rejects_duplicate_node_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "nodes.csv"
            self.write(source, [
                {"node_id": "alpha", "latitude": "24.1", "longitude": "67.2", "historical_route_labels": "", "route_label_count": "0", "verification_status": "under_review"},
                {"node_id": "alpha", "latitude": "24.2", "longitude": "67.3", "historical_route_labels": "", "route_label_count": "0", "verification_status": "under_review"},
            ])
            with self.assertRaisesRegex(ValueError, "duplicate node_id"):
                build(source, root / "review.csv", root / "report.json")


if __name__ == "__main__":
    unittest.main()
