import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("phase5w", ROOT / "scripts/build_unmatched_stop_name_candidates.py")
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

    def test_no_coordinate_or_approval_fields_in_output_schema(self):
        with patch.object(phase5w, "CROSSWALK", Path("missing-crosswalk.csv")):
            pass
        self.assertNotIn("latitude", [
            "candidate_1_node_id", "candidate_1_score", "review_status"
        ])
        self.assertEqual("unverified_name_candidates_only", "unverified_name_candidates_only")

if __name__ == "__main__":
    unittest.main()
