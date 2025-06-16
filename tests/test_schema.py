from datetime import datetime

import pytest
from pydantic import ValidationError

from app.uk_train_schedule.schema import JourneyRequest


def test_station_codes_too_short():
    with pytest.raises(ValidationError) as exc:
        JourneyRequest(
            station_codes=["ABC"], start_time="2025-06-16T10:00:00", max_wait=10
        )
    assert "At least two station codes are required." in str(exc.value)


def test_station_codes_invalid_format():
    with pytest.raises(ValidationError) as exc:
        JourneyRequest(
            station_codes=["ABC", "12X"], start_time="2025-06-16T10:00:00", max_wait=10
        )
    assert "Invalid station code: 12X" in str(exc.value)


def test_start_time_invalid():
    with pytest.raises(ValidationError) as exc:
        JourneyRequest(
            station_codes=["ABC", "DEF"], start_time="not-a-date", max_wait=10
        )
    assert "start_time must be a valid ISO 8601 datetime string." in str(exc.value)


def test_start_time_default():
    req = JourneyRequest(station_codes=["ABC", "DEF"], max_wait=10)
    # Should default to a valid ISO string
    datetime.fromisoformat(req.start_time)


def test_max_wait_too_low():
    with pytest.raises(ValidationError) as exc:
        JourneyRequest(
            station_codes=["ABC", "DEF"], start_time="2025-06-16T10:00:00", max_wait=0
        )
    assert "max_wait must be between 1 and 600 minutes." in str(exc.value)


def test_max_wait_too_high():
    with pytest.raises(ValidationError) as exc:
        JourneyRequest(
            station_codes=["ABC", "DEF"], start_time="2025-06-16T10:00:00", max_wait=601
        )
    assert "max_wait must be between 1 and 600 minutes." in str(exc.value)


def test_valid_request():
    req = JourneyRequest(
        station_codes=["ABC", "DEF"], start_time="2025-06-16T10:00:00", max_wait=30
    )
    assert req.station_codes == ["ABC", "DEF"]
    assert req.start_time == "2025-06-16T10:00:00"
    assert req.max_wait == 30
