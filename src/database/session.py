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
    except Exception as e:
        logger.error(f"Database engine context error: {e}")
        raise
    finally:
        engine.dispose(close=True)
        logger.info("Database engine disposed.")


def get_db():
    with get_engine() as engine:
        SessionLocal = sqlalchemy.orm.sessionmaker(
            autocommit=False, autoflush=False, bind=engine
        )
        db = SessionLocal()
        try:
            logger.info("Database session started.")
            yield db
        except Exception as e:
            logger.error(f"Database session error: {e}")
            raise
        finally:
            db.close()
            logger.info("Database session closed.")
