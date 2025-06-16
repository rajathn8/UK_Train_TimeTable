from fastapi.testclient import TestClient
from app.router import app


def test_root():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "UK Train Timetable API" in response.json()["message"]


def test_health():
    client = TestClient(app)
    response = client.get("/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["api_version"] == "v1"
    assert data["app_name"] == "UK Train Timetable"
    assert "time" in data
    assert "python_version" in data
    assert "os" in data
    assert "env" in data
    assert data["description"].startswith("Health check endpoint")
