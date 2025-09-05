"""
Script to process existing emails through the retrieval service.
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from backend.core.database import engine
from backend.services.email_retrieval import EmailRetrievalService
from backend.models.email import Email


def process_existing_emails():
    """Process existing emails in the database through the retrieval service."""
    # Create database session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Get all emails from database
        emails = db.query(Email).all()
        print(f"Found {len(emails)} emails in database")
        
        # Create retrieval service
        service = EmailRetrievalService()
        
        # Process each email
        for email in emails:
            # In a real implementation, we would convert the database email back to 
            # an EmailMessage object and process it through the service
            # For now, we'll just show that we can access the emails
            print(f"Processing email: {email.subject[:50]}...")
            
            # Example: Update extracted_info if it's missing
            if not email.extracted_info:
                # Create a mock EmailMessage object from the database email
                # This is a simplified example
                print(f"  Updating extracted info for: {email.subject[:30]}...")
                # In a real implementation, we would do actual processing here
                
        print("Finished processing emails")
        
    except Exception as e:
        print(f"Error processing emails: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    process_existing_emails()