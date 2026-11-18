import csv
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data/research/PHASE_5AG_OFFICIAL_SEQUENCE_NAME_RECONCILIATION.csv"
REPORT = ROOT / "data/research/PHASE_5AG_OFFICIAL_SEQUENCE_NAME_RECONCILIATION_REPORT.json"

class Phase5AGTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Rebuild transient Phase 5W/5AA inputs so the normal pytest workflow is self-contained.
        commands = [
            [sys.executable, str(ROOT / "scripts/build_unmatched_stop_name_candidates.py"), "--build"],
            [sys.executable, str(ROOT / "scripts/build_phase5aa_remaining_unmatched_review.py"), "--build"],
            [sys.executable, str(ROOT / "scripts/build_phase5ag_official_sequence_name_reconciliation.py"), "--build"],
        ]
        for command in commands:
            subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)

    def test_all_82_residual_rows_are_represented_without_approval(self):
        with OUTPUT.open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        keys = {(r["route_code"], r["source_stop_sequence"]) for r in rows}
        self.assertEqual(len(keys), 82)
        self.assertTrue(all(r["physical_stop_verification"] == "unverified" for r in rows))
        self.assertTrue(all(r["coordinate_assignment"] == "not_assigned" for r in rows))
        self.assertTrue(all(r["route_approval_status"] == "not_approved" for r in rows))
        self.assertTrue(all(r["name_match_type"] in {
            "exact_normalized_name", "user_confirmed_spelling_alias", "direction_descriptor_reference_only", "no_exact_sequence_name_match"
        } for r in rows))

    def test_no_fuzzy_matches_and_no_coordinates(self):
        with OUTPUT.open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertTrue(all(not r["official_entry_name"] or r["official_sequence_number"] for r in rows))
        self.assertTrue(all(not r["official_entry_type"] or r["official_entry_type"] in {"operator_published_named_entry", "direction_descriptor"} for r in rows))
        self.assertTrue(all("score" not in r["name_match_type"] for r in rows))
        self.assertNotIn("latitude", rows[0])
        self.assertNotIn("longitude", rows[0])

    def test_report_exists_and_declares_name_only_scope(self):
        self.assertTrue(REPORT.is_file())
        import json
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["residual_source_rows"], 82)
        self.assertIn("name_only", report["status"])

if __name__ == "__main__":
    unittest.main()
