import httpx
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .models import TimetableEntry
from .crud import (
    get_timetable_entries,
    add_timetable_entry,
)
from typing import List, Tuple
from app.settings import settings

TRANSPORT_API_URL = (
    "https://transportapi.com/v3/uk/train/station_timetables/{station_from}.json"
)


# Helper to parse time strings
def parse_time(date_str: str, time_str: str) -> datetime:
    return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")


def fetch_and_store_timetable(
    db: Session, station_from: str, station_to: str, starting_time: str
) -> None:
    # Use a 3-hour window for caching
    start_dt = datetime.fromisoformat(starting_time)
    window_start = start_dt.replace(minute=0, second=0, microsecond=0)
    window_end = window_start + timedelta(hours=3)
    # Check if we already have timetable entries for this route and window
    existing_entries = (
        db.query(TimetableEntry)
        .filter(
            TimetableEntry.station_from == station_from,
            TimetableEntry.station_to == station_to,
            TimetableEntry.aimed_departure_time >= window_start,
            TimetableEntry.aimed_departure_time < window_end,
        )
        .first()
    )
    if existing_entries:
        return  # Data already cached for this window, skip API call
    params = dict(
        app_id=settings.app_id,
        app_key=settings.app_key,
        live=False,
        station_detail="calling_at",
        train_status="passenger",
        datetime=window_start.isoformat(),
        limit=1000,
        calling_at=station_to,
    )
    url = TRANSPORT_API_URL.format(station_from=station_from)
    with httpx.Client() as client:
        response = client.get(url, params=params)
        data = response.json()
        date = data["date"]
        for dep in data["departures"]["all"]:
            service_id = dep["service"]
            aimed_departure_time = parse_time(date, dep["aimed_departure_time"])
            for call in dep["station_detail"]["calling_at"]:
                if call["station_code"] == station_to:
                    aimed_arrival_time = parse_time(date, call["aimed_arrival_time"])
                    add_timetable_entry(
                        db,
                        service_id,
                        station_from,
                        station_to,
                        aimed_departure_time,
                        aimed_arrival_time,
                    )


# Main journey logic
def find_earliest_journey(
    db: Session, station_codes: List[str], start_time: str, max_wait: int
) -> Tuple[List[dict], str]:
    journey = []
    current_time = datetime.fromisoformat(start_time)
    for i in range(len(station_codes) - 1):
        station_from = station_codes[i]
        station_to = station_codes[i + 1]
        entries = get_timetable_entries(db, station_from, station_to, current_time)
        if not entries:
            fetch_and_store_timetable(
                db, station_from, station_to, current_time.isoformat()
            )
            entries = get_timetable_entries(db, station_from, station_to, current_time)
        if not entries:
            return (
                journey,
                f"No trains found from {station_from} to {station_to} after {current_time}",
            )
        entry = entries[0]
        wait_time = (entry.aimed_departure_time - current_time).total_seconds() / 60
        if wait_time > max_wait:
            return (
                journey,
                f"Wait time at {station_from} exceeds max_wait ({wait_time:.0f} > {max_wait})",
            )
        journey.append(
            {
                "from": station_from,
                "to": station_to,
                "departure": entry.aimed_departure_time.isoformat(),
                "arrival": entry.aimed_arrival_time.isoformat(),
                "service_id": entry.service_id,
            }
        )
        current_time = entry.aimed_arrival_time
    return journey, journey[-1]["arrival"] if journey else ""
