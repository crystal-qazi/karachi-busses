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
