from fastapi.testclient import TestClient

from app.api.server import create_app
from app.config import Settings


def test_health_returns_200() -> None:
    app = create_app(Settings())
    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 200


def test_health_service_is_vivi() -> None:
    app = create_app(Settings())
    client = TestClient(app)

    payload = client.get("/health").json()
    assert payload["service"] == "vivi"
