from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi import status

from app.uk_train_schedule import controller


@pytest.fixture
def db():
    return MagicMock()


def test_parse_time():
    dt = controller.parse_time("2025-06-16", "10:00")
    assert dt == datetime(2025, 6, 16, 10, 0)


def test_timetable_cache_hit_returns_none_on_exception(db):
    db.query.side_effect = Exception("fail")
    result = controller._timetable_cache_hit(
        db, "AAA", "BBB", datetime.now(), datetime.now()
    )
    assert result is None


def test_fetch_timetable_from_api_malformed(monkeypatch):
    class DummyResp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"departures": {}}

    with patch("httpx.Client.get", return_value=DummyResp()):
        with pytest.raises(controller.TransportAPIException):
            controller._fetch_timetable_from_api("AAA", "BBB", datetime.now())


def test_store_timetable_entries_handles_no_date(db):
    controller._store_timetable_entries(db, {}, "AAA", "BBB")
    db.add.assert_not_called()


def test_fetch_and_store_timetable_cache_hit(db):
    with patch.object(controller, "_timetable_cache_hit", return_value=True):
        controller.fetch_and_store_timetable(
            db, "AAA", "BBB", datetime.now().isoformat(), 10
        )
    db.add.assert_not_called()


def test_find_earliest_journey_no_trains(db):
    db.reset_mock()
    with patch(
        "app.uk_train_schedule.controller.get_timetable_entries", return_value=[]
    ):
        with patch.object(controller, "fetch_and_store_timetable"):
            with patch(
                "app.uk_train_schedule.controller.get_timetable_entries",
                return_value=[],
            ):
                with pytest.raises(controller.TransportAPIException) as exc:
                    controller.find_earliest_journey(
                        db, ["AAA", "BBB"], datetime.now().isoformat(), 10
                    )
                assert exc.value.status_code == status.HTTP_404_NOT_FOUND
