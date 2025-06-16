import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.session import get_db

from .controller import find_earliest_journey
from .schema import JourneyRequest, JourneyResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/journey", tags=["journey"])


# Note: This is a POST endpoint because the request body contains a list of station codes and other parameters.
# Using POST allows us to accept complex input as JSON, which is not practical with GET query parameters.
@router.post("/", response_model=JourneyResponse, status_code=200)
def journey(req: JourneyRequest, db: Session = Depends(get_db)):
    logger.info(f"Journey endpoint called with: {req}")
    journey, arrival = find_earliest_journey(
        db, req.station_codes, req.start_time, req.max_wait
    )
    if not journey:
        logger.warning(f"No journey found for: {req}")
        raise HTTPException(status_code=404, detail=arrival)
    logger.info(f"Journey found: {journey}")
    return JourneyResponse(journey=journey, arrival_time=arrival)
