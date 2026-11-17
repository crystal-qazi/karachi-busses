import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "phase5w", ROOT / "scripts/build_unmatched_stop_name_candidates.py"
)
phase5w = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(phase5w)


class NameCandidateTests(unittest.TestCase):
    def test_normalization_aliases_spelling_variant(self):
        self.assertEqual(phase5w.normalize("Suadabad"), phase5w.normalize("Saudabad"))
        self.assertEqual(phase5w.normalize("Guru Mandar"), phase5w.normalize("Gurumandir"))

    def test_score_prefers_matching_name(self):
        exact = phase5w.score_names("Nagan Chowrangi", "nagan_chowrangi")
        unrelated = phase5w.score_names("Nagan Chowrangi", "korangi_no_5")
        self.assertGreater(exact, unrelated)

    def test_build_preserves_unmatched_and_emits_names_not_coordinates(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            crosswalk = tmp / "crosswalk.csv"
            nodes = tmp / "nodes.csv"
            output = tmp / "candidates.csv"
            report = tmp / "report.json"
            with crosswalk.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "route_code", "route_name", "source_stop_sequence",
                        "source_stop_name", "review_status",
                    ],
                )
                writer.writeheader()
                writer.writerow({
                    "route_code": "R2", "route_name": "Route 02",
                    "source_stop_sequence": "2", "source_stop_name": "Nagan Chowrangi",
                    "review_status": "unmatched",
                })
                writer.writerow({
                    "route_code": "R2", "route_name": "Route 02",
                    "source_stop_sequence": "3", "source_stop_name": "Already matched",
                    "review_status": "candidate_name_match",
                })
            with nodes.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["node_id"])
                writer.writeheader()
                writer.writerow({"node_id": "nagan_chowrangi"})
                writer.writerow({"node_id": "korangi_no_5"})

            with (
                patch.object(phase5w, "CROSSWALK", crosswalk),
                patch.object(phase5w, "NODES", nodes),
                patch.object(phase5w, "OUTPUT", output),
                patch.object(phase5w, "REPORT", report),
            ):
                unmatched_count, node_count = phase5w.build()

            self.assertEqual((unmatched_count, node_count), (1, 2))
            with output.open(newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["review_status"], "unverified_name_candidates_only")
            self.assertEqual(rows[0]["candidate_1_node_id"], "nagan_chowrangi")
            self.assertNotIn("latitude", rows[0])
            self.assertNotIn("longitude", rows[0])
            self.assertNotIn("coordinate_node_id", rows[0])
            report_data = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(report_data["automatic_assignments"], 0)
            self.assertFalse(report_data["coordinates_emitted"])


if __name__ == "__main__":
    unittest.main()
