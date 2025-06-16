from datetime import datetime

from app.uk_train_schedule.models import TimetableEntry


def test_timetable_entry_instantiation():
    entry = TimetableEntry(
        service_id="svc1",
        station_from="AAA",
        station_to="BBB",
        aimed_departure_time=datetime(2025, 6, 16, 10, 0),
        aimed_arrival_time=datetime(2025, 6, 16, 11, 0),
    )
    assert entry.service_id == "svc1"
    assert entry.station_from == "AAA"
    assert entry.station_to == "BBB"
    assert entry.aimed_departure_time.hour == 10
    assert entry.aimed_arrival_time.hour == 11
