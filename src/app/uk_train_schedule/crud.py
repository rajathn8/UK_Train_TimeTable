from .models import Station, TrainService, TimetableEntry
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime


def get_station_by_code(db: Session, code: str) -> Optional[Station]:
    return db.query(Station).filter(Station.code == code).first()


def add_station(db: Session, code: str, name: str) -> Station:
    station = Station(code=code, name=name)
    db.add(station)
    db.commit()
    db.refresh(station)
    return station


def add_train_service(
    db: Session, service_id: str, operator: str, operator_name: str
) -> TrainService:
    service = TrainService(
        service_id=service_id, operator=operator, operator_name=operator_name
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


def add_timetable_entry(
    db: Session,
    service_id: str,
    station_from: str,
    station_to: str,
    aimed_departure_time: datetime,
    aimed_arrival_time: datetime,
) -> TimetableEntry:
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
