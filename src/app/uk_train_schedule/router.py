from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .controller import find_earliest_journey
from .schema import JourneyRequest, JourneyResponse
from .models import Base
import sqlalchemy
import contextlib

router = APIRouter(prefix="/v1/journey", tags=["journey"])

# Dependency to get DB session
@contextlib.contextmanager
def get_engine():
    engine = sqlalchemy.create_engine("sqlite:///train_schedule.db")
    try:
        yield engine
    finally:
        engine.dispose(close=True)


def get_db():
    with get_engine() as engine:
        SessionLocal = sqlalchemy.orm.sessionmaker(
            autocommit=False, autoflush=False, bind=engine
        )
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()


@router.post("/", response_model=JourneyResponse)
def journey(req: JourneyRequest, db: Session = Depends(get_db)):
    journey, arrival = find_earliest_journey(
        db, req.station_codes, req.start_time, req.max_wait
    )
    if not journey:
        raise HTTPException(status_code=404, detail=arrival)
    return JourneyResponse(journey=journey, arrival_time=arrival)
