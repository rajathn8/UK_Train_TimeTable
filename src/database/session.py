import sqlalchemy
from sqlalchemy.orm import sessionmaker

from app.settings import settings

# Create the engine and sessionmaker once at import time (singleton pattern)
engine = sqlalchemy.create_engine(settings.db_url, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
