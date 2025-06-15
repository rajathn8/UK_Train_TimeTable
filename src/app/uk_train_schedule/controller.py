import httpx
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .crud import get_timetable_entries, add_timetable_entry, add_train_service, add_station
from .models import TimetableEntry
from typing import List, Tuple
import os

TRANSPORT_API_URL = "https://transportapi.com/v3/uk/train/station_timetables/{station_from}.json"

# Helper to parse time strings

def parse_time(date_str: str, time_str: str) -> datetime:
    return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

def fetch_and_store_timetable(db: Session, station_from: str, station_to: str, starting_time: str) -> None:
    params = dict(
        app_id=os.getenv("app_id"),
        app_key=os.getenv("app_key"),
        live=False,
        station_detail="calling_at",
        train_status="passenger",
        datetime=starting_time,
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
            operator = dep.get("operator", "")
            operator_name = dep.get("operator_name", "")
            add_train_service(db, service_id, operator, operator_name)
            aimed_departure_time = parse_time(date, dep["aimed_departure_time"])
            for call in dep["station_detail"]["calling_at"]:
                if call["station_code"] == station_to:
                    aimed_arrival_time = parse_time(date, call["aimed_arrival_time"])
                    add_timetable_entry(db, service_id, station_from, station_to, aimed_departure_time, aimed_arrival_time)

# Main journey logic
def find_earliest_journey(db: Session, station_codes: List[str], start_time: str, max_wait: int) -> Tuple[List[dict], str]:
    journey = []
    current_time = datetime.fromisoformat(start_time)
    for i in range(len(station_codes) - 1):
        station_from = station_codes[i]
        station_to = station_codes[i+1]
        entries = get_timetable_entries(db, station_from, station_to, current_time)
        if not entries:
            fetch_and_store_timetable(db, station_from, station_to, current_time.isoformat())
            entries = get_timetable_entries(db, station_from, station_to, current_time)
        if not entries:
            return journey, f"No trains found from {station_from} to {station_to} after {current_time}"
        entry = entries[0]
        wait_time = (entry.aimed_departure_time - current_time).total_seconds() / 60
        if wait_time > max_wait:
            return journey, f"Wait time at {station_from} exceeds max_wait ({wait_time:.0f} > {max_wait})"
        journey.append({
            "from": station_from,
            "to": station_to,
            "departure": entry.aimed_departure_time.isoformat(),
            "arrival": entry.aimed_arrival_time.isoformat(),
            "service_id": entry.service_id
        })
        current_time = entry.aimed_arrival_time
    return journey, journey[-1]["arrival"] if journey else ""
