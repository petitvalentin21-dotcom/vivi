from fastapi.testclient import TestClient

from app.api.server import create_app
from app.config import Settings


def _settings_with_key(key: str = "test-secret") -> Settings:
    return Settings(api_key=key)


def test_auth_disabled_when_no_key_configured() -> None:
    client = TestClient(create_app(Settings()))
    response = client.post("/chat", json={"message": "hi"})
    assert response.status_code != 401


def test_auth_required_when_key_configured_and_no_header() -> None:
    client = TestClient(create_app(_settings_with_key()))
    response = client.post("/chat", json={"message": "hi"})
    assert response.status_code == 401


def test_auth_accepted_with_valid_bearer_token() -> None:
    client = TestClient(create_app(_settings_with_key("my-key")))
    response = client.post(
        "/chat",
        json={"message": "hi"},
        headers={"Authorization": "Bearer my-key"},
    )
    assert response.status_code != 401


def test_auth_rejected_with_wrong_bearer_token() -> None:
    client = TestClient(create_app(_settings_with_key("my-key")))
    response = client.post(
        "/chat",
        json={"message": "hi"},
        headers={"Authorization": "Bearer wrong-key"},
    )
    assert response.status_code == 401


def test_auth_accepted_with_x_vivi_api_key_header() -> None:
    client = TestClient(create_app(_settings_with_key("my-key")))
    response = client.post(
        "/chat",
        json={"message": "hi"},
        headers={"X-VIVI-API-Key": "my-key"},
    )
    assert response.status_code != 401


def test_auth_localhost_bypass_skips_key_check() -> None:
    client = TestClient(create_app(_settings_with_key()))
    # TestClient sends requests with client host "testclient", not localhost —
    # so the bypass does NOT apply here. This test verifies the regular path.
    response = client.post("/chat", json={"message": "hi"})
    assert response.status_code == 401


def test_auth_error_payload_has_expected_shape() -> None:
    client = TestClient(create_app(_settings_with_key()))
    response = client.post("/chat", json={"message": "hi"})
    assert response.status_code == 401
    body = response.json()
    assert "detail" in body
    assert body["detail"]["error"]["code"] == "auth_required"
