from fastapi.testclient import TestClient

from app.api.server import create_app
from app.config import Settings


if __name__ == "__main__":
    app = create_app(Settings())
    client = TestClient(app)
    for endpoint in ("/health", "/runtime/info"):
        response = client.get(endpoint)
        print(endpoint, response.status_code)
        print(response.json())
