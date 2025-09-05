"""
Test script for response generation.
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.response_generation import ResponseGenerator
from backend.services.knowledge_base import KnowledgeBase
from backend.services.ai_processing import SentimentType


def test_response_generation():
    """Test the response generation system."""
    print("Testing Response Generation System")
    print("=" * 35)
    
    # Create a knowledge base with sample items
    kb = KnowledgeBase()
    kb.add_item(
        title="Account Login Issues",
        content="If you're unable to log into your account, try resetting your password. Click 'Forgot Password' on the login page and follow the instructions sent to your email.",
        category="Account Management",
        tags=["login", "account", "password"]
    )
    
    kb.add_item(
        title="Password Reset Process",
        content="To reset your password: 1) Go to the login page and click 'Forgot Password', 2) Enter your email address, 3) Check your email for a password reset link, 4) Click the link and enter a new password.",
        category="Account Management",
        tags=["password", "reset", "account"]
    )
    
    kb.add_item(
        title="Billing Issues",
        content="For billing issues, please contact our billing department at billing@company.com or call 1-800-123-4567.",
        category="Billing",
        tags=["billing", "payment", "invoice"]
    )
    
    # Create response generator
    generator = ResponseGenerator(kb)
    
    # Test cases
    test_emails = [
        {
            "subject": "Help with login issue",
            "body": "I can't access my account. This is really frustrating. Please help!",
            "sentiment": SentimentType.NEGATIVE
        },
        {
            "subject": "Thank you for your service",
            "body": "I really appreciate the excellent support you provided. Everything is working perfectly now.",
            "sentiment": SentimentType.POSITIVE
        },
        {
            "subject": "General inquiry about billing",
            "body": "I would like to know more about your billing process.",
            "sentiment": SentimentType.NEUTRAL
        },
        {
            "subject": "Password reset needed",
            "body": "I forgot my password and need to reset it. Can you help?",
            "sentiment": SentimentType.NEUTRAL
        }
    ]
    
    for i, email in enumerate(test_emails, 1):
        print(f"\nTest Email {i}:")
        print(f"Subject: {email['subject']}")
        print(f"Body: {email['body']}")
        print(f"Sentiment: {email['sentiment']}")
        
        # Generate standard response
        response = generator.generate_response(
            email["subject"], 
            email["body"], 
            email["sentiment"]
        )
        print(f"Generated Response ({len(response)} chars):")
        print("-" * 20)
        print(response[:200] + "..." if len(response) > 200 else response)
        
        # Generate empathetic response (if negative sentiment)
        if email["sentiment"] == SentimentType.NEGATIVE:
            empathetic_response = generator.generate_empathetic_response(
                email["subject"], 
                email["body"], 
                email["sentiment"]
            )
            print(f"Empathetic Response ({len(empathetic_response)} chars):")
            print("-" * 20)
            print(empathetic_response[:200] + "..." if len(empathetic_response) > 200 else empathetic_response)


if __name__ == "__main__":
    test_response_generation()