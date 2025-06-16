from fastapi.testclient import TestClient

from app.router import app


def test_journey_endpoint_valid(monkeypatch):
    client = TestClient(app)
    # Patch controller to avoid real DB/API
    monkeypatch.setattr(
        "app.uk_train_schedule.controller.find_earliest_journey",
        lambda db, codes, start, wait: "2025-06-16T12:00:00",
    )
    payload = {
        "station_codes": ["AAA", "BBB"],
        "start_time": "2025-06-16T10:00:00",
        "max_wait": 30,
    }
    resp = client.post("/v1/journey/", json=payload)
    assert resp.status_code == 200
    assert resp.json()["arrival_time"] == "2025-06-16T12:00:00"


def test_journey_endpoint_error(monkeypatch):
    client = TestClient(app)
    from fastapi import HTTPException

    def raise_exc(*a, **kw):
        raise HTTPException(status_code=404, detail="No trains found")

    monkeypatch.setattr(
        "app.uk_train_schedule.controller.find_earliest_journey",
        raise_exc,
    )
    payload = {
        "station_codes": ["AAA", "BBB"],
        "start_time": "2025-06-16T10:00:00",
        "max_wait": 30,
    }
    resp = client.post("/v1/journey/", json=payload)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "No trains found"
