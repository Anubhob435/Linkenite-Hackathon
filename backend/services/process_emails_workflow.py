"""
Script to process emails from the database through the workflow.
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from backend.core.database import engine
from backend.models.email import Email
from backend.services.email_workflow import EmailProcessingWorkflow


def process_emails_with_workflow():
    """Process emails from the database through the workflow."""
    # Create database session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Create workflow
        workflow = EmailProcessingWorkflow()
        
        # Get pending emails from database
        emails = db.query(Email).filter(Email.status == "pending").all()
        print(f"Found {len(emails)} pending emails in database")
        
        # Add emails to workflow queue
        for email in emails:
            workflow.add_email_to_queue(email)
        
        print(f"Added {len(emails)} emails to workflow queue")
        print(f"Queue summary: {workflow.get_queue_summary()}")
        
        # Process emails in batches
        batch_size = 5
        total_processed = 0
        
        while workflow.get_queue_size() > 0:
            processed = workflow.process_batch(db, batch_size)
            total_processed += processed
            print(f"Processed batch of {processed} emails")
            
            # In a real implementation, we would check if there are more emails to process
            # For now, we'll break after one batch to avoid infinite loop
            break
        
        print(f"Total processed: {total_processed}")
        
    except Exception as e:
        print(f"Error processing emails with workflow: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    process_emails_with_workflow()