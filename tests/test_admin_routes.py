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

def test_historical_network_screen_and_api_are_removed(client):
    for path in ("/admin/historical-network", "/admin/historical-network/data",
                 "/admin/historical-network/snap", "/admin/historical-network/route-geometry"):
        assert client.get(path).status_code == 404
    assert client.get("/static/js/historical-network-map.js").status_code == 404


def test_admin_navigation_does_not_link_historical_network(client):
    with client.session_transaction() as session:
        session["admin_user_id"] = 1
    response = client.get("/admin/")
    assert response.status_code == 200
    assert b"Historical network" not in response.data
