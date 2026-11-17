import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_osm_district_boundaries.py"
SPEC = importlib.util.spec_from_file_location("audit_osm_district_boundaries", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class DistrictIdentityTests(unittest.TestCase):
    def test_maps_nazimabad_alias_to_karachi_central(self):
        self.assertEqual(
            MODULE.classify_district({
                "name:en": "Nazimabad District",
                "wikipedia": "en:Karachi Central District",
            }),
            "Karachi Central",
        )

    def test_maps_english_district_name(self):
        self.assertEqual(
            MODULE.classify_district({"name:en": "Karachi East District"}),
            "Karachi East",
        )

    def test_unknown_district_is_not_guessed(self):
        self.assertIsNone(MODULE.classify_district({"name:en": "Unknown District"}))

    def test_all_seven_official_districts_are_configured(self):
        self.assertEqual(len(MODULE.EXPECTED_DISTRICTS), 7)


if __name__ == "__main__":
    unittest.main()
