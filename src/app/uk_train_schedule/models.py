from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime

Base = declarative_base()


class TimetableEntry(Base):
    """
    Represents a single train journey between two stations.
    Each entry is uniquely identified by its id
    service_id can be used to distinguish
    between different trains on the same route and time.
    """

    __tablename__ = "timetable_entries"
    id = Column(Integer, primary_key=True, doc="Primary key.")
    service_id = Column(String, doc="Unique identifier for the train service")
    station_from = Column(String, doc="Departure station code")
    station_to = Column(String, doc="Arrival station code")
    aimed_departure_time = Column(DateTime, doc="Scheduled departure time in UTC.")
    aimed_arrival_time = Column(DateTime, doc="Scheduled arrival time in UTC.")
