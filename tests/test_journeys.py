from contextlib import contextmanager


def test_journeys_requires_origin_and_destination(client):
    response = client.get("/api/v1/journeys")
    assert response.status_code == 400


def test_journeys_rejects_invalid_origin_and_destination(client):
    response = client.get("/api/v1/journeys?origin_lat=91&origin_lng=67&destination=Saddar")
    assert response.status_code == 400
    response = client.get("/api/v1/journeys?origin_lat=24&origin_lng=67&destination=x")
    assert response.status_code == 400


def test_journeys_returns_empty_when_no_active_stops(client, monkeypatch):
    from app.api import journeys as module

    class Cursor:
        def execute(self, *_args): pass
        def fetchall(self): return []
        def close(self): pass

    class Connection:
        def cursor(self, dictionary=True): return Cursor()
        def close(self): pass

    @contextmanager
    def fake_cursor_context(**kwargs):
        yield Connection(), Cursor()

    monkeypatch.setattr(module, "cursor_context", fake_cursor_context)
    response = client.get("/api/v1/journeys?origin_lat=24.86&origin_lng=67.0&destination=Saddar")
    assert response.status_code == 200
    assert response.get_json()["data"]["journeys"] == []
