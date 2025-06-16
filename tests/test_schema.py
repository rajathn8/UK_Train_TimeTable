import logging
from datetime import datetime
import logging
from datetime import datetime

import pytest
from pydantic import ValidationError

from app.uk_train_schedule.schema import JourneyRequest

logger = logging.getLogger(__name__)


def test_station_codes_too_short():
    logger.info("Testing station_codes too short.")
    with pytest.raises(ValidationError) as exc:
        JourneyRequest(
            station_codes=["ABC"], start_time="2025-06-16T10:00:00", max_wait=10
        )
    assert "At least two station codes are required." in str(exc.value)


def test_station_codes_invalid_format():
    logger.info("Testing station_codes invalid format.")
    with pytest.raises(ValidationError) as exc:
        JourneyRequest(
            station_codes=["ABC", "12X"], start_time="2025-06-16T10:00:00", max_wait=10
        )
    assert "Invalid station code: 12X" in str(exc.value)


def test_start_time_invalid():
    logger.info("Testing start_time invalid.")
    with pytest.raises(ValidationError) as exc:
        JourneyRequest(
            station_codes=["ABC", "DEF"], start_time="not-a-date", max_wait=10
        )
    assert "start_time must be a valid ISO 8601 datetime string." in str(exc.value)


def test_start_time_default():
    logger.info("Testing start_time default.")
    req = JourneyRequest(station_codes=["ABC", "DEF"], max_wait=10)
    # Should default to a valid ISO string
    datetime.fromisoformat(req.start_time)


def test_max_wait_too_low():
    logger.info("Testing max_wait too low.")
    with pytest.raises(ValidationError) as exc:
        JourneyRequest(
            station_codes=["ABC", "DEF"], start_time="2025-06-16T10:00:00", max_wait=0
        )
    assert "max_wait must be between 1 and 600 minutes." in str(exc.value)


def test_max_wait_too_high():
    logger.info("Testing max_wait too high.")
    with pytest.raises(ValidationError) as exc:
        JourneyRequest(
            station_codes=["ABC", "DEF"], start_time="2025-06-16T10:00:00", max_wait=601
        )
    assert "max_wait must be between 1 and 600 minutes." in str(exc.value)


def test_valid_request():
    logger.info("Testing valid JourneyRequest.")
    req = JourneyRequest(
        station_codes=["ABC", "DEF"], start_time="2025-06-16T10:00:00", max_wait=30
    )
    assert req.station_codes == ["ABC", "DEF"]
    assert req.start_time == "2025-06-16T10:00:00"
    assert req.max_wait == 30
