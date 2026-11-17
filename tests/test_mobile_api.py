from unittest.mock import patch

from app import create_app


def client():
    app = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False})
    return app.test_client()


def test_mobile_manifest_is_content_addressed():
    snapshot = {"routes": [], "directions": [], "stops": [], "direction_stops": [], "shapes": []}
    with patch("app.api.mobile._published_snapshot", return_value=snapshot):
        response = client().get("/api/v1/mobile/manifest")
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["schema_version"] == 1
    assert data["sync_mode"] == "full_snapshot"
    assert data["incremental_sync_available"] is False
    assert data["checksum"] == "sha256:" + data["dataset_version"]
    assert response.headers["ETag"] == '"' + data["dataset_version"] + '"'
    from datetime import datetime
    generated_at = datetime.fromisoformat(data["generated_at"].replace("Z", "+00:00"))
    assert generated_at.utcoffset() is not None


def test_mobile_snapshot_contains_same_version_and_data():
    snapshot = {"routes": [{"id": 9}], "directions": [], "stops": [], "direction_stops": [], "shapes": []}
    with patch("app.api.mobile._published_snapshot", return_value=snapshot):
        response = client().get("/api/v1/mobile/snapshot")
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["dataset"] == snapshot
    assert data["dataset_version"] == data["checksum"].removeprefix("sha256:")


def test_mobile_api_hides_database_error_details():
    with patch("app.api.mobile._published_snapshot", side_effect=RuntimeError("secret database detail")):
        response = client().get("/api/v1/mobile/manifest")
    assert response.status_code == 503
    assert "secret database detail" not in response.get_data(as_text=True)
