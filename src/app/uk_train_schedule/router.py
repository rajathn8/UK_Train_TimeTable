from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .controller import find_earliest_journey
from .schema import JourneyRequest, JourneyResponse
from database.session import get_db

router = APIRouter(prefix="/v1/journey", tags=["journey"])

# Note: This is a POST endpoint because the request body contains a list of station codes and other parameters.
# Using POST allows us to accept complex input as JSON, which is not practical with GET query parameters.
@router.post("/", response_model=JourneyResponse, status_code=200)
def journey(req: JourneyRequest, db: Session = Depends(get_db)):
    journey, arrival = find_earliest_journey(
        db, req.station_codes, req.start_time, req.max_wait
    )
    if not journey:
        raise HTTPException(status_code=404, detail=arrival)
    return JourneyResponse(journey=journey, arrival_time=arrival)
