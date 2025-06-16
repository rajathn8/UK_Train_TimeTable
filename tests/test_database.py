from database.session import get_engine, get_db
import pytest

def test_get_engine_context():
    with get_engine() as engine:
        assert engine is not None
        # Should be a SQLAlchemy engine
        assert hasattr(engine, 'connect')

def test_get_db_yields_session():
    gen = get_db()
    db = next(gen)
    assert db is not None
    # Clean up
    try:
        next(gen)
    except StopIteration:
        pass
