"""Tests for the admin-only connected-road route geometry preview endpoint.

The endpoint routes a historical route's ordered stops through the OSM road
graph. It must never write to the database and must flag legs it cannot route
instead of inventing geometry.
"""

import json

import pytest

from app.admin import routes as admin_routes
from app.snapping import reset_road_index_cache


@pytest.fixture(autouse=True)
def _fresh_road_cache():
    reset_road_index_cache()
    yield
    reset_road_index_cache()


@pytest.fixture()
def logged_in(client):
    with client.session_transaction() as session:
        session["admin_user_id"] = 1
    return client


HISTORICAL_SOURCE_NAME = (
    "Karachi Bus Network Research Dataset (user-provided cleaned files)")


def _road_feature(way_id, coords, tags=None):
    return {
        "type": "Feature",
        "id": f"way/{way_id}/1",
        "properties": {"@id": way_id, "tags": tags or {"highway": "residential"}},
        "geometry": {"type": "LineString", "coordinates": coords},
    }


def _write_roads(tmp_path, features):
    roads = tmp_path / "roads.geojson"
    roads.write_text(json.dumps({
        "type": "FeatureCollection", "features": features,
    }), encoding="utf-8")
    return roads


def _config(monkeypatch, roads_path, **overrides):
    config = {
        "OSM_ROADS_GEOJSON": str(roads_path),
        "ROUTE_SNAP_MAX_DISTANCE_M": overrides.get("snap", 150),
        "ROUTE_BBOX_PAD_M": overrides.get("pad", 1500),
        "ROUTE_COST_BUDGET_FACTOR": overrides.get("factor", 3.0),
        "ROUTE_COST_BUDGET_EXTRA_M": overrides.get("extra", 2500),
    }
    monkeypatch.setattr(
        admin_routes, "current_app", type("Cfg", (), {"config": config})())


def _patch_cursor(monkeypatch, route_row, directions_rows, stops_by_direction):
    class FakeCursor:
        def __init__(self):
            self.query = ""
            self.params = None

        def execute(self, query, params=None):
            self.query = query
            self.params = params

        def fetchone(self):
            if "FROM bus_routes" in self.query:
                return route_row
            raise AssertionError(f"Unexpected fetchone: {self.query}")

        def fetchall(self):
            if "FROM route_directions" in self.query:
                return directions_rows
            if "FROM route_stops" in self.query:
                direction_id = self.params[0]
                return stops_by_direction.get(direction_id, [])
            raise AssertionError(f"Unexpected fetchall: {self.query}")

    class FakeCursorContext:
        def __enter__(self):
            return None, FakeCursor()

        def __exit__(self, exc_type, exc, traceback):
            return False

    monkeypatch.setattr(admin_routes, "cursor_context", FakeCursorContext)


def _route_row(route_id=94, code="EV-1"):
    return {"id": route_id, "route_code": code,
            "route_name": code, "status": "under_review"}


def _direction_row(direction_id=94, name="EV-1"):
    return {"id": direction_id, "direction_name": name,
            "start_label": None, "end_label": None}


def _stop_row(stop_id, name, lat, lng, sequence, status="under_review"):
    return {"id": stop_id, "stop_name": name, "latitude": lat,
            "longitude": lng, "status": status, "stop_sequence": sequence}


def test_route_geometry_requires_login(client):
    response = client.get("/admin/historical-network/route-geometry?route_id=94")
    assert response.status_code == 302
    assert "/admin/login" in response.headers["Location"]


def test_route_geometry_rejects_non_numeric_route_id(logged_in):
    response = logged_in.get("/admin/historical-network/route-geometry?route_id=abc")
    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "INVALID_ROUTE_ID"


def test_route_geometry_route_not_in_historical_source(logged_in, monkeypatch, tmp_path):
    _patch_cursor(monkeypatch, None, [], {})
    roads = _write_roads(tmp_path, [])
    _config(monkeypatch, roads)
    response = logged_in.get("/admin/historical-network/route-geometry?route_id=15")
    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "NOT_FOUND"


def test_route_geometry_route_without_directions(logged_in, monkeypatch, tmp_path):
    _patch_cursor(monkeypatch, _route_row(), [], {})
    roads = _write_roads(tmp_path, [])
    _config(monkeypatch, roads)
    response = logged_in.get("/admin/historical-network/route-geometry?route_id=94")
    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "NO_DIRECTIONS"


def test_route_geometry_missing_road_data_returns_503(logged_in, monkeypatch, tmp_path):
    _patch_cursor(monkeypatch, _route_row(), [_direction_row()], {})
    missing = tmp_path / "does-not-exist.geojson"
    _config(monkeypatch, missing)
    response = logged_in.get("/admin/historical-network/route-geometry?route_id=94")
    assert response.status_code == 503
    assert response.get_json()["error"]["code"] == "ROAD_DATA_MISSING"


def test_route_geometry_routed_two_stop_route(logged_in, monkeypatch, tmp_path):
    # One east-west road, two stops on it in travel order.
    roads = _write_roads(tmp_path, [
        _road_feature(1000, [[67.00, 24.90], [67.01, 24.90]],
                      {"highway": "primary", "name": "Test Road"}),
    ])
    _patch_cursor(
        monkeypatch, _route_row(), [_direction_row()],
        {94: [_stop_row(514, "Stop A", 24.9000, 67.0000, 1),
              _stop_row(515, "Stop B", 24.9000, 67.0100, 2)]})
    _config(monkeypatch, roads)
    response = logged_in.get("/admin/historical-network/route-geometry?route_id=94")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["route"]["id"] == 94
    assert payload["route"]["code"] == "EV-1"
    assert payload["note"]["code"] == "CANDIDATE_ONLY"
    assert payload["config"]["max_snap_distance_m"] == 150
    direction = payload["directions"][0]
    assert direction["direction_id"] == 94
    assert direction["summary"]["status"] == "routed"
    assert direction["summary"]["leg_count"] == 1
    assert direction["legs"][0]["status"] == "routed"
    assert direction["legs"][0]["from_stop"]["id"] == 514
    assert direction["legs"][0]["to_stop"]["id"] == 515
    # Geometry runs stop A → road nodes → stop B.
    assert direction["geometry"][0] == [67.0, 24.9]
    assert direction["geometry"][-1] == [67.01, 24.9]
    way_ids = [way["osm_way_id"] for way in direction["legs"][0]["ways_used"]]
    assert way_ids == ["1000"]


def test_route_geometry_flags_disconnected_leg(logged_in, monkeypatch, tmp_path):
    # Two roads with no connection; the second leg must be flagged, not bridged.
    roads = _write_roads(tmp_path, [
        _road_feature(1000, [[67.00, 24.90], [67.01, 24.90]]),
        _road_feature(2000, [[67.50, 25.50], [67.51, 25.50]]),
    ])
    _patch_cursor(
        monkeypatch, _route_row(), [_direction_row()],
        {94: [_stop_row(1, "Stop A", 24.9000, 67.0000, 1),
              _stop_row(2, "Stop B", 24.9000, 67.0100, 2),
              _stop_row(3, "Stop C", 25.5000, 67.5000, 3)]})
    _config(monkeypatch, roads)
    response = logged_in.get("/admin/historical-network/route-geometry?route_id=94")
    assert response.status_code == 200
    direction = response.get_json()["directions"][0]
    assert direction["summary"]["status"] == "partial"
    assert direction["summary"]["routed_legs"] == 1
    assert direction["summary"]["problem_legs"] == 1
    assert direction["legs"][1]["status"] == "no_path"
    assert "no_connected_path_within_budget" in direction["legs"][1]["flags"]
    # Problem legs are never merged into the combined geometry.
    assert direction["geometry"][-1] == [67.01, 24.9]


def test_route_geometry_reports_stops_without_coordinates(logged_in, monkeypatch, tmp_path):
    roads = _write_roads(tmp_path, [
        _road_feature(1000, [[67.00, 24.90], [67.01, 24.90]]),
    ])
    _patch_cursor(
        monkeypatch, _route_row(), [_direction_row()],
        {94: [_stop_row(514, "Stop A", 24.9000, 67.0000, 1),
              _stop_row(515, "Unmatched Stop", None, None, 2)]})
    _config(monkeypatch, roads)
    response = logged_in.get("/admin/historical-network/route-geometry?route_id=94")
    assert response.status_code == 200
    direction = response.get_json()["directions"][0]
    assert direction["summary"]["status"] == "missing_coordinates"
    assert direction["legs"] == []
    assert direction["stops_without_coordinates"] == [
        {"id": 515, "name": "Unmatched Stop", "sequence": 2}]
    # Coordinate-bearing stops are still reported.
    assert [s["id"] for s in direction["stops"]] == [514]


def test_route_geometry_empty_direction_summarised(logged_in, monkeypatch, tmp_path):
    roads = _write_roads(tmp_path, [
        _road_feature(1000, [[67.00, 24.90], [67.01, 24.90]]),
    ])
    _patch_cursor(
        monkeypatch, _route_row(), [_direction_row()], {94: []})
    _config(monkeypatch, roads)
    response = logged_in.get("/admin/historical-network/route-geometry?route_id=94")
    assert response.status_code == 200
    direction = response.get_json()["directions"][0]
    assert direction["summary"]["status"] == "no_stops"
    assert direction["legs"] == []
