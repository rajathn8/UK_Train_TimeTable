import pytest
from unittest.mock import MagicMock
from datetime import datetime
from app.uk_train_schedule import crud
from app.uk_train_schedule.models import TimetableEntry

@pytest.fixture
def db():
    db = MagicMock()
    db.query().filter_by().first.return_value = TimetableEntry(
        service_id="svc1", station_from="AAA", station_to="BBB",
        aimed_departure_time=datetime.now(), aimed_arrival_time=datetime.now()
    )
    return db

def test_post_timetable_entry_new(db):
    db.query().filter_by().first.return_value = None
    db.add.side_effect = None
    entry = crud.post_timetable_entry(
        db, "svc1", "AAA", "BBB", datetime.now(), datetime.now()
    )
    db.add.assert_called()
    db.commit.assert_called()
    assert entry is not None

def test_post_timetable_entry_duplicate(db):
    db.add.side_effect = Exception("IntegrityError")
    db.commit.side_effect = Exception("IntegrityError")
    db.query().filter_by().first.return_value = TimetableEntry(
        service_id="svc1", station_from="AAA", station_to="BBB",
        aimed_departure_time=datetime.now(), aimed_arrival_time=datetime.now()
    )
    entry = crud.post_timetable_entry(
        db, "svc1", "AAA", "BBB", datetime.now(), datetime.now()
    )
    db.rollback.assert_called()
    assert entry is not None

def test_get_timetable_entries(db):
    db.query().filter().order_by().all.return_value = [
        TimetableEntry(service_id="svc1", station_from="AAA", station_to="BBB",
                       aimed_departure_time=datetime.now(), aimed_arrival_time=datetime.now())
    ]
    entries = crud.get_timetable_entries(db, "AAA", "BBB", datetime.now())
    assert len(entries) == 1
