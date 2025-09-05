"""
Test script for email retrieval service.
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.email_retrieval import EmailRetrievalService
from backend.email_providers.base import EmailMessage
from datetime import datetime


async def test_email_retrieval_service():
    """Test the email retrieval service."""
    service = EmailRetrievalService()
    
    # Test filtering support emails
    print("Testing support email filtering...")
    
    # Create some test emails
    test_emails = [
        EmailMessage(
            message_id="1",
            sender="user@example.com",
            recipients=["support@company.com"],
            subject="Support needed with my account",
            body="I'm having trouble accessing my account. Can you help?",
            received_at=datetime.now()
        ),
        EmailMessage(
            message_id="2",
            sender="user@example.com",
            recipients=["info@company.com"],
            subject="General inquiry about services",
            body="I'd like to know more about your services.",
            received_at=datetime.now()
        ),
        EmailMessage(
            message_id="3",
            sender="customer@example.com",
            recipients=["support@company.com"],
            subject="Help with billing issue",
            body="There's an error in my bill. Please assist.",
            received_at=datetime.now()
        )
    ]
    
    # Filter support emails
    support_emails = service.filter_support_emails(test_emails)
    print(f"Filtered {len(support_emails)} support emails from {len(test_emails)} total emails")
    
    # Test metadata extraction
    print("\nTesting metadata extraction...")
    for email in support_emails:
        metadata = service.extract_email_metadata(email)
        print(f"Email subject: {email.subject}")
        print(f"Contact info: {metadata.get('contact_info', {})}")
        print(f"Requirements: {metadata.get('requirements', [])}")
        print()
    
    # Test conversion to database model
    print("Testing conversion to database model...")
    db_emails = [service.convert_to_db_model(email) for email in support_emails]
    print(f"Converted {len(db_emails)} emails to database models")
    
    # Test deduplication
    print("\nTesting deduplication...")
    # Create some duplicate emails
    duplicate_emails = db_emails + db_emails[:1]  # Add one duplicate
    unique_emails = service.deduplicate_emails(duplicate_emails)
    print(f"Deduplicated emails: {len(duplicate_emails)} -> {len(unique_emails)}")


if __name__ == "__main__":
    asyncio.run(test_email_retrieval_service())