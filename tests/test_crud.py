from datetime import datetime, timezone
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
        aimed_departure_time=datetime(2025, 6, 16, 10, 0, tzinfo=timezone.utc),
        aimed_arrival_time=datetime(2025, 6, 16, 11, 0, tzinfo=timezone.utc),
    )
    return db


def test_post_timetable_entry_new(db):
    db.query().filter_by().first.return_value = None
    db.add.side_effect = None
    dt_dep = datetime(2025, 6, 16, 10, 0, 42, 123456, tzinfo=timezone.utc)
    dt_arr = datetime(2025, 6, 16, 11, 0, 59, 999999, tzinfo=timezone.utc)
    assert crud.post_timetable_entry(db, "svc1", "AAA", "BBB", dt_dep, dt_arr)
    db.add.assert_called()
    db.commit.assert_called()


def test_post_timetable_entry_duplicate(db):
    db.add.side_effect = IntegrityError("mock", "mock", "mock")
    db.commit.side_effect = IntegrityError("mock", "mock", "mock")
    db.query().filter_by().first.return_value = TimetableEntry(
        service_id="svc1",
        station_from="AAA",
        station_to="BBB",
        aimed_departure_time=datetime(2025, 6, 16, 10, 0, tzinfo=timezone.utc),
        aimed_arrival_time=datetime(2025, 6, 16, 11, 0, tzinfo=timezone.utc),
    )
    dt_dep = datetime(2025, 6, 16, 10, 0, 42, 123456, tzinfo=timezone.utc)
    dt_arr = datetime(2025, 6, 16, 11, 0, 59, 999999, tzinfo=timezone.utc)
    assert not crud.post_timetable_entry(db, "svc1", "AAA", "BBB", dt_dep, dt_arr)
    db.rollback.assert_called()


def test_get_timetable_entries(db):
    db.query().filter().order_by().first.return_value = TimetableEntry(
        service_id="svc1",
        station_from="AAA",
        station_to="BBB",
        aimed_departure_time=datetime(2025, 6, 16, 10, 0, tzinfo=timezone.utc),
        aimed_arrival_time=datetime(2025, 6, 16, 11, 0, tzinfo=timezone.utc),
    )
    dt = datetime(2025, 6, 16, 10, 0, 42, 123456, tzinfo=timezone.utc)
    entry = crud.get_earliest_timetable_entry(db, "AAA", "BBB", dt)
    assert (
        entry
        and entry.aimed_departure_time.tzinfo == timezone.utc
        and entry.aimed_arrival_time.tzinfo == timezone.utc
    )
    assert (
        entry.aimed_departure_time.second == 0
        and entry.aimed_departure_time.microsecond == 0
    )
    assert (
        entry.aimed_arrival_time.second == 0
        and entry.aimed_arrival_time.microsecond == 0
    )
    db.query().filter().order_by().first.return_value = None
    assert crud.get_earliest_timetable_entry(db, "AAA", "BBB", dt) is None
