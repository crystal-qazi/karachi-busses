import importlib.util
import unittest
from pathlib import Path
from shapely.geometry import LineString, Point, box

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "extract_osm_karachi_stop_candidates.py"
SPEC = importlib.util.spec_from_file_location("extract_osm_karachi_stop_candidates", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class BusStopCandidateFilterTests(unittest.TestCase):
    def test_includes_highway_bus_stop(self):
        self.assertTrue(MODULE.is_bus_stop_candidate({"highway": "bus_stop"}))

    def test_includes_bus_station(self):
        self.assertTrue(MODULE.is_bus_stop_candidate({"amenity": "bus_station"}))

    def test_includes_bus_tagged_platform(self):
        self.assertTrue(MODULE.is_bus_stop_candidate({"public_transport": "platform", "bus": "yes"}))

    def test_excludes_rail_only_platform(self):
        self.assertFalse(MODULE.is_bus_stop_candidate({"public_transport": "platform", "train": "yes"}))

    def test_excludes_generic_platform_without_bus_evidence(self):
        self.assertFalse(MODULE.is_bus_stop_candidate({"highway": "platform"}))

    def test_candidate_kind(self):
        self.assertEqual(MODULE.candidate_kind({"highway": "bus_stop"}), "highway_bus_stop")
        self.assertEqual(MODULE.candidate_kind({"amenity": "bus_station"}), "bus_station")

class GeometryTests(unittest.TestCase):
    def test_point_inside_boundary_is_retained(self):
        point = Point(5, 5)
        clipped = MODULE.clip_candidate_geometry(point, box(0, 0, 10, 10))
        self.assertEqual(clipped, point)

    def test_line_is_clipped_to_boundary(self):
        line = LineString([(-5, 5), (15, 5)])
        clipped = MODULE.clip_candidate_geometry(line, box(0, 0, 10, 10))
        self.assertAlmostEqual(clipped.length, 10)
        self.assertEqual(tuple(clipped.coords[0]), (0, 5))
        self.assertEqual(tuple(clipped.coords[-1]), (10, 5))

    def test_outside_point_is_empty(self):
        self.assertIsNone(MODULE.clip_candidate_geometry(Point(20, 20), box(0, 0, 10, 10)))

if __name__ == "__main__":
    unittest.main()
