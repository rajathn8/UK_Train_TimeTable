from app.health.router import health_check
from app.health.schema import HealthResponse

def test_health_check_returns_healthresponse():
    resp = health_check()
    assert isinstance(resp, HealthResponse)
    assert resp.status == "ok"
    assert resp.api_version == "v1"
    assert resp.app_name == "UK Train Timetable"
    assert resp.description.startswith("Health check endpoint")
    assert resp.python_version
    assert resp.os
    assert resp.env
