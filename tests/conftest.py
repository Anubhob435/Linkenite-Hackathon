"""
Pytest configuration and fixtures.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.database import Base, get_db
from backend.core.config import Settings


@pytest.fixture(scope="session")
def test_settings():
    """Test settings fixture."""
    return Settings(
        DATABASE_URL="sqlite:///:memory:",
        DEBUG=True,
        ENVIRONMENT="test"
    )


@pytest.fixture(scope="session")
def test_engine(test_settings):
    """Test database engine fixture."""
    engine = create_engine(
        test_settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine


@pytest.fixture(scope="session")
def test_session_factory(test_engine):
    """Test session factory fixture."""
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session(test_engine, test_session_factory):
    """Database session fixture for each test."""
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    session = test_session_factory()
    
    try:
        yield session
    finally:
        session.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def override_get_db(db_session):
    """Override get_db dependency for testing."""
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass
    
    return _get_test_db