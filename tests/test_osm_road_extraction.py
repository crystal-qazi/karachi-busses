import importlib.util
import unittest
from pathlib import Path
from shapely.geometry import LineString, box

SCRIPT=Path(__file__).resolve().parents[1]/"scripts"/"extract_osm_karachi_roads.py"
SPEC=importlib.util.spec_from_file_location("extract_osm_karachi_roads",SCRIPT)
MODULE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class RoadFilterTests(unittest.TestCase):
    def test_includes_residential(self): self.assertTrue(MODULE.is_bus_road({"highway":"residential"}))
    def test_excludes_footway(self): self.assertFalse(MODULE.is_bus_road({"highway":"footway"}))
    def test_excludes_private_access(self): self.assertFalse(MODULE.is_bus_road({"highway":"primary","access":"private"}))
    def test_excludes_motor_vehicle_prohibition(self): self.assertFalse(MODULE.is_bus_road({"highway":"secondary","motor_vehicle":"no"}))
    def test_preserves_direction_and_access_tags(self):
        tags={"highway":"primary","oneway":"-1","access":"destination"}
        self.assertTrue(MODULE.is_bus_road(tags))
        self.assertEqual(tags["oneway"],"-1")
        self.assertEqual(tags["access"],"destination")

class RoadClippingTests(unittest.TestCase):
    def test_clips_line_to_polygon(self):
        parts=MODULE.clipped_line_parts(LineString([(-5,5),(15,5)]),box(0,0,10,10))
        self.assertEqual(len(parts),1)
        self.assertAlmostEqual(parts[0].length,10)
        self.assertEqual(tuple(parts[0].coords[0]),(0,5))
        self.assertEqual(tuple(parts[0].coords[-1]),(10,5))
    def test_outside_line_is_empty(self):
        self.assertEqual(MODULE.clipped_line_parts(LineString([(-5,-5),(-1,-1)]),box(0,0,10,10)),[])
    def test_geometry_collection_keeps_only_lines(self):
        from shapely.geometry import GeometryCollection,Point
        parts=MODULE.line_parts(GeometryCollection([LineString([(0,0),(1,1)]),Point(2,2)]))
        self.assertEqual(len(parts),1)
        self.assertEqual(parts[0].geom_type,"LineString")

if __name__=="__main__": unittest.main()
