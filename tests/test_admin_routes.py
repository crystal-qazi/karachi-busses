def test_admin_pages_require_login(client):
    for path in ("/admin/", "/admin/routes", "/admin/stops", "/admin/operators", "/admin/imports"):
        response = client.get(path)
        assert response.status_code == 302
        assert "/admin/login" in response.headers["Location"]


def test_login_page_loads(client):
    response = client.get("/admin/login")
    assert response.status_code == 200
    assert b"Administrator sign in" in response.data


def test_admin_map_data_requires_login(client):
    response = client.get("/api/v1/admin/routes/1/directions/1/map-data")
    assert response.status_code == 302


def test_service_worker_route_still_available(client):
    response = client.get("/service-worker.js")
    assert response.status_code == 200
    assert b"karachi-buses-shell" in response.data

def test_admin_post_requires_csrf_token(client):
    response = client.post("/admin/login", data={"username": "admin", "password": "secret"})
    assert response.status_code == 400


def test_stop_picker_asset_available(client):
    response = client.get("/static/js/stop-picker.js")
    assert response.status_code == 200
    assert b"map.on(\"click\"" in response.data


def test_historical_network_map_requires_login(client):
    response = client.get("/admin/historical-network")
    assert response.status_code == 302
    assert "/admin/login" in response.headers["Location"]


def test_historical_network_data_requires_login(client):
    response = client.get("/admin/historical-network/data")
    assert response.status_code == 302
    assert "/admin/login" in response.headers["Location"]


def test_historical_network_map_uses_official_leaflet_integrity_hashes(client):
    with client.session_transaction() as session:
        session["admin_user_id"] = 1
    response = client.get("/admin/historical-network")
    assert response.status_code == 200
    assert b'integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="' in response.data
    assert b'integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="' in response.data


def test_historical_network_data_returns_all_572_unverified_stops(client, monkeypatch):
    """The admin QA endpoint must include under-review historical stops."""
    from app.admin import routes as admin_routes

    class FakeCursor:
        def __init__(self):
            self.query = ""
            self.params = None

        def execute(self, query, params=None):
            self.query = query
            self.params = params

        def fetchone(self):
            assert "FROM data_sources" in self.query
            return {
                "id": 4,
                "source_name": "Karachi Bus Network Research Dataset (user-provided cleaned files)",
                "verification_status": "pending",
            }

        def fetchall(self):
            if "FROM bus_stops" in self.query:
                assert "WHERE source_id=%s" in self.query
                assert self.params == (4,)
                assert "status=" not in self.query.lower()
                return [
                    {
                        "id": index + 1,
                        "stop_name": f"Historical Stop {index + 1}",
                        "latitude": 24.80 + index * 0.0001,
                        "longitude": 67.00 + index * 0.0001,
                        "status": "under_review",
                    }
                    for index in range(572)
                ]
            if "FROM bus_routes" in self.query:
                return []
            if "FROM route_segments" in self.query:
                return []
            raise AssertionError(f"Unexpected query: {self.query}")

    class FakeCursorContext:
        def __enter__(self):
            return None, FakeCursor()

        def __exit__(self, exc_type, exc, traceback):
            return False

    monkeypatch.setattr(admin_routes, "cursor_context", lambda: FakeCursorContext())
    with client.session_transaction() as session:
        session["admin_user_id"] = 1

    response = client.get("/admin/historical-network/data")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["counts"]["stops"] == 572
    assert len(payload["stops"]) == 572
    assert {stop["status"] for stop in payload["stops"]} == {"under_review"}
    assert all(24.0 <= stop["lat"] <= 25.5 for stop in payload["stops"])
    assert all(66.0 <= stop["lng"] <= 68.0 for stop in payload["stops"])
