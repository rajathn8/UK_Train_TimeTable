"""
CRUD operations for TimetableEntry in the UK Train Timetable application.
Handles database insertions and queries for train schedules.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.uk_train_schedule.models import TimetableEntry

logger = logging.getLogger(__name__)


def post_timetable_entry(
    db: Session,
    service_id: str,
    station_from: str,
    station_to: str,
    aimed_departure_time: datetime,
    aimed_arrival_time: datetime,
) -> bool:
    """
    Add a new timetable entry for a train between two stations.
    Returns True if a new entry was added, False if duplicate.
    """
    # Ensure all datetimes are timezone-aware and in UTC
    if aimed_departure_time.tzinfo is None:
        aimed_departure_time = aimed_departure_time.replace(tzinfo=timezone.utc)
    else:
        aimed_departure_time = aimed_departure_time.astimezone(timezone.utc)
    if aimed_arrival_time.tzinfo is None:
        aimed_arrival_time = aimed_arrival_time.replace(tzinfo=timezone.utc)
    else:
        aimed_arrival_time = aimed_arrival_time.astimezone(timezone.utc)
    entry = TimetableEntry(
        service_id=service_id,
        station_from=station_from,
        station_to=station_to,
        aimed_departure_time=aimed_departure_time,
        aimed_arrival_time=aimed_arrival_time,
    )
    try:
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return True
    except IntegrityError:
        db.rollback()
        logger.warning(
            f"Duplicate timetable entry: {service_id} - {station_from}->{station_to} |"
            f"{aimed_departure_time}|"
        )
        return False


def get_earliest_timetable_entry(
    db: Session, station_from: str, station_to: str, after_time: datetime
) -> TimetableEntry | None:
    """
    Get the earliest timetable entry for a route after a given time, ordered by departure.
    Args:
        db (Session): SQLAlchemy session
        station_from (str): Departure station code
        station_to (str): Arrival station code
        after_time (datetime): Only entries after this time
    Returns:
        TimetableEntry | None: The earliest timetable entry or None if not found
    """
    # Truncate seconds and microseconds for time comparison
    if after_time.tzinfo is None:
        after_time = after_time.replace(tzinfo=timezone.utc)
    else:
        after_time = after_time.astimezone(timezone.utc)
    after_time_trunc = after_time.replace(second=0, microsecond=0)
    entry = (
        db.query(TimetableEntry)
        .filter(
            TimetableEntry.station_from == station_from,
            TimetableEntry.station_to == station_to,
            TimetableEntry.aimed_departure_time >= after_time_trunc,
        )
        .order_by(TimetableEntry.aimed_departure_time)
        .first()
    )

    if entry:
        if entry.aimed_departure_time.tzinfo is None:
            entry.aimed_departure_time = entry.aimed_departure_time.replace(
                tzinfo=timezone.utc
            )
        if entry.aimed_arrival_time.tzinfo is None:
            entry.aimed_arrival_time = entry.aimed_arrival_time.replace(
                tzinfo=timezone.utc
            )
    return entry
