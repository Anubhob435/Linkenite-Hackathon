"""
Test script for AI processing engine.
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.ai_processing import AIProcessingEngine


def test_ai_processing_engine():
    """Test the AI processing engine."""
    engine = AIProcessingEngine()
    
    # Test cases
    test_emails = [
        {
            "subject": "Thank you for your excellent service",
            "body": "I really appreciate the great support you provided. Everything is working perfectly now. Thank you so much!"
        },
        {
            "subject": "Urgent: System is down",
            "body": "Our system has crashed and we cannot access it. This is critical and needs immediate attention. Please help ASAP!"
        },
        {
            "subject": "General inquiry about pricing",
            "body": "I would like to know more about your pricing options. Can you provide details?"
        },
        {
            "subject": "Complaint about service quality",
            "body": "I am very disappointed with your service. This is terrible and I'm frustrated with the poor quality."
        },
        {
            "subject": "Help with account setup",
            "body": "I need assistance setting up my account. Can you guide me through the process?"
        }
    ]
    
    print("Testing AI Processing Engine")
    print("=" * 40)
    
    for i, email in enumerate(test_emails, 1):
        print(f"\nTest Email {i}:")
        print(f"Subject: {email['subject']}")
        print(f"Body: {email['body'][:100]}...")
        
        results = engine.process_email(email["subject"], email["body"])
        print(f"Sentiment: {results['sentiment']}")
        print(f"Priority: {results['priority']}")
        print(f"Extracted Info: {results['extracted_info']}")


if __name__ == "__main__":
    test_ai_processing_engine()