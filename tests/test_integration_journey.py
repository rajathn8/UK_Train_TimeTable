import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
import pytest
from fastapi.testclient import TestClient

from app.router import app


@pytest.fixture(autouse=True)
def patch_controller(monkeypatch):
    # Patch at the import location used by the FastAPI app
    import app.uk_train_schedule.router as journey_router

    monkeypatch.setattr(
        journey_router,
        "find_earliest_journey",
        lambda db, codes, start, wait: "2025-06-16T12:00:00",
    )
    yield


def test_journey_endpoint_valid():
    client = TestClient(app)
    payload = {
        "station_codes": ["AAA", "BBB"],
        "start_time": "2025-06-16T10:00:00",
        "max_wait": 30,
    }
    resp = client.post("/v1/journey/", json=payload)
    assert resp.status_code == 200
    assert resp.json()["arrival_time"] == "2025-06-16T12:00:00"


def test_journey_endpoint_error(monkeypatch):
    from fastapi import HTTPException

    import app.uk_train_schedule.router as journey_router

    def raise_exc(*a, **kw):
        raise HTTPException(status_code=404, detail="No trains found")

    monkeypatch.setattr(journey_router, "find_earliest_journey", raise_exc)
    client = TestClient(app)
    payload = {
        "station_codes": ["AAA", "BBB"],
        "start_time": "2025-06-16T10:00:00",
        "max_wait": 30,
    }
    resp = client.post("/v1/journey/", json=payload)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "No trains found"
