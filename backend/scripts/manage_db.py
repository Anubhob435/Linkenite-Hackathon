"""
Database management utility script.
"""
import argparse
import logging
from pathlib import Path

from backend.scripts.init_db import init_database
from backend.scripts.seed_data import seed_database
from backend.core.database import drop_tables, check_database_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reset_database(csv_file_path: str = None):
    """Reset database by dropping and recreating tables, then seeding data."""
    logger.info("Resetting database...")
    
    try:
        # Drop existing tables
        drop_tables()
        
        # Initialize database
        if not init_database():
            return False
        
        # Seed with data if CSV file provided
        if csv_file_path:
            seed_database(csv_file_path)
        
        logger.info("Database reset completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        return False


def main():
    """Main function for database management CLI."""
    parser = argparse.ArgumentParser(description="Database management utility")
    parser.add_argument(
        "command",
        choices=["init", "seed", "reset", "check"],
        help="Command to execute"
    )
    parser.add_argument(
        "--csv-file",
        default="68b1acd44f393_Sample_Support_Emails_Dataset.csv",
        help="Path to CSV file for seeding data"
    )
    
    args = parser.parse_args()
    
    if args.command == "check":
        if check_database_connection():
            logger.info("Database connection is working")
            return 0
        else:
            logger.error("Database connection failed")
            return 1
    
    elif args.command == "init":
        if init_database():
            return 0
        else:
            return 1
    
    elif args.command == "seed":
        try:
            seed_database(args.csv_file)
            return 0
        except Exception as e:
            logger.error(f"Seeding failed: {e}")
            return 1
    
    elif args.command == "reset":
        if reset_database(args.csv_file):
            return 0
        else:
            return 1


if __name__ == "__main__":
    exit(main())