from datetime import datetime
import logging

from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()

logger = logging.getLogger(__name__)


class TimetableEntry(Base):
    """
    Represents a single train journey between two stations.
    Each entry is uniquely identified by its id
    service_id can be used to distinguish
    between different trains on the same route and time.
    """

    __tablename__ = "timetable_entries"
    id = Column(Integer, primary_key=True, doc="Primary key.")
    service_id = Column(
        String,
        unique=True,
        nullable=False,
        doc="Unique identifier for the train service",
    )
    station_from = Column(String, nullable=False, doc="Departure station code")
    station_to = Column(String, nullable=False, doc="Arrival station code")
    aimed_departure_time = Column(
        DateTime, nullable=False, doc="Scheduled departure time in UTC."
    )
    aimed_arrival_time = Column(
        DateTime, nullable=False, doc="Scheduled arrival time in UTC."
    )


def create_all_tables(db_url=None):
    """Create all tables in the database if they do not exist."""
    if db_url is None:
        from app.settings import settings

        db_url = settings.db_url
    engine = create_engine(db_url)
    logger.info(f"Creating all tables in the database: {db_url}")
    Base.metadata.create_all(engine)
    logger.info("All tables created or already exist.")


def truncate_to_minute(dt: datetime) -> datetime:
    """Return a copy of dt with seconds and microseconds set to zero."""
    logger.debug(f"Truncating datetime to minute: {dt}")
    return dt.replace(second=0, microsecond=0)


"""
setting nullable=False ensures that these fields must have a value,
and unique=True on service_id ensures that no two entries can have the same service ID.
This model can be used to store and retrieve train schedules in a database.
"""
