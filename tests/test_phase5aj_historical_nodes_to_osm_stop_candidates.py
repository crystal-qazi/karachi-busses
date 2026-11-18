import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_phase5aj_historical_nodes_to_osm_stop_candidates.py"
SPEC = importlib.util.spec_from_file_location("audit_phase5aj_historical_nodes_to_osm_stop_candidates", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class MatchClassificationTests(unittest.TestCase):
    def test_exact_name_is_candidate_not_verification(self):
        self.assertEqual(MODULE.classify_candidate(1, 3), "exact_name_and_proximity_candidate")

    def test_proximity_only_is_separate(self):
        self.assertEqual(MODULE.classify_candidate(0, 2), "proximity_only_candidates")

    def test_no_nearby_candidate(self):
        self.assertEqual(MODULE.classify_candidate(0, 0), "no_candidate_within_250m")

    def test_normalization_is_conservative(self):
        self.assertEqual(MODULE.normalize("FTC"), "ftc")
        self.assertNotEqual(MODULE.normalize("Sorab Goth"), MODULE.normalize("Sohrab Goth"))

if __name__ == "__main__":
    unittest.main()
