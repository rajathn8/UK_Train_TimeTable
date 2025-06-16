"""
Production-grade tests for controller logic in UK Train Timetable application.
Covers all major controller functions, error handling, and edge cases.
Follows best practices for logging, patching, and assertions.
"""

import logging
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from typing import Generator, Any

import pytest
from fastapi import status

from app.uk_train_schedule import controller
from app.uk_train_schedule.models import TimetableEntry, truncate_to_minute

logger = logging.getLogger(__name__)


@pytest.fixture
def db() -> Generator[Any, None, None]:
    """Fixture for a mock database session."""
    db = MagicMock()
    return db


def test_parse_time() -> None:
    """Test parsing of date and time strings."""
    logger.info("Testing parse_time.")
    dt = controller.parse_time("2025-06-16", "10:00")
    assert dt == datetime(2025, 6, 16, 10, 0)


def test_timetable_cache_hit_returns_none_on_exception(db: Any) -> None:
    """Test _timetable_cache_hit returns None on DB exception."""
    logger.info("Testing _timetable_cache_hit returns None on exception.")
    db.query.side_effect = Exception("fail")
    result = controller._timetable_cache_hit(
        db, "AAA", "BBB", datetime.now(), datetime.now()
    )
    assert result is None


def test_fetch_timetable_from_api_malformed(monkeypatch: Any) -> None:
    """Test _fetch_timetable_from_api raises on malformed response."""
    logger.info("Testing _fetch_timetable_from_api with malformed response.")

    class DummyResp:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict:
            return {"departures": {}}

    with patch("httpx.Client.get", return_value=DummyResp()):
        with pytest.raises(controller.TransportAPIException):
            controller._fetch_timetable_from_api("AAA", "BBB", datetime.now())


def test_store_timetable_entries_handles_no_date(db: Any) -> None:
    """Test _store_timetable_entries handles missing date field."""
    logger.info("Testing _store_timetable_entries handles no date.")
    controller._store_timetable_entries(db, {}, "AAA", "BBB")
    db.add.assert_not_called()


def test_fetch_and_store_timetable_cache_hit(db: Any) -> None:
    """Test fetch_and_store_timetable does not add if cache hit."""
    logger.info("Testing fetch_and_store_timetable cache hit.")
    with patch.object(controller, "_timetable_cache_hit", return_value=True):
        controller.fetch_and_store_timetable(
            db, "AAA", "BBB", datetime.now().isoformat(), 10
        )
    db.add.assert_not_called()


def test_find_earliest_journey_no_trains(db: Any) -> None:
    """Test find_earliest_journey raises if no trains found."""
    logger.info("Testing find_earliest_journey with no trains.")
    db.reset_mock()
    with patch(
        "app.uk_train_schedule.controller.get_timetable_entries", return_value=[]
    ):
        with patch.object(controller, "fetch_and_store_timetable"):
            with patch(
                "app.uk_train_schedule.controller.get_timetable_entries",
                return_value=[],
            ):
                with pytest.raises(controller.TransportAPIException) as exc:
                    controller.find_earliest_journey(
                        db, ["AAA", "BBB"], datetime.now().isoformat(), 10
                    )
                assert exc.value.status_code == status.HTTP_404_NOT_FOUND


def test_fetch_and_store_timetable_truncates_minute(db: Any) -> None:
    """Test fetch_and_store_timetable truncates to minute precision."""
    logger.info("Testing fetch_and_store_timetable truncates minute.")
    with patch(
        "app.uk_train_schedule.controller._timetable_cache_hit"
    ) as cache_hit, patch(
        "app.uk_train_schedule.controller._fetch_timetable_from_api"
    ) as fetch_api, patch(
        "app.uk_train_schedule.controller._store_timetable_entries"
    ) as store_entries:
        cache_hit.return_value = None
        fetch_api.return_value = {"date": "2025-06-16", "departures": {"all": []}}
        dt = datetime(2025, 6, 16, 10, 0, 42, 123456)
        controller.fetch_and_store_timetable(db, "AAA", "BBB", dt.isoformat(), 30)
        args, _ = fetch_api.call_args
        assert args[2].second == 0
        assert args[2].microsecond == 0


def test_find_earliest_journey_truncates_minute(db: Any) -> None:
    """Test find_earliest_journey truncates to minute precision."""
    logger.info("Testing find_earliest_journey truncates minute.")
    with patch(
        "app.uk_train_schedule.controller.get_timetable_entries"
    ) as get_entries, patch(
        "app.uk_train_schedule.controller.fetch_and_store_timetable"
    ) as fetch_store:
        dt = datetime(2025, 6, 16, 10, 0, 42, 123456)
        entry = TimetableEntry(
            service_id="svc1",
            station_from="AAA",
            station_to="BBB",
            aimed_departure_time=truncate_to_minute(dt),
            aimed_arrival_time=truncate_to_minute(dt + timedelta(minutes=10)),
        )
        get_entries.return_value = [entry]
        arrival = controller.find_earliest_journey(
            db, ["AAA", "BBB"], dt.isoformat(), 30
        )
        assert ":00" in arrival  # seconds are zero
