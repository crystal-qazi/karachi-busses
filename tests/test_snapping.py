import importlib.util
import json
import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path

APP_SNAPPING = Path(__file__).resolve().parents[1] / "app" / "snapping.py"
SPEC = importlib.util.spec_from_file_location("app.snapping", APP_SNAPPING)
SNAP = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SNAP  # register so dataclass/typing machinery resolves
SPEC.loader.exec_module(SNAP)

try:  # pragma: no cover - exercised only when shapely/pyproj importable
    import pyproj  # noqa: F401
    HAS_PYPROJ = True
except ImportError:
    HAS_PYPROJ = False


def _road_feature(way_id, coords, tags=None):
    return {
        "type": "Feature",
        "id": f"way/{way_id}/1",
        "properties": {
            "@type": "way",
            "@id": way_id,
            "tags": tags or {"highway": "residential", "name": "Test Road"},
        },
        "geometry": {"type": "LineString", "coordinates": coords},
    }


@unittest.skipUnless(HAS_PYPROJ, "pyproj not installed")
class LoadRoadsTests(unittest.TestCase):
    def test_load_accepts_dict(self):
        fc = {"type": "FeatureCollection", "features": [
            _road_feature(1, [(67.0, 24.8), (67.1, 24.8)]),
        ]}
        index = SNAP.load_roads(fc)
        self.assertEqual(index.feature_count, 1)

    def test_load_accepts_json_string(self):
        import json
        fc = {"type": "FeatureCollection", "features": [
            _road_feature(2, [(67.0, 24.8), (67.1, 24.8)]),
        ]}
        index = SNAP.load_roads(json.dumps(fc))
        self.assertEqual(index.feature_count, 1)

    def test_load_accepts_path(self):
        import json
        import tempfile
        fc = {"type": "FeatureCollection", "features": [
            _road_feature(3, [(67.0, 24.8), (67.1, 24.8)]),
        ]}
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "roads.geojson"
            p.write_text(json.dumps(fc), encoding="utf-8")
            index = SNAP.load_roads(p)
            self.assertEqual(index.feature_count, 1)

    def test_empty_feature_collection(self):
        index = SNAP.load_roads({"type": "FeatureCollection", "features": []})
        self.assertTrue(index.is_empty)
        self.assertIsNone(index.snap(24.8, 67.05, 1000))

    def test_skips_non_line_features(self):
        fc = {"type": "FeatureCollection", "features": [
            {"type": "Feature", "properties": {}, "geometry": {
                "type": "Point", "coordinates": [67.0, 24.8]}},
            _road_feature(5, [(67.0, 24.8), (67.1, 24.8)]),
        ]}
        index = SNAP.load_roads(fc)
        self.assertEqual(index.feature_count, 1)

    def test_multiline_is_flattened(self):
        fc = {"type": "FeatureCollection", "features": [
            {"type": "Feature", "properties": {"@id": 9, "tags": {"highway": "primary"}},
             "geometry": {"type": "MultiLineString", "coordinates": [
                 [(67.0, 24.8), (67.05, 24.8)],
                 [(67.05, 24.8), (67.1, 24.8)],
             ]}},
        ]}
        index = SNAP.load_roads(fc)
        self.assertEqual(index.feature_count, 2)


@unittest.skipUnless(HAS_PYPROJ, "pyproj not installed")
class SnapTests(unittest.TestCase):
    def setUp(self):
        # A horizontal road at latitude 24.80 from lng 67.00 to 67.10.
        fc = {"type": "FeatureCollection", "features": [
            _road_feature(100, [(67.0, 24.80), (67.10, 24.80)],
                          {"highway": "secondary", "name": "Shahrah-e-Faisal"}),
        ]}
        self.index = SNAP.load_roads(fc)

    def test_snaps_to_road_within_radius(self):
        # Point just north of the road; snap should land exactly on the line.
        result = SNAP.nearest_road_snap(24.801, 67.05, self.index, max_distance_m=500)
        self.assertIsNotNone(result)
        # UTM round-trip precision is ~1 m (~1e-5 deg), so use a tolerant bound.
        self.assertAlmostEqual(result.lat, 24.80, places=4)
        self.assertAlmostEqual(result.lng, 67.05, places=6)
        self.assertEqual(result.road_name, "Shahrah-e-Faisal")
        self.assertEqual(result.highway, "secondary")
        self.assertEqual(result.way_id, "100")
        self.assertLess(result.distance_m, 200)

    def test_returns_none_beyond_max_distance(self):
        result = SNAP.nearest_road_snap(24.85, 67.05, self.index, max_distance_m=100)
        self.assertIsNone(result)

    def test_as_dict_shape(self):
        result = SNAP.nearest_road_snap(24.801, 67.05, self.index, max_distance_m=500)
        d = result.as_dict()
        for key in ("latitude", "longitude", "distance_m", "road_name", "highway", "osm_way_id"):
            self.assertIn(key, d)


@unittest.skipUnless(HAS_PYPROJ, "pyproj not installed")
class SnapCandidatesTests(unittest.TestCase):
    def setUp(self):
        # Two parallel roads: one at lat 24.80 (nearest), one at 24.805.
        near = _road_feature(300, [(67.0, 24.80), (67.10, 24.80)],
                             {"highway": "trunk", "name": "Near Road"})
        far = _road_feature(301, [(67.0, 24.805), (67.10, 24.805)],
                            {"highway": "secondary", "name": "Far Road"})
        self.index = SNAP.load_roads(
            {"type": "FeatureCollection", "features": [near, far]}
        )

    def test_returns_candidates_ordered_by_distance(self):
        candidates = SNAP.road_snap_candidates(24.802, 67.05, self.index,
                                               max_distance_m=500, max_candidates=5)
        self.assertEqual(len(candidates), 2)
        self.assertEqual(candidates[0].way_id, "300")
        self.assertEqual(candidates[1].way_id, "301")
        self.assertLess(candidates[0].distance_m, candidates[1].distance_m)
        # Each candidate carries the road geometry and tags.
        self.assertTrue(candidates[0].way_geometry)
        self.assertEqual(candidates[0].way_geometry[0], (67.0, 24.80))
        self.assertEqual(candidates[0].way_tags.get("highway"), "trunk")
        self.assertEqual(candidates[0].way_tags.get("name"), "Near Road")
        # as_dict serialises geometry + tags.
        d = candidates[0].as_dict()
        self.assertIn("way_geometry", d)
        self.assertIn("tags", d)

    def test_caps_candidate_count(self):
        # Three roads, but cap at 2.
        third = _road_feature(302, [(67.0, 24.804), (67.10, 24.804)],
                              {"highway": "residential", "name": "Third Road"})
        index = SNAP.load_roads(
            {"type": "FeatureCollection", "features": [
                _road_feature(300, [(67.0, 24.80), (67.10, 24.80)]),
                _road_feature(301, [(67.0, 24.802), (67.10, 24.802)]),
                third,
            ]}
        )
        candidates = SNAP.road_snap_candidates(24.802, 67.05, index,
                                               max_distance_m=500, max_candidates=2)
        self.assertEqual(len(candidates), 2)
        self.assertEqual({c.way_id for c in candidates}, {"300", "301"})

    def test_deduplicates_overlapping_duplicate_way_segments(self):
        # The same OSM way appears as overlapping duplicate segments; they must
        # collapse to a single candidate (nearest segment).
        dup1 = _road_feature(400, [(67.0, 24.80), (67.10, 24.80)],
                             {"highway": "primary", "name": "Dup Road"})
        dup2 = _road_feature(400, [(67.0, 24.80), (67.10, 24.80)],
                             {"highway": "primary", "name": "Dup Road"})
        other = _road_feature(401, [(67.0, 24.805), (67.10, 24.805)],
                              {"highway": "residential", "name": "Other Road"})
        index = SNAP.load_roads(
            {"type": "FeatureCollection", "features": [dup1, dup2, other]}
        )
        candidates = SNAP.road_snap_candidates(24.802, 67.05, index,
                                               max_distance_m=500, max_candidates=5)
        way_ids = [c.way_id for c in candidates]
        self.assertEqual(way_ids, ["400", "401"])
        self.assertEqual(len(way_ids), len(set(way_ids)))

    def test_distinct_overlapping_roads_both_appear(self):
        # Two *different* ways that overlap in space each remain candidates.
        a = _road_feature(500, [(67.0, 24.80), (67.10, 24.80)],
                          {"highway": "trunk", "name": "Road A"})
        b = _road_feature(501, [(67.0, 24.80), (67.10, 24.80)],
                          {"highway": "service", "name": "Road B"})
        index = SNAP.load_roads({"type": "FeatureCollection", "features": [a, b]})
        candidates = SNAP.road_snap_candidates(24.802, 67.05, index,
                                               max_distance_m=500, max_candidates=5)
        self.assertEqual({c.way_id for c in candidates}, {"500", "501"})

    def test_invalid_geometry_is_skipped(self):
        # A malformed geometry feature must not break loading or snapping.
        fc = {"type": "FeatureCollection", "features": [
            {"type": "Feature", "properties": {}, "geometry": {
                "type": "LineString", "coordinates": "not-a-coordinate-list"}},
            _road_feature(600, [(67.0, 24.80), (67.10, 24.80)]),
        ]}
        index = SNAP.load_roads(fc)
        self.assertEqual(index.feature_count, 1)
        candidates = SNAP.road_snap_candidates(24.802, 67.05, index,
                                               max_distance_m=500, max_candidates=5)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].way_id, "600")

    def test_no_candidates_beyond_radius(self):
        candidates = SNAP.road_snap_candidates(24.85, 67.05, self.index,
                                               max_distance_m=100, max_candidates=5)
        self.assertEqual(candidates, [])


@unittest.skipUnless(HAS_PYPROJ, "pyproj not installed")
class RoadIndexCacheTests(unittest.TestCase):
    """Process-level cache semantics of ``load_roads_cached``."""

    # 2020-09 in nanoseconds; an exact multiple of the 100 ns FILETIME step
    # so os.utime round-trips it exactly on Windows.
    BASE_MTIME_NS = 1_600_000_000_000_000_000

    def setUp(self):
        SNAP.reset_road_index_cache()
        self.addCleanup(SNAP.reset_road_index_cache)
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "roads.geojson"
        self.cache_key = str(self.path.resolve())

    def _write(self, text, mtime_ns=None):
        self.path.write_text(text, encoding="utf-8")
        if mtime_ns is not None:
            os.utime(self.path, ns=(mtime_ns, mtime_ns))

    def _road_fc(self, way_id):
        return json.dumps({"type": "FeatureCollection", "features": [
            _road_feature(way_id, [(67.0, 24.8), (67.1, 24.8)]),
        ]})

    def test_missing_file_raises_road_source_error(self):
        with self.assertRaises(SNAP.RoadSourceError):
            SNAP.load_roads_cached(self.path)
        self.assertNotIn(self.cache_key, SNAP._road_index_cache)

    def test_directory_source_raises_road_source_error(self):
        with self.assertRaises(SNAP.RoadSourceError):
            SNAP.load_roads_cached(self.path.parent)

    def test_invalid_json_raises_and_leaves_no_cache_entry(self):
        self._write("{not valid json")
        with self.assertRaises(SNAP.RoadSourceError):
            SNAP.load_roads_cached(self.path)
        self.assertNotIn(self.cache_key, SNAP._road_index_cache)

    def test_failed_build_does_not_poison_cache(self):
        self._write("{not valid json")
        with self.assertRaises(SNAP.RoadSourceError):
            SNAP.load_roads_cached(self.path)
        # Repairing the same file must yield a working index.
        self._write(self._road_fc(700))
        index = SNAP.load_roads_cached(self.path)
        self.assertEqual(index.feature_count, 1)
        result = SNAP.nearest_road_snap(24.801, 67.05, index, max_distance_m=500)
        self.assertEqual(result.way_id, "700")

    def test_empty_collection_is_cached_as_empty_index(self):
        self._write(json.dumps({"type": "FeatureCollection", "features": []}))
        first = SNAP.load_roads_cached(self.path)
        self.assertTrue(first.is_empty)
        self.assertIsNone(SNAP.nearest_road_snap(24.8, 67.0, first,
                                                 max_distance_m=100))
        self.assertIs(SNAP.load_roads_cached(self.path), first)

    def test_cache_reuse_returns_same_object(self):
        self._write(self._road_fc(100))
        first = SNAP.load_roads_cached(self.path)
        self.assertIs(SNAP.load_roads_cached(self.path), first)

    def test_mtime_change_invalidates_cache(self):
        self._write(self._road_fc(1000), mtime_ns=self.BASE_MTIME_NS)
        first = SNAP.load_roads_cached(self.path)
        # Same byte length, different content, a later mtime.
        self._write(self._road_fc(2000),
                    mtime_ns=self.BASE_MTIME_NS + 1_000_000_000)
        second = SNAP.load_roads_cached(self.path)
        self.assertIsNot(second, first)
        result = SNAP.nearest_road_snap(24.801, 67.05, second,
                                        max_distance_m=500)
        self.assertEqual(result.way_id, "2000")

    def test_size_change_invalidates_cache(self):
        self._write(self._road_fc(1000), mtime_ns=self.BASE_MTIME_NS)
        first = SNAP.load_roads_cached(self.path)
        original_size = os.stat(self.path).st_size
        # Longer content, original mtime restored so only the size differs.
        self._write(self._road_fc(3000) + "\n", mtime_ns=self.BASE_MTIME_NS)
        self.assertEqual(os.stat(self.path).st_mtime_ns, self.BASE_MTIME_NS)
        second = SNAP.load_roads_cached(self.path)
        self.assertIsNot(second, first)
        self.assertGreater(os.stat(self.path).st_size, original_size)
        result = SNAP.nearest_road_snap(24.801, 67.05, second,
                                        max_distance_m=500)
        self.assertEqual(result.way_id, "3000")

    def test_concurrent_requests_build_once(self):
        self._write(self._road_fc(400))
        real_load = SNAP.load_roads
        builds = []
        builds_lock = threading.Lock()

        def counting_load(geojson):
            with builds_lock:
                builds.append(1)
            return real_load(geojson)

        SNAP.load_roads = counting_load
        self.addCleanup(setattr, SNAP, "load_roads", real_load)

        barrier = threading.Barrier(4)
        results, errors = [], []

        def worker():
            try:
                barrier.wait(timeout=10)
                results.append(SNAP.load_roads_cached(self.path))
            except Exception as exc:  # surfaced below
                errors.append(exc)

        threads = [threading.Thread(target=worker) for _ in range(4)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=30)
        self.assertEqual(errors, [])
        self.assertEqual(len(results), 4)
        self.assertEqual(len(builds), 1)
        self.assertEqual(len({id(r) for r in results}), 1)

    def test_reset_forces_rebuild(self):
        self._write(self._road_fc(500))
        first = SNAP.load_roads_cached(self.path)
        SNAP.reset_road_index_cache(self.path)
        second = SNAP.load_roads_cached(self.path)
        self.assertIsNot(second, first)
        SNAP.reset_road_index_cache()
        third = SNAP.load_roads_cached(self.path)
        self.assertIsNot(third, second)

    def test_relative_and_absolute_paths_share_entry(self):
        self._write(self._road_fc(600))
        absolute = SNAP.load_roads_cached(self.path)
        cwd = os.getcwd()
        os.chdir(self.path.parent)
        self.addCleanup(os.chdir, cwd)
        relative = SNAP.load_roads_cached(Path("roads.geojson"))
        self.assertIs(relative, absolute)


if __name__ == "__main__":
    unittest.main()
