import logging
import re
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class JourneyRequest(BaseModel):
    """
    Request schema for journey planning.
    - station_codes: List of station codes (in order) for the journey.
    - start_time: ISO 8601 formatted start time (e.g., '2025-06-04T07:00:00+01:00').
    - max_wait: Maximum wait time (in minutes) allowed at any station.
    """

    station_codes: List[str] = Field(
        ..., description="List of three-letter station codes in journey order."
    )
    start_time: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Journey start time in ISO 8601 format.",
    )
    max_wait: int = Field(
        ..., description="Maximum wait time at any station in minutes."
    )

    @field_validator("station_codes")
    def validate_station_codes(v):
        logger.debug(f"Validating station_codes: {v}")
        if not v or len(v) < 2:
            raise ValueError("At least two station codes are required.")
        for code in v:
            if not re.fullmatch(r"[A-Z]{3}", code):
                raise ValueError(
                    f"Invalid station code: {code}. Must be three uppercase letters."
                )
        return v

    @field_validator("start_time")
    def validate_start_time(v):
        logger.debug(f"Validating start_time: {v}")
        if not v:
            v = datetime.now().isoformat()
        try:
            datetime.fromisoformat(v)
        except Exception:
            raise ValueError("start_time must be a valid ISO 8601 datetime string.")
        return v

    @field_validator("max_wait")
    def validate_max_wait(v):
        logger.debug(f"Validating max_wait: {v}")
        if v <= 0 or v > 600:
            raise ValueError("max_wait must be between 1 and 600 minutes.")
        return v


class JourneyResponse(BaseModel):
    """
    Response schema for journey planning.
    - arrival_time: Final arrival time at the destination station (ISO 8601 format).
    """

    arrival_time: Optional[str] = Field(
        None,
        description="Final arrival time at the destination station (ISO 8601 format).",
    )
