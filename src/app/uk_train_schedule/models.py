from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime

Base = declarative_base()


class TimetableEntry(Base):
    __tablename__ = "timetable_entries"
    id = Column(Integer, primary_key=True)
    service_id = Column(String)
    station_from = Column(String)
    station_to = Column(String)
    aimed_departure_time = Column(DateTime)
    aimed_arrival_time = Column(DateTime)
