"""Tests for the admin-only OSM road snap preview endpoint.

The endpoint proposes a *geometric* road snap for a single historical stop. It
must never write to the database: route assignments, stop names, statuses and
stored coordinates are all read-only here.
"""

import json

import pytest

from app.admin import routes as admin_routes


@pytest.fixture()
def logged_in(client):
    with client.session_transaction() as session:
        session["admin_user_id"] = 1
    return client


def _historical_source_row():
    return {
        "id": 4,
        "source_name": "Karachi Bus Network Research Dataset (user-provided cleaned files)",
        "verification_status": "pending",
    }


def _stop_row(stop_id=514, lat=24.95043743, lng=67.21548491, status="under_review"):
    return {
        "id": stop_id,
        "stop_name": "Cmh Malir Cantt",
        "latitude": lat,
        "longitude": lng,
        "status": status,
    }


def _fake_cursor(stop_row=None):
    class FakeCursor:
        def __init__(self):
            self.query = ""
            self.params = None

        def execute(self, query, params=None):
            self.query = query
            self.params = params

        def fetchone(self):
            if "FROM data_sources" in self.query:
                return _historical_source_row()
            if "FROM bus_stops" in self.query:
                return stop_row
            raise AssertionError(f"Unexpected query: {self.query}")

    return FakeCursor()


def _patch_cursor(monkeypatch, stop_row=_stop_row()):
    class FakeCursorContext:
        def __enter__(self):
            return None, _fake_cursor(stop_row)

        def __exit__(self, exc_type, exc, traceback):
            return False

    monkeypatch.setattr(admin_routes, "cursor_context", lambda: FakeCursorContext())
    return _fake_cursor(stop_row)


def test_snap_endpoint_requires_login(client):
    response = client.get("/admin/historical-network/snap?stop_id=514")
    assert response.status_code == 302
    assert "/admin/login" in response.headers["Location"]


def test_snap_endpoint_rejects_non_numeric_stop_id(logged_in):
    response = logged_in.get("/admin/historical-network/snap?stop_id=abc")
    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "INVALID_STOP_ID"


def test_snap_endpoint_missing_road_data_returns_503(logged_in, monkeypatch, tmp_path):
    _patch_cursor(monkeypatch, _stop_row())
    # Point at a GeoJSON path that does not exist.
    missing = tmp_path / "does-not-exist.geojson"
    monkeypatch.setattr(
        admin_routes,
        "current_app",
        type("Cfg", (), {"config": {"OSM_ROADS_GEOJSON": str(missing),
                                    "SNAP_MAX_DISTANCE_M": 500}})(),
    )
    response = logged_in.get("/admin/historical-network/snap?stop_id=514")
    assert response.status_code == 503
    assert response.get_json()["error"]["code"] == "ROAD_DATA_MISSING"


def test_snap_endpoint_invalid_stop_coordinates_returns_422(logged_in, monkeypatch, tmp_path):
    _patch_cursor(monkeypatch, _stop_row(lat=None, lng=None))
    roads = tmp_path / "roads.geojson"
    roads.write_text(json.dumps({"type": "FeatureCollection", "features": []}), encoding="utf-8")
    monkeypatch.setattr(
        admin_routes,
        "current_app",
        type("Cfg", (), {"config": {"OSM_ROADS_GEOJSON": str(roads),
                                    "SNAP_MAX_DISTANCE_M": 500}})(),
    )
    response = logged_in.get("/admin/historical-network/snap?stop_id=514")
    assert response.status_code == 422
    assert response.get_json()["error"]["code"] == "INVALID_COORDINATES"


def test_snap_endpoint_successful_preview(logged_in, monkeypatch, tmp_path):
    _patch_cursor(monkeypatch, _stop_row())
    # A horizontal road near the stop at latitude 24.95.
    roads = tmp_path / "roads.geojson"
    roads.write_text(json.dumps({
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "id": "way/1000/1",
            "properties": {"@id": 1000, "tags": {"highway": "trunk", "name": "Malir Cantt Road"}},
            "geometry": {"type": "LineString", "coordinates": [
                [67.21, 24.9504], [67.22, 24.9504],
            ]},
        }],
    }), encoding="utf-8")
    monkeypatch.setattr(
        admin_routes,
        "current_app",
        type("Cfg", (), {"config": {"OSM_ROADS_GEOJSON": str(roads),
                                    "SNAP_MAX_DISTANCE_M": 500}})(),
    )
    response = logged_in.get("/admin/historical-network/snap?stop_id=514")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["stop"]["id"] == 514
    assert payload["stop"]["status"] == "under_review"
    assert payload["snapped"]["road_name"] == "Malir Cantt Road"
    assert payload["snapped"]["highway"] == "trunk"
    assert payload["snapped"]["osm_way_id"] == "1000"
    assert payload["snapped"]["distance_m"] >= 0
    assert payload["note"]["code"] == "CANDIDATE_ONLY"


def test_snap_endpoint_no_road_within_range(logged_in, monkeypatch, tmp_path):
    _patch_cursor(monkeypatch, _stop_row())
    # Road far away (well beyond the max distance) -> no snap candidate.
    roads = tmp_path / "roads.geojson"
    roads.write_text(json.dumps({
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "id": "way/2000/1",
            "properties": {"@id": 2000, "tags": {"highway": "residential", "name": "Far Road"}},
            "geometry": {"type": "LineString", "coordinates": [
                [67.10, 24.50], [67.11, 24.50],
            ]},
        }],
    }), encoding="utf-8")
    monkeypatch.setattr(
        admin_routes,
        "current_app",
        type("Cfg", (), {"config": {"OSM_ROADS_GEOJSON": str(roads),
                                    "SNAP_MAX_DISTANCE_M": 500}})(),
    )
    response = logged_in.get("/admin/historical-network/snap?stop_id=514")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["snapped"] is None
    assert payload["note"]["code"] == "NO_SNAP_WITHIN_RANGE"


def _write_roads(tmp_path, features):
    roads = tmp_path / "roads.geojson"
    roads.write_text(json.dumps({
        "type": "FeatureCollection",
        "features": features,
    }), encoding="utf-8")
    return roads


def _snap_config_monkeypatch(monkeypatch, roads_path, max_distance=500, max_candidates=5):
    monkeypatch.setattr(
        admin_routes,
        "current_app",
        type("Cfg", (), {"config": {
            "OSM_ROADS_GEOJSON": str(roads_path),
            "SNAP_MAX_DISTANCE_M": max_distance,
            "SNAP_MAX_CANDIDATES": max_candidates,
        }})(),
    )


def _road_feature(way_id, coords, tags=None):
    return {
        "type": "Feature",
        "id": f"way/{way_id}/1",
        "properties": {"@id": way_id, "tags": tags or {"highway": "residential"}},
        "geometry": {"type": "LineString", "coordinates": coords},
    }


def test_snap_endpoint_returns_candidates_ordered(logged_in, monkeypatch, tmp_path):
    _patch_cursor(monkeypatch, _stop_row())
    roads = _write_roads(tmp_path, [
        _road_feature(1000, [[67.21, 24.9504], [67.22, 24.9504]],
                      {"highway": "trunk", "name": "Malir Cantt Road"}),
        _road_feature(2000, [[67.21, 24.9512], [67.22, 24.9512]],
                      {"highway": "secondary", "name": "Parallel Road"}),
    ])
    _snap_config_monkeypatch(monkeypatch, roads)
    response = logged_in.get("/admin/historical-network/snap?stop_id=514")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["max_candidates"] == 5
    assert len(payload["candidates"]) == 2
    # Ordered by distance, nearest first.
    assert payload["candidates"][0]["osm_way_id"] == "1000"
    assert payload["candidates"][1]["osm_way_id"] == "2000"
    assert payload["candidates"][0]["distance_m"] < payload["candidates"][1]["distance_m"]
    # Each candidate carries geometry + tags; the nearest equals `snapped`.
    first = payload["candidates"][0]
    assert first["road_name"] == "Malir Cantt Road"
    assert first["highway"] == "trunk"
    assert first["way_geometry"]
    assert first["way_geometry"][0] == [67.21, 24.9504]
    assert first["tags"]["highway"] == "trunk"
    assert payload["snapped"]["osm_way_id"] == first["osm_way_id"]


def test_snap_endpoint_deduplicates_duplicate_way_segments(logged_in, monkeypatch, tmp_path):
    _patch_cursor(monkeypatch, _stop_row())
    # Same way id as two overlapping segments plus a distinct parallel road.
    roads = _write_roads(tmp_path, [
        _road_feature(3000, [[67.21, 24.9504], [67.22, 24.9504]],
                      {"highway": "primary", "name": "Dup Road"}),
        _road_feature(3000, [[67.21, 24.9504], [67.22, 24.9504]],
                      {"highway": "primary", "name": "Dup Road"}),
        _road_feature(3001, [[67.21, 24.9512], [67.22, 24.9512]],
                      {"highway": "residential", "name": "Other Road"}),
    ])
    _snap_config_monkeypatch(monkeypatch, roads)
    response = logged_in.get("/admin/historical-network/snap?stop_id=514")
    assert response.status_code == 200
    payload = response.get_json()
    way_ids = [c["osm_way_id"] for c in payload["candidates"]]
    assert way_ids == ["3000", "3001"]
    assert len(way_ids) == len(set(way_ids))


def test_snap_endpoint_caps_candidate_count(logged_in, monkeypatch, tmp_path):
    _patch_cursor(monkeypatch, _stop_row())
    roads = _write_roads(tmp_path, [
        _road_feature(4000, [[67.21, 24.9504], [67.22, 24.9504]]),
        _road_feature(4001, [[67.21, 24.9510], [67.22, 24.9510]]),
        _road_feature(4002, [[67.21, 24.9518], [67.22, 24.9518]]),
    ])
    _snap_config_monkeypatch(monkeypatch, roads, max_candidates=2)
    response = logged_in.get("/admin/historical-network/snap?stop_id=514")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["max_candidates"] == 2
    assert len(payload["candidates"]) == 2


def test_snap_endpoint_invalid_geometry_is_skipped(logged_in, monkeypatch, tmp_path):
    _patch_cursor(monkeypatch, _stop_row())
    roads = _write_roads(tmp_path, [
        {"type": "Feature", "properties": {}, "geometry": {
            "type": "LineString", "coordinates": "not-a-coordinate-list"}},
        _road_feature(5000, [[67.21, 24.9504], [67.22, 24.9504]],
                      {"highway": "tertiary", "name": "Valid Road"}),
    ])
    _snap_config_monkeypatch(monkeypatch, roads)
    response = logged_in.get("/admin/historical-network/snap?stop_id=514")
    assert response.status_code == 200
    payload = response.get_json()
    assert len(payload["candidates"]) == 1
    assert payload["candidates"][0]["osm_way_id"] == "5000"


def test_snap_endpoint_no_candidates_sets_empty_array(logged_in, monkeypatch, tmp_path):
    _patch_cursor(monkeypatch, _stop_row())
    roads = _write_roads(tmp_path, [
        _road_feature(6000, [[67.10, 24.50], [67.11, 24.50]],
                      {"highway": "residential", "name": "Far Road"}),
    ])
    _snap_config_monkeypatch(monkeypatch, roads)
    response = logged_in.get("/admin/historical-network/snap?stop_id=514")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["snapped"] is None
    assert payload["candidates"] == []
    assert payload["note"]["code"] == "NO_SNAP_WITHIN_RANGE"
