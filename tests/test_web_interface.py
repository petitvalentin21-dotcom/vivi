from fastapi.testclient import TestClient

from app.api.server import create_app
from app.config import Settings


def test_root_serves_web_interface() -> None:
    client = TestClient(create_app(Settings()))
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "VIVI" in response.text


def test_web_static_assets_are_accessible() -> None:
    client = TestClient(create_app(Settings()))

    css = client.get("/web/style.css")
    js = client.get("/web/app.js")

    assert css.status_code == 200
    assert js.status_code == 200
