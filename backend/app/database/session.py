from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.core.config import get_database_url


def get_engine() -> Engine:
    return create_engine(get_database_url(), pool_pre_ping=True)


def check_database_connection() -> bool:
    engine = get_engine()
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    finally:
        engine.dispose()
