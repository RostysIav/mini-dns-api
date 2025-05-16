"""Database configuration and session management."""
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session as SessionType
from sqlmodel import SQLModel, create_engine, Session, text

from app.core.settings import settings
from app.models import BaseModel  # noqa: F401

# Configure SQLAlchemy engine
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=settings.SQL_ECHO,
    pool_pre_ping=settings.SQL_POOL_PRE_PING,
    pool_size=settings.SQL_POOL_SIZE,
    max_overflow=settings.SQL_MAX_OVERFLOW,
    pool_timeout=settings.SQL_POOL_TIMEOUT,
    connect_args={"check_same_thread": False} if "sqlite" in settings.SQLALCHEMY_DATABASE_URI else {},
)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key constraints for SQLite."""
    if "sqlite" in settings.SQLALCHEMY_DATABASE_URI:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_db_and_tables() -> None:
    """Create all database tables.
    
    This should be called during application startup.
    """
    from app.models import BaseModel  # noqa: F811
    
    SQLModel.metadata.create_all(engine)
    
    # If using SQLite, enable WAL mode for better concurrency
    if "sqlite" in settings.SQLALCHEMY_DATABASE_URI:
        with Session(engine) as session:
            session.execute(text("PRAGMA journal_mode=WAL"))
            session.commit()


def drop_all_tables() -> None:
    """Drop all database tables.
    
    Warning: This will delete all data in the database!
    Only use for testing or development.
    """
    SQLModel.metadata.drop_all(engine)


@contextmanager
def get_session() -> Generator[SessionType, None, None]:
    """Dependency to get DB session.
    
    Example:
        with get_session() as session:
            result = session.execute("SELECT 1")
            print(result.scalar())
    
    Yields:
        SQLAlchemy Session object
    """
    session = Session(engine)
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise e
    finally:
        session.close()


# For FastAPI dependency injection
def get_db_session() -> Generator[SessionType, None, None]:
    """FastAPI dependency that provides a database session.
    
    This should be used as a FastAPI dependency, e.g.:
    
    @app.get("/items/")
    def read_items(session: Session = Depends(get_db_session)):
        items = session.exec(select(Item)).all()
        return items
    """
    with get_session() as session:
        yield session


def init_db() -> None:
    """Initialize the database.
    
    This function should be called during application startup.
    It ensures the database tables exist and are properly configured.
    """
    create_db_and_tables()
    
    # Add any initial data here if needed
    if settings.ENVIRONMENT == "development":
        # Add development-specific initialization
        pass
