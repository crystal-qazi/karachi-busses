def test_health_without_database_check(client):
    response = client.get("/api/v1/health?check_db=false")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["data"]["application"] == "healthy"
    assert payload["data"]["database"] == "not_checked"


def test_health_database_success(client, monkeypatch):
    class FakeCursor:
        def execute(self, _query):
            pass
        def fetchone(self):
            return (1,)
        def close(self):
            pass

    class FakeConnection:
        def cursor(self):
            return FakeCursor()
        def close(self):
            pass

    monkeypatch.setattr("app.api.health.get_db_connection", lambda: FakeConnection())
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.get_json()["data"]["database"] == "healthy"


def test_health_database_failure(client, monkeypatch):
    def fail_connection():
        raise RuntimeError("database unavailable")

    monkeypatch.setattr("app.api.health.get_db_connection", fail_connection)
    response = client.get("/api/v1/health")
    assert response.status_code == 503
    assert response.get_json()["error"]["code"] == "DATABASE_UNAVAILABLE"


def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Karachi Buses" in response.data
    assert b"openstreetmap" in response.data.lower()
