"""
Script to check AI processing results.
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from backend.core.database import engine
from backend.models.email import Email


def check_ai_results():
    """Check AI processing results in the database."""
    # Create database session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Get first 10 emails from database
        emails = db.query(Email).limit(10).all()
        print(f"Checking {len(emails)} emails for AI processing results:")
        print("=" * 60)
        
        for email in emails:
            print(f"Subject: {email.subject[:40]}...")
            print(f"  Sentiment: {email.sentiment}")
            print(f"  Priority: {email.priority}")
            print(f"  Status: {email.status}")
            if email.extracted_info:
                print(f"  Extracted Info: {list(email.extracted_info.keys())}")
            print()
        
    except Exception as e:
        print(f"Error checking AI results: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    check_ai_results()