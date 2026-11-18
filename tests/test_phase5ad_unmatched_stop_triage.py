import csv
import tempfile
import unittest
from pathlib import Path
from scripts.build_phase5ad_unmatched_stop_triage import build

class Phase5ADTests(unittest.TestCase):
    def test_classifies_without_assigning_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "input.csv"
            fields = [
                "route_code","route_name","source_stop_sequence","source_stop_name",
                "candidate_1_node_id","candidate_1_score","candidate_2_node_id","candidate_2_score",
                "candidate_3_node_id","candidate_3_score","candidate_count_at_or_above_0_45",
                "physical_stop_verification","coordinate_assignment","route_approval_status",
            ]
            rows = [
                ["R1","Route 1","1","Stop A","alpha","0.9100","beta","0.8800","gamma","0.5000","3","unverified","not_assigned","not_approved"],
                ["R2","Route 2","2","Stop B","delta","0.7200","epsilon","0.3000","","","1","unverified","not_assigned","not_approved"],
                ["R3","Route 3","3","Stop C","zeta","0.2000","eta","0.1000","","","0","unverified","not_assigned","not_approved"],
            ]
            with source.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f); writer.writerow(fields); writer.writerows(rows)
            out = root / "out.csv"; report = root / "report.json"
            result = build(source, out, report)
            self.assertEqual(result["counts"]["rows"], 3)
            with out.open(encoding="utf-8", newline="") as f:
                written = list(csv.DictReader(f))
            self.assertEqual(written[0]["candidate_ambiguity"], "multiple_close_text_candidates")
            self.assertEqual(written[1]["top_candidate_band"], "possible")
            self.assertEqual(written[2]["triage_priority"], "low")
            self.assertTrue(all(r["physical_stop_verification"] == "unverified" for r in written))
            self.assertTrue(all(r["coordinate_assignment"] == "not_assigned" for r in written))

    def test_rejects_duplicate_route_sequence(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "input.csv"
            fields = ["route_code","route_name","source_stop_sequence","source_stop_name",
                "candidate_1_node_id","candidate_1_score","candidate_2_node_id","candidate_2_score",
                "candidate_3_node_id","candidate_3_score","candidate_count_at_or_above_0_45",
                "physical_stop_verification","coordinate_assignment","route_approval_status"]
            row = ["R1","Route 1","1","Stop","x","0.8","","","","","1","unverified","not_assigned","not_approved"]
            with source.open("w", newline="", encoding="utf-8") as f:
                w=csv.writer(f); w.writerow(fields); w.writerow(row); w.writerow(row)
            with self.assertRaisesRegex(ValueError, "duplicate"):
                build(source, Path(tmp)/"out.csv", Path(tmp)/"report.json")

if __name__ == "__main__":
    unittest.main()
