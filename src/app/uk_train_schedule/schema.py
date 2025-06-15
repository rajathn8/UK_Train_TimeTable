from pydantic import BaseModel
from typing import List, Optional


class JourneyRequest(BaseModel):
    station_codes: List[str]
    start_time: str  # ISO format
    max_wait: int


class JourneyLeg(BaseModel):
    from_: str
    to: str
    departure: str
    arrival: str
    service_id: str


class JourneyResponse(BaseModel):
    journey: List[dict]
    arrival_time: Optional[str]
