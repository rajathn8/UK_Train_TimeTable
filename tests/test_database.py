from database.session import get_db, get_engine
import logging

logger = logging.getLogger(__name__)


def test_get_engine_context():
    logger.info("Testing get_engine context manager.")
    with get_engine() as engine:
        assert engine is not None
        # Should be a SQLAlchemy engine
        assert hasattr(engine, "connect")


def test_get_db_yields_session():
    logger.info("Testing get_db yields session.")
    gen = get_db()
    db = next(gen)
    assert db is not None
    # Clean up
    try:
        next(gen)
    except StopIteration:
        pass
