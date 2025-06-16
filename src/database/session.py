import contextlib
import logging

import sqlalchemy

from app.settings import settings

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def get_engine():
    engine = sqlalchemy.create_engine(settings.db_url)
    logger.info(f"Database engine created for {settings.db_url}")
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
            logger.debug("Database session closed.")
