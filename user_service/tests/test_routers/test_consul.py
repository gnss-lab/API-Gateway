from fastapi.testclient import TestClient
from src.config.config import create_app

app, _, _ = create_app()
client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"message": "Service is healthy"}
