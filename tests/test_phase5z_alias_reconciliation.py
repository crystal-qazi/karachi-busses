import csv
import tempfile
import unittest
from pathlib import Path

from scripts.reconcile_user_confirmed_stop_aliases import build


class AliasReconciliationTests(unittest.TestCase):
    def write_csv(self, path, fields, rows):
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def test_confirmed_alias_is_recorded_without_coordinate_assignment(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            crosswalk = root / "crosswalk.csv"
            shortlist = root / "shortlist.csv"
            aliases = root / "aliases.csv"
            output = root / "out"
            self.write_csv(crosswalk,
                ["route_code", "source_stop_sequence", "source_stop_name", "coordinate_node_id", "latitude", "longitude"],
                [{"route_code": "R1", "source_stop_sequence": "1", "source_stop_name": "Khokharapar 04", "coordinate_node_id": "", "latitude": "", "longitude": ""},
                 {"route_code": "R1", "source_stop_sequence": "2", "source_stop_name": "Model Colony", "coordinate_node_id": "model_colony", "latitude": "24.9", "longitude": "67.1"}])
            self.write_csv(shortlist,
                ["route_code", "source_stop_sequence", "source_stop_name", "candidate_node_id"],
                [{"route_code": "R1", "source_stop_sequence": "1", "source_stop_name": "Khokharapar 04", "candidate_node_id": "khokrapar_no_4"}])
            self.write_csv(aliases,
                ["source_stop_name", "historical_node_id", "route_codes", "occurrence_count", "name_alias_status", "confirmation_basis", "physical_stop_verification", "coordinate_assignment"],
                [{"source_stop_name": "Khokharapar 04", "historical_node_id": "khokrapar_no_4", "route_codes": "R1", "occurrence_count": "1", "name_alias_status": "confirmed_by_user", "confirmation_basis": "user_confirmed_in_chat", "physical_stop_verification": "unverified", "coordinate_assignment": "not_assigned"}])
            report = build(crosswalk, shortlist, aliases, output)
            with (output / "PHASE_5Z_USER_CONFIRMED_ALIAS_RECONCILIATION.csv").open(encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(report["reconciliation_counts"]["confirmed_name_alias"], 1)
            self.assertEqual(rows[0]["name_alias_status"], "confirmed_by_user")
            self.assertEqual(rows[0]["confirmed_historical_node_id"], "khokrapar_no_4")
            self.assertEqual(rows[0]["coordinate_node_id"], "")
            self.assertEqual(rows[0]["latitude"], "")
            self.assertEqual(rows[0]["physical_stop_verification"], "unverified")
            self.assertEqual(rows[0]["coordinate_assignment"], "not_assigned")
            self.assertEqual(rows[0]["route_approval_status"], "not_approved")
            self.assertEqual(rows[1]["name_alias_status"], "no_user_confirmed_alias")
            self.assertEqual(rows[1]["coordinate_node_id"], "model_colony")

    def test_rejects_unconfirmed_alias_register(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            crosswalk, shortlist, aliases = root / "c.csv", root / "s.csv", root / "a.csv"
            self.write_csv(crosswalk, ["route_code", "source_stop_sequence", "source_stop_name", "coordinate_node_id", "latitude", "longitude"],
                [{"route_code": "R1", "source_stop_sequence": "1", "source_stop_name": "Example", "coordinate_node_id": "", "latitude": "", "longitude": ""}])
            self.write_csv(shortlist, ["route_code", "source_stop_sequence", "source_stop_name", "candidate_node_id"],
                [{"route_code": "R1", "source_stop_sequence": "1", "source_stop_name": "Example", "candidate_node_id": "example_node"}])
            self.write_csv(aliases, ["source_stop_name", "historical_node_id", "route_codes", "occurrence_count", "name_alias_status", "confirmation_basis", "physical_stop_verification", "coordinate_assignment"],
                [{"source_stop_name": "Example", "historical_node_id": "example_node", "route_codes": "R1", "occurrence_count": "1", "name_alias_status": "unverified", "confirmation_basis": "similarity_only", "physical_stop_verification": "unverified", "coordinate_assignment": "not_assigned"}])
            with self.assertRaisesRegex(ValueError, "without explicit user confirmation"):
                build(crosswalk, shortlist, aliases, root / "out")

    def test_rejects_existing_coordinate_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            crosswalk, shortlist, aliases = root / "c.csv", root / "s.csv", root / "a.csv"
            self.write_csv(crosswalk, ["route_code", "source_stop_sequence", "source_stop_name", "coordinate_node_id", "latitude", "longitude"],
                [{"route_code": "R1", "source_stop_sequence": "1", "source_stop_name": "Example", "coordinate_node_id": "existing", "latitude": "24.9", "longitude": "67.1"}])
            self.write_csv(shortlist, ["route_code", "source_stop_sequence", "source_stop_name", "candidate_node_id"],
                [{"route_code": "R1", "source_stop_sequence": "1", "source_stop_name": "Example", "candidate_node_id": "example_node"}])
            self.write_csv(aliases, ["source_stop_name", "historical_node_id", "route_codes", "occurrence_count", "name_alias_status", "confirmation_basis", "physical_stop_verification", "coordinate_assignment"],
                [{"source_stop_name": "Example", "historical_node_id": "example_node", "route_codes": "R1", "occurrence_count": "1", "name_alias_status": "confirmed_by_user", "confirmation_basis": "user_confirmed_in_chat", "physical_stop_verification": "unverified", "coordinate_assignment": "not_assigned"}])
            with self.assertRaisesRegex(ValueError, "overwrite an existing coordinate"):
                build(crosswalk, shortlist, aliases, root / "out")


if __name__ == "__main__":
    unittest.main()
