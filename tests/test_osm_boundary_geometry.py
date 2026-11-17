import importlib.util
import subprocess
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_osm_boundary.py"
SPEC = importlib.util.spec_from_file_location("build_osm_boundary", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class BoundaryTests(unittest.TestCase):
    def test_accepts_localized_karachi_division_name(self):
        tags = {
            "boundary": "administrative",
            "admin_level": "5",
            "name": "کراچی ڈویژن",
            "name:en": "Karachi Division",
        }
        self.assertEqual(MODULE.validate_relation_identity(tags), "Karachi Division")

    def test_rejects_wrong_admin_level(self):
        tags = {
            "boundary": "administrative",
            "admin_level": "6",
            "name": "کراچی ڈویژن",
            "name:en": "Karachi Division",
        }
        with self.assertRaisesRegex(ValueError, "admin_level"):
            MODULE.validate_relation_identity(tags)

    def test_valid_polygon_and_area(self):
        try:
            import shapely
            import pyproj
        except ImportError:
            self.skipTest("Optional GIS packages not installed in base CI.")
        geometry = {"type": "Polygon", "coordinates": [[[67,24],[67.1,24],[67.1,24.1],[67,24.1],[67,24]]]}
        result = MODULE.validate_geometry(geometry)
        self.assertTrue(result["is_valid"])
        self.assertGreater(result["area_km2"], 0)
        self.assertEqual(result["area_crs"], "EPSG:32642")
    def test_rejects_bowtie_polygon(self):
        try:
            import shapely
            import pyproj
        except ImportError:
            self.skipTest("Optional GIS packages not installed in base CI.")
        geometry = {"type": "Polygon", "coordinates": [[[67,24],[67.1,24.1],[67,24.1],[67.1,24],[67,24]]]}
        with self.assertRaisesRegex(ValueError, "Invalid polygon"):
            MODULE.validate_geometry(geometry)
    def test_rejects_point(self):
        with self.assertRaisesRegex(ValueError, "Polygon or MultiPolygon"):
            MODULE.validate_geometry({"type":"Point","coordinates":[67,24]})
    def test_dry_run(self):
        result = subprocess.run(["python", str(SCRIPT)], check=True, capture_output=True, text=True)
        self.assertIn("DRY RUN", result.stdout)

if __name__ == "__main__":
    unittest.main()
