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
from app.uk_train_schedule.crud import (
    get_earliest_timetable_entry,
    post_timetable_entry,
)

logger = logging.getLogger(__name__)

TRANSPORT_API_URL = (
    "https://transportapi.com/v3/uk/train/station_timetables/{station_from}.json"
)


# Custom exception for TransportAPI errors
class TransportAPIException(HTTPException):
    """Exception for TransportAPI errors."""

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
    Uses get_earliest_timetable_entry from crud, but restricts to window_end.
    """
    try:
        # Use the CRUD function, but filter for window_end as well
        entry = get_earliest_timetable_entry(db, station_from, station_to, window_start)
        if entry:
            if window_start <= entry.aimed_departure_time < window_end:
                return entry
        return None
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
            try:
                response = client.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                # Validate response structure
                if "departures" not in data or "all" not in data.get("departures", {}):
                    logger.error(f"Malformed response from TransportAPI: {data}")
                    raise TransportAPIException(
                        detail="Malformed response from TransportAPI",
                        status_code=status.HTTP_502_BAD_GATEWAY,
                    )
                return data
            except httpx.HTTPStatusError as exc:
                # Try to extract error message from TransportAPI JSON if present
                try:
                    error_json = exc.response.json()
                    error_detail = error_json.get("error")
                    if error_detail:
                        detail = f"TransportAPI returned HTTP {exc.response.status_code}: {error_detail}"
                    else:
                        detail = f"TransportAPI returned HTTP {exc.response.status_code}: {exc.response.text}"
                except Exception:
                    detail = f"TransportAPI returned HTTP {exc.response.status_code}: {exc.response.text}"
                logger.error(detail)
                raise TransportAPIException(
                    detail=detail,
                    status_code=exc.response.status_code,
                ) from exc
    except httpx.TimeoutException as exc:
        logger.error(
            f"Timeout fetching timetable for {station_from}->{station_to} at "
            f"{window_start}: {exc}"
        )
        raise TransportAPIException(
            detail="Timeout from TransportAPI",
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        ) from exc
    except httpx.RequestError as exc:
        logger.error(
            f"Request error fetching timetable for {station_from}->{station_to} at "
            f"{window_start}: {exc}"
        )
        raise TransportAPIException(
            detail="Request error from TransportAPI",
            status_code=status.HTTP_502_BAD_GATEWAY,
        ) from exc
    except TransportAPIException:
        raise
    except Exception as exc:
        logger.error(
            f"Unexpected error fetching timetable for {station_from}->{station_to} at "
            f"{window_start}: {exc}"
        )
        raise TransportAPIException(
            detail="Unexpected error from TransportAPI",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from exc


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


def fetch_or_store_timetable(
    db: Session, station_from: str, station_to: str, starting_time: str, max_wait: int
):
    """
    Fetch and cache timetable data for a given station pair and time window.
    If a cached entry exists, return it. Otherwise, fetch from the API, store, and return the new entry.
    """
    window_start = datetime.fromisoformat(starting_time)
    window_end = window_start + timedelta(minutes=max_wait)
    cache_entry = _timetable_cache_hit(
        db, station_from, station_to, window_start, window_end
    )
    if cache_entry:
        logger.info(
            f"Cache hit for {station_from}->{station_to} in window {window_start} to {window_end}"
        )
        return cache_entry
    logger.info(
        f"Fetching timetable from API for {station_from}->{station_to} at {window_start} for window {max_wait} minutes"
    )
    data = _fetch_timetable_from_api(station_from, station_to, window_start)
    _store_timetable_entries(db, data, station_from, station_to)
    logger.info(
        f"Stored timetable entries for {station_from}->{station_to} in window {window_start} to {window_end}"
    )
    return _timetable_cache_hit(db, station_from, station_to, window_start, window_end)


def find_earliest_journey(
    db: Session, station_codes: List[str], start_time: str, max_wait: int
) -> str:
    """
    Finds the earliest valid journey for a list of station codes and a start time.
    Returns the arrival time at the final destination as an ISO8601 string.
    Raises TransportAPIException if any leg cannot be completed.
    """
    logger.info(
        f"Finding earliest journey for {station_codes} from {start_time} with max_wait {max_wait}"
    )
    current_time = datetime.fromisoformat(start_time)
    for station_from, station_to in zip(station_codes, station_codes[1:]):
        entry = fetch_or_store_timetable(
            db, station_from, station_to, current_time.isoformat(), max_wait
        )
        if not entry:
            logger.warning(
                f"No trains found for {station_from} to {station_to} after {current_time}"
            )
            raise TransportAPIException(
                detail=(
                    f"No trains found for {station_from} to {station_to} after {current_time}"
                ),
                status_code=status.HTTP_404_NOT_FOUND,
            )
        wait_time = (entry.aimed_departure_time - current_time).total_seconds() / 60
        if wait_time > max_wait:
            logger.warning(
                f"Wait time at {station_from} exceeds max_wait: {wait_time:.0f} > {max_wait}"
            )
            raise TransportAPIException(
                detail=(
                    f"Wait time at {station_from} exceeds max_wait ({wait_time:.0f} > {max_wait})"
                ),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        current_time = entry.aimed_arrival_time
    logger.info(f"Final arrival time: {current_time.isoformat()}")
    return current_time.isoformat()
