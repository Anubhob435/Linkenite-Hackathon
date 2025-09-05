"""
Script to check generated responses.
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from backend.core.database import engine
from backend.models.response import Response


def check_responses():
    """Check generated responses in the database."""
    # Create database session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Get first 5 responses from database
        responses = db.query(Response).limit(5).all()
        print(f"Found {len(responses)} responses in database:")
        print("=" * 50)
        
        for response in responses:
            print(f"Response ID: {response.id[:8]}...")
            print(f"Email ID: {response.email_id[:8]}...")
            print(f"Status: {response.status}")
            print(f"Content preview: {response.generated_content[:100]}...")
            print()
        
    except Exception as e:
        print(f"Error checking responses: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    check_responses()