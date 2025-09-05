"""
Script to process emails in the database through the AI processing engine.
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from backend.core.database import engine
from backend.services.ai_processing import AIProcessingEngine
from backend.models.email import Email


def process_emails_with_ai():
    """Process emails in the database through the AI processing engine."""
    # Create database session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Get all emails from database
        emails = db.query(Email).all()
        print(f"Found {len(emails)} emails in database")
        
        # Create AI processing engine
        ai_engine = AIProcessingEngine()
        
        # Process each email
        for email in emails:
            print(f"Processing email: {email.subject[:50]}...")
            
            # Process email through AI engine
            results = ai_engine.process_email(email.subject, email.body)
            
            # Update email with AI results
            email.sentiment = results["sentiment"]
            email.priority = results["priority"]
            
            # Update extracted_info with AI results
            if email.extracted_info:
                email.extracted_info.update(results["extracted_info"])
            else:
                email.extracted_info = results["extracted_info"]
            
            # Update email status to processed
            from backend.models.email import EmailStatus
            email.status = EmailStatus.PROCESSED
        
        # Commit changes to database
        db.commit()
        print(f"Processed and updated {len(emails)} emails in the database")
        
    except Exception as e:
        print(f"Error processing emails: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    process_emails_with_ai()