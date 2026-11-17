import unittest
from pathlib import Path
import importlib.util

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "acquire_osm_road_data.py"
SPEC = importlib.util.spec_from_file_location("acquire_osm_road_data", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AcquisitionSafetyTests(unittest.TestCase):
    def test_only_geofabrik_https_is_allowed(self):
        MODULE.validate_source(MODULE.DATA_URL)
        for url in (
            "http://download.geofabrik.de/asia/pakistan-latest.osm.pbf",
            "https://example.com/pakistan-latest.osm.pbf",
            "https://download.geofabrik.de.evil.example/file",
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                MODULE.validate_source(url)

    def test_md5_parser_requires_32_hex_characters(self):
        self.assertEqual(MODULE.parse_md5("d41d8cd98f00b204e9800998ecf8427e  file"),
                         "d41d8cd98f00b204e9800998ecf8427e")
        with self.assertRaises(ValueError):
            MODULE.parse_md5("not a checksum")

    def test_dry_run_does_not_download(self):
        import subprocess
        result = subprocess.run(
            ["python", str(SCRIPT)],
            check=True, capture_output=True, text=True
        )
        self.assertIn("DRY RUN", result.stdout)
        self.assertNotIn("Downloading", result.stdout)


if __name__ == "__main__":
    unittest.main()
