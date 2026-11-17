import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "acquire_osm_boundary.py"
SPEC = importlib.util.spec_from_file_location("acquire_osm_boundary", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


VALID_XML = """<osm version="0.6">
  <node id="1" lat="24.0" lon="67.0"/>
  <node id="2" lat="24.1" lon="67.1"/>
  <way id="10"><nd ref="1"/><nd ref="2"/></way>
  <relation id="6080948" version="4" timestamp="2025-01-14T11:35:00Z">
    <member type="way" ref="10" role="outer"/>
    <tag k="boundary" v="administrative"/>
    <tag k="name" v="Karachi Division"/>
  </relation>
</osm>"""


class OSMRelationAcquisitionTests(unittest.TestCase):
    def test_inspects_relation_identity_tags_and_references(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "relation.osm"
            path.write_text(VALID_XML, encoding="utf-8")
            result = MODULE.inspect_relation(path)
        self.assertEqual(result["relation_id"], 6080948)
        self.assertEqual(result["outer_member_count"], 1)
        self.assertEqual(result["member_way_count"], 1)
        self.assertEqual(result["missing_direct_members"], 0)
        self.assertEqual(result["missing_way_nodes"], 0)

    def test_rejects_wrong_relation_name(self):
        xml = VALID_XML.replace("Karachi Division", "Wrong Place")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "relation.osm"
            path.write_text(xml, encoding="utf-8")
            with self.assertRaises(ValueError):
                MODULE.inspect_relation(path)

    def test_rejects_missing_member_way(self):
        xml = VALID_XML.replace('<way id="10"><nd ref="1"/><nd ref="2"/></way>', "")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "relation.osm"
            path.write_text(xml, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "direct relation members"):
                MODULE.inspect_relation(path)

    def test_rejects_missing_way_node(self):
        xml = VALID_XML.replace('<node id="2" lat="24.1" lon="67.1"/>', "")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "relation.osm"
            path.write_text(xml, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "nodes referenced"):
                MODULE.inspect_relation(path)

    def test_dry_run_does_not_extract(self):
        import subprocess
        result = subprocess.run(
            ["python", str(SCRIPT)],
            check=True, capture_output=True, text=True
        )
        self.assertIn("DRY RUN", result.stdout)
        self.assertNotIn("Extracting", result.stdout)

    def test_requires_local_pbf_before_running_osmium(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                MODULE.extract_from_pbf(Path(tmp) / "missing.osm.pbf", Path(tmp) / "out")


if __name__ == "__main__":
    unittest.main()
