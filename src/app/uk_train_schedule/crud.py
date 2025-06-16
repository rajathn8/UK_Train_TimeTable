from .models import TimetableEntry
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime


def add_timetable_entry(
    db: Session,
    service_id: str,
    station_from: str,
    station_to: str,
    aimed_departure_time: datetime,
    aimed_arrival_time: datetime,
) -> TimetableEntry:
    """
    Add a new timetable entry for a train between two stations.
    """
    entry = TimetableEntry(
        service_id=service_id,
        station_from=station_from,
        station_to=station_to,
        aimed_departure_time=aimed_departure_time,
        aimed_arrival_time=aimed_arrival_time,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_timetable_entries(
    db: Session, station_from: str, station_to: str, after_time: datetime
) -> List[TimetableEntry]:
    """
    Get all timetable entries for a route after a given time, ordered by departure.
    """
    return (
        db.query(TimetableEntry)
        .filter(
            TimetableEntry.station_from == station_from,
            TimetableEntry.station_to == station_to,
            TimetableEntry.aimed_departure_time >= after_time,
        )
        .order_by(TimetableEntry.aimed_departure_time)
        .all()
    )
