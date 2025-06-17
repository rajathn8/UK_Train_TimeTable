"""
Journey planning API router for UK Train Timetable.
Defines endpoints for journey planning and integrates with controller logic.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db

from .controller import TransportAPIException, find_earliest_journey
from .schema import JourneyRequest, JourneyResponse

router = APIRouter(prefix="/v1/journey", tags=["journey"])


# Note: This is a POST endpoint because the request body contains a list of station
# codes and other parameters.
# Using POST allows us to accept complex input as JSON, which is not practical with GET
# query parameters.
@router.post(
    "/",
    response_model=JourneyResponse,
    status_code=200,
    summary="Plan a journey",
    description="""
    Plan a journey using a list of station codes, start time, and max wait.
    Returns the earliest possible arrival time at the destination.
    """,
)
def journey(req: JourneyRequest, db: Session = Depends(get_db)):
    """
    Plan a journey using the provided station codes, start time, and max wait.
    Args:
        req (JourneyRequest): Journey planning request
        db (Session): SQLAlchemy session (dependency)
    Returns:
        JourneyResponse: Arrival time at destination
    Raises:
        TransportAPIException: If journey planning fails
    """
    try:
        arrival = find_earliest_journey(
            db, req.station_codes, req.start_time, req.max_wait
        )
        return JourneyResponse(arrival_time=arrival)
    except TransportAPIException as exc:
        raise exc
