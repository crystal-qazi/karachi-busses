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
