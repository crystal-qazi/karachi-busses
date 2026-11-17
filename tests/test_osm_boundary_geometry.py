import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_osm_boundary.py"
SPEC = importlib.util.spec_from_file_location("build_osm_boundary", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class OSMBoundaryGeometryTests(unittest.TestCase):
    def test_selects_exact_relation_feature(self):
        feature = {
            "type": "Feature",
            "properties": {"@type": "relation", "@id": 6080948},
            "geometry": {"type": "MultiPolygon", "coordinates": []},
        }
        result = MODULE.find_relation_feature({"type": "FeatureCollection", "features": [feature]})
        self.assertEqual(result["properties"]["@id"], 6080948)

    def test_rejects_wrong_or_missing_relation(self):
        with self.assertRaisesRegex(ValueError, "found 0"):
            MODULE.find_relation_feature({"type": "FeatureCollection", "features": []})

    def test_rejects_duplicate_relation_features(self):
        feature = {"type": "Feature", "properties": {"@type": "relation", "@id": 6080948},
                   "geometry": {"type": "Polygon", "coordinates": []}}
        with self.assertRaisesRegex(ValueError, "found 2"):
            MODULE.find_relation_feature({"type": "FeatureCollection", "features": [feature, feature]})

    def test_dry_run_does_not_build(self):
        import subprocess
        result = subprocess.run(["python", str(SCRIPT)], check=True, capture_output=True, text=True)
        self.assertIn("DRY RUN", result.stdout)

    def test_geometry_validation_when_gis_dependencies_available(self):
        try:
            import shapely  # noqa: F401
            import pyproj  # noqa: F401
        except ImportError:
            self.skipTest("Optional GIS dependencies are not installed in standard CI.")
        feature = {
            "type": "Feature",
            "properties": {},
            "geometry": {"type": "Polygon", "coordinates": [[
                [67.0, 24.0], [67.1, 24.0], [67.1, 24.1],
                [67.0, 24.1], [67.0, 24.0]
            ]]},
        }
        result = MODULE.validate_geometry(feature)
        self.assertTrue(result["is_valid"])
        self.assertGreater(result["area_km2"], 0)


if __name__ == "__main__":
    unittest.main()
