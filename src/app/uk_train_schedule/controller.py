"""
Controller logic for journey planning and TransportAPI integration.
Handles fetching, caching, and planning journeys using database and external API.
"""

import logging
from datetime import datetime, timedelta
from typing import List

import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.settings import settings

from .crud import get_timetable_entries, post_timetable_entry
from .models import TimetableEntry, truncate_to_minute

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

TRANSPORT_API_URL = (
    "https://transportapi.com/v3/uk/train/station_timetables/{station_from}.json"
)


# Custom exception for TransportAPI errors
class TransportAPIException(HTTPException):
    """
    Custom exception for TransportAPI failures with HTTP status code.
    Args:
        detail (str): Error detail message
        status_code (int): HTTP status code (default: 502)
    """

    def __init__(self, detail: str, status_code: int = status.HTTP_502_BAD_GATEWAY):
        super().__init__(status_code=status_code, detail=detail)


# Helper to parse time strings
def parse_time(date_str: str, time_str: str) -> datetime:
    """
    Parse date and time strings into a datetime object.
    Args:
        date_str (str): Date string (YYYY-MM-DD)
        time_str (str): Time string (HH:MM)
    Returns:
        datetime: Combined datetime object
    """
    return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")


def _timetable_cache_hit(
    db: Session,
    station_from: str,
    station_to: str,
    window_start: datetime,
    window_end: datetime,
):
    """
    Returns the first matching TimetableEntry if found, otherwise None.
    Args:
        db (Session): SQLAlchemy session
        station_from (str): Departure station code
        station_to (str): Arrival station code
        window_start (datetime): Start of time window
        window_end (datetime): End of time window
    Returns:
        TimetableEntry or None
    """
    try:
        return (
            db.query(TimetableEntry)
            .filter(
                TimetableEntry.station_from == station_from,
                TimetableEntry.station_to == station_to,
                TimetableEntry.aimed_departure_time >= window_start,
                TimetableEntry.aimed_departure_time < window_end,
            )
            .order_by(TimetableEntry.aimed_departure_time.asc())
            .first()
        )
    except Exception as exc:
        logger.error(
            f"Database error during cache check for {station_from}->{station_to} in "
            f"window {window_start} to {window_end}: {exc}"
        )
        return None


def _fetch_timetable_from_api(
    station_from: str, station_to: str, window_start: datetime
) -> dict:
    """
    Fetch timetable data from TransportAPI for the given window.
    Args:
        station_from (str): Departure station code
        station_to (str): Arrival station code
        window_start (datetime): Start of time window (UTC)
    Returns:
        dict: API response data
    Raises:
        TransportAPIException: If the API call fails or returns an error status.
    """
    from datetime import timezone

    if window_start.tzinfo is None:
        window_start_utc = window_start.replace(tzinfo=timezone.utc)
    else:
        window_start_utc = window_start.astimezone(timezone.utc)
    datetime_str = window_start_utc.strftime("%Y-%m-%dT%H:%M:00Z")
    params = {
        "app_id": settings.app_id,
        "app_key": settings.app_key,
        "live": False,
        "station_detail": "calling_at",
        "train_status": "passenger",
        "datetime": datetime_str,
        "limit": 1000,
        "calling_at": station_to,
    }
    url = TRANSPORT_API_URL.format(station_from=station_from)
    try:
        with httpx.Client() as client:
            response = client.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            # Validate response structure
            if "departures" not in data or "all" not in data.get("departures", {}):
                logger.error(f"Malformed response from TransportAPI: {data}")
                raise TransportAPIException("Malformed response from TransportAPI")
            return data
    except httpx.TimeoutException as exc:
        logger.error(
            f"Timeout fetching timetable for {station_from}->{station_to} at "
            f"{window_start}: {exc}"
        )
        raise TransportAPIException("Timeout from TransportAPI") from exc
    except httpx.RequestError as exc:
        logger.error(
            f"Request error fetching timetable for {station_from}->{station_to} at "
            f"{window_start}: {exc}"
        )
        raise TransportAPIException("Request error from TransportAPI") from exc
    except httpx.HTTPStatusError as exc:
        logger.error(
            f"HTTP error fetching timetable for {station_from}->{station_to} at "
            f"{window_start}: {exc}"
        )
        raise TransportAPIException("HTTP Error from TransportAPI") from exc
    except Exception as exc:
        logger.error(
            f"Unexpected error fetching timetable for {station_from}->{station_to} at "
            f"{window_start}: {exc}"
        )
        raise TransportAPIException("Unexpected error from TransportAPI") from exc


def _store_timetable_entries(
    db: Session, data: dict, station_from: str, station_to: str
) -> None:
    """
    Store timetable entries from API data into the database.
    Logs errors and skips malformed entries, but continues processing others.
    Args:
        db (Session): SQLAlchemy session
        data (dict): API response data
        station_from (str): Departure station code
        station_to (str): Arrival station code
    """
    stored_count = 0
    try:
        date = data.get("date")
        if not date:
            logger.error("No 'date' in API response.")
            return
        departures = data.get("departures", {}).get("all", [])
        for dep in departures:
            try:
                service_id = dep.get("service")
                aimed_departure_time = parse_time(date, dep.get("aimed_departure_time"))
                for call in dep.get("station_detail", {}).get("calling_at", []):
                    if call.get("station_code") == station_to:
                        aimed_arrival_time = parse_time(
                            date, call.get("aimed_arrival_time")
                        )
                        post_timetable_entry(
                            db,
                            service_id,
                            station_from,
                            station_to,
                            aimed_departure_time,
                            aimed_arrival_time,
                        )
                        stored_count += 1
            except Exception as entry_exc:
                logger.error(
                    f"Error storing entry for service_id={dep.get('service')}: "
                    f"{entry_exc}"
                )
        logger.info(
            f"Stored {stored_count} timetable entries for "
            f"{station_from}->{station_to}"
        )
    except Exception as exception:
        logger.error(
            f"Error processing timetable entries for {station_from}->{station_to}: "
            f"{exception}"
        )


def fetch_and_store_timetable(
    db: Session, station_from: str, station_to: str, starting_time: str, max_wait: int
) -> None:
    """
    Fetch and cache timetable data for a given station pair and time window.
    If a cached entry exists, do nothing. Otherwise, fetch from the API and store new entries.
    Args:
        db (Session): SQLAlchemy session
        station_from (str): Departure station code
        station_to (str): Arrival station code
        starting_time (str): Start time in ISO 8601
        max_wait (int): Maximum wait time in minutes
    Raises:
        TransportAPIException: If the API call fails or returns an error status.
    """
    try:
        window_start = truncate_to_minute(datetime.fromisoformat(starting_time))
        window_end = window_start + timedelta(minutes=max_wait)
        cache_entry = _timetable_cache_hit(
            db, station_from, station_to, window_start, window_end
        )
        if cache_entry:
            logger.info(
                f"Cache hit for {station_from}->{station_to} in window "
                f"{window_start} to {window_end}"
            )
            return

        logger.info(
            f"Fetching timetable from API for {station_from}->{station_to} at "
            f"{window_start} for window {max_wait} minutes"
        )
        data = _fetch_timetable_from_api(station_from, station_to, window_start)
        _store_timetable_entries(db, data, station_from, station_to)
        logger.info(
            f"Stored timetable entries for {station_from}->{station_to} in window "
            f"{window_start} to {window_end}"
        )
    except TransportAPIException as api_exc:
        logger.error(f"TransportAPIException: {api_exc}")
        raise
    except Exception as exc:
        logger.error(f"Unexpected error for {station_from}->{station_to}: {exc}")
        return


def find_earliest_journey(
    db: Session, station_codes: List[str], start_time: str, max_wait: int
) -> str:
    """
    Finds the earliest valid journey for a list of station codes and a start time.
    Returns the arrival time at the final destination as an ISO8601 string.
    Raises TransportAPIException if any leg cannot be completed.
    Args:
        db (Session): SQLAlchemy session
        station_codes (List[str]): List of station codes in journey order
        start_time (str): Start time in ISO 8601
        max_wait (int): Maximum wait time in minutes
    Returns:
        str: Arrival time at destination (ISO 8601)
    """
    logger.info(
        f"Finding earliest journey for {station_codes} from {start_time} with "
        f"max_wait {max_wait}"
    )
    current_time = truncate_to_minute(datetime.fromisoformat(start_time))
    for station_from, station_to in zip(station_codes, station_codes[1:]):
        entries = get_timetable_entries(db, station_from, station_to, current_time)
        if not entries:
            fetch_and_store_timetable(
                db, station_from, station_to, current_time.isoformat(), max_wait
            )
            entries = get_timetable_entries(db, station_from, station_to, current_time)
        if not entries:
            logger.warning(
                f"No trains found from {station_from} to {station_to} after "
                f"{current_time}"
            )
            raise TransportAPIException(
                detail=(
                    f"No trains found from {station_from} to {station_to} after "
                    f"{current_time}"
                ),
                status_code=status.HTTP_404_NOT_FOUND,
            )
        entry = entries[0]
        wait_time = (entry.aimed_departure_time - current_time).total_seconds() / 60
        if wait_time > max_wait:
            logger.warning(
                f"Wait time at {station_from} exceeds max_wait: "
                f"{wait_time:.0f} > {max_wait}"
            )
            raise TransportAPIException(
                detail=(
                    f"Wait time at {station_from} exceeds max_wait "
                    f"({wait_time:.0f} > {max_wait})"
                ),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        current_time = entry.aimed_arrival_time
    logger.info(f"Final arrival time: {current_time.isoformat()}")
    return current_time.isoformat()
