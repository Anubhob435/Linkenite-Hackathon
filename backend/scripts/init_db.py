"""
Database initialization script.
"""
import logging
from pathlib import Path

from backend.core.database import create_tables, check_database_connection
from backend.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """Initialize the database with tables and basic data."""
    logger.info("Starting database initialization...")
    
    # Check database connection
    if not check_database_connection():
        logger.error("Cannot connect to database. Please check your configuration.")
        return False
    
    try:
        # Create tables
        create_tables()
        logger.info("Database initialization completed successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


if __name__ == "__main__":
    success = init_database()
    if not success:
        exit(1)