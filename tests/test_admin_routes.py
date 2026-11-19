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
