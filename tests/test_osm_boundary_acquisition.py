import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import xml.etree.ElementTree as ET

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "acquire_osm_boundary.py"
SPEC = importlib.util.spec_from_file_location("acquire_osm_boundary", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class OSMRelationAcquisitionTests(unittest.TestCase):
    def test_only_selected_relation_endpoint_on_osm_api(self):
        MODULE.validate_source(MODULE.API_URL)
        for url in (
            "http://api.openstreetmap.org/api/0.6/relation/6080948/full",
            "https://example.com/api/0.6/relation/6080948/full",
            "https://api.openstreetmap.org/api/0.6/relation/1/full",
            "https://api.openstreetmap.org/api/0.6/relation/6080948",
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                MODULE.validate_source(url)

    def test_inspects_relation_identity_tags_and_members(self):
        xml = """<osm version="0.6">
          <relation id="6080948" version="4" timestamp="2025-01-14T11:35:00Z">
            <member type="way" ref="10" role="outer"/>
            <member type="way" ref="11" role="inner"/>
            <tag k="boundary" v="administrative"/>
            <tag k="name" v="Karachi Division"/>
          </relation>
          <way id="10"><nd ref="1"/><nd ref="2"/></way>
          <way id="11"><nd ref="3"/><nd ref="4"/></way>
        </osm>"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "relation.osm"
            path.write_text(xml, encoding="utf-8")
            result = MODULE.inspect_relation(path)
        self.assertEqual(result["relation_id"], 6080948)
        self.assertEqual(result["outer_member_count"], 1)
        self.assertEqual(result["inner_member_count"], 1)
        self.assertEqual(result["member_way_count"], 2)

    def test_rejects_wrong_relation_name(self):
        xml = """<osm><relation id="6080948">
          <tag k="boundary" v="administrative"/>
          <tag k="name" v="Wrong Place"/>
        </relation></osm>"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "relation.osm"
            path.write_text(xml, encoding="utf-8")
            with self.assertRaises(ValueError):
                MODULE.inspect_relation(path)

    def test_dry_run_does_not_download(self):
        import subprocess
        result = subprocess.run(
            ["python", str(SCRIPT)],
            check=True, capture_output=True, text=True
        )
        self.assertIn("DRY RUN", result.stdout)
        self.assertNotIn("downloaded", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()
