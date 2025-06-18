import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from datetime import datetime, timezone

from app.uk_train_schedule.models import TimetableEntry


def test_timetable_entry_instantiation():
    entry = TimetableEntry(
        service_id="svc1",
        station_from="AAA",
        station_to="BBB",
        aimed_departure_time=datetime(2025, 6, 16, 10, 0, tzinfo=timezone.utc),
        aimed_arrival_time=datetime(2025, 6, 16, 11, 0, tzinfo=timezone.utc),
    )
    assert entry.service_id == "svc1"
    assert entry.station_from == "AAA"
    assert entry.station_to == "BBB"
    assert entry.aimed_departure_time.hour == 10
    assert entry.aimed_arrival_time.hour == 11
    assert entry.aimed_departure_time.second == 0
    assert entry.aimed_departure_time.microsecond == 0
    assert entry.aimed_arrival_time.second == 0
    assert entry.aimed_arrival_time.microsecond == 0
    assert entry.aimed_departure_time.tzinfo == timezone.utc
    assert entry.aimed_arrival_time.tzinfo == timezone.utc
