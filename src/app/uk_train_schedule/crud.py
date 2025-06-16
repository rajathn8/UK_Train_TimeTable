import logging
from datetime import datetime
from typing import List

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import TimetableEntry

logger = logging.getLogger(__name__)


def post_timetable_entry(
    db: Session,
    service_id: str,
    station_from: str,
    station_to: str,
    aimed_departure_time: datetime,
    aimed_arrival_time: datetime,
) -> TimetableEntry:
    """
    Add a new timetable entry for a train between two stations.
    Prevents duplicate entries for the same service and departure time.
    """
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
        logger.info(
            f"Added timetable entry: {service_id} - {station_from}->{station_to} |"
            f"{aimed_departure_time}|"
        )
        return entry
    except IntegrityError:
        db.rollback()
        logger.warning(
            f"Duplicate timetable entry: {service_id} - {station_from}->{station_to} |"
            f"{aimed_departure_time}|"
        )
        return db.query(TimetableEntry).filter_by(service_id=service_id).first()


def get_timetable_entries(
    db: Session, station_from: str, station_to: str, after_time: datetime
) -> List[TimetableEntry]:
    """
    Get all timetable entries for a route after a given time, ordered by departure.
    """
    logger.info(
        f"Fetching timetable entries: {station_from}->{station_to} after {after_time}"
    )
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
