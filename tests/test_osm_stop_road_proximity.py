import importlib.util
import unittest
from pathlib import Path
SCRIPT=Path(__file__).resolve().parents[1]/"scripts"/"audit_stop_road_proximity.py"
SPEC=importlib.util.spec_from_file_location("audit_stop_road_proximity",SCRIPT)
MODULE=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(MODULE)

class ProximityBandTests(unittest.TestCase):
    def test_bands(self):
        self.assertEqual(MODULE.proximity_band(10),"0-15m")
        self.assertEqual(MODULE.proximity_band(15),"0-15m")
        self.assertEqual(MODULE.proximity_band(30),"15-50m")
        self.assertEqual(MODULE.proximity_band(75),"50-100m")
        self.assertEqual(MODULE.proximity_band(200),"100-250m")
        self.assertEqual(MODULE.proximity_band(300),">250m")
        self.assertEqual(MODULE.proximity_band(None),"no_road_geometry")

if __name__=="__main__": unittest.main()
