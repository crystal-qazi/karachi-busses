from contextlib import contextmanager
import json


def _install_rows(monkeypatch, rows):
    from app.api import journeys as module

    class Cursor:
        def execute(self, *_args): pass
        def fetchall(self): return rows
        def close(self): pass

    class Connection:
        def cursor(self, dictionary=True): return Cursor()
        def close(self): pass

    @contextmanager
    def fake_cursor_context(**kwargs):
        yield Connection(), Cursor()

    monkeypatch.setattr(module, "cursor_context", fake_cursor_context)


def _row(direction, route, sequence, stop_id, stop_name, lat, shape=None):
    return {
        "direction_id": direction, "direction_name": "Outbound",
        "start_label": "Start", "end_label": "End",
        "route_id": route, "route_code": f"R-{route}",
        "route_name": f"Route {route}", "operator_name": "Operator",
        "stop_id": stop_id, "stop_name": stop_name,
        "latitude": lat, "longitude": 67.0, "address": None,
        "stop_sequence": sequence,
        "shape_geojson": json.dumps(shape) if shape else None,
    }


def _journey_url(from_lat=24.8600, to_lat=24.8620, radius=150):
    return (
        "/api/v1/journeys?origin_lat=" + str(from_lat) +
        "&origin_lng=67&destination_lat=" + str(to_lat) +
        "&destination_lng=67&radius=" + str(radius)
    )


def test_journeys_requires_both_locations(client):
    response = client.get("/api/v1/journeys")
    assert response.status_code == 400
    response = client.get("/api/v1/journeys?origin_lat=24.86&origin_lng=67")
    assert response.status_code == 400


def test_journeys_rejects_invalid_coordinates(client):
    assert client.get(_journey_url(from_lat=91)).status_code == 400
    assert client.get(_journey_url(to_lat=24.862, radius=50)).status_code == 400


def test_journeys_returns_empty_when_no_active_stops(client, monkeypatch):
    _install_rows(monkeypatch, [])
    response = client.get(_journey_url())
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["journeys"] == []
    assert data["origin_stop_count"] == 0


def test_direct_journey_uses_ordered_route_stops(client, monkeypatch):
    shape = {"type": "LineString", "coordinates": [
        [67.0, 24.8599], [67.0, 24.8600], [67.0005, 24.8610],
        [67.0, 24.8620], [67.0, 24.8630],
    ]}
    rows = [
        _row(10, 1, 1, 1, "Origin stop", 24.8600, shape),
        _row(10, 1, 2, 2, "Intermediate", 24.8610, shape),
        _row(10, 1, 3, 3, "Saddar Market", 24.8620, shape),
    ]
    _install_rows(monkeypatch, rows)
    response = client.get(_journey_url())
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["journey_count"] == 1
    leg = data["journeys"][0]["legs"][0]
    assert data["journeys"][0]["type"] == "direct"
    assert leg["direction"]["id"] == 10
    assert leg["stops"][0]["name"] == "Origin stop"
    assert leg["stops"][-1]["name"] == "Saddar Market"
    assert leg["shape"]["type"] == "LineString"
    assert len(leg["shape"]["coordinates"]) == 3


def test_route_in_reverse_stop_order_is_not_a_direct_journey(client, monkeypatch):
    rows = [
        _row(10, 1, 1, 3, "Destination", 24.8620),
        _row(10, 1, 2, 2, "Middle", 24.8610),
        _row(10, 1, 3, 1, "Origin", 24.8600),
    ]
    _install_rows(monkeypatch, rows)
    response = client.get(_journey_url())
    assert response.status_code == 200
    assert response.get_json()["data"]["journeys"] == []


def test_one_transfer_uses_a_shared_stop(client, monkeypatch):
    rows = [
        _row(10, 1, 1, 1, "Origin stop", 24.8600),
        _row(10, 1, 2, 2, "Shared interchange", 24.8700),
        _row(20, 2, 1, 2, "Shared interchange", 24.8700),
        _row(20, 2, 2, 3, "Destination", 24.8800),
    ]
    _install_rows(monkeypatch, rows)
    response = client.get(_journey_url(from_lat=24.8600, to_lat=24.8800, radius=500))
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["journey_count"] == 1
    journey = data["journeys"][0]
    assert journey["type"] == "one_transfer"
    assert journey["transfer_count"] == 1
    assert journey["transfer_stop"]["id"] == 2
    assert len(journey["legs"]) == 2
