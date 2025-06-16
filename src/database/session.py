import sqlalchemy
import contextlib
from app.settings import settings


@contextlib.contextmanager
def get_engine():
    engine = sqlalchemy.create_engine(settings.db_url)
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
