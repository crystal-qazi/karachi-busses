import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import build_phase5aa_remaining_unmatched_review as phase


class RemainingUnmatchedTests(unittest.TestCase):
    def write(self, path, fields, rows):
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def test_excludes_only_confirmed_alias_occurrence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            crosswalk = root / "crosswalk.csv"
            candidates = root / "candidates.csv"
            shortlist = root / "shortlist.csv"
            aliases = root / "aliases.csv"
            output = root / "out.csv"
            report = root / "report.json"
            self.write(crosswalk,
                ["route_code", "source_stop_sequence", "source_stop_name", "review_status"],
                [{"route_code": "R1", "source_stop_sequence": "1", "source_stop_name": "Alias Stop", "review_status": "unmatched"},
                 {"route_code": "R1", "source_stop_sequence": "2", "source_stop_name": "Unknown Stop", "review_status": "unmatched"}])
            candidate_fields = ["route_code", "source_stop_sequence", "source_stop_name", "candidate_1_node_id", "candidate_1_score", "review_status"]
            self.write(candidates, candidate_fields,
                [{"route_code": "R1", "source_stop_sequence": "1", "source_stop_name": "Alias Stop", "candidate_1_node_id": "alias_node", "candidate_1_score": "1.0000", "review_status": "unverified_name_candidates_only"},
                 {"route_code": "R1", "source_stop_sequence": "2", "source_stop_name": "Unknown Stop", "candidate_1_node_id": "maybe_node", "candidate_1_score": "0.6000", "review_status": "unverified_name_candidates_only"}])
            self.write(shortlist, ["route_code", "source_stop_sequence", "source_stop_name", "candidate_node_id"],
                [{"route_code": "R1", "source_stop_sequence": "1", "source_stop_name": "Alias Stop", "candidate_node_id": "alias_node"}])
            self.write(aliases, ["source_stop_name", "historical_node_id", "route_codes", "name_alias_status", "confirmation_basis"],
                [{"source_stop_name": "Alias Stop", "historical_node_id": "alias_node", "route_codes": "R1", "name_alias_status": "confirmed_by_user", "confirmation_basis": "user_confirmed_in_chat"}])
            with patch.object(phase, "CROSSWALK", crosswalk), patch.object(phase, "CANDIDATES", candidates), patch.object(phase, "SHORTLIST", shortlist), patch.object(phase, "ALIASES", aliases):
                result = phase.build(output, report)
            with output.open(encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(result["counts"]["original_unmatched_rows"], 2)
            self.assertEqual(result["counts"]["confirmed_alias_occurrences_excluded"], 1)
            self.assertEqual(result["counts"]["remaining_unmatched_rows"], 1)
            self.assertEqual(rows[0]["source_stop_name"], "Unknown Stop")
            self.assertEqual(rows[0]["physical_stop_verification"], "unverified")
            self.assertEqual(rows[0]["coordinate_assignment"], "not_assigned")
            self.assertEqual(rows[0]["route_approval_status"], "not_approved")

    def test_rejects_candidate_without_user_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            crosswalk, candidates, shortlist, aliases = [root / x for x in ("c.csv", "n.csv", "s.csv", "a.csv")]
            self.write(crosswalk, ["route_code", "source_stop_sequence", "source_stop_name", "review_status"],
                [{"route_code": "R1", "source_stop_sequence": "1", "source_stop_name": "Stop", "review_status": "unmatched"}])
            self.write(candidates, ["route_code", "source_stop_sequence", "source_stop_name", "review_status"],
                [{"route_code": "R1", "source_stop_sequence": "1", "source_stop_name": "Stop", "review_status": "unverified_name_candidates_only"}])
            self.write(shortlist, ["route_code", "source_stop_sequence", "source_stop_name", "candidate_node_id"],
                [{"route_code": "R1", "source_stop_sequence": "1", "source_stop_name": "Stop", "candidate_node_id": "node"}])
            self.write(aliases, ["source_stop_name", "historical_node_id", "route_codes", "name_alias_status", "confirmation_basis"],
                [{"source_stop_name": "Stop", "historical_node_id": "node", "route_codes": "R1", "name_alias_status": "unverified", "confirmation_basis": "similarity_only"}])
            with patch.object(phase, "CROSSWALK", crosswalk), patch.object(phase, "CANDIDATES", candidates), patch.object(phase, "SHORTLIST", shortlist), patch.object(phase, "ALIASES", aliases):
                with self.assertRaisesRegex(ValueError, "non-user-confirmed alias"):
                    phase.build(root / "out.csv", root / "report.json")


if __name__ == "__main__":
    unittest.main()
