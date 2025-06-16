from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime

# Base class for all SQLAlchemy models
Base = declarative_base()


class TimetableEntry(Base):
    """
    Represents a single train journey between two stations.
    Stores both the scheduled (aimed) and actual times for auditing and journey planning.
    Each entry is uniquely identified by its id, but service_id can be used to distinguish
    between different trains on the same route and time.
    """

    __tablename__ = "timetable_entries"
    id = Column(Integer, primary_key=True, doc="Primary key.")
    service_id = Column(
        String,
        doc="Unique identifier for the train service (from the API, may not be unique across all time). Useful for deduplication and tracking.",
    )
    station_from = Column(
        String, doc="Departure station code (3-letter code, e.g., 'KGX')."
    )
    station_to = Column(
        String, doc="Arrival station code (3-letter code, e.g., 'EDB')."
    )
    aimed_departure_time = Column(
        DateTime, doc="Scheduled (aimed) departure time in UTC."
    )
    aimed_arrival_time = Column(DateTime, doc="Scheduled (aimed) arrival time in UTC.")
    # Optionally, you could add actual_departure_time and actual_arrival_time for real-time updates
    # actual_departure_time = Column(DateTime, nullable=True, doc="Actual departure time if available.")
    # actual_arrival_time = Column(DateTime, nullable=True, doc="Actual arrival time if available.")

    def __repr__(self):
        return (
            f"<TimetableEntry(id={self.id}, service_id={self.service_id}, "
            f"from={self.station_from}, to={self.station_to}, "
            f"aimed_departure_time={self.aimed_departure_time}, aimed_arrival_time={self.aimed_arrival_time})>"
        )
