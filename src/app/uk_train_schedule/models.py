from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

Base = declarative_base()


class Station(Base):
    __tablename__ = "stations"
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String)


class TrainService(Base):
    __tablename__ = "train_services"
    id = Column(Integer, primary_key=True)
    service_id = Column(String, unique=True, nullable=False)
    operator = Column(String)
    operator_name = Column(String)


class TimetableEntry(Base):
    __tablename__ = "timetable_entries"
    id = Column(Integer, primary_key=True)
    service_id = Column(String, ForeignKey("train_services.service_id"))
    station_from = Column(String)
    station_to = Column(String)
    aimed_departure_time = Column(DateTime)
    aimed_arrival_time = Column(DateTime)
