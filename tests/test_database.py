from database.session import get_db


def test_get_db_yields_session():
    gen = get_db()
    db = next(gen)
    assert db is not None
    # Clean up
    try:
        next(gen)
    except StopIteration:
        pass
