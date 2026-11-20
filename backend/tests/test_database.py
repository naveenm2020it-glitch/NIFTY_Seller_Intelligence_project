import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.database.session import get_engine


def test_database_connection_executes_select_one() -> None:
    engine = get_engine()
    try:
        with engine.connect() as connection:
            assert connection.execute(text("SELECT 1")).scalar_one() == 1
    finally:
        engine.dispose()


def test_database_connection_fails_clearly_when_database_is_unavailable(monkeypatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@127.0.0.1:1/nifty_seller_intelligence",
    )
    engine = get_engine()
    try:
        with pytest.raises(OperationalError):
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
    finally:
        engine.dispose()
