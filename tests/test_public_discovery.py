from contextlib import contextmanager

import pytest



def test_map_routes_returns_only_valid_published_route_shapes(client, monkeypatch):
    from app.api import public

    rows = [
        {"direction_id": 7, "direction_name": "Northbound", "route_id": 2,
         "route_code": "R-1", "route_name": "Tower - Saddar",
         "geojson": {"type": "LineString", "coordinates": [[67.0, 24.8], [67.1, 24.9]]}},
        {"direction_id": 8, "direction_name": "Southbound", "route_id": 2,
         "route_code": "R-1", "route_name": "Tower - Saddar", "geojson": None},
    ]

    class Cursor:
        def execute(self, sql, params=None):
            assert "verification_status='verified'" in sql
            assert "r.status='active'" in sql
        def fetchall(self): return rows
        def close(self): pass

    class Connection:
        def cursor(self, dictionary=True): return Cursor()
        def close(self): pass

    @contextmanager
    def fake_cursor_context(**kwargs):
        yield Connection(), Cursor()

    monkeypatch.setattr(public, "cursor_context", fake_cursor_context)
    response = client.get("/api/v1/routes/map")
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["direction_count"] == 1
    assert data["directions"][0]["id"] == 7
    assert data["directions"][0]["shape"]["type"] == "LineString"


def test_nearby_requires_coordinates(client):
    response = client.get("/api/v1/discover/nearby")
    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "INVALID_PARAMETER"


@pytest.mark.parametrize("query", [
    "?lat=91&lng=67", "?lat=24&lng=181", "?lat=24&lng=67&radius=50",
    "?lat=24&lng=67&radius=12000", "?lat=24&lng=67&limit=101", "?lat=nan&lng=67",
])
def test_nearby_rejects_invalid_parameters(client, query):
    response = client.get("/api/v1/discover/nearby" + query)
    assert response.status_code == 400


def test_nearby_returns_grouped_stops_and_routes(client, monkeypatch):
    from app.api import public

    rows = [
        {"stop_id": 3, "stop_name": "Numaish", "latitude": 24.8731, "longitude": 67.0332,
         "address": None, "direction_id": 7, "direction_name": "Northbound",
         "start_label": "Tower", "end_label": "Saddar", "route_id": 2,
         "route_code": "R-1", "route_name": "Tower - Saddar", "operator_name": "Demo",
         "distance_metres": 420.25},
        {"stop_id": 3, "stop_name": "Numaish", "latitude": 24.8731, "longitude": 67.0332,
         "address": None, "direction_id": 8, "direction_name": "Southbound",
         "start_label": "Saddar", "end_label": "Tower", "route_id": 2,
         "route_code": "R-1", "route_name": "Tower - Saddar", "operator_name": "Demo",
         "distance_metres": 420.25},
    ]

    class Cursor:
        def execute(self, sql, params):
            assert "distance_metres" in sql
            assert len(params) == 14
        def fetchall(self): return rows
        def close(self): pass

    class Connection:
        def cursor(self, dictionary=True): return Cursor()
        def close(self): pass

    @contextmanager
    def fake_cursor_context(**kwargs):
        yield Connection(), Cursor()

    monkeypatch.setattr(public, "cursor_context", fake_cursor_context)
    response = client.get("/api/v1/discover/nearby?lat=24.87&lng=67.03")
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["stop_count"] == 1
    assert data["stops"][0]["name"] == "Numaish"
    assert len(data["stops"][0]["directions"]) == 2
    assert data["stops"][0]["directions"][0]["route"]["code"] == "R-1"


def test_direction_not_found(client, monkeypatch):
    from app.api import public

    class Cursor:
        def execute(self, *_args): pass
        def fetchone(self): return None
        def close(self): pass

    class Connection:
        def cursor(self, dictionary=True): return Cursor()
        def close(self): pass

    @contextmanager
    def fake_cursor_context(**kwargs):
        yield Connection(), Cursor()

    monkeypatch.setattr(public, "cursor_context", fake_cursor_context)
    response = client.get("/api/v1/directions/999")
    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "NOT_FOUND"


def test_search_requires_two_characters(client):
    response = client.get("/api/v1/search?q=a")
    assert response.status_code == 400


def test_location_search_validates_query_without_calling_geocoder(client):
    response = client.get("/api/v1/locations/search?q=a")
    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "INVALID_PARAMETER"
