"""
Test script for email processing workflow.
"""
import sys
import os
import asyncio

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.email_workflow import EmailProcessingWorkflow
from backend.models.email import Email, SentimentType, PriorityLevel, EmailStatus
import uuid
from datetime import datetime


def test_email_workflow():
    """Test the email processing workflow."""
    print("Testing Email Processing Workflow")
    print("=" * 35)
    
    # Create workflow
    workflow = EmailProcessingWorkflow()
    
    # Create some sample emails
    email1 = Email(
        id=str(uuid.uuid4()),
        sender_email="user1@example.com",
        subject="Urgent: System access blocked",
        body="I cannot access the system. This is critical for my work.",
        received_at=datetime.now(),
        sentiment=SentimentType.NEGATIVE,
        priority=PriorityLevel.URGENT,
        status=EmailStatus.PENDING
    )
    
    email2 = Email(
        id=str(uuid.uuid4()),
        sender_email="user2@example.com",
        subject="General query about subscription",
        body="I would like to know more about your subscription options.",
        received_at=datetime.now(),
        sentiment=SentimentType.NEUTRAL,
        priority=PriorityLevel.NOT_URGENT,
        status=EmailStatus.PENDING
    )
    
    email3 = Email(
        id=str(uuid.uuid4()),
        sender_email="user3@example.com",
        subject="Immediate support needed for billing error",
        body="There is a billing error where I was charged twice. This needs immediate correction.",
        received_at=datetime.now(),
        sentiment=SentimentType.NEGATIVE,
        priority=PriorityLevel.URGENT,
        status=EmailStatus.PENDING
    )
    
    # Add emails to queue
    print("Adding emails to queue...")
    workflow.add_email_to_queue(email1)
    workflow.add_email_to_queue(email2)
    workflow.add_email_to_queue(email3)
    
    print(f"Queue size: {workflow.get_queue_size()}")
    print(f"Queue summary: {workflow.get_queue_summary()}")
    
    # Show queue contents (for testing purposes)
    print("\nQueue contents:")
    for i, (priority, counter, timestamp, email) in enumerate(workflow.processing_queue):
        print(f"  {i+1}. {email.subject[:30]}... (Priority: {priority})")
    
    print("\nIn a real implementation, emails would be processed with a database session")
    print("and the AI processing and response generation would be applied.")


if __name__ == "__main__":
    test_email_workflow()
