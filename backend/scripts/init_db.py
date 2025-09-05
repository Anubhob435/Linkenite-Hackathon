"""
Database initialization script.
"""
import os
import sys
import pandas as pd
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.config import settings
from backend.core.database import Base
from backend.models.email import Email, SentimentType, PriorityLevel, EmailStatus

def init_db():
    """Initialize the database."""
    # Create database engine
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("Database initialized successfully!")

def load_sample_data():
    """Load sample data from CSV file."""
    # Create database engine
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Read CSV file
        csv_path = "68b1acd44f393_Sample_Support_Emails_Dataset.csv"
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            
            # Load data into database
            for index, row in df.iterrows():
                email = Email(
                    id=str(uuid.uuid4()),
                    sender_email=row['sender'],
                    subject=row['subject'],
                    body=row['body'],
                    received_at=pd.to_datetime(row['sent_date']),
                    sentiment=SentimentType.NEUTRAL,  # Will be updated by AI processing
                    priority=PriorityLevel.NOT_URGENT,  # Will be updated by AI processing
                    status=EmailStatus.PENDING
                )
                db.add(email)
            
            db.commit()
            print(f"Loaded {len(df)} sample emails into the database!")
        else:
            print(f"CSV file {csv_path} not found. Skipping sample data load.")
    except Exception as e:
        print(f"Error loading sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    load_sample_data()