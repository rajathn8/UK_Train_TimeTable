import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db

from .controller import TransportAPIException, find_earliest_journey
from .schema import JourneyRequest, JourneyResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/journey", tags=["journey"])


# Note: This is a POST endpoint because the request body contains a list of station codes and other parameters.
# Using POST allows us to accept complex input as JSON, which is not practical with GET query parameters.
@router.post("/", response_model=JourneyResponse, status_code=200)
def journey(req: JourneyRequest, db: Session = Depends(get_db)):
    logger.info(f"Journey endpoint called with: {req}")
    try:
        arrival = find_earliest_journey(
            db, req.station_codes, req.start_time, req.max_wait
        )
        logger.info(f"Journey found, arrival time: {arrival}")
        return JourneyResponse(arrival_time=arrival)
    except TransportAPIException as exc:
        logger.warning(f"Journey planning failed: {exc.detail}")
        raise exc
