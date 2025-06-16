from datetime import datetime
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.uk_train_schedule import crud
from app.uk_train_schedule.models import TimetableEntry


@pytest.fixture
def db():
    db = MagicMock()
    db.query().filter_by().first.return_value = TimetableEntry(
        service_id="svc1",
        station_from="AAA",
        station_to="BBB",
        aimed_departure_time=datetime(2025, 6, 16, 10, 0),
        aimed_arrival_time=datetime(2025, 6, 16, 11, 0),
    )
    return db


def test_post_timetable_entry_new(db):
    db.query().filter_by().first.return_value = None
    db.add.side_effect = None
    dt_dep = datetime(2025, 6, 16, 10, 0, 42, 123456)
    dt_arr = datetime(2025, 6, 16, 11, 0, 59, 999999)
    entry = crud.post_timetable_entry(db, "svc1", "AAA", "BBB", dt_dep, dt_arr)
    db.add.assert_called()
    db.commit.assert_called()
    assert entry is not None
    assert entry.aimed_departure_time.second == 0
    assert entry.aimed_departure_time.microsecond == 0
    assert entry.aimed_arrival_time.second == 0
    assert entry.aimed_arrival_time.microsecond == 0


def test_post_timetable_entry_duplicate(db):
    db.add.side_effect = IntegrityError("mock", "mock", "mock")
    db.commit.side_effect = IntegrityError("mock", "mock", "mock")
    db.query().filter_by().first.return_value = TimetableEntry(
        service_id="svc1",
        station_from="AAA",
        station_to="BBB",
        aimed_departure_time=datetime(2025, 6, 16, 10, 0),
        aimed_arrival_time=datetime(2025, 6, 16, 11, 0),
    )
    dt_dep = datetime(2025, 6, 16, 10, 0, 42, 123456)
    dt_arr = datetime(2025, 6, 16, 11, 0, 59, 999999)
    entry = crud.post_timetable_entry(db, "svc1", "AAA", "BBB", dt_dep, dt_arr)
    db.rollback.assert_called()
    assert entry is not None
    assert entry.aimed_departure_time.second == 0
    assert entry.aimed_departure_time.microsecond == 0
    assert entry.aimed_arrival_time.second == 0
    assert entry.aimed_arrival_time.microsecond == 0


def test_get_timetable_entries(db):
    db.query().filter().order_by().all.return_value = [
        TimetableEntry(
            service_id="svc1",
            station_from="AAA",
            station_to="BBB",
            aimed_departure_time=datetime(2025, 6, 16, 10, 0),
            aimed_arrival_time=datetime(2025, 6, 16, 11, 0),
        )
    ]
    dt = datetime(2025, 6, 16, 10, 0, 42, 123456)
    entries = crud.get_timetable_entries(db, "AAA", "BBB", dt)
    assert len(entries) == 1
    for entry in entries:
        assert entry.aimed_departure_time.second == 0
        assert entry.aimed_departure_time.microsecond == 0
        assert entry.aimed_arrival_time.second == 0
        assert entry.aimed_arrival_time.microsecond == 0
