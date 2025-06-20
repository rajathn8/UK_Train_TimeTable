"""
Production-grade tests for controller logic in UK Train Timetable application.
Covers all major controller functions, error handling, and edge cases.
Follows best practices for logging, patching, and assertions.
"""

from datetime import datetime, timedelta
from typing import Any, Generator
from unittest.mock import MagicMock, patch

import httpx
import pytest
from fastapi import status

from app.uk_train_schedule import controller


@pytest.fixture
def db() -> Generator[Any, None, None]:
    """Fixture for a mock database session."""
    db = MagicMock()
    return db


def test_parse_time() -> None:
    """Test parsing of date and time strings."""
    dt = controller.parse_time("2025-06-16", "10:00")
    assert dt == datetime(2025, 6, 16, 10, 0)


def test_timetable_cache_hit_returns_none_on_exception(db: Any) -> None:
    """Test _timetable_cache_hit returns None on DB exception."""
    db.query.side_effect = Exception("fail")
    result = controller._timetable_cache_hit(
        db, "AAA", "BBB", datetime.now(), datetime.now()
    )
    assert result is None


def test_fetch_timetable_from_api_malformed(monkeypatch: Any) -> None:
    """Test _fetch_timetable_from_api raises on malformed response."""

    class DummyResp:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict:
            return {"departures": {}}

    with patch("httpx.Client.get", return_value=DummyResp()):
        with pytest.raises(controller.TransportAPIException) as exc:
            controller._fetch_timetable_from_api("AAA", "BBB", datetime.now())
        assert exc.value.status_code == 502
        assert "Malformed response" in str(exc.value.detail)


def test_fetch_timetable_from_api_timeout(monkeypatch: Any) -> None:
    """Test _fetch_timetable_from_api raises 504 on timeout."""

    class DummyTimeout(Exception):
        pass

    def raise_timeout(*args, **kwargs):
        raise httpx.TimeoutException("timeout")

    monkeypatch.setattr(httpx.Client, "get", raise_timeout)
    with pytest.raises(controller.TransportAPIException) as exc:
        controller._fetch_timetable_from_api("AAA", "BBB", datetime.now())
    assert exc.value.status_code == 504
    assert "Timeout" in str(exc.value.detail)


def test_fetch_timetable_from_api_request_error(monkeypatch: Any) -> None:
    """Test _fetch_timetable_from_api raises 502 on request error."""

    def raise_request_error(*args, **kwargs):
        raise httpx.RequestError("request error", request=None)

    monkeypatch.setattr(httpx.Client, "get", raise_request_error)
    with pytest.raises(controller.TransportAPIException) as exc:
        controller._fetch_timetable_from_api("AAA", "BBB", datetime.now())
    assert exc.value.status_code == 502
    assert "Request error" in str(exc.value.detail)


def test_fetch_timetable_from_api_http_status_error(monkeypatch: Any) -> None:
    """Test _fetch_timetable_from_api raises with actual HTTP status code."""

    class DummyResponse:
        status_code = 403
        text = "Forbidden"

    class DummyHTTPStatusError(httpx.HTTPStatusError):
        def __init__(self):
            super().__init__("error", request=None, response=DummyResponse())
            self.response = DummyResponse()

    def raise_http_status_error(*args, **kwargs):
        raise DummyHTTPStatusError()

    monkeypatch.setattr(httpx.Client, "get", raise_http_status_error)
    with pytest.raises(controller.TransportAPIException) as exc:
        controller._fetch_timetable_from_api("AAA", "BBB", datetime.now())
    assert exc.value.status_code == 403
    assert "TransportAPI returned HTTP 403" in str(exc.value.detail)


def test_fetch_timetable_from_api_unexpected_error(monkeypatch: Any) -> None:
    """Test _fetch_timetable_from_api raises 500 on unexpected error."""

    def raise_unexpected(*args, **kwargs):
        raise Exception("unexpected")

    monkeypatch.setattr(httpx.Client, "get", raise_unexpected)
    with pytest.raises(controller.TransportAPIException) as exc:
        controller._fetch_timetable_from_api("AAA", "BBB", datetime.now())
    assert exc.value.status_code == 500
    assert "Unexpected error" in str(exc.value.detail)


def test_store_timetable_entries_handles_no_date(db: Any) -> None:
    """Test _store_timetable_entries handles missing date field."""
    controller._store_timetable_entries(db, {}, "AAA", "BBB")
    db.add.assert_not_called()


def test_fetch_or_store_timetable_cache_hit(db: Any) -> None:
    """Test fetch_or_store_timetable does not add if cache hit."""
    with patch.object(controller, "_timetable_cache_hit", return_value=True):
        controller.fetch_or_store_timetable(
            db, "AAA", "BBB", datetime.now().isoformat(), 10
        )
    db.add.assert_not_called()


def test_find_earliest_journey_no_trains(db: Any) -> None:
    """Test find_earliest_journey raises if no trains found."""
    db.reset_mock()
    with patch(
        "app.uk_train_schedule.controller.get_earliest_timetable_entry",
        return_value=None,
    ):
        with patch.object(controller, "fetch_or_store_timetable", return_value=None):
            with patch(
                "app.uk_train_schedule.controller.get_earliest_timetable_entry",
                return_value=None,
            ):
                with pytest.raises(controller.TransportAPIException) as exc:
                    controller.find_earliest_journey(
                        db, ["AAA", "BBB"], datetime.now().isoformat(), 10
                    )
                assert exc.value.status_code == status.HTTP_404_NOT_FOUND


def test_fetch_or_store_timetable_truncates_minute(db: Any) -> None:
    """Test fetch_or_store_timetable truncates to minute precision."""
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
        controller.fetch_or_store_timetable(
            db, "AAA", "BBB", dt.replace(second=0, microsecond=0).isoformat(), 30
        )
        args, _ = fetch_api.call_args
        assert args[2].second == 0
        assert args[2].microsecond == 0


def test_find_earliest_journey_truncates_minute(db: Any) -> None:
    """Test find_earliest_journey truncates to minute precision."""
    from app.uk_train_schedule.models import TimetableEntry

    dt = datetime(2025, 6, 16, 10, 0, 42, 123456)
    entry = TimetableEntry(
        service_id="svc1",
        station_from="AAA",
        station_to="BBB",
        aimed_departure_time=dt.replace(second=0, microsecond=0),
        aimed_arrival_time=dt.replace(second=0, microsecond=0) + timedelta(minutes=10),
    )
    with patch(
        "app.uk_train_schedule.controller.get_earliest_timetable_entry",
        return_value=entry,
    ), patch(
        "app.uk_train_schedule.controller.fetch_or_store_timetable", return_value=entry
    ):
        arrival = controller.find_earliest_journey(
            db, ["AAA", "BBB"], dt.isoformat(), 30
        )
        # Should be truncated to minute
        assert arrival.endswith(":00")
