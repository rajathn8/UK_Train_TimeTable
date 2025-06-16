from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from fastapi import status

from app.uk_train_schedule import controller
from app.uk_train_schedule.models import TimetableEntry, truncate_to_minute


@pytest.fixture
def db():
    db = MagicMock()
    return db


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


def test_fetch_and_store_timetable_truncates_minute(db):
    with patch(
        "app.uk_train_schedule.controller._timetable_cache_hit"
    ) as cache_hit, patch(
        "app.uk_train_schedule.controller._fetch_timetable_from_api"
    ) as fetch_api, patch(
        "app.uk_train_schedule.controller._store_timetable_entries"
    ) as store_entries:
        cache_hit.return_value = None
        fetch_api.return_value = {"date": "2025-06-16", "departures": {"all": []}}
        dt = datetime(2025, 6, 16, 10, 0, 42, 123456)
        controller.fetch_and_store_timetable(db, "AAA", "BBB", dt.isoformat(), 30)
        args, _ = fetch_api.call_args
        assert args[2].second == 0
        assert args[2].microsecond == 0


def test_find_earliest_journey_truncates_minute(db):
    with patch(
        "app.uk_train_schedule.controller.get_timetable_entries"
    ) as get_entries, patch(
        "app.uk_train_schedule.controller.fetch_and_store_timetable"
    ) as fetch_store:
        dt = datetime(2025, 6, 16, 10, 0, 42, 123456)
        entry = TimetableEntry(
            service_id="svc1",
            station_from="AAA",
            station_to="BBB",
            aimed_departure_time=truncate_to_minute(dt),
            aimed_arrival_time=truncate_to_minute(dt + timedelta(minutes=10)),
        )
        get_entries.return_value = [entry]
        arrival = controller.find_earliest_journey(
            db, ["AAA", "BBB"], dt.isoformat(), 30
        )
        assert ":00" in arrival  # seconds are zero
