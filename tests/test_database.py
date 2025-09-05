"""
Unit tests for database utilities and operations.
"""
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError

from backend.core.database import (
    get_db_session, create_tables, drop_tables, check_database_connection
)


class TestDatabaseUtilities:
    """Test cases for database utility functions."""
    
    def test_get_db_session_success(self, test_engine, test_session_factory):
        """Test successful database session context manager."""
        from sqlalchemy import text
        
        with patch('backend.core.database.SessionLocal', test_session_factory):
            with get_db_session() as session:
                assert session is not None
                # Session should be usable
                result = session.execute(text("SELECT 1")).scalar()
                assert result == 1
    
    def test_get_db_session_with_exception(self, test_engine, test_session_factory):
        """Test database session context manager with exception."""
        with patch('backend.core.database.SessionLocal', test_session_factory):
            with pytest.raises(ValueError):
                with get_db_session() as session:
                    # Simulate an error that should trigger rollback
                    raise ValueError("Test error")
    
    def test_check_database_connection_success(self, test_engine):
        """Test successful database connection check."""
        with patch('backend.core.database.engine', test_engine):
            result = check_database_connection()
            assert result is True
    
    def test_check_database_connection_failure(self):
        """Test database connection check failure."""
        mock_engine = MagicMock()
        mock_engine.connect.side_effect = SQLAlchemyError("Connection failed")
        
        with patch('backend.core.database.engine', mock_engine):
            result = check_database_connection()
            assert result is False
    
    def test_create_tables_success(self, test_engine):
        """Test successful table creation."""
        with patch('backend.core.database.engine', test_engine):
            # Should not raise an exception
            create_tables()
    
    def test_create_tables_failure(self):
        """Test table creation failure."""
        mock_engine = MagicMock()
        mock_base = MagicMock()
        mock_base.metadata.create_all.side_effect = SQLAlchemyError("Create failed")
        
        with patch('backend.core.database.engine', mock_engine):
            with patch('backend.core.database.Base', mock_base):
                with pytest.raises(SQLAlchemyError):
                    create_tables()
    
    def test_drop_tables_success(self, test_engine):
        """Test successful table dropping."""
        with patch('backend.core.database.engine', test_engine):
            # Should not raise an exception
            drop_tables()
    
    def test_drop_tables_failure(self):
        """Test table dropping failure."""
        mock_engine = MagicMock()
        mock_base = MagicMock()
        mock_base.metadata.drop_all.side_effect = SQLAlchemyError("Drop failed")
        
        with patch('backend.core.database.engine', mock_engine):
            with patch('backend.core.database.Base', mock_base):
                with pytest.raises(SQLAlchemyError):
                    drop_tables()